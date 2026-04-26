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
env_target_set=${AI_AGENT_TARGET_DIR+x}
env_target=${AI_AGENT_TARGET_DIR-}
env_skills_set=${AI_AGENT_SKILLS_DIR+x}
env_skills=${AI_AGENT_SKILLS_DIR-}
env_extra_skills_set=${AI_AGENT_EXTRA_SKILLS_DIRS+x}
env_extra_skills=${AI_AGENT_EXTRA_SKILLS_DIRS-}

state_dir=${AI_AGENT_STATE_DIR:-$HOME/.ai-agent-config}
state_file=${AI_AGENT_STATE_FILE:-$(expand_home "$state_dir")/config.env}
if [ -f "$state_file" ]; then
  # shellcheck source=/dev/null
  . "$state_file"
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_target_set:-}" = "x" ] && AI_AGENT_TARGET_DIR=$env_target
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills
[ "${env_extra_skills_set:-}" = "x" ] && AI_AGENT_EXTRA_SKILLS_DIRS=$env_extra_skills

dry_run=${AI_AGENT_DRY_RUN:-0}
uninstall_instructions=${AI_AGENT_UNINSTALL_INSTRUCTIONS:-1}
uninstall_skills=${AI_AGENT_UNINSTALL_SKILLS:-1}
uninstall_state=${AI_AGENT_UNINSTALL_STATE:-1}

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

case "$uninstall_state" in
  0|1) ;;
  *) fail "AI_AGENT_UNINSTALL_STATE must be 0 or 1" ;;
esac

if [ "$dry_run" != "1" ]; then
  command -v trash >/dev/null 2>&1 || fail "trash is required for safe uninstall"
fi

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(abs_existing_dir "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
target_dir=${AI_AGENT_TARGET_DIR:-}
[ -n "$target_dir" ] || fail "AI_AGENT_TARGET_DIR is not set and no saved setup state was found"
target_dir=$(expand_home "$target_dir")
target_missing=0
if [ -d "$target_dir" ]; then
  target_dir=$(CDPATH= cd "$target_dir" && pwd -P)
else
  target_missing=1
  warn "target directory is missing; instruction links will be skipped: $target_dir"
fi
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
    [ -e "$dst" ] && warn "skip non-link $label: $dst"
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
  if [ "$target_missing" = "1" ]; then
    warn "skip instruction links because target directory is missing: $target_dir"
    return 0
  fi
  src_root="$config_home/instructions"
  uninstall_managed_link "$target_dir/AGENTS.md" "$src_root/AGENTS.md" "instruction link"
  uninstall_managed_link "$target_dir/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
  uninstall_managed_link "$target_dir/CLAUDE.md" "$src_root/CLAUDE.md" "instruction link"
  uninstall_managed_link "$target_dir/GEMINI.md" "$src_root/GEMINI.md" "instruction link"
  uninstall_managed_link "$target_dir/.github/copilot-instructions.md" "$src_root/.github/copilot-instructions.md" "instruction link"
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

say "AI agent config uninstall"
say "config: $config_home"
say "target: $target_dir"
say "state: $state_file"

if [ "$uninstall_instructions" = "1" ]; then
  uninstall_instruction_links
else
  say "skip: instruction uninstall disabled"
fi

if [ "$uninstall_skills" = "1" ]; then
  uninstall_skills_from_dir "$skills_dir"
  if [ -n "$extra_skills_dirs" ]; then
    old_ifs=$IFS
    IFS=:
    for dir in $extra_skills_dirs; do
      [ -n "$dir" ] || continue
      uninstall_skills_from_dir "$dir"
    done
    IFS=$old_ifs
  fi
else
  say "skip: skill uninstall disabled"
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
