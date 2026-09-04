# Anti-Patterns

Use this file during self-review. These are defects to hunt, not style preferences.

## Core Anti-Patterns

- **F1. Topic title**: the title names a subject but does not state a conclusion.
- **F2. Evidence mismatch**: the title claims a number, period, or causal point the visual
  evidence does not prove.
- **F3. Two protagonists**: two charts, two messages, or two focal objects compete.
- **F4. Template reflex**: cards, equal grids, or two columns appear before judgment.
- **F5. Empty-body slide**: small objects float in excessive whitespace.
- **F6. Crammed-body slide**: the page fits only by shrinking important typography.
- **F7. Weak evidence inflated**: anecdote, logo, or unsupported claim gets strong visual
  weight.
- **F8. Ghost source**: source is missing, impossible, placeholder-like, or mixed with an
  assumption.
- **F9. Forecast disguised as actual**: plan, estimate, and target look identical to facts.
- **F10. Decoration as impact**: gradients, shadows, icons, or color noise replace structure.
- **F11. Repeated shell**: unrelated pages reuse the same layout grammar.
- **F12. Footer dominance**: source/note becomes visually louder than the argument.

## Extended Anti-Patterns

- **F13. Tiny proof**: the main chart/table/image is smaller than its claim deserves.
- **F14. Delta collision**: YoY, vs plan, or prior-year text is glued to the value line.
- **F15. Single-bar chart**: a lone bar is used where no comparison is possible.
- **F16. Fixed close**: closing page defaults to left-heavy statement plus metadata.
- **F17. Process afterthought**: arrow outcome labels are tiny, off-center, or treated as
  footnotes.
- **F18. Grid/flex breach**: notes describe structure but the render shows floating blocks,
  uneven gaps, or broken alignment.

## IR Anti-Patterns

- **F19. Progress without denominator**: progress is shown without target/range/context.
- **F20. Good-news-only grammar**: bad news is hidden or presented with a different visual
  grammar.
- **F21. Appendix logic in the mainline**: dense backup material replaces a focused proof page.
- **F22. Unsupported superlative**: rank, first, best, No.1, or largest lacks denominator,
  date, and source.
- **F23. Generic market size**: TAM is presented without reachable opportunity or assumptions.
- **F24. Cause-free movement**: chart shows movement but no driver, event, or interpretation.

## Production Anti-Patterns (machine-checked since 2026-09)

- **F25. Label on the edge**: a value label, delta, or heading whose glyphs cross a bar, card,
  or band edge. `verify_deck` reports it as a straddle failure; the fix is a measured frame
  height (`drawn_line_h`) and an anchor above or inside the shape, never a nudge by eye.
- **F26. Under-occupied body**: content-sized cards or rows that use less than half of the body
  band. `lint_render` reports the occupancy; the fix is the shared fill contract (`fit_band`),
  not a per-slide constant.
- **F27. Silent overload**: a spec past a pattern's cap that renders with text spilling over
  its frame. `validate_spec` caps cardinality; the reclaim ladder compresses gaps first; what
  still does not fit is reported, never hidden and never shrunk.

## Capstone Test

If the slide disappeared, would the reader's decision or belief change less? If not, delete,
merge, or rewrite the slide.

