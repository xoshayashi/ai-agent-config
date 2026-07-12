# Generic Composition Protocol

The skill should compose a finance artifact from the user's decision and the
model's economic dependencies. It should not begin by assigning the company to a
fixed stage, sector, or fundraising-purpose template.

## Composition Order

Use this order before deciding workbook sheets, metrics, or visuals:

1. Define the decision, user, horizon, currency, grain, entity scope, and source
   boundary.
2. Extract source facts, management claims, estimates, placeholders, and
   unknowns.
3. Identify the economic unit or units that create value.
4. Build candidate driver families across demand, monetization, delivery,
   capacity, capital, ownership, valuation, and evidence.
5. Select the drivers that matter because of decision relevance, financial
   impact, evidence weakness, controllability, time variability, or investor
   scrutiny.
6. Add only the output surfaces needed to make the selected drivers auditable.

Examples in this skill are pattern prompts. They are not defaults. A future
agent should treat SaaS, marketplace, hardware, fintech, deeptech, service,
consumer, bio, climate, real-estate, infrastructure, and AI-native companies as
different combinations of the same economic primitives, not as separate rigid
templates.

## Decision-Led Composition Rules

- Choose tabs, KPIs, scenarios, valuation methods, colors, and cell positions
  from the decision, driver tree, and audit need.
- Add metrics that change a decision, validate a driver, explain a risk, or
  support an investor / operator conversation.
- Treat maturity labels such as seed, growth, or pre-IPO as evidence about
  uncertainty, proof, financing need, and expected diligence depth.
- Map sector examples back to their underlying economic primitives before
  reusing them.
- Let workbook layout express the hierarchy created by the model logic; keep
  business-mechanic decisions in the economic kernel and prompt reasoning.

## Genericity Check

Before finalizing the artifact, ask:

- Could the same instruction work for a different business mechanic after
  changing only the driver primitives?
- Are examples clearly examples, not hidden defaults?
- Are fixed sheet names, cell addresses, colors, or metrics used only where the
  workbook contract requires them?
- Does the model omit irrelevant surfaces while preserving dependency closure?
- Can the user trace each important output back to source facts, selected
  assumptions, explanatory drivers, formulas, and checks?
