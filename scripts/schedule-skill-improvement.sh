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
cadence=${AI_AGENT_IMPROVEMENT_CADENCE:-${AI_AGENT_UPDATE_CADENCE:-daily}}
interval=${AI_AGENT_IMPROVEMENT_INTERVAL_SECONDS:-}
disable_schedule=0
label=${AI_AGENT_IMPROVEMENT_LABEL:-com.ai-agent-config.skill-improvement}
bot_script="$config_home/scripts/skill-improvement-bot.py"
dry_run=${AI_AGENT_DRY_RUN:-0}
create_pr=${AI_AGENT_IMPROVEMENT_CREATE_PR:-0}
apply_review=${AI_AGENT_IMPROVEMENT_APPLY_REVIEW:-0}
auto_merge=${AI_AGENT_IMPROVEMENT_AUTO_MERGE:-0}
improvement_llm=${AI_AGENT_IMPROVEMENT_LLM:-}
log_days=${AI_AGENT_LOG_DAYS:-14}
log_roots=${AI_AGENT_LOG_ROOTS:-}
log_roots_only=${AI_AGENT_LOG_ROOTS_ONLY:-0}

cadence_key=$(printf '%s' "$cadence" | tr '[:upper:]' '[:lower:]')
case "$cadence_key" in
  recommended|daily|day|1d)
    interval=86400
    ;;
  weekly|week|1w)
    interval=604800
    ;;
  manual|none|off|disabled)
    disable_schedule=1
    ;;
  custom)
    [ -n "$interval" ] || fail "AI_AGENT_IMPROVEMENT_CADENCE=custom requires AI_AGENT_IMPROVEMENT_INTERVAL_SECONDS"
    ;;
  *)
    fail "AI_AGENT_IMPROVEMENT_CADENCE must be recommended, daily, weekly, manual, or custom"
    ;;
esac

if [ "$disable_schedule" = "0" ]; then
  case "$interval" in
    ''|*[!0-9]*)
      fail "AI_AGENT_IMPROVEMENT_INTERVAL_SECONDS must be a positive integer"
      ;;
  esac
  [ "$interval" -gt 0 ] || fail "AI_AGENT_IMPROVEMENT_INTERVAL_SECONDS must be a positive integer"
fi

case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

[ -f "$bot_script" ] || fail "skill improvement bot is missing: $bot_script"
python_bin=$(command -v python3 || true)
[ -n "$python_bin" ] || fail "python3 is required for skill improvement automation"

os=$(uname -s 2>/dev/null || printf unknown)
say "AI agent skill improvement scheduler"
say "config: $config_home"

if [ "$disable_schedule" = "1" ]; then
  say "automatic skill-improvement scans disabled by AI_AGENT_IMPROVEMENT_CADENCE=$cadence"
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
      say "would disable systemd user timer: ai-agent-config-skill-improvement.timer"
    else
      systemctl --user disable --now ai-agent-config-skill-improvement.timer >/dev/null 2>&1 || true
      say "disabled systemd user timer if it existed: ai-agent-config-skill-improvement.timer"
    fi
  else
    warn "automatic scheduling is not supported on this system"
  fi
  say "manual scan command:"
  say "  python3 $bot_script scan"
  exit 0
fi

say "interval seconds: $interval"

