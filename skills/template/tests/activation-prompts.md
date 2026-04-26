# Activation Test Prompts

Use these prompts when creating or reviewing a skill from `skills/template/SKILL.md.template`.

## Should Trigger

Replace these with realistic prompts for the new skill:

- "Create a reusable workflow for replace-with-domain-task."
- "Review whether this skill activates for replace-with-user-intent."
- "Build a skill that helps with replace-with-specialized-output."

## Should Not Trigger

Replace these with boundary prompts that the base LLM can handle without the skill:

- "Explain replace-with-basic-concept in one paragraph."
- "Fix a small typo in this text."
- "Answer a general question that does not need replace-with-specialized-workflow."

## Ambiguous Prompts

Replace these with prompts where the agent should clarify or use a lighter workflow:

- "Can you help with replace-with-broad-area?"
- "Make this better."
- "Research this."

## Review Notes

- **Trigger wording:** Does the `description` include natural phrases a user would actually type?
- **Boundary:** Are should-not-trigger cases narrow enough to avoid loading the skill for generic work?
- **Portability:** Does activation depend on one LLM CLI's private feature, or will it work through plain language?
- **Evidence:** If the skill includes non-obvious rules, are they backed by `references/evidence-notes.md.template` or another reference file?
