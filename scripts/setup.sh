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

codex_home=$(abs_dir "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(abs_dir "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
gemini_home=$(abs_dir "${AI_AGENT_GEMINI_HOME:-$HOME/.gemini}")
skills_dir=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}
state_dir=${AI_AGENT_STATE_DIR:-$HOME/.llm-config}

install_instructions=${AI_AGENT_INSTALL_INSTRUCTIONS:-1}
install_skills=${AI_AGENT_INSTALL_SKILLS:-1}
install_hooks=${AI_AGENT_INSTALL_HOOKS:-1}
hooks_runtime_link=${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}
extra_skills_dirs=${AI_AGENT_EXTRA_SKILLS_DIRS:-}
conflict_mode=${AI_AGENT_CONFLICT_MODE:-backup}
persist_config=${AI_AGENT_PERSIST_CONFIG:-1}
require_llm_clis=${AI_AGENT_REQUIRE_LLM_CLIS:-1}
timestamp=$(date +%Y%m%d-%H%M%S)
backup_dir=$(expand_home "${AI_AGENT_BACKUP_DIR:-$state_dir/backups/$timestamp}")

if [ -n "${AI_AGENT_TARGET_DIR:-}" ]; then
  warn "AI_AGENT_TARGET_DIR is deprecated and ignored. Instructions are now installed globally."
fi
if [ -n "${AI_AGENT_HOOKS_SCOPE:-}" ]; then
  warn "AI_AGENT_HOOKS_SCOPE is deprecated and ignored. Hooks are now installed globally."
fi

case "$conflict_mode" in
  backup|skip|fail) ;;
  *) fail "AI_AGENT_CONFLICT_MODE must be backup, skip, or fail" ;;
esac

case "$persist_config" in
  0|1) ;;
  *) fail "AI_AGENT_PERSIST_CONFIG must be 0 or 1" ;;
esac

case "$require_llm_clis" in
  0|1) ;;
  *) fail "AI_AGENT_REQUIRE_LLM_CLIS must be 0 or 1" ;;
esac

case "$install_instructions" in
  0|1) ;;
  *) fail "AI_AGENT_INSTALL_INSTRUCTIONS must be 0 or 1" ;;
esac

case "$install_skills" in
  0|1) ;;
  *) fail "AI_AGENT_INSTALL_SKILLS must be 0 or 1" ;;
esac

case "$install_hooks" in
  0|1) ;;
  *) fail "AI_AGENT_INSTALL_HOOKS must be 0 or 1" ;;
esac

[ -n "$hooks_runtime_link" ] || fail "AI_AGENT_HOOKS_RUNTIME_LINK must not be empty"

if [ "$require_llm_clis" = "1" ]; then
  missing=
  for cli in claude codex gemini; do
    if ! command -v "$cli" >/dev/null 2>&1; then
      missing="$missing $cli"
    fi
  done
  if [ -n "$missing" ]; then
    fail "missing required LLM CLI(s):$missing. Install and login all of them, or set AI_AGENT_REQUIRE_LLM_CLIS=0 to continue at your own risk."
  fi
fi

ensure_trash_installed() {
  if command -v trash >/dev/null 2>&1; then
    return 0
  fi

  os=$(uname -s 2>/dev/null || printf unknown)
  pkg_cmd=""
  case "$os" in
    Darwin)
      command -v brew >/dev/null 2>&1 && pkg_cmd="brew install trash"
      ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        pkg_cmd="sudo apt-get install -y trash-cli"
      elif command -v dnf >/dev/null 2>&1; then
        pkg_cmd="sudo dnf install -y trash-cli"
      elif command -v pacman >/dev/null 2>&1; then
        pkg_cmd="sudo pacman -S --noconfirm trash-cli"
      fi
      ;;
  esac

  if [ -z "$pkg_cmd" ]; then
    fail "trash is required for safe removal but not installed, and no supported package manager was found on $os. Install trash (macOS) or trash-cli (Linux) manually, then re-run."
  fi

  say ""
  say "trash command not found on this system."
  say "  Proposed install: $pkg_cmd"

  if [ "$dry_run" = "1" ]; then
    say "  would run the proposed command and continue"
    return 0
  fi

  if [ "${AI_AGENT_ASSUME_YES:-0}" = "1" ]; then
    say "  AI_AGENT_ASSUME_YES=1 set; running install without prompt"
  elif [ ! -t 0 ]; then
    fail "stdin is not a TTY; cannot prompt. Run '$pkg_cmd' manually then re-run, or set AI_AGENT_ASSUME_YES=1."
  else
    printf '  Run this install command now? [y/N]: ' >&2
    IFS= read -r answer || answer=""
    case "$answer" in
      Y|y|YES|yes|Yes) ;;
      *) fail "declined; run '$pkg_cmd' yourself, then re-run setup" ;;
    esac
  fi

  # shellcheck disable=SC2086
  if ! eval "$pkg_cmd"; then
    fail "trash install failed: $pkg_cmd"
  fi

  if ! command -v trash >/dev/null 2>&1; then
    fail "trash still not on PATH after install; check your PATH and try again"
  fi
  say "trash installed successfully."
}

