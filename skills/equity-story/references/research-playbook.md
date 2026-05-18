# Research Playbook

A strategy or an equity story is only as strong as the information under it.
The recurring failure is an argument built on what the user happened to supply
plus the model's prior knowledge — a thesis asserted, not researched. This
playbook is for the agent building the story: it sets out **what to research**
and **how to research it efficiently** when the supplied inputs are thin or the
load-bearing claims rest on facts no one has checked.

Use it at *Inputs to gather first* and return to it from any workflow step where
the evidence is thinner than the claim it must carry. Match the effort to the
stakes — a seed story does not need an IPO-grade evidence base — but never let a
load-bearing claim stand on an unresearched assumption.

## Part A — The research agenda

Research is not open-ended reading. Target the facts the story's load-bearing
claims depend on. Organize the work by what each finding feeds.

- **"Why now" signals.** The inflection has to be evidenced, not asserted. Find
  the concrete curves that crossed: technology cost or performance trajectories,
  regulatory changes, adoption or penetration thresholds, measurable shifts in
  buyer behaviour. Timestamp each ("cloud inference cost down ~40% since 2020",
  "regulation X took effect 2024"). Two or three quantified, dated signals beat
  a vague claim that "the market is ready".
- **Market evidence.** Beyond the TAM number itself: the growth drivers, the
  budget the spend comes out of, the demand trend. For the headline market size
  and its triangulation, the discipline is in `references/market-sizing.md` —
  this playbook supplies the *inputs* that file's methods consume.
- **Competitors and comparables.** Map the real competitive set — including the
  non-obvious substitute and the incumbent's adjacent move — not a flattering
  shortlist. For a priced round, also research comparable companies and their
  valuation multiples (use the median, exclude outliers). The frameworks for
  *interpreting* this sit in `references/strategy-frameworks.md`; the agenda here
  is to *gather* the competitor and comparable facts they operate on.
- **Customer and demand evidence.** The strongest evidence is primary: what
  customers actually do and say. Where the story leans on demand or retention,
  seek evidence that does not come only from a management-curated list — a
  curated reference list is a designed selection bias. Sources that sidestep
  that bias: public review platforms, industry-specific forums and user
  communities, and channel checks with distributors, resellers or implementation
  partners. These corroborate or contradict the commercial claims.
- **Regulatory and structural landscape.** Licensing regimes, compliance
  obligations, and pending regulatory change — especially when the business
  model, or an adjacency the growth story depends on, operates in a regulated
  activity.
- **Team and founder verification.** The "why us" claim rests on concrete,
  checkable achievements and a genuine unfair advantage — research what can be
  verified rather than restating a biography.

**Authoritative sources, in rough order of weight:** primary and government
statistics (census, labour and trade agencies); standards bodies and industry
associations; public-company filings (10-K, 有価証券報告書 / EDINET, earnings
disclosures); reputable research-firm reports; primary research (expert and
customer interviews, channel checks). Cite the issuing body, the publication and
its date — a secondary aggregator's restatement is not a source.

## Part B — Researching efficiently with agents

When the gaps are more than a quick lookup, research **breadth-first** rather
than serializing every search. The method below is the orchestrator–worker
pattern: one agent scopes the work and synthesizes the results, while parallel
lines of research each cover an independent slice. What matters is this
*discipline* — scoped briefs, breadth-then-depth, source quality, synthesis —
not the mechanism. Where the environment provides a way to dispatch research
subagents, use it; where it does not, apply the same discipline to parallel
direct searches, each scoped as if it were a subagent brief.

- **Decide whether to split the work.** A single fact — one figure, one date —
  is a direct lookup; do it inline. Split into parallel lines when the research
  divides into *independent* sub-questions that can be pursued at once without
  depending on each other's results. Parallel research costs materially more —
  in tokens and tool calls — than a single search; reserve it for genuine
  breadth, not for one question.
- **Scale the number of research lines to the work.** A focused comparison needs
  two to four parallel lines; a broad research front needs more. Give each a
  distinct slice — by sub-question, industry segment, or source type — so no two
  repeat the same search. Separation of concerns is what makes parallelism pay.
- **Brief each line with four things.** Every brief states: the **objective**
  (the specific question to answer); the **output format** expected back;
  **guidance on sources and tools** (which sources count, primary over
  secondary); and the **task boundary** (what is in and out of scope). A vague
  brief — "research the market" — produces duplicated, unfocused work.
- **Go breadth-first, then deepen.** Open with broad scoping queries to see the
  landscape, evaluate what comes back, then narrow to the specifics. A line that
  starts with hyper-specific queries often returns nothing and misses context.
- **Steer to source quality explicitly.** Left unguided, search drifts to
  SEO-optimized content farms over authoritative material. Prefer primary
  sources, name the issuing body and date, and treat any load-bearing figure as
  unverified until checked against its origin. When a primary source and a
  secondary restatement of it disagree, use the primary figure and note the
  discrepancy — do not silently carry the aggregator's number.
- **Synthesize, don't concatenate.** The orchestrator integrates the findings
  into one picture: keep each claim tied to its source, surface contradictions
  between lines rather than silently choosing one, and judge
  what is still missing. Then make an explicit call — dispatch another round, or
  stop because the evidence is sufficient for the stakes.
- **Seek disconfirming evidence on purpose.** The sharpest research failure is
  confirmation bias — finding only what supports the thesis. Brief at least one
  line of inquiry to look for what would *weaken* the story: the strongest
  competitor, the demand that is not there, the regulatory obstacle. This feeds
  the objection and diligence work directly.

**Common failure modes:** over-parallelizing a task a single lookup would have
settled; vague briefs that cause two lines to duplicate each other; chasing a
rabbit hole past the point of relevance; trusting the first source without
checking it; and stopping when the answer is *comfortable* rather than when the
load-bearing claims are actually supported.

When the research is done, every load-bearing claim should trace to a named,
dated source — and the gaps that remain should be tagged `[open]`, not papered
over. That is the handoff from research into the rest of the workflow.
