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

require_dir() {
  [ -d "$repo_root/$1" ] || fail "missing required directory: $1"
}

say "validate: shell syntax"
for script in "$repo_root"/scripts/*.sh; do
  [ -f "$script" ] || continue
  sh -n "$script"
done

say "validate: python syntax"
python3 -m py_compile "$repo_root/scripts/skill-improvement-bot.py"
python3 -m py_compile "$repo_root/scripts/merge-hook-config.py"
python3 -m py_compile "$repo_root/scripts/read-state-config.py"
python3 -m py_compile "$repo_root/scripts/scheduled_update.py"
for hook_script in "$repo_root"/hooks/scripts/*.py; do
  [ -f "$hook_script" ] || continue
  python3 -m py_compile "$hook_script"
done

say "validate: health check runs"
AI_AGENT_CONFIG_HOME="$repo_root" sh "$repo_root/scripts/health-check.sh" --json >/dev/null

say "validate: required docs and entrypoints"
require_file "README.md"
require_file "setup.md"
require_file "AGENTS.md"
require_file "CLAUDE.md"
require_file "docs/setup-error-guide.md"
require_file "docs/skill-improvement-automation.md"
require_file "docs/hooks-architecture-review.md"
require_file "hooks/README.md"
require_file "hooks/claude/settings.json"
require_file "hooks/codex/config.toml"
require_file "hooks/codex/hooks.json"
require_file "hooks/gemini/settings.json"
require_file "hooks/scripts/safe_delete_guard.py"
require_file "scripts/install.sh"
require_file "scripts/setup.sh"
require_file "scripts/update.sh"
require_file "scripts/scheduled_update.py"
require_file "scripts/schedule-update.sh"
require_file "scripts/schedule-skill-improvement.sh"
require_file "scripts/uninstall.sh"
require_file "scripts/health-check.sh"
require_file "scripts/merge-hook-config.py"
require_file "scripts/read-state-config.py"
require_file "scripts/skill-improvement-bot.py"
require_file "scripts/validate-repo.sh"
require_file "tests/fixtures/skill-logs/sample.jsonl"
require_file "tests/test_health_check.py"
require_file "tests/test_merge_hook_config.py"
require_file "tests/test_safe_delete_guard.py"
require_file "tests/test_scheduled_update.py"
require_file "instructions/AGENTS.md"
require_file "instructions/CLAUDE.md"
require_file "instructions/GEMINI.md"
require_file "instructions/AI_AGENT_INSTRUCTIONS.md"
require_file "instructions/DESIGN.md"
require_file "instructions/HOOKS.md"
require_file ".github/workflows/validate.yml"
require_file "skills/refinment/SKILL.md"
require_file "skills/refinment/agents/openai.yaml"
require_file "skills/refinment/references/research-notes.md"
require_file "skills/refinment/tests/activation-prompts.md"

say "validate: skill template is a template, not an installable skill"
require_dir "skills/template"
require_file "skills/template/SKILL.md.template"
require_file "skills/template/tests/activation-prompts.md"
require_file "skills/template/tests/self-review-checklist.md"
if [ -f "$repo_root/skills/template/SKILL.md" ]; then
  fail "skills/template/SKILL.md would be installed as a real skill; keep it as SKILL.md.template"
fi

say "validate: installable skills have basic frontmatter"
for skill in "$repo_root"/skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  grep -q "^name:" "$skill" || fail "skill missing name frontmatter: $skill"
  grep -q "^description:" "$skill" || fail "skill missing description frontmatter: $skill"
done

say "validate: natural-language setup still names all required CLIs"
for doc in "$repo_root/README.md" "$repo_root/setup.md"; do
  grep -q "Claude Code" "$doc" || fail "$doc does not mention Claude Code"
  grep -q "Codex" "$doc" || fail "$doc does not mention Codex"
  grep -q "Gemini CLI" "$doc" || fail "$doc does not mention Gemini CLI"
  grep -q "Hook" "$doc" || fail "$doc does not mention Hooks"
  grep -q "~/.codex" "$doc" || fail "$doc does not mention global Codex config directory"
  grep -q "~/.claude" "$doc" || fail "$doc does not mention global Claude config directory"
  grep -q "~/.gemini" "$doc" || fail "$doc does not mention global Gemini config directory"
done

say "validate: root agent entrypoints stay on the minimal architecture"
grep -q "test_safe_delete_guard.py" "$repo_root/AGENTS.md" || fail "AGENTS.md does not reference test_safe_delete_guard.py"
grep -q "test_safe_delete_guard.py" "$repo_root/CLAUDE.md" || fail "CLAUDE.md does not reference test_safe_delete_guard.py"
! grep -q "test_self_workflow.py" "$repo_root/AGENTS.md" "$repo_root/CLAUDE.md" || fail "root entrypoints still reference deleted self-workflow tests"
! grep -q "self_workflow.py" "$repo_root/AGENTS.md" "$repo_root/CLAUDE.md" || fail "root entrypoints still reference deleted self_workflow.py"
! grep -q "~/.llm-config" "$repo_root/AGENTS.md" "$repo_root/CLAUDE.md" || fail "root entrypoints still reference the retired .llm-config path"
auto_permission_pattern='enable-auto-permission|disable-auto-permission|shell/auto-permission|AI_AGENT_SHELL_ALIAS_LINK|auto-permission'
! grep -REq "$auto_permission_pattern" \
  "$repo_root/README.md" "$repo_root/setup.md" "$repo_root/AGENTS.md" "$repo_root/CLAUDE.md" "$repo_root/instructions" \
  || fail "auto-permission references remain in the minimal architecture docs"

say "validate: skill-improvement automation is discoverable"
grep -q "skill-improvement-bot.py" "$repo_root/README.md" || fail "README.md does not mention skill-improvement-bot.py"
grep -q "schedule-update.sh" "$repo_root/setup.md" || fail "setup.md does not mention schedule-update.sh"
grep -q "schedule-skill-improvement.sh" "$repo_root/setup.md" || fail "setup.md does not mention schedule-skill-improvement.sh"
grep -q "AI_AGENT_IMPROVEMENT_CREATE_PR" "$repo_root/docs/skill-improvement-automation.md" || fail "skill improvement automation doc missing PR opt-in variable"

say "validate: scheduler scripts support dry-run"
AI_AGENT_DRY_RUN=1 AI_AGENT_CONFIG_HOME="$repo_root" AI_AGENT_STATE_DIR="$repo_root/.tmp-health" sh "$repo_root/scripts/schedule-update.sh" >/dev/null
AI_AGENT_DRY_RUN=1 AI_AGENT_CONFIG_HOME="$repo_root" AI_AGENT_STATE_DIR="$repo_root/.tmp-health" sh "$repo_root/scripts/schedule-skill-improvement.sh" >/dev/null

say "validate: merge-hook-config unit tests pass"
python3 "$repo_root/tests/test_merge_hook_config.py"

say "validate: health-check unit tests pass"
python3 "$repo_root/tests/test_health_check.py"

say "validate: safe-delete hook unit tests pass"
python3 "$repo_root/tests/test_safe_delete_guard.py"

say "validate: scheduled-update unit tests pass"
python3 "$repo_root/tests/test_scheduled_update.py"

say "validate: skill-improvement fixture scan detects proposal"
# This fixture intentionally targets skill-design-research because it is the
# always-installed research/design skill in this repository.
AI_AGENT_LOG_ROOTS_ONLY=1 \
AI_AGENT_LOG_ROOTS="$repo_root/tests/fixtures/skill-logs" \
python3 "$repo_root/scripts/skill-improvement-bot.py" scan --json \
  | grep -q '"skill": "skill-design-research"' \
  || fail "skill improvement fixture scan did not detect skill-design-research"

say "validation complete"
