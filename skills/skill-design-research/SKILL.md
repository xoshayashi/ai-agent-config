---
name: skill-design-research
description: Use this skill when creating, updating, reviewing, or debugging activation for skills, agents, prompts, instruction modules, orchestration/delegation workflows, slash commands, or reusable AI workflows where design quality matters. Use it to ground non-obvious choices in research, official references, benchmarks, or credible domain literature; set trigger and metadata conditions so the workflow actually activates; and keep SKILL.md lean by moving detailed evidence to references.
---

# Skill Design Research

Use this skill to give non-trivial skills, agents, prompts, and reusable workflows a strong research backbone while keeping the final instructions lean.

## Use When

- A new skill, agent, prompt, or reusable workflow needs more than common-sense instructions.
- You are reviewing or troubleshooting whether a skill, agent, command, or reusable workflow will activate for realistic user requests.
- You are defining trigger descriptions, aliases, default prompts, routing metadata, slash-command behavior, should-trigger examples, or should-not-trigger boundaries.
- Design choices depend on a domain standard, fragile workflow, evaluation method, or current research.
- The user asks for a skill or agent to be academically grounded, research-backed, or built from best practices.

Do not use this for tiny wording edits or behavior capable agents already handle well by default.

## Workflow

1. **Frame the design question.** Identify the intended user, job, triggering situations, expected outputs, failure modes, and non-obvious design choices that need evidence.
2. **Design the activation surface.** Write or revise the `description` and any UI/routing metadata so the skill triggers on user intent, not only on internal implementation terms. Include realistic should-trigger and should-not-trigger examples when activation risk matters.
3. **Build an evidence plan.** Prefer recent academic surveys, peer-reviewed papers, credible preprints, benchmarks, technical reports, official references, domain standards, and high-quality practitioner evidence when academic evidence is thin.
4. **Search with bounded query breadth.** Use concise, high-signal Web Search queries that are likely to return a useful result set. Do not pack the whole research question, all constraints, and every synonym into one query; split the work into several shorter query families and adjust after seeing result quality.
5. **Classify source strength.** Label evidence as peer-reviewed finding, academic survey, preprint, benchmark, technical report, official reference, domain standard, vendor claim, practitioner report, or informed assumption.
6. **Translate evidence into behavior.** Convert sources into actionable design rules, evaluation checks, workflows, templates, or reference material. Do not summarize papers for their own sake.
7. **Keep the skill lean.** Put only the trigger, core workflow, essential decision rules, and reference-routing guidance in `SKILL.md`. Move detailed literature notes, citation lists, examples, and domain background into `references/`.
8. **Self-review the design.** Check that every non-obvious rule has a source or explicit rationale, the activation metadata fits realistic prompts, the skill is not duplicating default agent behavior, and the workflow is practical under real context limits.

## Source Quality Guide

Use [references/research-foundations.md](references/research-foundations.md) when designing skills or agents for LLM agents, prompt workflows, delegation, self-review, tool use, or evaluation.

Use [references/activation-examples.md](references/activation-examples.md) when tuning or reviewing this skill's own trigger description.

Use [references/source-quality.md](references/source-quality.md) when the task needs deeper guidance on source hierarchy, search patterns, evidence labels, or where to store literature notes.

## Output Pattern

When reporting or editing a skill, include:

- **Design basis:** the few evidence-backed principles that shaped the skill.
- **Source labels:** which claims are peer-reviewed, preprint, benchmark, official, vendor, practitioner, or assumption.
- **Activation fit:** the metadata, trigger phrases, and should-not-trigger boundary that make the workflow discoverable without making it over-broad.
- **Skill impact:** what changed in the workflow, trigger, checks, references, or assets because of the evidence.
- **Context control:** what stayed out of `SKILL.md` and moved to `references/` to avoid bloat.
