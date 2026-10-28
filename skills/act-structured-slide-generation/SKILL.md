---
name: act-structured-slide-generation
description: "Generates and repairs native, editable 16:9 .pptx decks from a prompt: banker-grade structured slides in the Act design language, composed by judgment over audience, claim, evidence, narrative role, grid/flex layout, design richness, and production constraints rather than slide-type templates. Use whenever the user asks for a deck, slides, presentation, or page-based business material, including Japanese terms such as 資料, 決算説明資料, IR資料, 提案書, 営業資料, 会社説明資料, 経営会議資料, 登壇資料, ピッチ資料, 事業計画資料, board deck, investor deck, or editable .pptx. Also critiques or redesigns an existing deck at design, structure, and claim level. Not for AI-image slides, ATOM-brand slides, narrative-only equity stories, proofreading-only edits, Google Slides-only work, or xlsx financial models."
compatibility: "Needs Python 3 with python-pptx, Pillow, lxml, fonttools, vl-convert-python and graphviz; the Graphviz dot CLI and LibreOffice (soffice) plus pdftoppm for diagrams and render QA; the Geist and Noto Sans JP fonts (scripts/setup_fonts.py). Built for Claude Code and Codex; see references/setup.md."
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

**Two rendering tracks, native first.** Every object routes to the most editable representation
it can faithfully take (`render_route`). The native python-pptx track (text, tables, native
charts, autoshapes) is the default and stays editable in PowerPoint. When an object genuinely
exceeds native — a combo/dual-axis chart, an area/radar chart, an org tree, a ring/funnel/
pyramid/Venn/matrix — it escalates to the image-asset track (Vega-Lite via `act_vega.py` for
every chart and schematic, Graphviz for relationship graphs, both through `act_assets.py` and one
shared token core in `act_theme.py`), embedded as an Act-styled picture with an audit sidecar.
Vega charts take their axes, gridlines, label sizes, legend, bar gaps, line weights and fonts from
the same tokens as native charts, so the two read as one deck. The waterfall is always a native
chart object. Escalate only the single hard object; keep the rest of the slide native.

**Design template ≠ layout template.** The rule above forbids picking a *per-slide layout* from
a type label. It does not forbid a *deck-level design template* — the calm-teal, formal-navy,
austere-ink, or bold-keynote look the whole deck wears, chosen once and applied to every slide.
That is the Google-Slides "theme", and it is a real, selectable choice (`meta.template`). A
template only re-parametrises the design tokens (colour role assignment, type scale, margins,
chart palette); it never touches the line-box model, fonts, or per-slide judgment. Choose the
template with the reader in mind (§1), then compose each slide by judgment (the chain above)
inside it. See `references/templates.md`.

## Required Workflow

Copy this checklist into your reply and tick it off as you go. Every gate is a command that
exits non-zero on a defect: when one fails, fix `deck.json` and rerun from that gate, never
patch the rendered file.

```
Deck progress:
- [ ] 0. Toolchain check passes (python3 -c ... && setup_fonts.py --check)
- [ ] 1. outline.md written; template chosen; high-risk inputs asked
- [ ] 2. deck.json authored (thesis, derivations, header contract, speaker_notes)
- [ ] 3. validate_spec → audit_argument → build_deck → verify_deck → render_deck → lint_render all exit 0
- [ ] 4. Contact sheet and every slide read; defects repaired in deck.json, then step 3 rerun
- [ ] 5. eval_deck.py ≥ 95 with an independent judge
- [ ] 6. Final report: files, checks run, remaining risks
```

### 0. Environment

Run from this skill directory. Check the toolchain before anything else, and install only what
this reports missing (`references/setup.md` has the commands and the font notes):

```bash
python3 -c "import pptx, PIL, lxml, fontTools, graphviz, vl_convert" && \
  command -v soffice dot >/dev/null && echo "ready"
python3 scripts/setup_fonts.py --check
```

### 1. Requirements And Outline

1. Confirm audience, desired action, talk time, page count, source files, mandatory topics,
   forbidden topics, brand constraints, and whether the deliverable must be editable .pptx.
