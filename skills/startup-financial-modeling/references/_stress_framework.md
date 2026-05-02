---
name: stress_framework
description: Stress test / Tail scenario / Cross-domain logic gap の正本。Recession, concentration loss, regulation shock, black swan の各 scenario 設計と、Equity ↔ Debt ↔ Tax 横断の影響伝播ロジック。監査 C-C-067..078 の解消。
type: reference
priority: P0
---

# Stress Framework — Cross-domain Logic & Tail Scenarios

このドキュメントは、財務モデルの **Stress / Tail シナリオ設計** と **Equity / Debt / Tax の cross-domain 影響伝播** の正本 (Single Source of Truth)。Reference 群 (00-14) の各 file はそれぞれの domain 内の mechanics を扱うが、**ドメイン横断の logic gap** は本書を canonical とする。

監査対応:
- C-C-067..071 (Cross-domain logic gap): §1
- C-C-072..074 (業態別 metric mismatch): §4.1
- C-C-075..078 (Stress / Tail scenario 仕様): §2

## 0. 使い方

- `scripts/build_model.py` の `build_stress_scenarios()` から正本として参照される。
- 個別 mechanics 詳細は各 reference へ back-reference (各節先頭に明示)。
- 数値水準 (e.g., recession で revenue -30%) は調整可能 parameter として `15_input_schema.md` の `stress_overrides` セクションに紐付ける想定。

## 目次

- §1 Cross-domain 影響 (Equity ↔ Debt ↔ Tax)
- §2 Stress / Tail シナリオ
- §3 Stress Test 実装
- §4 業態別 / Stage 別 applicability
- §5 数値例 mini case

---

## 1. Cross-domain 影響 (Equity ↔ Debt ↔ Tax)

> **SSoT 範囲**: 本節は cross-domain (2 つ以上の domain にまたがる) 影響伝播ロジックを扱う。各 domain 内部の単独 mechanics は以下を参照:
> - Equity: `04a_convertible_and_terms.md`, `04b_cap_table_mechanics.md`, `05_valuation_wacc.md`
> - Debt: `11_debt_financing.md`
> - Tax: `12_tax_strategy.md`
> - IPO: `14_ipo_readiness.md`

### 1.1 Equity round 後の Debt covenant 影響 (C-C-067)

**Back-reference**: `11_debt_financing.md` §3 (covenant 定義), §4 (credit metrics); `04b_cap_table_mechanics.md` §3 (Series 構造).

#### 1.1.1 Trigger 条件

Equity round (Series A/B/C/...) のクロージング直後、以下の covenant は数値変動を起こす:

| Covenant | 母数変動 | 方向性 |
|---|---|---|
| Leverage Ratio (Net Debt / EBITDA) | EBITDA 変化なし、Net Debt は cash 増 → Net Debt **減** | 数値 **改善** |
| Debt / Equity Ratio | Equity 分母増 | 数値 **改善** |
| Min Liquidity (Cash floor) | Cash 増 | 緩和余地拡大 |
| Fixed Charge Coverage Ratio | EBITDA 変化なし、debt service 同 | 不変 |
| **Incurrence Covenant** (新規借入時の追加 debt 制限) | Permitted debt basket は通常 EBITDA や Total Cap の % で定義 | basket 拡大可能 |

#### 1.1.2 Restricted Payments (RP) trigger

- Equity round の proceeds で **dividend / 自己株式取得 / Subordinated debt prepay** を実行すると RP covenant 抵触リスク。
- 典型的 RP basket: $5M build-up basket + 50% of consolidated net income from baseline date。
- Equity proceeds は通常 RP basket とは別枠で **proceeds basket** として使用可能だが、specific use clause (e.g., "for working capital only") が紐付けば prepay 不可。

#### 1.1.3 Negative Covenant の動的再評価

- Equity round 後、investor (新規 lead) は side letter で additional debt 制限を求めるケースあり (Pro rata 維持目的)。
- Lender 側は equity round を welcome するが、Change of Control 条項に抵触しないよう投資家 ownership を継続監視。

#### 1.1.4 数値感応度 (Series B 後の例)

| Pre-Series B | Post-Series B | 変動 |
|---|---|---|
| Cash $5M, Debt $20M, EBITDA -$2M | Cash $25M, Debt $20M, EBITDA -$2M | Net Debt $15M → -$5M |
| Leverage Ratio: N/A (EBITDA <0) | Leverage Ratio: N/A | 不変 |
| Min Liquidity (covenant: Cash > $3M) | Cash floor headroom 大幅拡大 | breach risk 解消 |
| Permitted Indebtedness basket: $5M | 同 (basket は equity raise で自動拡大しない契約多い) | 制限不変 |

→ **誤解しやすい点**: 「Equity 入金 = covenant 全て改善」ではない。**incurrence covenant の basket は明示的拡大条項がない限り不変**。新規 debt facility を追加するには basket 増額の amendment が必要。

### 1.2 Down round 時の Anti-dilution → Pool 拡大 → 再希薄化 cascade (C-C-068)

**Back-reference**: `04a_convertible_and_terms.md` §3 (Anti-dilution); `04b_cap_table_mechanics.md` §5 (Option Pool).

#### 1.2.1 Trigger 順序 (4 段階)

1. **Trigger event**: Down round (新規 round price < 既存 preferred の conversion price)
2. **Anti-dilution conversion ratio 変動**: 既存 preferred の conversion price 引き下げ → 既存 preferred の as-converted 株数増加
3. **Option Pool refresh**: 新 lead investor 要求で post-money option pool % を再充当 → pool 拡大は通常 pre-money で吸収 → 既存 株主希薄化
4. **再希薄化 cascade**: pool 拡大による既存 preferred 持分低下 → SAFE / Note の MFN clause で更に低い cap に再 mark → 二次的 down 効果

