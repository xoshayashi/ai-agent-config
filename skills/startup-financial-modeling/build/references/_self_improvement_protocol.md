# Self Improvement Protocol

Use this reference when a skill run has produced an artifact, when the user
asks to improve or repair a prior skill output, or when execution logs expose a
repeatable weakness. The purpose is to turn observed friction into reusable
skill improvements without overfitting to one company, source, or local machine.

## Trigger Signals

- The artifact is complete enough for closeout or the user asks for a follow-up
  improvement to a skill-generated output.
- Tests, strict audit, quality gates, recalc/render checks, live-comps refresh,
  source extraction, or tool calls fail, time out, or require manual workaround.
- The same fix loop repeats: command reruns, layout repairs, source rereads,
  brittle prompt interpretation, missing dependency closure, or cleanup noise.
- User feedback reveals a gap between the intended decision and the delivered
  workbook, memo, model spec, assumption register, or audit.
- External AI-agent, prompt, X, or workflow research is requested for improving
  the skill itself rather than supporting a financial claim.

## Evidence To Inspect

Inspect only the minimum sanitized evidence needed to learn the failure mode:

- failing command names, exit status, exact error class, and the check that
  later passed;
- before/after artifact deltas and the user correction that motivated them;
- repeated tool-call, source-ingestion, render, recalc, or dependency patterns;
- missing or weak eval coverage that allowed the defect through;
- unnecessary work such as excess files, broad searches, stale generated
  artifacts, or manual cleanup caused by the skill workflow.
- cost and efficiency signals such as wall time, repeated tool calls, large
  context loads, live-route degradation, and whether added process complexity
  materially improved output quality.

Never store raw local logs, secrets, API keys, private source text, customer
data, full conversation transcripts, or personal identifiers in the skill. If a
detail is confidential or source-specific, keep it in the artifact or final
report as an open item, not in reusable skill instructions.

## Reflection Record

When a reusable lesson is justified, keep the record compact and sanitized:

- task type and artifact type;
- redacted trace/log pointer or command evidence;
- observed failure and verification evidence;
- root-cause category;
- generalized lesson;
- proposed skill/runtime/test/eval change;
- privacy classification;
- cost/latency or tool-call impact when it affected the run;
- required regression proof.

The durable memory is the pattern: "failure pattern -> generalized rule ->
required check." Do not preserve a raw transcript as the lesson.

## Improvement Loop

1. Classify the signal: one-off artifact issue, reusable skill gap, eval gap,
   runtime helper bug, reference/protocol gap, dependency/tooling gap, or
   documentation ambiguity.
2. Fix the artifact first when the user-facing output is still wrong. Do not
   spend the user's time improving the skill while the requested workbook or
   memo remains broken.
3. Generalize only after naming the invariant. Convert the log lesson into a
   rule such as "when terminal demand is stated away from its noun, require
   structured YAML extraction" rather than copying the incident.
4. Patch the lowest durable layer:
   - runtime/helper code when deterministic behavior can prevent the defect;
   - tests, eval assertions, or quality gates when verification was missing;
   - reference protocol when judgment or routing must change;
   - `SKILL.md` only when triggering or first-step behavior must change.
5. Add regression proof. A reusable improvement needs at least one of: pytest,
   quality-gate assertion, eval assertion, deterministic rubric check, strict
   audit coverage, or an explicit closeout checklist item. Validate any durable
   reflection record with `build/runtime/self_improvement.py` or an equivalent
   privacy / invariant-shape scanner before writing it to the skill or progress
   log.
6. Keep eval roles separate. Capability evals prove broad skill behavior,
   regression evals protect known failures and should stay near-perfect, and
   holdout/adversarial examples should not be tuned against during the same
   iteration.
7. Rerun the check that failed and one broader gate that proves the skill still
   behaves in its normal path.
8. Before writing any Reflection Record, run `validate_reflection_record` from
   `build/runtime/self_improvement.py` or an equivalent scanner on the proposed
   record. Record only concise, sanitized learning in the project progress log
   when one already exists. Do not create auxiliary changelogs just for the
   skill.

## Research Intake

External material can improve the workflow, not the finance evidence. Use
papers, official docs, and reputable engineering posts as primary sources. Use
X/public social posts only as weak signals for practitioner pain points such as
trace capture, eval harnesses, failed-hypothesis notes, and feedback routing.

Translate research into concrete gates:

- Reflection and self-refinement patterns become a feedback -> refine -> verify
  loop with explicit stop conditions.
- Trace-based agent-improvement guidance becomes "derive changes from observed
  traces/logs, convert recurring failures into regression tests, then verify
  offline before closeout."
- Evaluator-optimizer patterns become separate generation, critique, repair,
  and acceptance checks when the output can demonstrably improve.
- Assertion/constraint research becomes deterministic workbook, source, unit,
  and design checks rather than free-form self-critique.
- Human/LLM judge guidance becomes advisory only unless paired with rule-based
  checks, artifact inspection, or domain rubric evidence.
- Cost/latency guidance becomes a complexity budget: add agent loops, live
  searches, or extra reviewers only when they improve measurable quality,
  reduce repeated failures, or protect a high-risk handoff.

## Stop Conditions

Do not generalize a lesson into the skill when:

- the issue is specific to one company, deal, confidential source, or temporary
  local environment;
- the evidence is a single ambiguous user preference with no reusable invariant;
- the proposed fix weakens strict audit, tests, or source discipline;
- the improvement depends on paid signup, credentials, policy change, or live
  production action the user has not approved;
- the change alters skill doctrine, privacy handling, evidence admissibility,
  or audit pass criteria without milestone/human review;
- no regression proof can be added.

If any stop condition applies, fix or document the artifact-level issue and
leave the skill unchanged.

## Closeout Addendum

Before final response on a skill-quality run, state whether session-log or
post-output learning produced a reusable change, which layer was patched, and
which regression proof now protects it. If no reusable change was justified,
say so and name the stop condition.