ensure_trash_installed

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

quote_sh() {
  printf "'"
  printf '%s' "$1" | sed "s/'/'\\\\''/g"
  printf "'"
}

write_state_config() {
  [ "$persist_config" = "1" ] || {
    say "skip: persistent setup state disabled"
    return 0
  }

  state_root=$(abs_dir "$state_dir")
  state_file="$state_root/config.env"
  say "state: $state_file"

  if [ "$dry_run" = "1" ]; then
    warn "would write persistent setup state: $state_file"
    return 0
  fi

  {
    printf '%s\n' '# Generated by llm-config scripts/setup.sh.'
    printf '%s\n' '# Used by scripts/update.sh to re-apply setup after pulling updates.'
    printf 'AI_AGENT_CONFIG_HOME=%s\n' "$(quote_sh "$config_home")"
    printf 'AI_AGENT_CODEX_HOME=%s\n' "$(quote_sh "$codex_home")"
    printf 'AI_AGENT_CLAUDE_HOME=%s\n' "$(quote_sh "$claude_home")"
    printf 'AI_AGENT_GEMINI_HOME=%s\n' "$(quote_sh "$gemini_home")"
    printf 'AI_AGENT_SKILLS_DIR=%s\n' "$(quote_sh "$skills_dir")"
    printf 'AI_AGENT_EXTRA_SKILLS_DIRS=%s\n' "$(quote_sh "$extra_skills_dirs")"
    printf 'AI_AGENT_INSTALL_INSTRUCTIONS=%s\n' "$(quote_sh "$install_instructions")"
    printf 'AI_AGENT_INSTALL_SKILLS=%s\n' "$(quote_sh "$install_skills")"
    printf 'AI_AGENT_INSTALL_HOOKS=%s\n' "$(quote_sh "$install_hooks")"
    printf 'AI_AGENT_HOOKS_RUNTIME_LINK=%s\n' "$(quote_sh "$hooks_runtime_link")"
    printf 'AI_AGENT_CONFLICT_MODE=%s\n' "$(quote_sh "$conflict_mode")"
    printf 'AI_AGENT_REQUIRE_LLM_CLIS=%s\n' "$(quote_sh "$require_llm_clis")"
    printf 'AI_AGENT_STATE_DIR=%s\n' "$(quote_sh "$state_root")"
    printf 'AI_AGENT_STATE_FILE=%s\n' "$(quote_sh "$state_file")"
  } > "$state_file"
  chmod 600 "$state_file"
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

backup_copy_existing() {
  # Like backup_existing, but COPIES the file instead of moving it. Used
  # before in-place edits (e.g. merge-hook-config.py) so the user has a
  # recovery path if the merge corrupts the destination, while the
  # destination remains in place for the merge to operate on.
  dst=$1
  rel=$(printf '%s\n' "$dst" | sed 's#^/##')
  backup_path="$backup_dir/$rel"
  backup_parent=$(dirname "$backup_path")
  say "backup: copy $dst -> $backup_path"
  run mkdir -p "$backup_parent"
  run cp -p "$dst" "$backup_path"
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
      clear_link_protection "$dst"
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
}

install_instruction_links() {
  src_root="$config_home/instructions"

  install_link "$src_root/AGENTS.md" "$codex_home/AGENTS.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$codex_home/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/DESIGN.md" "$codex_home/DESIGN.md"
  install_link "$src_root/HOOKS.md" "$codex_home/HOOKS.md"

  install_link "$src_root/CLAUDE.md" "$claude_home/CLAUDE.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$claude_home/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/DESIGN.md" "$claude_home/DESIGN.md"
  install_link "$src_root/HOOKS.md" "$claude_home/HOOKS.md"

  install_link "$src_root/GEMINI.md" "$gemini_home/GEMINI.md"
  install_link "$src_root/AI_AGENT_INSTRUCTIONS.md" "$gemini_home/AI_AGENT_INSTRUCTIONS.md"
  install_link "$src_root/DESIGN.md" "$gemini_home/DESIGN.md"
  install_link "$src_root/HOOKS.md" "$gemini_home/HOOKS.md"
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

install_hook_runtime_link() {
  dst=$(expand_home "$hooks_runtime_link")
  src="$config_home/hooks"
  if [ "$dst" = "$src" ]; then
    say "ok: hook runtime path is repository hook directory: $dst"
    return 0
  fi
  install_link "$src" "$dst"
}

install_hook_config() {
  src=$1
  dst=$2
  kind=$3

  [ -e "$src" ] || fail "source does not exist: $src"

  if [ -L "$dst" ]; then
    current=$(readlink "$dst")
    if [ "$current" = "$src" ]; then
      say "ok: $dst -> $src"
      clear_link_protection "$dst"
      return 0
    fi
  fi

  if [ ! -e "$dst" ] && [ ! -L "$dst" ]; then
    install_link "$src" "$dst"
    return 0
  fi

  [ -f "$dst" ] || fail "hook config destination is not a regular file: $dst"
  command -v python3 >/dev/null 2>&1 || fail "python3 is required to append hook settings into existing config: $dst"

  say "append: existing CLI settings preserved; merging only managed Hook entries"
  say "append: $dst <= $src"
  if [ "$dry_run" = "1" ]; then
    python3 "$config_home/scripts/merge-hook-config.py" "$kind" "$src" "$dst" --dry-run
  else
    case "$conflict_mode" in
      backup) backup_copy_existing "$dst" ;;
      *) : ;;
    esac
    python3 "$config_home/scripts/merge-hook-config.py" "$kind" "$src" "$dst"
  fi
}

