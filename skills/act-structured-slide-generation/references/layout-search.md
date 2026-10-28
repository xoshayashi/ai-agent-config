# Layout Search: Reason About Content, Measure The Geometry

`composite` can be written two ways. With `grid`, the author places every block. With
`blocks`, the author states what each block *is for* and `scripts/layout_search.py` enumerates
the arrangements, measures each with the builder's own geometry, and ranks them. The build uses
the top candidate; the CLI shows the top few with a score breakdown so the author can choose on
content grounds. This file explains why the work is split this way and how to use it.

## What The Research Says (2023-2026)

| Finding | Source | What we take |
|---|---|---|
| Sample several layouts and rank them with geometric metrics (alignment, overlap); removing the ranker worsens every task | LayoutPrompter (NeurIPS 2023) | Enumerate candidates, rank by measured scores |
| Exemplar selection is the biggest single gain (random exemplars: mIoU 0.43 → 0.25) | LayoutPrompter | A prior for known-good recipes (`consulting-page-catalogue.md`) |
| Plan in words first, then lay out: fewer constraint violations (3% → 1%) and less occlusion | Two-stage CoT for banner layout (2025) | Roles and the reader question are decided before geometry |
| VLMs judge slide aesthetics poorly (sometimes worse than chance); verifiable metrics reach F1 ≈ 0.8 for whitespace and aspect, at near-zero cost | AeSlides (2026) | Geometry is scored by code, never by "it looks fine" |
| Post-generation visual reflection gave no gain and cost +155% prompt tokens; ~70% of runs stopped after one round | AeSlides (DeepPresenter baseline) | One render pass for defects with deterministic lint, not open-ended self-critique |
| Rule-based rewards — aspect, whitespace, collision, balance, font readability — improve all five dimensions; per-slide generation is more robust than whole-deck | Building Presentation Intelligence (2026) | The metric set below; layout is solved per slide |
| Self-refinement with a rendered snapshot helps most in the first round | AutoPresent (CVPR 2025) | Render once to catch defects the metrics cannot see (wrong data, odd copy) |
| Reference slides supply functional types and content schemas | PPTAgent (EMNLP 2025) | Archetypes are mapped to blocks, not copied as templates |

The common thread: language models are strong at deciding *what matters* and weak at judging
*whether a layout looks right*. So the model reasons about content, and code measures geometry.

## The Method

1. **Reason (the author).** For the slide, write the reader question and the single takeaway
   (`slide-judgment-system.md`). Then give each block a role:
   - `focal` — the block that answers the reader question (at most one).
   - `support` — evidence or reading notes for the focal block.
   - `context` — background the reader may skip.
   - `conclusion` — the one sentence to remember (a `callout`; it goes last, full width or as
     the right-hand cell of a situation / complication / resolution row).
   Defaults: a `callout` is the conclusion; when every body block has the same type and no
   role (three issue cards) they are equal `support` peers; otherwise the first body block
   without a role is the focal one. Writing both `grid` and `blocks` is an error (the grid
   would silently win).
2. **Enumerate (code).** One-, two- and three-row grids from a small grammar: row spans such as
   12, 7/5, 8/4, 6/6, 4/4/4, 6/3/3, 3/3/3/3, every ordering of the body blocks, and row-height
   weights. Peer blocks (same type and role) keep the author's order, so three issue cards are
   not permuted into duplicates. Measured: 90 candidates / 0.02s for chart + notes + conclusion,
   254 / 0.04s for four peer cards + conclusion, about 6,000 / 0.23s for four distinct blocks +
   conclusion. The result is cached per process, so validate and build each search once.
3. **Measure (code).** Each candidate goes through `_composite_layout` and `block_need_h`, the
   same functions that draw the slide. Candidates that overflow the body, give a chart fewer
   than 4 columns, or give a table less than about 1in per column are dropped. The rest are scored.
4. **Choose (the author).** The build takes the top candidate. Run
   `python3 scripts/layout_search.py deck.json --slide N --top 3` to see the alternatives, and
   `--emit cands.json` to build them side by side. Pick a lower-ranked candidate only for a
   *content* reason ("the reader must see the table before the chart"), then pin it by writing
   its `grid`. Do not override the ranking because one layout "looks better": that is exactly the
   judgment the research says models get wrong.
5. **Verify (code).** Validate, build, verify and lint as usual. Render once and check for what
   no metric sees: wrong numbers, unreadable copy, a chart that does not prove the title.

## Scores

All parts are in [0, 1]; the total is a fixed weighted sum (no learning, deterministic ties).

| Part | Weight | Measures |
|---|---|---|
| `hierarchy` | 0.18 | The focal block is the largest body block (1.2x the next = full marks). A focal KPI or callout instead needs the top row |
| `fill` | 0.14 | Text and KPI blocks are not stretched into hollow cells beside a tall chart |
| `legible` | 0.14 | Text columns hold at least about 13 characters per line; callouts are not squeezed |
| `reading` | 0.12 | The focal block is read first (top, then left); the conclusion is read last |
| `consistency` | 0.12 | Blocks of the same type and role (peer cards, twin charts) get the same size |
| `balance` | 0.09 | Content-weighted centroid near the centre (horizontal offset weighs more), as in AeSlides |
| `shape` | 0.09 | Charts stay landscape (width/height 1.2-2.6) |
| `used` | 0.06 | Share of the body band used (no stranded space) |
| `catalogue` | 0.04 | The grid matches a known-good recipe |
| `simplicity` | 0.02 | Fewer rows and cells |

Overflow is a hard filter, not a score. When no candidate fits, validate errors and the build
draws an equal-span fallback with a warning, so the overflow is named instead of hidden.

## Limits

- Up to four body blocks and one conclusion. A denser page is two slides, or a hand-written
  `grid`.
- The metrics measure geometry from block sizes, not rendered pixels. The render-and-lint pass in
  the workflow still catches pixel-level defects.
- The weights are a design judgment, documented here and fixed in code. Change them only with a
  test that shows which known-good composition moves up or down.

## Sources

- LayoutPrompter: Awaken the Design Ability of Large Language Models — NeurIPS 2023 — arXiv 2311.06495
- Content-Aware Ad Banner Layout Generation with Two-Stage Chain-of-Thought in VLMs — arXiv 2512.12596
- AeSlides: Incentivizing Aesthetic Layout in LLM-Based Slide Generation via Verifiable Rewards — arXiv 2604.22840
- Building Presentation Intelligence for High-Quality Slide Generation — arXiv 2610.30888
- AutoPresent: Designing Structured Visuals from Scratch — CVPR 2025 — arXiv 2501.00912
- PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides — EMNLP 2025 — arXiv 2501.03936
