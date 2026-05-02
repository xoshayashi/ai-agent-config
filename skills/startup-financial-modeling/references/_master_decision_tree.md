---
name: master_decision_tree
description: Cross-file decision routing. ユーザーの意図 → どの reference を読み 4 路 (調達 / バリュエーション / 投資判断 / 借入) を統合的に判断する正本。E-C-001 解消。
type: reference
priority: P0
---

# Master Decision Tree

このドキュメントは reference 群 (00-14) 横断の **意思決定 routing 正本**。
個別 file は「How」(計算・条項・数値) を、本 file は「Where to read first / In what order」(どの順で読み、何を判定するか) を司る。

監査 E (Strategy) Critical finding **E-C-001** 解消: `04a` (転換商品), `05` (valuation), `08` (investment thesis), `11` (debt) を貫く master tree が存在せず、ユーザー側で 4 file をどの順で参照すべきか判断不能だった点を補完する。

> 同 file 内で `01a` のように小数点・記法が出てくる場合は **canonical naming は `_terminology.md`** に従う。`#0000FF` 等の color code は同 file の §1 を引く。

---

## 0. このドキュメントの読み方

### 0.1 5 つの top-level 意思決定 (entry point)

ユーザー (founder / VC / PE / アナリスト) が抱える典型的な質問は、本 file の §A〜§E の 5 つに収まる:

| Section | 質問 | 主たる出口 reference |
|---|---|---|
| A | 「どの調達手段で資金を調える?」 | 04a (転換) / 04b (希薄) / 11 (debt) |
| B | 「企業価値はいくらか?」 | 05 (valuation core) + 02/03 (driver) + 10 (sanity) |
| C | 「この案件に投資するか?」 | 08 (thesis) + 09 (TAM) + 04b (cap table) + 10 (smell) |
| D | 「Equity か Debt か」 | 04a + 11 + 06 (CFS impact) + 10 |
| E | 「業態 × stage で何を読むか」 (cross-cutting matrix) | 全 reference の routing 表 |

### 0.2 各 tree の凡例

```
Q: 質問
├── 答 a → 次の Q または 最終 reference
└── 答 b → 次の Q または 最終 reference
```

- 矢印の終端は「読み始める file の section 番号」を示す。
- `(skip)` と書かれた節は、そこで判定が決まり後続 Q 不要の意。
- `WATCH` / `PASS` / `FAIL` は §C の 3 値分類 (08 §3 とアラインされる)。

### 0.3 4 つの principle (本 tree が破られない条件)

1. **terminology は `_terminology.md` を SSoT** とする。本 file は用語を再定義しない。
2. **数値閾値は 08 §4 (kill criteria) と 02/03 (業態 metric) に back-reference** する。本 file は閾値の出所を持たない。
3. **WACC・割引率は 05 §1.6** が正本。本 file は「DCF を使うか」までを判断し、率は読み手が 05 で確認する。
4. **日本固有 (J-KISS / 政策金融公庫 / 経営者保証)** は `07_japan_specifics.md` に back-reference。本 file は routing のみ。

---

## A. 調達戦略の選択 (Equity vs Convertible vs Debt)

### A.1 Decision tree

```
Q1: ARR or revenue 計上済 (12 ヶ月で >$0)?
├── No (Pre-revenue / pre-product) →
│     Q1a: Lead VC 確定?
│     ├── Yes → Series A 優先株 (04a §6 + 04b §3)
│     └── No  → SAFE / J-KISS でブリッジ (04a §2 / §3)
│           Q1b: 法人格は?
│           ├── 米 Delaware C-corp → SAFE (04a §2)
│           ├── 日本株式会社        → J-KISS (04a §3)
│           └── Singapore / Cayman  → SAFE (04a §2) もしくは Convertible Note
│
└── Yes →
    Q2: 次回 priced round までの runway ≥ 12 ヶ月?
    ├── Yes →
    │     Q2a: 直近 12 ヶ月 ARR growth ≥ 100% (Series A 規模)?
    │     ├── Yes → Equity round 中心 (04a §6 + 04b §3 + 05 §10)
    │     └── No  → Convertible bridge を検討 (04a §1.4 + §2.3)
    │
    └── No (runway < 12 ヶ月) →
        Q3: Recurring revenue ≥ $1M ARR (= debt 適格)?
        ├── Yes → Q3a: 既存 equity 直近 18 ヶ月以内?
        │             ├── Yes → Venture debt (11 §1.1) を equity 補完で
        │             └── No  → まず bridge SAFE (04a §2) → 後に debt
        │
        └── No  →
            Q4: 国内中小事業 (年商 < ¥1B)?
            ├── Yes → JFC 創業融資 / 制度融資 (07 §6 / 11 §10)
            └── No  → Bridge equity (04a §1.4) or 親会社借入 (11 §6)
```

