#!/bin/sh
# Optional opt-in: install shell wrappers that start Codex / Gemini CLI / Claude Code
# in their auto-approval startup mode by default for new shell sessions.
#
# This is intentionally NOT part of scripts/setup.sh because it lowers the
# default safety bar of three CLIs at once and writes a managed block into
# the user's shell rc file. Run this script only when you understand the
# trade-off. Reverse it with scripts/disable-auto-permission.sh.

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
config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)

src="$config_home/shell/auto-permission.sh"
[ -f "$src" ] || fail "shell wrapper source missing: $src"

shell_alias_link=${AI_AGENT_SHELL_ALIAS_LINK:-$HOME/.llm-config/auto-permission.sh}
dst=$(expand_home "$shell_alias_link")

dry_run=${AI_AGENT_DRY_RUN:-0}
case "$dry_run" in 0|1) ;; *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;; esac

assume_yes=${AI_AGENT_ASSUME_YES:-0}
case "$assume_yes" in 0|1) ;; *) fail "AI_AGENT_ASSUME_YES must be 0 or 1" ;; esac

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

rc_file=$(detect_shell_rc) || rc_file=""

marker_open='# >>> ai-agent-config managed shell wrappers >>>'
marker_close='# <<< ai-agent-config managed shell wrappers <<<'

if [ -n "$rc_file" ] && [ -f "$rc_file" ] && grep -Fq "$marker_open" "$rc_file"; then
  say "ok: managed wrapper block already present in $rc_file"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    say "ok: $dst -> $src"
  else
    warn "wrapper block exists but symlink missing or wrong: $dst"
    warn "run scripts/disable-auto-permission.sh, then re-run this script to repair"
  fi
  exit 0
fi

cat <<EOF >&2

Shell wrapper installation (opt-in, irreversible until disabled)
================================================================

If you proceed, the following CLIs will be wrapped to start in their
auto-approval mode by default whenever a new shell session sources your
rc file. After this, agents launched through these CLIs can take
destructive actions on your machine without asking each time:

  codex    --dangerously-bypass-approvals-and-sandbox
  gemini   --yolo
  claude   --permission-mode auto         (normal interactive sessions only;
                                           maintenance subcommands such as
                                           auth / install / mcp / plugin /
                                           doctor stay safe)

Files this script will create or modify:

  $dst
      (new symlink to $src)
  ${rc_file:-(no shell rc detected for SHELL=${SHELL:-unset})}
      (one managed marker block appended at the end)

The default if you press Enter is NO. To reverse this later, run:
  sh scripts/disable-auto-permission.sh

EOF

if [ -z "$rc_file" ]; then
  fail "could not detect shell rc file (SHELL=${SHELL:-unset}); aborting"
fi

if [ "$assume_yes" = "1" ]; then
  say "AI_AGENT_ASSUME_YES=1 set; proceeding without interactive confirmation"
elif [ ! -t 0 ]; then
  fail "stdin is not a TTY and AI_AGENT_ASSUME_YES is not set; aborting"
else
  printf 'Proceed and install the shell wrapper block? [y/N]: ' >&2
  IFS= read -r answer || answer=""
  case "$answer" in
    Y|y|YES|yes|Yes) ;;
    *) fail "declined; no changes made" ;;
  esac
fi

if [ "$dry_run" = "1" ]; then
  say "would create symlink: $dst -> $src"
  say "would append marker block to: $rc_file"
  exit 0
fi

mkdir -p "$(dirname "$dst")"
if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
  say "ok: symlink already correct: $dst -> $src"
elif [ -L "$dst" ] || [ -e "$dst" ]; then
  fail "destination already exists and is not the managed symlink: $dst -- remove it first or set AI_AGENT_SHELL_ALIAS_LINK to a different path"
else
  ln -s "$src" "$dst"
  say "linked: $dst -> $src"
fi

[ -f "$rc_file" ] || touch "$rc_file"
{
  printf '\n%s\n' "$marker_open"
  printf '# Managed by scripts/enable-auto-permission.sh in ai-agent-config.\n'
  printf '# Reverse with scripts/disable-auto-permission.sh.\n'
  printf '[ -r "%s" ] && . "%s"\n' "$dst" "$dst"
  printf '%s\n' "$marker_close"
} >> "$rc_file"
say "appended marker block to: $rc_file"

cat <<EOF >&2

Done. Open a new shell, or run:
  exec \$SHELL -l
to load the wrappers in this session.

EOF