#### 1.2.2 Anti-dilution 式 (Broad-based Weighted Average)

```
NCP = OCP × (A + B) / (A + C)

NCP : New Conversion Price (after adjustment)
OCP : Old Conversion Price
A   : Outstanding shares (fully-diluted) prior to new issuance
B   : Shares that would have been issued at OCP for new issuance proceeds
C   : Actual shares issued in down round
```

#### 1.2.3 創業者持分の 2 段階低下計算

| 段階 | 計算ステップ | 創業者持分への影響 |
|---|---|---|
| Step 0 (pre-down round) | Founders 40%, Preferred 30%, Pool 20%, Other 10% | 40% (baseline) |
| Step 1 (down round 完了 + AD 適用前) | New money issuance のみ反映 | 32% (希薄化 -8pt) |
| Step 2 (Anti-dilution conversion) | 既存 preferred の conversion ratio 上昇 | 30% (-2pt) |
| Step 3 (Pool refresh) | Post-money pool 拡大分を pre-money で吸収 | 27% (-3pt) |
| Step 4 (MFN cascade on existing SAFEs) | Existing uncapped SAFEs re-marked to new low cap | 25% (-2pt) |

→ **Net effect**: Down round 単独 -8pt → Cascade 込み **-15pt** (1.875 倍)。

#### 1.2.4 Full Ratchet との比較

- Full Ratchet (extreme protective): conversion price = new round price (即下げ)。創業者持分 -25pt 規模に拡大。
- Broad-based weighted average (標準): 上記計算式。実務では 95% 以上の VC term sheet で採用。
- Narrow-based weighted average: only common stock を A に算入 → AD 効果が大きい。

#### 1.2.5 Pay-to-play との相互作用

- Down round 時、既存 preferred が pro rata 投資しない場合 **pay-to-play** clause で AD protection を失う条項あり。
- 結果として、不参加投資家の持分は preferred → common 自動転換され、参加投資家の持分が相対的に保護される。

### 1.3 Tax loss carryforward 中の M&A (C-C-069)

**Back-reference**: `12_tax_strategy.md` §6 (NOL 一般), §7 (組織再編税制).

#### 1.3.1 米国: Section 382 limitation

- **Trigger**: Ownership change (5%-shareholders の cumulative ownership 変動 > 50pt over 3-year window)。
- **Effect**: Pre-change NOL の年間使用上限 = (Equity Value at change date) × (Long-term Tax-Exempt Rate)。
- **数値例**: Equity Value $50M × LTTER 4.5% = **annual NOL usage cap $2.25M**。$30M NOL の場合、消化に約 14 年。
- **Built-in gain/loss 調整**: NUBIG (Net Unrealized Built-In Gain) > $10M または 15% of asset value の場合、5 年以内の recognized gain は cap を超えて使用可。

#### 1.3.2 日本: 適格組織再編 vs 非適格

| 区分 | NOL (繰越欠損金) 引継 | 主要要件 |
|---|---|---|
| 適格合併 (グループ内) | 全額引継 (制限なし、ただし租税回避要件審査) | 完全支配関係継続、被合併法人の事業継続 |
| 適格合併 (共同事業) | 引継可だが「みなし共同事業要件」充足が必要 | 事業関連性、規模、経営参画、株式継続保有 |
| 非適格合併 | NOL **消失** | 上記要件未充足 |
| 適格分割 / 株式交換 | 一部引継 | 個別判定 |
| 適格現物出資 | 限定的 | 個別判定 |

- **特定資産譲渡等損失の損金不算入**: 適格でも、合併前 5 年以内の含み損資産は損金算入制限あり。
- **支配関係継続要件**: 5 年内の支配関係発生でない場合、NOL 引継に追加制限。

#### 1.3.3 M&A バリュエーションへの影響

```
Adjusted Enterprise Value = Standalone EV + PV(NOL utilization)

PV(NOL) = Σ_{t=1}^{T} (NOL_used_t × tax_rate) / (1 + WACC)^t

T : NOL 消化年数 (Section 382 cap または NOL expiration の早い方)
```

**数値例**: $30M NOL, US, Section 382 cap $2.25M/年, tax rate 21%, WACC 10%
- 消化年数 = 30 / 2.25 = 13.3 年
- 各年 tax shield = $2.25M × 21% = $0.4725M
- PV = $0.4725M × annuity factor(10%, 13.3yr) ≈ $3.4M

→ Buyer 側は $3.4M を valuation で credit する余地あり (ただし Section 382 limitation の確実性次第)。

#### 1.3.4 Cross-domain trigger チェックリスト

M&A 実行時の cross-domain チェック:
- [ ] Section 382 / 適格判定の事前モデリング
- [ ] Debt 側の Change of Control 条項 (acceleration trigger)
- [ ] Equity 側の drag-along / tag-along, ROFR
- [ ] Stock option の acceleration (single trigger / double trigger)
- [ ] 401(k) / 退職金税制の影響 (US: §280G excess parachute payments)

### 1.4 IPO 時の SO acceleration + Lock-up + Greenshoe (C-C-070)

**Back-reference**: `14_ipo_readiness.md` §4 (Stock Option), §5 (Lock-up & Greenshoe).

#### 1.4.1 SO acceleration trigger

| Type | 発動条件 | 加速範囲 |
|---|---|---|
| Single trigger | IPO / M&A の単独 event | Vesting schedule の残期間全部 → 即 vest |
| Double trigger | IPO / M&A + その後の termination without cause | 1st event 時点では vest 加速なし。2nd event で残全 vest |
| Modified single trigger | IPO / M&A + 6-12 ヶ月 employment 継続 | 部分加速 |

- 実務では IPO 単独 trigger は稀。多くは M&A + termination の double trigger。
- IPO 単独で SO 加速発動するケースは、創業者初期付与または Senior exec の特定 grant のみ。

