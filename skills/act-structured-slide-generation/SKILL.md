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

**Two rendering tracks, native first.** Every object routes to the most editable representation
it can faithfully take (`render_route`). The native python-pptx track (text, tables, native
charts, autoshapes) is the default and stays editable in PowerPoint. When an object genuinely
exceeds native — a combo/dual-axis chart, an area/radar chart, an org tree, a ring/funnel/
pyramid/Venn/matrix — it escalates to the image-asset track (matplotlib / Graphviz via
`act_assets.py`, one shared token core via `act_theme.py`), embedded as an Act-styled picture
with an audit sidecar. Escalate only the single hard object; keep the rest of the slide native.

## Required Workflow

### 0. Environment

Run from this skill directory unless an output path is explicit. **Check first — the machine
may already have everything, in which case use the system `python3` and do NOT create a venv**
(a venv only adds an activation step to every command):

```bash
python3 -c "import pptx, PIL, lxml, fontTools, matplotlib, matplotlib_venn, graphviz" && \
  command -v soffice dot >/dev/null && echo "ready — no venv needed"
```

If something is missing, install it into the system Python (macOS / Homebrew):

```bash
brew install python-matplotlib          # matplotlib + numpy for the image-asset track
brew install graphviz                   # the `dot` CLI (relationship graphs)
brew install --cask libreoffice         # `soffice`, used to render .pptx → PDF/PNG
python3 -m pip install --break-system-packages python-pptx Pillow lxml fonttools \
                                        matplotlib-venn graphviz pytest
```

Homebrew's Python is PEP 668 "externally managed", so plain `pip install` is refused —
`--break-system-packages` is what lets these (pure-Python) packages land in it. Only reach
for a venv if you cannot install into the system Python:

```bash
python3 -m venv .venv && . .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
```

The image-asset deps (matplotlib, matplotlib-venn, Graphviz) are imported lazily — a
native-only deck runs without them, and they are only needed when a deck uses an image chart
`kind` or the `diagram` pattern.

### 1. Requirements And Outline

1. Confirm audience, desired action, talk time, page count, source files, mandatory topics,
   forbidden topics, brand constraints, and whether the deliverable must be editable .pptx.
2. Read all provided source material before drafting. Record provenance in `outline.md`.
3. Write `outline.md` with audience/action, governing thought, chapter spine, action-title
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

Declare `meta.thesis` first — the sentence the deck proves and the figure that settles it —
and declare a `derivation` for every rate, multiple or share the moment you write it. A
derivation forces its inputs onto the deck: an author who wants to title a slide 「前年比42%増」
must first have a prior-year figure to derive it from, so the evidence is planned with the
claim rather than reverse-engineered under it (`references/argument-integrity.md`).

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

**Line breaks.** Write copy; the builder writes the line breaks. Short display text (labels,
headings, cell text, conclusion lines) breaks at phrase boundaries so the phrasing shows in
the shape; sentences and body copy fill their lines, each line ending on a whole word. The
renderer is never left to wrap an overflowing sentence — its letter spacing differs from the
builder's by a fraction, and that fraction is what drops a break inside a word. A symbolic closing message is composed as
a form — its measure, its line balance and its surrounding whitespace are chosen together. A
`\n` you type is honoured as a forced break, which is what makes it right for a slot with an
exact line count (the cover subtitle's two lines). When a word is wider than its column,
`verify_deck` names it: shorten the word or widen the column. See
`references/copy-and-title-rules.md`.

**Emphasis without dashes.** On a slide, a clause break is a comma and an emphasis break is a
line. A point that deserves to stand alone gets its own line — on a statement slide it becomes
the `lead`, with the sentence that supports it set below in smaller type. `validate_spec`
flags dashes in slide-visible text.

**Text frames.** A group that reads as one thing is one text box, built from paragraphs
(label -> value -> note; heading -> body; a whole interpretation rail). Leading follows the
type size (`tokens.leading`), paragraph spacing is authored as the ink gap you want to see,
and every frame is the size of its text. `verify_deck` reports overlapping frames. See
`references/grid-and-flex-strategy.md`.

Source, assumption, and note fields stay small in the footer area; page numbers are never
rendered.

### 2b. Talk Script (speaker_notes)

`speaker_notes` is the presenter's spoken script and NOTHING else. Design metadata
(judgment fields, "reader_question", "composition", "focal", rhythm labels) must never
appear there — a presenter reads these notes verbatim while delivering.

**Content fidelity — the script and the slide must be the same argument.** Write scripts
against the FINAL slide bodies (after visual QA), and re-check them whenever a slide's
copy changes — stale notes that describe an older body are a defect ("script drift").
Concretely:

- Every number, date, and proper noun you speak must exist on that slide (or in its
  note/assumption). A number that appears only in the script is a hallucination risk —
  `validate_spec.py` flags unit-bearing numbers absent from the slide.
- Every load-bearing element must be touched: the title claim (paraphrased), the focal
  object, the key rows/steps/columns, the insight band, and any caveat note — speak the
  caveat in natural language ("この期間は会議時点の見込みです" 等).
- Do not read the title string verbatim as the opening; restate the claim in spoken form.

**Open on the scene, then the claim.** The presenter's first sentence puts the audience
somewhere: a person, a place, an action. 「朝、倉庫の点呼です。ドライバーの声が少し低い。」— then
the claim, then the evidence in the slide's reading order. A script that could be read over any
slide in the deck is not yet doing its job; `validate_spec.py` warns when a slide's notes carry
no scene.

**Narrative — the deck reads as ONE story, not per-slide captions.** Each script:

1. picks up from the previous slide's bridge (no reset openings like 「このスライドでは」;
   vary the openers — three slides in a row starting with 「次に」 is a template smell),
