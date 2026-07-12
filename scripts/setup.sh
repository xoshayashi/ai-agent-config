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
setup_macos_bootstrap=${AI_AGENT_SETUP_MACOS_BOOTSTRAP:-1}
setup_macos_settings=${AI_AGENT_SETUP_MACOS_SETTINGS:-1}
show_auth_steps=${AI_AGENT_SHOW_AUTH_STEPS:-1}

case "$conflict_mode" in
  skip|fail|replace) ;;
  *) fail "AI_AGENT_CONFLICT_MODE must be skip, fail, or replace" ;;
esac

case "$setup_macos_bootstrap" in
  0|1) ;;
  *) fail "AI_AGENT_SETUP_MACOS_BOOTSTRAP must be 0 or 1" ;;
esac

case "$setup_macos_settings" in
  0|1) ;;
  *) fail "AI_AGENT_SETUP_MACOS_SETTINGS must be 0 or 1" ;;
esac

case "$show_auth_steps" in
  0|1) ;;
  *) fail "AI_AGENT_SHOW_AUTH_STEPS must be 0 or 1" ;;
esac

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(abs_existing_dir "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
codex_home=$(abs_dir "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(abs_dir "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
home_dir=$(abs_dir "${AI_AGENT_HOME:-$HOME}")
timestamp=$(date +%Y%m%d-%H%M%S)
skill_source_root="$config_home/skills"
retired_skill_names="daily-llm-history-instruction-review"

if [ -n "${AI_AGENT_TARGET_DIR:-}" ]; then
  warn "AI_AGENT_TARGET_DIR is ignored. Instructions are installed globally."
fi

is_darwin() {
  [ "$(uname -s 2>/dev/null || printf unknown)" = "Darwin" ]
}

brew_command() {
  if command -v brew >/dev/null 2>&1; then
    command -v brew
  elif [ -x /opt/homebrew/bin/brew ]; then
    printf '%s\n' /opt/homebrew/bin/brew
  elif [ -x /usr/local/bin/brew ]; then
    printf '%s\n' /usr/local/bin/brew
  else
    return 1
  fi
}

shell_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

run_in_terminal() {
  label=$1
  command_text=$2
  wait_seconds=${AI_AGENT_TERMINAL_WAIT_SECONDS:-900}

  if [ "$dry_run" = "1" ]; then
    say "would open Terminal for $label: $command_text"
    return 0
  fi
  if ! is_darwin || ! command -v open >/dev/null 2>&1; then
    fail "$label requires a terminal for password entry, but Terminal.app cannot be opened"
  fi

  status_file="${TMPDIR:-/tmp}/ai-agent-terminal-status.$$.$(date +%s)"
  command_file="${TMPDIR:-/tmp}/ai-agent-terminal-run.$$.$(date +%s).command"
  quoted_status=$(shell_quote "$status_file")
  quoted_config=$(shell_quote "$config_home")

  (
    umask 077
    cat >"$command_file" <<EOF
#!/bin/sh
cd $quoted_config || exit 1
printf '%s\n' 'setup.sh: $label'
printf '%s\n' 'Enter your macOS password in this Terminal window if sudo asks.'
$command_text
status=\$?
printf '%s\n' "\$status" > $quoted_status
if [ "\$status" -eq 0 ]; then
  printf '%s\n' 'setup.sh: completed successfully.'
else
  printf '%s\n' "setup.sh: failed with exit status \$status."
fi
printf '%s\n' 'You can close this Terminal window.'
exit "\$status"
EOF
  )
  chmod 700 "$command_file"

  say "terminal: $label"
  open "$command_file"

  elapsed=0
  while [ ! -f "$status_file" ]; do
    if [ "$elapsed" -ge "$wait_seconds" ]; then
      fail "$label did not finish within ${wait_seconds}s"
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done

  status=$(cat "$status_file")
  unlink "$status_file" 2>/dev/null || true
  unlink "$command_file" 2>/dev/null || true
  [ "$status" = "0" ] || fail "$label failed in Terminal with exit status $status"
}

ensure_sudo() {
  reason=$1
  if [ "$dry_run" = "1" ]; then
    say "would validate sudo: $reason"
    return 0
  fi
  if sudo -n true >/dev/null 2>&1; then
    return 0
  fi
  if [ -t 0 ]; then
    say "sudo: $reason"
    sudo -v
    return 0
  fi
  fail "sudo authentication is required for $reason"
}

install_command_line_tools() {
  if ! is_darwin; then
    return 0
  fi
  if xcode-select -p >/dev/null 2>&1; then
    say "ok: Command Line Tools installed"
    return 0
  fi
  say "install: Command Line Tools"
  run xcode-select --install
  say "Complete the Command Line Tools installer dialog, then rerun setup.sh."
  exit 0
}

install_homebrew() {
  if ! is_darwin; then
    warn "skip Homebrew setup; this is not macOS"
    return 0
  fi
  if brew_path=$(brew_command); then
    say "ok: Homebrew at $brew_path"
  elif [ "$dry_run" = "1" ]; then
    say "would install: Homebrew"
  else
    say "install: Homebrew"
    NONINTERACTIVE=1 /bin/bash -c "$(/usr/bin/curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  if brew_path=$(brew_command); then
    brew_prefix=$("$brew_path" --prefix)
    export PATH="$brew_prefix/bin:$brew_prefix/opt/python/libexec/bin:$brew_prefix/share/google-cloud-sdk/bin:/usr/local/bin:$PATH"
  else
    export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
  fi
}

brew_install_formulae() {
  brew_path=$(brew_command) || {
    warn "brew unavailable; skip formula install"
    return 0
  }

  for formula in \
    git \
    gh \
    hf \
    mas \
    python \
    pipx \
    zsh-autosuggestions \
    fzf \
    zoxide \
    starship \
    zsh-syntax-highlighting \
    displayplacer
  do
    if ! "$brew_path" list --formula "$formula" >/dev/null 2>&1; then
      say "install: brew formula $formula"
      run "$brew_path" install "$formula"
    elif [ -n "$("$brew_path" outdated --formula "$formula" 2>/dev/null || true)" ]; then
      say "upgrade: brew formula $formula"
      run "$brew_path" upgrade "$formula"
    else
      say "ok: brew formula $formula"
    fi
  done

  python_prefix=$("$brew_path" --prefix python 2>/dev/null || true)
  if [ -n "$python_prefix" ]; then
    export PATH="$python_prefix/libexec/bin:$PATH"
  fi
}

pipx_package_version() {
  package=$1
  command -v pipx >/dev/null 2>&1 || return 1
  python3 - "$package" <<'PY'
import json
import subprocess
import sys

package = sys.argv[1]
try:
    data = subprocess.check_output(["pipx", "list", "--json"], text=True, stderr=subprocess.DEVNULL)
    venvs = json.loads(data).get("venvs", {})
    meta = venvs.get(package, {}).get("metadata", {})
    main = meta.get("main_package", {})
    version = main.get("package_version")
    if version:
        print(version)
        raise SystemExit(0)
except Exception:
    pass
raise SystemExit(1)
PY
}

pypi_latest_version() {
  package=$1
  command -v curl >/dev/null 2>&1 || return 1
  curl -fsSL "https://pypi.org/pypi/$package/json" 2>/dev/null \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["info"]["version"])'
}

install_pipx_packages() {
  if ! command -v pipx >/dev/null 2>&1; then
    if [ "$dry_run" = "1" ]; then
      for package in colab-cli; do
        say "install: pipx package $package"
        run pipx install "$package"
      done
      return 0
    fi
    warn "pipx unavailable; skip Python CLI setup"
    return 0
  fi

  for package in colab-cli; do
    installed_version=$(pipx_package_version "$package" 2>/dev/null || true)
    if [ -z "$installed_version" ]; then
      say "install: pipx package $package"
      run pipx install "$package"
      continue
    fi

    latest_version=$(pypi_latest_version "$package" 2>/dev/null || true)
    if [ -n "$latest_version" ] && [ "$installed_version" != "$latest_version" ]; then
      say "upgrade: pipx package $package ($installed_version -> $latest_version)"
      run pipx upgrade "$package"
    else
      say "ok: pipx package $package"
    fi
  done
}

install_antigravity_cli() {
  export PATH="$HOME/.local/bin:$PATH"
  if command -v agy >/dev/null 2>&1; then
    say "upgrade: Antigravity CLI"
    run agy update
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    warn "curl unavailable; skip Antigravity CLI install"
    return 0
  fi
  say "install: Antigravity CLI"
  # Official Antigravity CLI documentation publishes this installer URL.
  run sh -c 'curl -fsSL https://antigravity.google/cli/install.sh | bash'
}

install_claude_code_native() {
  export PATH="$HOME/.local/bin:$PATH"

  if brew_path=$(brew_command); then
    for cask in claude-code@latest claude-code; do
      if "$brew_path" list --cask --versions "$cask" >/dev/null 2>&1; then
        say "uninstall: brew cask $cask"
        run "$brew_path" uninstall --cask "$cask"
      fi
    done
  fi

  if [ -x "$HOME/.local/bin/claude" ]; then
    say "ok: Claude Code native install"
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    warn "curl unavailable; skip Claude Code native install"
    return 0
  fi
  say "install: Claude Code native"
  run sh -c 'curl -fsSL https://claude.ai/install.sh | bash'
}

install_codex_cli_native() {
  export PATH="$HOME/.local/bin:$PATH"

  if brew_path=$(brew_command); then
    if "$brew_path" list --cask --versions codex >/dev/null 2>&1; then
      say "uninstall: brew cask codex"
      run "$brew_path" uninstall --cask codex
    fi
  fi

  if [ -x "$HOME/.local/bin/codex" ]; then
    say "ok: Codex CLI standalone install"
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    warn "curl unavailable; skip Codex CLI standalone install"
    return 0
  fi
  say "install: Codex CLI standalone"
  # Official Codex CLI documentation publishes this standalone installer URL.
  run sh -c 'curl -fsSL https://chatgpt.com/codex/install.sh | CODEX_NON_INTERACTIVE=1 sh'
}

brew_cask_installed() {
  brew_path=$1
  cask=$2
  if "$brew_path" list --cask --versions "$cask" 2>/dev/null | grep -Eq "^$cask([[:space:]]|$)"; then
    return 0
  fi
  case "$cask" in
    displaylink) [ -d "/Applications/DisplayLink Manager.app" ] && return 0 ;;
    docker-desktop) [ -d "/Applications/Docker.app" ] && return 0 ;;
    gcloud-cli) command -v gcloud >/dev/null 2>&1 && return 0 ;;
    google-drive) [ -d "/Applications/Google Drive.app" ] && return 0 ;;
    ollama-app) [ -d "/Applications/Ollama.app" ] && return 0 ;;
    tailscale-app) [ -d "/Applications/Tailscale.app" ] && return 0 ;;
    zoom) [ -d "/Applications/zoom.us.app" ] && return 0 ;;
  esac
  brew_prefix=$("$brew_path" --prefix)
  [ -d "$brew_prefix/Caskroom/$cask/.metadata" ]
}