#### 1.4.2 Lock-up と SO 行使制限

- 標準 lock-up: 180 日 (IPO 価格決定日 から)。
- Lock-up 期間中の SO 行使: 法的に禁止ではないが、引受団 (underwriter) との agreement で **行使後株式の sale 禁止**。
- Cashless exercise (sell-to-cover) は lock-up 期間中不可 → optionee は手元現金で exercise + tax 必要。
- Early lock-up release: 引受団判断で 90 日経過時点で部分解除あり (= 株価維持目的)。

#### 1.4.3 Greenshoe (Over-allotment Option) 影響

- 発行体オプション: 引受団に最大 15% の追加発行権利を付与。
- Greenshoe full exercise の場合、IPO 直後の dilution が想定 +13% 程度。
- Greenshoe stabilization: IPO 後 30 日以内に株価が下回った場合、引受団が市場で買戻し → 結果 greenshoe 部分の発行を行わず → dilution なし。

#### 1.4.4 最終キャップテーブル (IPO completion 後)

| 段階 | 流通株式数 | 創業者持分 | 備考 |
|---|---|---|---|
| Pre-IPO (S-1 filing) | 80M shares | 25% | Preferred 全 common 転換後 |
| IPO primary offering | +10M shares | 22% | 12.5% dilution |
| IPO secondary offering | +2M (existing 株式) | 22% | 創業者 sell-down 含むなら更に低下 |
| Greenshoe full exercise | +1.8M shares | 21% | 2% additional dilution |
| 6 ヶ月 lock-up 経過 | 同 | 21% | 流通量増だが持分不変 |
| SO post-IPO grant 開始 | +pool refresh | 19-20% | 通常 IPO 時に pool refresh |

#### 1.4.5 IPO 時 cross-domain 連動表

| Event | Equity 影響 | Debt 影響 | Tax 影響 |
|---|---|---|---|
| S-1 filing | 公開準備 | Debt covenant の "IPO-triggered" prepay 義務 trigger 可能 | None |
| IPO pricing | Pre-IPO valuation 確定 | Convertible note は IPO で auto-conversion (殆どの場合) | None |
| IPO completion | Preferred → Common 強制転換 | Mandatory prepayment (一部 venture debt) | SO exercise → AMT 課税対象 |
| Lock-up expiration | 創業者 sell-down 開始 | None | LT capital gain (要件: holding > 1y) |
| Post-IPO grants | New SO pool refresh | None | Section 162(m) deduction limit |

### 1.5 Bankruptcy 時の各 claim priority (C-C-071)

**Back-reference**: `11_debt_financing.md` §8 (デフォルト処理).

#### 1.5.1 Absolute Priority Rule (US Chapter 11)

優先順位 (上位から):

1. **DIP Financing** (Debtor-in-Possession): super-priority administrative claim。Chapter 11 申請後の operating capital。
2. **Administrative Claims**: 弁護士費用、courts fees、post-petition trade claims、employee wages (post-petition)。
3. **Senior Secured (1st lien)**: collateral 担保範囲内で最優先。Senior term loan 等。
4. **Senior Secured (2nd lien)**: 1st lien の余剰担保価値からの回収。
5. **Senior Unsecured**: 担保なしの senior debt (e.g., senior notes)。
6. **Subordinated Debt**: contractually subordinated。Mezz, sub notes 等。
7. **Trade Creditors (pre-petition unsecured)**: 通常の取引債権 (申請前発生)。
8. **Preferred Equity** (Liquidation Preference 適用順):
   - Series E (most recent) 1x → Series D 1x → ... → Series A 1x (通常 reverse 順)
   - Participating preferred は LP + pro rata of common pool
   - Conversion option: as-converted の方が有利な場合は common と同列
9. **Common Stock**: 残余分配 (実務ではゼロが大多数)。

#### 1.5.2 日本: 民事再生 / 会社更生

| 区分 | 民事再生 (Civil Rehabilitation) | 会社更生 (Corporate Reorganization) |
|---|---|---|
| 主導 | Debtor-in-Possession (経営陣残留) | 更生管財人選任 (経営権剥奪) |
| 担保権 | 別除権 (separate execution) - 担保実行可 | 更生担保権 - 計画内処理 |
| 期間 | 6 ヶ月-3 年 | 1-5 年 |
| 株主 | 通常 100% 減資 | 100% 減資 + 新株発行 |
| 適用ケース | 中堅企業の早期再生 | 大企業の包括的再建 |

- 担保権の取扱が日米で大きく異なる: US は automatic stay で担保実行も停止、日本民再は別除権で実行可能 (ただし管財人交渉の余地)。

#### 1.5.3 Liquidation preference の発動例

**Scenario**: Total proceeds $50M for distribution to claim holders。

| Claim | Amount | LP / 倍率 | Distribution |
|---|---|---|---|
| DIP loan | $5M | super-priority | $5M (full) |
| Admin claims | $3M | priority | $3M (full) |
| Senior secured | $25M | 1st lien | $25M (full) |
| Senior unsecured | $10M | pari passu | $10M (full) |
| Trade creditors | $4M | pari passu w/ unsecured | $4M (但しpro-rata if 不足) |
| Subtotal | $47M | | $47M |
| **Remaining** | | | **$3M** |
| Series B Preferred | $20M @ 1x LP | non-participating | min($3M, $20M) = $3M |
| Series A Preferred | $10M @ 1x LP | non-participating | $0 |
| Common (Founders + employees) | residual | | $0 |

→ Series B 投資家は $20M 投資に対し $3M 回収 (15%)。Series A と Common は **wipe out**。

#### 1.5.4 DIP Financing の super-priority 構造

