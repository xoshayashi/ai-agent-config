#!/bin/sh
set -eu

format=${AI_AGENT_HEALTH_FORMAT:-text}
strict=${AI_AGENT_HEALTH_STRICT:-0}

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
if [ -f "$state_file" ]; then
  # shellcheck source=/dev/null
  . "$state_file"
  state_loaded=true
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_codex_home_set:-}" = "x" ] && AI_AGENT_CODEX_HOME=$env_codex_home
[ "${env_claude_home_set:-}" = "x" ] && AI_AGENT_CLAUDE_HOME=$env_claude_home
[ "${env_gemini_home_set:-}" = "x" ] && AI_AGENT_GEMINI_HOME=$env_gemini_home
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills
[ "${env_hooks_runtime_set:-}" = "x" ] && AI_AGENT_HOOKS_RUNTIME_LINK=$env_hooks_runtime

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
  needle=$3
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
    if grep -q "$needle" "$dst" 2>/dev/null; then
      printf 'appended'
    else
      printf 'present-unmanaged'
    fi
  else
    printf 'missing'
  fi
}

codex_agents_status=$(link_status_for "$codex_home/AGENTS.md" "$config_home/instructions/AGENTS.md")
codex_shared_status=$(link_status_for "$codex_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
codex_design_status=$(link_status_for "$codex_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
claude_entry_status=$(link_status_for "$claude_home/CLAUDE.md" "$config_home/instructions/CLAUDE.md")
claude_shared_status=$(link_status_for "$claude_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
claude_design_status=$(link_status_for "$claude_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
gemini_entry_status=$(link_status_for "$gemini_home/GEMINI.md" "$config_home/instructions/GEMINI.md")
gemini_shared_status=$(link_status_for "$gemini_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
gemini_design_status=$(link_status_for "$gemini_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
hook_runtime_status=$(link_status_for "$hooks_runtime_path" "$config_home/hooks")

claude_hook_status=$(hook_config_status_for "$claude_home/settings.json" "$config_home/hooks/claude/settings.json" "llm-config/hooks/scripts")
codex_config_status=$(hook_config_status_for "$codex_home/config.toml" "$config_home/hooks/codex/config.toml" "codex_hooks = true")
codex_hook_status=$(hook_config_status_for "$codex_home/hooks.json" "$config_home/hooks/codex/hooks.json" "llm-config/hooks/scripts")
gemini_hook_status=$(hook_config_status_for "$gemini_home/settings.json" "$config_home/hooks/gemini/settings.json" "llm-config/hooks/scripts")

skill_status=missing
skill_link="$skills_dir/skill-design-research"
if [ -L "$skill_link" ]; then
  if [ "$(readlink "$skill_link" 2>/dev/null || true)" = "$config_home/skills/skill-design-research" ]; then
    skill_status=ok
  else
    skill_status=mismatch
    mark_status warn
  fi
elif [ -e "$skill_link" ]; then
  skill_status=non-link
  mark_status warn
else
  mark_status warn
fi

for status in \
  "$gh_status" "$claude_status" "$codex_status" "$gemini_status" \
  "$codex_agents_status" "$codex_shared_status" "$codex_design_status" \
  "$claude_entry_status" "$claude_shared_status" "$claude_design_status" \
  "$gemini_entry_status" "$gemini_shared_status" "$gemini_design_status" \
  "$skill_status" "$hook_runtime_status" \
  "$claude_hook_status" "$codex_config_status" "$codex_hook_status" "$gemini_hook_status"; do
  [ "$status" = "ok" ] || [ "$status" = "appended" ] || mark_status warn
done

if [ "$format" = "json" ]; then
  printf '{\n'
  printf '  "overall": "%s",\n' "$(overall_status)"
  printf '  "config_home": "%s",\n' "$(json_escape "$config_home")"
  printf '  "state_file": "%s",\n' "$(json_escape "$state_file")"
  printf '  "state_loaded": %s,\n' "$(json_value "$state_loaded")"
  printf '  "codex_home": "%s",\n' "$(json_escape "$codex_home")"
  printf '  "claude_home": "%s",\n' "$(json_escape "$claude_home")"
  printf '  "gemini_home": "%s",\n' "$(json_escape "$gemini_home")"
  printf '  "skills_dir": "%s",\n' "$(json_escape "$skills_dir")"
  printf '  "hooks_runtime_link": "%s",\n' "$(json_escape "$hooks_runtime_path")"
  printf '  "commands": {\n'
  printf '    "git": {"status": "%s", "path": "%s"},\n' "$git_status" "$(json_escape "$git_path")"
  printf '    "gh": {"status": "%s", "path": "%s"},\n' "$gh_status" "$(json_escape "$gh_path")"
  printf '    "claude": {"status": "%s", "path": "%s"},\n' "$claude_status" "$(json_escape "$claude_path")"
  printf '    "codex": {"status": "%s", "path": "%s"},\n' "$codex_status" "$(json_escape "$codex_path")"
  printf '    "gemini": {"status": "%s", "path": "%s"}\n' "$gemini_status" "$(json_escape "$gemini_path")"
  printf '  },\n'
  printf '  "github": {"status": "%s"},\n' "$github_status"
  printf '  "repository": {"status": "%s", "branch": "%s", "head": "%s", "dirty": %s, "origin": "%s", "upstream": "%s", "ahead": %s, "behind": %s},\n' "$repo_status" "$(json_escape "$repo_branch")" "$(json_escape "$repo_head")" "$(json_value "$repo_dirty")" "$(json_escape "$repo_remote")" "$(json_escape "$repo_upstream")" "$(json_value "$repo_ahead")" "$(json_value "$repo_behind")"
  printf '  "links": {\n'
  printf '    "codex_AGENTS.md": "%s",\n' "$codex_agents_status"
  printf '    "codex_AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$codex_shared_status"
  printf '    "codex_DESIGN.md": "%s",\n' "$codex_design_status"
  printf '    "claude_CLAUDE.md": "%s",\n' "$claude_entry_status"
  printf '    "claude_AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$claude_shared_status"
  printf '    "claude_DESIGN.md": "%s",\n' "$claude_design_status"
  printf '    "gemini_GEMINI.md": "%s",\n' "$gemini_entry_status"
  printf '    "gemini_AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$gemini_shared_status"
  printf '    "gemini_DESIGN.md": "%s",\n' "$gemini_design_status"
  printf '    "hook-runtime": "%s",\n' "$hook_runtime_status"
  printf '    "claude-hooks": "%s",\n' "$claude_hook_status"
  printf '    "codex-config": "%s",\n' "$codex_config_status"
  printf '    "codex-hooks": "%s",\n' "$codex_hook_status"
  printf '    "gemini-hooks": "%s"\n' "$gemini_hook_status"
  printf '  },\n'
  printf '  "skills": {"skill-design-research": "%s"},\n' "$skill_status"
  printf '  "automation": {"skill_improvement_schedule": "%s"}\n' "$skill_improvement_schedule"
  printf '}\n'
else
  printf 'AI Agent Config health: %s\n' "$(overall_status)"
  printf 'config: %s\n' "$config_home"
  printf 'state: %s (%s)\n' "$state_file" "$(if [ "$state_loaded" = "true" ]; then printf loaded; else printf missing; fi)"
  printf 'homes: codex=%s claude=%s gemini=%s\n' "$codex_home" "$claude_home" "$gemini_home"
  printf 'hooks-runtime-link: %s\n' "$hooks_runtime_path"
  printf 'repository: %s branch=%s head=%s dirty=%s upstream=%s ahead=%s behind=%s\n' "$repo_status" "${repo_branch:-unknown}" "${repo_head:-unknown}" "$repo_dirty" "${repo_upstream:-none}" "$repo_ahead" "$repo_behind"
  printf 'github: %s\n' "$github_status"
  printf 'commands: git=%s gh=%s claude=%s codex=%s gemini=%s\n' "$git_status" "$gh_status" "$claude_status" "$codex_status" "$gemini_status"
  printf 'links: codex(AGENTS=%s shared=%s design=%s) claude(CLAUDE=%s shared=%s design=%s) gemini(GEMINI=%s shared=%s design=%s)\n' \
    "$codex_agents_status" "$codex_shared_status" "$codex_design_status" "$claude_entry_status" "$claude_shared_status" "$claude_design_status" "$gemini_entry_status" "$gemini_shared_status" "$gemini_design_status"
  printf 'hooks: runtime=%s claude=%s codex-config=%s codex-hooks=%s gemini=%s\n' \
    "$hook_runtime_status" "$claude_hook_status" "$codex_config_status" "$codex_hook_status" "$gemini_hook_status"
  printf 'skills: skill-design-research=%s\n' "$skill_status"
  printf 'automation: skill-improvement-schedule=%s\n' "$skill_improvement_schedule"
fi

if [ "$strict" = "1" ] && [ "$(overall_status)" != "ok" ]; then
  exit 1
fi
