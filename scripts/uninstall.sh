#!/bin/sh
set -eu

say() {
  printf '%s\n' "$*"
}

warn() {
  printf 'warning: %s\n' "$*" >&2
}

fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

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

abs_existing_dir() {
  dir=$(expand_home "$1")
  [ -d "$dir" ] || fail "directory does not exist: $dir"
  (cd "$dir" && pwd -P)
}

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

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
env_extra_skills_set=${AI_AGENT_EXTRA_SKILLS_DIRS+x}
env_extra_skills=${AI_AGENT_EXTRA_SKILLS_DIRS-}
env_hooks_set=${AI_AGENT_INSTALL_HOOKS+x}
env_hooks=${AI_AGENT_INSTALL_HOOKS-}
env_hooks_runtime_set=${AI_AGENT_HOOKS_RUNTIME_LINK+x}
env_hooks_runtime=${AI_AGENT_HOOKS_RUNTIME_LINK-}

state_dir=${AI_AGENT_STATE_DIR:-$HOME/.llm-config}
state_file=${AI_AGENT_STATE_FILE:-$(expand_home "$state_dir")/config.env}
if [ -f "$state_file" ]; then
  # shellcheck source=/dev/null
  . "$state_file"
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_codex_home_set:-}" = "x" ] && AI_AGENT_CODEX_HOME=$env_codex_home
[ "${env_claude_home_set:-}" = "x" ] && AI_AGENT_CLAUDE_HOME=$env_claude_home
[ "${env_gemini_home_set:-}" = "x" ] && AI_AGENT_GEMINI_HOME=$env_gemini_home
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills
[ "${env_extra_skills_set:-}" = "x" ] && AI_AGENT_EXTRA_SKILLS_DIRS=$env_extra_skills
[ "${env_hooks_set:-}" = "x" ] && AI_AGENT_INSTALL_HOOKS=$env_hooks
[ "${env_hooks_runtime_set:-}" = "x" ] && AI_AGENT_HOOKS_RUNTIME_LINK=$env_hooks_runtime

dry_run=${AI_AGENT_DRY_RUN:-0}
uninstall_instructions=${AI_AGENT_UNINSTALL_INSTRUCTIONS:-1}
uninstall_skills=${AI_AGENT_UNINSTALL_SKILLS:-1}
uninstall_hooks=${AI_AGENT_UNINSTALL_HOOKS:-1}
uninstall_state=${AI_AGENT_UNINSTALL_STATE:-1}
hooks_runtime_link=${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}

case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

case "$uninstall_instructions" in
  0|1) ;;
  *) fail "AI_AGENT_UNINSTALL_INSTRUCTIONS must be 0 or 1" ;;
esac

case "$uninstall_skills" in
  0|1) ;;
  *) fail "AI_AGENT_UNINSTALL_SKILLS must be 0 or 1" ;;
esac

case "$uninstall_hooks" in
  0|1) ;;
  *) fail "AI_AGENT_UNINSTALL_HOOKS must be 0 or 1" ;;
esac

[ -n "$hooks_runtime_link" ] || fail "AI_AGENT_HOOKS_RUNTIME_LINK must not be empty"

case "$uninstall_state" in
  0|1) ;;
  *) fail "AI_AGENT_UNINSTALL_STATE must be 0 or 1" ;;
esac

if [ "$dry_run" != "1" ]; then
  command -v trash >/dev/null 2>&1 || fail "trash is required for safe uninstall"