- Pre-petition lender が DIP も提供する "Defensive DIP" が一般的。
- Roll-up: pre-petition senior secured を DIP に組み込み、super-priority に格上げ → 他の claim より優先。
- Adequate protection: pre-petition secured creditor の collateral 価値毀損に対する補償 (利息継続支払、追加担保等)。

---

## 2. Stress / Tail シナリオ

> **設計原則**:
> - シナリオは **independent** ではなく **correlation** を考慮 (e.g., recession で revenue 減 + funding window close は同時)。
> - 数値水準は **対 base case** (絶対値ではなく Δ) で定義 → 業態 / stage を変えても再利用可。
> - 各シナリオに **trigger condition**, **propagation path**, **survival metric** を明記。

### 2.1 Recession Scenario (C-C-075)

#### 2.1.1 Recession 定義 (本書の数値仕様)

| Driver | Δ vs Base | 持続期間 | 備考 |
|---|---|---|---|
| Revenue | **-30%** (1 quarter で発動) | 4-6 quarter | 既存契約の churn + 新規受注減 合算 |
| Gross Margin | **-500 bps** | 同 | Cost passing できない前提 |
| CAC | **+50%** | 同 | acquisition difficulty ↑ |
| Churn (gross) | **+200 bps/年** (= +0.5pt/quarter) | 同 | customer cancellation 増 |
| Funding window | **closed** (12-18 ヶ月 access なし) | 12-18 ヶ月 | VC が deployment 抑制 |
| Multiple compression | EV/Revenue **-40%** | recovery まで | exit valuation 下方修正 |

#### 2.1.2 Recession 伝播 path

```
Macro Recession (GDP -2%)
  ↓
Customer budget cut (Revenue -30%)
  ↓
Cost adjustment lag (Gross margin -500bps)
  ↓
Burn rate ↑↑ (Cash runway 短縮)
  ↓
Funding window closed → Bridge round 不可
  ↓
[Path A] Layoff + cost cut で延命 → Recovery 期に縮小再起動
[Path B] Down round (50% off) で生き残り → 創業者持分大幅希薄化
[Path C] Wind-down trigger → 静かに closing
```

#### 2.1.3 Recovery profile

- L-shape: 4-6 quarter 低位停滞 (典型 SaaS 中堅 + horizontal 広告依存)
- U-shape: 6-9 quarter で gradual recovery (B2B mid-market)
- V-shape: 2-3 quarter で急回復 (essential services, defense tech)
- W-shape: double dip (financial crisis + secondary shock の場合)

### 2.2 Customer Concentration Loss (C-C-076)

#### 2.2.1 Top customer (15-30% revenue) 喪失

| Driver | Δ |
|---|---|
| Revenue (immediate) | -15% to -30% (1 quarter で発動) |
| AR write-down | up to outstanding receivable |
| Gross margin | mild improvement (大口は通常 discount) |
| CAC payback (replace 必要) | 12-24 ヶ月分の new sales 必要 |
| Bank covenant | leverage / coverage 急悪化 → breach risk |

#### 2.2.2 Top 5 customers 同時喪失 (45-60% revenue)

- 連鎖 churn: 「○○社が解約した」の悪い噂で snowball。
- 業界誌、Reddit, Glassdoor で negative signal が拡散。
- Sales pipeline coverage 急減 (1 ratio → 0.3)。

#### 2.2.3 Concentration metrics

```
Herfindahl-Hirschman Index (HHI) for customer concentration
  HHI = Σ_i (revenue_share_i)^2

  HHI < 1500: 健全 (top 5 < 30% combined)
  HHI 1500-2500: 注意
  HHI > 2500: 集中度高 (top 1 > 50% 等)

Customer-level value at risk (CVaR_5%)
  = expected loss in worst 5% of customer churn scenarios
```

#### 2.2.4 業態別 trigger 水準

| 業態 | Top 1 として警戒水準 | Top 5 合計警戒水準 |
|---|---|---|
| Enterprise SaaS | 15% | 50% |
| Marketplace (GMV) | 25% | 60% |
| Agency / Services | 20% | 55% |
| Manufacturing (B2B) | 30% | 70% |
| DTC (consumer) | 5% | 20% |

### 2.3 Regulatory Shock (C-C-077)

#### 2.3.1 Fintech: BSA/AML 強化

- KYC / AML compliance cost +50-200%。
- New customer onboarding 期間 2x。
- Per-transaction TCO 上昇 → unit economics 圧迫。
- 2023 年 Operation Choke Point 2.0 等、debanking risk。

#### 2.3.2 Bio: FDA 承認遅延

- 承認 timeline +12-24 ヶ月。
- Trial 拡大要求 → R&D budget +30-100%。
- Cash burn 延長による additional 資金調達必要。

#### 2.3.3 Cross-border 規制

| 規制 | 対象 | Impact |
|---|---|---|
| US 海外送金規制 (FinCEN) | Fintech, Crypto | Reporting threshold 引き下げ → cost 増 |
| 中国 VIE 構造制限 | China-tech | US listing 困難 → exit 経路喪失 |
| EU GDPR | All EU operations | Fine up to 4% global revenue |
| EU AI Act | AI products | High-risk system に新規制 |
| インド データローカライゼーション | Fintech, SaaS | 国内 datacenter 必須化 |

#### 2.3.4 新税制

| 制度 | 対象 | Impact |
|---|---|---|
| OECD Pillar 2 (Global Min Tax 15%) | EBT > €750M グループ | 低税率国の tax planning 不能 |
| Digital Services Tax (DST) | Tech 大手 | EU/UK で 2-7% revenue tax |
| 米 IRA (Inflation Reduction Act) | Energy/Hard tech | 補助金 vs 中国 equipment 制限 |
| 日本 賃上げ促進税制 | 国内全社 | 給与増加分 30-40% 税額控除 (positive) |

### 2.4 Black Swan (C-C-078 part 1)

#### 2.4.1 Pandemic (COVID-19 type)