### A.2 Convertible 4 兄弟の選び方

`04a §1.3` の 4 商品横断比較表を ROUTING の観点で再編した:

| 質問 | 答 | 商品 | 理由 |
|---|---|---|---|
| Cap だけで Discount 不要? | Y | YC SAFE Cap-only | 計算が単純 |
| Discount だけ? | Y | YC SAFE Discount-only | 早期 friend round |
| 両方欲しい (US) | Y | YC SAFE Cap+Discount | YC default |
| 法的に「社債」が必要 (日本) | Y | J-KISS / 新株予約権付社債 | 会社法上の根拠 |
| 投資家が満期返済を希望 | Y | Convertible Note | SAFE は満期なし |

### A.3 数値で見る「いつ equity に切り替えるか」

```
SAFE で 1 ラウンド (ceiling)
  → 累計 SAFE 投資額が想定 post-money の 25-30% 超 → 必ず priced round へ
  → SAFE holder ≥ 5 名 → cap table 整理目的で priced round 推奨
  → 経過 18 ヶ月超 → SAFE が 「stale」 化、re-cap リスク (04a §2.7)
```

実務 rule: 「**3 SAFE までは許容、4 つ以上は必ず priced round で整理**」。
See: 04a §2.4 (5 標準テンプレート) で SAFE 種類が混在する場合は更に厳しく。

### A.4 例外節: Pre-revenue でも debt ありえる場合

- ハードウェア / 設備投資型 → リース (07 §7) または設備融資 (11 §10.3)
- 補助金 (J-Startup, 経産省, 自治体) → 返済不要、ただし dilution に類似する 「効力制約」 あり (07 §7.2)
- グラント (academic / non-profit) → 返済不要、IP 制約に注意

これらは **本 tree の主筋 (Equity / Convertible / Debt) とは別 layer** なので、A.1 の判定後に「重ねて取得できる subsidy」 として扱う。

---

## B. バリュエーション手法選択

### B.1 Stage × 手法 maturity 表

`05 (valuation_wacc.md)` の章番号と対応:

| Stage | 第一手法 | 第二手法 | 第三手法 | 業態固有 |
|---|---|---|---|---|
| Pre-product | VC method (05 §4) | Berkus (05 §5) | Scorecard (05 §6) | — |
| Pre-revenue (MVP) | VC method (05 §4) | Risk-factor summation (05 §6) | Scorecard | SaaS なら Bessemer fit (05 §10) |
| Early revenue (<$1M ARR) | VC method (05 §4) | Comps (05 §2) | DCF (05 §1) は弱い | SaaS / Marketplace multiple |
| Series A (~$1-10M ARR) | DCF stage-discount (05 §1) | Comps (05 §2) | VC method (05 §4) | 業態 multiple (05 §10/11) |
| Series B-C (~$10-100M ARR) | DCF (05 §1) | Comps (05 §2) | Precedent (05 §3) | LTV/CAC sanity (02 §5) |
| Pre-IPO (>$100M ARR) | DCF (05 §1) | Comps (05 §2) | Precedent (05 §3) | sum-of-parts も (05 §7) |
| Public | DCF (05 §1) | Comps (05 §2) | EV/EBITDA / P/E | — |

### B.2 Decision tree

