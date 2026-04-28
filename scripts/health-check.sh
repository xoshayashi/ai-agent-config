#!/bin/sh
set -eu

format=${AI_AGENT_HEALTH_FORMAT:-text}
strict=${AI_AGENT_HEALTH_STRICT:-0}
redact_output=${AI_AGENT_HEALTH_REDACT:-1}

warn() {
  printf 'warning: %s\n' "$*" >&2
}

case "${1:-}" in
  --json)
    format=json
    ;;
  --text)
    format=text
    ;;
  '')
    ;;
  *)
    printf 'error: usage: %s [--text|--json]\n' "$0" >&2
    exit 2
    ;;
esac

case "$format" in
  text|json) ;;
  *) printf 'error: AI_AGENT_HEALTH_FORMAT must be text or json\n' >&2; exit 2 ;;
esac

case "$strict" in
  0|1) ;;
  *) printf 'error: AI_AGENT_HEALTH_STRICT must be 0 or 1\n' >&2; exit 2 ;;
esac

case "$redact_output" in
  0|1) ;;
  *) printf 'error: AI_AGENT_HEALTH_REDACT must be 0 or 1\n' >&2; exit 2 ;;
esac

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

expand_home() {
  case "$1" in
    '~')
      printf '%s\n' "$HOME"
      ;;
    '~/'*)
      printf '%s/%s\n' "$HOME" "${1#~/}"
      ;;
    *)
      printf '%s\n' "$1"
      ;;
  esac
}

json_escape() {
  printf '%s' "$1" | awk '
    BEGIN { ORS = "" }
    {
      gsub(/\\/, "\\\\")
      gsub(/"/, "\\\"")
      gsub(/\t/, "\\t")
      gsub(/\r/, "\\r")
      if (NR > 1) {
        printf "\\n"
      }
      printf "%s", $0
    }
  '
}

json_value() {
  case "$1" in
    true|false|null)
      printf '%s' "$1"
      ;;
    ''|*[!0-9]*)
      printf '"%s"' "$(json_escape "$1")"
      ;;
    *)
      printf '%s' "$1"
      ;;
  esac
}

status_rank=0
mark_status() {
  case "$1" in
    fail)
      status_rank=2
      ;;
    warn)
      if [ "$status_rank" -lt 1 ]; then
        status_rank=1
      fi
      ;;
  esac
}

overall_status() {
  case "$status_rank" in
    0) printf 'ok' ;;
    1) printf 'warn' ;;
    *) printf 'fail' ;;
  esac
}

command_path() {
  command -v "$1" 2>/dev/null || true
}

