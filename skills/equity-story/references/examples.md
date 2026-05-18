# Worked Example — Equity Story Reference

A compact, annotated equity story for a **fictional** Series B company. It shows
the full arc end to end and the evidence-tagging convention. `> Annotation:`
lines explain *why* each move is made — they are not part of the deliverable.

**"Forgeline" is a fictional company.** Its name, figures, founders and metrics
are all invented for illustration — it is not, and does not refer to, any real
business.

---

# Equity Story — Forgeline

*Series B equity story. Audience: growth-stage venture investors. Geography: US.*

> **Evidence legend.** `[fact]` supplied/verified · `[derived]` computed from
> facts · `[estimate]` inferred · `[open]` a diligence question. No figure is
> invented to fill a gap.

> Annotation: a one-line legend up front lets a sceptical reader separate
> verified facts from inference at a glance. Both the spine and the proof points
> below lean on it.

## Thesis in brief

**Forgeline is a marketplace where companies upload a custom-part design and get
it manufactured by a vetted network of small machine shops — instant quote, one
accountable counterparty, parts shipped.**

Investment highlights:

1. **The contrarian core.** The industry treats machining *capacity* as the
   binding constraint and races to add it; Forgeline's bet is that capacity was
   never scarce — *matching* was. Instant quoting removed the real bottleneck,
   and the winner is whoever clears the market, not whoever owns the machines.
2. **A two-sided marketplace past its cold start.** 2,400 buyers and 600 shops
   transact on the platform `[fact]`; the liquidity that makes a marketplace
   hard to start now works *for* Forgeline, not against it.
3. **The flywheel is showing in the numbers.** GMV grew from $14M to $48M
   annualized in twelve months `[fact]` — a 3.4× year, against the ~40–60%
   typical for a marketplace at this size `[estimate]` — at an 18% take rate
   `[fact]`; buyer net revenue retention is 140% `[fact]`, well above the
   ~110% B2B-marketplace median `[estimate]` — the installed base compounds on
   its own.
4. **Founder-market fit on both sides.** The founders ran operations at a
   contract manufacturer and marketplace operations at a logistics platform —
   the supply side and the marketplace mechanics this business fuses.
5. **A wedge that opens a category.** CNC machining is the entry point; sheet
   metal, injection molding and finishing are the same buyers, the same shops,
   the same engine.

**Carry-home:** *Forgeline is the demand layer for custom manufacturing — the
constraint was never the machines, it was the matching.*

> Annotation: highlight 1 states the contrarian core in one plain sentence — the
> belief the thesis bets against. Highlight 3 puts each load-bearing number next
> to a benchmark, so the reader can weigh it. The carry-home compresses the whole
> thesis into one line a reader can repeat intact.

## Why now

Running a custom-parts marketplace was impractical for one structural reason:
**quoting**. Pricing a machined part means interpreting its geometry, tolerances
and material — historically a day or more of a skilled estimator's time. A
marketplace cannot clear if every quote takes a day.

Two things changed:

- **Instant quoting became real.** Automated geometry analysis now prices a part
  in seconds from the uploaded CAD file. The transaction that used to take days
  is now immediate `[estimate]` — the direction is well established across the
  digital-manufacturing tooling layer.
- **Shop capacity is visibly underused, and supply chains are reshoring.** Small
  shops run below capacity and want fill-in work; buyers burned by long offshore
  lead times are sourcing domestically `[estimate]`.

The inflection that matters is the first: instant quoting removed the friction
that made the marketplace un-runnable. That is why Forgeline is a business now
and was not five years ago.

> Annotation: "why now" is anchored to one concrete, quantified inflection
> (quoting time: days → seconds), placed early, and stated as load-bearing. The
> reshoring tailwind is secondary and tagged `[estimate]`.

## The problem

A hardware company's engineer needs 50 custom machined brackets. Today that
means: email the drawing to three or four shops, wait days for quotes back,
compare them, pick one, chase status by phone, and hope the parts arrive on
spec. Every new part repeats the loop. The buyer carries the integration cost of
managing a roster of shops; no single shop is accountable for the whole order.

