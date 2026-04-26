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

env_config_set=${AI_AGENT_CONFIG_HOME+x}
env_config=${AI_AGENT_CONFIG_HOME-}
env_target_set=${AI_AGENT_TARGET_DIR+x}
env_target=${AI_AGENT_TARGET_DIR-}
env_skills_set=${AI_AGENT_SKILLS_DIR+x}
env_skills=${AI_AGENT_SKILLS_DIR-}
env_extra_skills_set=${AI_AGENT_EXTRA_SKILLS_DIRS+x}
env_extra_skills=${AI_AGENT_EXTRA_SKILLS_DIRS-}
env_hooks_set=${AI_AGENT_INSTALL_HOOKS+x}
env_hooks=${AI_AGENT_INSTALL_HOOKS-}
env_hooks_scope_set=${AI_AGENT_HOOKS_SCOPE+x}
env_hooks_scope=${AI_AGENT_HOOKS_SCOPE-}
env_hooks_runtime_set=${AI_AGENT_HOOKS_RUNTIME_LINK+x}
env_hooks_runtime=${AI_AGENT_HOOKS_RUNTIME_LINK-}

state_dir=${AI_AGENT_STATE_DIR:-$HOME/.llm-config}
legacy_state_dir=${AI_AGENT_LEGACY_STATE_DIR:-$HOME/.ai-agent-config}
if [ -n "${AI_AGENT_STATE_FILE:-}" ]; then
  state_file=$(expand_home "$AI_AGENT_STATE_FILE")
else
  state_file=$(expand_home "$state_dir")/config.env
  legacy_state_file=$(expand_home "$legacy_state_dir")/config.env
  if [ ! -f "$state_file" ] && [ -f "$legacy_state_file" ]; then
    state_file=$legacy_state_file
  fi
fi
if [ -f "$state_file" ]; then
  # shellcheck source=/dev/null
  . "$state_file"
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_target_set:-}" = "x" ] && AI_AGENT_TARGET_DIR=$env_target
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills
[ "${env_extra_skills_set:-}" = "x" ] && AI_AGENT_EXTRA_SKILLS_DIRS=$env_extra_skills
[ "${env_hooks_set:-}" = "x" ] && AI_AGENT_INSTALL_HOOKS=$env_hooks
[ "${env_hooks_scope_set:-}" = "x" ] && AI_AGENT_HOOKS_SCOPE=$env_hooks_scope
[ "${env_hooks_runtime_set:-}" = "x" ] && AI_AGENT_HOOKS_RUNTIME_LINK=$env_hooks_runtime

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
  fail "config repository has local changes. Commit them, move them aside, or set AI_AGENT_UPDATE_ALLOW_DIRTY=1 if you know this is safe."
fi

run git -C "$config_home" fetch "$remote" "$branch"
run git -C "$config_home" merge --ff-only FETCH_HEAD

if [ "$rerun_setup" = "1" ]; then
  [ -n "${AI_AGENT_TARGET_DIR:-}" ] || fail "AI_AGENT_TARGET_DIR is not set and no saved setup state was found. Run scripts/setup.sh once, or set AI_AGENT_TARGET_DIR."
  say "re-apply setup"
  run env \
    "AI_AGENT_CONFIG_HOME=$config_home" \
    "AI_AGENT_TARGET_DIR=$AI_AGENT_TARGET_DIR" \
    "AI_AGENT_SKILLS_DIR=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}" \
    "AI_AGENT_EXTRA_SKILLS_DIRS=${AI_AGENT_EXTRA_SKILLS_DIRS:-}" \
    "AI_AGENT_INSTALL_INSTRUCTIONS=${AI_AGENT_INSTALL_INSTRUCTIONS:-1}" \
    "AI_AGENT_INSTALL_SKILLS=${AI_AGENT_INSTALL_SKILLS:-1}" \
    "AI_AGENT_INSTALL_HOOKS=${AI_AGENT_INSTALL_HOOKS:-1}" \
    "AI_AGENT_HOOKS_SCOPE=${AI_AGENT_HOOKS_SCOPE:-target}" \
    "AI_AGENT_HOOKS_RUNTIME_LINK=${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}" \
    "AI_AGENT_CONFLICT_MODE=${AI_AGENT_CONFLICT_MODE:-backup}" \
    "AI_AGENT_PROTECT_LINKS=${AI_AGENT_PROTECT_LINKS:-auto}" \
    "AI_AGENT_STATE_DIR=$state_dir" \
    "AI_AGENT_DRY_RUN=$dry_run" \
    sh "$config_home/scripts/setup.sh"
else
  say "skip: setup re-apply disabled"
fi

say "update complete"