display_path() {
  path=$1
  if [ "$redact_output" = "0" ]; then
    printf '%s' "$path"
    return 0
  fi
  case "$path" in
    '')
      printf ''
      ;;
    */*)
      printf '.../%s' "$(basename "$path")"
      ;;
    *)
      printf '%s' "$path"
      ;;
  esac
}

display_remote() {
  remote=$1
  if [ "$redact_output" = "0" ]; then
    printf '%s' "$remote"
    return 0
  fi
  [ -n "$remote" ] || {
    printf ''
    return 0
  }
  printf '[redacted]'
}

load_state_file() {
  path=$1
  [ -f "$path" ] || return 1
  command -v python3 >/dev/null 2>&1 || {
    warn "python3 is required to read setup state safely: $path"
    return 1
  }
  parser="$script_dir/read-state-config.py"
  [ -f "$parser" ] || {
    warn "state parser not found: $parser"
    return 1
  }
  if ! parsed=$(python3 "$parser" "$path" 2>/dev/null); then
    warn "state file could not be read safely: $path"
    return 1
  fi
  tab=$(printf '\t')
  while IFS="$tab" read -r key value; do
    [ -n "$key" ] || continue
    case "$key" in
      AI_AGENT_CONFIG_HOME) AI_AGENT_CONFIG_HOME=$value ;;
      AI_AGENT_CODEX_HOME) AI_AGENT_CODEX_HOME=$value ;;
      AI_AGENT_CLAUDE_HOME) AI_AGENT_CLAUDE_HOME=$value ;;
      AI_AGENT_GEMINI_HOME) AI_AGENT_GEMINI_HOME=$value ;;
      AI_AGENT_SKILLS_DIR) AI_AGENT_SKILLS_DIR=$value ;;
      AI_AGENT_HOOKS_RUNTIME_LINK) AI_AGENT_HOOKS_RUNTIME_LINK=$value ;;
      AI_AGENT_REQUIRE_LLM_CLIS) AI_AGENT_REQUIRE_LLM_CLIS=$value ;;
      AI_AGENT_STATE_DIR) AI_AGENT_STATE_DIR=$value ;;
      AI_AGENT_STATE_FILE) AI_AGENT_STATE_FILE=$value ;;
    esac
  done <<EOF
$parsed
EOF
  return 0
}

env_config_set=${AI_AGENT_CONFIG_HOME+x}
env_config=${AI_AGENT_CONFIG_HOME-}
env_codex_home_set=${AI_AGENT_CODEX_HOME+x}
env_codex_home=${AI_AGENT_CODEX_HOME-}
env_claude_home_set=${AI_AGENT_CLAUDE_HOME+x}
env_claude_home=${AI_AGENT_CLAUDE_HOME-}
env_gemini_home_set=${AI_AGENT_GEMINI_HOME+x}
env_gemini_home=${AI_AGENT_GEMINI_HOME-}
env_skills_set=${AI_AGENT_SKILLS_DIR+x}
env_skills=${AI_AGENT_SKILLS_DIR-}
env_hooks_runtime_set=${AI_AGENT_HOOKS_RUNTIME_LINK+x}
env_hooks_runtime=${AI_AGENT_HOOKS_RUNTIME_LINK-}

state_dir=${AI_AGENT_STATE_DIR:-$HOME/.llm-config}
legacy_state_dir=${AI_AGENT_LEGACY_STATE_DIR:-$HOME/.ai-agent-config}
if [ -n "${AI_AGENT_STATE_FILE:-}" ]; then
  state_file=$(expand_home "$AI_AGENT_STATE_FILE")
else
  state_file=$(expand_home "$state_dir")/config.env
  legacy_state_file=$(expand_home "$legacy_state_dir")/config.env
  if [ ! -f "$state_file" ] && [ -f "$legacy_state_file" ]; then
    state_file=$legacy_state_file
  fi
fi
state_loaded=false
if load_state_file "$state_file"; then
  state_loaded=true
elif [ -f "$state_file" ]; then
  mark_status warn
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_codex_home_set:-}" = "x" ] && AI_AGENT_CODEX_HOME=$env_codex_home
[ "${env_claude_home_set:-}" = "x" ] && AI_AGENT_CLAUDE_HOME=$env_claude_home
[ "${env_gemini_home_set:-}" = "x" ] && AI_AGENT_GEMINI_HOME=$env_gemini_home
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills
[ "${env_hooks_runtime_set:-}" = "x" ] && AI_AGENT_HOOKS_RUNTIME_LINK=$env_hooks_runtime
state_dir=${AI_AGENT_STATE_DIR:-$state_dir}
if [ -n "${AI_AGENT_STATE_FILE:-}" ]; then
  state_file=$(expand_home "$AI_AGENT_STATE_FILE")
fi

if [ -n "${AI_AGENT_TARGET_DIR:-}" ]; then
  warn "AI_AGENT_TARGET_DIR is deprecated and ignored. Instructions are now installed globally."
fi
if [ -n "${AI_AGENT_HOOKS_SCOPE:-}" ]; then
  warn "AI_AGENT_HOOKS_SCOPE is deprecated and ignored. Hooks are now installed globally."
fi

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(expand_home "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
codex_home=$(expand_home "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(expand_home "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
gemini_home=$(expand_home "${AI_AGENT_GEMINI_HOME:-$HOME/.gemini}")
skills_dir=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}
hooks_runtime_link=${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}
hooks_runtime_path=$(expand_home "$hooks_runtime_link")

git_path=$(command_path git)
gh_path=$(command_path gh)
claude_path=$(command_path claude)
codex_path=$(command_path codex)
gemini_path=$(command_path gemini)
ollama_path=$(command_path ollama)

response_strategy_enabled=${AI_AGENT_HOOKS_ENABLE_RESPONSE_STRATEGY:-0}
response_strategy_provider=${AI_AGENT_RESPONSE_STRATEGY_PROVIDER:-auto}
response_strategy_ollama_model=${AI_AGENT_RESPONSE_STRATEGY_OLLAMA_MODEL:-}

skill_improvement_schedule=unsupported
os=$(uname -s 2>/dev/null || printf unknown)
if [ "$os" = "Darwin" ]; then
  skill_improvement_label=${AI_AGENT_IMPROVEMENT_LABEL:-com.llm-config.skill-improvement}
  skill_improvement_plist="$HOME/Library/LaunchAgents/$skill_improvement_label.plist"
  if [ -f "$skill_improvement_plist" ]; then
    if launchctl list "$skill_improvement_label" >/dev/null 2>&1; then
      skill_improvement_schedule=active
    else
      skill_improvement_schedule=installed
    fi
  else
    skill_improvement_schedule=missing
  fi
elif command -v systemctl >/dev/null 2>&1; then
  if systemctl --user is-active llm-config-skill-improvement.timer >/dev/null 2>&1; then
    skill_improvement_schedule=active
  elif systemctl --user is-enabled llm-config-skill-improvement.timer >/dev/null 2>&1; then
    skill_improvement_schedule=installed
  else
    skill_improvement_schedule=missing
  fi
fi

repo_status=fail
repo_branch=
repo_dirty=unknown
repo_remote=
repo_head=
repo_upstream=
repo_ahead=unknown
repo_behind=unknown

if [ -n "$git_path" ] && [ -d "$config_home/.git" ]; then
  if git -C "$config_home" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    repo_status=ok
    repo_branch=$(git -C "$config_home" rev-parse --abbrev-ref HEAD 2>/dev/null || printf unknown)
    repo_head=$(git -C "$config_home" rev-parse --short HEAD 2>/dev/null || printf unknown)
    repo_remote=$(git -C "$config_home" remote get-url origin 2>/dev/null || true)
    repo_upstream=$(git -C "$config_home" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
    if [ -n "$repo_upstream" ]; then
      set -- $(git -C "$config_home" rev-list --left-right --count "$repo_upstream...HEAD" 2>/dev/null || printf 'unknown unknown')
      repo_behind=${1:-unknown}
      repo_ahead=${2:-unknown}
    fi
    if [ -n "$(git -C "$config_home" status --porcelain 2>/dev/null)" ]; then
      repo_dirty=true
      repo_status=warn
      mark_status warn
    else
      repo_dirty=false
    fi
  else
    mark_status fail
  fi
else
  mark_status fail
fi

github_status=unknown
if [ -n "$gh_path" ]; then
  if gh auth status -h github.com >/dev/null 2>&1; then
    github_status=ok
  else
    github_status=warn
    mark_status warn
  fi
else
  github_status=missing-gh
  mark_status warn
fi

command_status() {
  if [ -n "$2" ]; then
    printf 'ok'
  else
    printf 'missing'
  fi
}

git_status=$(command_status git "$git_path")
gh_status=$(command_status gh "$gh_path")
claude_status=$(command_status claude "$claude_path")
codex_status=$(command_status codex "$codex_path")
gemini_status=$(command_status gemini "$gemini_path")
ollama_status=$(command_status ollama "$ollama_path")

link_status_for() {
  dst=$1
  expected=$2
  parent=$(dirname "$dst")
  if [ ! -d "$parent" ]; then
    printf 'missing-target'
  elif [ ! -L "$dst" ]; then
    printf 'missing'
  else
    current=$(readlink "$dst" 2>/dev/null || true)
    if [ "$current" = "$expected" ]; then
      printf 'ok'
    else
      printf 'mismatch'
    fi
  fi
}

hook_config_status_for() {
  dst=$1
  expected=$2
  kind=$3
  parent=$(dirname "$dst")
  if [ ! -d "$parent" ]; then
    printf 'missing-target'
  elif [ -L "$dst" ]; then
    current=$(readlink "$dst" 2>/dev/null || true)
    if [ "$current" = "$expected" ]; then
      printf 'ok'
    else
      printf 'mismatch'
    fi
  elif [ -f "$dst" ]; then
    if [ "$kind" = "codex-config" ]; then
      if grep -Eq '^[[:space:]]*codex_hooks[[:space:]]*=[[:space:]]*true[[:space:]]*$' "$dst" 2>/dev/null; then
        printf 'appended'
      else
        printf 'present-unmanaged'
      fi
      return 0
    fi
    if ! command -v python3 >/dev/null 2>&1; then
      printf 'present-unmanaged'
      return 0
    fi
status=$(python3 - "$dst" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("present-unmanaged")
    raise SystemExit(0)

hooks = data.get("hooks")
if not isinstance(hooks, dict):
    print("present-unmanaged")
    raise SystemExit(0)

legacy_hints = {
    "safe_delete_guard.py",
    "peer_prompt_refinement.py",
    "refinment.py",
    "response_strategy_bridge.py",
    "multillm_orchestrator.py",
}

for groups in hooks.values():
    if not isinstance(groups, list):
        continue
    for group in groups:
        if not isinstance(group, dict):
            continue
        if group.get("_llm_config_managed") is True:
            print("appended")
            raise SystemExit(0)
        hook_items = group.get("hooks")
        if not isinstance(hook_items, list):
            continue
        for hook in hook_items:
            if not isinstance(hook, dict):
                continue
            command = hook.get("command")
            if not isinstance(command, str):
                continue
            if "AI_AGENT_HOOKS_RUNTIME_LINK" in command and any(hint in command for hint in legacy_hints):
                print("appended-legacy")
                raise SystemExit(0)

print("present-unmanaged")
PY
)
    printf '%s' "${status:-present-unmanaged}"
  else
    printf 'missing'
  fi
}

codex_agents_status=$(link_status_for "$codex_home/AGENTS.md" "$config_home/instructions/AGENTS.md")
codex_shared_status=$(link_status_for "$codex_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
codex_design_status=$(link_status_for "$codex_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
codex_hooks_doc_status=$(link_status_for "$codex_home/HOOKS.md" "$config_home/instructions/HOOKS.md")
claude_entry_status=$(link_status_for "$claude_home/CLAUDE.md" "$config_home/instructions/CLAUDE.md")
claude_shared_status=$(link_status_for "$claude_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
claude_design_status=$(link_status_for "$claude_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
claude_hooks_doc_status=$(link_status_for "$claude_home/HOOKS.md" "$config_home/instructions/HOOKS.md")
gemini_entry_status=$(link_status_for "$gemini_home/GEMINI.md" "$config_home/instructions/GEMINI.md")
gemini_shared_status=$(link_status_for "$gemini_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
gemini_design_status=$(link_status_for "$gemini_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
gemini_hooks_doc_status=$(link_status_for "$gemini_home/HOOKS.md" "$config_home/instructions/HOOKS.md")
hook_runtime_status=$(link_status_for "$hooks_runtime_path" "$config_home/hooks")

claude_hook_status=$(hook_config_status_for "$claude_home/settings.json" "$config_home/hooks/claude/settings.json" json)
codex_config_status=$(hook_config_status_for "$codex_home/config.toml" "$config_home/hooks/codex/config.toml" codex-config)
codex_hook_status=$(hook_config_status_for "$codex_home/hooks.json" "$config_home/hooks/codex/hooks.json" json)
gemini_hook_status=$(hook_config_status_for "$gemini_home/settings.json" "$config_home/hooks/gemini/settings.json" json)

skills_json_body=
skills_text_summary=
skills_total=0
skills_warn=0
for skill_src in "$config_home"/skills/*; do
  [ -d "$skill_src" ] || continue
  [ -f "$skill_src/SKILL.md" ] || continue
  skill_name=$(basename "$skill_src")
  skill_link="$skills_dir/$skill_name"
  skill_status=missing
  if [ -L "$skill_link" ]; then
    if [ "$(readlink "$skill_link" 2>/dev/null || true)" = "$skill_src" ]; then
      skill_status=ok
    else
      skill_status=mismatch
    fi
  elif [ -e "$skill_link" ]; then
    skill_status=non-link
  fi

  skills_total=$((skills_total + 1))
  case "$skill_status" in
    ok) ;;
    *)
      skills_warn=$((skills_warn + 1))
      mark_status warn
      ;;
  esac

  if [ -n "$skills_json_body" ]; then
    skills_json_body="$skills_json_body,\n"
  fi
  skills_json_body="${skills_json_body}    \"$(json_escape "$skill_name")\": \"$(json_escape "$skill_status")\""
done

if [ "$skills_total" -eq 0 ]; then
  skills_json_body='    "__none__": "missing-source-skills"'
  skills_text_summary="none"
  mark_status warn
else
  skills_text_summary="total=$skills_total warn=$skills_warn"
fi

orchestration_mode=skill-driven
if [ -z "$claude_path" ] && [ -z "$gemini_path" ]; then
  orchestration_status=missing-claude-and-gemini
  mark_status warn
elif [ -z "$claude_path" ]; then
  orchestration_status=missing-claude
  mark_status warn
elif [ -z "$gemini_path" ]; then
  orchestration_status=missing-gemini
  mark_status warn
else
  orchestration_status=ready
fi

response_strategy_status=disabled
response_strategy_effective_provider=$response_strategy_provider
case "$response_strategy_enabled" in
  0|1) ;;
  *)
    response_strategy_status=invalid-enable-flag
    mark_status warn
    ;;
esac

if [ "$response_strategy_enabled" = "1" ]; then
  case "$response_strategy_provider" in
    auto)
      if [ -n "$gemini_path" ]; then
        response_strategy_effective_provider=gemini
        response_strategy_status=ready
      elif [ -n "$codex_path" ]; then
        response_strategy_effective_provider=codex
        response_strategy_status=ready
      elif [ -n "$ollama_path" ] && [ -n "$response_strategy_ollama_model" ]; then
        response_strategy_effective_provider=ollama
        response_strategy_status=ready
      else
        response_strategy_status=missing-peer-cli
        mark_status warn
      fi
      ;;
    gemini)
      if [ -n "$gemini_path" ]; then
        response_strategy_status=ready
      else
        response_strategy_status=missing-gemini
        mark_status warn
      fi
      ;;
    codex)
      if [ -n "$codex_path" ]; then
        response_strategy_status=ready
      else
        response_strategy_status=missing-codex
        mark_status warn
      fi
      ;;
    ollama)
      if [ -z "$ollama_path" ]; then
        response_strategy_status=missing-ollama
        mark_status warn
      elif [ -z "$response_strategy_ollama_model" ]; then
        response_strategy_status=missing-ollama-model
        mark_status warn
      else
        response_strategy_status=ready
      fi
      ;;
    *)
      response_strategy_status=invalid-provider
      mark_status warn
      ;;
  esac
fi

for status in \
  "$gh_status" "$claude_status" "$codex_status" "$gemini_status" \
  "$codex_agents_status" "$codex_shared_status" "$codex_design_status" "$codex_hooks_doc_status" \
  "$claude_entry_status" "$claude_shared_status" "$claude_design_status" "$claude_hooks_doc_status" \
  "$gemini_entry_status" "$gemini_shared_status" "$gemini_design_status" "$gemini_hooks_doc_status" \
  "$hook_runtime_status" \
  "$claude_hook_status" "$codex_config_status" "$codex_hook_status" "$gemini_hook_status"; do
  [ "$status" = "ok" ] || [ "$status" = "appended" ] || [ "$status" = "appended-legacy" ] || mark_status warn
done

if [ "$format" = "json" ]; then
  printf '{\n'
  printf '  "overall": "%s",\n' "$(overall_status)"
  printf '  "redacted": %s,\n' "$(json_value "$([ "$redact_output" = "1" ] && printf true || printf false)")"
  printf '  "config_home": "%s",\n' "$(json_escape "$(display_path "$config_home")")"
  printf '  "state_file": "%s",\n' "$(json_escape "$(display_path "$state_file")")"
  printf '  "state_loaded": %s,\n' "$(json_value "$state_loaded")"
  printf '  "codex_home": "%s",\n' "$(json_escape "$(display_path "$codex_home")")"
  printf '  "claude_home": "%s",\n' "$(json_escape "$(display_path "$claude_home")")"
  printf '  "gemini_home": "%s",\n' "$(json_escape "$(display_path "$gemini_home")")"
  printf '  "skills_dir": "%s",\n' "$(json_escape "$(display_path "$skills_dir")")"
  printf '  "hooks_runtime_link": "%s",\n' "$(json_escape "$(display_path "$hooks_runtime_path")")"
  printf '  "commands": {\n'
  printf '    "git": {"status": "%s", "path": "%s"},\n' "$git_status" "$(json_escape "$(display_path "$git_path")")"
  printf '    "gh": {"status": "%s", "path": "%s"},\n' "$gh_status" "$(json_escape "$(display_path "$gh_path")")"
  printf '    "claude": {"status": "%s", "path": "%s"},\n' "$claude_status" "$(json_escape "$(display_path "$claude_path")")"
  printf '    "codex": {"status": "%s", "path": "%s"},\n' "$codex_status" "$(json_escape "$(display_path "$codex_path")")"
  printf '    "gemini": {"status": "%s", "path": "%s"},\n' "$gemini_status" "$(json_escape "$(display_path "$gemini_path")")"
  printf '    "ollama": {"status": "%s", "path": "%s"}\n' "$ollama_status" "$(json_escape "$(display_path "$ollama_path")")"
  printf '  },\n'
  printf '  "github": {"status": "%s"},\n' "$github_status"
  printf '  "repository": {"status": "%s", "branch": "%s", "head": "%s", "dirty": %s, "origin": "%s", "upstream": "%s", "ahead": %s, "behind": %s},\n' "$repo_status" "$(json_escape "$repo_branch")" "$(json_escape "$repo_head")" "$(json_value "$repo_dirty")" "$(json_escape "$(display_remote "$repo_remote")")" "$(json_escape "$(display_remote "$repo_upstream")")" "$(json_value "$repo_ahead")" "$(json_value "$repo_behind")"
  printf '  "links": {\n'
  printf '    "codex_AGENTS.md": "%s",\n' "$codex_agents_status"
  printf '    "codex_AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$codex_shared_status"
  printf '    "codex_DESIGN.md": "%s",\n' "$codex_design_status"
  printf '    "codex_HOOKS.md": "%s",\n' "$codex_hooks_doc_status"
  printf '    "claude_CLAUDE.md": "%s",\n' "$claude_entry_status"
  printf '    "claude_AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$claude_shared_status"
  printf '    "claude_DESIGN.md": "%s",\n' "$claude_design_status"
  printf '    "claude_HOOKS.md": "%s",\n' "$claude_hooks_doc_status"
  printf '    "gemini_GEMINI.md": "%s",\n' "$gemini_entry_status"
  printf '    "gemini_AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$gemini_shared_status"
  printf '    "gemini_DESIGN.md": "%s",\n' "$gemini_design_status"
  printf '    "gemini_HOOKS.md": "%s",\n' "$gemini_hooks_doc_status"
  printf '    "hook-runtime": "%s",\n' "$hook_runtime_status"
  printf '    "claude-hooks": "%s",\n' "$claude_hook_status"
  printf '    "codex-config": "%s",\n' "$codex_config_status"
  printf '    "codex-hooks": "%s",\n' "$codex_hook_status"
  printf '    "gemini-hooks": "%s"\n' "$gemini_hook_status"
  printf '  },\n'
  printf '  "skills": {\n%b\n  },\n' "$skills_json_body"
  printf '  "hooks": {"orchestration": {"mode": "%s", "status": "%s"}, "response_strategy": {"enabled": %s, "provider": "%s", "effective_provider": "%s", "status": "%s", "ollama_model": "%s"}},\n' "$(json_escape "$orchestration_mode")" "$orchestration_status" "$(json_value "$response_strategy_enabled")" "$(json_escape "$response_strategy_provider")" "$(json_escape "$response_strategy_effective_provider")" "$response_strategy_status" "$(json_escape "$response_strategy_ollama_model")"
  printf '  "automation": {"skill_improvement_schedule": "%s"}\n' "$skill_improvement_schedule"
  printf '}\n'
else
  printf 'AI Agent Config health: %s\n' "$(overall_status)"
  printf 'redacted: %s\n' "$([ "$redact_output" = "1" ] && printf yes || printf no)"
  printf 'config: %s\n' "$(display_path "$config_home")"
  printf 'state: %s (%s)\n' "$(display_path "$state_file")" "$(if [ "$state_loaded" = "true" ]; then printf loaded; else printf missing; fi)"
  printf 'homes: codex=%s claude=%s gemini=%s\n' "$(display_path "$codex_home")" "$(display_path "$claude_home")" "$(display_path "$gemini_home")"
  printf 'hooks-runtime-link: %s\n' "$(display_path "$hooks_runtime_path")"
  printf 'repository: %s branch=%s head=%s dirty=%s upstream=%s ahead=%s behind=%s\n' "$repo_status" "${repo_branch:-unknown}" "${repo_head:-unknown}" "$repo_dirty" "$(display_remote "${repo_upstream:-none}")" "$repo_ahead" "$repo_behind"
  printf 'github: %s\n' "$github_status"
  printf 'commands: git=%s gh=%s claude=%s codex=%s gemini=%s ollama=%s\n' "$git_status" "$gh_status" "$claude_status" "$codex_status" "$gemini_status" "$ollama_status"
  printf 'links: codex(AGENTS=%s shared=%s design=%s hooks=%s) claude(CLAUDE=%s shared=%s design=%s hooks=%s) gemini(GEMINI=%s shared=%s design=%s hooks=%s)\n' \
    "$codex_agents_status" "$codex_shared_status" "$codex_design_status" "$codex_hooks_doc_status" "$claude_entry_status" "$claude_shared_status" "$claude_design_status" "$claude_hooks_doc_status" "$gemini_entry_status" "$gemini_shared_status" "$gemini_design_status" "$gemini_hooks_doc_status"
  printf 'hooks: runtime=%s claude=%s codex-config=%s codex-hooks=%s gemini=%s\n' \
    "$hook_runtime_status" "$claude_hook_status" "$codex_config_status" "$codex_hook_status" "$gemini_hook_status"
  printf 'hooks-orchestration: mode=%s status=%s\n' \
    "$orchestration_mode" "$orchestration_status"
  printf 'hooks-response-strategy: enabled=%s provider=%s effective=%s status=%s\n' \
    "$response_strategy_enabled" "$response_strategy_provider" "$response_strategy_effective_provider" "$response_strategy_status"
  printf 'skills: %s\n' "$skills_text_summary"
  printf 'automation: skill-improvement-schedule=%s\n' "$skill_improvement_schedule"
fi

if [ "$strict" = "1" ] && [ "$(overall_status)" != "ok" ]; then
  exit 1
fi
