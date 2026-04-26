#!/bin/sh
set -eu

say() {
  printf '%s\n' "$*"
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

repo_url=${AI_AGENT_REPO_URL:-https://github.com/xoshayashi/llm-config.git}
config_home=$(expand_home "${AI_AGENT_CONFIG_HOME:-$HOME/Documents/llm-config}")
branch=${AI_AGENT_UPDATE_BRANCH:-main}
dry_run=${AI_AGENT_DRY_RUN:-0}

case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN must be 0 or 1" ;;
esac

command -v git >/dev/null 2>&1 || fail "git is required"

say "AI agent config install"
say "repository: $repo_url"
say "config: $config_home"
say "branch: $branch"

if [ -d "$config_home/.git" ]; then
  say "existing repository found; updating instead of cloning"
  AI_AGENT_CONFIG_HOME="$config_home" sh "$config_home/scripts/update.sh"
else
  if [ -e "$config_home" ]; then
    fail "target exists but is not a git repository: $config_home"
  fi
  parent=$(dirname "$config_home")
  if [ "$dry_run" = "1" ]; then
    say "would run: mkdir -p $parent"
    say "would run: git clone --branch $branch $repo_url $config_home"
    say "would run: AI_AGENT_CONFIG_HOME=$config_home sh $config_home/scripts/setup.sh"
  else
    mkdir -p "$parent"
    git clone --branch "$branch" "$repo_url" "$config_home"
    AI_AGENT_CONFIG_HOME="$config_home" sh "$config_home/scripts/setup.sh"
  fi
fi
