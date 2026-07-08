# python-pptx pitfalls and rules (read when modifying the renderer)

Sources: the official anthropics/skills pptx skill, community CJK skills, and this skill's
own field testing.

## Japanese fonts (most critical)

1. `run.font.name` rewrites only `<a:latin>`. Japanese runs need an explicit
   `<a:ea typeface="Noto Sans JP"/>` under `<a:rPr>` (implemented by build_deck.py's
   `_set_run_fonts`). Skip it and Japanese text silently falls back to MS Mincho etc. in
   real PowerPoint.
2. Chart-internal text also needs `<a:ea>` on `defRPr` under `<c:txPr>` (implemented by
   `_chart_ea_fonts`). Table-cell runs likewise (covered via `_table_font` →
   `_set_run_fonts`).
3. Weight 600 cannot be expressed with the bold flag. Specify the separate family names
   "Geist SemiBold" / "Noto Sans JP SemiBold" (assumes the static 600 instances are
   installed). 700 is bold=True.
4. python-pptx cannot embed fonts. Machines without Geist / Noto Sans JP will substitute.
   tokens.json's fallback_ea (Yu Gothic) is the hedge.

## Dimensions and XML

5. 1 inch = 914,400 EMU; 1 pt = 12,700 EMU; 16:9 = 12,192,000 × 6,858,000 EMU. Always use
   the `Inches()/Pt()/Emu()` helpers; never raw ints. XML `sz` is centipoints
   (`sz="1800"` = 18pt) — confusing it with points is a 100× error.
6. XML manipulation uses lxml (python-pptx is lxml internally). `xml.etree.ElementTree`
   corrupts namespaces — never.
7. There is no z-order API. XML order inside spTree is stacking order = **add backgrounds
   and underlays first**.
8. There is no transparency API (insert `<a:alpha>` into fill XML). Mixing alpha into an
   8-digit hex corrupts the file.
9. Files in scripts/ named like stdlib modules (`io.py`, `types.py`, `inspect.py`) kill
   lxml with circular imports.
10. There is no slide delete/reorder API. **Fixes edit deck.json and rebuild everything** —
    that is the rule.

## Text and overflow

11. Never trust `fit_text()` / autofit. fit_text needs a font path and mismeasures CJK;
    normAutofit is not recomputed until PowerPoint opens the file. Final sizes come from
    verify_deck.py's Pillow real-font measurement (getlength on the actual TTFs); write
    only confirmed values.
12. No auto-shrink on overflow. Text-budget violations (validate_spec.py) go back to the
    spec for rewriting. Only titles get the two-line fallback (handled by build_deck.py).
13. There is no bullet API. This skill standardizes on plain text boxes with a leading
    「・」 (no collision with placeholder-derived buChar, so no double bullets).

## Charts

14. chartEx types (native waterfall etc.) cannot be generated. waterfall / roadmap /
    2x2 map / market funnel are drawn by shape composition (data not editable, but shapes
    are editable individually). Standard charts (column/bar/line/donut) are generated
    natively, keeping data editability.
15. Fine-grained formatting APIs are thin. Series color, gap_width, and data labels are
    API-level; anything past that (secondary axes, …) means XML surgery on
    `chart._chartSpace` — avoid on principle. Per-point fill/outline is available via
    `series.points[i].format.fill / .line` (used by forecast_from's actual/forecast
    styling; renders correctly in LibreOffice too).
16. Table column widths do not auto-fit. Always give col_widths (ratios). Cells carry
    default side padding (0.1in each), so keep text budgets conservative.

## Known LibreOffice render-QA quirks

- **LibreOffice 26.2 draws negative values in column/bar charts as absolute (upward)
  bars** (the axis range extends negative but the bar points up; line charts are fine;
  the pptx data itself is correct and PowerPoint renders correctly).
  → Put negative series in a line chart, the waterfall pattern, or a table.
  validate_spec.py warns.

## Design discipline

17. A full-width accent rule under the title is banned as the "AI-generated slide"
    signature. Act headers are undecorated (hierarchy from the title/subtitle size
    contrast alone).
18. No centered body text (except cover, section dividers, KPI values).
19. Smart quotes and placeholder residue (lorem, xxxx, TBD) are lint-detected and removed.
20. Set shadow.inherit = False on every shape (Act bans drop shadows).
