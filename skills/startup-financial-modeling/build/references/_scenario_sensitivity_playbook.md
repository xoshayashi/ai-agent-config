# Scenario and Sensitivity Playbook

Scenario and sensitivity work should make uncertainty actionable. It should not
be a cosmetic downside/base/upside table with unrelated scalar changes.

## Scenario Construction

A scenario is a coherent story about how drivers move together. Build each case
from a named cause, driver changes, financial outputs, and decision impact.

Scenario cases can include:

- delayed launch or milestone slip;
- slower conversion or weaker demand quality;
- lower price, take rate, attach rate, or utilization;
- higher COGS, support load, BOM, warranty, cloud, or implementation cost;
- slower collections, higher inventory, lower customer advances, or tighter AP;
- hiring bottleneck, productivity miss, or deployment capacity constraint;
- financing market closure, lower debt/lease capacity, or worse round terms;
- regulatory delay, clinical/trial delay, credit loss, fraud/loss, or churn.

Do not shock every line independently. If demand falls, revenue, support load,
working capital, runway, financing need, valuation, and ownership should move
through formulas unless a specific management action offsets the shock.

## Sensitivity Selection

Choose sensitivity axes from high-impact and high-uncertainty drivers:

- drivers with weak evidence;
- drivers with high effect on cash, runway, ownership, valuation, or covenants;
- drivers investors are likely to diligence;
- drivers management can actually influence;
- drivers whose downside breaks the funding plan.

Every sensitivity matrix should state:

- why the row and column variables were chosen;
- which scenario it is anchored to;
- which output it pressures;
- what decision changes when the result crosses a threshold.

## Artifact Schema

For scenario and sensitivity surfaces, include enough metadata for the reader to
understand the judgment:

| Field | Purpose |
|---|---|
| Case or matrix | Name of the case or sensitivity view |
| Cause | Operating or financing reason the case exists |
| Linked driver changes | The assumptions changed together |
| Formula-linked outputs | Cash, margin, valuation, ownership, covenant, or KPI outputs |
| Breakpoint | Threshold where the decision changes |
| Decision implication | What management or investor should do differently |
| DD action | Evidence needed to confirm or retire the risk |

If a workbook helper uses a generic starter case, rewrite or annotate the case
so it maps to evidenced drivers before presenting it as decision support.

Avoid mechanically using volume x price for every model. A pricing decision may
need price x churn, a runway decision may need burn x financing timing, a debt
decision may need EBITDA x covenant headroom, and a hardware model may need
BOM x deployment utilization.

## Mechanic-Aware Axes

Choose axes from the actual economic unit and weakest evidence, not the company
label:

- recurring contract: conversion, ACV/expansion, churn/retention, CAC or sales
  capacity;
- marketplace / transaction: GMV liquidity, take rate, incentives/fraud, repeat
  behavior, settlement or working-capital timing;
- asset / hardware: deployment capacity, utilization, BOM/service cost, capex,
  warranty, lease/debt availability;
- balance-sheet / fintech: origination, loss/collection, funding cost, warehouse
  headroom, regulatory capital;
- proof-before-revenue: milestone timing, prototype or trial cost, grant/advance
  coverage, hiring capacity.

When a workbook helper emits starter cases, rename and annotate the axes so the
reader sees which evidenced weakness each case is pressuring.

## Breakpoints

Where possible, calculate or explain breakpoints:

- minimum price or take rate to reach target margin;
- minimum units/customers to cover fixed cost;
- maximum burn before target runway breaks;
- maximum capex or working-capital drag before funding gap appears;
- valuation or round-size threshold where founder/investor ownership becomes
  unacceptable;
- covenant or liquidity threshold that blocks debt capacity.

Breakpoints are often more decision-useful than a large grid of numbers.

## Output Linkage

Scenario and sensitivity sheets should feed the IC memo. The memo should name
the downside trigger, the metric that shows it, and the action or diligence
needed before relying on the plan.
