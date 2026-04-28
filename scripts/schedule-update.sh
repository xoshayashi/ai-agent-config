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

xml_escape() {
  printf '%s' "$1" | sed \
    -e 's/&/\&amp;/g' \
    -e 's/</\&lt;/g' \
    -e 's/>/\&gt;/g' \
    -e 's/"/\&quot;/g' \
    -e "s/'/\&apos;/g"
}

systemd_require_safe_value() {
  label=$1
  value=$2
  case "$value" in
    *[\"\\\\]*|*" "*|*"	"*|*'
'*)
      fail "$label contains spaces, quotes, backslashes, or newlines; systemd scheduling cannot safely write this value"
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
cadence=${AI_AGENT_UPDATE_CADENCE:-}
interval=${AI_AGENT_UPDATE_INTERVAL_SECONDS:-}
disable_updates=0
label=${AI_AGENT_UPDATE_LABEL:-com.ai-agent-config.update}
update_remote=${AI_AGENT_UPDATE_REMOTE:-origin}
update_branch=${AI_AGENT_UPDATE_BRANCH:-main}
update_script="$config_home/scripts/update.sh"
scheduled_update_runner="$config_home/scripts/scheduled_update.py"
runtime_dir="$state_dir/runtime"
runtime_update_entrypoint="$runtime_dir/ai-agent-update"
runtime_scheduled_update_runner="$runtime_dir/scheduled_update.py"
runtime_state_parser="$runtime_dir/read-state-config.py"
dry_run=${AI_AGENT_DRY_RUN:-0}
skip_when_dirty=${AI_AGENT_UPDATE_SKIP_WHEN_DIRTY:-1}
skip_when_branch_mismatch=${AI_AGENT_UPDATE_SKIP_WHEN_BRANCH_MISMATCH:-1}

if [ -n "$cadence" ]; then
  cadence_key=$(printf '%s' "$cadence" | tr '[:upper:]' '[:lower:]')
  case "$cadence_key" in
    recommended|daily|day|1d)
      interval=86400
      ;;
    half-day|twice-daily|12h)
      interval=43200
      ;;
    weekly|week|1w)
      interval=604800
      ;;
    manual|none|off|disabled)
      disable_updates=1
      ;;
    custom)
      [ -n "$interval" ] || fail "AI_AGENT_UPDATE_CADENCE=custom requires AI_AGENT_UPDATE_INTERVAL_SECONDS"
      ;;
    *)
      fail "AI_AGENT_UPDATE_CADENCE must be recommended, daily, twice-daily, weekly, manual, or custom"
      ;;
  esac
fi

if [ "$disable_updates" = "0" ]; then
  interval=${interval:-86400}
  case "$interval" in
    ''|*[!0-9]*)
      fail "AI_AGENT_UPDATE_INTERVAL_SECONDS must be a positive integer"
      ;;
  esac
  [ "$interval" -gt 0 ] || fail "AI_AGENT_UPDATE_INTERVAL_SECONDS must be a positive integer"
fi

case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

[ -x "$update_script" ] || fail "update script is not executable: $update_script"
[ -f "$scheduled_update_runner" ] || fail "scheduled update runner is missing: $scheduled_update_runner"
[ -f "$config_home/scripts/read-state-config.py" ] || fail "state parser is missing: $config_home/scripts/read-state-config.py"
python_bin=$(command -v python3 || true)
[ -n "$python_bin" ] || fail "python3 is required for automatic update scheduling"

case "$skip_when_dirty" in
  0|1) ;;
  *) fail "AI_AGENT_UPDATE_SKIP_WHEN_DIRTY must be 0 or 1" ;;
esac

case "$skip_when_branch_mismatch" in
  0|1) ;;
  *) fail "AI_AGENT_UPDATE_SKIP_WHEN_BRANCH_MISMATCH must be 0 or 1" ;;
esac

install_runtime_files() {
  if [ "$dry_run" = "1" ]; then
    say "would refresh update runtime entrypoint: $runtime_update_entrypoint"
    say "would refresh update runtime runner: $runtime_scheduled_update_runner"
    say "would refresh update runtime parser: $runtime_state_parser"
    return 0
  fi
  mkdir -p "$runtime_dir"
  cp "$scheduled_update_runner" "$runtime_scheduled_update_runner"
  chmod 755 "$runtime_scheduled_update_runner"
  cp "$config_home/scripts/read-state-config.py" "$runtime_state_parser"
  chmod 644 "$runtime_state_parser"
  cat > "$runtime_update_entrypoint" <<EOF
#!/bin/sh
exec "$python_bin" "$runtime_scheduled_update_runner" "\$@"
EOF
  chmod 755 "$runtime_update_entrypoint"
}

os=$(uname -s 2>/dev/null || printf unknown)
say "AI agent config update scheduler"
say "config: $config_home"

