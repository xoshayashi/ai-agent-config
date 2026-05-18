---
name: equity-story
description: >-
  Build a company's equity story — the structured valuation thesis that argues why an
  investor should back this company, at this price, now. Use this whenever the user needs
  an investor-facing narrative: a fundraising story, pitch narrative, investment thesis,
  IPO equity story, IR / roadshow message, growth-potential disclosure (成長可能性資料),
  or wants to sharpen "why invest in us". Trigger even when the user only says
  "equity story", "エクイティストーリー", "investor narrative", "fundraising story", or asks
  how to frame their company for investors — for VC rounds (seed to growth), late-stage,
  or IPO, in Japan or the US. This skill produces the narrative and strategic framing;
  for the financial model and projections use startup-financial-modeling, and for
  finished slide images use the slide-image skills.
---

# Equity Story

## What an equity story is

An equity story is the **valuation thesis**: a coherent argument for *why an
investor should back this specific company, at this price, right now*. It is not
a pitch deck. The deck is an artifact; the equity story is the argument the deck
exists to carry. Investors do not invest in returns — they invest in a narrative
they can believe and then **defend internally** (to an investment committee, a
valuation committee, or their own partners).

So the test of an equity story is not "is it polished" but: **can a sceptical
reader follow the logic alone, find the risks already addressed, and repeat the
thesis in two sentences afterwards?** Optimize for that, never for decoration.

Three failure modes recur. Watch for them throughout:
- **Solution-first.** Leading with the product before the reader feels the
  problem leaves the thesis with no emotional anchor — it reads as a product
  tour, not an investment case.
- **Claims without evidence, or evidence without claims.** A number only
  persuades when it is attached to the specific assertion it proves. Standalone
  metric slides are a sign of a weak narrative.
- **Narrative detached from economic reality.** A story that needs the reader to
  ignore the unit economics, the comparable set, or the cash position will be
  found out. Stories that survive are the ones grounded in the numbers.

The craft and substance standards in this skill are **universal** — they apply
at every stage and in every geography. What the stage playbooks adjust is the
*depth and kind of evidence*, not the quality bar.

## Inputs to gather first

Before writing anything, establish these five things. Infer small gaps and state
the assumption; only ask the user when an answer materially changes the thesis.

1. **Company & product** — what it does, in one plain sentence a non-expert
   understands. If you cannot write that sentence, the story is not ready.
2. **Stage & context** — VC seed / VC growth / late-stage-private / IPO /
   public IR / M&A exit. And the geography: **Japan or US** (this changes the
   playbook materially).
3. **What is known** — traction, financials, market data, unit economics. If a
   financial model spreadsheet (xlsx) exists, pull unit economics, NRR, runway
   and comparable-company multiples from it and **cite it as the source**; if a
   model is needed and missing, build it with `startup-financial-modeling`
   first. Without a model, mark figures as estimates or assumptions and keep
   them separable from facts.
4. **Audience** — who reads this (seed VC, growth fund, crossover investor,
   IPO institutional book, retail). The audience sets how much vision vs. proof
   the story should carry.
5. **The ask** — round size / offering, valuation or range, and the milestones
   the money buys.

## Workflow

Work through these steps in order. Most steps point to a reference file to load
when you reach it — load them just in time, not all upfront.

### 1. Choose the stage playbook

Read `references/stage-playbooks.md`. The **centre of gravity of the argument
shifts by stage**: seed leans on team, insight and early signal; growth leans on
unit economics and proof of scale; IPO and public markets lean on predictable
cash flow, a path to the Rule of 40, comparables discipline, and governance.
A seed-stage argument presented to an IPO book — or vice versa — fails.

If the context is a **Japanese IPO or Japanese fundraising**, also read
`references/japan-ipo.md`. Japan has its own conventions: the underwriter's
review (引受審査), the mandatory growth-potential disclosure (成長可能性資料),
the anticipated-Q&A pack (想定問答集), the Growth-to-Prime market path, and a
more conservative, IPO-oriented exit culture.

If the audience is a **strategic acquirer (M&A exit)** rather than an investor,
read the "M&A exit / strategic-buyer narrative" section of
`references/stage-playbooks.md` — the story shifts from standalone return to
synergy and accretion. When the exit path is unstated, ask the user before
defaulting to a fundraising framing.

### 2. Build the narrative spine

Every equity story, at every stage, answers four questions. This is the spine —
build it before drafting prose.

- **Why now** — *Why is this possible now and not five years ago?* Nature
  abhors a vacuum: if the opportunity is real, something changed — technology
  cost, regulation, behaviour, a crossed adoption threshold. Name the
  inflection and quantify it. A story without a credible "why now" cannot
  explain why the window is open. Place it early.
- **Why us** — *Why will this team win this market?* Investors back people.
  Use concrete, verifiable achievements and a genuine unfair advantage
  (founder-market fit), not titles or biographies.
- **Why this** — *Why this problem and this market?* State the problem before
  the solution, so the reader feels the pain first. Then give the non-obvious
  insight: the truth about the market others have missed. Never claim "no
  competition" — it signals either no research or no understanding of the
  market.
