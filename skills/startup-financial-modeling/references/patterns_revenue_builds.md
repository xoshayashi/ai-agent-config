# Revenue-Build Pattern Catalog (Driver-Tree Reference)

Conventions: **[I]** = input assumption, **[C]** = calculated row. Rows listed in top-down calculation order. Every archetype block ends with archetype-specific quality checks; cross-cutting rules at the bottom apply to all.

## 1. Subscription / Recurring (B2B & B2C)
Rollforward per segment (Janz's elephant/deer/rabbit/mouse ARPA tiers — segment when ARPA differs >5x: [Five Ways to Build a $100M Business](https://christophjanz.blogspot.com/2014/10/five-ways-to-build-100-million-business.html)):
1. Opening customers **[C]** (= prior closing; Y1 opening [I])
2. New customers **[I]** (or [C] from GTM funnel: leads × conversion, or reps × productivity)
3. Churned customers **[C]** = opening × churn rate **[I]** (never applied to same-period new adds)
4. Closing customers **[C]**; Average customers **[C]** = (open+close)/2
5. ARPA **[I]** (starting) with expansion/uplift % **[I]** → effective ARPA **[C]**
6. New/Expansion/Contraction/Churned MRR (or ARR) **[C]** → Ending ARR **[C]** (waterfall: [WSP ARR](https://www.wallstreetprep.com/knowledge/annual-recurring-revenue-arr/), [WSP MRR](https://www.wallstreetprep.com/knowledge/monthly-recurring-revenue-mrr/))
7. Recognized revenue **[C]** = average ARR/12 per month (mid-period convention), NOT ending ARR
8. Billings **[C]** = revenue + Δdeferred revenue, driven by billing-frequency mix [I] ([Chargebee bookings/billings/revenue](https://www.chargebee.com/blog/bookings-vs-billings-vs-revenue/)) — feeds cash, not P&L
- Checks: (a) implied NRR **[C]** = (open + expansion − contraction − churn)/open; flag >120% B2B or >100% B2C without evidence, and disclose GRR alongside so upsells don't mask logo churn ([Gainsight NRR](https://www.gainsight.com/blog/net-revenue-retention/), KeyBanc private-SaaS median ~109%). (b) Ending ARR ≠ next-year revenue — revenue must lag ARR when growing ([WSO ARR-to-revenue](https://www.wallstreetoasis.com/forum/private-equity/saas-modeling-arr-to-revenue)).

## 2. Usage / Consumption-Based
1. Customer rollforward **[C]** (same as #1) split committed vs on-demand **[I]** mix
2. Consumption units per customer per period **[C]** = starting usage [I] × cohort ramp curve [I] (new cohorts start low and ramp over 6–18 months; usage precedes commitment — [Mostly Metrics on Snowflake](https://www.mostlymetrics.com/p/how-snowflake-forecasts-consumption-based-revenue))
3. Rate per unit **[I]** (committed discount vs on-demand list — [Revefi Snowflake pricing](https://www.revefi.com/blog/snowflake-consumption-based-pricing-model))
4. Consumption revenue **[C]** = units × rate; recognized as consumed, not as billed
5. Subscription floor / minimum commit **[C]** = MAX(consumption, committed floor) when contracts have minimums
6. Commitment drawdown / RPO **[C]** — track pre-purchased capacity balance separately from revenue
- Checks: (a) recognized revenue ≤ commitments + on-demand; do not forecast revenue from bookings/RPO directly — Snowflake explicitly discloses RPO "not indicative" of consumption timing ([Snowflake 8-K](https://www.sec.gov/Archives/edgar/data/1640147/000164014722000078/fy2023q2earnings.htm)). (b) implied NRR from usage growth must be decomposed (customers × usage/customer × rate) — rate cuts hiding in volume growth is the classic error.

## 3. Marketplace / Platform
1. Active buyers **[C]** = rollforward (new [I], repeat retention % [I]) — or supplier-led: suppliers × listings × sell-through [I] when supply-constrained
2. Orders **[C]** = buyers × purchase frequency **[I]**
3. AOV **[I]** → GMV **[C]** = orders × AOV ([Lenny's marketplace metrics](https://www.lennysnewsletter.com/p/the-most-important-marketplace-metrics), [a16z 13 metrics](https://a16z.com/13-metrics-for-marketplace-companies/))
4. Take rate **[I]** → Net revenue **[C]** = GMV × take rate (agent presentation; gross only if principal — see cross-cutting)
5. Other revenue **[C]** (ads/subscriptions/shipping) as separate lines, never blended into take rate
- Checks: (a) take-rate trajectory vs value provided — Gurley: high rakes drive disintermediation; a16z Marketplace 100 median ~15% ([A Rake Too Far](https://abovethecrowd.com/2013/04/18/a-rake-too-far-optimal-platformpricing-strategy/)). (b) show liquidity/supply feasibility: implied GMV per supplier and match/utilization rate must stay plausible; also GMV retention by buyer cohort ([a16z GMV retention](https://a16z.com/gmv-retention-the-marketplace-metric-most-ignore/)).

## 4. Transactional / Payments
1. Active merchants/accounts **[C]** = rollforward
2. TPV per account **[I→C]** = transactions × average transaction size, with same-store TPV growth [I]
3. TPV **[C]**; Gross take rate **[I]** → Gross revenue **[C]** = TPV × take rate ([WSP take rate](https://www.wallstreetprep.com/knowledge/take-rate/), [Stripe TPV](https://stripe.com/resources/more/total-payment-value-tpv-what-it-means-why-it-matters-and-how-to-use-it-wisely))
4. Processing costs **[C]** = TPV × (interchange + assessment + processor) bps **[I]** — model in COGS, not netted, unless agent
5. Net revenue **[C]**; Net take rate **[C]** = net revenue / TPV (payfac healthy range ~0.2–3% of TPV depending on rail/merchant size)
- Checks: (a) net take rate is the honest row — flag models where gross take rate is constant while merchant mix shifts to enterprise (take rates compress with size). (b) revenue growth should not exceed TPV growth without an explicit pricing/mix driver row.

## 5. Unit Sales (Hardware / DTC)
1. Units sold **[C]** by channel (DTC [I from traffic × conversion], retail/distributor [I from doors × sell-through])
2. ASP **[C]** = Σ(channel price [I] net of channel discount [I] × channel mix % [I]) ([Building Hardware model guide](https://buildinghardware.substack.com/p/financial-model-for-physical-products))
3. Hardware revenue **[C]** = units × ASP, with recognition on shipment/delivery (lag from order [I])
4. Attach-rate add-ons **[C]** = units × attach % [I] × add-on price [I] (accessories, warranties, consumables — consumables need an installed-base rollforward)
5. COGS/unit **[C]** = BOM + assembly + logistics + warranty [I], with cost-down curve [I] (% reduction per volume doubling or per year) — a credible curve is a core pitch asset
- Checks: (a) gross margin band sanity: consumer hardware ~25–45%, B2B 40–60%; a model jumping to software-like margins needs an explicit cost-down justification. (b) channel-mix consistency — ASP, CAC, and working capital must all move with the same mix assumption (retail = lower ASP but no CAC; DTC = higher ASP + ad spend + inventory).

## 6. Professional Services
1. Billable headcount **[C]** = hiring plan [I] with ramp weighting [I]
2. Available hours **[C]** = headcount × hours/period [I]
3. Utilization % **[I]** → Billable hours **[C]** (target 70–80%; >80% sustained = burnout flag — [Kantata benchmarks](https://www.kantata.com/blog/article/professional-services-utilization-benchmarks))
4. Bill rate **[I]** × realization % **[I]** → Revenue **[C]** = headcount × utilization × rate ([Ruddr utilization](https://www.ruddr.com/post/the-critical-importance-of-utilization-tracking-for-professional-services-firms))
5. Backlog rollforward **[C]** = opening + bookings [I] − revenue recognized; revenue capped by MIN(capacity, backlog conversion)
- Checks: (a) revenue is supply-capped — any period where modeled revenue > billable hours × rate is an error, not upside. (b) backlog coverage (backlog ÷ next-period revenue) should stay ≥ ~1x; growth without bookings growth is fictional.

## 7. Advertising / Media
1. Users **[C]** = MAU/DAU rollforward (new [I], retention curve [I])
2. Engagement **[I]** = sessions × time or pageviews per user
3. Ad impressions **[C]** = users × engagement × ad load [I] (impressions per session/DAU — [Unity ads metrics](https://support.unity.com/hc/en-us/articles/14315398301332-What-do-the-following-fields-Ads-Revenue-Impressions-eCPM-Fill-Rate-Impression-DAU-mean-in-the-UnityAds-reporting))
4. Monetized impressions **[C]** = impressions × fill rate [I]
5. Revenue **[C]** = monetized impressions / 1,000 × eCPM [I], with seasonality (Q4 CPMs up to ~3x Q1 — [AdPushup](https://www.adpushup.com/blog/ad-metrics/))
- Checks: (a) ad load ceiling — flag ad load growth as the dominant driver (UX-destructive); user/engagement growth should carry the build. (b) eCPM must be benchmarked by format/geo; blended eCPM rising while mix shifts to lower-value geos is inconsistent.

## 8. Hybrid / Multi-Stream (hardware+SaaS, license+maintenance)
Structure: one block per stream, linked by attach and installed base — never a single blended line.
1. Anchor stream **[C]** (hardware units or license deals) per archetype #5 / #1
2. Installed base rollforward **[C]** = opening + new units − retirements
3. Attach: subscription adds **[C]** = new units × attach rate [I] (attach varies by SKU — Peloton discloses attach and subscriber count separately, subscriptions now ~65% of revenue at >70% GM vs low hardware GM: [Business of Apps Peloton](https://www.businessofapps.com/data/peloton-statistics/)); attached subs then follow archetype #1 rollforward with their own churn
4. License+maintenance variant: maintenance **[C]** = installed license base × maintenance % of license price [I] (typ. 18–22%) × renewal rate [I]
5. Mix disclosure rows **[C]**: revenue % by stream, blended gross margin bridged from per-stream margins
- Checks: (a) recurring stream must reconcile to installed base × attach × ARPU — subscriptions can't outgrow the base that feeds them. (b) blended gross margin must move mechanically with mix; a fixed blended margin with shifting mix is a wiring bug.

## Cross-Cutting Rules (apply to every build)
- **Recognition basis disclosure.** Every model states which basis each row is on: bookings vs billings vs recognized revenue vs ARR, and carries deferred revenue as the bridge (billings = revenue + Δdeferred — [NetSuite](https://www.netsuite.com/portal/resource/articles/accounting/bookings-model.shtml), [BIWS](https://breakingintowallstreet.com/kb/venture-capital/saas-accounting/)). P&L uses recognized revenue only; cash uses billings.
- **Gross/net decision (principal vs agent, ASC 606).** Decide once per stream via control test (fulfillment responsibility, inventory risk, pricing discretion): principal → gross revenue + fulfillment in COGS; agent → net fee only ([RevenueHub](https://www.revenuehub.org/article/principalagent-considerations-gross-vs-net), [PwC Viewpoint 10.1](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/revenue_from_contrac/revenue_from_contrac_US/chapter_10_principa_US/10_1_chapter_overview_US.html)). Always show GMV/TPV as a memo row regardless of presentation.
- **Capacity reality check (row, not driver).** Alongside the demand-driven build, compute implied GTM capacity: ramped reps × attainment-adjusted quota (weight ramping hires 25–75%, use historical attainment not 100% — [Forecastio](https://forecastio.ai/blog/top-down-vs-bottom-up-forecasting)). New ARR required by the build must be ≤ this capacity; if the build is instead capacity-driven, run demand as the check.
- **Top-down TAM pairing.** Bottom-up is the forecast; top-down is the sanity check: compute implied market share each year and flag implausible share trajectories or >15% divergence between approaches ([Finro](https://www.finrofca.com/news/top-down-vs-bottom-up-revenue-modeling-which-is-right-for-your-startup), [financial-modeling.com](https://www.financial-modeling.com/revenue-model-excel-bottom-up-top-down/)).
- **Cohort vs aggregate.** Aggregate rollforward is acceptable at plan stage when churn/ARPA are roughly homogeneous and horizon is annual; switch to cohort layers when (i) retention is strongly tenure-dependent (consumer subs, usage ramps), (ii) NRR is a headline claim, or (iii) monthly seat/usage ramps materially shift in-year revenue ([Mosaic revenue forecasting](https://www.mosaic.tech/financial-model/revenue-forecasting), [Maxio MRR cohorts](https://www.maxio.com/saaspedia/mrr-cohort)). Minimum viable middle ground: separate "existing base" vs "new business" layers even in aggregate models.
- **Universal wiring checks.** Rollforward integrity (closing = opening + adds − losses, every stream, every period); churn applied to opening base only; revenue uses average not ending balances; every [I] has a benchmark citation or historical anchor; no driver grows purely by "% growth" without a physical decomposition.