```
Q1: Stage は?
├── Pre-product / Pre-rev → 05 §4 + §5 + §6 (定量より定性)
├── Early Rev               → 05 §4 + §10 (SaaS) または §11 (vertical)
├── Series A-B              → 05 §1 (DCF) + §2 (Comps) + §10/11
├── Series C-Pre-IPO        → 05 §1 + §2 + §3 (Precedent)
└── Public                  → 05 §1 + §2

Q2: Cap table に未転換 SAFE / J-KISS が残?
├── Yes → 04a §2.6 / §3.6 で転換 → 04b §1.3 TSM (Treasury Stock Method) → 05 で Equity Value 算定
└── No  → 直接 05 へ

Q3: 業態固有 multiple が必要?
├── SaaS               → 05 §10 (Bessemer / ICONIQ benchmark)
├── Marketplace        → 05 §11.1 (GMV multiple, Take rate sensitivity)
├── Fintech            → 05 §11.2 (P/B, NIM, Loan book LTV)
├── Bio / Pharma       → 05 §8 (Real Options, rNPV)
├── Hardware           → 05 §2 を primary、EV/EBITDA で
├── E-commerce         → 05 §11.3 (EV/Sales + Contribution margin)
└── Energy / Infra     → DCF + WACC を厚く (05 §1.6)

Q4: シナリオ感度を要するか?
├── Yes → 05 §9 (Scenario / Tornado) + 10 §11 (Sensitivity craft)
└── No  → base case 単本でも可
```

### B.3 Pre-money / Post-money の混乱を避ける rule

```
- Term sheet で「pre-money $X」と書かれた → Equity Value (pre-money) の話。
  Investor 出資分を加えると post-money になる。
- DCF / Comps の出力は **Equity Value (post-money 観点なし)** = TEV - Net Debt - 優先株.
- SAFE Cap が「post-money」と書かれていれば、そのまま投資家持分が固定 (04a §2.2).
- SAFE Cap が「pre-money」と書かれていれば、後続 SAFE で投資家・創業者ともに薄まる.
```

5 章 (valuation) の数字を term sheet に当てる前に、必ず **04a §2.6 の Closed-form** で SAFE 転換後の希釈を確認すること。これを怠ると term sheet の post-money が cap table 上で再現できない。

### B.4 評価レンジの triangulation

複数手法から得た EV を並べた時の取り扱い:

```
- DCF と Comps の差が ±20% 以内 → 中央値を base case
- 差が ±20-50%        → outlier 確認、driver 整合チェック (05 §9)
- 差が ±50% 超        → 必ずどちらかが間違い、source of truth 再点検
- VC method のみ (early stage) → 必ず sensitivity (target multiple ±2x)
```

---

## C. 投資判断 (Go / No-Go / Watch)

### C.1 4 段ゲート方式

```
Q1: Stage に応じた 量的閾値 (08 §4 kill criteria) を全て通過?
├── No  → FAIL (kill criterion 該当、proceed しない)
└── Yes →
    Q2: TAM × max realistic share > target ARR (= exit に必要な売上)? (09 §7)
    ├── No  → WATCH (TAM 検証要、bottom-up が weak)
    └── Yes →
        Q3: Founder / Team が健全 (08 §9)?
        ├── No  → WATCH (founder risk、ref check 強化)
        └── Yes →
            Q4: Cap table が clean (04b §11 dirty cap detection)?
            ├── No  → WATCH (clean-up condition を term sheet に)
            └── Yes → PASS (proceed to DD / IC)
```

### C.2 4 段ゲートの意味するもの

| Gate | 観点 | 主参照 | typical fail 例 |
|---|---|---|---|
| Q1 量的 | 数字が嘘ついていないか | 08 §4 | Burn multiple > 3, NRR < 90% |
| Q2 市場 | 帰結 (exit) が描けるか | 09 §7 | TAM 過大、SOM 5% 仮定で目標未達 |
| Q3 人 | execute できる team か | 08 §9 | Solo founder + 業界経験ゼロ |
| Q4 構造 | 数字の主語が誰か | 04b §11 | Founder 持分 < 20%、Stacked SAFE |

「PASS」 は「投資する」 を意味しない。**DD 開始 GO** の意。最終投資判断は 08 §10 (IC memo) に従う。

### C.3 WATCH の使い方

WATCH は「pause」 ではなく「**condition 付き conditional pass**」。
代表例:
- WATCH (TAM): 「次回 board update で bottom-up TAM 数字を 3 customer 実測で示せ」
- WATCH (founder): 「CTO hire を term sheet 条件に」
- WATCH (cap table): 「pre-closing で stacked SAFE を一掃」

これらは「6 ヶ月以内に解消されなければ FAIL に降格」 が標準。

### C.4 投資 thesis の最低条件 (08 §2 と整合)