cask_needs_terminal() {
  case "$1" in
    chatgpt|claude|displaylink|docker-desktop|google-drive|tailscale-app|zoom) return 0 ;;
    *) return 1 ;;
  esac
}

prepare_latest_cask_conflicts() {
  brew_path=$1
  :
}

brew_install_casks() {
  brew_path=$(brew_command) || {
    warn "brew unavailable; skip cask install"
    return 0
  }
  quoted_brew=$(shell_quote "$brew_path")
  prepare_latest_cask_conflicts "$brew_path"

  for cask in \
    chatgpt \
    claude \
    displaylink \
    gcloud-cli \
    slack \
    tailscale-app \
    thebrowsercompany-dia \
    google-chrome \
    google-drive \
    docker-desktop \
    visual-studio-code \
    libreoffice \
    maccy \
    ollama-app \
    zoom
  do
    quoted_cask=$(shell_quote "$cask")
    if brew_cask_installed "$brew_path" "$cask"; then
      if [ -n "$("$brew_path" outdated --cask "$cask" 2>/dev/null || true)" ]; then
        if cask_needs_terminal "$cask" && [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
          run_in_terminal "brew cask $cask upgrade" "$quoted_brew upgrade --cask $quoted_cask"
          continue
        fi
        say "upgrade: brew cask $cask"
        run "$brew_path" upgrade --cask "$cask"
      else
        say "ok: brew cask $cask"
      fi
    else
      case "$cask" in
        chatgpt)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"ChatGPT\"' >/dev/null 2>&1 || true; pkill -x ChatGPT >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask || $quoted_brew install --cask --adopt $quoted_cask"
            continue
          fi
          ;;
        claude)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"Claude\"' >/dev/null 2>&1 || true; pkill -x Claude >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask || $quoted_brew install --cask --adopt $quoted_cask"
            continue
          fi
          ;;
        displaylink)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"DisplayLink Manager\"' >/dev/null 2>&1 || true; pkill -x DisplayLinkUserAgent >/dev/null 2>&1 || true; pkill -x DisplayLinkXpcService >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask"
            continue
          fi
          ensure_sudo "brew cask $cask"
          ;;
        docker-desktop)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"Docker\"' >/dev/null 2>&1 || true; pkill -x Docker >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask"
            continue
          fi
          ensure_sudo "brew cask $cask"
          ;;
        google-drive)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"Google Drive\"' >/dev/null 2>&1 || true; pkill -x 'Google Drive' >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask"
            continue
          fi
          ensure_sudo "brew cask $cask"
          ;;
        tailscale-app)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"Tailscale\"' >/dev/null 2>&1 || true; pkill -x Tailscale >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask"
            continue
          fi
          ensure_sudo "brew cask $cask"
          ;;
        zoom)
          if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
            run_in_terminal "brew cask $cask" "osascript -e 'quit app \"zoom.us\"' >/dev/null 2>&1 || true; pkill -x zoom.us >/dev/null 2>&1 || true; $quoted_brew list --cask --versions $quoted_cask >/dev/null 2>&1 || $quoted_brew install --cask $quoted_cask || $quoted_brew reinstall --cask $quoted_cask"
            continue
          fi
          ensure_sudo "brew cask $cask"
          ;;
      esac
      say "install: brew cask $cask"
      if run "$brew_path" install --cask "$cask"; then
        :
      else
        say "adopt: brew cask $cask"
        run "$brew_path" install --cask --adopt "$cask"
      fi
    fi
  done
}

