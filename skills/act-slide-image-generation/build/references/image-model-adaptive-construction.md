# Image-Model-Adaptive Slide Construction

Use this process to translate strategy content into a slide composition that GPT Image 2 can render and revise reliably. Keep the full analytical specification for validation, then compile it into a concise visible-state prompt for image generation.

## Operating Model

GPT Image 2 follows natural-language instructions, renders multilingual text, accepts image references, and supports generation and editing. OpenAI also documents remaining variance in exact text placement, fine layout control, and cross-generation consistency. Design the workflow around those strengths and variances:

- resolve meaning and structure before image generation
- express complex layouts as named regions and repeated equal modules
- bind each short visible string to one component and one placement
- generate and validate one slide at a time
- route structural variance to zero-base regeneration and isolated local variance to a focused edit

## Seven Gates

### G0 — Content contract

Freeze one governing thought, one audience decision, one reading path, and one evidence state. Create `content_atom_registry`; each atom includes `id`, `exact_text`, `semantic_role`, `evidence_state`, `priority`, `component_id`, `anchor_line`, `baseline_step`, `max_lines`, and `expected_occurrences: 1`. The anchor and baseline bind every visible string to compact region-relative geometry without creating a separate decorative box.

Compile provenance as one `footer_master` atom. Include a `Source: ` entry only when `source_plan` registers a genuine traceable external publication. Add at most one `Assumption: ` and one `Note: ` annotation, in that order, and retain detailed internal material in notes or the source ledger. The combined atom uses the canonical centered footer baseline for its one- or two-line budget.

Register message boxes separately from icon-bearing modules. Compile each as one text atom with zero icon children and the canonical one-line master: 17pt text, 25px line metric, 24px horizontal/vertical padding, and 73px total height on the 1672x941 basis.

### G1 — Copy capacity

Measure every visible string before layout. Apply the header budgets from `core-layout-and-typography.md`. Body module headings use one short line; support copy uses up to two readable lines. Keep the full slide at 18 or fewer visible string atoms as the first-pass production heuristic. Select rewrite, merge, or split until each text component fits its declared width at the deck-wide type scale.

Record `copy_capacity_status: approved`, total visible-string count, total Japanese full-width-equivalent count, maximum lines per component, and `microtext_component_count: 0`. This numerical budget is a production heuristic derived from the model's documented text/layout variance, not an OpenAI product limit.

### G2 — Topology and complexity

Freeze one primary topology and one visual anchor. Use 2-4 major regions, hierarchy depth 2-3, and 2-5 repeated modules in a peer group when repetition is part of the message. Give the reading path 3-6 named steps. Keep one emphasis system.

Record `model_fit_plan` with `governing_thought_count: 1`, `primary_topology_count: 1`, `visual_anchor_count: 1`, major-region count, hierarchy depth, repeated-module maximum, reading-path step count, visible-string count, reference-image count, generation batch size, and feasibility status. Select `rewrite`, `merge`, or `split` until `render_feasibility: approved`.

### G3 — Full geometry validation

Create and validate the complete 1672x941-basis layout plan: header furniture, Grid/Flex tree, component geometry, body structural rules, connectors, rigidity, occupancy, quiet region, and footer mode. This plan is the audit source of truth. It may contain precise values that support validation without appearing verbatim in the image prompt.

### G4 — Render-prompt compilation

Compile the validated plan into a concise 2048x1152 visible-state contract. Convert only the shell, header, 2-4 major region bounds, repeated-module relationships, one emphasis region, and connector path to the output basis. Keep validation metadata, scores, grow/shrink arithmetic, and unused coordinates in the plan manifest.

Use eight short labeled blocks:

1. `DELIVERABLE` — audience and use
2. `MESSAGE` — one governing thought
3. `CANVAS` — output basis and header/body/footer bands
4. `LAYOUT MAP` — named major regions, spans, shared edges, and reading path
5. `EXACT COPY` — quoted atoms, each once, with role and region
6. `VISUAL SYSTEM` — type roles, palette, rules, fills, and icon language
7. `PRESERVATION STATE` — approved edge furniture, shared geometry, and reference roles
8. `ACCEPTANCE` — exact text, grid, occupancy, padding, and balance checks

Use explicit spatial language such as left, right, top, bottom, equal width, shared baseline, and orthogonal path. Keep each instruction single-purpose and state each visible invariant once.

### G5 — One-slide render and PNG audit

Generate one slide per call. Use low quality only for a deliberate structural exploration; use high quality for Japanese text, dense exhibits, and final masters. Keep 2048x1152 as the standard 16:9 output.

Inspect the completed PNG at full size and thumbnail size. Compare OCR/visual text, occurrence count, line count, component bounds, outer-band inventory, shared axes, peer dimensions, rule endpoints, connector route, occupancy, and optical balance with the plan and exact-copy ledger. When the runtime exposes `revised_prompt`, save it in the render manifest and compare its exact-copy and layout invariants with the frozen contract.

### G6 — Repair routing

Choose one route from measured variance:

- semantic, text-system, topology, silhouette, reading-path, occupancy, or multi-region grid variance → regenerate from the frozen specification
- one isolated text, color, icon, or local-spacing variance → focused image edit naming one region and one change category
- two focused edit attempts on the same slide → regenerate from the frozen specification

Every focused edit restates the approved header, exact-copy ledger, grid skeleton, outer-band furniture, and reference roles. Keep the change set and preservation set in the render manifest.

## Required Manifests

Keep these compact artifacts for each approved slide:

- `slide_spec`: governing thought, content atoms, exact-copy ledger, evidence state
- `layout_plan`: complete validation geometry and model-fit plan
- `render_prompt_manifest`: compiled prompt version, exact-copy hash, visible component IDs, footer mode, reference roles, generation route, and revised prompt when exposed
- `png_audit`: measured text, geometry, rigidity, occupancy, furniture, and repair route

## Research Basis

- [OpenAI Image Generation guide](https://developers.openai.com/api/docs/guides/image-generation): generation/editing, sizes, quality, image inputs, revised prompts, and documented limitations.
- [OpenAI GPT Image 2 model](https://developers.openai.com/api/docs/models/gpt-image-2): model inputs, outputs, and supported image-generation route.
- [OpenAI Cookbook: GPT Image prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide): artifact specifications, labeled prompt sections, explicit text, hierarchy, placement, and iterative edits.
- [OpenAI Academy: Creating images with ChatGPT](https://openai.com/academy/image-generation/): clear prompts, short quoted text, spatial language, small reference sets, and targeted revisions.

The numeric composition and copy budgets in this file are ACT production heuristics derived from the documented model characteristics. They are audited against rendered output and may be calibrated through approved pilots without changing the one-message, exact-copy, and validation-first workflow.
