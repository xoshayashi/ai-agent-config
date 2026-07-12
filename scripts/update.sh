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

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(abs_existing_dir "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
remote=${AI_AGENT_UPDATE_REMOTE:-origin}
branch=${AI_AGENT_UPDATE_BRANCH:-main}
dry_run=${AI_AGENT_DRY_RUN:-${AI_AGENT_UPDATE_DRY_RUN:-0}}
allow_dirty=${AI_AGENT_UPDATE_ALLOW_DIRTY:-0}
rerun_setup=${AI_AGENT_UPDATE_RERUN_SETUP:-1}

case "$dry_run" in
  0|1) ;;
  *) fail "AI_AGENT_DRY_RUN or AI_AGENT_UPDATE_DRY_RUN must be 0 or 1" ;;
esac
case "$allow_dirty" in
  0|1) ;;
  *) fail "AI_AGENT_UPDATE_ALLOW_DIRTY must be 0 or 1" ;;
esac
case "$rerun_setup" in
  0|1) ;;
  *) fail "AI_AGENT_UPDATE_RERUN_SETUP must be 0 or 1" ;;
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

[ -d "$config_home/.git" ] || fail "not a git repository: $config_home"
command -v git >/dev/null 2>&1 || fail "git is required"

say "AI agent config update"
say "config: $config_home"
say "remote: $remote"
say "branch: $branch"

current_branch=$(git -C "$config_home" rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "$branch" ]; then
  fail "config repository is on '$current_branch', not '$branch'. Set AI_AGENT_UPDATE_BRANCH or switch branches before updating."
fi

if [ "$allow_dirty" != "1" ] && [ -n "$(git -C "$config_home" status --porcelain)" ]; then
  fail "config repository has local changes. Commit them, move them aside, or set AI_AGENT_UPDATE_ALLOW_DIRTY=1 if this update owns them."
fi

run git -C "$config_home" fetch "$remote" "$branch"
run git -C "$config_home" merge --ff-only FETCH_HEAD

if [ "$rerun_setup" = "1" ]; then
  say "re-apply setup"
  run env \
    "AI_AGENT_CONFIG_HOME=$config_home" \
    "AI_AGENT_CODEX_HOME=${AI_AGENT_CODEX_HOME:-$HOME/.codex}" \
    "AI_AGENT_CLAUDE_HOME=${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}" \
    "AI_AGENT_CONFLICT_MODE=${AI_AGENT_CONFLICT_MODE:-skip}" \
    "AI_AGENT_DRY_RUN=$dry_run" \
    sh "$config_home/scripts/setup.sh"
else
  say "skip: setup re-apply disabled"
fi

say "update complete"
