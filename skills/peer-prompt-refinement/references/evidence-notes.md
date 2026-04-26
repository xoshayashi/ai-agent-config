# Evidence Notes

Use this file when reviewing or extending `peer-prompt-refinement`. Keep the operational workflow in `SKILL.md`; keep evidence and rationale here.

## Source Log

| Design Rule | Source | Source Type | How It Changes The Skill |
|---|---|---|---|
| Use LLMs as prompt optimizers, but keep a bounded optimization loop. | [Large Language Models as Optimizers / OPRO](https://openreview.net/forum?id=Bb4VGOWELI) | Research paper | The skill asks one peer LLM to improve the prompt before execution, but does not start open-ended prompt search. |
| Self-feedback and revision can improve outputs without changing model weights. | [Self-Refine](https://arxiv.org/abs/2303.17651) | Preprint | Peer output must include missing considerations and risks, not only a rewritten prompt. |
| Iterative reflection can help agent behavior, but needs bounded loops. | [Reflexion](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html) | Peer-reviewed conference paper | The skill enforces "run once per user prompt" and recursion guards. |
| Tool-using agents benefit from explicit action/observation loops. | [ReAct](https://openreview.net/forum?id=WE_vluYUL-X) | Peer-reviewed conference paper | The skill has a concrete sequence: decide, build context, call peer, inspect, activate skills, execute. |
| Agent workflows should distinguish fixed workflow from open-ended autonomy. | [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Official engineering guidance | This is implemented as a deterministic preflight workflow, not a multi-agent debate loop. |
| Skill activation depends heavily on concise descriptions and realistic trigger boundaries. | [Agent Skills, Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) | Open standard guidance | The frontmatter description is intentionally broad but includes skip conditions and recursion boundaries. |
| Prompt optimization methods can be brittle and task-dependent. | [Are Large Language Models Good Prompt Optimizers?](https://arxiv.org/abs/2402.02101) | Preprint | Peer suggestions are treated as advisory; the main agent must preserve original constraints and reject harmful drift. |
| Prompting techniques are numerous and task-dependent, so a skill should choose technique families deliberately. | [The Prompt Report](https://arxiv.org/abs/2406.06608) | Systematic survey / preprint | The skill does not stack many named prompt tricks; it asks the peer to improve the prompt around the task's actual missing properties. |
| Automatic prompt optimization is useful but remains a rapidly changing field with open challenges. | [A Systematic Survey of Automatic Prompt Optimization Techniques](https://aclanthology.org/2025.emnlp-main.1681/) | Peer-reviewed EMNLP 2025 survey | The peer LLM produces an advisory candidate prompt that the main agent must inspect before use. |
| Prompt quality can be evaluated as properties, and multi-property enhancements are not always better than targeted single-property improvements. | [What Makes a Good Natural Language Prompt?](https://arxiv.org/abs/2506.06950) | 2025 preprint | The skill adds the "avoid prompt-trick stacking" rule and favors the smallest high-leverage prompt improvement. |
| Abstracting the problem before detailed reasoning can improve difficult reasoning tasks. | [Take a Step Back](https://proceedings.iclr.cc/paper_files/paper/2024/hash/592da1445a51e54a3987958b5831948f-Abstract-Conference.html) | Peer-reviewed ICLR 2024 paper | Improved prompts should express goals and governing principles before concrete tactics when the task is complex. |
| Letting the model compose a task-specific reasoning structure can outperform fixed reasoning prompts. | [Self-Discover](https://openreview.net/forum?id=BROvXhmzYK) | Peer-reviewed NeurIPS 2024 paper | The skill asks the peer to preserve choice and suggest workflow options instead of hard-coding one reasoning path. |
| Verification questions can reduce hallucination in fact-heavy generation. | [Chain-of-Verification](https://openreview.net/forum?id=ek3GqAs2uO) | ICLR 2024 workshop paper | Peer output may include verification or self-check ideas when factuality, research, or implementation correctness matters. |
| Long-context models can underuse information buried in the middle. | [Lost in the Middle](https://arxiv.org/abs/2307.03172) | TACL paper | The Context Packet should put current ask and critical constraints where they are easy to notice, not bury them in long history. |
| Context engineering treats prompt quality as systematic selection, processing, and management of information payloads. | [A Survey of Context Engineering for LLMs](https://arxiv.org/abs/2507.13334) | 2025 survey preprint | The skill explicitly engineers the Context Packet rather than only rewriting wording. |
| Moderate prompt compression can help long-context performance, but lost technical entities can break tasks. | [An Empirical Study on Prompt Compression](https://arxiv.org/abs/2505.00019) | ICLR 2025 workshop paper | The skill summarizes irrelevant history while preserving exact paths, symbols, errors, and IDs. |
| Structured input/output can improve adherence when instructions are counterintuitive. | [Structured Outputs in Prompt Engineering](https://aclanthology.org/2025.wasp-main.13/) | ACL WASP 2025 workshop paper | The peer request uses explicit structured sections and required fields. |
| Prompt injection work supports separating instructions from data and respecting authority levels. | [StruQ](https://arxiv.org/abs/2402.06363) and [Instruction Hierarchy](https://arxiv.org/abs/2404.13208) | USENIX 2025 paper / 2024 preprint | The Context Packet separates instructions, background, and quoted data; peers cannot override higher-priority constraints. |
| Chain-of-thought prompting has model- and task-dependent value and can increase variability. | [Prompting Science Report 2](https://arxiv.org/abs/2506.07142) | 2025 technical report / preprint | The skill does not add verbose chain-of-thought by default; it prefers concise rationale, checks, or verification where useful. |
| Gemini CLI supports headless prompt mode. | [Gemini CLI Headless Mode](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md) | Official documentation | The routing reference uses Gemini `--prompt` / `-p` and text output. |
| Gemini CLI supports piping stdin as context in headless workflows. | [Gemini CLI Automation Tutorial](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/tutorials/automation.md) | Official documentation | The routing reference pipes the Context Packet via stdin instead of putting long user context in argv. |
| Codex CLI supports non-interactive `codex exec`, prompt-plus-stdin context, and `codex exec -` for full stdin prompts. | [OpenAI Codex non-interactive mode](https://developers.openai.com/codex/noninteractive) | Official documentation | The Gemini -> Codex route uses `codex exec -` with read-only sandbox and no approvals. |

## Design Decisions

- **Kept in `SKILL.md`:** activation, recursion guard, context packet requirements, peer route, constraint preservation, skill re-evaluation.
- **Kept in references:** exact CLI command patterns, source rationale, test prompts.
- **Excluded:** multi-peer parallel critique, benchmark scoring, and repeated prompt optimization loops because they add latency and scope beyond the user's requested preflight.
- **Degree-of-freedom rule:** improved prompts should clarify goals, constraints, and evaluation criteria without prematurely fixing a single method or conclusion. This comes from the user's durable preference and from the brittleness noted in prompt-optimization evidence.
- **Rejected as defaults:** emotional pressure, roleplay personas, mandatory verbose chain-of-thought, broad many-shot examples, and multi-round automatic prompt search. They are either generic, brittle, costly, privacy-sensitive, or too task-dependent for an always-on preflight skill.

## Activation Notes

- Should trigger for almost any new user task prompt: coding, research, planning, writing, operations, debugging, review, skill creation, or tool use.
- Should not trigger for pure acknowledgments, "stop", "pause", simple status checks, or prompts already marked `[PROMPT_REFINEMENT_DONE]`.
- Risky ambiguity: very small tasks such as "date", "pwd", or "yes" may not justify peer latency even though they are prompts. Treat them as non-substantive.
