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
    sound="Funk"
    ;;
  *)
    message="作業が完了しました"
    sound="Glass"
    ;;
esac

if [ "$(uname -s 2>/dev/null || printf unknown)" = "Darwin" ] && command -v osascript >/dev/null 2>&1; then
  # label/category are fixed strings supplied by this repo's hook config,
  # so there is no untrusted input to escape here.
  osascript -e "display notification \"$message\" with title \"$label\" sound name \"$sound\"" >/dev/null 2>&1 \
    || printf '\a' >&2
else
  # Non-macOS fallback: terminal bell. Most terminals flash or chime on BEL.
  printf '\a' >&2
fi

# Valid no-op JSON result for the calling CLI's hook parser.
printf '{}\n'
exit 0
