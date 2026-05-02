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
    '~') printf '%s\n' "$HOME" ;;
    '~/'*) printf '%s/%s\n' "$HOME" "${1#~/}" ;;
    *) printf '%s\n' "$1" ;;
  esac
}

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

dry_run=${AI_AGENT_DRY_RUN:-0}
case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

if [ "$dry_run" != "1" ]; then
  command -v trash >/dev/null 2>&1 || fail "trash is required for uninstall"
fi

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(expand_home "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
codex_home=$(expand_home "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(expand_home "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
gemini_home=$(expand_home "${AI_AGENT_GEMINI_HOME:-$HOME/.gemini}")
skill_source_root="$config_home/skills"

run() {
  if [ "$dry_run" = "1" ]; then
    printf 'would run:'
    for arg in "$@"; do
      printf ' %s' "$arg"
    done
    printf '\n'
  else
    "$@"
  fi
}

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

trash_path() {
  path=$1
  label=$2
  if [ ! -e "$path" ] && [ ! -L "$path" ]; then
    return 0
  fi
  if [ "$dry_run" = "1" ]; then
    say "would trash $label: $path"
    return 0
  fi
  command -v trash >/dev/null 2>&1 || fail "trash is required for uninstall"
  clear_link_protection "$path"
  trash "$path"
  say "trashed $label: $path"
}

remove_managed_link() {
  dst=$1
  expected=$2
  label=$3
  if [ ! -L "$dst" ]; then
    if [ -e "$dst" ]; then
      warn "skip non-link $label: $dst"
    fi
    return 0
  fi
  current=$(readlink "$dst" 2>/dev/null || true)
  if [ "$current" != "$expected" ]; then
    warn "skip unmanaged link $label: $dst -> $current"
    return 0
  fi
  trash_path "$dst" "$label"
}

say "AI agent config uninstall (instructions only)"
say "config: $config_home"

src_root="$config_home/instructions"
remove_managed_link "$codex_home/AGENTS.md" "$src_root/AGENTS.md" "instruction link"
remove_managed_link "$codex_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
remove_managed_link "$codex_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

remove_managed_link "$claude_home/CLAUDE.md" "$src_root/CLAUDE.md" "instruction link"
remove_managed_link "$claude_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
remove_managed_link "$claude_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

remove_managed_link "$gemini_home/GEMINI.md" "$src_root/GEMINI.md" "instruction link"
remove_managed_link "$gemini_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "instruction link"
remove_managed_link "$gemini_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

remove_skill_links() {
  [ -d "$skill_source_root" ] || return 0

  for target_home in "$codex_home" "$claude_home" "$gemini_home"; do
    target_root="$target_home/skills"
    for skill_dir in "$skill_source_root"/*; do
      [ -d "$skill_dir" ] || continue
      skill_name=$(basename "$skill_dir")
      remove_managed_link "$target_root/$skill_name" "$skill_dir" "skill link"
    done
  done
}

remove_skill_links

say "uninstall complete"