- 物理 service 業: revenue -80% (1 quarter)
- E-commerce: revenue +50% (positive shock)
- B2B SaaS (essential): +20%
- Travel/hospitality: -90%
- Recovery 6-24 ヶ月 (業態依存)

#### 2.4.2 主要 supplier 破綻 (Hardware)

- 単一 supplier 依存度 > 50% の component が trigger。
- 代替 supplier qualification 6-18 ヶ月。
- Inventory write-down + production halt。
- 例: 2020-2023 半導体不足 (TSMC dependence)。

#### 2.4.3 Cybersecurity major breach

| Cost component | 想定額 |
|---|---|
| Forensic investigation | $0.5-2M |
| Customer notification | $50-200/customer |
| Regulatory fine | up to 4% global revenue (GDPR) |
| Class action settlement | $5-50M |
| Customer churn | +10-30% in next 12 months |
| Cyber insurance retention | $1-5M |
| Brand damage (intangible) | varies |

#### 2.4.4 Founder departure / health issue

- Key person clause trigger: VC は acceleration / put right を保有することがある。
- Bus factor < 2 の startup は valuation discount 20-50%。
- 後継 CEO 探索期間 6-18 ヶ月。

### 2.5 Macro (C-C-078 part 2)

#### 2.5.1 Interest rate +500bps (debt cost 急騰)

- Floating rate debt: 即時 cost +500bps。
- Fixed rate refi: refi 時に +500bps cost 上乗せ。
- Discount rate ↑ → terminal value ↓ (valuation 圧縮)。
- Multiple compression: PER 25 → 18 など。

#### 2.5.2 FX +/- 30%

| 局面 | Export 主導 | Import 主導 |
|---|---|---|
| 自国通貨安 +30% | Revenue ↑ (positive) | COGS ↑ (negative) |
| 自国通貨高 -30% | Revenue ↓ (negative) | COGS ↓ (positive) |

- Hedging cost: 通常 1-3% per annum。
- Translation effect (BS): Equity (CTA) ±10-20%。

#### 2.5.3 Inflation +10%

- Wage cost ↑ (人件費 50% 比率 → 5pt margin 圧迫)。
- 価格転嫁可能性 (B2B contract 多くは 1 年 lag)。
- Real revenue growth = Nominal growth - Inflation → 実質縮小リスク。
- Inventory FIFO/LIFO の earnings 影響 (米国: LIFO で earnings 抑圧 → tax 軽減)。

---

## 3. Stress Test 実装

### 3.1 Sensitivity Table 設計

#### 3.1.1 Top 5 driver の選定

各業態で寄与度上位 5 driver を選び、それぞれ ±20%, ±50%, ±100% で感応度を測定:

| 業態 | Driver 1 | Driver 2 | Driver 3 | Driver 4 | Driver 5 |
|---|---|---|---|---|---|
| SaaS | New ARR/月 | Gross churn | Gross margin | CAC | Pricing increase |
| Marketplace | GMV | Take rate | Active buyers | Repeat rate | Fulfillment cost |
| Hardware | Unit volume | ASP | BOM cost | Yield | Inventory days |
| Fintech | TPV | Take rate | Default rate | Fraud rate | CAC |
| Bio | Trial success | Time to approval | Reimbursement rate | COGS | Patent expiry |

#### 3.1.2 Tornado Chart 作成

```
Output metric: 24-month runway (months)

Baseline runway: 18 months

Variable           -100%      -50%      -20%   Base   +20%    +50%    +100%
New ARR/月            6        10        15      18    21      26      32
Gross churn          26        22        20      18    16      14      11
Gross margin         12        14        16      18    20      22      24
CAC                  24        21        19      18    17      15      12
Salary inflation     21        20        19      18    17       15     12

→ 寄与度 (range width) ranking:
  1. New ARR (range: 6-32, 26 months)
  2. Gross churn (range: 11-26, 15 months)
  3. Gross margin (range: 12-24, 12 months)
  4. CAC (range: 12-24, 12 months)
  5. Salary inflation (range: 12-21, 9 months)
```

### 3.2 Scenario Manager

#### 3.2.1 5 シナリオ標準セット

| Scenario | Probability (subjective) | Driver の動かし方 |
|---|---|---|
| Best | 15% | Top 3 driver +20% |
| Base | 50% | Plan as filed |
| Worst | 25% | Top 3 driver -20% |
| Stress | 8% | Recession spec (§2.1) 適用 |
| Tail | 2% | Black Swan (§2.4) 適用 |

#### 3.2.2 Path-dependent シナリオ

```
Recession Path (4 quarter of -30% revenue, then -10%, then -5%, then recovery)

Q1: Revenue -30%, Cost -5% (lag) → margin -1500bps
Q2: Revenue -30%, Cost -15% (catch-up) → margin -1000bps
Q3: Revenue -30%, Cost -25% (right-size) → margin -500bps
Q4: Revenue -10%, Cost stable → margin -200bps
Q5+: Recovery
```

#### 3.2.3 Monte Carlo 簡易版

```
For each trial t (1..1000):
  Revenue_t = Revenue_base × (1 + N(0, 0.3))  # Normal dist, σ=30%
  COGS_t    = COGS_base × (1 + N(0, 0.15))
  ...
  Cash_t12 = compute_cash_position(Revenue_t, COGS_t, ...)

Output: P(Cash_t12 < 0) = % of trials with negative cash at month 12
        P(runway < 12) = % of trials with insufficient runway
```

### 3.3 Survival Analysis

#### 3.3.1 Runway Projection across scenarios