On the other side, a small machine shop has idle machine-hours but no cheap way
to find the next job — it relies on word of mouth and a handful of repeat
accounts, and quoting eats the owner's evenings.

So the pain is concrete and recurring on both sides: **buyers spend days
sourcing every part and own all the coordination risk; shops have capacity they
cannot fill.**

> Annotation: problem before solution, told from the customer's side, both
> sides of the marketplace. The reader feels the pain before the product
> appears.

## The insight & the solution

**The insight.** The bottleneck was never manufacturing capacity — it was
*matching*. The capacity exists; what was missing was a way to price and route a
job fast enough for a marketplace to clear. Once quoting is instant, a
marketplace can aggregate fragmented demand and fragmented supply that neither
side could find efficiently alone.

**What Forgeline built.** A buyer uploads a CAD file and gets a price in
seconds. Forgeline routes the job to a vetted shop, manages the order, and is
the single accountable counterparty for quality and delivery. The buyer never
manages a roster of shops; the shop gets matched demand without quoting.

> Annotation: the insight is non-obvious (the constraint is matching, not
> capacity) and it is what the "why now" unlocks. The solution follows from it.

## Why this team

- **Manufacturing operations.** One founder ran operations at a contract
  manufacturer — direct, verifiable experience with the supply side: how shops
  price, schedule and fail `[fact]`.
- **Marketplace operations.** The other ran marketplace operations at a
  logistics platform — direct experience building liquidity and trust in a
  two-sided market `[fact]`.

The unfair advantage is the pairing: marketplace skill without manufacturing
depth mis-vets shops; manufacturing depth without marketplace skill cannot build
liquidity. `[open]` The bench below the founders is a fair diligence question.

> Annotation: concrete, verifiable, each founder owns one side of the business.
> The thin spot (the team bench) is named, not hidden.

## Market

Sized **bottom-up**, customers × spend, calculation shown. US manufacturing
output is context, not the TAM — Forgeline earns a take rate on routed orders.

- **SOM — the CNC machining wedge.** US firms regularly buying custom machined
  parts online: ~120,000 `[estimate]`; serviceable custom-parts spend ~$25k per
  firm per year `[estimate]`; at an 18% take rate, SOM ≈ 120,000 × $25k × 18% ≈
  **$540M/year** `[derived]`. Forgeline's ~$8.6M net revenue `[derived]` is a low
  single-digit share of this wedge — proven, with room left.
- **SAM — all digital custom-parts sourcing** (add sheet metal, molding,
  finishing): on the order of **$2–3B/year** of take-rate revenue `[estimate]`.
- **TAM — the category the wedge opens.** With adjacent processes and supply-side
  financial services layered on, **$5–7B/year** `[estimate]`.

The defensible number is the bottom-up SOM; SAM and TAM rest on assumptions
diligence should test. The wedge alone supports this round.

> Annotation: bottom-up, calculation visible, SOM→TAM order, headline output
> figure refused as TAM. Estimates tagged.

## Business model & unit economics

Forgeline takes an **18% take rate** `[fact]` on GMV routed through the platform.

| Metric | Value | What it proves |
|---|---|---|
| GMV | $48M annualized, up from $14M `[fact]` | The marketplace is clearing and accelerating |
| Take rate | 18% `[fact]` | Forgeline captures real value for the coordination it removes |
| Buyer NRR | 140% `[fact]` | Buyers route more parts over time — the base compounds |
| Blended gross margin | 35% `[fact]` | Marketplace economics; thinner than software, normal for managed marketplaces |

`[open]` Gross retention behind the 140% NRR, take-rate durability under
competition, and shop-side retention are the first diligence items.

> Annotation: each number sits next to the claim it proves. Open items named
> rather than papered over.

## Competition & moat

**The competitive map.** The default is the buyer's own roster of shops
(fragmented, manual). Other digital-manufacturing marketplaces exist and compete
directly. Large contract manufacturers serve big accounts but not the long tail.
"No competition" would signal no research.

**Why Forgeline keeps winning** — durability, kept distinct from market size:

- **Network effects (two-sided).** More shops → faster quotes, more capacity,
  better pricing → more buyers → more volume for shops. The 140% buyer NRR
  `[fact]` is early evidence the loop holds.
