#!/bin/sh
set -eu

format=${AI_AGENT_HEALTH_FORMAT:-text}
strict=${AI_AGENT_HEALTH_STRICT:-0}

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
env_target_set=${AI_AGENT_TARGET_DIR+x}
env_target=${AI_AGENT_TARGET_DIR-}
env_skills_set=${AI_AGENT_SKILLS_DIR+x}
env_skills=${AI_AGENT_SKILLS_DIR-}

state_dir=${AI_AGENT_STATE_DIR:-$HOME/.ai-agent-config}
state_file=${AI_AGENT_STATE_FILE:-$(expand_home "$state_dir")/config.env}
state_loaded=false
if [ -f "$state_file" ]; then
  # shellcheck source=/dev/null
  . "$state_file"
  state_loaded=true
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_target_set:-}" = "x" ] && AI_AGENT_TARGET_DIR=$env_target
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(expand_home "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
target_dir=${AI_AGENT_TARGET_DIR:-}
skills_dir=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}

git_path=$(command_path git)
gh_path=$(command_path gh)
claude_path=$(command_path claude)
codex_path=$(command_path codex)
gemini_path=$(command_path gemini)

skill_improvement_schedule=unsupported
os=$(uname -s 2>/dev/null || printf unknown)
if [ "$os" = "Darwin" ]; then
  skill_improvement_label=${AI_AGENT_IMPROVEMENT_LABEL:-com.ai-agent-config.skill-improvement}
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
  if systemctl --user is-active ai-agent-config-skill-improvement.timer >/dev/null 2>&1; then
    skill_improvement_schedule=active
  elif systemctl --user is-enabled ai-agent-config-skill-improvement.timer >/dev/null 2>&1; then
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
  target_root=$3
  if [ -z "$target_root" ]; then
    printf 'unknown'
  elif [ ! -d "$target_root" ]; then
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

agents_link_status=$(link_status_for "${target_dir:-}/AGENTS.md" "$config_home/instructions/AGENTS.md" "$target_dir")
claude_link_status=$(link_status_for "${target_dir:-}/CLAUDE.md" "$config_home/instructions/CLAUDE.md" "$target_dir")
gemini_link_status=$(link_status_for "${target_dir:-}/GEMINI.md" "$config_home/instructions/GEMINI.md" "$target_dir")
shared_link_status=$(link_status_for "${target_dir:-}/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md" "$target_dir")

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

for status in "$gh_status" "$claude_status" "$codex_status" "$gemini_status" \
  "$agents_link_status" "$claude_link_status" "$gemini_link_status" "$shared_link_status" "$skill_status"; do
  [ "$status" = "ok" ] || mark_status warn
done

if [ "$format" = "json" ]; then
  printf '{\n'
  printf '  "overall": "%s",\n' "$(overall_status)"
  printf '  "config_home": "%s",\n' "$(json_escape "$config_home")"
  printf '  "state_file": "%s",\n' "$(json_escape "$state_file")"
  printf '  "state_loaded": %s,\n' "$(json_value "$state_loaded")"
  printf '  "target_dir": "%s",\n' "$(json_escape "$target_dir")"
  printf '  "skills_dir": "%s",\n' "$(json_escape "$skills_dir")"
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
  printf '    "AGENTS.md": "%s",\n' "$agents_link_status"
  printf '    "AI_AGENT_INSTRUCTIONS.md": "%s",\n' "$shared_link_status"
  printf '    "CLAUDE.md": "%s",\n' "$claude_link_status"
  printf '    "GEMINI.md": "%s",\n' "$gemini_link_status"
  printf '    "skill-design-research": "%s"\n' "$skill_status"
  printf '  },\n'
  printf '  "automation": {"skill_improvement_schedule": "%s"}\n' "$skill_improvement_schedule"
  printf '}\n'
else
  printf 'AI Agent Config health: %s\n' "$(overall_status)"
  printf 'config: %s\n' "$config_home"
  printf 'state: %s (%s)\n' "$state_file" "$(if [ "$state_loaded" = "true" ]; then printf loaded; else printf missing; fi)"
  printf 'target: %s\n' "${target_dir:-not set}"
  printf 'repository: %s branch=%s head=%s dirty=%s upstream=%s ahead=%s behind=%s\n' "$repo_status" "${repo_branch:-unknown}" "${repo_head:-unknown}" "$repo_dirty" "${repo_upstream:-none}" "$repo_ahead" "$repo_behind"
  printf 'github: %s\n' "$github_status"
  printf 'commands: git=%s gh=%s claude=%s codex=%s gemini=%s\n' "$git_status" "$gh_status" "$claude_status" "$codex_status" "$gemini_status"
  printf 'links: AGENTS.md=%s AI_AGENT_INSTRUCTIONS.md=%s CLAUDE.md=%s GEMINI.md=%s skill-design-research=%s\n' \
    "$agents_link_status" "$shared_link_status" "$claude_link_status" "$gemini_link_status" "$skill_status"
  printf 'automation: skill-improvement-schedule=%s\n' "$skill_improvement_schedule"
fi

if [ "$strict" = "1" ] && [ "$(overall_status)" != "ok" ]; then
  exit 1
fi
