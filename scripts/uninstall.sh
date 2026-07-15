#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1


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
home_dir=$(expand_home "${AI_AGENT_HOME:-$HOME}")
skill_source_root="$config_home/skills"
retired_skill_names="daily-llm-history-instruction-review"

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

remove_skill_links() {
  [ -d "$skill_source_root" ] || return 0

  for target_home in "$codex_home" "$claude_home"; do
    target_root="$target_home/skills"
    for skill_dir in "$skill_source_root"/*; do
      [ -d "$skill_dir" ] || continue
      skill_name=$(basename "$skill_dir")
      remove_managed_link "$target_root/$skill_name" "$skill_dir" "skill link"
    done
  done
}

remove_retired_skill_links() {
  for target_home in "$codex_home" "$claude_home"; do
    target_root="$target_home/skills"
    for skill_name in $retired_skill_names; do
      remove_managed_link "$target_root/$skill_name" "$skill_source_root/$skill_name" "retired skill link"
    done
  done
}

remove_shell_links() {
  remove_managed_link "$home_dir/.zshrc" "$config_home/shell/.zshrc" "shell dotfile link"
}

remove_notification_hooks() {
  helper="$config_home/scripts/install-notifications.py"
  if [ ! -f "$helper" ]; then
    warn "missing $helper; skip notification hook removal"
    return 0
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not found; skip notification hook removal"
    return 0
  fi
  # A function's positional parameters are local in POSIX sh and restored on
  # return, so building the helper's argv with `set --` does not affect $@
  # in the caller.
  set -- --mode uninstall \
    --config-home "$config_home" \
    --claude-home "$claude_home" \
    --codex-home "$codex_home"
  if [ "$dry_run" = "1" ]; then
    set -- "$@" --dry-run
  fi
  python3 "$helper" "$@"
  # Codex's hooks.json exists only for hooks. When the merge leaves it empty,
  # trash it so uninstall fully restores the pre-install state.
  hooks_json="$codex_home/hooks.json"
  if [ "$dry_run" != "1" ] && [ -f "$hooks_json" ] \
    && [ "$(tr -d ' \t\n' < "$hooks_json" 2>/dev/null)" = "{}" ]; then
    trash_path "$hooks_json" "empty codex hooks.json"
  fi
}

say "AI agent config uninstall"
say "config: $config_home"

src_root="$config_home/instructions"
remove_managed_link "$codex_home/AGENTS.md" "$src_root/AGENTS.md" "instruction link"
remove_managed_link "$codex_home/INSTRUCTIONS.md" "$src_root/INSTRUCTIONS.md" "instruction link"
remove_managed_link "$codex_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

remove_managed_link "$claude_home/CLAUDE.md" "$src_root/CLAUDE.md" "instruction link"
remove_managed_link "$claude_home/INSTRUCTIONS.md" "$src_root/INSTRUCTIONS.md" "instruction link"
remove_managed_link "$claude_home/DESIGN.md" "$src_root/DESIGN.md" "instruction link"

# 旧名 AI_AGENT_INSTRUCTIONS.md へのリンクが残っていれば併せて外す(INSTRUCTIONS.md へ改名済み)。
remove_managed_link "$codex_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "retired instruction link"
remove_managed_link "$claude_home/AI_AGENT_INSTRUCTIONS.md" "$src_root/AI_AGENT_INSTRUCTIONS.md" "retired instruction link"

remove_shell_links

# Preserve skill-backups directories. They may contain user files moved out of
# active skill roots so backup folders are not loaded as skills.
remove_skill_links
remove_retired_skill_links
remove_notification_hooks

say "uninstall complete"
