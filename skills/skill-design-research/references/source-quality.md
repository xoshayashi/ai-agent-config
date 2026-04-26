# Source Quality For Skill Design

Use this reference when a skill, agent, prompt, or reusable workflow needs an evidence-backed design.

## Evidence Hierarchy

| Source Type | Use For | Caution |
|---|---|---|
| **Academic surveys / systematic reviews** | Mapping a field, finding consensus, avoiding one-paper overfitting | May lag fast-moving practice |
| **Peer-reviewed papers** | Stable findings, validated methods, accepted terminology | Check task fit and external validity |
| **Benchmarks / evaluation reports** | Comparing methods and defining measurable quality bars | Benchmark may not match the user's task |
| **Preprints** | Current frontier ideas and recent experiments | Treat as provisional unless independently supported |
| **Technical reports** | Implementation details, scaling lessons, system architecture | May omit negative results |
| **Official references** | APIs, file formats, product behavior, limits, setup | Can be incomplete on best practice |
| **Domain standards** | Compliance, safety, terminology, professional norms | May be slow or jurisdiction-specific |
| **Vendor claims** | Product capabilities and roadmap signals | Mark clearly; verify where decisions depend on it |
| **Practitioner reports** | Operational lessons and real-world friction | Treat as contextual, not universal |
| **Informed assumptions** | Filling gaps where evidence is thin | State assumptions and validation needs |

## Search Patterns

Adapt these patterns to the domain and current year. Treat them as **short query families**, not as one combined query.

- `"[topic]" survey recent`
- `"[topic]" benchmark evaluation`
- `"[topic]" systematic review`
- `"[topic]" agent workflow evaluation`
- `"[topic]" human factors study`
- `"[topic]" technical report`
- `"[topic]" best practices official documentation`
- `site:arxiv.org "[topic]" survey`
- `site:acm.org "[topic]"`
- `site:ieee.org "[topic]"`

Prefer current sources for fast-moving AI, agent, model, API, and tooling topics. Prefer standards, surveys, and official references when stability matters more than novelty.

## Query Breadth Control

Search queries should be long enough to express intent, but short enough to avoid filtering away valid results.

- **Start short:** Use the core entity/topic plus one purpose qualifier when useful, such as `survey`, `benchmark`, `official docs`, `release notes`, `pricing`, `security`, or the current year.
- **Avoid over-specified first searches:** Do not include every constraint, synonym, expected conclusion, product name, date range, and source type in the same query.
- **Split, then compare:** Use several focused queries for distinct source types or angles instead of one overloaded query.
- **Adjust based on results:** If results are too sparse or off-target, remove the weakest qualifier, replace overly specific terms with broader ones, or search a known source directly. If results are too broad, add one qualifier at a time.
- **Use exact phrases sparingly:** Quote titles, error messages, unique phrases, identifiers, or exact product names. Avoid quoting generic concepts because it can hide useful sources that use nearby terminology.
- **Keep entities intact:** Do not remove exact package names, file names, error codes, standards numbers, or paper titles when those are the thing being searched.

## Translate Evidence Into Skill Design

For each important source, extract only what changes the skill:

| Field | Meaning |
|---|---|
| **Finding** | What the source supports |
| **Design implication** | What the skill should do differently |
| **Confidence** | High / medium / low, with reason |
| **Evidence label** | Survey, peer-reviewed, preprint, benchmark, official, vendor, etc. |
| **Where it belongs** | `SKILL.md`, `references/`, `assets/`, `scripts/`, or omit |

## Keep `SKILL.md` Lean

Put content in `SKILL.md` only when it changes behavior every time the skill fires:

- Trigger conditions
- Core workflow
- Mandatory checks
- Key source-backed heuristics
- Pointers to specific reference files

Move the rest to `references/`:

- Literature summaries
- Citation lists
- Long examples
- Domain background
- Evaluation rubrics
- Source-by-source notes

Do not include paper summaries just because they were read. Include only evidence that changes a decision, workflow, evaluation criterion, or reusable artifact.
