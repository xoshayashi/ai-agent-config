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

say "validate: health check runs"
AI_AGENT_CONFIG_HOME="$repo_root" sh "$repo_root/scripts/health-check.sh" --json >/dev/null

say "validate: required docs and entrypoints"
require_file "README.md"
require_file "setup.md"
require_file "docs/setup-error-guide.md"
require_file "docs/compatibility.md"
require_file "compatibility/llm-cli-matrix.yml"
require_file "scripts/install.sh"
require_file "scripts/setup.sh"
require_file "scripts/update.sh"
require_file "scripts/schedule-update.sh"
require_file "scripts/uninstall.sh"
require_file "scripts/health-check.sh"
require_file "scripts/validate-repo.sh"
require_file "instructions/AGENTS.md"
require_file "instructions/CLAUDE.md"
require_file "instructions/GEMINI.md"
require_file "instructions/AI_AGENT_INSTRUCTIONS.md"
require_file "instructions/.github/copilot-instructions.md"

say "validate: compatibility matrix mentions supported LLM CLIs"
grep -q "claude-code:" "$repo_root/compatibility/llm-cli-matrix.yml" || fail "compatibility matrix missing claude-code"
grep -q "codex:" "$repo_root/compatibility/llm-cli-matrix.yml" || fail "compatibility matrix missing codex"
grep -q "gemini-cli:" "$repo_root/compatibility/llm-cli-matrix.yml" || fail "compatibility matrix missing gemini-cli"

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
done

say "validation complete"
