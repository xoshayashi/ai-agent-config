---
name: refinment
description: Use this skill when Codex should refine an ambiguous prompt or brief only when needed, keep the refinement self-contained, show the refined prompt when it materially changes the contract, and preserve optionality instead of over-constraining the task. Trigger on meaningful ambiguity, conflicting constraints, instruction/data mixing, or ambiguous next-step briefs in spec, implementation, or verification. Skip trivial chat, already-clear prompts, routine phase transitions, and turns already executing from the current refinment brief.
---

# Refinement (`refinment`)

Use this skill to run a refinement pass on a working prompt or brief before acting, while keeping Codex self-contained. The historical skill id in this repo is `refinment`.

## Core Rules

- **Run only when it materially helps.** Use refinment for non-trivial new tasks or ambiguous brief handoffs, not as decoration on every turn or on routine phase changes.
- **Stay self-contained.** Do not call another LLM, subprocess reviewer, or external prompt improver from this skill.
- **Refine sparingly.** Default to the original prompt unless there is a real contract gap, conflict, or instruction/data ambiguity worth fixing.
- **Show the refined prompt only when you actually refine.** Put a short `Refined prompt:` block in the next visible user update before continuing the work.
- **Skip silently by default.** If no refinement is needed, continue the task unless the user explicitly asked to inspect the prompt or brief.
- **No silent mutation.** If you changed the working prompt in a meaningful way, surface the change explicitly.
- **Preserve authority.** The refined brief must not override system, developer, tool, or user instructions.
- **Rewrite the contract, not the path.** Clarify the goal, deliverable, hard constraints, evidence needs, and stopping conditions without hard-locking one method, tool, reasoning style, conclusion, file layout, or output shape unless the user already required that.
- **Prefer minimal edits.** If the original prompt is already strong, keep the refinment small and focused.
- **Keep the result compact.** Do not turn a short, fixable ambiguity into a long laundry list of edge cases.
- **Add only non-obvious special considerations.** Do not pad the brief with generic prompt-engineering boilerplate. Add a special rule only when it is materially relevant and not already normal agent behavior.
- **Keep exact entities intact.** Preserve quoted constraints, paths, commands, symbols, IDs, branch names, and error text.
- **Keep instructions and data separate.** When the prompt mixes instructions with quoted text, examples, background documents, or user-provided data, make that separation clearer instead of letting everything blur together.
- **Keep tool policy local.** Do not stuff tool-specific operating policy into the refined prompt when it belongs in tool descriptions or a higher-priority instruction layer.
- **Bound the loop.** One refinment pass by default. Do not turn this into open-ended prompt optimization.
- **Prevent recursion.** If the current turn is already executing from the latest refinment brief, continue the task instead of refining again.

## Use When

- A new task prompt is missing task-critical contract information such as the objective, deliverable, hard constraints, verification needs, or output shape.
- A new task prompt has multiple constraints, ambiguity, repo or file context, or a high chance of preventable misinterpretation.
- The prompt contains conflicting or competing requirements.
- Instructions and quoted/background data are mixed in a way that risks authority confusion.
- There is known evidence that similar prompts caused prompt-linked failures or regressions.
- The prompt is being adapted to a materially different model or workflow and needs a fresh, contract-preserving baseline.
- A spec draft needs one internal readiness pass before implementation starts.
- An implementation stop boundary is ambiguous enough that the next step, target files, or verification goal is unclear.
- A verification stop boundary needs a tighter completion brief before deciding whether the task is done.

## Do Not Use When

- The user only said thanks, stop, pause, or asked for a simple status update.
- The current turn is a short follow-up nudge on an already-active task and the working brief is still clear.
- The prompt is already clear, self-contained, executable, and unlikely to benefit from another pass.
- The likely problem is retrieval, tooling, missing context, model choice, or environment setup rather than wording.
- The user explicitly wants the original wording left untouched.
- The prompt is intentionally open-ended and that openness is part of the task.
- The next step is a normal implementation -> test or test -> report transition with no real contract ambiguity.
- You would only be restating generic good practice with no task-specific value.

## Workflow

1. **Classify the mode.** Use one of: `task_prompt`, `spec`, `implementation`, `verification`.
2. **Extract the contract.** Pull out:
   - objective
   - deliverable
   - hard constraints
   - evidence or verification needs
   - explicitly preserved open choices
3. **Detect gaps or conflicts.** Look for missing contract fields, conflicting requirements, or mixed instruction/data boundaries.
4. **Decide `skip` or `refine`.** Refine only if at least one real trigger is present and no skip condition blocks it.
5. **If refining, produce one compact Refinment Brief.** Fill only the missing contract elements, preserve exact entities, and avoid generic prompt-fluff.
6. **Run the guardrail check.** Before returning the refined brief, ask:
   - Did this clarify the contract rather than force a path?
   - Did it preserve all explicit constraints?
   - Did it keep examples as examples?
   - Did it avoid unnecessary tool, format, or reasoning commitments?
   - Did it preserve useful user ambiguity?
   - Did it stay compact enough to help rather than bloat context?
7. **Keep special considerations narrow.** Include only non-obvious additions that materially improve execution; routine clarity, structure, and constraint preservation happen by default and do not need to be called out.
8. **Act from the result in the same turn.**
   - `skip`: continue from the original brief without a `No refinement needed` block unless the user asked to inspect it
   - `task_prompt`: show `Refined prompt:` to the user, then start the work from it
   - `spec`: revise or continue the spec from the refined brief
   - `implementation`: do the next concrete implementation step or move into verification when the work is ready
   - `verification`: run the smallest missing verification/self-review step or declare completion only when evidence is real

## Output Shape

Use a small, readable block only when you actually refine or when the user explicitly asked to see the result:

```text
Refined prompt:
- ...

What changed:
- ...

Preserved constraints:
- ...

Open choices preserved:
- ...   # omit this section when nothing non-obvious must be called out
```

When the input is a spec, implementation brief, or verification brief rather than a raw user prompt, replace `prompt` with `brief` where that reads more naturally. Keep the same visibility and preservation rules.

## References

- Use [references/research-notes.md](references/research-notes.md) when extending this skill or checking which non-obvious refinment rules are source-backed.
- Use [tests/activation-prompts.md](tests/activation-prompts.md) to check trigger breadth and over-trigger boundaries.
