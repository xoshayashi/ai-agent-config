# Activation Examples

Use these examples when reviewing whether `skill-design-research` will activate for the right work without becoming over-broad.

## Should Trigger

- "Create a new skill for research strategy, but ground it in recent papers and official sources."
- "This skill did not fire. Review its activation conditions and frontmatter description."
- "Design an agent delegation workflow with a strong research backbone."
- "Update this instruction module so it routes to the right skill and includes a self-review loop."
- "Make a slash command for planning; use best practices and keep it portable across LLM CLIs."
- "Review whether this prompt workflow is evidence-backed or just generic advice."
- "Build a skill for self-review and evaluation based on academic sources."
- "Tune the trigger description for this skill so realistic user requests activate it."

## Should Not Trigger

- "Fix this typo in the README."
- "Convert this CSV to JSON."
- "Summarize this PDF quickly."
- "What is the current time?"
- "Run the existing test suite."
- "Add one missing import to this file."

## Review Questions

- Does the frontmatter `description` mention the artifact types users actually name, such as skills, agents, prompts, instructions, workflows, slash commands, and activation?
- Does it cover implicit user intent, such as "why did this not fire?" or "make this research-backed," without requiring the exact skill name?
- Is there a clear boundary that excludes tiny edits and ordinary tasks capable agents can handle without this skill?
- Are UI metadata and default prompts consistent with the frontmatter description?
