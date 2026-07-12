# Milestone Reviews

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
