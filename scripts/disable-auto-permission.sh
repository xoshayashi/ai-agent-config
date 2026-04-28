#!/bin/sh
# Reverse scripts/enable-auto-permission.sh:
#   - remove the managed marker block from the user's shell rc file
#   - remove the managed symlink at $AI_AGENT_SHELL_ALIAS_LINK
#
# Idempotent: safe to run multiple times. Skips silently when nothing is found.

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

shell_alias_link=${AI_AGENT_SHELL_ALIAS_LINK:-$HOME/.llm-config/auto-permission.sh}
dst=$(expand_home "$shell_alias_link")

dry_run=${AI_AGENT_DRY_RUN:-0}
case "$dry_run" in 0|1) ;; *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;; esac

detect_shell_rc() {
  case "${SHELL:-}" in
    */zsh) printf '%s/.zshrc\n' "$HOME" ;;
    */bash)
      if [ -f "$HOME/.bash_profile" ]; then
        printf '%s/.bash_profile\n' "$HOME"
      elif [ -f "$HOME/.bashrc" ]; then
        printf '%s/.bashrc\n' "$HOME"
      else
        return 1
      fi
      ;;
    *) return 1 ;;
  esac
}

remove_marker_block() {
  rc_file=$1
  [ -f "$rc_file" ] || return 0
  if ! grep -Fq 'ai-agent-config managed shell wrappers' "$rc_file"; then
    return 0
  fi
  if [ "$dry_run" = "1" ]; then
    say "would remove managed marker block from $rc_file"
    return 0
  fi
  tmp="${rc_file}.disable.$$"
  if ! awk '
    /^# >>> ai-agent-config managed shell wrappers >>>/ { skip=1; next }
    /^# <<< ai-agent-config managed shell wrappers <<</ { if (skip) { skip=0; next } }
    !skip { print }
    END {
      if (skip) {
        print "error: open marker found but matching close marker missing; rc file not modified" > "/dev/stderr"
        exit 1
      }
    }
  ' "$rc_file" > "$tmp"; then
    [ -e "$tmp" ] && trash "$tmp" 2>/dev/null || true
    fail "refusing to overwrite $rc_file: managed marker block appears truncated"
  fi
  mv "$tmp" "$rc_file"
  say "removed managed marker block from $rc_file"
}

remove_managed_link() {
  if [ ! -L "$dst" ]; then
    [ -e "$dst" ] && warn "skip non-symlink at $dst"
    return 0
  fi
  if [ "$dry_run" = "1" ]; then
    say "would remove symlink: $dst"
    return 0
  fi
  command -v trash >/dev/null 2>&1 || fail "trash is required for safe removal"
  trash "$dst"
  say "trashed symlink: $dst"
}

rc_file=$(detect_shell_rc) || rc_file=""
if [ -z "$rc_file" ]; then
  warn "could not detect shell rc file (SHELL=${SHELL:-unset}); skip rc cleanup"
else
  remove_marker_block "$rc_file"
fi

remove_managed_link

cat <<EOF >&2

Done. Open a new shell, or unset the wrappers in this session with:
  unset -f claude 2>/dev/null
  unalias codex gemini 2>/dev/null

EOF