install_hook_links() {
  command -v python3 >/dev/null 2>&1 || fail "python3 is required for shared Hook scripts"
  src_root="$config_home/hooks"
  install_hook_runtime_link
  install_hook_config "$src_root/claude/settings.json" "$claude_home/settings.json" json
  install_hook_config "$src_root/codex/config.toml" "$codex_home/config.toml" codex-config
  install_hook_config "$src_root/codex/hooks.json" "$codex_home/hooks.json" json
  install_hook_config "$src_root/gemini/settings.json" "$gemini_home/settings.json" json
}

say "AI agent config setup (global mode)"
say "config: $config_home"
say "codex home: $codex_home"
say "claude home: $claude_home"
say "gemini home: $gemini_home"
if [ "$install_hooks" = "1" ]; then
  say "note: Codex multi-LLM orchestration Hook is installed but disabled by default. Enable it only when needed with AI_AGENT_HOOKS_ENABLE_MULTILLM_ORCHESTRATION=1."
fi

if [ "$install_instructions" = "1" ]; then
  install_instruction_links
else
  say "skip: instruction links disabled"
fi

if [ "$install_skills" = "1" ]; then
  install_skills_to_dir "$skills_dir"
  if [ -n "$extra_skills_dirs" ]; then
    had_ifs=${IFS+x}
    old_ifs=${IFS-}
    IFS=:
    for dir in $extra_skills_dirs; do
      [ -n "$dir" ] || continue
      install_skills_to_dir "$dir"
    done
    if [ "$had_ifs" = "x" ]; then
      IFS=$old_ifs
    else
      unset IFS
    fi
  fi
else
  say "skip: skill links disabled"
fi

if [ "$install_hooks" = "1" ]; then
  install_hook_links
else
  say "skip: hook links disabled"
fi

write_state_config
say "setup complete"