if [ "$os" = "Darwin" ]; then
  launch_dir="$HOME/Library/LaunchAgents"
  plist="$launch_dir/$label.plist"
  if [ "$dry_run" = "1" ]; then
    say "would write launchd plist: $plist"
    say "would schedule skill-improvement bot: $bot_script cycle"
    exit 0
  fi
  mkdir -p "$launch_dir" "$state_dir"
  label_xml=$(xml_escape "$label")
  python_bin_xml=$(xml_escape "$python_bin")
  bot_script_xml=$(xml_escape "$bot_script")
  state_dir_xml=$(xml_escape "$state_dir")
  config_home_xml=$(xml_escape "$config_home")
  create_pr_xml=$(xml_escape "$create_pr")
  apply_review_xml=$(xml_escape "$apply_review")
  auto_merge_xml=$(xml_escape "$auto_merge")
  improvement_llm_xml=$(xml_escape "$improvement_llm")
  log_days_xml=$(xml_escape "$log_days")
  log_roots_xml=$(xml_escape "$log_roots")
  log_roots_only_xml=$(xml_escape "$log_roots_only")
  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$label_xml</string>
  <key>ProgramArguments</key>
  <array>
    <string>$python_bin_xml</string>
    <string>$bot_script_xml</string>
    <string>cycle</string>
  </array>
  <key>StartInterval</key>
  <integer>$interval</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>AI_AGENT_STATE_DIR</key>
    <string>$state_dir_xml</string>
    <key>AI_AGENT_CONFIG_HOME</key>
    <string>$config_home_xml</string>
    <key>AI_AGENT_IMPROVEMENT_CREATE_PR</key>
    <string>$create_pr_xml</string>
    <key>AI_AGENT_IMPROVEMENT_APPLY_REVIEW</key>
    <string>$apply_review_xml</string>
    <key>AI_AGENT_IMPROVEMENT_AUTO_MERGE</key>
    <string>$auto_merge_xml</string>
    <key>AI_AGENT_IMPROVEMENT_LLM</key>
    <string>$improvement_llm_xml</string>
    <key>AI_AGENT_LOG_DAYS</key>
    <string>$log_days_xml</string>
    <key>AI_AGENT_LOG_ROOTS</key>
    <string>$log_roots_xml</string>
    <key>AI_AGENT_LOG_ROOTS_ONLY</key>
    <string>$log_roots_only_xml</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$state_dir_xml/skill-improvement.log</string>
  <key>StandardErrorPath</key>
  <string>$state_dir_xml/skill-improvement.err.log</string>
</dict>
</plist>
EOF
  if command -v plutil >/dev/null 2>&1; then
    plutil -lint "$plist" >/dev/null
  fi
  launchctl unload "$plist" >/dev/null 2>&1 || true
  launchctl load "$plist"
  say "scheduled with launchd: $plist"
elif command -v systemctl >/dev/null 2>&1; then
  systemd_dir="$HOME/.config/systemd/user"
  service="$systemd_dir/ai-agent-config-skill-improvement.service"
  timer="$systemd_dir/ai-agent-config-skill-improvement.timer"
  if [ "$dry_run" = "1" ]; then
    say "would write systemd service: $service"
    say "would write systemd timer: $timer"
    say "would enable timer with systemctl --user enable --now ai-agent-config-skill-improvement.timer"
    exit 0
  fi
  systemd_require_safe_value "AI_AGENT_STATE_DIR" "$state_dir"
  systemd_require_safe_value "AI_AGENT_CONFIG_HOME" "$config_home"
  systemd_require_safe_value "python3 path" "$python_bin"
  systemd_require_safe_value "bot script path" "$bot_script"
  systemd_require_safe_value "AI_AGENT_IMPROVEMENT_LLM" "$improvement_llm"
  systemd_require_safe_value "AI_AGENT_LOG_ROOTS" "$log_roots"
  mkdir -p "$systemd_dir" "$state_dir"
  cat > "$service" <<EOF
[Unit]
Description=AI Agent Config skill improvement scan

[Service]
Type=oneshot
Environment="AI_AGENT_STATE_DIR=$state_dir"
Environment="AI_AGENT_CONFIG_HOME=$config_home"
Environment="AI_AGENT_IMPROVEMENT_CREATE_PR=$create_pr"
Environment="AI_AGENT_IMPROVEMENT_APPLY_REVIEW=$apply_review"
Environment="AI_AGENT_IMPROVEMENT_AUTO_MERGE=$auto_merge"
Environment="AI_AGENT_IMPROVEMENT_LLM=$improvement_llm"
Environment="AI_AGENT_LOG_DAYS=$log_days"
Environment="AI_AGENT_LOG_ROOTS=$log_roots"
Environment="AI_AGENT_LOG_ROOTS_ONLY=$log_roots_only"
ExecStart=$python_bin "$bot_script" cycle
EOF
  cat > "$timer" <<EOF
[Unit]
Description=Run AI Agent Config skill improvement scan periodically

[Timer]
# Run once after boot so machines that were asleep during the interval still catch up.
OnBootSec=10m
OnUnitActiveSec=${interval}s
Unit=ai-agent-config-skill-improvement.service

[Install]
WantedBy=timers.target
EOF
  systemctl --user daemon-reload
  systemctl --user enable --now ai-agent-config-skill-improvement.timer
  say "scheduled with systemd user timer: $timer"
else
  warn "automatic scheduling is not supported on this system"
  say "manual scan command:"
  say "  python3 $bot_script scan"
fi