mas_app_installed() {
  app_id=$1
  command -v mas >/dev/null 2>&1 || return 1
  mas list 2>/dev/null | grep -Eq "^$app_id[[:space:]]"
}

install_mas_apps() {
  if ! is_darwin; then
    return 0
  fi
  if ! command -v mas >/dev/null 2>&1; then
    if [ "$dry_run" = "1" ]; then
      say "install: Mac App Store app Perplexity (1668000334)"
      run mas install 1668000334
      return 0
    fi
    warn "mas unavailable; skip Mac App Store app install"
    return 0
  fi
  if ! mas account >/dev/null 2>&1; then
    warn "Mac App Store is not signed in; skip Perplexity install"
    say "manual auth step: sign in to App Store, then rerun setup"
    return 0
  fi

  if mas_app_installed 1668000334; then
    say "upgrade: Mac App Store app Perplexity"
    run mas upgrade 1668000334
  else
    say "install: Mac App Store app Perplexity"
    run mas install 1668000334
  fi
}

install_macos_bootstrap() {
  [ "$setup_macos_bootstrap" = "1" ] || {
    say "skip: macOS bootstrap disabled"
    return 0
  }
  install_command_line_tools
  install_homebrew
  brew_install_formulae
  install_pipx_packages
  install_antigravity_cli
  install_codex_cli_native
  install_claude_code_native
  brew_install_casks
  install_mas_apps
}