1b. **Choose the design template.** Offer the basic looks and let the reader's context decide:
   `standard` (calm teal, general), `navy` (formal, board/IR), `monochrome` (austere ink, one
   accent), `bold` (keynote scale, pitch). List them from the registry, don't hard-code:
   `python3 scripts/build_deck.py --templates`. When unsure which fits, render the outline's
   cover + one evidence slide under two candidates and let the user pick. Record the choice in
   `outline.md` and set it as `meta.template` (§2); every slide then wears it. See
   `references/templates.md`.
2. Read all provided source material before drafting. Record provenance in `outline.md`.
3. Write `outline.md` (starter: `assets/outline.md`) with audience/action, governing thought, chapter spine, action-title
   sequence, evidence status, open questions, and talk-time budget. For every chapter, name
   the one concrete scene it must put in the reader's head (who is standing where, what they
   do next, what changes) — the chapter's slides are then judged by whether that scene comes
   through (`references/concreteness.md`).
4. Stop and ask for missing high-risk inputs when a claim would otherwise require invented
   numbers, fake sources, or unsupported company facts.
5. Run the outline read-through before building:

```bash
python3 scripts/validate_spec.py deck.json --outline
```

### 2. Author `deck.json`

Set `meta.template` to the look chosen in §1b (omit it for `standard`). Then declare
`meta.thesis` — the sentence the deck proves and the figure that settles it — and declare a
`derivation` for every rate, multiple or share the moment you write it. A derivation forces its
inputs onto the deck: an author who wants to title a slide 「前年比42%増」 must first have a
prior-year figure to derive it from, so the evidence is planned with the claim rather than
reverse-engineered under it (`references/argument-integrity.md`).

The template is a deck-level choice, not a per-slide one: one `meta.template` wears the whole
deck. A larger type scale (`bold`) leaves less room in the one-line header, so `validate_spec`
may ask for a shorter title under it — shorten the copy, never switch the type size by hand.

Read these references before writing or substantially repairing `deck.json`:

- `references/slide-decision-engine.md`
- `references/slide-judgment-system.md`
- `references/deck-spec.md`
- `references/design-principles.md`
- `references/grid-and-flex-strategy.md`
- `references/copy-and-title-rules.md`
- `references/talk-script-and-tts.md` (when writing `speaker_notes`)
- `references/evidence-and-claim-rules.md`

For IR / earnings / evidence-heavy decks, also read
`references/composition-atoms.md` (the evidence-emphasis move→knob map) and
the capability boundary in `references/data-and-diagram-rules.md`. Prove titles with the
emphasis knobs (`emphasis_col`, `focal_category`, `segment_labels`, `annotation.badge`,
`color_negatives`, `focal`) rather than inventing bespoke layout, and re-express any slide whose
load-bearing object the renderer cannot draw.

For each content slide, record the judgment fields in WORKING NOTES (outline.md or a
blueprints file) — never inside `speaker_notes`. The CANONICAL field list lives in
`references/slide-judgment-system.md` (22 numbered fields plus annotation_policy,
rhythm_role, fill_repair, failure_mode, repair_instruction); `slide-decision-engine.md`
§3 defines the per-slide minimum vocabulary that maps into it. Do not maintain a third
list here — when in doubt, follow slide-judgment-system.md.

Write Japanese slide text in noun-ending / headline style with no sentence-final full stop.
The title must state the conclusion, not the topic.

**Concreteness.** A claim names a who, a when and a what-happens: 「点検の記録を、作業を止めずに
会話で終える」, not 「現場の効率化」. Name the mechanism (which system, which step, which handoff)
rather than the direction. Give a national number a companion at the scale a person feels
(1日あたり / 1人あたり / 1現場あたり), derived with a `derivation` so the arithmetic is checked.
`validate_spec.py` warns on an abstract noun with no actor, and on a deck whose social-scale
figures never land in a human unit. See `references/concreteness.md`.

**Header contract (hard rule).** Every slide carries BOTH a main title and a subtitle, and
each fits on exactly ONE rendered line — no `\n`, no wrapping. Overflow is a spec defect:
shorten the copy, never the type size (`validate_spec.py` errors on violations).

The contract is declared as data in `tokens.json` → `header_contract`, not hard-coded per
slide type. A `default` entry (title + subtitle, one line each) applies to every pattern, so
new patterns inherit it automatically; only patterns whose renderer genuinely differs
override it:

