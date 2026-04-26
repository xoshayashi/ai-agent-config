---
name: skill-design-research
description: Use when creating or materially updating a skill, agent, prompt, orchestration workflow, reusable workflow, or instruction module and the design needs a strong evidence base from research papers, academic surveys, benchmarks, technical reports, official references, or credible domain literature. Helps turn sources into concise, practical skill instructions without bloating SKILL.md.
---

# Skill Design Research

Use this skill to give non-trivial skills, agents, prompts, and reusable workflows a strong research backbone while keeping the final instructions lean.

## Use When

- A new skill, agent, prompt, or reusable workflow needs more than common-sense instructions.
- Design choices depend on a domain standard, fragile workflow, evaluation method, or current research.
- The user asks for a skill or agent to be academically grounded, research-backed, or built from best practices.

Do not use this for tiny wording edits or behavior capable agents already handle well by default.

## Workflow

1. **Frame the design question.** Identify the intended user, job, triggering situations, expected outputs, failure modes, and non-obvious design choices that need evidence.
2. **Build an evidence plan.** Prefer recent academic surveys, peer-reviewed papers, credible preprints, benchmarks, technical reports, official references, domain standards, and high-quality practitioner evidence when academic evidence is thin.
3. **Classify source strength.** Label evidence as peer-reviewed finding, academic survey, preprint, benchmark, technical report, official reference, domain standard, vendor claim, practitioner report, or informed assumption.
4. **Translate evidence into behavior.** Convert sources into actionable design rules, evaluation checks, workflows, templates, or reference material. Do not summarize papers for their own sake.
5. **Keep the skill lean.** Put only the trigger, core workflow, essential decision rules, and reference-routing guidance in `SKILL.md`. Move detailed literature notes, citation lists, examples, and domain background into `references/`.
6. **Self-review the design.** Check that every non-obvious rule has a source or explicit rationale, the skill is not duplicating default agent behavior, and the resulting workflow is practical under real context limits.

## Source Quality Guide

Use [references/source-quality.md](references/source-quality.md) when the task needs deeper guidance on source hierarchy, search patterns, evidence labels, or where to store literature notes.

## Output Pattern

When reporting or editing a skill, include:

- **Design basis:** the few evidence-backed principles that shaped the skill.
- **Source labels:** which claims are peer-reviewed, preprint, benchmark, official, vendor, practitioner, or assumption.
- **Skill impact:** what changed in the workflow, trigger, checks, references, or assets because of the evidence.
- **Context control:** what stayed out of `SKILL.md` and moved to `references/` to avoid bloat.