2. opens with the claim in spoken language, then walks the evidence in the slide's visual
   reading order, naming the actual labels and numbers the audience should look at,
3. states the implication (so-what) before leaving the slide,
4. ends with a bridge that hands off to the next slide's question.

Spoken register throughout: natural です/ます sentences, no noun-ending fragments, no
bullet dumps. Read the finished set aloud start-to-finish once — if any transition
jars or a slide's script could be shuffled elsewhere without anyone noticing, the
narrative is not yet doing its job.

**Readable by a voice, and by the presenter.** The script is read aloud — by a person or by
a speech engine — so a fragment a voice cannot say is a defect there, even though the same
character is right on the slide (which is read with the eyes). Open the fragments that a TTS
engine skips, spells out, or reads in English: arrows, range tildes, math and relation signs,
the accounting triangle, `&`, inline fractions, `2.4x`, `vs`, `CAGR`, `YoY`, `SaaS`, an
em-dash used as a pause. Open them into the words a presenter would actually say — the form
follows the kind of fragment (operators and relations into kana/kanji, units into
katakana/kanji, fractions reordered denominator-first, letter-wise acronyms like KPI/ARR left
as Latin, word-like ones like SaaS into katakana). Stop there: rewriting every Latin string
into katakana makes the notes unreadable for the human holding them.
`validate_spec.py` warns on each un-speakable fragment and names the reading; the table is
`references/tts_readings.json`, the reasoning `references/talk-script-and-tts.md`. Never
apply these conversions to slide-visible text.

Depth target: ~150-300 Japanese characters per content slide (≈30-60 seconds of speech);
calibrate the deck total against `meta.talk_minutes` (~300字/分). A one-line note is a
defect on any slide except the cover. `validate_spec.py` warns on metadata leakage,
thin scripts, non-spoken register, title-verbatim openings, and slide-absent numbers.

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

Record findings in `review-log.md`. Repair in this order:

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
| `references/design-principles.md` | Act visual grammar and slide-level design decisions |
| `references/grid-and-flex-strategy.md` | Granular grid/flex contract for layout consistency |
| `references/composition-vocabulary.md` | Composition moves, not templates |
| `references/composition-atoms.md` | IR-slide composition atoms + evidence-emphasis move→knob map |
| `references/ir-slide-design-principles.md` | IR and investor-deck design principles |
| `references/evidence-and-claim-rules.md` | Claim/evidence/status/source discipline |
| `references/data-and-diagram-rules.md` | Chart and diagram selection rules |
| `references/visual-hierarchy-rules.md` | Reading path, emphasis, alignment, accessibility |
| `references/copy-and-title-rules.md` | Action titles, Japanese slide copy, line-break discipline |
| `references/argument-integrity.md` | The argument contract enforced by `audit_argument.py` |
| `references/concreteness.md` | Scenes, named mechanisms, felt scale (lexicon: `concreteness-lexicon.json`) |
| `references/commitment-lexicon.json` | Terms that decide promise / rank / hedge / motion |
| `references/talk-script-and-tts.md` | Speaker-notes readings a voice can say (table: `tts_readings.json`) |
| `references/design-richness-rules.md` | Freshness and impact without decoration |
| `references/humanize.md` | Remove AI-like generic output |
| `references/anti-patterns.md` | Failure modes to hunt before delivery |
| `references/all-perspective-review.md` | Twenty-lens review checklist |
| `references/review-and-repair-rubric.md` | Operational repair menu and scoring gate |
| `references/visual-qa-and-repair-rubric.md` | Render-based multi-lens visual QA |
| `references/pptx-pitfalls.md` | python-pptx implementation pitfalls |
| `references/tokens.json` | Single source for Act color, type, and grid tokens |
| `scripts/act_theme.py` | Token-core adapter: feeds tokens.json to every backend (native, matplotlib, Graphviz) |
| `scripts/act_assets.py` | Image-asset backend: Act-styled deterministic charts/diagrams for objects native cannot draw |
| `assets/deck-workspace-template/` | Optional starter for `outline.md` and `review-log.md` |

## Skill Maintenance

Use:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -p no:cacheprovider
python3 /Users/sh/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py .
```

Remove caches after local testing if they appear:

```bash
trash .pytest_cache tests/__pycache__ scripts/__pycache__
```
