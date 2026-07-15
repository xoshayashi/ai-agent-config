# Milestone Reviews

- milestone: updated reference-deck provenance footer | host: codex | end state: reviewed
  routes: antigravity=ok | digest route: yes
  conclusion: the new 9pt vertically centered x72/y866/w1528/h48 footer master, Source-only external provenance, and optional Assumption/Note annotations are consistent with the updated PPTX.
  verified: OOXML measurements were checked across slides 2-19; the reviewer independently confirmed geometry, centered baselines, prefix ordering, and empty-footer behavior; local skill eval passes 170/170.
  next: generate future ACT slides with one combined footer_master atom and the updated provenance rules.

- milestone: reference-deck master and replaceable semantic color architecture | host: codex | end state: reviewed
  routes: claude=blocked-then-repaired, antigravity=ok | digest route: yes
  conclusion: palette keys are replaceable behind stable roles, all reference-master geometry reaches the render basis, and the sample plus validator now enforce a non-overlapping body/message composition.
  verified: each Claude blocker was checked against current builder, geometry, plan, and prompt output and repaired; Antigravity's final strict gate found no blockers; local skill eval passes 163/163 and package tests pass 27/27.
  next: use `--design-tokens PATH` for palette changes while preserving the canonical geometry and semantic role schema.

- milestone: model-adaptive grid, balanced geometry, and luminous semantic tone vocabulary | host: codex | end state: degraded
  routes: claude=degraded, antigravity=ok | digest route: yes
  conclusion: the final plan, compiler, and rejection gates are coherent after fixing grid-width arithmetic, footer-present geometry, text/rule/connector coordinate loss, and explicit ambient/lifted/structural/focal role binding.
  verified: Claude's two blocking rounds were checked against the cited builder and geometry lines and repaired; the final Claude rerun timed out without output, while Antigravity independently confirmed the corrected arithmetic and 125/125 eval result; local packaging tests and diff checks also pass.
  next: use the compiled role-to-target tone map and render-basis coordinates for the next zero-base slide generation, then inspect the PNG against the same plan.

- milestone: slide-image quality architecture overhaul | host: codex | end state: reviewed
  routes: claude=degraded, antigravity=ok | digest route: yes
  conclusion: architecture direction is sound; add PNG noise density, relax manifest measurement tolerance to one grid unit, and remove remaining canonical-geometry string duplication before handoff
  verified: claims matched package_slide_images_to_pptx.py and build_act_slide_prompt.py; implemented 5-pixel row density, 8px tolerance, and canonical-geometry.json references; unit and skill evals rerun
  next: run full regression, existing-deck packaging, stale-rule scan, and completion audit

- milestone: positive generation-guidance refactor | host: codex | end state: reviewed
  routes: claude=ok | digest route: yes
  conclusion: positive lean contract preserves required quality guidance after Honey, composition-readiness, furniture, and Source-sentinel corrections
  verified: reviewer claims matched SKILL.md, lean_generation_contract, eval scenarios, and source-none contract; strict gate passed after three repair rounds; local skill eval passed 420/420
  next: retain QA rejection logic outside the image prompt and use the positive contract for future generation
- milestone: unified header, equal outer shell, and zonal mass contract | host: codex | end state: reviewed
  routes: claude=ok | digest route: yes
  conclusion: arithmetic conflicts in header stack, footer envelope, planning outputs, and size routing were identified and reconciled; the live lean and planning routes now share the current geometry.
  verified: canonical arithmetic checks pass; generated-contract assertions pass; skill eval 418/418 and packaging tests 27/27 pass with bytecode writes disabled; reviewer claims were checked against the cited files.
  next: regenerate deck pages from the revised contract and inspect their actual PNG bounds before delivery.

- milestone: higher occupancy and recursive Grid/Flex contract | host: codex | end state: reviewed
  routes: claude=blocked, antigravity=ok | digest route: yes
  conclusion: two Claude review rounds exposed declarative occupancy, unreachable sample targets, denominator ambiguity, and envelope-bound conflicts; the repaired contract passed an independent Antigravity strict gate with no blocker.
  verified: every cited issue was checked against the current builder and canonical geometry; plan values now derive from grid spans, Flex allocation rectangles, body-band area, and text/object ink shares; adversarial validation and package tests passed.
  next: use validated layout plans for subsequent slide generation and measure the generated PNG against the matching layout audit.

- milestone: footer-absent lower placement and outer-margin parity | host: codex | end state: reviewed
  routes: claude=blocked, antigravity=ok | digest route: yes
  conclusion: footer-absent body closure, centroid, quiet clearance, and visible-margin parity are mathematically consistent after removing the old anti-symmetry escape and separating footer modes.
  verified: reviewer arithmetic matched canonical geometry and the sample plan; footer-absent y=280..869, bottom closure y=857..869, centroid 59-62%, and <=12px margin difference are enforced; footer-present remains independently bounded.
  next: use the updated sample layout plan for the next footer-free generation and inspect actual H1/body ink margins.

- milestone: reference-render padding and header-scale calibration | host: codex | end state: reviewed
  routes: claude=blocked, antigravity=ok | digest route: yes
  conclusion: keep the reachable 50/72/17/72 shell and 16-column grid, audit its outside bands as quiet canvas, and use 47-50px H1 plus 33-35px subtitle rendered bands.
  verified: Claude's grid-reachability blocker matched the compiler arithmetic, the unreachable 112px container rule was removed, and Antigravity confirmed the repaired geometry closes and preserves the measured 28pt/20pt source master.
  next: use the supplied reference-render header crop for the next pilot and approve pixels only after the edge-band and rendered-height checks pass.

- milestone: unified header furniture and first-render contract | host: codex | end state: reviewed
  routes: claude=blocked, antigravity=ok | digest route: yes
  conclusion: title-side accent geometry is closed through a positive header inventory, body-contained geometry, compiled first-render routing, audited style-board order, and fixed header/footer/message masters.
  verified: Claude findings were checked and repaired across connector containment, manual-prompt bypass, header atom anchors, footer transparency, one-line footer baselines, and message-box identity; Antigravity strict gate then passed; skill eval 182/182, PPTX tests 27/27, and git diff check passed.
  next: generate the next sample through the validated layout plan and inspect the actual header pixel inventory before approving it as a pilot.
- milestone: header/body/footer balance and argument-closure repairs | host: codex | end state: degraded
  routes: claude=degraded, antigravity=degraded | digest route: yes
  conclusion: Prior Claude blockers were repaired in the cited validator paths; final compact rereview routes returned no substantive body, so independent final approval remains unavailable.
  verified: Grounding and primary-evidence checks passed against build_act_slide_prompt.py and sample-layout-plan.json; adjudication used the user contract plus 194/194 regression results; the next generated plan is predicted to reject direct-Grid mass, in-range occupancy drift, and unowned open closure rows.
  next: Keep the mechanical gate green and rerun the compact rereview when either external route returns substantive output.
