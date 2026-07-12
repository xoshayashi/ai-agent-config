# Review And Repair Rubric

Use this file for the human repair loop after `lint_render`. `visual-qa-and-repair-rubric.md`
is the multi-lens visual checklist; this file is the operational repair menu.

## Self-Review Checklist

Before independent judging, confirm:

- title read-through forms a coherent deck argument
- each content slide has one claim
- title and evidence match
- sources, assumptions, and notes are separated
- typography is readable, with footer allowed to stay small
- YoY/delta/comparison sublines have visible air
- grid/flex contract is visible in the render
- body field is neither sparse nor cramped
- charts are comparative when using bars/columns
- closing slide role is chosen from the story, not a fixed template
- page numbers are absent
- no placeholder numbers or sources remain

## Repair Menu

- **R1. Rewrite title**: use when the slide has a topic title or claim/evidence mismatch.
- **R2. Split slide**: use when two claims or protagonists compete.
- **R3. Strengthen evidence**: add source, denominator, period, or better proof.
- **R4. Change composition move**: switch from cards/two-column/equal grid to a move that
  matches the evidence.
- **R5. Enlarge focal object**: scale chart/table/value/image before adding decoration.
- **R6. Rebuild grid/flex**: redefine role map, spans, alignment spine, bands, and gaps.
- **R7. Repair density**: move excess detail to notes/appendix or fill dead space with larger
  proof objects.
- **R8. Repair metric spacing**: separate value, unit, and YoY/delta subline.
- **R9. Replace single-bar chart**: use comparison, gauge, range, hero number, or table row.
- **R10. Rebalance close**: choose thesis, proof strip, decision request, next actions, quote,
  or legal close.
- **R11. Normalize color**: reduce accent, remove decoration, stabilize meaning.
- **R12. Fix source discipline**: separate source, assumption, note, and legal caveat.
- **R13. Fix production defect**: overflow, cropping, font substitution, broken render.
- **R14. Return to outline**: use when the chapter spine, governing thought, or evidence base
  is wrong.

## Severity

- **P0**: factual contradiction, unreadable proof, overlap, cut-off text, impossible source,
  or broken render.
- **P1**: grid/flex breach, weak evidence, title mismatch, excessive whitespace, cramped
  hierarchy, single-bar chart, fixed closing page.
- **P2**: polish, minor rhythm, small alignment drift, or optional copy tightening.

## Scoring Gate

Use defect-deduction scoring with `evals/rubric.json`. The deck must score at least 95
after independent judging. A beautiful deck with unsupported claims still fails.