- **Why this price** — *Why does this valuation make sense?* Justify it as
  *risk already retired × upside still to come*. For private rounds: the
  concrete milestones the round funds over the next 18–24 months, and why the
  next round will be priced higher. For IPO/public: comparable-company logic
  and multiple discipline (see stage playbook). Show progress as **a line, not
  a dot** — the trajectory since the last raise, not a single snapshot.

### 3. Select the strategic framing

Read `references/strategy-frameworks.md`. It is a catalogue of moat,
positioning, and business-model frameworks with a **dispatch table** ("in this
situation, reach for this"). Use it to answer two *separate* questions:

- **How big is the opportunity?** (category design, blue ocean, jobs-to-be-done)
- **Why will the company keep winning?** (the 7 Powers, network effects,
  counter-positioning, switching costs)

Keep these distinct. Opportunity frameworks do not prove durability — pair them
with a moat framework so the story explains both the prize *and* the reason a
fast follower or incumbent cannot take it. Tie each business line to at least
one named source of durable advantage.

This repository's host environment may also expose strategy skills
(`jobs-to-be-done`, `crossing-the-chasm`, `blue-ocean-strategy`,
`obviously-awesome`, and others). When a framework needs deeper treatment than
the catalogue gives, consult the dedicated skill rather than re-deriving it.

### 4. Place proof points as evidence

Numbers belong *next to the claim they prove*, never in a standalone pile.

- **TAM / SAM / SOM** proves *Why this* (the size). Build it **bottom-up**
  (customers × price) with the calculation shown. Top-down billions read as
  hand-waving and draw the most scrutiny. Order it SOM → TAM: the wedge you can
  take, then the category it opens.
- **Traction** is the empirical proof that *Why now* and *Why us* were right.
  Always time-stamped ("0 → 1,000 in 8 weeks", not "1,000 users"). Investors
  back momentum, not absolute numbers. If traction is weak, omit the section
  rather than dressing it up.
- **Unit economics** prove *Why this price* and durability. Use verifiable
  actuals — CAC, LTV, gross margin, payback, burn multiple, NRR. Their weight
  in the story rises with stage.

For each major claim, identify the one **load-bearing number** — the figure
that, if it were false, would break the claim — and present it **in context**,
never naked. A number alone is arithmetic; a number against a comparison is
evidence. Pair it with a prior-period delta, an industry benchmark, or a cohort
cut so the reader can judge its weight ("NRR 128%, vs. a 110% SaaS median",
not "NRR 128%").

### 5. Preempt the objections

Read `references/investor-objections.md`. A strong equity story does not hide
its weaknesses — it **frames them first and shows why they are acceptable**.
Walk the objection catalogue, pull the questions a real investor at this stage
and geography would ask, and fold the answers into the body of the story. Then
collect the sharpest ones into an explicit anticipated-Q&A section.

### 6. Draft the equity story

Produce the output in the format below. As you draft, read
`references/narrative-craft.md` and apply it — the logic alone does not make a
story get read to the end, remembered, and retold accurately to partners who
were not in the room. Craft carries the logic; it never fakes it.

### 7. Self-review and iterate

Run the self-review checklist. Do **not** present the story as finished on the
first pass — score it honestly, fix the gaps, and iterate until it passes or a
concrete blocker remains. This discipline is the point of the skill.

## Output format

Default to a structured Markdown document. Adjust depth to stage and audience,
but keep this order — it *is* the narrative spine made visible:

```markdown
# Equity Story — [Company]

> Evidence legend: [fact] supplied/verified · [derived] computed from facts ·
> [estimate]/[assumption] inferred · [open] a diligence question.

## Thesis in brief
[The company in one declarative sentence. Then 3–5 investment highlights —
the load-bearing reasons to invest, each one sentence. One highlight should
state the contrarian core: what most informed people believe that this thesis
bets against. Close with the carry-home — the single phrase or image compact
enough that a reader repeats it intact to partners who were not in the room.]

## Why now
[The inflection. Quantified.]

## The problem
[The customer pain, told from the customer's side. Before the solution.]

## The insight & the solution
[The non-obvious truth, then what the company built on it.]

## Why this team
[Concrete, verifiable founder-market fit and unfair advantage.]

## Market
[Bottom-up TAM / SAM / SOM with the calculation shown. SOM → TAM.]

## Business model & unit economics
[How it makes money; CAC / LTV / margin / payback / NRR as actuals or
clearly-marked estimates.]

## Competition & moat
[Honest competitive map. The named sources of durable advantage from the
strategy frameworks. Opportunity size and durability kept distinct.]

## Traction
[Time-stamped evidence. Omit if genuinely weak.]

## Financial trajectory & the ask
[The path; the round/offering; what the capital buys; the milestones.]

## Vision
[The wedge → category arc: take the wedge, earn the right to the category.]

## Anticipated investor questions
[The toughest questions for this stage/geography, each with a direct answer.]
```

When the user wants a deck, append a **slide outline**: a one-line heading and
a one-line message per slide, mapped to the sections above. Generate slide
*images* only via the dedicated slide-image skills — this skill owns the
narrative and the headings, not the rendering.

Write in the user's working language. In a Japanese IPO context, generate the
sections that correspond to official documents — the 成長可能性資料 growth
disclosure, the 想定問答集, prospectus-equivalent text — **in Japanese**, since
those are written in Japanese by convention.

**Mark the evidence status of every material figure.** A reader — and a
diligence team — must be able to tell a verified fact from an inference at a
glance. Use a short, explicit convention and a one-line legend at the top of the
document, for example: `[fact]` supplied or verified, `[derived]` computed from
facts, `[estimate]`/`[assumption]` inferred, `[open]` an unresolved question for
diligence. Never invent a number to fill a gap — tag it `[open]` and name it as
a diligence item. Naming the open items is what makes the rest credible.

Tie every recommendation to the reader's decision criteria (price, ROI, cost
structure, growth, durability). Follow `DESIGN.md` for tone: quiet, specific,
no hype, no unsupported superlatives. See `references/examples.md` for a
compact worked equity story that shows the whole arc end to end.

