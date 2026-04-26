# Research Foundations For Skill And Agent Design

This reference gives `skill-design-research` its baseline research backbone. Use it when designing skills, agents, prompts, reusable workflows, delegation patterns, self-review loops, or evaluation checks.

Do not treat this as a fixed citation list. Add domain-specific sources when the target skill needs them, and only move a source into `SKILL.md` when it changes behavior every time the skill fires.

## Baseline Design Principles

| Principle | Supporting Sources | Design Implication |
|---|---|---|
| **Separate workflows from agents.** | Anthropic's agent engineering guidance distinguishes predefined workflows from systems where models dynamically direct tools and process. Recent agent surveys also organize agent design around construction, application, and evaluation. | For each skill or reusable workflow, decide whether it needs a deterministic workflow, an agentic loop, or a hybrid. Do not add agent autonomy when a clear workflow is enough. |
| **Design activation metadata as part of the product.** | Agent Skills uses progressive disclosure: agents first see only name and description, then load full instructions after a match. OpenAI's Skills docs likewise describe skill invocation from `name`, `description`, and `path` metadata. | Treat frontmatter `description`, aliases, default prompts, routing metadata, and should-trigger/should-not-trigger examples as core deliverables, not packaging afterthoughts. |
| **Interleave reasoning, action, and observations for tool-using agents.** | ReAct shows that combining reasoning traces with task-specific actions helps models plan, update, handle exceptions, and gather external information. | For tool-heavy skills, specify the action loop: plan, call tool, inspect observation, revise plan, and stop when acceptance criteria are met. |
| **Use feedback and self-review as an explicit improvement loop.** | Reflexion and Self-Refine both support test-time improvement through feedback, reflection, and iterative revision without changing model weights. | For fragile or high-quality deliverables, include a bounded review/refinement loop with concrete critique dimensions and a stop condition. |
| **Evaluate prompts and workflows against task criteria, not vibes.** | OpenAI's evaluation guidance emphasizes evals because generative systems are variable; DSPy frames prompts and pipelines as optimizable against metrics. | Define success criteria, failure modes, test prompts, rubrics, or task-specific checks for non-trivial skills. |
| **Prefer source-backed heuristics over generic advice.** | Surveys and official references are useful for broad patterns, while benchmarks, standards, and domain literature are needed for task-specific reliability. | A skill should encode only the heuristics that materially change behavior for that domain or workflow. Keep generic capability assumptions out. |
| **Keep Web Search queries broad enough to find evidence.** | Search guidance from official and library sources treats result count as feedback: add terms to narrow broad results, remove or broaden terms when results are too sparse. | Start with concise, high-signal query families and iterate. Avoid packing the full research question and every constraint into one search string. |

## Source Map

| Source | Type | Use It For |
|---|---|---|
| [Agent Skills overview](https://agentskills.io/home) | Open standard documentation | Progressive disclosure, cross-product skill structure, required `SKILL.md` metadata |
| [Agent Skills, "Optimizing skill descriptions"](https://agentskills.io/skill-creation/optimizing-descriptions) | Open standard guidance | Trigger description design, should-trigger and should-not-trigger query sets |
| [Agent Skills, "Best practices for skill creators"](https://agentskills.io/skill-creation/best-practices) | Open standard guidance | Keeping skills lean, progressive disclosure, validation loops, procedures over declarations |
| [OpenAI, "Skills"](https://developers.openai.com/api/docs/guides/tools-skills) | Official documentation | Skill mounting, metadata-based invocation, local vs hosted skill behavior, safety considerations |
| [Anthropic, "Building effective agents"](https://www.anthropic.com/engineering/building-effective-agents) | Official engineering guidance | Workflow vs agent distinction, parallelization, orchestrator-worker, evaluator-optimizer patterns |
| [Wang et al., "A survey on large language model based autonomous agents"](https://link.springer.com/article/10.1007/s11704-024-40231-1) | Peer-reviewed survey | Agent construction, application areas, evaluation strategies, field taxonomy |
| [Chowa et al., "From language to action"](https://link.springer.com/article/10.1007/s10462-025-11471-9) | Peer-reviewed review | LLMs as autonomous agents and tool users; current survey context |
| [Yao et al., "ReAct"](https://openreview.net/forum?id=WE_vluYUL-X) | Peer-reviewed conference paper | Reasoning-plus-action loops for agents that use tools or external information |
| [Shinn et al., "Reflexion"](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html) | Peer-reviewed conference paper | Feedback, reflection, and memory for iterative agent improvement |
| [Madaan et al., "Self-Refine"](https://arxiv.org/abs/2303.17651) | Preprint | Self-feedback and iterative refinement patterns for outputs |
| [Khattab et al., "DSPy"](https://openreview.net/forum?id=PFS4ffN9Yx) | Research paper / workshop | Treating prompts and LM pipelines as structured, optimizable programs |
| [OpenAI, "Evaluation best practices"](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | Official documentation | Eval design for variable AI systems, workflow-level testing, instruction-following checks |

## Minimum Evidence Packet

Before finalizing a non-trivial skill or agent, capture:

| Field | Required Content |
|---|---|
| **Design question** | What design choice is not obvious and needs evidence |
| **Evidence used** | 3-7 strongest sources, labeled by source type |
| **Activation plan** | Trigger description, likely user phrasings, should-trigger examples, and should-not-trigger boundaries |
| **Design implications** | What each source changes in the skill, workflow, trigger, or evaluation |
| **Validation plan** | How the skill's behavior will be checked on realistic tasks |
| **Context control** | What belongs in `SKILL.md` vs `references/` |

## Anti-Patterns

- Do not cite papers without turning them into design implications.
- Do not treat one preprint, vendor article, or benchmark as a universal rule.
- Do not hide activation-critical conditions only inside `SKILL.md`; they must appear in frontmatter description or other routing metadata.
- Do not add long literature summaries to `SKILL.md`.
- Do not encode default model capabilities as "skill instructions" unless a repeated quality gap or fragile workflow justifies it.
- Do not let delegated agents inherit broad research tasks without distinct scopes, expected outputs, and synthesis criteria.
