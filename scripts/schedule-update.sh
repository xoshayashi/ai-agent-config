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

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
state_dir=$(expand_home "${AI_AGENT_STATE_DIR:-$HOME/.ai-agent-config}")
interval=${AI_AGENT_UPDATE_INTERVAL_SECONDS:-86400}
label=${AI_AGENT_UPDATE_LABEL:-com.ai-agent-config.update}
update_remote=${AI_AGENT_UPDATE_REMOTE:-origin}
update_branch=${AI_AGENT_UPDATE_BRANCH:-main}
update_script="$config_home/scripts/update.sh"
dry_run=${AI_AGENT_DRY_RUN:-0}

case "$interval" in
  ''|*[!0-9]*)
    fail "AI_AGENT_UPDATE_INTERVAL_SECONDS must be a positive integer"
    ;;
esac

case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

[ -x "$update_script" ] || fail "update script is not executable: $update_script"

os=$(uname -s 2>/dev/null || printf unknown)
say "AI agent config update scheduler"
say "config: $config_home"
say "interval seconds: $interval"

if [ "$os" = "Darwin" ]; then
  launch_dir="$HOME/Library/LaunchAgents"
  plist="$launch_dir/$label.plist"
  if [ "$dry_run" = "1" ]; then
    say "would write launchd plist: $plist"
    say "would schedule update script: $update_script"
    exit 0
  fi
  mkdir -p "$launch_dir" "$state_dir"
  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$label</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string>
    <string>$update_script</string>
  </array>
  <key>StartInterval</key>
  <integer>$interval</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>AI_AGENT_STATE_DIR</key>
    <string>$state_dir</string>
    <key>AI_AGENT_UPDATE_REMOTE</key>
    <string>$update_remote</string>
    <key>AI_AGENT_UPDATE_BRANCH</key>
    <string>$update_branch</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$state_dir/update.log</string>
  <key>StandardErrorPath</key>
  <string>$state_dir/update.err.log</string>
</dict>
</plist>
EOF
  launchctl unload "$plist" >/dev/null 2>&1 || true
  launchctl load "$plist"
  say "scheduled with launchd: $plist"
elif command -v systemctl >/dev/null 2>&1; then
  systemd_dir="$HOME/.config/systemd/user"
  mkdir -p "$systemd_dir" "$state_dir"
  service="$systemd_dir/ai-agent-config-update.service"
  timer="$systemd_dir/ai-agent-config-update.timer"
  if [ "$dry_run" = "1" ]; then
    say "would write systemd service: $service"
    say "would write systemd timer: $timer"
    say "would enable timer with systemctl --user enable --now ai-agent-config-update.timer"
    exit 0
  fi
  cat > "$service" <<EOF
[Unit]
Description=Update AI agent config

[Service]
Type=oneshot
Environment="AI_AGENT_STATE_DIR=$state_dir"
Environment="AI_AGENT_UPDATE_REMOTE=$update_remote"
Environment="AI_AGENT_UPDATE_BRANCH=$update_branch"
ExecStart=/bin/sh "$update_script"
EOF
  cat > "$timer" <<EOF
[Unit]
Description=Run AI agent config update periodically

[Timer]
OnBootSec=5m
OnUnitActiveSec=${interval}s
Unit=ai-agent-config-update.service

[Install]
WantedBy=timers.target
EOF
  systemctl --user daemon-reload
  systemctl --user enable --now ai-agent-config-update.timer
  say "scheduled with systemd user timer: $timer"
else
  warn "automatic scheduling is not supported on this system"
  say "manual update command:"
  say "  sh $update_script"
fi
