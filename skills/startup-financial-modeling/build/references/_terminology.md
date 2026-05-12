# Terminology

- `Economic kernel`: the generic set of drivers, engines, capital flows, and
  outputs that explains how the startup turns activity into cash, ownership,
  valuation, and risk.
- `Model grain`: the time resolution used by the workbook: annual, quarterly,
  monthly, or mixed, with explicit fiscal-year convention.
- `Driver tree`: the dependency map from operational primitives to revenue,
  cost, cash, capital needs, ownership, and valuation.
- `Operating engine`: the formulas that convert customers, units, usage,
  conversion, retention, utilization, and price into revenue and gross profit.
- `Cost engine`: the formulas that connect headcount, activity, variable cost,
  fixed cost, commissions, support, R&D, G&A, and delivery cost.
- `Asset engine`: the logic for capex, depreciation, leases, inventory,
  deployed assets, manufacturing cost, and utilization.
- `Working-capital engine`: the logic for receivables, payables, deferred
  revenue, inventory, customer advances, tax timing, and cash conversion.
- `Capital stack`: equity, convertibles, venture debt, leases, grants, customer
  advances, debt instruments, warrants, covenants, and cash sources/uses.
- `Ownership waterfall`: founder, employee, investor, convertible, warrant,
  option-pool, secondary, and exit ownership traced across transactions.
- `Scenario`: a coherent set of assumptions such as base, downside, upside,
  break-even, debt case, dilution case, exit case, or delayed-launch case.
- `Sensitivity`: one- or two-variable movement around a scenario that shows the
  value, runway, cash, dilution, or covenant impact of key assumptions.
- `Valuation`: DCF, exit multiple, revenue multiple, gross-profit multiple,
  comparables, SOTP, M&A proceeds, IPO-support analysis, or investor return
  logic.
- `Source fact`: a value directly provided by the user or cited source.
- `Selected assumption`: a modeler-entered estimate, placeholder,
  interpolation, management target, or scenario choice used by downstream
  formulas. Label assumptions separately from source facts.
- `Explanatory driver`: an independent primitive that makes a selected
  assumption plausible, such as funnel volume, conversion, workload, cost
  stack, capacity, timing, or financing terms.
- `Constraint / check`: a formula that compares selected and implied values or
  tests capacity, cash, covenant, ownership, valuation, or support coverage.
- `Dependent formula`: an output calculated from source facts, selected
  assumptions, and explanatory drivers. It is a consequence, not evidence for
  the assumptions that create it.
- `Decision output`: a metric, scenario result, valuation, memo point, or DD
  question that changes a pricing, financing, hiring, valuation, ownership, or
  investment decision.
