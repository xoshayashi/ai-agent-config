# Milestone Review Record

- milestone: English rewrite and cleanup of `act-structured-slide-generation` docs/evals | host: codex | end state: blocked
  routes: claude=degraded(timeout 180s), gemini=degraded(missing CLI), antigravity=degraded(timeout 180s) | digest route: yes
  conclusion: no independent judgment review completed; do not treat this milestone as externally reviewed
  verified: mechanical checks passed (`pytest` 63 passed, `quick_validate` valid, eval deck validate/build/verify/render/lint all passed with 12 slides / 0 findings and baseline diff unchanged)
  next: hand off with the independent-review limitation disclosed

- milestone: banker-grade robustness upgrade of `act-structured-slide-generation` (stress-test-driven) | host: claude-code | end state: complete
  routes: codex=ok (skill-level text review of skill-rubric.json, ~62s, converged) | digest route: no (reviewer read the tree itself)
  method: authored a fresh 14-slide stress brief (manufacturer portfolio restructuring — negatives, dense multi-segment P&L, negative-drag waterfall, thin-evidence sizing, long KPI deltas, long closer) that the two showcase decks could not exercise; the gaps it surfaced defined the scope.
  changes: (1) center_hero statement now clause-breaks on 、 and font-fits (28pt floor) so the closing line never orphans a tail char — also fixed the same latent orphan in BOTH shipped example closers; (2) KPI card delta row height is now measured so a long delta cannot collide with its note (verify_deck FAIL on the stress deck → 0 failures); (3) validate_spec warns when a center-hero statement clause exceeds 22 全角; (4) doc fixes — SKILL.md pip path `scripts/requirements.txt`, deck-spec.md chart types corrected to the real `column|stacked_column|bar|line|donut`.
  conclusion: independent codex review scored 99/100 (pass, threshold 95), verified all four changes correct/regression-free via its own Python probes, and raised one legitimate minor (statement warning was over-broad across variants) — FIXED and re-verified (center_hero warns, split_evidence does not).
  verified: `pytest` 63 passed; `quick_validate` valid; both example decks + the stress deck pass validate/build/verify/render/lint; orphan and KPI-overlap fixes visually confirmed in rendered PNGs with short-delta KPIs pixel-unchanged.