```
A. The market is large or rapidly growing (09 §3-§7)
B. The team can win the market (08 §9)
C. The unit economics will work at scale (02 §5 LTV/CAC)
D. The company can defend the position (08 §6 moat)
E. We can underwrite a 10x return scenario (05 §4 VC method)
```

5 つすべてが ≥ Yellow なら PASS、1 つでも Red なら WATCH/FAIL。

---

## D. Debt vs Equity の意思決定

### D.1 Decision tree

```
Q1: Founder 希薄化感度 (現在持分)?
├── Founder 持分 < 30% → Debt prefer (希釈余地少ない)
│         Q1a: ARR ≥ $1M?
│         ├── Yes → Venture debt (11 §1.1)
│         └── No  → JFC / 制度融資 (11 §10) または bridge SAFE (04a §2)
│
├── 30-50% → 中庸: Equity と Debt のハイブリッド (Convertible debt = 04a §4)
│
└── ≥ 50% → Equity prefer (まだ希釈許容、Debt の制約を回避)
              Q1b: Lead VC 確定?
              ├── Yes → Priced equity (04a §6)
              └── No  → SAFE bridge (04a §2)

Q2: Covenant 制約の許容度?
├── Strict OK   → Senior secured debt (11 §1.7) or Banks
├── Light のみ → RBF (Revenue-Based Financing, 11 §1.2) / Convertible (04a §3)
└── ZERO        → Equity 一択 (04a §6)

Q3: Cash flow profile (FCF + / -)?
├── FCF + (黒字)   → Debt 余地あり、senior loan 相談可
├── FCF flat       → Venture debt (margin で repay)
└── FCF deeply -   → Equity / Convertible のみ。Debt は 11 §3 (戻れぬ路)
```

### D.2 Debt 適格性 4 条件 (11 §1 と整合)

```
i.   Recurring revenue ≥ $1M ARR (or local equivalent)
ii.  Equity round が直近 18 ヶ月以内に存在 (= venture debt only)
iii. Gross margin ≥ 50% (lender pleasing)
iv.  Cash runway > debt のターム (利息・元本に runway を吸われない)
```

4 つすべて Yes → Venture debt OK。
1 つでも No → 別 path へ (RBF or Equity)。

### D.3 Debt のコストを下げる優先順位

```
Cheapest →  Most expensive
JFC / 制度融資 (~1-2%) → 銀行プロパー (~2-4%) → ベンチャーデビット (~10-13%)
                                                   → RBF (~12-18%) → Convertible (~5% coupon + dilution)
                                                                       → Equity (cost = dilution)
```

Equity の 「コスト」 は IRR 期待値 (LP に約す return)。Series A で平均 25-30%/年。
これを debt と直接比較する場合、`(Equity dilution × Future EV) / Loan amount` で年換算する。

### D.4 経営者保証 (日本特有)

- JFC / 制度融資の多くで経営者保証あり → wind-down 時に founder 個人責任。
- 2023 改定 「経営者保証ガイドライン」 で限定可、ただし lender 任意。
- Wind-down framework (10 §19) と連動: **debt 取る前に exit / wind-down シナリオで残債を確認**。

---

## E. 業態 × Stage × 規模 routing 表

### E.1 主要業態 5 (SaaS / Marketplace / Fintech / Bio / Hardware)

| 業態 | Pre-rev | Early Rev | Series A | Series B-C | Pre-IPO |
|---|---|---|---|---|---|
| SaaS         | 04a + 09     | + 02 + 03 §1 | + 04b + 05 §10 | + 06 + 11 §1 | + 13a/b + 14 |
| Marketplace  | 04a + 09     | + 03 §2     | + 04b + 05 §11.1 | + 06 + 11 | + 13 + 14 |
| Fintech      | 04a + 09 + 12 | + 03 §3   | + 04b + 05 §11.2 | + 06 + 11 §10 | + 12 + 13 + 14 |
| Bio / Pharma | 04a + 09     | + 03 §5     | + 04b + 05 §8 | + 06 + 11    | + 12 + 13 + 14 |
| Hardware     | 04a + 09 + 07 §7 | + 03 §4 | + 04b + 05 §2 | + 06 + 11 §10.3 | + 13 + 14 |

### E.2 cross-cutting (常時参照)

