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

abs_dir() {
  dir=$(expand_home "$1")
  if [ ! -d "$dir" ]; then
    if [ "$dry_run" = "1" ]; then
      warn "would create directory: $dir"
    else
      mkdir -p "$dir"
    fi
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

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(abs_existing_dir "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
target_dir=$(abs_dir "${AI_AGENT_TARGET_DIR:-$PWD}")
skills_dir=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}

install_instructions=${AI_AGENT_INSTALL_INSTRUCTIONS:-1}
install_skills=${AI_AGENT_INSTALL_SKILLS:-1}
extra_skills_dirs=${AI_AGENT_EXTRA_SKILLS_DIRS:-}
conflict_mode=${AI_AGENT_CONFLICT_MODE:-backup}
protect_links=${AI_AGENT_PROTECT_LINKS:-auto}
timestamp=$(date +%Y%m%d-%H%M%S)
backup_dir=$(expand_home "${AI_AGENT_BACKUP_DIR:-$target_dir/.ai-agent-config-backups/$timestamp}")

case "$conflict_mode" in
  backup|skip|fail) ;;
  *) fail "AI_AGENT_CONFLICT_MODE must be backup, skip, or fail" ;;
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

protect_link() {
  path=$1
  case "$protect_links" in
    0|false|no)
      return 0
      ;;
    auto)
      is_darwin || return 0
      ;;
  esac
  if is_darwin; then
    chmod -h +a "everyone deny delete" "$path" 2>/dev/null || warn "could not apply delete protection to $path"
  fi
}

backup_existing() {
  dst=$1
  rel=$(printf '%s\n' "$dst" | sed 's#^/##')
  backup_path="$backup_dir/$rel"
  backup_parent=$(dirname "$backup_path")
  say "backup: $dst -> $backup_path"
  clear_link_protection "$dst"
  run mkdir -p "$backup_parent"
  run mv "$dst" "$backup_path"
}

install_link() {
  src=$1
  dst=$2

  [ -e "$src" ] || fail "source does not exist: $src"
  parent=$(dirname "$dst")
  [ -d "$parent" ] || run mkdir -p "$parent"

  if [ -L "$dst" ]; then
    current=$(readlink "$dst")
    if [ "$current" = "$src" ]; then
      say "ok: $dst -> $src"
      protect_link "$dst"
      return 0
    fi
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
      backup)
        backup_existing "$dst"
        ;;
    esac
  fi

  say "link: $dst -> $src"
  run ln -s "$src" "$dst"
  if [ "$dry_run" != "1" ]; then
    protect_link "$dst"
  fi
}

install_instruction_links() {
  src_root="$config_home/instructions"
  install_link "$src_root/AGENTS.md" "$target_dir/AGENTS.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$target_dir/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/CLAUDE.md" "$target_dir/CLAUDE.md"
  install_link "$src_root/GEMINI.md" "$target_dir/GEMINI.md"
  install_link "$src_root/.github/copilot-instructions.md" "$target_dir/.github/copilot-instructions.md"
}

install_skills_to_dir() {
  dst_root=$(abs_dir "$1")
  for skill in "$config_home"/skills/*; do
    [ -d "$skill" ] || continue
    [ -f "$skill/SKILL.md" ] || continue
    name=$(basename "$skill")
    install_link "$skill" "$dst_root/$name"
  done
}

say "AI agent config setup"
say "config: $config_home"
say "target: $target_dir"

if [ "$install_instructions" = "1" ]; then
  install_instruction_links
else
  say "skip: instruction links disabled"
fi

if [ "$install_skills" = "1" ]; then
  install_skills_to_dir "$skills_dir"
  if [ -n "$extra_skills_dirs" ]; then
    old_ifs=$IFS
    IFS=:
    for dir in $extra_skills_dirs; do
      [ -n "$dir" ] || continue
      install_skills_to_dir "$dir"
    done
    IFS=$old_ifs
  fi
else
  say "skip: skill links disabled"
fi

say "setup complete"
