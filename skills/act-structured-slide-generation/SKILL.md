---
name: act-structured-slide-generation
description: "Generate and repair native, editable 16:9 .pptx decks from a prompt: banker-grade structured slides in the Act design language, composed by judgment over audience, claim, evidence, narrative role, grid/flex layout, design richness, and production constraints rather than slide-type templates. Use whenever the user asks for a deck, slides, presentation, or page-based business material, including Japanese terms such as 資料, 決算説明資料, IR資料, 提案書, 営業資料, 会社説明資料, 経営会議資料, 登壇資料, ピッチ資料, 事業計画資料, board deck, investor deck, or editable .pptx. Also use to critique or redesign an existing deck at design, structure, and claim level. Not for AI-image slides, ATOM-brand slides, narrative-only equity stories, proofreading-only edits, Google Slides-only work, or xlsx financial models."
---

# Act Structured Slide Generation

Build native, editable 16:9 PowerPoint decks in the Act design language. The target is a
banker-grade / strategy-consulting base: action titles, one claim per page, aligned evidence,
explicit sources, calm color, and a disciplined grid. Add modern freshness only through
composition, scale contrast, hierarchy, density control, and page rhythm.

Slide-visible copy and generated deck content are Japanese by default. This operating manual
is English so the skill guidance is clear, compact, and maintainable.

## Core Rule: Judgment, Not Templates

Never select a layout because a slide has a familiar type label. Decide through this chain:

`source understanding -> reader_question -> single_takeaway -> focal_object -> evidence_strategy -> composition_move -> density_control -> grid/flex contract -> QA -> repair`

For every content slide, propose two or three materially different visual directions before
choosing one. Repeated cards, equal grids, standard two-column pages, large empty fields,
decorative arrows, or a fixed closing page are failures unless the slide's evidence and
reader question specifically require them.

The code provides safe primitives, not a design template. The prompt and references must
drive flexible composition. If the renderer's default shape produces a rigid or low-density
page, change the spec, choose a different pattern, or extend the primitive.

## Required Workflow

### 0. Environment