| Topic | file | trigger |
|---|---|---|
| Design / formatting | 00 | 全ての output |
| Modeling 規範 | 01a | 数式・三表整合・命名 |
| 検証 / Sensitivity | 01b | 数値の自己整合・stress |
| Modeling craft | 10 | smell test, maturity |
| Terminology / SSoT | _terminology | 用語衝突時 |
| Master decision tree | _master_decision_tree (本 file) | 4 路を跨ぐ判断 |

### E.3 日本特有が混在する場合

`07_japan_specifics.md` を以下の **どれか一つでも該当** したら必ず併読:
- 法人格が日本株式会社
- 投資家に日本 VC が含まれる
- 出口に東証 IPO を想定
- 補助金 / 融資 (政策金融公庫 / 制度融資 / 補助金) を含む
- 税務 (租税特別措置法、ストックオプション税制) が論点

### E.4 ステージ移行時の chain (順序)

調達ラウンドが進む = 以下の order で読む:

```
Pre-seed (SAFE)           → 04a + 09 + 10 + (07 if 日本)
Seed (SAFE / J-KISS)      → 04a + 04b + 09 + 10 + (07)
Series A (Priced)         → 04a §6 + 04b + 05 + 02 / 03 + 08 + 09 + 10
Series B (Priced + Debt)  → 04a + 04b + 05 + 06 + 11 + 02 / 03 + 08
Series C (Priced + Debt+Pref) → 同上 + 04a §5 (優先株仕組) + 11 §1.1 (venture debt) + 12 (税)
Pre-IPO                   → + 13a (連結) + 13b (treasury) + 14 (IPO readiness)
Post-IPO                  → public 化、本 skill の対象外 (M&A / SPAC のみ)
```

---

## F. 4 file 連動の典型シナリオ (worked routing examples)

### F.1 シナリオ 1: SaaS Series A (US Delaware)

ARR $3M, growth 200% YoY, 既に SAFE 累計 $4M 残。

```
Step 1 (調達)        : §A → Q2 Yes (12mo runway), Q2a Yes (≥100% growth) → Equity round
Step 2 (転換)        : 04a §2.6 で SAFE → Series A 優先株への closed-form 転換
Step 3 (cap table)   : 04b §1.3 TSM で fully diluted shares 算定
Step 4 (valuation)   : §B → Series A → 05 §1 (DCF) + §2 (Comps) + §10 (Bessemer)
Step 5 (投資判断)    : §C → Q1 通過、Q2 (TAM), Q3 (founder), Q4 (cap clean) を順に
Step 6 (term sheet) : 04a §6 (preferred terms) + 04b §3 (anti-dilution)
```

### F.2 シナリオ 2: 日本 Bio Seed → Series A

J-KISS 累計 ¥300M、Series A 申込で東証マザーズ視野。

```
Step 1 (現状把握)   : 07 §3 (日本 SO 制度) + 07 §6 (補助金状況)
Step 2 (調達決定)   : §A → Q1 No (pre-rev) → J-KISS → 完了済、Series A へ
Step 3 (J-KISS 転換): 04a §3.6 で行使価額算定
Step 4 (valuation)  : §B → Pre-revenue (Bio) → 05 §8 (rNPV) + §4 (VC method)
Step 5 (Series A)   : 04b §3 (優先株) + 05 §1 (但し Bio 用 cash flow shape)
Step 6 (税戦略)     : 12 §3 (税制適格 SO) + 12 §5 (法人税繰越)
```

### F.3 シナリオ 3: 黒字 SaaS で venture debt 検討

ARR $10M, GM 75%, Series B 完了後 12 ヶ月、cash $8M、burn $400K/月。

```
Step 1 (Equity vs Debt) : §D → Q1 founder 持分 22% < 30% → Debt prefer
                          Q1a ARR > $1M → Venture debt 候補
                          Q2 covenant strict OK → Senior unsec or venture debt
                          Q3 FCF flat → Venture debt
Step 2 (適格判定)       : D.2 i-iv 全 Yes
Step 3 (構造組成)       : 11 §1.1 (term loan) + 11 §1.6 (warrants)
Step 4 (CFS impact)     : 06 §3 (debt schedule) + 06 §5 (interest expense)
Step 5 (covenant 設計)  : 11 §4 (financial covenants) と FY24 forecast の整合
Step 6 (経営者保証)     : 該当なし (米法人)、ただし日本 sub があれば 07 §6.4 で要確認
```

### F.4 シナリオ 4: Wind-down に向かう

