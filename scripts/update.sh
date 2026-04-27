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

load_state_file() {
  path=$1
  [ -f "$path" ] || return 1
  command -v python3 >/dev/null 2>&1 || {
    warn "python3 is required to read setup state safely: $path"
    return 1
  }
  parser="$script_dir/read-state-config.py"
  [ -f "$parser" ] || {
    warn "state parser not found: $parser"
    return 1
  }
  if ! parsed=$(python3 "$parser" "$path" 2>/dev/null); then
    warn "state file could not be read safely: $path"
    return 1
  fi

  tab=$(printf '\t')
  while IFS="$tab" read -r key value; do
    [ -n "$key" ] || continue
    case "$key" in
      AI_AGENT_CONFIG_HOME) AI_AGENT_CONFIG_HOME=$value ;;
      AI_AGENT_CODEX_HOME) AI_AGENT_CODEX_HOME=$value ;;
      AI_AGENT_CLAUDE_HOME) AI_AGENT_CLAUDE_HOME=$value ;;
      AI_AGENT_GEMINI_HOME) AI_AGENT_GEMINI_HOME=$value ;;
      AI_AGENT_SKILLS_DIR) AI_AGENT_SKILLS_DIR=$value ;;
      AI_AGENT_EXTRA_SKILLS_DIRS) AI_AGENT_EXTRA_SKILLS_DIRS=$value ;;
      AI_AGENT_INSTALL_INSTRUCTIONS) AI_AGENT_INSTALL_INSTRUCTIONS=$value ;;
      AI_AGENT_INSTALL_SKILLS) AI_AGENT_INSTALL_SKILLS=$value ;;
      AI_AGENT_INSTALL_HOOKS) AI_AGENT_INSTALL_HOOKS=$value ;;
      AI_AGENT_HOOKS_RUNTIME_LINK) AI_AGENT_HOOKS_RUNTIME_LINK=$value ;;
      AI_AGENT_CONFLICT_MODE) AI_AGENT_CONFLICT_MODE=$value ;;
      AI_AGENT_PROTECT_LINKS) AI_AGENT_PROTECT_LINKS=$value ;;
      AI_AGENT_REQUIRE_LLM_CLIS) AI_AGENT_REQUIRE_LLM_CLIS=$value ;;
      AI_AGENT_STATE_DIR) AI_AGENT_STATE_DIR=$value ;;
      AI_AGENT_STATE_FILE) AI_AGENT_STATE_FILE=$value ;;
    esac
  done <<EOF
$parsed
EOF
  return 0
}

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

env_config_set=${AI_AGENT_CONFIG_HOME+x}
env_config=${AI_AGENT_CONFIG_HOME-}
env_codex_home_set=${AI_AGENT_CODEX_HOME+x}
env_codex_home=${AI_AGENT_CODEX_HOME-}
env_claude_home_set=${AI_AGENT_CLAUDE_HOME+x}
env_claude_home=${AI_AGENT_CLAUDE_HOME-}
env_gemini_home_set=${AI_AGENT_GEMINI_HOME+x}
env_gemini_home=${AI_AGENT_GEMINI_HOME-}
env_skills_set=${AI_AGENT_SKILLS_DIR+x}
env_skills=${AI_AGENT_SKILLS_DIR-}
env_extra_skills_set=${AI_AGENT_EXTRA_SKILLS_DIRS+x}
env_extra_skills=${AI_AGENT_EXTRA_SKILLS_DIRS-}
env_hooks_set=${AI_AGENT_INSTALL_HOOKS+x}
env_hooks=${AI_AGENT_INSTALL_HOOKS-}
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
state_loaded=0
if load_state_file "$state_file"; then
  state_loaded=1
fi

[ "${env_config_set:-}" = "x" ] && AI_AGENT_CONFIG_HOME=$env_config
[ "${env_codex_home_set:-}" = "x" ] && AI_AGENT_CODEX_HOME=$env_codex_home
[ "${env_claude_home_set:-}" = "x" ] && AI_AGENT_CLAUDE_HOME=$env_claude_home
[ "${env_gemini_home_set:-}" = "x" ] && AI_AGENT_GEMINI_HOME=$env_gemini_home
[ "${env_skills_set:-}" = "x" ] && AI_AGENT_SKILLS_DIR=$env_skills
[ "${env_extra_skills_set:-}" = "x" ] && AI_AGENT_EXTRA_SKILLS_DIRS=$env_extra_skills
[ "${env_hooks_set:-}" = "x" ] && AI_AGENT_INSTALL_HOOKS=$env_hooks
[ "${env_hooks_runtime_set:-}" = "x" ] && AI_AGENT_HOOKS_RUNTIME_LINK=$env_hooks_runtime
state_dir=${AI_AGENT_STATE_DIR:-$state_dir}
if [ -n "${AI_AGENT_STATE_FILE:-}" ]; then
  state_file=$(expand_home "$AI_AGENT_STATE_FILE")
fi

if [ -n "${AI_AGENT_TARGET_DIR:-}" ]; then
  warn "AI_AGENT_TARGET_DIR is deprecated and ignored. Instructions are now installed globally."
fi
if [ -n "${AI_AGENT_HOOKS_SCOPE:-}" ]; then
  warn "AI_AGENT_HOOKS_SCOPE is deprecated and ignored. Hooks are now installed globally."
fi

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
if [ "$state_loaded" = "0" ]; then
  warn "state file not loaded; using environment/defaults: $state_file"
fi

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
  say "re-apply setup"
  run env \
    "AI_AGENT_CONFIG_HOME=$config_home" \
    "AI_AGENT_CODEX_HOME=${AI_AGENT_CODEX_HOME:-$HOME/.codex}" \
    "AI_AGENT_CLAUDE_HOME=${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}" \
    "AI_AGENT_GEMINI_HOME=${AI_AGENT_GEMINI_HOME:-$HOME/.gemini}" \
    "AI_AGENT_SKILLS_DIR=${AI_AGENT_SKILLS_DIR:-$HOME/.agents/skills}" \
    "AI_AGENT_EXTRA_SKILLS_DIRS=${AI_AGENT_EXTRA_SKILLS_DIRS:-}" \
    "AI_AGENT_INSTALL_INSTRUCTIONS=${AI_AGENT_INSTALL_INSTRUCTIONS:-1}" \
    "AI_AGENT_INSTALL_SKILLS=${AI_AGENT_INSTALL_SKILLS:-1}" \
    "AI_AGENT_INSTALL_HOOKS=${AI_AGENT_INSTALL_HOOKS:-1}" \
    "AI_AGENT_HOOKS_RUNTIME_LINK=${AI_AGENT_HOOKS_RUNTIME_LINK:-$HOME/.llm-config/hooks}" \
    "AI_AGENT_CONFLICT_MODE=${AI_AGENT_CONFLICT_MODE:-backup}" \
    "AI_AGENT_PROTECT_LINKS=${AI_AGENT_PROTECT_LINKS:-auto}" \
    "AI_AGENT_REQUIRE_LLM_CLIS=${AI_AGENT_REQUIRE_LLM_CLIS:-1}" \
    "AI_AGENT_STATE_DIR=$state_dir" \
    "AI_AGENT_STATE_FILE=$state_file" \
    "AI_AGENT_DRY_RUN=$dry_run" \
    sh "$config_home/scripts/setup.sh"
else
  say "skip: setup re-apply disabled"
fi

say "update complete"