say "AI agent config setup"
say "config: $config_home"
say "codex home: $codex_home"
say "claude home: $claude_home"
say "home: $home_dir"

install_macos_bootstrap

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
    *) printf '%s\n' "$parent" ;;
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
}

install_shell_links() {
  install_link "$config_home/shell/.zshrc" "$home_dir/.zshrc"
}

install_skill_links() {
  [ -d "$skill_source_root" ] || return 0

  for target_home in "$codex_home" "$claude_home"; do
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
  for target_home in "$codex_home" "$claude_home"; do
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
  for target_home in "$codex_home" "$claude_home"; do
    move_skill_backups_out_of_root "$target_home/skills" "$target_home/skill-backups"
  done

  legacy_agents_home=$(expand_home "${AI_AGENT_LEGACY_AGENTS_HOME:-$HOME/.agents}")
  move_skill_backups_out_of_root "$legacy_agents_home/skills" "$legacy_agents_home/skill-backups"
}

install_notification_hooks() {
  helper="$config_home/scripts/install-notifications.py"
  if [ ! -f "$helper" ]; then
    warn "missing $helper; skip notification hook setup"
    return 0
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not found; skip notification hook setup"
    return 0
  fi
  # A function's positional parameters are local in POSIX sh and restored on
  # return, so building the helper's argv with `set --` does not affect $@
  # in the caller.
  set -- --mode install \
    --config-home "$config_home" \
    --claude-home "$claude_home" \
    --codex-home "$codex_home"
  if [ "$dry_run" = "1" ]; then
    set -- "$@" --dry-run
  fi
  python3 "$helper" "$@"
}