```
Scenario      M3    M6    M9    M12   M15   M18   M21   M24
Base         100%   95%   90%   85%   75%   60%   45%   25%   ← cash %
Worst         95%   80%   65%   45%   25%   10%    0%    0%
Stress        90%   65%   40%   15%    0%    0%    0%    0%
Tail          80%   45%   15%    0%    0%    0%    0%    0%

Survival probability at M12:
  Base: cash > 0
  Worst: cash > 0 (barely)
  Stress: cash hits 0 ← Bridge round must close by M9
  Tail: cash hits 0 ← Wind-down by M9
```

#### 3.3.2 Bridge Funding 必要 timing

```
Trigger: cash runway < 6 months at any point in scenario

Action timeline (assumed Bridge round close = 4 months from trigger):
  T-6 month: 投資家接触開始
  T-4 month: Term sheet negotiation
  T-3 month: DD start
  T-1 month: Closing
  T-0: Funded

→ Stress scenario で cash runway 6m を割るのは M3 → Bridge close は M7 を target。
```

#### 3.3.3 Wind-down trigger threshold

```
Wind-down triggers (any one is sufficient):
  - Cash < 4 weeks operating expense (regardless of bridge timing)
  - Bridge round 失敗 confirmed (主要 lead pull out)
  - Key customer (> 50% revenue) 解約 + 代替不可
  - 主要規制不適合 (operating license 喪失)
  - 主要 founder 離脱 + 後継不可

Wind-down 時の意思決定 path:
  Path 1: ABC (Assignment for Benefit of Creditors) - 私的整理
  Path 2: Chapter 7 (US) / 破産 (日本) - 法的清算
  Path 3: Acqui-hire (talent + IP のみ売却)
  Path 4: Tax shell sale (NOL を持つ shell 売却)
```

---

## 4. 業態別 / Stage 別 applicability

### 4.1 業態別 metric mismatch 防止 (C-C-072..074)

#### 4.1.1 「Pre-revenue で LTV/CAC を語らない」(C-C-072)

**問題**: Pre-revenue (= 売上 0 または極小) 段階で LTV/CAC 比率を主要 KPI とする誤謬。

**根拠**:
- LTV (Lifetime Value) は **観測された** customer cohort retention curve から算出。観測歴がない段階で LTV は推定値の推定値 → 誤差幅が極大。
- CAC は paid acquisition の歴史データから算出。Pre-revenue で marketing budget が極小の段階では noisy。
- LTV/CAC > 3 を目指す指標として運用すると、人為的に CAC を低く出す operational pressure が掛かる (e.g., organic only にして LTV を不当に高く見せる)。

**正しい代替指標 (Pre-revenue)**:
- TAM × penetration assumption の sanity check
- Wait list size, beta user engagement
- Time to first $ (TTF$)
- Founder hours per customer interview
- Pilot conversion rate (paid pilot → contract)

#### 4.1.2 「Profitable 企業で Burn Multiple を見ない」(C-C-073)

**問題**: Profitable (FCF > 0) 段階の企業に Burn Multiple を主要 KPI として当てはめる誤謬。

**根拠**:
- Burn Multiple = Net Burn / Net New ARR。FCF > 0 の企業は分子 (Burn) が **負** または **0** → 比率は無意味 / 負値。
- Profitable 企業の効率性指標は **Rule of 40** (Growth% + FCF Margin%) や **EBITDA margin** が適切。

**正しい代替指標 (Profitable stage)**:
- Rule of 40 (Growth% + FCF Margin% > 40)
- EBITDA margin (target 業態別: SaaS > 25%, Marketplace > 15%)
- ROIC, ROE
- Cash conversion (FCF / Net Income)

#### 4.1.3 「IPO 後企業で SAFE 残高を考慮しない」(C-C-074)

**問題**: Post-IPO 企業の cap table 分析で SAFE / 転換社債残高を考慮する誤謬。

**根拠**:
- IPO 時に SAFE / convertible note は **強制転換** (mandatory conversion) されるのが標準。
- IPO 後の企業の outstanding は **Common + Preferred (residual ありなら) + RSU/SO unvested** のみ。
- SAFE 残高を持ち続けることは S-1 / 10-K で disclose されるが、極めて稀。
- 例外: IPO 直前に発行した bridge SAFE で converion 適用除外条項を含むもの (これも IPO 後 6 ヶ月以内に converted/cancelled される場合がほとんど)。

**正しい代替指標 (Post-IPO)**:
- Diluted shares outstanding (DSO)
- Treasury stock 残高
- Pending RSU/SO grants (vested but unexercised)
- Buyback program 残高

#### 4.1.4 業態別 metric applicability matrix

| Metric | Pre-rev | Pre-PMF | Series A | Series B-C | Pre-IPO | Post-IPO |
|---|---|---|---|---|---|---|
| LTV/CAC | NG | △ | OK | OK | OK | OK |
| Burn Multiple | NG | OK | OK | OK | △ (FCF 接近) | NG (FCF >0) |
| Rule of 40 | NG | △ | OK | OK | OK | OK |
| Magic Number | NG | △ | OK | OK | OK | OK |
| SAFE 残高 | OK | OK | OK | △ (converted) | △ | NG |
| Liquidation Preference | NG | OK | OK | OK | OK | NG |
| Diluted EPS | NG | NG | △ | △ | OK | OK |
| EV/Revenue | △ | OK | OK | OK | OK | OK |
| EV/EBITDA | NG | NG | △ | △ | OK | OK |
| P/E | NG | NG | NG | NG | △ | OK |
| FCF yield | NG | NG | NG | △ | OK | OK |
| Section 382 NOL | △ | OK | OK | OK | OK | OK |

#### 4.1.5 業態別 metric applicability

| Metric | SaaS | Marketplace | Hardware | Fintech | Bio | Consumer DTC |
|---|---|---|---|---|---|---|
| ARR / MRR | OK | NG (GMV) | NG | △ | NG | NG (revenue) |
| GMV / Take Rate | NG | OK | NG | △ | NG | △ |
| Unit Economics (BOM) | NG | NG | OK | NG | △ | OK |
| TPV | NG | △ | NG | OK | NG | NG |
| Cohort Retention | OK | OK | △ | OK | NG | OK |
| Trial success rate | NG | NG | NG | NG | OK | NG |
| Inventory turn | NG | △ | OK | NG | △ | OK |
| Default rate | NG | NG | NG | OK | NG | NG (consumer credit case のみ) |