Run from this skill directory unless an output path is explicit:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
```

If PowerPoint rendering is needed on macOS and LibreOffice is missing:

```bash
brew install --cask libreoffice
```

### 1. Requirements And Outline

1. Confirm audience, desired action, talk time, page count, source files, mandatory topics,
   forbidden topics, brand constraints, and whether the deliverable must be editable .pptx.
2. Read all provided source material before drafting. Record provenance in `outline.md`.
3. Write `outline.md` with audience/action, governing thought, chapter spine, action-title
   sequence, evidence status, open questions, and talk-time budget.
4. Stop and ask for missing high-risk inputs when a claim would otherwise require invented
   numbers, fake sources, or unsupported company facts.
5. Run the outline read-through before building:

```bash
python3 build/scripts/validate_spec.py deck.json --outline
```

### 2. Author `deck.json`

Read these references before writing or substantially repairing `deck.json`:

- `build/references/slide-decision-engine.md`
- `build/references/slide-judgment-system.md`
- `build/references/deck-spec.md`
- `build/references/design-principles.md`
- `build/references/grid-and-flex-strategy.md`
- `build/references/copy-and-title-rules.md`
- `build/references/evidence-and-claim-rules.md`

For each content slide, fill the judgment fields in speaker notes or working notes:

- reader question
- single takeaway
- focal object
- evidence strategy
- composition move
- density control
- grid role map
- column span plan
- alignment spine
- body band plan
- edge lock
- flex main axis
- cross-axis alignment
- gap scale
- grow/shrink/wrap behavior
- fill repair
- failure mode
- repair instruction

Write Japanese slide text in noun-ending / headline style with no sentence-final full stop.
The title must state the conclusion, not the topic. Source, assumption, and note fields stay
small in the footer area; page numbers are never rendered.

### 3. Validate, Build, Verify, Render

All commands must pass before final delivery:

```bash
python3 build/scripts/validate_spec.py deck.json
python3 build/scripts/build_deck.py deck.json -o deck.pptx
python3 build/scripts/verify_deck.py deck.pptx
sh build/scripts/render_deck.sh deck.pptx render/
python3 build/scripts/lint_render.py render/ --spec deck.json
```

Use `--baseline` after the first render so regression checks focus on intended changes:

```bash
python3 build/scripts/lint_render.py render-v2/ --spec deck.json --baseline render/
```

### 4. Visual Review

Never finish on machine checks alone. Review the contact sheet, header strip, and individual
rendered PNGs. Inspect at least these issues:

- unreadable small text, especially body copy and numeric labels
- metric delta / YoY text glued to the value line
- excessive whitespace, low information density, or cramped clusters
- objects not aligned to the declared grid/flex contract
- a lone bar pretending to be a chart when no comparison is possible
- arrow outcomes or bold labels too small or not centered in their target field
- fixed-looking statement slides, especially left-heavy text blocks or redundant company/date
  metadata
- page numbers
- placeholder sources, unsupported assumptions, or invented facts

Record findings in `review-log.md`. Repair in this order:

`P0 unreadable/overlap/factual contradiction -> P1 grid, evidence, source, and hierarchy defects -> P2 polish`

Return to the outline when the defect is structural, not visual: wrong governing thought,
missing evidence, conflicting chapters, or a title sequence that no longer reads through.

### 5. Independent Rubric Loop

After self-repair, use an independent reviewer from the other CLI to score the rendered PNGs
with `build/evals/rubric.json`. Iterate until the deck scores at least 95.

```bash
python3 build/scripts/eval_deck.py render/ --rubric build/evals/rubric.json --judge codex --anchor deck.json
python3 build/scripts/eval_deck.py render/ --rubric build/evals/rubric.json --judge claude --anchor deck.json
```

Use `--judge codex` when the host is Claude Code. Use `--judge claude` when the host is Codex.
Every reported defect must be rechecked against the actual render before editing; judges can
hallucinate. Keep iterating until the visual output, not just the JSON, is acceptable.

### 6. Final Report

Leave these artifacts in the requested output directory:

- `outline.md`
- `deck.json`
- `deck.pptx`
- rendered slide PNGs and share PDF under `render/`
- `review-log.md`
- rubric score or reviewer output when available

Final response: give the file paths, the validation commands that passed, the rubric score,
and any known residual risk.

## Non-Negotiable Prohibitions

- Do not invent company facts, market sizes, sources, or dates. Mark missing evidence as open.
- Do not use slide-type templates as the design decision. Pattern names are implementation
  primitives only.
- Do not create page numbers.
- Do not create a fixed closing slide. Choose the closing role from the deck's story: thesis,
  evidence strip, decision request, next actions, legal close, or quote. Omit company/date
  metadata unless legally required.
- Do not allow small typography to carry important information. Footer text may be small;
  body evidence must be readable from the back row.
- Do not glue YoY, delta, or comparison text to the value line. Treat it as a separate metric
  subline with visible air.
- Do not use a single standalone bar as a chart. Use a hero number, gauge, range, table, or
  comparative bars instead.
- Do not let decorative freshness override auditability. Freshness comes from composition,
  not gradients, shadows, icons, or color noise.

## File Map

Read only what the task needs, but do not skip the required workflow references.

| File | Use |
|---|---|
| `build/references/slide-decision-engine.md` | End-to-end decision flow from sources to repair |
| `build/references/slide-judgment-system.md` | Per-slide judgment fields and anti-template audit |
| `build/references/deck-spec.md` | `deck.json` schema, pattern fields, chart spec, copy rules |
| `build/references/design-principles.md` | Act visual grammar and slide-level design decisions |
| `build/references/grid-and-flex-strategy.md` | Granular grid/flex contract for layout consistency |
| `build/references/composition-vocabulary.md` | Composition moves, not templates |
| `build/references/corpus-derived-composition-atoms.md` | IR-corpus atoms for evidence-led pages |
| `build/references/ir-slide-design-principles.md` | Corpus-derived IR and investor-deck principles |
| `build/references/evidence-and-claim-rules.md` | Claim/evidence/status/source discipline |
| `build/references/data-and-diagram-rules.md` | Chart and diagram selection rules |
| `build/references/visual-hierarchy-rules.md` | Reading path, emphasis, alignment, accessibility |
| `build/references/copy-and-title-rules.md` | Action titles and Japanese slide copy discipline |
| `build/references/design-richness-rules.md` | Freshness and impact without decoration |
| `build/references/humanize.md` | Remove AI-like generic output |
| `build/references/anti-patterns.md` | Failure modes to hunt before delivery |
| `build/references/all-perspective-review.md` | Twenty-lens review checklist |
| `build/references/review-and-repair-rubric.md` | Operational repair menu and scoring gate |
| `build/references/visual-qa-and-repair-rubric.md` | Render-based multi-lens visual QA |
| `build/references/pptx-pitfalls.md` | python-pptx implementation pitfalls |
| `build/references/tokens.json` | Single source for Act color, type, and grid tokens |
| `assets/deck-workspace-template/` | Optional starter for `outline.md` and `review-log.md` |

## Skill Maintenance

Use:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest build/tests -p no:cacheprovider
python3 /Users/sh/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Remove caches after local testing if they appear:

```bash
trash .pytest_cache build/tests/__pycache__
```