install_skill_runtime_support() {
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not found; skill scripts (financial modeling, slide packaging) will not run"
  elif ! python3 -c 'import openpyxl' >/dev/null 2>&1; then
    requirements_file="$skill_source_root/startup-financial-modeling/scripts/requirements.txt"
    if [ ! -f "$requirements_file" ]; then
      warn "python package openpyxl missing; requirements file not found: $requirements_file"
    elif ! python3 -m pip --version >/dev/null 2>&1; then
      warn "python package openpyxl missing; python3 pip is unavailable"
    elif [ "$dry_run" = "1" ]; then
      run python3 -m pip install --user --break-system-packages -r "$requirements_file"
    else
      say "install: python package openpyxl"
      if python3 -m pip install --user --break-system-packages -r "$requirements_file"; then
        if python3 -c 'import openpyxl' >/dev/null 2>&1; then
          say "ok: python package openpyxl"
        else
          warn "python package openpyxl still does not import after install"
        fi
      else
        warn "python package openpyxl install failed; install with: python3 -m pip install --user --break-system-packages -r $requirements_file"
      fi
    fi
  else
    say "ok: python package openpyxl"
  fi

  # act-structured-slide-generation runtime: python-pptx / Pillow / lxml / fonttools
  if command -v python3 >/dev/null 2>&1; then
    if ! python3 -c 'import pptx, PIL, lxml, fontTools' >/dev/null 2>&1; then
      requirements_file="$skill_source_root/act-structured-slide-generation/scripts/requirements.txt"
      if [ ! -f "$requirements_file" ]; then
        warn "python packages for act-structured-slide-generation missing; requirements file not found: $requirements_file"
      elif ! python3 -m pip --version >/dev/null 2>&1; then
        warn "python packages for act-structured-slide-generation missing; python3 pip is unavailable"
      elif [ "$dry_run" = "1" ]; then
        run python3 -m pip install --user --break-system-packages -r "$requirements_file"
      else
        say "install: python packages for act-structured-slide-generation (python-pptx/Pillow/lxml/fonttools)"
        if python3 -m pip install --user --break-system-packages -r "$requirements_file" \
          && python3 -c 'import pptx, PIL, lxml, fontTools' >/dev/null 2>&1; then
          say "ok: python packages for act-structured-slide-generation"
        else
          warn "python packages for act-structured-slide-generation still missing; install with: python3 -m pip install --user --break-system-packages -r $requirements_file"
        fi
      fi
    else
      say "ok: python packages for act-structured-slide-generation"
    fi
  fi

  # pdftoppm (poppler) renders the PDF to per-slide PNGs for the deck QA loop.
  if command -v pdftoppm >/dev/null 2>&1; then
    say "ok: pdftoppm resolves"
  else
    warn "pdftoppm (poppler) not found; act-structured-slide-generation render QA will be skipped (optional: brew install poppler)"
  fi

  # macOS Homebrew installs LibreOffice as `soffice`; skills probe the
  # `libreoffice` name. Add a same-directory compatibility symlink so the name
  # resolves. This does not install LibreOffice itself.
  if command -v libreoffice >/dev/null 2>&1; then
    say "ok: libreoffice command resolves"
  elif command -v soffice >/dev/null 2>&1; then
    soffice_path=$(command -v soffice)
    soffice_dir=$(dirname "$soffice_path")
    libreoffice_link="$soffice_dir/libreoffice"
    if [ -e "$libreoffice_link" ] || [ -L "$libreoffice_link" ]; then
      warn "skip libreoffice compatibility link; path already exists: $libreoffice_link"
    elif [ ! -w "$soffice_dir" ]; then
      warn "cannot add libreoffice compatibility link; directory not writable: $soffice_dir"
    else
      say "link: $libreoffice_link -> $soffice_path"
      run ln -s "$soffice_path" "$libreoffice_link"
    fi
  else
    warn "libreoffice/soffice not found; xlsx recalculation and slide PDF rendering will be skipped (optional: brew install --cask libreoffice)"
  fi
}

