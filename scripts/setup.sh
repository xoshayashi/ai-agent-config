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

abs_dir() {
  dir=$(expand_home "$1")
  if [ ! -d "$dir" ]; then
    run mkdir -p "$dir"
  fi
  if [ -d "$dir" ]; then
    (cd "$dir" && pwd -P)
  else
    printf '%s\n' "$dir"
  fi
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

dry_run=${AI_AGENT_DRY_RUN:-0}
case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

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

conflict_mode=${AI_AGENT_CONFLICT_MODE:-skip}
require_llm_clis=${AI_AGENT_REQUIRE_LLM_CLIS:-1}

case "$conflict_mode" in
  skip|fail|replace) ;;
  *) fail "AI_AGENT_CONFLICT_MODE must be skip, fail, or replace" ;;
esac

case "$require_llm_clis" in
  0|1) ;;
  *) fail "AI_AGENT_REQUIRE_LLM_CLIS must be 0 or 1" ;;
esac

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(abs_existing_dir "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
codex_home=$(abs_dir "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(abs_dir "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
gemini_home=$(abs_dir "${AI_AGENT_GEMINI_HOME:-$HOME/.gemini}")
timestamp=$(date +%Y%m%d-%H%M%S)
skill_source_root="$config_home/skills"
retired_skill_names="daily-llm-history-instruction-review"

if [ -n "${AI_AGENT_TARGET_DIR:-}" ]; then
  warn "AI_AGENT_TARGET_DIR is ignored. Instructions are installed globally."
fi

if [ "$require_llm_clis" = "1" ]; then
  missing=
  for cli in claude codex gemini; do
    if ! command -v "$cli" >/dev/null 2>&1; then
      missing="$missing $cli"
    fi
  done
  if [ -n "$missing" ]; then
    fail "missing required LLM CLI(s):$missing. Install and login all of them, or set AI_AGENT_REQUIRE_LLM_CLIS=0."
  fi
fi

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

backup_root_for() {
  dst=$1
  parent=$(dirname "$dst")
  case "$parent" in
    */skills) printf '%s/skill-backups\n' "$(dirname "$parent")" ;;
    *) printf '%s/.ai-agent-config-backups\n' "$parent" ;;
  esac
}

unique_backup_path() {
  backup_dir=$1
  backup_name=$2
  candidate="$backup_dir/$backup_name"
  suffix=1
  while [ -e "$candidate" ] || [ -L "$candidate" ]; do
    candidate="$backup_dir/$backup_name.$suffix"
    suffix=$((suffix + 1))
  done
  printf '%s\n' "$candidate"
}

replace_existing() {
  dst=$1
  backup_dir=$(backup_root_for "$dst")
  backup_path=$(unique_backup_path "$backup_dir" "$(basename "$dst").backup-$timestamp")
  say "replace: $dst -> $backup_path"
  run mkdir -p "$backup_dir"
  if [ "$dry_run" = "1" ]; then
    run mv "$dst" "$backup_path"
    return 0
  fi
  clear_link_protection "$dst"
  mv "$dst" "$backup_path"
}

trash_managed_path() {
  path=$1
  label=$2
  if [ ! -e "$path" ] && [ ! -L "$path" ]; then
    return 0
  fi
  if ! command -v trash >/dev/null 2>&1; then
    warn "trash unavailable; skip $label cleanup: $path"
    return 0
  fi
  if [ "$dry_run" = "1" ]; then
    say "would trash $label: $path"
    return 0
  fi
  clear_link_protection "$path"
  say "trash $label: $path"
  trash "$path"
}

install_link() {
  src=$1
  dst=$2
  [ -e "$src" ] || fail "source does not exist: $src"
  parent=$(dirname "$dst")
  [ -d "$parent" ] || run mkdir -p "$parent"

  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    say "ok: $dst -> $src"
    clear_link_protection "$dst"
    return 0
  fi

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    case "$conflict_mode" in
      skip)
        warn "skipping existing path: $dst"
        return 0
        ;;
      fail)
        fail "path already exists: $dst"
        ;;
      replace)
        replace_existing "$dst"
        ;;
    esac
  fi

  say "link: $dst -> $src"
  run ln -s "$src" "$dst"
}

install_instruction_links() {
  src_root="$config_home/instructions"
  install_link "$src_root/AGENTS.md" "$codex_home/AGENTS.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$codex_home/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/DESIGN.md" "$codex_home/DESIGN.md"

  install_link "$src_root/CLAUDE.md" "$claude_home/CLAUDE.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$claude_home/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/DESIGN.md" "$claude_home/DESIGN.md"

  install_link "$src_root/GEMINI.md" "$gemini_home/GEMINI.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$gemini_home/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/DESIGN.md" "$gemini_home/DESIGN.md"
}

install_skill_links() {
  [ -d "$skill_source_root" ] || return 0

  for target_home in "$codex_home" "$claude_home" "$gemini_home"; do
    target_root="$target_home/skills"
    run mkdir -p "$target_root"

    for skill_dir in "$skill_source_root"/*; do
      [ -d "$skill_dir" ] || continue
      skill_name=$(basename "$skill_dir")
      case "$skill_name" in
        *.backup-*)
          warn "skip backup skill source: $skill_dir"
          continue
          ;;
      esac
      install_link "$skill_dir" "$target_root/$skill_name"
    done
  done
}

remove_retired_skill_links() {
  for target_home in "$codex_home" "$claude_home" "$gemini_home"; do
    target_root="$target_home/skills"
    for skill_name in $retired_skill_names; do
      dst="$target_root/$skill_name"
      expected="$skill_source_root/$skill_name"
      if [ ! -L "$dst" ]; then
        if [ -e "$dst" ]; then
          warn "skip non-link retired skill path: $dst"
        fi
        continue
      fi
      current=$(readlink "$dst" 2>/dev/null || true)
      if [ "$current" != "$expected" ]; then
        warn "skip unmanaged retired skill link: $dst -> $current"
        continue
      fi
      trash_managed_path "$dst" "retired skill link"
    done
  done
}

move_skill_backups_out_of_root() {
  skill_root=$1
  backup_root=$2
  [ -d "$skill_root" ] || return 0

  for backup_path in "$skill_root"/*.backup-*; do
    [ -e "$backup_path" ] || [ -L "$backup_path" ] || continue
    backup_dst=$(unique_backup_path "$backup_root" "$(basename "$backup_path")")
    say "move skill backup out of skill root: $backup_path -> $backup_dst"
    run mkdir -p "$backup_root"
    if [ "$dry_run" = "1" ]; then
      run mv "$backup_path" "$backup_dst"
      continue
    fi
    clear_link_protection "$backup_path"
    mv "$backup_path" "$backup_dst"
  done
}

move_existing_skill_backups() {
  for target_home in "$codex_home" "$claude_home" "$gemini_home"; do
    move_skill_backups_out_of_root "$target_home/skills" "$target_home/skill-backups"
  done

  legacy_agents_home=$(expand_home "${AI_AGENT_LEGACY_AGENTS_HOME:-$HOME/.agents}")
  move_skill_backups_out_of_root "$legacy_agents_home/skills" "$legacy_agents_home/skill-backups"
}

say "AI agent config setup (instructions only)"
say "config: $config_home"
say "codex home: $codex_home"
say "claude home: $claude_home"
say "gemini home: $gemini_home"

move_existing_skill_backups
install_instruction_links
remove_retired_skill_links
install_skill_links

say "setup complete"