### 4.2 Cross-domain Stage applicability

| Domain 論点 | Idea | Pre-seed | Seed | Series A | B-C | Late | Pre-IPO | Post-IPO |
|---|---|---|---|---|---|---|---|---|
| **Equity** | | | | | | | | |
| SAFE / Note | △ | OK | OK | △ | NG | NG | NG | NG |
| Priced round | NG | △ | OK | OK | OK | OK | OK | NG |
| Anti-dilution | NG | △ | OK | OK | OK | OK | OK | NG (post-conversion) |
| Pay-to-play | NG | NG | △ | OK | OK | OK | OK | NG |
| Greenshoe | NG | NG | NG | NG | NG | NG | OK | △ (secondary) |
| Lock-up | NG | NG | NG | NG | △ | △ | OK | △ (key holders) |
| **Debt** | | | | | | | | |
| Founder personal guarantee | △ | OK (公庫) | OK | △ | NG | NG | NG | NG |
| Venture Debt (Tranche A) | NG | NG | △ | OK | OK | OK | OK | NG (corporate debt) |
| Mezzanine | NG | NG | NG | NG | △ | OK | OK | OK |
| Senior Secured Term Loan | NG | NG | NG | NG | △ | OK | OK | OK |
| Bond / Public Debt | NG | NG | NG | NG | NG | NG | △ | OK |
| Multi-covenant cross-default | NG | NG | NG | △ | OK | OK | OK | OK |
| **Tax** | | | | | | | | |
| QSBS (US) eligibility | OK | OK | OK | OK | OK | △ | △ | △ |
| Section 1202 5y holding | OK | OK | OK | OK | OK | OK | OK | OK |
| NOL carryforward | △ | OK | OK | OK | OK | OK | OK | OK |
| Section 382 limit | NG | NG | △ | OK | OK | OK | OK | OK |
| Pillar 2 (Global Min Tax) | NG | NG | NG | NG | △ | OK | OK | OK |
| 適格 / 非適格 組織再編 | NG | △ | OK | OK | OK | OK | OK | OK |
| **IPO/M&A** | | | | | | | | |
| S-1 / Form F-1 | NG | NG | NG | NG | NG | △ | OK | NG |
| 適格上場 (TSE Growth) | NG | NG | NG | NG | NG | △ | OK | NG |
| 子会社上場 | NG | NG | NG | NG | NG | △ | OK | OK |
| Acqui-hire | NG | OK | OK | OK | △ | △ | NG | NG |

凡例: OK = 主要論点、△ = 状況により適用、NG = 通常該当なし。

---

## 5. 数値例 mini case

### 5.1 Recession × Marketplace × Series B (GMV -25% scenario)

**Setup**:
- Marketplace, Series B clozed 12 ヶ月前
- Pre-recession metrics: GMV $200M/年、take rate 12%、Net revenue $24M、Burn $1M/月
- Cash $20M、Runway 20 ヶ月

**Recession 適用 (本書 §2.1 spec)**:
- Revenue (= GMV × take rate) -30% → Net revenue $16.8M (-$7.2M)
- Gross margin -500bps → さらに -$1.2M
- CAC +50% → marketing 効率低下、growth 鈍化
- Funding window closed 12-18 ヶ月

**Path-dependent 計算 (4 quarter)**:

| Quarter | GMV | Net Rev | Cost (lag) | EBITDA | Cash 残 |
|---|---|---|---|---|---|
| Q0 (pre) | $50M | $6.0M | $7.0M | -$1.0M | $20.0M |
| Q1 | $35M (-30%) | $4.2M | $6.7M (-5%) | -$2.5M | $17.5M |
| Q2 | $35M | $4.2M | $5.6M (-20%) | -$1.4M | $16.1M |
| Q3 | $35M | $4.2M | $4.7M (-33%) | -$0.5M | $15.6M |
| Q4 | $40M (-20%) | $4.8M | $4.7M | $0.1M | $15.7M |
| Q5 | $42M | $5.0M | $4.7M | $0.3M | $16.0M |

**結果**:
- Recession 6 quarter で cash $20M → $16M (drawdown $4M)
- Funding window 12-18 ヶ月 closed でも生存可能
- 但し growth narrative は失われ次回 round の valuation -50% 想定 → Down round 不可避

**Key insight**: Marketplace の revenue が $7M 減でも cost cutting で延命可能。但し take rate 圧力 (cross-side fee 戦争) と repeat rate 低下が同時発生する場合は更に悪化。

### 5.2 Customer Loss × SaaS × Series A (top 1 顧客 25% 喪失)

**Setup**:
- B2B SaaS, Series A closed 6 ヶ月前
- Pre-loss: ARR $4M, top 1 customer = $1M (25%), Burn $300K/月
- Cash $8M, Runway 26 ヶ月

**Top 1 喪失適用**:

| 段階 | ARR | NRR (annual) | Burn | Bank covenant |
|---|---|---|---|---|
| Pre | $4.0M | 110% | -$300K/月 | OK |
| Post-loss (immediate) | $3.0M | NRR 計算 not meaningful 1Q | -$300K/月 | covenant ARR floor breach risk |
| +6 months | $3.3M (回復 +$300K new) | NRR 105% | -$280K (cost cut) | covenant cure period 適用中 |
| +12 months | $3.8M | NRR 100% | -$250K | OK (cure 完了) |