fi

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(abs_existing_dir "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
codex_home=$(expand_home "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(expand_home "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
gemini_home=$(expand_home "${AI_AGENT_GEMINI_HOME:-$HOME/.gemini}")
skills_dir=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}
extra_skills_dirs=${AI_AGENT_EXTRA_SKILLS_DIRS:-}

is_darwin() {
  [ "$(uname -s 2>/dev/null || printf unknown)" = "Darwin" ]
}

clear_link_protection() {
  path=$1
  [ -L "$path" ] || return 0
  if is_darwin; then
    chmod -h -N "$path" 2>/dev/null || true
  fi
}

safe_trash() {
  path=$1
  label=$2
  if [ "$dry_run" = "1" ]; then
    say "would trash $label: $path"
  else
    clear_link_protection "$path"
    trash "$path"
    say "trashed $label: $path"
  fi
}

uninstall_managed_link() {
  dst=$1
  expected=$2
  label=$3

  if [ ! -L "$dst" ]; then
    if [ -e "$dst" ]; then
      warn "skip non-link $label: $dst"
    fi
    return 0
  fi

  current=$(readlink "$dst")
  if [ "$current" != "$expected" ]; then
    warn "skip unmanaged link $label: $dst -> $current"
    return 0
  fi

  safe_trash "$dst" "$label"
}

uninstall_instruction_links() {
  src_root="$config_home/instructions"
  uninstall_managed_link "$codex_home/AGENTS.md" "$src_root/AGENTS.md" "instruction link"
  uninstall_managed_link "$codex_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
  uninstall_managed_link "$codex_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

  uninstall_managed_link "$claude_home/CLAUDE.md" "$src_root/CLAUDE.md" "instruction link"
  uninstall_managed_link "$claude_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
  uninstall_managed_link "$claude_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

  uninstall_managed_link "$gemini_home/GEMINI.md" "$src_root/GEMINI.md" "instruction link"
  uninstall_managed_link "$gemini_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
  uninstall_managed_link "$gemini_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"
}

uninstall_skills_from_dir() {
  dst_root=$(expand_home "$1")
  [ -d "$dst_root" ] || {
    warn "skip missing skills directory: $dst_root"
    return 0
  }
  for skill in "$config_home"/skills/*; do
    [ -d "$skill" ] || continue
    [ -f "$skill/SKILL.md" ] || continue
    name=$(basename "$skill")
    uninstall_managed_link "$dst_root/$name" "$skill" "skill link"
  done
}

uninstall_hook_runtime_link() {
  uninstall_managed_link "$(expand_home "$hooks_runtime_link")" "$config_home/hooks" "hook runtime link"
}

uninstall_hook_config() {
  dst=$1
  expected=$2
  kind=$3

  if [ -L "$dst" ]; then
    uninstall_managed_link "$dst" "$expected" "hook config link"
    return 0
  fi

  if [ -f "$dst" ]; then
    command -v python3 >/dev/null 2>&1 || fail "python3 is required to remove managed hook settings from existing config: $dst"
    if [ "$dry_run" = "1" ]; then
      python3 "$config_home/scripts/merge-hook-config.py" "$kind" "$expected" "$dst" --remove --dry-run
    else
      python3 "$config_home/scripts/merge-hook-config.py" "$kind" "$expected" "$dst" --remove
    fi
    return 0
  fi

  if [ -e "$dst" ]; then
    warn "skip non-file hook config: $dst"
  fi
}

uninstall_user_hook_links() {
  src_root="$config_home/hooks"
  uninstall_hook_config "$claude_home/settings.json" "$src_root/claude/settings.json" json
  uninstall_hook_config "$codex_home/config.toml" "$src_root/codex/config.toml" codex-config
  uninstall_hook_config "$codex_home/hooks.json" "$src_root/codex/hooks.json" json
  uninstall_hook_config "$gemini_home/settings.json" "$src_root/gemini/settings.json" json
}

uninstall_hook_links() {
  uninstall_hook_runtime_link
  uninstall_user_hook_links
}

if [ -n "${AI_AGENT_TARGET_DIR:-}" ]; then
  warn "AI_AGENT_TARGET_DIR is deprecated and ignored."
fi
if [ -n "${AI_AGENT_HOOKS_SCOPE:-}" ]; then
  warn "AI_AGENT_HOOKS_SCOPE is deprecated and ignored."
fi

say "AI agent config uninstall (global mode)"
say "config: $config_home"
say "codex home: $codex_home"
say "claude home: $claude_home"
say "gemini home: $gemini_home"
say "state: $state_file"

if [ "$uninstall_instructions" = "1" ]; then
  uninstall_instruction_links
else
  say "skip: instruction uninstall disabled"
fi

if [ "$uninstall_skills" = "1" ]; then
  uninstall_skills_from_dir "$skills_dir"
  if [ -n "$extra_skills_dirs" ]; then
    had_ifs=${IFS+x}
    old_ifs=${IFS-}
    IFS=:
    for dir in $extra_skills_dirs; do
      [ -n "$dir" ] || continue
      uninstall_skills_from_dir "$dir"
    done
    if [ "$had_ifs" = "x" ]; then
      IFS=$old_ifs
    else
      unset IFS
    fi
  fi
else
  say "skip: skill uninstall disabled"
fi

if [ "$uninstall_hooks" = "1" ]; then
  uninstall_hook_links
else
  say "skip: hook uninstall disabled"
fi

if [ "$uninstall_state" = "1" ]; then
  if [ -e "$state_file" ]; then
    safe_trash "$state_file" "state file"
  else
    warn "skip missing state file: $state_file"
  fi
else
  say "skip: state uninstall disabled"
fi

say "uninstall complete"
