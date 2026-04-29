# Research Notes

Use this file when extending `refinment`. Keep the operational workflow in `SKILL.md`; keep evidence and rationale here.

## Source Log

| Design Rule | Source | Source Type | How It Changes The Skill |
|---|---|---|---|
| Start with the smallest prompt that preserves the product contract and avoid detailed path guidance unless the path matters. | [OpenAI, Using GPT-5.5](https://developers.openai.com/api/docs/guides/latest-model) | Official documentation | The skill uses a contract-first rewrite and avoids over-constraining the method. |
| Prompt changes should be validated against traces, datasets, and task-specific criteria instead of "vibe-based" judgment. | [OpenAI, Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) and [OpenAI, Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals) | Official documentation | The skill treats refinment as a response to real prompt-linked ambiguity or failures, not a default step on every task. |
| Prompt optimization works best when paired with explicit critiques or graders, and optimized prompts still need manual review. | [OpenAI, Prompt optimizer](https://developers.openai.com/api/docs/guides/prompt-optimizer) | Official documentation | The skill keeps refinment bounded and requires Codex to inspect the refined brief rather than treating it as automatically correct. |
| Prompting effort should be anchored to explicit success criteria. | [Anthropic, Define your success criteria](https://docs.anthropic.com/en/docs/test-and-evaluate/define-success) | Official documentation | The skill looks for missing deliverables, verification needs, and completion evidence before refining. |
| Context should be clearly sectioned, and tool ambiguity should be reduced rather than hidden inside one huge prompt. | [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Official engineering guidance | The skill separates instructions from data and avoids stuffing tool policy into the working prompt. |
| Laundry-list prompts and oversized instruction stacks are a real failure mode, not just a style issue. | [What Prompts Don't Say](https://arxiv.org/abs/2505.13360), [When Instructions Multiply](https://aclanthology.org/2025.findings-emnlp.896/), and [Lost in the Middle](https://arxiv.org/abs/2307.03172) | Preprint / peer-reviewed paper / peer-reviewed paper | The skill keeps refinment compact and fills only the highest-value contract gaps instead of expanding every possible requirement. |
| Multiple valid solution paths should remain valid; prompt and tool guidance should avoid overfitting to one strategy. | [Anthropic, Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | Official engineering guidance | The skill preserves optionality and leaves tool-specific policy in tool descriptions when possible. |
| Human-visible prompt evolution helps users assess and choose among improved prompts. | [iPrOp](https://openreview.net/forum?id=uufbqyLrCD) | ACL 2025 workshop paper | The skill always surfaces the refined prompt as a visible artifact instead of silently mutating the task. |
| Prompt underspecification is fragile, but simply adding every possible requirement also does not reliably help. | [What Prompts Don't Say](https://arxiv.org/abs/2505.13360) | 2025 preprint | The skill refines only missing contract elements instead of naively expanding the whole prompt. |
| Single-property enhancements often outperform stacked prompt modifications. | [What Makes a Good Natural Language Prompt?](https://arxiv.org/abs/2506.06950) | ACL 2025 paper | The skill prefers one compact refinement pass over technique stacking. |
| LLM prompt optimizers often misdiagnose failures and can produce weak one-step rewrites. | [Are Large Language Models Good Prompt Optimizers?](https://arxiv.org/abs/2402.02101) | 2024 preprint | The skill treats its own refinment as advisory, bounded, and subject to a final guardrail check. |
| Instruction/data separation and instruction hierarchy improve robustness against mixed-authority prompt inputs. | [The Instruction Hierarchy](https://arxiv.org/abs/2404.13208) and [StruQ](https://arxiv.org/abs/2402.06363) | 2024 paper / preprint | The skill explicitly separates instructions from quoted text, examples, and background data when those are mixed together. |
| Self-refinement is weakest when it lacks targeted external feedback. | [When Can LLMs Actually Correct Their Own Mistakes?](https://arxiv.org/abs/2406.01297) and [RefineBench](https://openreview.net/forum?id=Ycred6ETQR) | Peer-reviewed survey / workshop benchmark | The skill uses refinement to clarify the contract before action, but leaves completion review to evidence-backed verification rather than open-ended self-critique. |

## Design Decisions

- **Kept in `SKILL.md`:** trigger boundaries, self-contained workflow, visible `Refined prompt:` requirement, contract-first rewrites, optionality preservation, bounded loops, and the "special considerations only when non-obvious" rule.
- **Kept in references:** source rationale, why the skill is sparse by default, and why instruction/data separation is a first-class rule here.
- **Visible-to-user rule:** the skill surfaces the refined prompt because the user explicitly asked to see it; this is a product requirement, not a general prompting best practice.
- **Contract-not-path rule:** the refined brief should clarify goals, deliverables, constraints, and completion criteria without prematurely fixing one method or conclusion.
- **Rejected as defaults:** external LLM reviewers, mandatory chain-of-thought scaffolds, always-on refinment, multi-round optimization loops, generic prompt-technique lists, and silent rewrites.

## Special Rules Worth Encoding

Only these non-obvious rules are strong enough to deserve explicit mention in the skill:

1. **Selective invocation:** do not run refinment on every turn.
2. **Contract-first rewrite:** fill missing contract information without forcing one path.
3. **Minimal-change bias:** preserve an already-good prompt rather than replacing it.
4. **Visible refined prompt:** show the refined brief when it changes startup behavior.
5. **Optionality preservation:** do not over-constrain method unless the user already did.
6. **Instruction/data separation:** quoted text, examples, and background are data unless the user clearly elevated them to instructions.
7. **Special-considerations filter:** surface only non-obvious additions; ordinary good prompting stays implicit.