## Self-review checklist

Score the draft against every item. A story has to be both *correct* and
*persuasive* — the two axes below are scored separately, and a "no" on either is
a gap to fix before iterating.

### A. Substance — is the argument correct?

1. **One-sentence test** — can the company be defined in one sentence a
   non-expert understands, with no jargon?
2. **Spine complete** — are Why now / Why us / Why this / Why this price each
   answered, and is "why now" anchored to a real, quantified inflection?
3. **Problem before solution** — does the reader feel the pain before seeing
   the product?
4. **Evidence attached** — is every material number next to the claim it
   proves, and is every load-bearing claim backed by something verifiable?
5. **Bottom-up market** — is TAM built bottom-up with the calculation visible,
   not an unsourced top-down billion?
6. **Opportunity vs. durability separated** — does the story name *both* how
   big the prize is *and* a specific reason the company keeps winning?
7. **Differentiation is concrete** — is the moat tied to a named framework and
   to evidence, not asserted as "first mover" or "better product"?
8. **Objections preempted** — are the obvious investor objections for this
   stage/geography addressed inside the story, not left for the reader to raise?
9. **Stage fit** — does the centre of gravity match the stage (team/insight for
   seed; unit economics for growth; cash flow/comparables/governance for IPO)?
10. **Grounded in reality** — does the thesis hold without asking the reader to
    ignore the unit economics, the comparable set, or the cash runway?
11. **Trajectory not snapshot** — is progress shown as a line (deltas over
    time), not a single dot?
12. **Retellable accurately, survives a sceptic** — could a third party read it
    alone, stress-test it, and still retell the thesis to a sceptical partner in
    thirty seconds without drifting?

### B. Craft & persuasion — will it get read, remembered, retold?

See `references/narrative-craft.md` for how to fix a "no" here.

13. **Carry-home** — is there a single phrase or image the reader walks out
    holding and can hand on intact?
14. **Contrarian core** — can the one non-obvious idea the thesis bets on — what
    most informed people believe that this story bets against — be stated in
    one plain sentence, and is it visible in the story?
15. **Insider detail** — does each major claim carry at least one concrete
    detail an outsider with no operating experience could not have written?
16. **Numbers in context** — does each major claim's load-bearing number appear
    with a comparison (prior period, benchmark, or cohort), not naked?
17. **Hook and ending** — does the first line create tension rather than define
    a term, and is the strongest line at the end?
18. **No empty superlatives** — is every "leading / best-in-class /
    transforming"-type word either earned by an adjacent verifiable fact or cut?

### Final gate

In one line, score the honest outcome: **would this win a second meeting, or be
set aside?** If "set aside", the draft is not done — find which axis failed and
iterate.

## References

Load these as the workflow reaches them, not all at once:

- `references/stage-playbooks.md` — how the argument shifts across VC seed,
  VC growth, late-stage, IPO and public-market IR; valuation and
  comparable-company framing; stage-specific failure modes.
- `references/strategy-frameworks.md` — catalogue of moat, positioning and
  business-model frameworks, each with essence / when to use / proof investors
  expect / pitfalls, plus a situation→framework dispatch table.
- `references/japan-ipo.md` — Japanese IPO and fundraising conventions:
  underwriter review, the 成長可能性資料 growth disclosure, prospectus drafting,
  想定問答集, the Growth→Prime path, comparable-company valuation practice.
- `references/investor-objections.md` — catalogue of tough investor questions
  by topic, with how to preempt each one inside the story.
- `references/narrative-craft.md` — the craft that makes a sound thesis get
  read, remembered and retold: tension, concreteness, the carry-home, the
  honesty boundary, and the banned-without-evidence phrases. Read while drafting.
- `references/examples.md` — a compact, annotated worked equity story
  (fictional growth-stage company) showing the full arc, the evidence-tagging
  convention, and how the framework choices land in practice.
