# Eval Scenario: Earnings Deck, Clean-Base Generation

For each iteration, use only this prompt to write `deck.json` from scratch. Then run the full
pipeline: validate -> build -> verify -> render -> lint_render -> eval_deck.py.

Do not edit a previous iteration's `deck.json`; the purpose is to measure the skill's current
generation quality.

## Input Prompt

Create a 10-12 slide Japanese earnings presentation for the fictional listed cloud HR SaaS
company WorkFlow Inc. The audience is institutional investors and analysts.

Use only the following facts and numbers:

- Q2 revenue: JPY 3.24bn, YoY +28%; subscription revenue: JPY 2.98bn, YoY +31%.
- ARR: JPY 12.8bn, YoY +30%, QoQ +JPY 0.85bn.
- Paid customers: 8,420, YoY +18%; ARPA: JPY 1.52mn, YoY +10%.
- NRR: 114%, prior-year period 111%; gross churn rate: annualized 3.2%.
- Adjusted operating profit: JPY 0.21bn, prior-year period JPY -0.18bn, turned profitable;
  adjusted operating margin: 6.5%.
- Gross margin: 78%, prior-year period 76%.
- S&M expense ratio: 42%, prior-year period 48%; R&D expense ratio: 18%.
- FY2026 full-year guidance: revenue JPY 13.2-13.6bn, YoY +26-30%; Q2 progress rate: 48%.
- Medium-term policy: target ARR JPY 25.0bn and adjusted operating margin 15% in FY2028.
- Growth strategy:
  1. enterprise migration: 42 new accounts with 1,000+ employees in Q2; cumulative 380.
  2. launch a third module, Talent Management, in Q3 after attendance and payroll modules.
  3. sales through labor-and-social-security attorney partners expanded to 35% of new sales.
- ARR quarterly trend in JPY bn: Q2/25 9.85 -> Q3/25 10.52 -> Q4/25 11.28 -> Q1/26 11.95
  -> Q2/26 12.80. These are the latest five quarters. YoY +30% = 12.80 / 9.85. QoQ
  +JPY 0.85bn = 12.80 - 11.95.
- Definition of adjusted operating profit: operating profit + share-based compensation
  expense + temporary M&A-related expenses.

