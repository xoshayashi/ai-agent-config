#!/bin/sh
# Shared desktop-notification hook for Claude Code / Codex / Gemini CLI.
#
# Invoked as a hook command:  notify.sh <label> <category>
#   label    human-facing source name, e.g. "Claude Code"
#   category "done"      -> the agent finished a turn
#            "attention" -> the agent needs input or approval
#
# Each CLI pipes a hook JSON payload on stdin. This script does not need any
# field from it, so stdin is intentionally left unread.
#
# Every CLI parses the hook's stdout as JSON. Gemini CLI treats non-JSON
# stdout as a parse failure, so this script must end by printing an empty
# JSON object. All log/bell output therefore goes to stderr only.
set -u

label=${1:-AI Agent}
category=${2:-done}

# Notification text is Japanese by default; edit the messages here to localize.
case "$category" in
  attention)
    message="承認または入力を待っています"
    sound_file="/System/Library/Sounds/Funk.aiff"
    ;;
  *)
    message="作業が完了しました"
    sound_file="/System/Library/Sounds/Glass.aiff"
    ;;
esac

# Two independent channels, no third-party app in the loop:
#   1. afplay chimes through the system audio - not gated by notification
#      permission (macOS only).
#   2. The terminal emulator surfaces the visual signal itself: a real banner
#      where it has a documented escape (iTerm2, WezTerm), otherwise a BEL
#      that each terminal turns into its own indicator (VS Code/Cursor ->
#      terminal activity badge, Apple Terminal -> bell notification per its
#      profile settings, Linux -> terminal default).
# When the hook runs without a controlling TTY (Claude Code Desktop, headless
# automation), the visual step silently no-ops and only the chime fires.
if [ "$(uname -s 2>/dev/null || printf unknown)" = "Darwin" ]; then
  if [ -f "$sound_file" ] && command -v afplay >/dev/null 2>&1; then
    afplay "$sound_file" >/dev/null 2>&1 &
  fi
fi

case "${TERM_PROGRAM:-}" in
  iTerm.app|WezTerm)
    # OSC 9: single-string notification, no title/message split. Write to the
    # controlling TTY because hook stdout is reserved for the JSON payload.
    # Subshell so /dev/tty open failures (TTY-less hooks) are silenced.
    ( printf '\033]9;%s: %s\007' "$label" "$message" >/dev/tty ) 2>/dev/null || true
    ;;
  *)
    ( printf '\a' >/dev/tty ) 2>/dev/null || true
    ;;
esac

# Valid no-op JSON result for the calling CLI's hook parser.
printf '{}\n'
exit 0