apply_power_settings() {
  if ! command -v pmset >/dev/null 2>&1; then
    fail "pmset unavailable; cannot apply power settings"
  fi
  pmset_custom=$(pmset -g custom 2>/dev/null || true)
  if printf '%s\n' "$pmset_custom" | grep -Eq 'lowpowermode[[:space:]]+1' \
    && printf '%s\n' "$pmset_custom" | grep -Eq 'Battery Power:' \
    && printf '%s\n' "$pmset_custom" | grep -Eq 'displaysleep[[:space:]]+2' \
    && printf '%s\n' "$pmset_custom" | grep -Eq 'AC Power:' \
    && printf '%s\n' "$pmset_custom" | grep -Eq 'displaysleep[[:space:]]+10'; then
    say "ok: power settings"
    return 0
  fi
  if [ "$dry_run" != "1" ] && [ ! -t 0 ] && ! sudo -n true >/dev/null 2>&1; then
    run_in_terminal "power settings" "sudo pmset -b lowpowermode 1 standby 1 ttyskeepawake 1 hibernatemode 3 powernap 1 displaysleep 2 womp 0 networkoversleep 0 sleep 1 lessbright 1 tcpkeepalive 1 disksleep 10 && sudo pmset -c lowpowermode 1 standby 1 ttyskeepawake 1 hibernatemode 3 powernap 1 displaysleep 10 womp 1 networkoversleep 0 sleep 1 tcpkeepalive 1 disksleep 10"
    return 0
  fi
  ensure_sudo "power settings"
  say "pmset: battery settings"
  run sudo pmset -b lowpowermode 1 standby 1 ttyskeepawake 1 hibernatemode 3 powernap 1 displaysleep 2 womp 0 networkoversleep 0 sleep 1 lessbright 1 tcpkeepalive 1 disksleep 10
  say "pmset: AC power settings"
  run sudo pmset -c lowpowermode 1 standby 1 ttyskeepawake 1 hibernatemode 3 powernap 1 displaysleep 10 womp 1 networkoversleep 0 sleep 1 tcpkeepalive 1 disksleep 10
}

