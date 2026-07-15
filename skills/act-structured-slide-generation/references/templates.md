# Design Templates

A design template is the look the whole deck wears — the Google-Slides "theme", not a
per-slide layout. One is chosen for the deck (`meta.template`) and every slide is generated
inside it. This is the one design choice that is a real menu; everything else on a slide is
composed by judgment (`slide-decision-engine.md`), never by a type label.

## The starter set

List them from the registry, never from memory (the valid set is the files in
`references/templates/`, exactly like the pattern registry):

```bash
python3 scripts/build_deck.py --templates
```

| `meta.template` | Look | Use it for |
|---|---|---|
| `standard` (default) | Calm teal on soft white | General IR, proposals, internal decks |
| `navy` | Navy lead, cool tint | Board, IR, regulated or financial audiences |
| `monochrome` | Ink and grey, one accent | Austere decks that argue with numbers and structure alone |
| `bold` | Teal, enlarged type | Stage talks and pitches read from the back of the room |

Omit `meta.template` (or set `standard`) and the deck is byte-for-byte what it was before
templates existed — the default is a true no-op.

## What a template may change, and what it may not

A template is a partial patch merged over `tokens.json` by `deck_text.resolve_tokens`. Every
script resolves the effective tokens through that one function, so the ruler the builder draws
with is the ruler the validator measures with.

**May override** — the visible design layer:

- `colors` — remap the role of the lead hue and its tints (`primary`, `primary_deep`,
  `primary_pale`, chart greys). `resolve_tokens` **enforces** two bounds: every value must
  already be in `tokens.colors` (a template introduces no new hex, so the colour allowlist is
  unchanged and `validate_spec` / `verify_deck` need no template awareness), and the accent
  roles (`accent`, `accent_pale`, `accent_line`) may not be remapped — the accent stays the
  single highlight (DESIGN.md: ≤1 use per slide), and `validate_spec` counts it from the base
  palette. A "bold" template gets its punch from scale, not more accent.
- `type_scale_pt` — the type sizes. Header capacity is derived from type size, so a larger
  scale simply asks for shorter titles; `validate_spec` flags any that overflow.
- `layout` (except `optical_stack`) — margins, gutter, header/divider geometry, card radius
  and tint, footer, chart unit-note.
- `chart_style` — the categorical series palette and bar geometry.

**Must not touch** — the invisible geometry the build bakes in but `verify_deck` cannot recover
from the built file:

- `leading` (the line-box / line-spacing model), `layout.optical_stack` (the 300 dpi ink
  calibration), `fonts`, `slide` dimensions, `text_budget`, `header_contract`, `color_policy`,
  `line_break`.

`resolve_tokens` raises if a template patch names any locked key — a template that reaches into
the line-box model is a defect, not a design choice, because it would make the builder and the
verifier disagree silently.

## Adding a template

1. Add `references/templates/<name>.json` with a `$template` block (`label`, `use`) and only
   the allowed overrides above. Keep every colour inside `tokens.colors`; if a genuinely new
   tone is needed, add it to `tokens.colors` once (it enters the sanctioned allowlist there).
2. Nothing else to register — `list_templates()` reads the directory, `validate_spec` accepts
   the new name, and `build_deck` applies it. Confirm with the full chain under the new
   template on one deck: `validate_spec` → `audit_argument` → `build_deck` → `verify_deck` →
   `lint_render`, all green.
