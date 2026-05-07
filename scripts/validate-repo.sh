#!/bin/sh
set -eu

say() {
  printf '%s\n' "$*"
}

fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

repo_root=$(CDPATH= cd "$script_dir/.." && pwd -P)

require_file() {
  [ -f "$repo_root/$1" ] || fail "missing required file: $1"
}

require_absent() {
  [ ! -e "$repo_root/$1" ] || fail "unexpected repository path exists: $1"
}

ensure_root_entrypoint_gone() {
  path=$1
  if ! git -C "$repo_root" ls-files --error-unmatch "$path" >/dev/null 2>&1; then
    return 0
  fi
  status=$(git -C "$repo_root" status --porcelain -- "$path")
  case "$status" in
    *D*) return 0 ;;
  esac
  fail "$path must not be tracked at repo root"
}

say "validate: shell syntax"
for script in "$repo_root"/scripts/*; do
  [ -f "$script" ] || continue
  first_line=$(sed -n '1p' "$script")
  case "$first_line" in
    *"/sh"|*"/bash"|*"env sh"|*"env bash") sh -n "$script" ;;
  esac
done

say "validate: required files"
require_file "README.md"
require_file "setup.md"
require_file "docs/setup-error-guide.md"
require_file "docs/codex-automation-daily-review.md"
require_file "scripts/setup.sh"
require_file "scripts/update.sh"
require_file "scripts/uninstall.sh"
require_file "scripts/health-check.sh"
require_file "scripts/validate-repo.sh"
require_file "instructions/AGENTS.md"
require_file "instructions/CLAUDE.md"
require_file "instructions/GEMINI.md"
require_file "instructions/AI_AGENT_INSTRUCTIONS.md"
require_file "instructions/DESIGN.md"
require_file "skills/daily-llm-history-instruction-review/SKILL.md"
require_file ".github/workflows/validate.yml"
require_file ".github/workflows/claude-code-review.yml"

say "validate: repository surface"
require_absent "hooks"
require_absent "tests"
require_absent "scripts/__pycache__"
require_absent "instructions/HOOKS.md"
require_absent "scripts/autonomous_runner.py"
require_absent "scripts/daily-llm-history-instruction-review"
require_absent "scripts/merge-hook-config.py"
require_absent "scripts/read-state-config.py"
require_absent "scripts/scheduled_update.py"
require_absent "scripts/schedule-update.sh"
require_absent "scripts/schedule-skill-improvement.sh"
require_absent "scripts/skill-improvement-bot.py"
require_absent "docs/autonomous-runner.md"
require_absent "docs/llm-history-instruction-review.md"
require_absent "docs/hooks-architecture-review.md"
require_absent "docs/skill-improvement-automation.md"
require_absent "docs/examples"
require_absent ".github/workflows/claude.yml"

tracked_ignored=$(git -C "$repo_root" ls-files -ci --exclude-standard)
[ -z "$tracked_ignored" ] || fail "tracked files must not be ignored by .gitignore: $(printf '%s' "$tracked_ignored" | tr '\n' ' ')"

if [ -d "$repo_root/skills" ]; then
  find "$repo_root/skills" -name __pycache__ -type d | grep -q . \
    && fail "skills/ must not contain __pycache__ directories"
  for skill_dir in "$repo_root"/skills/*; do
    [ -d "$skill_dir" ] || fail "skills/ must contain skill directories only"
    [ -f "$skill_dir/SKILL.md" ] || fail "missing skill entrypoint: skills/$(basename "$skill_dir")/SKILL.md"
    grep -Eq '^name: ' "$skill_dir/SKILL.md" \
      || fail "skill SKILL.md must define name: skills/$(basename "$skill_dir")/SKILL.md"
    grep -Eq '^description: ' "$skill_dir/SKILL.md" \
      || fail "skill SKILL.md must define description: skills/$(basename "$skill_dir")/SKILL.md"
  done
fi

say "validate: entrypoint wording"
ensure_root_entrypoint_gone "AGENTS.md"
ensure_root_entrypoint_gone "CLAUDE.md"
ensure_root_entrypoint_gone "GEMINI.md"
grep -Fq "~/.codex/AI_AGENT_INSTRUCTIONS.md" "$repo_root/instructions/AGENTS.md" \
  || fail "Codex AGENTS entrypoint must point to ~/.codex/AI_AGENT_INSTRUCTIONS.md"
grep -Fq "~/.codex/DESIGN.md" "$repo_root/instructions/AGENTS.md" \
  || fail "Codex AGENTS entrypoint must point to ~/.codex/DESIGN.md"
! grep -Fq "HOOKS.md" "$repo_root/instructions/AGENTS.md" "$repo_root/instructions/CLAUDE.md" "$repo_root/instructions/GEMINI.md" \
  || fail "instruction entrypoints must reference only current instruction files"

say "validate: docs and instructions stay within current scope"
! grep -REq "autonomous-runner|skill-improvement-bot|safe_delete_guard|HOOKS\\.md|schedule-update|schedule-skill-improvement" \
  "$repo_root/README.md" "$repo_root/setup.md" "$repo_root/docs" "$repo_root/instructions" \
  || fail "docs or instructions reference out-of-scope paths"
grep -Fq "Codex App Automations" "$repo_root/README.md" \
  || fail "README.md must prefer Codex App Automations for daily review docs"
grep -Fq "Codex App Automations" "$repo_root/setup.md" \
  || fail "setup.md must prefer Codex App Automations for daily review docs"
grep -Fq '## Coding Collaboration Defaults' "$repo_root/instructions/AI_AGENT_INSTRUCTIONS.md" \
  || fail "shared instructions must include coding collaboration defaults"
grep -Fq 'Coding Collaboration Defaults' "$repo_root/README.md" \
  || fail "README.md must mention coding collaboration defaults"
grep -Fq 'daily-llm-history-instruction-review' "$repo_root/docs/codex-automation-daily-review.md" \
  || fail "Codex automation guide must include the daily review skill name"
for launchd_doc in "$repo_root/README.md" "$repo_root/setup.md" "$repo_root/docs/codex-automation-daily-review.md"; do
  grep -Fq 'launchd は使いません' "$launchd_doc" \
    || fail "daily review docs must state launchd is not used: ${launchd_doc#$repo_root/}"
done
! grep -REq "cron-log|scripts/daily-llm-history-instruction-review" \
  "$repo_root/README.md" "$repo_root/setup.md" "$repo_root/docs" "$repo_root/instructions" "$repo_root/skills/daily-llm-history-instruction-review" \
  || fail "daily history review docs must not reintroduce launchd runner paths"
grep -Fq 'install_skill_links' "$repo_root/scripts/setup.sh" \
  || fail "setup.sh must install shared skill links"
grep -Fq 'remove_skill_links' "$repo_root/scripts/uninstall.sh" \
  || fail "uninstall.sh must remove shared skill links"
grep -Fq 'skills_status_for' "$repo_root/scripts/health-check.sh" \
  || fail "health-check.sh must report shared skill links"

say "validate: health-check runs"
AI_AGENT_CONFIG_HOME="$repo_root" sh "$repo_root/scripts/health-check.sh" --json >/dev/null

say "validate: setup dry-run runs"
AI_AGENT_DRY_RUN=1 AI_AGENT_CONFIG_HOME="$repo_root" AI_AGENT_REQUIRE_LLM_CLIS=0 sh "$repo_root/scripts/setup.sh" >/dev/null

say "validation complete"
