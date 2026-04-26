# Skill Self-Review Checklist

Use this before treating a new or updated skill as complete.

## Activation

- The frontmatter `description` names the user intent, not only an internal implementation detail.
- The skill has at least three realistic should-trigger prompts and three should-not-trigger prompts.
- The skill avoids broad phrases that would capture ordinary writing, coding, or Q&A work.

## Scope

- `SKILL.md` contains only the rules that must always load.
- Long examples, source notes, benchmarks, and domain background live in `references/`.
- The skill does not duplicate behavior that Claude Code, Codex, or Gemini CLI already handle well by default.

## Evidence

- Non-obvious workflow choices cite official references, academic sources, standards, benchmarks, or clearly marked assumptions.
- Source strength is labeled in the evidence notes.
- Evidence changes the skill's behavior, checks, or boundaries rather than being decorative.
- Web Search queries used for evidence gathering were concise enough to return useful results, with separate focused queries for different source types or angles.

## Portability

- Tool-specific behavior is labeled with a compatibility tag from `docs/compatibility.md`.
- The skill can still be understood as plain instructions if a specific LLM CLI ignores vendor-specific metadata.
- Any setup, test, or verification command has a safe fallback or explanation.

## Verification

- The skill was read in the form the LLM will actually load.
- Activation prompts were tested or manually reviewed against the frontmatter description.
- The final review found no mismatch between skill name, description, workflow, references, and expected output.