| Pattern | Title | Subtitle slot | Lines |
|---|---|---|---|
| (default — all patterns) | `title` | `subtitle` | 1 / 1 |
| `cover` | `title` | `subtitle` | 1 / **2** (exactly two lines joined with `\n`) |
| `section_divider` | `title` | **`desc`** (it has no header chrome) | 1 / 1 |

Per-line character limits are never written down: they are derived from the render geometry
(box width ÷ type size) by `deck_text.header_slots()`, which both the validator and the
renderer read. Changing a type scale or a layout width moves the limit automatically — do not
reintroduce hard-coded character budgets for headers.

**Copy and layout contracts (details in the references).**

- **Line breaks:** write copy; the builder writes the breaks. Display text breaks at phrase
  boundaries, body copy wraps naturally, and a `\n` you type is a forced break (use it only for
  slots with an exact line count, like the cover subtitle) — `references/copy-and-title-rules.md`.
- **Emphasis without dashes:** a clause break is a comma, an emphasis break is its own line (the
  `lead` on a statement slide); `validate_spec` flags dashes in slide-visible text.
- **Body fill and card copy:** blocks grow toward 74% of the body band; past a pattern's cap the
  renderer reclaims spacing and then *reports* overflow instead of shrinking type. Write cards to
  their size (a bold one-line lead plus about three two-line items); validate and verify name a
  card that is under 60% full. Fix copy, never type size — `references/grid-and-flex-strategy.md`.

**Choosing the primitive.** Pick by the reader question, then look up the shape:

| The page needs | Use | Reference |
|---|---|---|
| A known consulting archetype | the pattern or `composite` recipe it maps to | `consulting-page-catalogue.md` |
| A combination (chart + notes + so-what, KPI strip + table, three issue cards + bar) | `composite` with role-tagged `blocks`; the layout search picks the arrangement | `layout-search.md` |
| A specific geometry (pillars, tree, decision timeline, risk grid, hub, before/after, cases, 2x2, workplan, Harvey balls) | the dedicated pattern | `deck-spec.md` |
| A chart beyond plain column / bar / line / stacked / donut | Vega-Lite (`kind: "vega"` or `mekko` / `slope` / `dumbbell` / `bullet`); waterfalls are always native | `charts-vega.md` |

For `composite` blocks, give each block a `role` (`focal` answers the reader question;
`support`, `context`, `conclusion`) and let `scripts/layout_search.py` measure the arrangements.
Inspect the top three with `layout_search.py deck.json --slide N --top 3`, and pin a `grid` only
for a content reason — never because a layout "looks better", since models judge slide
aesthetics poorly and the geometry is measured instead. Pick a chart from the comparison the
title makes (component, item, time series, frequency, correlation, bridge, two-point change, vs
target). A `sticker` ("暫定", "例示") marks a slide's status in the top-right corner; an
illustrative sticker requires an `assumption`.

**Text frames.** A group that reads as one thing is one text box, built from paragraphs
(label -> value -> note; heading -> body; a whole interpretation rail). Leading follows the
type size (`tokens.leading`), paragraph spacing is authored as the ink gap you want to see,
and every frame is the size of its text. `verify_deck` reports overlapping frames. See
`references/grid-and-flex-strategy.md`.

Source, assumption, and note fields stay small in the footer area; page numbers are never
rendered. `note` exists only to change how a number reads (denominator, definition, scope) —
never as commentary or a navigation hint, and never on a slide that shows no number;
`validate_spec` warns on such a note. Put the remark in the body or in `speaker_notes` instead.

### 2b. Talk Script (speaker_notes)

`speaker_notes` is the presenter's spoken script and nothing else: no design metadata
(judgment fields, "reader_question", "composition", "focal"), because a presenter reads it aloud.
Write it against the final slide bodies and re-check it whenever a slide's copy changes.

- **Same argument as the slide:** every number, date and proper noun you speak is on the slide;
  touch the title claim (paraphrased, not read verbatim), the focal object, and any caveat.
- **Scene, then claim:** open on a person, a place or an action (「朝、倉庫の点呼です。ドライバーの声が少し低い。」),
  then the claim, then the evidence in the slide's reading order.
- **One story:** pick up the previous slide's bridge (no 「このスライドでは」 openings), state the
  so-what, and hand off to the next slide's question. Spoken です/ます, no bullet dumps.
- **Speakable:** open fragments a voice cannot say (arrows, tildes, `vs`, `YoY`, the accounting
  triangle) into words; never apply these readings to slide-visible text.