**Cross-domain trigger**:
- Debt covenant: Min ARR floor $3.5M に違反 → 30 day cure period 開始 → 90 日以内に new ARR で回復しないと default
- Equity 側: 投資家報告で down-rev guidance, board call 緊急開催
- Tax: 影響なし (ARR は収益認識上 monthly recognition、loss は徐々に反映)

**Bridge action**:
- M&A 発表で代替顧客探索 → 半年で $0.5-0.8M new ARR の獲得が target
- Debt waiver 交渉: lender に 1 quarter の cure 延長を要請、warrant additional 1% 提供

**Key insight**: Top 1 = 25% 喪失は Series A startup として recoverable だが、6-12 ヶ月の集中対応必要。Debt covenant の cure period が tight な場合は equity rescue (insider bridge) 並行検討。

### 5.3 Regulatory × Fintech × Pre-IPO (新規制で TPV -15%)

**Setup**:
- Fintech (payments), Pre-IPO 12 ヶ月前
- Pre-shock: TPV $10B/年, take rate 1.2%, Net revenue $120M, EBITDA $30M, S-1 filed

**規制適用 (FinCEN reporting threshold 引き下げ + KYC 強化)**:

| Driver | Δ | 影響 |
|---|---|---|
| TPV | -15% (compliance cost で merchant 流出) | -$1.5B |
| Take rate | +5bps (compliance fee 転嫁) | +$50M effect |
| Net revenue | -$120M × 15% + $50M = -$8M | $112M |
| Compliance cost (incremental) | +$15M/年 | EBITDA -$15M |
| EBITDA | $30M → $7M (-77%) | margin 25% → 6% |

**IPO 影響**:
- S-1 amendment 必要 (risk factor 追加, 業績修正)
- Roadshow 価格 -30% (multiple 圧縮 + 業績悪化)
- IPO 延期 6-12 ヶ月 検討

**Cross-domain trigger**:
- Equity: Pre-IPO 投資家の anti-dilution clause で valuation step-down 警戒
- Debt: 規制 license 維持を financial covenant に組込まれている case (e.g., minimum compliance score 維持)
- Tax: 規制対応費用は通常 deductible だが、罰金は non-deductible

**Path**:
- Path A: IPO 強行 (低 valuation でも上場優先)
- Path B: IPO 延期 + 規制完全対応 → 2 年後に再 file
- Path C: M&A (戦略的売却で大手 fintech へ 統合)

**Key insight**: Pre-IPO の規制 shock は valuation を 30-50% 押し下げる典型。S-1 タイミングと規制 effective date の調整が critical。

### 5.4 Founder × Bio × Phase 2 (主要 founder 退任)

**Setup**:
- Bio (oncology), Phase 2 trial 進行中
- Pre-event: Cash $40M, Burn $4M/月 (R&D heavy), Phase 2 readout 6 ヶ月後
- Lead PI = 共同 founder = CSO

**Founder 退任 (健康問題で immediate departure)**:

| 領域 | Impact |
|---|---|
| Trial 進行 | Phase 2 PI 交代 → IRB 再承認手続 (3 ヶ月) → readout 9 ヶ月後にずれ |
| Investor confidence | Series C 追加調達 difficulty。既存投資家の bridge 要請 |
| Key person clause | VC が put right を発動可能 (但し公的義務 vs 投資家関係で実務は negotiation) |
| Recruitment | 後継 CSO 探索 9-12 ヶ月。Reputation のある PI 必要 |

**Cash projection**:

| 月 | Burn | Cash 残 | Event |
|---|---|---|---|
| 0 | $4M | $40M | Founder 退任 |
| +3 | $4.5M (legal + recruit) | $26.5M | IRB 再承認 |
| +6 | $4M | $14.5M | Trial 再開 |
| +9 | $4M | $2.5M | Phase 2 readout 予定 |
| +12 | needs $5M+ | bridge 必要 | Bridge round close |

**Cross-domain**:
- Tax: NOL 蓄積額 $50M+ (R&D heavy) → Section 382 trigger に注意 (大幅 ownership change risk)
- Equity: Phase 2 readout 待たずに down round 余儀なし (-40% valuation 想定)
- Debt: venture debt facility は通常 Bio Phase 2 では使えず → Equity 一択
- IPO: Pre-IPO talk あったが 12-18 ヶ月後ろ倒し

**Key insight**: Bio の Phase 2 段階で key founder loss は survival 直結。Bridge financing (insider lead) + 後継 CSO 確保 (Phase 2 readout までに名前のある PI) の 2 手で時間稼ぎ。Phase 2 結果次第で次の round が決まる。

---

## 6. Cross-reference 一覧

本書から各 reference への back-reference:

| 本書 section | Back-reference 先 |
|---|---|
| §1.1 Equity → Debt covenant | `11_debt_financing.md` §3, §4 |
| §1.2 Down round cascade | `04a_convertible_and_terms.md` §3, `04b_cap_table_mechanics.md` §5 |
| §1.3 Tax × M&A | `12_tax_strategy.md` §6, §7 |
| §1.4 IPO acceleration | `14_ipo_readiness.md` §4, §5 |
| §1.5 Bankruptcy priority | `11_debt_financing.md` §8 |

---

> **本リファレンスのメンテナンス**: Stress scenario の数値水準 (recession で revenue -30% 等) は経済環境変化に応じて年次 review 推奨。Black Swan セクションは新規事象 (e.g., COVID-19, SVB collapse, AI disruption) を追加。Cross-domain logic は Equity / Debt / Tax の各規制改正 (e.g., 経営者保証ガイドライン, Pillar 2, Section 382 改正) に応じて update。

> **本書の参照位置**: `scripts/build_model.py` の `build_stress_scenarios()` および `cross_domain_check.py` から正本として参照される。Stress test 実装は §3、業態別 applicability matrix は §4、cross-domain 影響伝播は §1 を pythonic に翻訳することで実装が可能。