- **Aggregation Theory.** Forgeline owns the buyer relationship and the demand;
  shop capacity is modular and substitutable. Owning demand is the durable
  position.
- **Switching costs (building).** As a buyer's part history, reorder flow and
  quality record accumulate on Forgeline, re-sourcing elsewhere gets costly.

`[open]` Multi-homing — shops and buyers using several marketplaces — is the
real risk to the network-effects claim and should be diligenced.

> Annotation: opportunity (Market) and durability (here) kept separate. The moat
> is tied to named frameworks and to evidence; the honest risk (multi-homing) is
> stated, per `strategy-frameworks.md`'s warning on network effects.

## Traction

Shown as a line, not a dot. All figures `[fact]`.

- **GMV $14M → $48M annualized in 12 months** — ~3.4×.
- **2,400 buyers, 600 shops** — real liquidity, past the cold start.
- **Buyer NRR 140%** — the base alone would compound revenue ~40%/year.

`[open]` A quarterly GMV series and cohort-level buyer retention would sharpen
the trajectory; they belong in the data room.

## Financial trajectory & the ask

**The path.** GMV 3.4× in a year at a stable 18% take rate — growth from
liquidity, not from discounting.

**The ask.** $25M Series B `[fact]`. `[open]` Valuation to be set against
current marketplace comparables — managed-marketplace multiples on net revenue,
not GMV.

**What it funds, next 18–24 months:**
1. Adjacent processes (sheet metal, molding) — same buyers and shops.
2. Shop-side financial services (faster payment, capacity financing) — deepens
   the supply side and adds revenue beyond the take rate.
3. Density in existing buyer segments — compounding the 140% NRR motion.

**Why the next round prices higher.** Each milestone retires a risk: adjacent
processes prove the engine generalizes; shop financial services prove revenue
beyond the take rate; density proves the core compounds. Risk retired × upside
ahead.

## Vision

The wedge is CNC machining. The category: **Forgeline as the demand layer for
custom manufacturing** — any process, any part, one accountable marketplace.
Win machining completely enough to be the obvious default, and the same engine —
instant quote, vetted supply, accountable delivery — extends to every adjacent
process.

## Anticipated investor questions

**1. What stops shops and buyers multi-homing?** A real risk. Mitigants:
accumulated part history and reorder flow create switching cost; density gives
the fastest quotes and best capacity. Forgeline does not assume exclusivity — it
earns the default-destination position. `[open]` Multi-homing rates should be
diligenced.

**2. 140% NRR — what is gross retention?** Net figure; gross retention and
whether expansion is concentrated are not in the inputs and are the first
diligence pull.

**3. Is the 18% take rate durable?** It is the value of removing days of
sourcing and the coordination risk. Competitive pressure could compress it;
shop-side financial services add revenue that does not depend on the take rate.

**4. 35% gross margin is thin.** Normal for a *managed* marketplace that owns
quality and delivery. The question is the path of margin as volume scales — a
diligence item for the financial model.

> Annotation: the sharpest objections, each answered directly; open items
> repeated honestly rather than smoothed over. Objections also appear inside the
> body sections — the Q&A collects the sharpest, it does not replace them.

---

## How to read this example

- The **spine** (why now / why us / why this / why this price) is visible in the
  section order — it is not a separate section, it *is* the structure.
- Every material number carries an **evidence tag**; `[open]` items are named as
  diligence questions, never invented.
- **Opportunity** (Market) and **durability** (Competition & moat) are kept in
  separate sections — the story argues the size of the prize *and* the reason
  the company keeps it.
- Strategy frameworks (marketplace flywheel, network effects, Aggregation
  Theory, switching costs) are named and tied to evidence, with the honest risk
  stated — see `strategy-frameworks.md`.
- The **contrarian core** (highlight 1) states in one plain sentence the belief
  the thesis bets against; the **carry-home** compresses the whole thesis to one
  repeatable line. Load-bearing numbers appear next to a benchmark, not naked —
  see `narrative-craft.md`.
- This example is Series B and US; for IPO/public-market framing see
  `stage-playbooks.md`, and for a Japanese IPO see `japan-ipo.md`.