Bridge 失敗、runway 4 ヶ月、Series A VC 1 社のみ、debt あり。

```
Step 1 (再 bridge 試行)  : §A → A.1 + A.4 (補助金) で短期 cash 確保
Step 2 (Acqui-hire 並行) : 10 §19.4 step 3
Step 3 (Wind-down 確定)  : 10 §19 (founder wind-down framework)
Step 4 (法務・会計士)    : 07 §6.4 (経営者保証ガイドライン適用判断) + 07 §8 (民事再生 / 破産)
Step 5 (stakeholder)    : 10 §19.4 step 5 (board → 投資家 → 従業員 → ベンダー → 顧客)
Step 6 (税務処理)       : 12 §7 (清算所得課税、欠損金引継ぎ)
```

---

## G. 失敗 mode と回避 (anti-pattern)

本 master tree が想定する 5 つの失敗を列挙:

### G.1 「3 file だけ読んで答える」

`04a / 05 / 08` だけ読んで 11 (debt) を読まない → equity 偏重で「希釈は避けたい founder 」を支援できない。
→ 必ず §A の Q3 (debt 適格判定) を通すこと。

### G.2 「terminology が file 間で異なる」

例: 「Valuation Cap」を 04a で「post-money」、05 で「pre-money」 として混在使用。
→ `_terminology.md` を SSoT として、不一致を見つけたら本 file の §B.3 で resolve。

### G.3 「pre-revenue で DCF を組む」

DCF は 5 年以上の安定的 cash flow が前提。Pre-revenue でこれを組むと「希望」を「数字」 に偽装する。
→ §B.1 表で stage 判定し、Pre-rev は VC method + Berkus + Scorecard。

### G.4 「Cap table を確認せず term sheet を切る」

未転換 SAFE / J-KISS が 4 つ以上ある状態で priced round を切ると、cap table が collapse する。
→ §A.3 の 「3 SAFE rule」 を厳守、必ず 04b §1.3 TSM で再計算。

### G.5 「Wind-down を VC 視点だけで考える」

08 の kill criteria は VC が「投資先を切る」 ための判断。これだけだと founder が残債・経営者保証で個人破産する path を覗かない。
→ 10 §19 (founder wind-down framework) を必ず併読。**E-C-005 解消の主旨**。

---

## H. 本 tree のメンテ規則

### H.1 更新 trigger

以下が起きたら本 file を更新:

1. 新 reference file 追加 → §E.1, §E.2 表に登録
2. 法改正 (会社法 / 金商法 / 政策金融公庫制度) → §A, §D の routing を見直し
3. SSoT 違反検出 (audit で発見) → §B.3, §G.2 を強化
4. 新業態の reference 追加 (例: AI 専用 metric) → §E.1 列追加
5. Stage 区分の変更 (例: pre-IPO の閾値変更) → §B.1 表更新

### H.2 更新時のチェックリスト

- [ ] `_terminology.md` と用語が一致するか
- [ ] §A〜§E の各 routing 終端が 「読み始める file の section」 を指しているか (file だけ指して section が無い、はNG)
- [ ] §F worked example が 4 つ以上あるか (現在 4)
- [ ] §G の anti-pattern が 5 つ揃っているか
- [ ] 監査 E (Strategy) Critical findings が再発生していないか

### H.3 廃止条件

将来、以下が起きたら本 file は分割 / 廃止候補:

- 行数が 1500 行を超え、routing tree より個別解説の比率が増えた → 解説部分を該当 file に戻す
- §A〜§E のうち 1 つだけが 70% を占める → 専用 file に切り出す (例: `_funding_decision.md`)

---

## I. References (本 file が back-reference する関係先)

```
- 04a_convertible_and_terms.md     : 転換型・優先株条項 ★ §A 主参照
- 04b_cap_table_mechanics.md       : Cap table / TSM / dilution ★ §C, §B 主参照
- 05_valuation_wacc.md             : DCF / Comps / Multiple / WACC ★ §B 主参照
- 08_investment_thesis.md          : 投資 thesis / kill criteria ★ §C 主参照
- _terminology.md                  : SSoT (用語 / 色 / 命名) ★ 全 file 共通
```

---

> 本 file は **意思決定の交通整理** を目的とする。具体計算・条項条件・数値閾値は必ず終端の reference を引いて確認すること。Master tree が「答え」 を持つことはない。