- **Depth:** about 150-300 Japanese characters per content slide, calibrated to
  `meta.talk_minutes` (about 300 characters per minute).

`validate_spec.py` warns on each of these. The full rules and the reading table are in
`references/talk-script-and-tts.md` and `references/tts_readings.json`.

### 3. Validate, Audit The Argument, Build, Verify, Render

All commands must pass before final delivery. `audit_argument.py` runs before the build,
because an argument defect is a defect in the spec: a rate that does not recompute, a
comparison with nothing to compare against, a source no one could request, or a closing line
that proves itself is fixed in `deck.json`, never in the render. It has no waiver flag — see
`references/argument-integrity.md`.

```bash
python3 scripts/validate_spec.py deck.json
python3 scripts/audit_argument.py deck.json
python3 scripts/build_deck.py deck.json -o deck.pptx
python3 scripts/verify_deck.py deck.pptx
sh scripts/render_deck.sh deck.pptx render/
python3 scripts/lint_render.py render/ --spec deck.json
```

`verify_deck.py` warns when display text could not be broken at a phrase boundary and fell
back to the renderer's own wrap (which splits words). Treat every such warning as a copy
defect on that slide: shorten the line or widen its column — do not shrink the type, and do
not hand-insert a `\n`.

Use `--baseline` after the first render so regression checks focus on intended changes:

```bash
python3 scripts/lint_render.py render-v2/ --spec deck.json --baseline render/
```

### 4. Visual Review

Never finish on machine checks alone. Review the contact sheet, header strip, and individual
rendered PNGs. Inspect at least these issues:

- unreadable small text, especially body copy and numeric labels
- a missing subtitle, or a title/subtitle that wrapped to a second line (cover subtitle:
  anything other than exactly two lines)
- a line broken mid-word, mid-okurigana, between a number and its unit, or a particle /
  symbol left at the head of a line (the break must fall at a 文節 boundary)
- a stacked card (label -> value -> note) whose gap under the value differs from the gap
  above it — the stack is spaced by ink, so unequal gaps mean the model or the copy is off
- metric delta / YoY text glued to the value line
- excessive whitespace, low information density, or cramped clusters
- objects not aligned to the declared grid/flex contract
- a lone bar pretending to be a chart when no comparison is possible
- arrow outcomes or bold labels too small or not centered in their target field
- fixed-looking statement slides, especially left-heavy text blocks or redundant company/date
  metadata
- page numbers
- placeholder sources, unsupported assumptions, or invented facts

Work through the seven lenses in `references/visual-qa-and-repair-rubric.md` and pick each
fix from its repair menu (R1-R14). Record findings in `review-log.md`. Repair in this order:

`P0 unreadable/overlap/factual contradiction -> P1 grid, evidence, source, and hierarchy defects -> P2 polish`

Return to the outline when the defect is structural, not visual: wrong governing thought,
missing evidence, conflicting chapters, or a title sequence that no longer reads through.

### 5. Independent Rubric Loop

After self-repair, use an independent reviewer from the other CLI to score the rendered PNGs
with `evals/rubric.json`. Iterate until the deck scores at least 95.

```bash
python3 scripts/eval_deck.py render/ --judge codex --anchor "<slide-1 title phrase>"
python3 scripts/eval_deck.py render/ --judge claude --anchor "<slide-1 title phrase>"
```