if [ "$disable_updates" = "1" ]; then
  say "automatic updates disabled by AI_AGENT_UPDATE_CADENCE=$cadence"
  if [ "$os" = "Darwin" ]; then
    launch_dir="$HOME/Library/LaunchAgents"
    plist="$launch_dir/$label.plist"
    disabled_plist="$state_dir/$label.plist.disabled.$(date +%Y%m%d-%H%M%S)"
    if [ "$dry_run" = "1" ]; then
      say "would unload launchd plist if present: $plist"
      say "would move existing plist out of LaunchAgents: $disabled_plist"
    elif [ -f "$plist" ]; then
      mkdir -p "$state_dir"
      launchctl unload "$plist" >/dev/null 2>&1 || true
      mv "$plist" "$disabled_plist"
      say "disabled launchd schedule: $disabled_plist"
    else
      say "no launchd schedule found: $plist"
    fi
  elif command -v systemctl >/dev/null 2>&1; then
    if [ "$dry_run" = "1" ]; then
      say "would disable systemd user timer: ai-agent-config-update.timer"
    else
      systemctl --user disable --now ai-agent-config-update.timer >/dev/null 2>&1 || true
      say "disabled systemd user timer if it existed: ai-agent-config-update.timer"
    fi
  else
    warn "automatic scheduling is not supported on this system"
  fi
  say "manual update command:"
  say "  sh $update_script"
  exit 0
fi

say "interval seconds: $interval"
install_runtime_files

if [ "$os" = "Darwin" ]; then
  launch_dir="$HOME/Library/LaunchAgents"
  plist="$launch_dir/$label.plist"
  if [ "$dry_run" = "1" ]; then
    say "would write launchd plist: $plist"
    say "would schedule update entrypoint: $runtime_update_entrypoint"
    exit 0
  fi
  mkdir -p "$launch_dir" "$state_dir"
  label_xml=$(xml_escape "$label")
  runtime_update_entrypoint_xml=$(xml_escape "$runtime_update_entrypoint")
  state_dir_xml=$(xml_escape "$state_dir")
  config_home_xml=$(xml_escape "$config_home")
  update_remote_xml=$(xml_escape "$update_remote")
  update_branch_xml=$(xml_escape "$update_branch")
  skip_when_dirty_xml=$(xml_escape "$skip_when_dirty")
  skip_when_branch_mismatch_xml=$(xml_escape "$skip_when_branch_mismatch")
  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$label_xml</string>
  <key>ProgramArguments</key>
  <array>
    <string>$runtime_update_entrypoint_xml</string>
  </array>
  <key>StartInterval</key>
  <integer>$interval</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>WorkingDirectory</key>
  <string>$state_dir_xml</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>AI_AGENT_STATE_DIR</key>
    <string>$state_dir_xml</string>
    <key>AI_AGENT_CONFIG_HOME</key>
    <string>$config_home_xml</string>
    <key>AI_AGENT_UPDATE_REMOTE</key>
    <string>$update_remote_xml</string>
    <key>AI_AGENT_UPDATE_BRANCH</key>
    <string>$update_branch_xml</string>
    <key>AI_AGENT_UPDATE_SKIP_WHEN_DIRTY</key>
    <string>$skip_when_dirty_xml</string>
    <key>AI_AGENT_UPDATE_SKIP_WHEN_BRANCH_MISMATCH</key>
    <string>$skip_when_branch_mismatch_xml</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$state_dir_xml/update.log</string>
  <key>StandardErrorPath</key>
  <string>$state_dir_xml/update.err.log</string>
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
  systemd_require_safe_value "AI_AGENT_STATE_DIR" "$state_dir"
  systemd_require_safe_value "AI_AGENT_CONFIG_HOME" "$config_home"
  systemd_require_safe_value "AI_AGENT_UPDATE_REMOTE" "$update_remote"
  systemd_require_safe_value "AI_AGENT_UPDATE_BRANCH" "$update_branch"
  systemd_require_safe_value "update runtime entrypoint path" "$runtime_update_entrypoint"
  cat > "$service" <<EOF
[Unit]
Description=Update AI agent config

[Service]
Type=oneshot
WorkingDirectory=$state_dir
Environment="AI_AGENT_STATE_DIR=$state_dir"
Environment="AI_AGENT_CONFIG_HOME=$config_home"
Environment="AI_AGENT_UPDATE_REMOTE=$update_remote"
Environment="AI_AGENT_UPDATE_BRANCH=$update_branch"
Environment="AI_AGENT_UPDATE_SKIP_WHEN_DIRTY=$skip_when_dirty"
Environment="AI_AGENT_UPDATE_SKIP_WHEN_BRANCH_MISMATCH=$skip_when_branch_mismatch"
ExecStart=$runtime_update_entrypoint
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