apply_display_settings() {
  display_script="$config_home/macos/displays/current.sh"
  if [ ! -f "$display_script" ]; then
    warn "missing $display_script; skip display arrangement"
    return 0
  fi
  if ! command -v displayplacer >/dev/null 2>&1; then
    warn "displayplacer unavailable; skip display arrangement"
    return 0
  fi
  say "displayplacer: apply current display arrangement"
  if ! run sh "$display_script"; then
    warn "display arrangement could not be fully applied; connect the saved displays and rerun setup"
  fi
}

apply_defaults_snapshots() {
  defaults_dir="$config_home/macos/defaults"
  if [ ! -d "$defaults_dir" ]; then
    warn "missing $defaults_dir; skip defaults snapshots"
    return 0
  fi

  find "$defaults_dir" -type f -name '*.plist' | sort | while IFS= read -r snapshot; do
    domain=$(basename "$snapshot" .plist)
    say "defaults import: $domain"
    run defaults import "$domain" "$snapshot"
  done
}

apply_stable_macos_overrides() {
  say "defaults: com.apple.dock mru-spaces"
  run defaults write com.apple.dock mru-spaces -bool false
}

install_key_binding_files() {
  keybindings_dir="$config_home/macos/keybindings"
  keybinding_file="$keybindings_dir/DefaultKeyBinding.dict"
  if [ ! -f "$keybinding_file" ]; then
    return 0
  fi

  target_dir="$home_dir/Library/KeyBindings"
  target_file="$target_dir/DefaultKeyBinding.dict"
  say "key bindings: $target_file"
  run mkdir -p "$target_dir"
  run cp "$keybinding_file" "$target_file"
}

apply_macos_settings() {
  [ "$setup_macos_settings" = "1" ] || {
    say "skip: macOS settings disabled"
    return 0
  }
  if ! is_darwin; then
    warn "skip macOS settings; this is not macOS"
    return 0
  fi

  apply_defaults_snapshots
  apply_stable_macos_overrides
  install_key_binding_files
  apply_power_settings
  apply_display_settings

  run killall Dock >/dev/null 2>&1 || true
  run killall Finder >/dev/null 2>&1 || true
  run killall SystemUIServer >/dev/null 2>&1 || true
}

manual_auth_header_printed=0

manual_auth_command() {
  if [ "$manual_auth_header_printed" = "0" ]; then
    say "manual auth steps:"
    manual_auth_header_printed=1
  fi
  say "  $*"
}

check_manual_auth_steps() {
  [ "$show_auth_steps" = "1" ] || {
    say "skip: auth step check disabled"
    return 0
  }

  if [ "$dry_run" = "1" ]; then
    say "manual auth steps:"
    say "  gh auth login"
    say "  gcloud auth login"
    say "  hf auth login"
    return 0
  fi

  say "auth checks"

  if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
      say "ok: gh auth"
    else
      manual_auth_command "gh auth login"
    fi
  else
    warn "gh unavailable; run setup again after GitHub CLI is installed"
  fi

  if command -v gcloud >/dev/null 2>&1; then
    gcloud_account=$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | sed -n '1p')
    if [ -n "$gcloud_account" ]; then
      say "ok: gcloud auth ($gcloud_account)"
    else
      manual_auth_command "gcloud auth login"
    fi
  else
    warn "gcloud unavailable; run setup again after Google Cloud CLI is installed"
  fi

  if command -v hf >/dev/null 2>&1; then
    if hf auth whoami >/dev/null 2>&1; then
      say "ok: hf auth"
    else
      manual_auth_command "hf auth login"
    fi
  else
    warn "hf unavailable; run setup again after Hugging Face CLI is installed"
  fi

  if [ "$manual_auth_header_printed" = "0" ]; then
    say "ok: all checked auth sessions are active"
  fi
}

move_existing_skill_backups
install_instruction_links
install_shell_links
remove_retired_skill_links
install_skill_links
install_notification_hooks
install_skill_runtime_support
apply_macos_settings
check_manual_auth_steps

say "setup complete"