The rubric loads automatically from `evals/rubric.json`; there is no `--rubric` flag.
`--anchor` takes a phrase from slide 1's title so the judge's readback proves it scored
the right images.

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
| `references/slide-decision-engine.md` | End-to-end decision flow from sources to repair |
| `references/slide-judgment-system.md` | Per-slide judgment fields and anti-template audit |
| `references/deck-spec.md` | `deck.json` schema, pattern fields, chart spec, copy rules |
| `references/templates.md` | Deck-level design templates (`meta.template`): the selectable looks and their bounds |
| `references/templates/*.json` | The template patches themselves (`standard`, `navy`, `monochrome`, `bold`) |
| `references/design-principles.md` | Act visual grammar, hierarchy, color, density judgment, and page rhythm |
| `references/grid-and-flex-strategy.md` | Granular grid/flex contract for layout consistency |
| `references/composition-vocabulary.md` | Composition moves, not templates |
| `references/charts-vega.md` | Vega-Lite charts and consulting recipes (mekko / slope / dumbbell / bullet), chart choice by comparison, checks |
| `references/layout-search.md` | Why and how `composite` blocks are arranged by search: roles, candidate grammar, verifiable scores, research sources |
| `references/consulting-page-catalogue.md` | Strategy-firm page archetypes → dedicated pattern or `composite` recipe |
| `references/composition-atoms.md` | IR-slide composition atoms + evidence-emphasis move→knob map |
| `references/ir-slide-design-principles.md` | IR and investor-deck design principles |
| `references/evidence-and-claim-rules.md` | Claim/evidence/status/source discipline |
| `references/data-and-diagram-rules.md` | Chart and diagram selection rules |
| `references/copy-and-title-rules.md` | Action titles, Japanese slide copy, line-break discipline |
| `references/argument-integrity.md` | The argument contract enforced by `audit_argument.py` |
| `references/concreteness.md` | Scenes, named mechanisms, felt scale (lexicon: `concreteness-lexicon.json`) |
| `references/commitment-lexicon.json` | Terms that decide promise / rank / hedge / motion |
| `references/setup.md` | Toolchain check, fonts, and install commands |
| `references/talk-script-and-tts.md` | Speaker-notes readings a voice can say (table: `tts_readings.json`) |
| `references/humanize.md` | Remove AI-like generic output |
| `references/anti-patterns.md` | Failure modes to hunt before delivery |
| `references/visual-qa-and-repair-rubric.md` | Render-based review loop: seven lenses, P0/P1/P2 severity, repair menu R1-R14, approve / repair / redesign verdict |
| `references/pptx-pitfalls.md` | python-pptx implementation pitfalls |
| `references/tokens.json` | Single source for Act color, type, and grid tokens |
| `scripts/act_theme.py` | Token-core adapter: feeds tokens.json to every backend (native, Vega-Lite, Graphviz) |
| `scripts/act_assets.py` | Image-asset backend: Act-styled deterministic charts/diagrams for objects native cannot draw |
| `scripts/act_vega.py` | Vega-Lite chart rendering: Act theme, `focal` / `labels`, consulting recipes, compile check |
| `scripts/layout_search.py` | Ranks `composite` arrangements from role-tagged `blocks`; `--top`, `--emit` to compare candidates |
| `scripts/stress_deck.py` | Dynamic-generation regression guard: every pattern at min / documented max / past capacity |
| `scripts/setup_fonts.py` | Installs / checks the Geist + Noto Sans JP static fonts the renderer measures with |
| `scripts/deck_text.py`, `scripts/deck_argument.py` | Shared modules: text measurement, header slots, template registry; evidence-vs-claim key split (used by validate, build, audit, contact sheet) |
| `scripts/contact_sheet.py` | Contact sheet and header strip from rendered PNGs (called by `render_deck.sh`) |
| `evals/rubric.json`, `evals/evals.json`, `evals/scenario-earnings.md` | Deck-scoring rubric read by `eval_deck.py`; skill eval cases; clean-base earnings scenario |
| `evals/skill-rubric.json` | Rubric for reviewing the skill itself (hand it to the milestone-review reviewer) |
| `examples/sample-deck.json`, `sample-earnings-deck.json`, `sample-consulting-deck.json` | Canonical decks: proposal, earnings, consulting (pillars / metric proof / logic tree / mix shift) |
| `assets/outline.md`, `assets/review-log.md` | Optional starters for the workspace `outline.md` and `review-log.md` |

## Skill Maintenance

Use:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -p no:cacheprovider
python3 scripts/stress_deck.py -o /tmp/stress --images     # every pattern at min / max / overload, all templates via --template
python3 ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py .
agentskills validate "$PWD"   # Agent Skills spec validator (pip install --user skills-ref); pass the path, not "."
```

After touching a renderer, rebuild and render the three example decks and read the contact
sheets — the stress fixture proves nothing breaks, the examples prove it still looks right.

For an independent review of the skill itself, give the reviewer `evals/skill-rubric.json`
(via the milestone-review skill) and record the outcome in the task's progress log, not in
this directory — the skill tree carries only what a run needs.

Remove caches after local testing if they appear:

```bash
trash .pytest_cache tests/__pycache__ scripts/__pycache__
```
