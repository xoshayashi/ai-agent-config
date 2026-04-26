# Skill Template

Use this folder as the starting point for new reusable skills.

`SKILL.md.template` is intentionally named with the `.template` suffix so setup scripts do not install this folder as a real skill. When creating a new skill, copy the template into a new folder such as `skills/my-skill/SKILL.md`, then fill in the placeholders.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md.template` | Lean skill body with frontmatter, workflow, references, and self-review prompts. |
| `references/evidence-notes.md.template` | Place to keep source-backed design notes without bloating `SKILL.md`. |
| `tests/activation-prompts.md` | Starter prompts for checking whether the skill activates at the right time. |
| `tests/self-review-checklist.md` | Quality gate before the skill is treated as complete. |
| `agents/openai.yaml.template` | Optional agent metadata template for environments that support it. |
