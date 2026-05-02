---
name: debt_financing
description: スタートアップ借入 / 社債 / LBO Debt の正本 (Venture Debt / RCF / Term Loan / 政策金融公庫 / SBA / Mezzanine / Covenant / Cross-default)。SKILL.md dispatch table の "venture debt vs equity" entry の補完 reference として §1.1, §18.1-18.6 で展開。
type: reference
priority: P1
related: [_terminology, _master_decision_tree, 06_three_statement, 07_japan_specifics, _stress_framework]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: Debt 商品定義 / Covenant / Cross-default は本書を canonical とする
- **Routing**: [`_master_decision_tree.md §D`](_master_decision_tree.md) (debt vs equity) から第 1 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (Covenant breach trigger / Cross-default mechanics) を必ず実行
- **関連 reference**: `06_three_statement` (Debt schedule) / `07_japan_specifics §11` (政策金融公庫) / `_stress_framework §2` (debt stress)

# 11. Debt Financing — スタートアップ向け借入・社債・LBO Debt 専用リファレンス

> **対象**: スタートアップ向け包括的財務モデリング Claude Code skill。
> **目的**: Debt 商品カタログと、debt schedule を 3-statement model に正しく織り込むための spec。
> **想定アウトプット**: `xlsx` の `DebtSchedule` シートが本書の式・チェックを 1:1 で実装している状態。`scripts/build_model.py` および `three_statement_builder.py` から本書を正本として参照する。
> **会計基準**: US GAAP (ASC 470, ASC 815, ASC 825) と J-GAAP (新株予約権付社債等) の論点を併記。
> **数値の前提**: 利率・上限額・適用期限は 2026 年 5 月時点。`SOFR` ベース水準は 4.0–4.5%、`TONA` は 0.4–0.5% を想定 (各ケースで明示)。

---

## 0. ドキュメントの使い方

- 本書は **商品カタログ → 価格 → covenants → metrics → modeling → cases → checklists** の順に並んでいる。Debt schedule を組む際は §5、価格設定は §2、covenants は §3、ケース別の完成形は §11 を起点にする。
- 数式は **A1 形式 Excel** または擬似コード。`[セル]` は変数、`{シート名}` はシート参照。`SUMPRODUCT` / `XNPV` / `XIRR` などの組込関数を多用する。
- Equity round / SAFE / J-KISS / 優先株条項は `04a_convertible_and_terms.md` と `04b_cap_table_mechanics.md` を参照。本書では転換社債と warrant の **debt 側** だけを扱う。
- Revolver の plug 機能、利払の循環参照解消は `06_three_statement.md` §4 の前提を継承する。重複は避け、本書では debt 商品横断の追加論点に集中する。
- 用語: `OID` (Original Issue Discount) / `PIK` (Payment-in-kind) / `MAC` (Material Adverse Change) / `MFN` (Most Favored Nation) / `FCCR` (Fixed Charge Coverage Ratio) / `DSCR` (Debt Service Coverage Ratio) / `TLB` (Term Loan B) / `RCF` (Revolving Credit Facility) / `ABL` (Asset-based Lending) / `RBF` (Revenue-based Financing) / `JFC` (日本政策金融公庫) / `DBJ` (日本政策投資銀行)。

---

## 目次

1. スタートアップ向け Debt 商品カタログ
2. Debt の価格設定 (Pricing)
3. Covenants (借入契約条項)
4. Credit Metrics (信用指標)
5. Debt Schedule の Modeling
6. Cost of Debt の計算
7. Debt Capacity Analysis
8. デフォルト・破綻処理
9. Equity-linked Features (Warrant / 転換)
10. 日本固有の Debt 環境
11. Sample Debt Modeling (7 ケース)
12. Anti-patterns (避けるべき)
13. 投資判断視点での Debt
14. Term Sheet レビュー
15. 主要参考文献・データソース
16. Debt Due Diligence チェックリスト
17. Term Sheet レビュー チェックリスト

---

## 1. スタートアップ向け Debt 商品カタログ

### 1.0 商品横断比較

| 商品 | 適用 stage | 利率レンジ (2026.5) | 期間 | 担保 | 希薄化 | 主な用途 |
|---|---|---|---|---|---|---|
| Venture Debt | Series A〜D | SOFR + 600〜900 bps + 5〜10% warrant | 36〜48 ヶ月 | All-asset / IP | 中 (warrant) | Runway 延長 / 資金効率改善 |
| RBF (Revenue-based) | $300K〜10M ARR | revenue 3〜10% / cap 1.3〜2.0x | 12〜36 ヶ月 | revenue assignment | なし | 成長加速 / マーケ予算 |
| Convertible Debt (CB) | Pre-Series A 〜 Bridge | 4〜8% + cap + 10〜20% disc | 12〜24 ヶ月 | unsecured | 高 (転換時) | Bridge / シード |
| Bridge Loan | 任意 | 10〜15% effective | 3〜9 ヶ月 | 場合により | 中 | Next round までのつなぎ |
| ABL | Revenue 計上後 | SOFR + 350〜700 bps | revolving | AR / Inventory | なし | WC, D2C / Hardware |
| Working Capital Line / RCF | Series B+ | SOFR + 200〜500 bps | revolving 3〜5y | あり / なし | なし | WC plug |
| Term Loan A / B | Series C+ / PE | SOFR + 250〜600 bps | 5〜7 年 | All-asset | なし | 拡張 / 買収 |
| Mezzanine | Late stage / LBO | 12〜18% all-in (cash + PIK + warrant) | 7〜10 年 | subordinated | 中 (warrant) | LBO 拡張 / 持株会社 |
| 政策金融公庫 創業融資 | Pre-revenue / 創業 5y 内 | 2.30〜4.65% | 5〜10 年 | 任意 (経営者保証緩和) | なし | 創業初期 |
| TLB (LBO) | PE-backed | SOFR + 300〜500 bps | 7 年 bullet | All-asset | なし | LBO senior |
| Senior Secured Notes | Late / PE-backed | 6〜9% fixed | 7〜10 年 | First lien | なし | LBO 中位 |
| Senior Unsecured Notes | 大型 LBO / IPO 前 | 8〜11% fixed | 8〜10 年 | unsecured | なし | LBO 拡張 |
| Subordinated Notes / PIK | LBO 上位 sponsors | 10〜14% (含 PIK) | 8〜12 年 | 劣後 | 場合により | LBO 上位 |

> **読み方**: spread は「無リスク基準金利 + α」の α 部分。`bps` = basis points (1bp = 0.01%)。`SOFR + 600 bps` で SOFR=4.30% なら all-in 10.30%。

### 1.1 Venture Debt

#### 1.1.1 歴史と現在 (post-SVB shift)

- **SVB (Silicon Valley Bank) 破綻 (2023 年 3 月)** によりベンチャーデット市場の地殻変動が起きた。SVB は 2022 年時点で venture debt 出し手の 50% 超のシェアを占め、商業銀行モデル (低金利 + commitment 速度) を構築していた。
- 破綻後の継承は (a) **First Citizens Bank (FCB)** が SVB 資産買収、(b) **HSBC Innovation Banking** が SVB UK / 一部 US 部門を継承、(c) **Stifel Venture Banking**、(d) **First National Bank of Omaha (FNB)** などへ分散。
- 一方、**non-bank lenders** (Hercules Capital, TriplePoint Capital, Trinity Capital, Runway Growth Finance, Horizon Technology Finance, WTI など BDC 系) は規模拡大。商業銀行よりも高い spread を取り、warrant coverage と PIK option を組み合わせた構造を提供する。
- 2024〜2026 年にかけて TLB / direct lending との境界が薄れる傾向。late-stage は **growth credit** ファンド (Owl Rock = Blue Owl, Golub Capital, Antares Capital, Ares Capital など) が参入し、$50M〜$300M tickets を扱う。
- 日本では **あおぞら銀行 (ABL Capital ベンチャーデット)**、**三井住友信託銀行 ベンチャーデット**、**みずほ銀行**、**INCJ (旧 産業革新機構)**、**JBIC IG (海外向け)**、**SBI 新生銀行 (旧 SBI 新生銀行)**、**GLOBIS Capital Partners** が代表的な提供者。tickets は ¥500M〜¥3B が中心。

#### 1.1.2 構造 (典型的な Venture Debt)

- **Term Loan + Warrant Coverage** の 2 ピース構造。
- Term loan は 36〜48 ヶ月、最初の 6〜12 ヶ月は **interest only (IO) 期間**、その後 amortization。
- Warrant coverage は **5〜10%** が典型 (= facility size × coverage % が warrant 予約権の額面)。strike は **当該 round の price** または直近 priced round。
- **Draw period**: facility の commit 後 12〜18 ヶ月で複数 tranche に分けて引き出すケースが多い。
- 担保: **All-asset lien** (UCC-1 in US、譲渡担保 / 動産担保 in Japan)。IP も担保化されるが、execute は稀。

#### 1.1.3 典型条件 (2026 年 5 月時点)

| 項目 | 典型レンジ | 備考 |
|---|---|---|
| Facility size | $5M〜$50M | Series 規模に応じる |
| Tenor | 36〜48 ヶ月 | 36 が中央値 |
| IO 期間 | 6〜12 ヶ月 | growth ステージで延長交渉 |
| Amortization | 後半 24〜30 ヶ月 (straight-line) | balloon 残しは稀 |
| Coupon (interest) | SOFR + 600〜900 bps | 2026.5 = 10.3〜13.3% all-in |
| Floor | SOFR ≥ 4.0% (一部 lender は 1.0%) | rate cap は基本ない |
| Warrant coverage | 5〜10% | 平均 7.5% |
| Closing fee | 0.5〜1.5% | upfront |
| Backend / final fee | 1.5〜3.5% | maturity 時に支払 |
| Prepayment | 1〜3% (declining) | 1 年目 3% → 3 年目 0% など |
| Min cash | 6 ヶ月 burn | covenant |

#### 1.1.4 借入余力 (Debt Capacity)

- **次 12 ヶ月 ARR の 25〜40%** が SaaS の rule of thumb。
- **直近 equity round 額の 25〜50%** ( "25/30/35/40 rule" でステージ毎に上昇)。
- Hercules Capital の公開 deck では「30% of cash + 30% of last round」を目安として掲げている。

#### 1.1.5 Covenants

- **Minimum cash**: $5M または 6〜12 ヶ月 burn の高い方。Bessemer の標準推奨は **6 ヶ月 burn** floor。
- **MRR / ARR floor**: 各 tranche draw 時に MRR / ARR の minimum を設定。trip すると追加 draw 不可。
- **No MAC clause** が交渉のポイント。MAC (Material Adverse Change) は lender 側に裁量で default 発動権を与えるため、強い founder は MAC 削除を要求する。
- **No additional debt**: senior debt 追加禁止 (revolver / WC line を除く)。
- **No dividends / buyback** (一部例外: tax distribution)。

#### 1.1.6 Equity Dilution 影響

- **Warrant dilution = (Coverage % × Facility) / Strike Price ÷ Total Shares Outstanding**
- ケース: $10M facility / 7.5% coverage / strike $8 / 10M shares → warrant 数 = $750K / $8 = 93,750 株 → dilution 0.94%。
- Equity round で同等資金 ($10M @ post $100M valuation) を取る場合の dilution は 9.1% (= 10/110)。venture debt の dilution は 1/10 程度に抑えられるのが価値。

#### 1.1.7 適用 stage と Trade-off

- **適用 stage**: Series A 後で revenue 計上開始済 (ARR ≥ $2M 目安)、〜 Series D まで。
- **強み**: equity dilution 抑制、runway 延長、cash 効率改善。
- **弱み**: 月次 amortization が cash burn を悪化させる、covenant trip リスク、lender が equity round の terms を縛る (consent 条項)。
- **典型的失敗**: (a) IO 期間に過剰投資して amortization 開始時に cash 不足、(b) covenant trip → cure が間に合わず default、(c) next round 失敗 → maturity で refinance できず破綻。

#### 1.1.8 主要プレイヤー (US / Japan)

| 国 | プレイヤー | タイプ | チケット | 備考 |
|---|---|---|---|---|
| US | Hercules Capital (HTGC) | BDC | $5M〜$100M+ | 上場、最大手 |
| US | TriplePoint Capital (TPVG / TPC) | BDC + ファンド | $5M〜$50M | growth lending 強い |
| US | Trinity Capital (TRIN) | BDC | $5M〜$50M | equipment financing も |
| US | Runway Growth Finance | BDC | $10M〜$75M | late-stage 寄り |
| US | Horizon Technology Finance | BDC | $5M〜$30M | tech / life science |
| US | Western Technology Investment (WTI) | private fund | $5M〜$100M | 老舗 |
| US | HSBC Innovation Banking | bank | $5M〜$100M | post-SVB UK/US |
| US | First Citizens Bank | bank | $5M〜$100M | SVB 後継 |
| US | Stifel Venture Banking | bank | $5M〜$50M | 中堅 |
| US | Comerica, Bridge Bank, Pacific Western | bank | $3M〜$30M | regional |
| JP | あおぞら銀行 | bank | ¥500M〜¥3B | ベンチャーデット部 |
| JP | 三井住友信託銀行 | bank | ¥500M〜¥3B | 信託グループ |
| JP | みずほ銀行 | bank | ¥1B〜¥5B | メガバンク |
| JP | SBI 新生銀行 | bank | ¥500M〜¥2B | 中堅 |
| JP | INCJ | 政府系 | ¥500M〜¥10B | メザニン主体 |
| JP | JBIC IG / DBJ | 政府系 | ¥1B〜 | 構造化 |
| JP | GLOBIS Capital Partners (debt fund) | ファンド | ¥300M〜¥1B | growth 寄り |

### 1.2 Revenue-based Financing (RBF)

#### 1.2.1 構造

- **元本 (advance) + 月次 revenue の % を返済 → cap multiple 達成で完済**。例: $1M advance、月次 revenue の 6%、cap 1.5x → 累計 $1.5M 払い終えたら終了。
- 期間は revenue 成長率次第 (12〜36 ヶ月)。
- 所有権・経営権への影響なし。

#### 1.2.2 適用条件

- **ARR ≥ $300K** (Lighter Capital の最低水準)、Pipe / Capchase は ARR ≥ $100K でも対応。
- **gross margin ≥ 50%** (SaaS の場合)、e-commerce は 30% でも可。
- **net revenue retention ≥ 80%**。
- **Stage**: late seed 〜 Series B、SaaS / D2C / e-commerce / クリエイターエコノミー。

#### 1.2.3 典型条件

| 項目 | 典型レンジ |
|---|---|
| Advance amount | $50K〜$10M |
| Revenue share | 3〜10% (中央値 6%) |
| Cap multiple | 1.3x〜2.0x (平均 1.5x) |
| Term (理論最長) | 24〜36 ヶ月 |
| Effective IRR | 15〜35% (返済が早いほど高 IRR) |
| Origination fee | 0〜2.5% |
| Personal guarantee | 不要 (一般的) |

#### 1.2.4 主要プレイヤー

- **US**: Pipe (ARR トレード型)、Capchase、Clearco (旧 Clearbanc、e-commerce)、Wayflyer (D2C / e-commerce)、Lighter Capital (SaaS)、Founderpath、Re:cap。
- **EU**: Re:cap (ドイツ)、Uncapped (UK)、Booste (ポーランド)。
- **JP**: **Yoii (ヨイ)** (旧 Yoii Fuel) — SaaS 向け RBF、$100K〜$5M。**Bizforward** — D2C / e-commerce 向け。**Anyflow / Inflection Capital** — 拡張中。

#### 1.2.5 会計処理

- **US GAAP**: ASC 470 で借入金 (notes payable) に分類。月次返済を `interest expense` と `principal repayment` に **effective interest method** で按分。cap multiple − advance を total finance charge として、想定期間で按分。
- **J-GAAP**: 短期借入金 / 長期借入金。利息相当額は支払利息として計上。
- 売掛金担保扱いになる場合、AR を BS から落とす (factoring 扱い) ケースもある。契約書での remedy / recourse 条項で判定。

#### 1.2.6 Trade-off

- **強み**: equity dilution 完全になし、personal guarantee なし、speed (5〜14 日で着金)、業績連動でダウンサイドが緩い。
- **弱み**: gross margin を圧迫 (毎月の revenue share)、cash conversion が悪化、cap reach 後の次調達は別途必要、effective IRR は 15〜35% と高め。
- **典型的失敗**: (a) revenue 急増局面で cap multiple に早く到達 → 結果的に effective IRR が想定の 2 倍以上になる、(b) 同時に複数 RBF を組成 → revenue 30% 超が返済に回る、(c) RBF 残高を venture debt の lender に開示せず covenant trip。

### 1.3 Convertible Debt (株式転換社債)

> 詳細条項は `04a_convertible_and_terms.md` 参照。本書では **debt 側** の論点のみ。

#### 1.3.1 基本構造

- **元本 (principal) + 利息 (interest, accrued) + valuation cap + discount + 転換 trigger**。
- 米国 Convertible Note は SVB Form / NVCA Form / 各 VC ファーム独自 Form がある。利率 4〜8%、満期 12〜24 ヶ月、cap + discount 併用が標準。
- 日本では **新株予約権付社債 (CB)** として会社法上の社債扱い (会社法 238 条以下)。J-GAAP では金融商品会計基準で区分処理。

#### 1.3.2 SAFE / J-KISS との対比 (debt 側)

| 軸 | Convertible Note | SAFE | J-KISS |
|---|---|---|---|
| Debt 性質 | あり (社債) | なし (将来株式取得権) | 形式は新株予約権 |
| 利息 | あり (4〜8%) | なし | なし (v2.0) |
| 満期 | あり (12〜24 ヶ月) | なし | あり (18 ヶ月で自動転換 / 協議) |
| BS 計上 | LT Debt → 転換時に Equity 振替 | mezzanine equity (US) | 純資産 (新株予約権) |
| Tax shield | 利息は損金算入 (US / JP) | なし | なし |
| 投資家保護 | 破産時に債権者として優先 | 株主同等 | 新株予約権者 |

#### 1.3.3 MFN (Most Favored Nation) Clause

- 後発の convertible が **より有利な条件** (low cap / high discount / 利息高 / 担保強) を持つ場合、先発の convertible holder が **後発の条件を選択できる** 権利。
- 実務上、SAFE / 新規 convertible round で **同 cap・同 discount に揃える** 強制力を持つ。
- モデリング: cap table で「MFN 適用後の最良条件」で転換株式数を計算する。Excel では `MAX` で cap / discount の有利な側を選択し、各 holder 毎に別計算。

#### 1.3.4 Modeling 要点 (debt 側)

- **発行時**: BS の `Convertible Notes Payable` として LT Debt 計上。CFS は CFF で `+Issuance` 計上。
- **利息**: PIK 形式で元本に加算 (accrued interest) または cash 払い。SaaS スタートアップは PIK が一般的。`Interest_t = Principal_{t-1} × Rate × DayCount`、`Principal_t = Principal_{t-1} + Interest_t`。
- **転換時**: priced round トリガで `Convertible Notes Payable` を `Common/Preferred Stock + APIC` に振替。CFS は **non-cash** (CFF にも CFI にも計上しない)。代わりに Supplemental disclosure (non-cash investing/financing) で開示。
- **満期で転換不可**: cash で返済または extend。default となれば破産事由。

### 1.4 Bridge Loan

#### 1.4.1 想定

- **次 round (priced) までの 3〜6 ヶ月 funding** を埋める短期借入。
- 形式は (a) **Insider Bridge** (既存 VC が convertible note / SAFE で出す)、(b) **3rd Party Bridge** (新規 lender が secured term loan で出す)。
- Insider bridge は VC が「次 round に参加する自信」のシグナル。3rd party bridge は商業条件が厳しいが、insider が出さない場合の最終手段。

#### 1.4.2 Pricing

- **Insider bridge**: 利率 5〜10%、cap は次 round の 80〜100%、discount 10〜30%。
- **3rd Party Bridge**: 10〜15% effective cost (含 fee + warrant + OID)。期間 3〜9 ヶ月。
- **Maturity exit**: 次 round で自動転換または cash 返済。

#### 1.4.3 Covenants

- 短期かつ最低限。Min cash floor、reporting、no additional debt が中心。MAC clause が含まれることが多いが、insider bridge では削除されるのが典型。

#### 1.4.4 Insider Bridge vs 3rd Party の見分け方

| 軸 | Insider Bridge | 3rd Party Bridge |
|---|---|---|
| 動機 | 次 round 確実、option 確保 | 純粋な lending profit |
| 利率 / 経済 | 緩め | 厳しい |
| 担保 | 通常なし | All-asset 取ることが多い |
| Speed | 速い (2〜4 週) | 中 (4〜8 週) |
| Down-round シグナル | 弱い (positive) | 中 (neutral〜negative) |
| ダウンサイド | round 失敗時に pari passu で round 参加 | default → 担保処分 |

### 1.5 Asset-based Lending (ABL)

#### 1.5.1 構造

- **AR (売掛金) と Inventory (在庫) を担保とする revolving facility**。
- **Borrowing Base** (借入可能額) を毎月 (週次の場合も) 計算し、それを上限に revolver として draw / pay down。
- 担保が裏付けなので、**EBITDA covenants が緩い** または unmatched (ABL は cash flow lending と違い、担保価値ベース)。

#### 1.5.2 Borrowing Base 計算式

```
Borrowing Base =
    AR × Advance Rate (typically 80–85%, eligible のみ)
  + Inventory × Advance Rate (typically 50–65%, raw + finished, eligible のみ)
  + Equipment × Advance Rate (typically 60–75% of Net Orderly Liquidation Value)
  − Reserves (dilutive items, fraud reserve, taxes)
```

- **Eligibility 除外**: 90 日超延滞 AR、特定大口顧客 (concentration cap 通常 25%)、政府向け、関連当事者向け、海外 AR 一部、disputed AR、in-transit / consigned inventory、obsolete inventory。
- **Advance rate** は lender の reasonableness と過去のロス・ヒストリで決まる。D2C / e-commerce は advance rate 高め。

#### 1.5.3 適用業態

- **D2C / e-commerce**: AR は薄いが inventory が厚い (Settle, Resolve が D2C 特化)。
- **Hardware / 製造業**: AR + Inventory の両方が太い。
- **B2B SaaS**: AR は太いが inventory はゼロ → AR-only ABL。
- **マーケットプレイス**: GMV-based の ABL が登場 (Pipe など特殊)。

#### 1.5.4 主要プレイヤー

- **US**: Wells Fargo Capital Finance、JPMorgan ABF、PNC Business Credit、Bank of America Business Capital、CIT Group (現 First Citizens)、Crystal Financial、SLR Capital (旧 Solar Capital)、White Oak。
- **Fintech-native**: **Settle** (D2C), **Resolve** (B2B AR financing), **Backd**, **Fundbox**, **Bluevine**, **C2FO**。
- **JP**: 三井住友銀行 ABL 事業部、みずほ銀行 動産担保、ジャックス、ABL協会加盟銀行 (60+ 行)。**動産・債権譲渡特例法** に基づく登記制度 (1998 年〜)。

#### 1.5.5 適用 stage と Trade-off

- **適用 stage**: revenue がある程度出てから (AR ≥ $1M 目安)。
- **強み**: 担保価値ベースで borrowing capacity が確保しやすい、EBITDA covenant がない / 緩い、低 cost。
- **弱み**: 担保管理 (field exam, 月次 BBC = Borrowing Base Certificate 報告)、operational burden、AR 集中度低下が条件。
- **典型的失敗**: (a) 集中顧客 1 社の大口未収を eligible と誤算 → 該当 AR が dispute → BBC 計算違反、(b) 在庫評価が NRV (正味実現可能価額) を上回って書き換え必要、(c) lockbox 切替コスト過小評価。

### 1.6 Working Capital Line / Revolver (RCF)

#### 1.6.1 構造

- **Revolving credit facility (RCF)**。一定の枠内で繰返し draw / pay down 可能。
- Committed (確約付き) または uncommitted。Committed RCF は unused commitment fee (0.25〜0.50%) を payable。
- 担保あり (secured) / なし (unsecured)。Unsecured RCF はより credit が必要。
- 期間 3〜5 年の committed が typical、annual review。

#### 1.6.2 借入余力 (Capacity)

- AR / Inventory がベース (ABL に近い場合)。
- Cash flow lending 型 RCF は **3〜4x EBITDA** を目安に枠を設定。
- スタートアップは ARR multiple based (0.5〜1.0x ARR) のケースもある。

#### 1.6.3 Covenants

- **Leverage Ratio**: Total Debt / EBITDA < 4〜6x。
- **Interest Coverage Ratio (ICR)**: EBITDA / Interest > 2〜3x。
- **FCCR**: > 1.0〜1.2x。
- **Min liquidity**: cash + RCF availability ≥ X ヶ月 burn。

#### 1.6.4 利率

- **SOFR + 200〜500 bps** が secured / mid-cap 領域。
- 大企業は SOFR + 100〜200 bps、スタートアップは SOFR + 400〜600 bps が現実値。
- **Floor**: ベンチマーク低水準時のみ意味あり (2026.5 では SOFR が高水準で floor 効かない)。

### 1.7 Term Loan (普通社債 / Senior Term Loan)

#### 1.7.1 構造

- **Term Loan A (TLA)**: 銀行 syndicate、bank holdco、5〜7 年、amortization stable (年 5〜10%)、SOFR + 200〜350 bps、軽量 maintenance covenants。
- **Term Loan B (TLB)**: institutional (CLO, mutual funds, BDC)、6〜7 年 bullet、minimal amortization (年 1%)、SOFR + 300〜500 bps、cov-lite 主流。
- スタートアップ向けは TLA 中心。LBO は TLB が主流。
- 担保: First lien all-asset。

#### 1.7.2 適用 stage

- **Series C+**: $20M+ ARR、cash flow positive または approaching、IPO 準備期。
- **Pre-IPO bridge**: IPO 直前の 18 ヶ月で取る一時 facility。

#### 1.7.3 Pricing

- TLA: SOFR + 250〜350 bps + 0.5〜1% upfront + 0.25% unused。
- TLB: SOFR + 350〜550 bps + 1〜2% OID + 1% prepayment 1y。
- Floor: SOFR ≥ 0.50〜1.00% (2026.5 では効かない)。

### 1.8 Mezzanine Financing (メザニンファイナンス)

#### 1.8.1 構造

- **Subordinated debt (劣後債) + warrants** または **subordinated note with PIK toggle**。
- Senior Debt の **下位**、Equity の **上位** に位置する。
- Coupon 構造: Cash interest (8〜12%) + PIK interest (3〜6%) + warrants (1〜5% of fully-diluted)。
- 期間 7〜10 年 bullet (no amortization 通常)。
- Call protection: 1〜3 年 non-call、その後 declining premium (105 / 102.5 / 100)。

#### 1.8.2 Pricing (all-in cost)

- Cash coupon 10〜12% + PIK 2〜4% + warrant value 2〜4% = **all-in 15〜20% pre-tax IRR** が lender の目標。
- 借り手側の effective rate は 12〜18% (warrant 価値を年率換算した分を含む)。

#### 1.8.3 適用

- **LBO**: senior + mezzanine + equity の典型 cap structure。
- **拡張 financing**: senior limit を超える追加 leverage が必要な場合。
- **Recap / dividend**: sponsor が equity 一部回収するための debt。

#### 1.8.4 主要プレイヤー

- **US**: Owl Rock (Blue Owl Capital)、Golub Capital、Antares Capital、Ares Capital、Audax Mezzanine、Crescent Capital、HPS Investment Partners、Twin Brook Capital。
- **JP**: 三井住友 DS アセットマネジメント、大和証券 SMBC PI、日本政策投資銀行 (DBJ)、農林中金、商工中金、新生銀行、INCJ。

### 1.9 Government / Public Funding (Japan focus)

> 詳細は §10 で深掘り。本節は overview。

- **日本政策金融公庫 (JFC)**: 創業融資 / 新事業活動促進資金 / 資本性ローン (劣後ローン)、利率 2.30〜4.65% (基準利率, 2026.5)、上限 7,200 万円 (普通)。
- **信用保証協会**: 保証付融資、80% / 100% 保証、保証料率 0.45〜1.90%。
- **商工中金 (商工組合中央金庫)**: 中堅向け、危機対応融資。
- **日本政策投資銀行 (DBJ)**: 大型 / 構造化、メザニン、劣後ローン。
- **NEDO / AMED / 経産省 補助金**: 返済不要 (一部は出世払いまたは利益連動返済)。

### 1.10 LBO Debt Structures

#### 1.10.1 Capital Stack の典型構成

| 層 | 商品 | 構成比 (典型) | Coupon | Maturity | 担保順位 |
|---|---|---|---|---|---|
| Senior Secured | RCF | 0〜5% | SOFR + 200〜350 bps | 5y | First lien |
| Senior Secured | TLA | 5〜15% | SOFR + 250〜400 bps | 5〜7y | First lien |
| Senior Secured | TLB | 35〜50% | SOFR + 300〜500 bps | 7y | First lien |
| Senior Secured | Senior Secured Notes | 10〜20% | 6〜9% fixed | 7〜10y | First / Second lien |
| Senior Unsecured | Senior Unsecured Notes | 10〜20% | 8〜11% fixed | 8〜10y | Unsecured |
| Subordinated | Subordinated Notes / Mezz | 5〜15% | 10〜14% (含 PIK) | 8〜12y | 劣後 |
| Holdco PIK | Holdco PIK Note | 0〜10% | 12〜15% PIK | 8〜10y | 持株会社劣後 |
| Equity | Sponsor Equity | 30〜40% | n/a | n/a | 残余 |

#### 1.10.2 Term Loan B (TLB)

- **Institutional leveraged loan market** で取引。CLO (Collateralized Loan Obligation) が最大の買い手。
- **Cov-lite** (maintenance covenant 削除、incurrence covenant のみ) が 90% 超 (LCD/Pitchbook 統計)。
- **Bullet at maturity**: amortization 1%/年が標準、95% を maturity で repay。
- **Soft call**: 通常 6 ヶ月 non-call または 1% premium。
- **Margin Ratchet**: leverage 改善で coupon 下がる仕組み (例: < 4x で 25 bps step-down)。

#### 1.10.3 Senior Notes (Bonds)

- **High-yield bond market** で取引。Rule 144A / Reg S。
- Fixed coupon、8〜10 年 maturity、call protection (5y / 7y / 10y で NC4 / NC5 / NC6)。
- **Make-whole call** (T+50 bps) → call protection 後の declining premium (102.5 / 101.25 / 100)。

#### 1.10.4 PIK / Holdco PIK

- **Operating Co (OpCo) PIK**: OpCo の subordinated note で利息が全額 PIK。
- **Holdco PIK**: 持株会社 (HoldCo) レベルで debt 発行。OpCo の cash flow が dividend で吸い上がるまで cash 利息を待つ。Holdco PIK は **structural subordination** (担保なし、OpCo の創業時債務に劣後)。
- Coupon 12〜15% all-PIK。元本に毎期加算され指数関数的に増加。
- Sponsor recap でよく使われ、equity 投資家への追加 distribution の原資。

#### 1.10.5 Sponsor Backing 影響

- KKR / Carlyle / Blackstone / Apollo / Bain Capital / TPG / CD&R などの大型 sponsor は relationship lending で **20〜50 bps** spread 削減を交渉できる。
- Sponsor の equity check が 30〜40% 入っていると lender の comfort が高まり、cov-lite + flexible covenants で組成可能。
- "Sponsor support" は **legally enforceable ではない** が、reputation effect で de facto の credit enhancement となる。




---

## 2. Debt の価格設定 (Pricing)

### 2.1 Reference Rate (基準金利)

#### 2.1.1 SOFR (US)

- **Secured Overnight Financing Rate**。NY 連銀公表、毎営業日。担保付翌日物 Repo 取引から計算される。LIBOR の置換 (cessation 2023.6) として標準化。
- 商品ローンでは **Term SOFR (CME 公表)** を使用。1M / 3M / 6M / 12M tenors。
- **2026 年 5 月時点の水準**: SOFR overnight 約 4.0〜4.3%、1M Term SOFR 約 4.0〜4.3%、3M Term SOFR 約 4.0〜4.3%。Fed の利下げサイクル後半で 2024〜2025 年に大幅低下した後、現在は安定圏。
- **Day Count Convention**: SOFR は **Actual/360** 慣習。利息計算 = `Principal × Rate × Days / 360`。
- **Reset 頻度**: 1M term は毎月、3M term は四半期。Reset 日は典型的に IPD (interest period date)。
- **Daily Compounded SOFR (in arrears)**: 一部の商品 (特に大型 syndicated) で使用。Term SOFR は forward-looking、daily compound は backward-looking という違い。

#### 2.1.2 TONA (Japan)

- **Tokyo Overnight Average Rate**。日銀公表。LIBOR (TIBOR) 置換のリスクフリーレート。
- 2026 年 5 月時点の水準: TONA 約 0.40〜0.50%。日銀の利上げサイクル進行中。
- **TORF (Tokyo Term Risk Free Rate)**: forward-looking term rate、QUICK ベンチマークが算出。Term SOFR の日本版。
- 商品ローンでは TIBOR が依然として併用される (短期はバンク慣行で残存)。

#### 2.1.3 EURIBOR / SONIA / その他

- **EURIBOR** (Euro Interbank Offered Rate): EU圏。Reform 後 hybrid methodology で残存。
- **SONIA** (Sterling Overnight Index Average): UK。LIBOR sterling 置換。
- **CORRA** (Canadian Overnight Repo Rate Average): Canada。
- **SARON** (Swiss Average Rate Overnight): Switzerland。

#### 2.1.4 ベンチマーク選択の実務

- **同一通貨**: 借入通貨に対応するベンチマーク。USD facility なら SOFR、JPY facility なら TONA。
- **クロスカレンシー**: hedge との組合せで実質コストを揃える。FX swap で USD → JPY funding を作り、TONA + spread にする等。
- **Floor**: ベンチマークが急落した場合の lender 保護。`max(Floor, SOFR + Spread)`。2026 年水準では floor が in-the-money でない。

### 2.2 Spread の決定要因

| 要因 | Spread への影響 | 典型ロジック |
|---|---|---|
| Credit rating | AAA→0、BBB→100bp、BB→300bp、B→500bp、CCC→800bp+ | synthetic rating でも適用 |
| Collateral | Secured > Unsecured | First lien は 100〜200bp 安 |
| Sponsor / Stage | Tier-1 sponsor で 25〜50bp 削減 | KKR/Carlyle/Blackstone 等 |
| Industry sector | SaaS (recurring) > Hardware > Cyclical | SaaS は 100〜200bp 安 |
| Tenure | 7y > 5y > 3y | 1 年延長で 25〜50bp 上昇 |
| Amortization | Bullet > Amortizing | bullet は 50〜100bp 上 |
| Equity cushion | High Cushion で 50〜150bp 削減 | LTV 50% → 70% で 100〜200bp 上 |
| Liquidity (size) | $500M+ > $50M > $10M | 大型 $50M+ は流動性 premium 削減 |
| Covenant package | Tighter > Cov-lite | cov-lite は 25〜75bp 上 |

### 2.3 OID (Original Issue Discount)

- **OID = Face Value − Issue Price**。額面の数 % 引きで発行 → 投資家の effective yield を押し上げる手法。
- 典型的に **1〜3%** (USD TLB)。99 OID = 1% OID と表記。
- **会計**: 借入時に face value で BS 計上、OID は **debt issuance costs** または **debt discount** として contra-liability。effective interest method で IS の interest expense に按分。
- **税務 (US)**: IRS rules に従い OID も interest として deduct 可 (Section 1272-1274)。
- **Effective Yield 計算**:

```
Effective Yield ≈ Coupon + (OID / Years)
精密版: Issue Price = Σ Coupon×PV + Face×PV(at maturity) を解いて IRR
```

例: 5y bullet TLB、coupon SOFR (4.30%) + 450bp = 8.80%、OID 99 (1%)、$100M facility:

```
Cash inflow = $100M × 99% = $99M
Annual interest = $100M × 8.80% = $8.80M
Maturity repayment = $100M
PV calc: $99M = Σ_{t=1..5} $8.80M / (1+r)^t + $100M / (1+r)^5
解: r ≈ 9.05% (≈ 8.80% + 1%/5y = 9.00% に近い、convexity で +5bp)
```

- **日本での扱い**: 日本企業発行の社債で OID は稀。法人税法上の処理は J-GAAP の社債発行差金として regulatory に整理 (社債発行差金は損金算入)。

### 2.4 Warrant Coverage Pricing

#### 2.4.1 構造

- **Warrant Coverage % = Warrant face value / Facility size**。例: $10M facility / 7.5% coverage = $750K warrant 額面。
- **Warrant 数 = Warrant face value / Strike Price**。Strike は当該 round 価格 (round-pricing) または lender 交渉で fixed price。

#### 2.4.2 Black-Scholes による Expected Value 計算

```
C = S × N(d1) − X × e^(−r×T) × N(d2)
d1 = [ln(S/X) + (r + σ²/2) × T] / (σ × √T)
d2 = d1 − σ × √T
```

- `S` = 現在の株価 (latest priced round)
- `X` = strike price
- `r` = risk-free rate (SOFR or US Treasury yield)
- `T` = warrant 期間 (typical 7〜10 年)
- `σ` = volatility (Public Comparable では SaaS 50〜70%、private では 70〜90% を仮定)
- `N(.)` = 標準正規分布 CDF

例: $10M facility / 7.5% coverage / strike $8 / current $8 / r=4%, T=7y, σ=70%:

```
d1 = [ln(1) + (0.04 + 0.49/2) × 7] / (0.7 × √7)
   = [0 + (0.04 + 0.245) × 7] / (0.7 × 2.646)
   = 1.995 / 1.852
   = 1.077

d2 = 1.077 − 1.852 = −0.775

N(1.077) ≈ 0.859
N(−0.775) ≈ 0.219

C = 8 × 0.859 − 8 × e^(−0.04×7) × 0.219
  = 6.875 − 8 × 0.756 × 0.219
  = 6.875 − 1.325
  = 5.55 / share

Warrant value = $750K / $8 × $5.55 = 93,750 shares × $5.55 = $520K
% of facility ≈ 5.2%
```

実務上: **Warrant Expected Value ≈ 50〜70% of face** (At-the-money、long-tenor)。

#### 2.4.3 Effective Cost への加算

```
Effective Cost (annualized) = Coupon + (Warrant Value / Facility / Years)
```

例 (続き): $10M / 8.80% / Warrant $520K / 4y avg life:

```
Effective = 8.80% + ($520K / $10M / 4y) = 8.80% + 1.30% = 10.10% all-in
```

### 2.5 Fee Structure

| Fee | レンジ | タイミング | 会計処理 (US GAAP) |
|---|---|---|---|
| Upfront / Closing fee | 0.5〜1.5% (commercial bank), 1〜3% (private credit) | Closing 時 | Debt issuance costs → effective interest method で按分 |
| Arrangement fee | 1〜2% (syndicated) | Closing 時 | 同上 |
| Unused commitment fee | 0.25〜0.50% / 年 | 四半期 | 当期費用 (other interest expense) |
| Letter of Credit fee | 1〜3% / 年 | 月次 / 四半期 | 当期費用 |
| Backend / Final / Maturity fee | 1.5〜3.5% (venture debt) | Maturity / Prepay 時 | accrue 方式で IS に均等按分 |
| Prepayment penalty | 1〜3% (declining) | Prepay 時 | Prepay 当期費用 |
| Make-whole call | T+50bp 残存 PV | 任意 prepay 時 | Prepay 当期費用 (extinguishment loss) |
| Exit fee (RBF / PIK) | 1〜3% | Cap reach / Maturity | 同上 |
| Agency / Trustee fee | $25K〜$100K / 年 | 年次 | OpEx |

**会計処理の要点**:

- **Debt issuance costs (DIC)**: ASC 835-30 で **直接控除型 (debt 残高から差し引く contra-liability)**。effective interest method で interest expense として按分。
- **Modification vs Extinguishment**: 既存 debt を refinance する場合、ASC 470-50 で 10% test (Cash flow PV 比較) → 10% 超で extinguishment、未満は modification。Extinguishment では新 fee を新規 debt の DIC に、未償却の old DIC は当期費用。

### 2.6 PIK (Payment-in-kind) Pricing

- **PIK 利息 = 現金支払の代わりに元本に加算**。
- Pure PIK: 全額 PIK。例: 12% all-PIK で 1 年後に元本が 1.12x。
- PIK Toggle: 借手が cash か PIK を選択。Cash で払う期は coupon に discount (例: PIK 12% / Cash 10%)。
- 複利計算: `Principal_t = Principal_{t-1} × (1 + PIK_rate)^t` (年複利)。月次なら `(1 + r/12)^12` で年率換算。

例: $30M PIK note / 12% / 5y bullet:

```
Year 0:  $30.0M
Year 1:  $30.0M × 1.12 = $33.6M
Year 2:  $33.6M × 1.12 = $37.6M
Year 3:  $37.6M × 1.12 = $42.1M
Year 4:  $42.1M × 1.12 = $47.2M
Year 5:  $47.2M × 1.12 = $52.9M ← Maturity 返済額
```

5 年で **76% 増加**。Sponsor は exit で $52.9M を返さないと持株者が劣後しか取れない。

### 2.7 Pricing 横断 — Effective Cost Worksheet

```
Effective All-in Cost (annualized) =
    Reference Rate (SOFR / TONA)
  + Spread (credit + collateral + sponsor + sector + tenor)
  + OID/年 (= OID% / Years to Maturity)
  + Upfront Fee/年 (= Fee% / Years)
  + Backend Fee/年 (= Fee% / Years)
  + Warrant Expected Value/年 (= BS value / Facility / Avg Life)
  + Unused Fee × (1 − Avg Drawn %) (revolver の場合)
```

**サンプル: $20M Venture Debt**

| 項目 | 値 |
|---|---|
| SOFR (3M Term) | 4.30% |
| Spread | 7.50% |
| Coupon (= sum) | 11.80% |
| OID 1% / 4y | +0.25% |
| Closing fee 1% / 4y | +0.25% |
| Backend fee 3% / 4y | +0.75% |
| Warrant 7.5% × 60% expected / 4y | +1.13% |
| **All-in effective cost** | **14.18%** |
| After-tax (35%) | 9.22% |

> **示唆**: 表記 spread が SOFR + 750bp (= 11.8% all-in) だが、warrant + OID + fees で **+240bp** 上乗せ。これを ignore すると WACC を 200bp 過小評価する。

---

## 3. Covenants (借入契約条項)

### 3.1 Financial Covenants (財務 covenant)

#### 3.1.1 Leverage Ratio

```
Total Leverage = Total Debt / LTM EBITDA
Net Leverage = (Total Debt − Unrestricted Cash) / LTM EBITDA
Senior Leverage = Senior Secured Debt / LTM EBITDA
First Lien Leverage = First Lien Debt / LTM EBITDA
```

- **Threshold**: Leveraged loan で **< 4〜6x**、HY bond で **< 6〜8x**、growth credit で **< 8x** (high-quality SaaS)。
- **Step-down**: 期間経過で threshold が下がる仕組み (例: Year 1: 6.0x / Year 2: 5.5x / Year 3: 5.0x)。
- **Covenant cushion**: Threshold − Actual。15% 未満は warning。
- **EBITDA Add-backs**: SaaS で **stock-based compensation**, **non-recurring items (litigation, restructuring)**, **pro-forma cost savings (run-rate synergies)**, **transaction expenses** が一般的に許容。"Adjusted EBITDA" の定義は契約書 Schedule で 1〜3 ページ占める。

#### 3.1.2 Interest Coverage Ratio (ICR)

```
ICR = LTM EBITDA / LTM Interest Expense
Cash ICR = LTM EBITDA / LTM Cash Interest (excludes PIK)
```

- **Threshold**: > 2.0〜3.0x が leveraged loan、> 1.5〜2.5x が HY bond。
- **Fixed Charge ベース** (FCCR との違い): ICR は principal repayment を含まない。

#### 3.1.3 Fixed Charge Coverage Ratio (FCCR)

```
FCCR = (LTM EBITDA − CapEx) / (LTM Interest + Scheduled Principal + Lease Payments)
```

- **Threshold**: > 1.0〜1.25x が standard、> 1.10x が tight。
- ABL や middle-market bank loan で多用される。
- 一部の契約は CapEx を maintenance CapEx (= D&A の 80〜100%) に限定し、growth CapEx を除外する。

#### 3.1.4 Debt Service Coverage Ratio (DSCR)

```
DSCR = CFADS / Debt Service
CFADS (Cash Flow Available for Debt Service) = EBITDA − CapEx − Tax − ΔWC
Debt Service = Cash Interest + Mandatory Principal Repayment + Lease
```

- **Threshold**: > 1.20〜1.40x、real estate / project finance で > 1.20x、SaaS で > 1.50x が typical。
- **Period**: rolling 12 months または look-forward 12 months。
- LBO model や project finance で核となる metric。

#### 3.1.5 Minimum Liquidity / Minimum Cash Balance

- **Threshold**: 6〜12 ヶ月 burn equivalent または絶対額 ($5M, $10M, $20M etc.)。
- Venture debt では **6 ヶ月 burn floor** が典型 (Bessemer 推奨)。
- "Liquidity" の定義: cash + RCF availability (一部は restricted cash 除外)。

#### 3.1.6 Maximum CapEx

- 年間 CapEx に cap。例: $10M/年または revenue × 8%。
- Carry-forward 条項: 未使用分を翌年に繰越可。

#### 3.1.7 Minimum ARR / Revenue (SaaS-specific)

- Venture debt 専用。各 tranche draw 時にも check される。
- Trailing 3-month ARR ≥ X、または LTM Revenue ≥ X。
- **Recurring Revenue Loan (RRL)** という商品では ARR multiple 自体が借入余力。

### 3.2 Negative Covenants (制限的 covenant)

| 項目 | 典型条項 | 例外 (carve-out) |
|---|---|---|
| 追加借入禁止 | Senior 追加禁止、capacity ratio 内のみ | RCF, capital lease, equipment financing $X/年 |
| Liens (担保設定) | Permitted Liens 列挙以外禁止 | Tax, judgment, lease, equipment lien |
| Asset Sales | $X 超売却禁止 / proceeds prepay 義務 | OBC (Ordinary Business Course), de minimis, intra-group |
| Material change of business | 業種変更禁止 | line extension OK |
| Restricted Payments (RP) | 配当・自己株・equity buyback 禁止 | builder basket, GP basket, tax distribution |
| Investments | M&A、JV 禁止 / cap | builder basket, ratio basket, permitted investments |
| Affiliate transactions | 関連当事者取引 fair value で arm's length | de minimis, tax-driven |
| Sale-Leaseback | 一定額超禁止 | 一部例外 |
| Subsidiary debt | 子会社の追加 debt 禁止 | working capital line OK |
| Issuance of disqualified stock | mandatory redemption preferred 禁止 | qualified preferred は OK |
| Dividends | senior debt 残存中は禁止 | 上記 RP basket と連動 |

#### 3.2.1 Builder Basket / GP Basket

- **Builder Basket**: 累積 net income (50% など) または cumulative EBITDA (一定 multiple) を分子に、cumulative restricted payments を分母にした basket。利益が出た分だけ dividend / buyback / investment 余力が増える。
- **GP Basket (General Permitted)**: 一定額の固定 cap (例: $50M)。

#### 3.2.2 Ratio-based Capacity

- "Permitted by ratio": leverage ratio が Z 以下なら追加 debt / RP / investment を許容。
- 例: "可能 if Total Leverage ≤ 4.0x and ICR ≥ 2.5x"。

### 3.3 Affirmative Covenants (積極的 covenant)

| 項目 | 内容 |
|---|---|
| Reporting | 月次 financial statement (内部用)、四半期 covenant compliance certificate、年次 audited financial |
| Audit | 年次 監査済 (Big 4 or Top 10)。Series B+ debt では mandatory |
| Insurance | D&O、E&O、Property、Cyber、適切な額面 |
| Compliance with law | Federal/state law、tax compliance、environmental |
| Maintenance of properties | PP&E の reasonable maintenance |
| Lender visit / inspection | 年 1〜2 回の plant visit / book inspection 権 |
| Notification of default | trigger 発生時の notice 義務 (5〜10 営業日内) |
| Hedging | rate hedge を一定額以上 mandatory にするケース |
| Maintenance of corporate existence | 解散・清算禁止 |
| Use of proceeds | facility 目的を制限 (例: WC, refinance, acquisition) |

### 3.4 Covenant Cushion 計算

```
Cushion % = (Threshold − Actual) / Threshold  [for max-type, e.g., leverage]
Cushion % = (Actual − Threshold) / Threshold  [for min-type, e.g., ICR]
```

| Cushion レベル | 意味合い | 推奨対応 |
|---|---|---|
| > 30% | Comfortable | 通常運営 |
| 15〜30% | OK | 監視強化 |
| 5〜15% | Tight | Plan B 準備 |
| 0〜5% | Warning | Sponsor / lender 早期 dialogue |
| < 0% | Trip | Cure / Waiver / Amendment 必要 |

### 3.5 Cure Rights / Equity Cure

#### 3.5.1 Equity Cure

- **Sponsor (PE) が equity を注入し、それを EBITDA に加算 (or debt 返済)** することで covenant trip を治す権利。
- **回数制限**: 通常 4 回 / 期間中、連続 2 回禁止。
- **Dollar cap**: notional EBITDA cure 額に cap (例: $10M / 期間)。
- **EBITDA cure か Debt prepay cure か**: lender 有利は debt prepay (実際に debt 削減)、borrower 有利は EBITDA cure (notional 加算のみ)。
- **会計**: cure 注入は equity issuance として APIC 増加、CFF で +cash。EBITDA cure は covenant calc 専用 (GAAP EBITDA は変わらない)。

#### 3.5.2 Cure Limitations

- **Look-back**: cure 後の covenant calc は現行期と直前 3 期の compliance を確認。
- **Mandatory prepay**: cure 額は原則 debt prepay に充当 (sponsor 投入分を debt 返済に回す)。

### 3.6 Maintenance Covenants vs Incurrence Covenants

| 軸 | Maintenance Covenant | Incurrence Covenant |
|---|---|---|
| Test 頻度 | 毎期 (四半期) | 特定 action 時のみ (debt issuance, RP, M&A) |
| Trip 結果 | Default | Action 不可 (existing debt は無関係) |
| 適用商品 | TLA, RCF, ABL, Venture Debt | TLB (cov-lite), HY Bond |
| 例 | Leverage ≤ 5x 毎期 | 追加 debt 発行可 if Leverage ≤ 4x at incurrence |

### 3.7 MAC (Material Adverse Change) Clause

- **定義**: borrower の business / financial / prospects に "material adverse" な変化があった場合、lender が default 宣言可能。
- **問題点**: lender 側に過剰な裁量。COVID-19 直後など、ambiguous な状況で発動懸念。
- **強い借手**: MAC を **削除**、または "demonstrable, quantitative material adverse" に限定。
- **Carve-out**: industry-wide event、sponsor change of control 以外、規制変更などを除外。

---

## 4. Credit Metrics (信用指標)

### 4.1 Leverage Metrics

| Metric | 計算式 | 用途 | 典型 threshold |
|---|---|---|---|
| Total Leverage | Total Debt / LTM EBITDA | 総合 | < 4〜6x leveraged, < 7x highly |
| Net Leverage | (Total Debt − Cash) / LTM EBITDA | より関連性高い | < 3.5〜5.5x |
| Senior Leverage | Senior Debt / LTM EBITDA | 担保付 | < 3〜4.5x |
| First Lien Leverage | First Lien / LTM EBITDA | 最高担保 | < 3〜4x |
| Total Debt / Total Cap | Total Debt / (Total Debt + Equity) | mix | < 50〜70% |
| Debt / Revenue | Total Debt / LTM Revenue | non-EBITDA model | < 1.5〜3x |
| Debt / Tangible Assets | Total Debt / (Tangible Assets) | ABL 系 | < 80% |

### 4.2 Coverage Metrics

| Metric | 計算式 | 典型 threshold |
|---|---|---|
| ICR | EBITDA / Interest | > 2〜3x |
| Cash ICR | EBITDA / Cash Interest (excl. PIK) | > 2〜3x |
| FCCR | (EBITDA − CapEx) / (Interest + Principal + Lease) | > 1.0〜1.25x |
| DSCR | CFADS / Debt Service | > 1.20〜1.40x |
| EBITDA-CapEx / Interest | (EBITDA − CapEx) / Interest | > 1.5x |

### 4.3 Liquidity Metrics

| Metric | 計算式 | 典型 threshold |
|---|---|---|
| Quick Ratio | (Cash + AR) / Current Liabilities | > 1.0 |
| Current Ratio | Current Assets / Current Liabilities | > 1.5 |
| Months of Liquidity | (Cash + Available Revolver) / Monthly Burn | > 12 ヶ月 |
| Cash / Total Debt | Cash / Total Debt | > 30% (high quality) |

### 4.4 SaaS-specific Credit Metrics

| Metric | 計算式 | 用途 |
|---|---|---|
| ARR / Total Debt | ARR / Total Debt | RBF / Venture Debt |
| ARR Multiple of Debt | Total Debt / ARR | < 0.5〜1.5x |
| LTV / Total Debt | LTV / Total Debt | unit economics check |
| CAC Payback / Debt Maturity | CAC payback months / Maturity months | < 50% |
| Burn Multiple | Net Burn / Net New ARR | 健全性、< 1 が良 |
| Rule of 40 | Growth % + EBITDA Margin % | > 40 % |
| NRR | Net Revenue Retention | > 110% (best in class) |

### 4.5 Synthetic Credit Rating (private companies)

- 各 metric を Moody's / S&P の rating grid にマッピングし、**synthetic rating** を算出。
- 例: BB rating の典型 = Net Leverage 4.0〜5.5x / ICR 2.0〜3.0x / FCCR 1.1〜1.4x / Margin 10〜20%。
- Lender は internal rating を debt pricing に使う。Agreement では rating grid に応じた step-up / step-down を spread に組込む。

### 4.6 LCD/Pitchbook の market benchmark (2026.5 想定)

- **Leveraged loan market average**: Total Leverage 5.5x、Senior Leverage 4.5x、ICR 2.5x。
- **High Yield Bond average**: Total Leverage 6.5x、ICR 3.0x。
- **Venture Debt (Hercules quarterly)**: typical issuer ARR multiple ~3〜5x、debt $5〜20M、duration 36 ヶ月。


---

## 5. Debt Schedule の Modeling

> 単一 facility の standard schedule、revolver plug、循環参照解消は `06_three_statement.md` §4 を継承。本章では **multi-tranche、cash sweep、mandatory prepay、PIK 三表波及、refinance、sensitivity** に絞る。

### 5.1 Multiple Tranche Modeling

#### 5.1.1 シート設計

`DebtSchedule` シートを **tranche × period** のマトリクスで構成。各 tranche に block を持たせる:

```
Block 1: TLA       — Beg Bal / Issue / Repay / Int / End Bal
Block 2: TLB       — 同上 + PIK accrual行
Block 3: RCF       — Avg Bal / Draw / Repay / Int / End Bal
Block 4: Senior Notes — coupon / call premium / End Bal
Block 5: Mezz / PIK   — Cash Int / PIK Int / End Bal
Block 6: Bridge / Other — flex
```

**サマリ block** で全 tranche の (a) 期初残高、(b) 利払合計、(c) 元本返済合計、(d) 期末残高、(e) Cash sweep 後の Free Cash Flow を集約。

#### 5.1.2 Cross-default 条項の影響

- **Cross-default**: 任意の facility で default 発生時、他 facility も default 扱い。
- **Cross-acceleration**: default 後に lender が "acceleration" を発動した時のみ trigger (slightly less aggressive)。
- **Modeling 上**: 一つでも covenant trip すると全 tranche の `Acceleration_t` フラグが立ち、期末残高が 0 → cash で全額返済 (or default scenario へ分岐) となる。Excel では `OR` で `IFERROR` を組合せ。

#### 5.1.3 Refinance を織り込む

```
=IF(EndOfPeriod_t = MaturityDate, RefiAssumed × OldBalance, ...)
RefiBalance_t+1 = OldBalance_t  ← roll
RefiInterest_t+1 = RefiBalance × NewSpread × DayCount
```

- New facility の terms (rate, tenor, fees) は別 input。
- Refinance fee (1〜2% × new face) を closing 時に IS の interest expense に計上 (or DIC として按分)。

### 5.2 Cash Sweep

#### 5.2.1 Excess Cash Flow (ECF) Sweep

- 借手が **超過 cash flow を mandatorily prepayment** する仕組み。Sponsor LBO では一般的。
- ECF 計算式 (典型):

```
ECF = Net Income
    + D&A
    + Deferred Tax
    − CapEx (maintenance + permitted growth)
    − Δ Working Capital
    − Mandatory debt amortization (already paid)
    − Permitted Restricted Payments
    − Other adjustments per credit agreement
```

- **Sweep %**: leverage に応じて step-down。例:

| Leverage | Sweep % |
|---|---|
| > 5.0x | 100% |
| 4.0〜5.0x | 75% |
| 3.0〜4.0x | 50% |
| < 3.0x | 25% (or 0%) |

- 適用順序: 通常 Senior → Mezz → 配当の優先順。Senior 内では First Lien → Second Lien。

#### 5.2.2 Excel 実装 (1 tranche の例)

```
[Year]                  Y1     Y2     Y3
EBITDA                  100    120    140
ΔWC                     -5     -10    -10
CapEx                   -20    -22    -25
Mandatory Princ.        -5     -5     -5
Cash Tax                -10    -15    -18
Cash Interest           -25    -22    -19
ECF (= sum)             35     46     63
Leverage start          5.0x   4.5x   3.8x
Sweep %                 100%   75%    50%
Sweep Amount            35     35     32
Beg Bal                 500    460    420
Mandatory Princ.        -5     -5     -5
Sweep Repayment         -35    -35    -32
End Bal                 460    420    383
```

#### 5.2.3 Sweep の典型 anti-pattern

- **100% 固定 sweep**: 現実は step-down が標準。100% 固定モデルは過剰に楽観 (deleverage が早すぎる)。
- **Sweep 後の WC 不足**: ECF を過大に sweep すると next year の WC が逼迫。Min cash floor を必ず設定。

### 5.3 Mandatory Prepayment Triggers

| Trigger | 通常 Sweep % | 例外 (reinvestment right) |
|---|---|---|
| Asset Sale Proceeds | 100% | 12〜18 ヶ月以内に再投資なら除外 |
| Insurance Proceeds | 100% | 同上 (reinvest 可) |
| Equity Issuance Proceeds | 50% (sometimes 100%) | Permitted issuance (ESOP, M&A) は除外 |
| Debt Issuance Proceeds | 100% | new debt が permitted refinancing なら除外 |
| Excess Cash Flow | step-down | 上述 |
| Change of Control | 101% put | bondholder put 権 (HY bond) |

### 5.4 PIK 利息 Mechanics と三表波及

#### 5.4.1 計算

```
Cash Interest = Principal × Cash_Rate
PIK Interest = Principal × PIK_Rate
Total Interest = Cash Interest + PIK Interest
Principal_t+1 = Principal_t + PIK Interest
```

#### 5.4.2 三表波及

- **IS (P&L)**: `Interest Expense = Cash Interest + PIK Interest` (両方 expense)。GAAP 上 Total expense は同じ。
- **CFS (CFO)**: 出発点 NI には full interest expense が引かれている → `Add back PIK Interest (non-cash)` を CFO に加算。CFS の Cash Interest だけが実際の cash 流出。
- **BS**:
  - Liability: `Long-term Debt_t = Long-term Debt_t-1 + PIK Interest_t − Repayment_t`。PIK 分が元本に積上がる。
  - Equity: 影響なし (IS 経由で RE 減少のみ)。

#### 5.4.3 Tax Shield の扱い

- **US**: PIK interest も deductible (Section 163)。ただし AHYDO (Applicable High Yield Discount Obligation, Section 163(i)) ルール: 5y 超 PIK で OID > AFR + 5%、yield > AFR + 6% なら一部 deduct 制限。
- **Japan**: 法人税法 22 条で「経済的利益」として **発生主義** で損金算入可。日本では PIK 慣行が稀なため tax case law 蓄積は薄い。

### 5.5 Debt 借換 (Refinancing) Modeling

#### 5.5.1 Modeling 手順

1. Maturity の 6〜18 ヶ月前に **refinance window** を設定。
2. 新 facility の terms (rate, tenor, fees) を別 input に。
3. Old facility の prepay (call premium がある場合は加算) → 新 facility issuance で同額 + α を得る。
4. Refi fees を **新 debt の DIC** として按分、old DIC の未償却分は **当期費用**。
5. Avg life の変更で WACD (Weighted Average Cost of Debt) も update。

#### 5.5.2 Refi が closed されないリスク

- Maturity wall が来る前に market 閉鎖 (例: GFC 2008、COVID 2020) → refinance 不可 → default。
- Modeling で **3 シナリオ** (Refi succeeds / Extend with higher rate / Default) を持つ。

### 5.6 Sensitivity Modeling

#### 5.6.1 Rate sensitivity

```
Sensitivity Table:
                  SOFR -200bp  SOFR -100bp  Base  SOFR +100bp  SOFR +200bp
Cash Interest      $5.0M       $6.0M        $7.0M  $8.0M       $9.0M
ICR                 4.5x        3.8x         3.3x   2.9x        2.6x
FCCR                1.5x        1.4x         1.3x   1.2x        1.1x
Covenant Headroom   +50%        +35%         +25%   +12%        −5% (Trip)
```

#### 5.6.2 EBITDA sensitivity

```
                  EBITDA -20%  -10%  Base  +10%  +20%
Net Leverage       5.6x        4.9x  4.5x  4.1x  3.8x
ICR                2.7x        3.0x  3.3x  3.6x  4.0x
Cushion (Lev<5)    -12%        +2%   +10%  +18%  +24%
```

#### 5.6.3 Two-way sensitivity (heat map)

- 縦軸 EBITDA growth、横軸 Rate changes、cell に **Covenant Headroom %** を表示。
- Red zone (cushion < 5%) を視覚的に identify。

---

## 6. Cost of Debt の計算

### 6.1 Pre-tax Cost (Tranche Level)

```
Pre-tax Cost (effective) = Coupon + OID/yr + Fees/yr + Warrant_EV/yr
                        + Prepay_Penalty_Adjustment (期待値)
```

- §2.7 の effective cost worksheet と一致。

### 6.2 Weighted Average Cost of Debt (WACD)

```
WACD_pre-tax = Σ_i (Tranche_i × Pre-tax Cost_i) / Total Debt
WACD_after-tax = Σ_i (Tranche_i × Pre-tax Cost_i × (1 − Tax_i)) / Total Debt
```

例:

| Tranche | Balance | Pre-tax Cost | Weight | Contribution |
|---|---|---|---|---|
| TLA | $10M | 7.0% | 6.7% | 0.469% |
| TLB | $80M | 9.5% | 53.3% | 5.063% |
| Senior Notes | $40M | 8.0% | 26.7% | 2.133% |
| Mezz (Cash + PIK) | $20M | 14.0% | 13.3% | 1.867% |
| **Total** | **$150M** | | | **9.532%** |

### 6.3 After-tax Cost

```
After-tax Cost = Pre-tax × (1 − Effective Tax Rate)
```

- US Federal + State combined ~ 25〜28%。
- Japan 実効税率 ~ 30〜34% (法人税 23.2% + 地方税 + 事業税)。
- After-tax WACD = 9.53% × (1 − 28%) = **6.86%**。

### 6.4 PIK の特殊扱い

- **GAAP IS**: PIK interest も interest expense として計上。
- **Tax**: US で は通常 deductible (例外 AHYDO は §5.4.3)。Japan も発生主義で deductible。
- **WACD への影響**: PIK 12% 全額の tranche は cash 流出 0 だが、tax shield は full coupon に適用 → after-tax cost = 12% × (1 − 28%) = **8.64%**。

### 6.5 Tax Shield Value (NPV)

```
Tax Shield NPV = Σ_t (Cash Interest_t + PIK Interest_t) × Tax Rate × DF_t
DF_t = 1 / (1 + r_unlevered)^t
```

- Modigliani-Miller の levered DCF approach で値段 (firm value) に加算。
- 完全 levered firm value = Unlevered firm value + Tax Shield NPV。

### 6.6 Restrictions on Tax Shield

- **§163(j) Limitation (US, TCJA 2017〜)**: Net Interest Expense > **30% of EBIT (post 2022)** は deduct 不可。Carryforward 可。
- **Japan 過大支払利子税制 (法 66 条の 5 の 2)**: 関連者間 net interest > **20% of 調整所得金額** は損金不算入。
- スタートアップは EBITDA がマイナスなら tax shield value はゼロ (carryforward しても破綻時消滅)。

---

## 7. Debt Capacity Analysis

### 7.1 EBITDA-based Capacity

```
Max Debt = EBITDA × Industry Multiple
```

| Industry / Quality | Multiple |
|---|---|
| Best-in-class SaaS (NRR>120%, Rule of 40) | 7〜9x |
| Average SaaS | 5〜7x |
| D2C (recurring) | 4〜6x |
| Hardware / B2C cyclical | 3〜4x |
| LBO sponsor-backed | 6〜8x (Total) |
| Distressed | 1〜3x |

### 7.2 ARR-based Capacity (SaaS)

```
Max Debt = NTM ARR × ARR Multiple
```

- Venture Debt: 0.25〜0.75x of NTM ARR (RBF 系は ≤ 1.0x)。
- Recurring Revenue Loan (RRL): 1.0〜1.5x of NTM ARR (high-quality only)。
- Lender 側の rule: "Debt should be repayable from 12 months of run-rate gross profit"。

### 7.3 FCF-based Capacity (DSCR Approach)

```
Max Debt Service = CFADS / Min DSCR
Max Debt (level pmt) = Max Debt Service × Annuity Factor (rate, tenor)
Annuity Factor = [1 − (1+r)^(−n)] / r
```

例: CFADS $50M、Min DSCR 1.40x、SOFR + 4% = 8.30%、7y amortizing:

```
Max Debt Service = $50M / 1.40 = $35.7M / 年
Annuity Factor (8.30%, 7y) = [1 − 1.083^(-7)] / 0.083 = 5.143
Max Debt = $35.7M × 5.143 = $183.6M
```

### 7.4 Asset-based Capacity (ABL formula)

```
Borrowing Base = AR_eligible × 0.80 + Inventory_eligible × 0.50 + Equipment × 0.65
```

例: AR $10M (90% eligible)、Inventory $5M (80% eligible)、Equipment $3M:

```
BB = 9.0M × 0.80 + 4.0M × 0.50 + 3.0M × 0.65
   = 7.2M + 2.0M + 1.95M
   = $11.15M
```

### 7.5 Real Estate / LTV

```
Max Debt = Real Estate Value × LTV
LTV = 65〜75% (commercial), 50〜65% (special-use, e.g., data center)
```

### 7.6 Layering Multiple Sources

スタートアップ実務では複数 source を **stack** する:

```
Total Available =
    Venture Debt (ARR × 0.4)
  + ABL (Borrowing Base)
  + Equipment Financing (Equipment Value × 0.7)
  + Senior Term Loan (EBITDA × 3 if positive)
```

各 source の covenant が独立に走り、cross-default 条項で連動。最も tight な covenant が **binding** となる。

---

## 8. デフォルト・破綻処理

### 8.1 Default Triggers

| Trigger | 詳細 |
|---|---|
| Payment Default | 元利金の支払遅延。grace period (3〜30 営業日) あり |
| Covenant Default | financial covenant trip。grace period 通常 30 営業日 (cure 可) |
| Cross Default | 他 debt の default が trigger。$X 以上に limit |
| Cross Acceleration | 他 debt が accelerated されたときのみ trigger (= cross default の弱い版) |
| Bankruptcy / Insolvency | 自主申請 or 強制申請 |
| Material Misrepresentation | reps & warranties の重大な虚偽 |
| Change of Control | sponsor change / 50% equity 移動 |
| Failure of Reporting | 30〜90 日 financial 提出遅延 |

### 8.2 Workout / Restructuring (Out-of-court)

#### 8.2.1 Standstill Agreement

- Lender が一定期間 (typical 30〜90 日) **acceleration を発動しない** 約束。
- 借手は修正計画提出、新 sponsor 探索、asset sale など。
- Forbearance fee 0.25〜1% を payable。

#### 8.2.2 Debt-for-equity Swap

- Senior の一部または全額を equity に転換。
- Sponsor 既存 equity は **wipe-out** (大幅希薄化または ゼロ化)。
- 新 sponsor cash injection と組合せが普通。

#### 8.2.3 Covenant Waiver / Amendment

- Lender が covenant を **一時的に緩和** または permanently amend。
- 通常 amendment fee 0.25〜1% を payable。
- Lender 過半数 (50%+1 to 100%) の同意が必要。Sacred rights (rate, principal, maturity, collateral) は **100% 同意 (unanimous)**。

#### 8.2.4 Maturity Extension

- Maturity を 1〜3 年延長。Coupon は通常 50〜200bp step-up。
- "Amend & Extend" (A&E) と呼ばれる典型 transaction。

### 8.3 Bankruptcy

#### 8.3.1 US — Chapter 7 vs Chapter 11

| 項目 | Chapter 7 | Chapter 11 |
|---|---|---|
| 性格 | 清算 (liquidation) | 再生 (reorganization) |
| 経営権 | Trustee に移管 | Debtor-in-possession (DIP) で経営継続 |
| 期間 | 数ヶ月〜1年 | 1〜3 年が普通 |
| 結果 | 資産売却、按分弁済 | Plan of Reorganization で resume |
| 対象 | 個人 + 中小 | 主に企業 |

**Absolute Priority Rule (APR)**:
1. Administrative claims (DIP financing, professional fees)
2. Secured claims (担保権者)
3. Priority unsecured (tax, employee wages 一部)
4. General unsecured (vendors, bonds)
5. Subordinated debt
6. Preferred equity
7. Common equity (typically wiped out)

#### 8.3.2 Japan — 民事再生 / 会社更生 / 破産

| 制度 | 性格 | 経営権 | 適用 |
|---|---|---|---|
| 破産 (破産法) | 清算 | 破産管財人 | 個人 + 法人、終結型 |
| 民事再生 (民事再生法) | 再生 | 再生債務者 (DIP 同等) | 中小〜中堅、speed 速い |
| 会社更生 (会社更生法) | 再生 | 更生管財人 | 大企業、stakeholder 多 |
| 特定調停 | 私的整理 | 経営者 | 軽度、scheme 簡易 |
| 事業再生 ADR | 私的整理 | 経営者 | 中堅、税制優遇あり |

担保権の取扱: 民事再生では **別除権** として担保権者は手続外で実行可。会社更生では **更生担保権** として手続内に組込み、経営権整理の一部となる。

#### 8.3.3 DIP Financing

- **Debtor-in-possession financing**: 破産手続中の運転資金を新規 lender が出す。
- **Super-priority claim** (US Chapter 11)、既存 secured creditor よりも優先。
- 年率 typically Prime + 500〜1,000 bps (12〜18%)。
- Japan では「共益債権」として通常 debt よりも優先 (民事再生法 119 条)。

### 8.4 Recovery Rates (LCD/Pitchbook 統計)

| 商品 | Avg Recovery (US, 2010-2024) |
|---|---|
| First Lien Bank Debt | 65〜80% |
| Second Lien | 45〜55% |
| Senior Unsecured Bond | 35〜45% |
| Subordinated Bond | 20〜30% |
| Mezz | 15〜25% |
| Preferred Equity | 5〜15% |
| Common Equity | 0〜5% |

Japan では実証データが乏しいが、メインバンク主導の私的再生で senior recovery ~70〜85% が想定値。

---

## 9. Equity-linked Features

### 9.1 Warrants

#### 9.1.1 構造

- **Strike Price**: 行使価格。priced round の price または fixed amount。
- **Coverage**: 上述。Facility size の % を warrant face value に換算。
- **Term (期間)**: 7〜10 年が typical。Maturity と無関係 (debt 返済後も warrant 残存)。
- **Vesting**: 通常即時 (issuance 時に full vest)。
- **Cashless Exercise**: 株式と引換に warrant を消却し、差額相当の株式を交付。
- **Anti-dilution**: 一部 warrant は full ratchet または broad-based weighted average の anti-dilution を持つ。

#### 9.1.2 Dilution 計算

```
Warrant Shares = Warrant Face Value / Strike Price
Dilution % = Warrant Shares / (Total Shares Outstanding + Warrant Shares)
```

#### 9.1.3 Lender 観点での EV uplift

- Lender 側は warrant の Black-Scholes 価値を **expected upside** として認識。
- 借手 IPO / M&A 時に exercise → liquidation proceeds から取得。
- Lender の "all-in IRR" target は 15〜18%。Coupon (10〜13%) + warrant value (3〜5%) で構成。

### 9.2 Conversion Rights

#### 9.2.1 Optional vs Mandatory

- **Optional (= 借手側 choice)**: 借手が任意で convert 可能。Convertible Note に多い。
- **Mandatory (= trigger 起動)**: 一定 event (qualified financing, IPO, M&A) で自動 convert。
- **Conversion Price**:
  - Convertible Note: max(Cap Price, Discount × Series Price)
  - Mandatory Convert Bond: floor / ceiling 範囲内で固定 ratio

#### 9.2.2 Trigger Events

- Qualified Financing (例: $5M+ raised at >$30M post)
- IPO (= QPO, Qualified Public Offering)
- Change of Control
- Maturity (default conversion)

### 9.3 Equity Kicker

#### 9.3.1 Success Bonus

- Exit (M&A, IPO) 達成で lender が固定額または equity ratchet を受領。
- 例: 「Exit value > $500M なら lender は $5M 追加 bonus」。

#### 9.3.2 IRR-based Payment

- Sponsor IRR が一定水準を上回ると lender にも追加 distribution。
- Mezz / Bridge financing で時々見られる。

#### 9.3.3 Royalty / Revenue Sharing (post payoff)

- Debt payoff 後も一定期間 revenue % を支払。
- Pharma / IP-heavy financing で時折使用。


---

## 10. 日本固有の Debt 環境

> 一般的な日本会計・税制論点は `07_japan_specifics.md` を参照。本章は **debt 商品** 固有の論点に集中する。

### 10.1 日本政策金融公庫 (JFC) — Japan Finance Corporation

#### 10.1.1 主要メニュー

JFC は政府系金融機関で、創業期スタートアップに最も使われる debt source。2026 年 5 月時点の主要商品:

| 商品名 | 対象 | 上限 | 期間 | 利率 |
|---|---|---|---|---|
| 新規開業・スタートアップ支援資金 | 創業前 / 創業後 5 年以内 | 7,200 万円 (うち運転 4,800 万) | 設備 20 年 / 運転 10 年 | 基準利率 2.30〜4.30% (担保あり) / 3.25〜4.65% (担保なし) |
| 新事業活動促進資金 | 経営革新計画 / 第二創業 | 7,200 万円 | 同上 | 同上 |
| 中小企業経営力強化資金 (廃止予定 → 統合) | 認定支援機関 経由 | 7,200 万円 | 同上 | 特別利率 |
| 資本性ローン (挑戦支援資本強化) | DDS 型劣後ローン | 1 億円〜 | 5〜20 年 (期限一括) | 業績連動 (赤字 0.5%、黒字 6.95% 等) |
| 女性、若者/シニア起業家支援資金 | 35 歳未満 / 55 歳以上 / 女性 | 7,200 万円 | 同上 | 特別利率 (基準より 0.65% 引下) |
| マル経融資 (商工会議所推薦) | 商工会会員、無担保無保証 | 2,000 万円 | 設備 10 年 / 運転 7 年 | 約 1.20% (経営改善) |

> **2024 年 4 月制度改正の要点**: 「新創業融資制度」(創業前後 限定的) は **廃止**、「新規開業・スタートアップ支援資金」に統合。創業者の自己資金要件 (1/10) も撤廃され、間口拡大。

> **2026 年 3 月時点利率**: 基準利率 (担保なし) 3.25〜4.65%、(担保あり) 2.30〜4.30%。スタートアップ向け創業支援貸付利率特例制度で **−0.65%** 引下。女性・35 歳未満・55 歳以上などで特別利率 A (担保なし 2.70〜4.30%) 適用可能。

#### 10.1.2 担保・保証要件

- **無担保 / 経営者保証なし** が原則化 (2014 年 経営者保証ガイドライン以降、2023 年改定で更に強化)。
- **無担保枠**: 商品により最大 4,800 万円 (2026.5 時点)。
- **保証人**: 法人の代表者を経営者保証ありで取る選択肢 (利率 0.1% 引下) と、保証なし (利率そのまま) の選択肢が併用される。
- **担保**: 設備融資では設備に抵当権、不動産担保、有価証券担保が選択可。

#### 10.1.3 資本性ローン (劣後ローン, DDS 型)

- **特徴**:
  - **期限一括返済 (bullet)** で運用期間中の元本返済不要。
  - **業績連動利率**: 直近期の赤字なら 0.5% (定額)、黒字累進的に 2.6% / 4.95% / 6.95% 等。
  - **DDS (Debt-Debt Swap) 効果**: 民間金融機関の評価上は **資本に準ずる** 扱い (= 自己資本性)、民間 debt 余力を増す。
  - 期間 5 / 7 / 10 / 15 / 20 年。期限到来で全額返済。
- **モデリング**:
  - 利率は **当期純利益のシグナル** で決定 → tax 計算後 NI を input に必要。
  - BS では「長期借入金」として表示 (legally debt) だが、注記で「資本性借入金」として開示。
  - 三表波及: 借入金 (BS LT Debt) +、現金 +。利息 (低水準) → IS interest expense。返済は maturity 時 lump sum。
  - シミュレーションでは「赤字期 0.5% / 黒字期 6.95%」の switch を `IF([NI]<0, 0.5%, 6.95%)` で実装。

#### 10.1.4 申請プロセスと留意点

- 申請から融資実行まで **3〜6 週間** が標準。
- 必要書類: 事業計画書、創業計画書、見積書、納税証明書、自己資金エビデンス、月次試算表 (creating period 後)。
- 創業計画書は JFC の所定 format。「動機 / 経営者経歴 / 商品サービス内容 / 取引先 / 借入状況 / 必要資金 / 事業見通し」を 8 項目で要約。
- **典型的失敗**: 自己資金要件の理解不足 (改正で撤廃されたが、実務上は 1/10〜1/3 を持っている方が審査有利)、面談で数字を答えられない、楽観過剰な計画。

### 10.2 信用保証協会

#### 10.2.1 制度概要

- 各都道府県・政令市・中小企業業種別に **52 協会** (2026.5 時点)。
- **公的保証付融資** (民間銀行が融資、保証協会が保証)。中小企業の信用補完。
- 保証範囲: **80% 部分保証** が基本、**100% 保証**は特定 product (セーフティネット保証 4 号 / 5 号、危機関連保証等)。

#### 10.2.2 保証料率

- **2026.5 時点** のスタンダード保証料率: **0.45〜1.90%** (信用区分 9 段階)。
- 制度融資では自治体補助で実質 0.20〜0.80% に低減するケースあり。
- 担保あり / なし、経営者保証あり / なし で differentiated。

#### 10.2.3 セーフティネット保証

- **4 号**: 災害・自然災害 (例: 能登半島地震、コロナ禍) で 100% 保証、別枠 2.8 億円。
- **5 号**: 不況業種、80% 保証、別枠 2.8 億円。
- **危機関連保証**: 大規模危機 (リーマン、コロナ) で 100% 保証、別枠 2.8 億円。
- 2024〜2026 年に COVID-19 関連の据置期間明けで返済再開、**ゼロゼロ融資 (実質無利子無担保) の借換需要** が発生。借換保証 (コロナ借換保証等) が拡大中。

#### 10.2.4 経営者保証なし融資の拡大

- **経営者保証ガイドライン (2014 年)** → 2023 年改定で「**経営者保証ありき** の融資慣行から脱却」を明記。
- **経営者保証ガイドラインの利用実績**: 2025 年度 (令和 7 年度) 統計で、新規融資の経営者保証なし比率が政府系 60%+、民間銀行 40%+ に到達。
- スタートアップは特に「経営者保証なし」を default で交渉すべき。
- **ガイドラインの 3 要件**:
  1. 法人と個人の財産分離 (役員報酬・配当が適切、私的流用なし)
  2. 適時適切な情報開示 (月次試算表、事業計画)
  3. 法人のみの資産・収益力で借入返済可能

### 10.3 商工組合中央金庫 (商工中金)

- 政府系金融機関で、中堅・中小企業向け。スタートアップは Series B+ 以降で利用機会。
- **危機対応融資**: 政府指定危機 (大規模災害・金融危機) 時の指定金融機関として運営。
- 商品: 一般融資、設備資金、運転資金、危機対応、特別融資、メザニン (商工中金メザニン投資)。
- 利率: 商業銀行と JFC の中間水準 (TIBOR + 100〜250 bps 想定)。

### 10.4 日本政策投資銀行 (DBJ)

- 政府系大型金融機関。スタートアップ用には dedicated メニューは少ないが、**メザニン / 劣後ローン / 構造化 financing** を late-stage で活用。
- **DBJ ベンチャー投資ファンド** + **DBJ 競争力強化ファンド** などで equity / mezz の組成。
- ticket size は ¥500M〜¥10B 規模。Pre-IPO や carve-out / spin-out で multi-tranche 構成を組む。

### 10.5 民間銀行融資

#### 10.5.1 メガバンク

| 銀行 | スタートアップ姿勢 |
|---|---|
| 三菱 UFJ 銀行 (MUFG) | "Garage" startup ハブ運営、Innovation Banking 部門あり、Series B+ で取引 |
| 三井住友銀行 (SMBC) | Future of Finance、海外 LP との connectivity 強い、IPO 準備期に強み |
| みずほ銀行 | Mizuho Innovation Frontier、CVC との連携 (Mizuho Capital) |
| りそな銀行 | 中堅向け、地域 startup と密着 |

メガバンクは pre-Series A まではほぼ取引せず (信用枠 limit)、Series A 後に当座貸越 / RCF / 設備資金で取引開始。Series C+ で venture debt (¥1B+) を提供する流れ。

#### 10.5.2 ネット銀行 / 新興系

| 銀行 | 特徴 |
|---|---|
| PayPay 銀行 | 法人ビジネスローン、AI 審査、ネット完結 |
| 楽天銀行 | 同上 |
| 住信 SBI ネット銀行 | 同上、UI 良好 |
| 商工中金 / SBI 新生 | 中堅ベンチャー向け |
| GMO あおぞらネット銀行 | スタートアップ向け、API 銀行 |
| GMO エポス銀行 | small ticket |

ネット銀行は ¥10M〜¥100M の運転資金 line を提供。審査が早く、AI ベースの credit scoring が普及。スタートアップ向け事業性融資は徐々に拡大中。

#### 10.5.3 地銀・第二地銀

- 地域に紐づくスタートアップ (地元での雇用、地域貢献) と密接。
- 静岡銀行、横浜銀行、千葉銀行、北國 FHD 等が積極姿勢。
- 大学発ベンチャーは大学のある地域の地銀との connectivity が重要。

### 10.6 ベンチャーデット in Japan (詳細)

#### 10.6.1 主要プロバイダー

| プロバイダー | 形態 | チケット | 特徴 |
|---|---|---|---|
| あおぞら銀行 ベンチャーデット | 銀行 | ¥500M〜¥3B | 国内専業最大手。Warrant coverage 5〜10% |
| 三井住友信託銀行 ベンチャーデット | 信託銀行 | ¥500M〜¥3B | 信託グループの厚み |
| みずほ銀行 ベンチャーデット | メガバンク | ¥1B〜¥5B | Late-stage 中心 |
| SBI 新生銀行 ベンチャーデット | 銀行 | ¥300M〜¥2B | 中堅ベンチャー |
| INCJ (旧 産業革新機構) | 政府系 | ¥500M〜¥10B | メザニン主体 |
| GLOBIS Capital Partners (Debt Fund) | ファンド | ¥300M〜¥1B | 一部 debt 商品提供 |
| 三菱 UFJ 銀行 (Innovation Banking) | メガバンク | ¥500M〜¥3B | Garage hub 経由 |

#### 10.6.2 国内 Venture Debt の特徴

- **Warrant 慣行が薄い**: 米国比で warrant coverage は 0〜5% が中心 (米国 5〜10%)。代わりに **stock acquisition rights (新株予約権)** または **success fee** (3〜5%) で economics 補完。
- **Personal guarantee**: 経営者保証ガイドラインで原則なし方向だが、創業者の "moral hazard" を防ぐため一部 lender が要求するケース残存。
- **Tenor**: 24〜36 ヶ月が中央値 (米国は 36〜48 ヶ月で長め)。
- **利率**: TIBOR / TONA + 250〜400 bps が中堅、+ 400〜700 bps が aggressive。米国比でだいぶ低い (絶対水準で 3〜7% all-in)。
- **Covenant**: financial covenant は緩め (cash floor のみが多い)、reporting と negative covenant が厚い。
- **市場規模**: 2025 年度の国内ベンチャーデット推計 ¥80B〜¥150B (推定値、INITIAL ベンチャーデット動向)、米国 $30B+ と比較して 1/15〜1/30 規模。

### 10.7 経営者保証ガイドライン (2014 年〜)

#### 10.7.1 経緯

- **2013 年 12 月公表**、**2014 年 2 月適用** 開始。中小企業庁・金融庁・商工会議所が共同で策定。
- **2022 年改定** (2023 年 4 月施行): 民間銀行・公的金融機関とも、経営者保証なし融資を default 設計に。
- **2023 年 11 月**: 政府は「**経営者保証改革プログラム**」を更新、2025 年度までに新規融資の経営者保証なし比率 60% を目標。
- **2024 年 7 月施行 改正中小企業金融円滑化法**: 経営者保証を求める場合の **理由の文書化** を金融機関に義務付け。

#### 10.7.2 3 要件

1. **法人と個人の資産分離**: 役員貸付なし、配当 / 役員報酬適切、私的流用なし。
2. **財務基盤の安定**: 自己資本比率 ≥ 20%、債務償還年数 ≤ 10 年など (個別判定)。
3. **適時適切な情報開示**: 月次試算表、年次決算、事業計画の定期提出。

#### 10.7.3 廃業時の弁済負担軽減

- 「特定債務者の保証等に係る特定調停手続」で **個人保証履行を 3 年分の生計費 + 自宅** まで保護。
- 経営者の再起を支援する制度設計。

#### 10.7.4 モデリング上の影響

- **シナリオ分岐**: 経営者保証あり / なしで信用 spread が 50〜100 bps 異なる場合がある。
- **創業者の risk**: 保証あり debt は founder の personal balance sheet に隠れた liability となる。
- **新ガイドライン適用が standard**。古い model (2010 年代前半) を流用する際は要確認。

### 10.8 中小企業向け税制連動

#### 10.8.1 中小企業事業再編投資損失準備金

- 中小企業 M&A 推進税制 (令和 3 年度新設、令和 8 年度大綱で延長見込)。
- M&A で取得した株式の **70%** を準備金として損金算入可。5 年経過後に 5 年均等取り崩し益金算入。
- スタートアップが買収する側になった場合の cash flow 改善効果。

#### 10.8.2 経営力向上計画

- **中小企業等経営強化法** に基づく計画認定。
- 認定で固定資産税 1/2 軽減 (3 年間)、低利融資、信用保証枠拡大。
- 認定取得で JFC / 商工中金の特別利率 (基準より 0.5〜1.0% 引下) 適用可。

#### 10.8.3 賃上げ促進税制

- 給与増加額の 15〜45% を法人税控除。雇用拡大局面のスタートアップに有利。
- 中小企業 (資本金 1 億円以下) 限定の上乗せ控除あり。

### 10.9 その他 日本固有 debt 商品

- **動産担保融資 (ABL)**: 動産・債権譲渡特例法 (1998 年〜)。在庫・売掛債権を担保とする融資。
- **流動化スキーム**: 売掛債権 / リース債権の SPV 流動化、AR 平均化・early monetization。
- **私募債 (少人数私募社債)**: 縁故 50 名以下に対する社債発行。手続簡易、登記不要。中堅スタートアップで時折活用。
- **ソーシャル・ローン / グリーン・ローン**: ESG 連動ローン。脱炭素・社会課題スタートアップで取扱拡大。
- **暗号資産担保ローン**: 一部 fintech で提供 (BlockFi / Genesis 破綻後は限定的)。
- **NEDO 助成金返済型**: 一部 NEDO product で「事業化後 5 年以内 売上 % 返済」型がある。

---

## 11. Sample Debt Modeling (7 ケース)

各ケースで以下を提示する:
- 前提と取引概要
- Debt Schedule (利息 / 元本 / 残高)
- Covenant Check
- 三表 への影響
- IRR / Cost of Capital 影響

### Case 1: SaaS Series B with $5M Venture Debt + 8% warrant

#### 1-A. 前提

- **借手**: SaaS スタートアップ、ARR $8M (Series B 直後)、growth 80%/y、burn $1M/月。
- **Debt**: $5M facility, 36 months, IO 6 months then amortize 30 months straight-line.
- **Pricing**: SOFR + 750 bps (= 4.30% + 7.50% = 11.80%), Closing fee 1.0%, Backend fee 2.0%, Warrant 8% coverage strike $5/share.
- **Covenants**: Min cash $3M, MRR ≥ $500K (= ARR ≥ $6M), no MAC.
- **Use of proceeds**: 18 ヶ月 runway 延長 + S&M 加速。

#### 1-B. Debt Schedule (簡略月次→年表示)

| 期 | Beg Bal | Issue | Cash Int | Princ Repay | End Bal |
|---|---|---|---|---|---|
| Y1 (M1-12) | $0 | $5,000K | $499K (IO 6m + amort 6m) | $501K | $4,499K |
| Y2 (M13-24) | $4,499K | $0 | $464K | $2,000K | $2,499K |
| Y3 (M25-36) | $2,499K | $0 | $215K | $2,499K | $0 |
| **Total** | | $5,000K | $1,178K | $5,000K | $0 |

(注) Y1 内で IO 6 ヶ月 → amortize 30 ヶ月開始、Y1 後半 6 ヶ月で約 $501K 返済。Y2 で $2,000K、Y3 で $2,499K 返済する straight-line。

#### 1-C. Effective Cost

- Coupon 11.80% (cash int)
- Closing fee 1.0% / 3y = 0.33%/yr
- Backend fee 2.0% / 3y = 0.67%/yr
- Warrant: $400K face / strike $5 = 80,000 shares。BS 評価 σ=70%, T=7y, r=4% → ~$3/share → $240K → /3y/$5M = 1.60%/yr.
- **Total Effective Cost ≈ 14.40% pre-tax, 10.37% after-tax (28%)**

#### 1-D. Covenant Check

```
ARR check (Y2 end): $14M (= $8M × 1.8 growth)  ≥ $6M ✓ (cushion +133%)
Cash check (Y2 end): $4M (post operations) ≥ $3M ✓ (cushion +33%)
```

#### 1-E. 三表波及

- **IS**: Y1 Interest expense $499K + Backend fee accrual $33K + Closing fee accrual $17K = $549K, Y2 $498K, Y3 $248K。
- **BS**: LT Debt は schedule 通り、APIC に Warrant value $240K 計上 (issuance 時)。
- **CFS**: CFF で Y1 +$5,000K issuance、Y1〜Y3 で principal repay −$501/-$2,000/-$2,499K。CFO 内 add-back none (cash interest はそのまま expense)。

#### 1-F. IRR / Cost of Capital 影響

- Equity 同額 ($5M post $50M valuation想定 = 9.1% dilution) を取った場合との比較:

| 指標 | Venture Debt | Equity ($5M @ $50M post) |
|---|---|---|
| 即時 dilution | 0.8% (warrant 80K / 10M shares) | 9.1% |
| 累積 cost (3y) | $1.18M (interest) + $240K (warrant) = $1.42M | $5M × valuation step-up |
| Founder IRR | 高 (dilution 抑制 + leverage 効果) | 中 |
| Downside | covenant trip / default | なし |

> **示唆**: Series B で revenue が見えていれば venture debt が有利。ただし growth が想定通り続かないと covenant trip リスクが顕在化。

### Case 2: D2C with $3M ABL on AR + Inventory

#### 2-A. 前提

- **借手**: D2C ブランド、年商 $20M、AR $2.5M、Inventory $4M、growth 30%/y。
- **ABL**: $3M revolving facility on Borrowing Base.
- **Pricing**: SOFR + 400 bps (= 8.30%), Unused fee 0.50%, Closing fee 0.75%。
- **Covenants**: FCCR ≥ 1.10x、Min EBITDA $1M trailing 12-month、Concentration < 25%。

#### 2-B. Borrowing Base & Drawn

```
BB = AR_eligible × 0.85 + Inv_eligible × 0.50
   = $2.5M × 0.95 × 0.85 + $4M × 0.80 × 0.50
   = $2.02M + $1.60M
   = $3.62M (Capped at $3M facility)

Avg Drawn Y1 = $2.0M (peak season WC)
Avg Unused = $1.0M
```

#### 2-C. Debt Schedule

| 期 | Avg Drawn | Cash Int | Unused Fee | Total Cost |
|---|---|---|---|---|
| Y1 | $2.0M | $166K (8.30%) | $5.0K | $171K |
| Y2 | $2.5M | $208K | $2.5K | $210K |
| Y3 | $2.8M | $232K | $1.0K | $233K |

#### 2-D. Covenant Check

```
FCCR Y1 = (EBITDA $2M − CapEx $0.3M) / (Int $171K + Princ $0 + Lease $50K)
        = $1.70M / $221K = 7.69x ✓
```

#### 2-E. 三表波及

- **IS**: Cash interest as above。
- **BS**: ABL drawn (Current portion of LT Debt) + AR と Inventory にネット pledge 注記。
- **CFS**: CFF で revolver draw / repay の net 計上。

#### 2-F. 経済性

- **Equity 比較**: $3M を Series A で取ると 7.5%〜10% dilution (D2C valuation $30M 想定)。ABL は dilution ゼロ。
- **WC 改善**: AR collection 改善で BB 拡大、growth に追随しやすい。
- **典型的失敗**: 集中顧客 (Amazon channel) の eligible 計算違いで BB 過大評価 → Lender との dispute で BBC 修正 → 突然の WC 不足。

### Case 3: PE-backed Buyout — TLB $50M + Mezz $20M + Equity $80M

#### 3-A. 前提

- **Target**: B2B software 会社、EBITDA $20M (steady)、growth 8%/y、margin 35%。
- **Purchase Price**: $150M (= 7.5x EBITDA)。
- **Cap Stack**:
  - TLB: $50M, SOFR + 425 bps (= 8.55%), 7y bullet, 1% amort/y, 1% OID, 1% NC1.
  - Mezz: $20M, 11% cash + 3% PIK, 8y bullet, NC3, warrant 2% fully-diluted.
  - Sponsor Equity: $80M, 50% ownership post.
  - Mgmt rollover: $0M (full sale).
- **Total Debt / EBITDA = 70/20 = 3.5x**, **Cash interest coverage Y1 ~ 3.6x**.

#### 3-B. Debt Schedule (Y1〜Y5)

```
TLB ($50M, 1% amort, 8.55% cash):
Y1: Beg $50.0M / Amort -$0.5M / Int $4.27M / End $49.5M
Y2: Beg $49.5M / Amort -$0.5M / Int $4.23M / End $49.0M
Y3: Beg $49.0M / Amort -$0.5M / Int $4.19M / End $48.5M
Y4: Beg $48.5M / Amort -$0.5M / Int $4.15M / End $48.0M
Y5: Beg $48.0M / Amort -$0.5M / Int $4.10M / End $47.5M

Mezz ($20M, 11% cash + 3% PIK):
Y1: Beg $20.0M / Cash Int $2.20M / PIK $0.60M / End $20.6M
Y2: Beg $20.6M / Cash Int $2.27M / PIK $0.62M / End $21.2M
Y3: Beg $21.2M / Cash Int $2.33M / PIK $0.64M / End $21.9M
Y4: Beg $21.9M / Cash Int $2.41M / PIK $0.66M / End $22.6M
Y5: Beg $22.6M / Cash Int $2.49M / PIK $0.68M / End $23.2M
```

(Cash sweep を簡略化のため省略。本格 LBO では ECF sweep を組込む)

#### 3-C. Covenant Check (Y1)

```
Total Leverage = ($49.5M + $20.6M) / $20M EBITDA = 3.51x ≤ 5.50x ✓
ICR = $20M / ($4.27M + $2.20M cash int) = 3.09x ≥ 2.50x ✓
FCCR = ($20M - $1M CapEx) / ($6.47M cash int + $0.5M amort) = 2.73x ≥ 1.10x ✓
```

#### 3-D. Equity Returns (sponsor IRR)

- **Exit Year 5**: EBITDA $20M × 1.08^5 = $29.4M, Multiple expansion to 8.0x → EV $235M.
- **Net Debt at exit**: TLB $47.5M + Mezz $23.2M = $70.7M.
- **Equity to sponsor**: $235M − $70.7M = $164M (warrant 2% dilution → $161M).
- **Sponsor IRR** = ($161M / $80M)^(1/5) − 1 = **15.0%**.
- Mezz lender all-in IRR = cash 11% + PIK contribution + warrant value ≈ **17%**.

### Case 4: Pre-revenue Bridge Loan from existing investors $2M

#### 4-A. 前提

- **借手**: Pre-revenue SaaS、Series A close 後 18 ヶ月、burn $300K/月、cash $1M。
- **Bridge**: $2M, 6 month maturity, 8% interest accrued, convert at next priced round at 20% discount, MFN clause, no MAC.
- **Insiders**: 既存 Series A VC (3 社) が pro rata で出資。

#### 4-B. 6 ヶ月 schedule

```
M0: Issue $2.0M, Beg $2.0M
M3: Beg $2.0M, Accrued Int $40K, End $2.04M
M6: Beg $2.04M, Accrued Int $41K, End $2.08M (満期)
```

- **Conversion at next round**: 6 ヶ月内に Series B クローズ (post-money $40M、share price $4)。
- Conversion price = $4 × 0.80 = $3.20。
- Shares issued = $2.08M / $3.20 = 650,000 shares (= ~5% post B)。

#### 4-C. 三表波及

- **発行時**: BS LT Debt +$2M, Cash +$2M。
- **Accrual**: IS Interest expense / BS Accrued Interest +$40K/quarter。
- **Conversion**: BS LT Debt -$2.08M, APIC +$2.08M (non-cash)。CFS supplemental disclosure。

#### 4-D. シナリオ分岐

- **Round closes**: 上記。
- **Round 失敗 → maturity 到来**: insider の選択肢 = (a) maturity extend、(b) cash repay、(c) waterfall conversion (default trigger)。実務上は (a) extend 6〜12 ヶ月が standard。

### Case 5: 政策金融公庫 ¥30M 創業融資 (Japan startup)

#### 5-A. 前提

- **借手**: 創業 1 年目、Pre-revenue SaaS、創業者の自己資金 ¥10M、家族 + Angel 計 ¥20M。
- **Loan**: ¥30M、新規開業・スタートアップ支援資金、無担保、経営者保証なし。
- **Pricing**: 基準利率 (担保なし) 3.65%、創業支援貸付特例 −0.65% = **実質 3.00%**。
- **期間**: 設備 ¥10M (10 年) + 運転 ¥20M (7 年)。据置期間 12 ヶ月。

#### 5-B. Debt Schedule (年表示、運転 ¥20M 部)

```
Y1: 据置 (元本支払なし、利息のみ)
    Cash Int = ¥20M × 3.00% = ¥600K
    End Bal = ¥20M

Y2-Y7: 元利均等返済 (6 年)
    年間元利金 ≈ ¥3.69M (= ¥20M / annuity factor (3%, 6y) = ¥20M / 5.417)
    Y2 Int ¥600K, Princ ¥3.09M, End ¥16.91M
    Y3 Int ¥507K, Princ ¥3.18M, End ¥13.73M
    ...
    Y7 Int ¥107K, Princ ¥3.58M, End ¥0
```

(設備 ¥10M, 10 年 元利均等は別途 schedule。簡略化のため省略)

#### 5-C. Covenant 等

- 公庫融資は **maintenance covenant なし** (commercial bank と異なる)。
- 月次試算表提出 (creating period 後)、年次決算報告。
- Material 違反 (粉飾、目的外使用) で期限の利益喪失。

#### 5-D. 三表波及

- **IS**: 利息 ¥600K (Y1)。
- **BS**: 長期借入金 ¥20M、1 年内返済予定額を流動負債に区分。
- **CFS**: CFF で issuance +¥20M、Y2 以降 principal -¥3.09M〜。

#### 5-E. 経済性

- **All-in cost ≈ 3.00%** (closing fee なし、保証料なし、warrant なし)。
- **Equity 同額 ¥30M を Series Seed で取る場合の dilution** = 30M / (preMoney + 30M)。
  - 例: pre-money ¥150M なら dilution = 30/180 = 16.7%。
  - JFC 融資は dilution 0%。
- 低水準利率 + 経営者保証なしで、創業期 SaaS スタートアップにとって **非常に有利な debt 商品**。
- **典型的失敗**: 据置期間明けの返済 cash flow を読めず、Y2 以降に runway crunch。

### Case 6: RBF $1M for D2C with 6% revenue share, 1.5x cap

#### 6-A. 前提

- **借手**: D2C 美容ブランド、月次 revenue $200K (steady)、growth 50%/y、gross margin 65%。
- **RBF**: $1M advance、月次 revenue の 6% 返済、cap 1.5x = $1.5M total payback。
- **Pricing**: closing fee 2% upfront (= $20K)、no warrant。

#### 6-B. Repayment Schedule

```
M1-M3 (rev $200K/月): 6% × $200K = $12K/月、累計 $36K → 残 $1,464K
M4-M6 (rev $230K → $250K growth): avg $14K/月 = $42K/3M、累計 $78K → 残 $1,422K
...

Growth 50%/y で revenue 倍増を仮定すると、cap reach は M14 前後:
M14 累計 $1,500K reach → 終了

実効期間 14 ヶ月、effective IRR ≈ ($1,500/$1,000)^(12/14) − 1 = 41% / 年率
```

#### 6-C. 計算詳細

- 元本 $1M、cap $1.5M、period 14 month assumed → IRR ≈ 41%。
- もし growth が遅く 24 ヶ月で reach → IRR ≈ 22%。
- 平均的に 18 ヶ月想定で IRR ≈ 30%。

#### 6-D. 三表波及

- **IS**: 月次 revenue share 全額を **interest expense (financing cost)** として効率金利法で按分。$500K total finance charge を 14 ヶ月 (or 想定期間) で按分。
- **BS**: Notes payable $1M (issuance 時)、毎月減少。Closing fee は DIC として contra-liability。
- **CFS**: CFF で issuance +$980K (= $1M − $20K)、毎月返済を CFF で principal、interest 部分を CFO interest expense。

#### 6-E. 経済性 vs Venture Debt

| 軸 | RBF | Venture Debt |
|---|---|---|
| Effective rate | 30〜40% (growth 中) | 14〜16% |
| Dilution | 0% | 1〜3% (warrant) |
| Speed | 5〜14 日 | 30〜60 日 |
| Covenant | minimal | financial covenant あり |
| Cash flow | revenue 連動 | fixed amort |

> **示唆**: RBF は Venture Debt の **2〜3 倍コスト** 高いが、speed と minimal covenant の代償として理にかなう。短期 (12 ヶ月以内) の WC bridging で活用するのが合理的。

### Case 7: PIK Note $30M for late-stage with 12% PIK + 3% cash

#### 7-A. 前提

- **借手**: Late-stage SaaS、ARR $80M、EBITDA $5M (positive 直後)、growth 35%/y、IPO 18 ヶ月後想定。
- **PIK Note**: $30M Holdco PIK、5y bullet、12% PIK + 3% cash、warrant 1.5% fully-diluted、call premium NC2 / 105 / 102.5 / 100.
- **Sponsor**: 大手 Growth Equity (Tier-1)、equity $200M 既出資、PIK は recap distribution の原資。

#### 7-B. Debt Schedule

```
Y0: Beg $0 / Issue $30.0M / End $30.0M
Y1: Beg $30.00M / Cash Int $0.90M / PIK $3.60M / End $33.60M
Y2: Beg $33.60M / Cash Int $1.01M / PIK $4.03M / End $37.63M
Y3: Beg $37.63M / Cash Int $1.13M / PIK $4.52M / End $42.15M
Y4: Beg $42.15M / Cash Int $1.26M / PIK $5.06M / End $47.21M
Y5: Beg $47.21M / Cash Int $1.42M / PIK $5.66M / End $52.87M (Maturity)
```

5 年で **76% 増加** (= $52.87M / $30M)。

#### 7-C. 三表波及

- **IS**: Cash int $0.90M〜$1.42M、PIK int $3.60M〜$5.66M。**全額 expense**。
- **BS**: LT Debt は yearly compounded 増加。Equity (RE) は IS 経由で減少。Warrant は APIC に当初評価額。
- **CFS**: CFO で `+ PIK Interest add-back (non-cash)`、cash 流出は cash int のみ。

#### 7-D. Covenant Check

```
Y1: Total Leverage = $33.60M / $5M EBITDA = 6.7x ≤ 8.0x ✓
    Cash ICR = $5M / $0.90M = 5.6x ≥ 2.0x ✓
    Total ICR = $5M / ($0.90M + $3.60M) = 1.11x — TIGHT ✗ (threshold 1.5x の場合)
```

→ Total ICR をベースにすると Y1 で trip。Cash ICR ベースの cov 設計で trip 回避。

#### 7-E. 経済性

- **Sponsor 観点**: $30M PIK で immediate recap distribution → equity IRR 改善。元本は 5 年後 IPO proceeds で 返済。
- **Lender 観点**: All-in IRR ~ 17% (12% PIK + 3% cash + 1.5% warrant value)。
- **Dilution**: 1.5% warrant のみ。

#### 7-F. 失敗シナリオ

- **IPO 遅延**: IPO 想定 18 ヶ月が 36 ヶ月延伸 → PIK が ¥40M+ に膨張、refinance 必要。
- **Multiple compression**: IPO valuation が想定の 50% → debt/EV 比率が悪化、warrant value も落ちる。
- **Tax shield loss**: PIK の deduction が AHYDO で制限 → 想定 tax shield が 30% カット。


---

## 12. Anti-patterns (避けるべき)

### 12.1 Cash sweep を 100% 固定にする

- 現実は **leverage step-down** が標準。100% 固定モデルは deleveraging が早すぎ、Cash 残高 floor を下回り、WC が枯渇する scenario。
- **正しい実装**: Leverage 帯ごとに sweep % を `IF` または `VLOOKUP` で取得。最低 cash floor を設定し、`MIN(ECF − floor protect, sweep_amount)` で取る。

### 12.2 Covenant cushion を見ずに max leverage で借入

- "Lender が許容するから取る" 思考は危険。**business plan の downside scenario** で trip しないか確認すべき。
- Cushion 15% 未満は warning。30%+ を target に、leverage を絞ること。

### 12.3 PIK 利息を P&L から除外

- "Non-cash だから skip" は **誤り**。GAAP / IFRS / J-GAAP いずれも **interest expense** として計上必須。EBITDA 計算では加算 back されるが、interest line には含む。
- 税務上も deductible (US AHYDO 例外、Japan 過大支払利子税制 例外を除く)。

### 12.4 Warrant 価値を effective cost に加算しない

- Coupon が 11% でも、warrant 8% coverage で Black-Scholes value 50% を換算すると **all-in は 13〜15%** になる。
- 加算しないと WACD を 200〜400bp 過小評価、結果 WACC を低く見積もり、DCF 評価が過大になる。

### 12.5 Refinancing を仮定しすぎ

- "Maturity で refinance" は **市場が開いている前提**。GFC 2008 や COVID 2020 のように credit market が閉鎖されると refinance 不可。
- Stress scenario で **refinance 失敗 = default** を組込むべき。

### 12.6 Sponsor backing を assume

- Sponsor (PE / VC) は **法的義務として** 追加 equity を入れる契約はない (一部 equity contribution agreement 除く)。
- "Sponsor が出すだろう" を base case に組み込まず、sponsor exit / non-support の scenario も持つ。

### 12.7 経営者保証必須前提 (Japan)

- 2014 年経営者保証ガイドライン以降、**経営者保証なし** が default 方向に進化。
- 「公庫だから保証取られる」は古い前提。最新 2024 年改定で更に緩和。
- Founder の personal liability を model に入れる際は、**ガイドライン適合性** を確認。

### 12.8 円借入と外貨借入の同時処理での FX risk 無視

- USD denominated debt を円ベースの BS / IS に取り込む際、**期末 FX で換算 → 為替差損益** が発生。
- Hedge していなければ revenue が JPY、debt が USD で **mismatch**、円安で debt 急膨張。
- **正しい実装**: 通貨別 debt schedule を作り、月次 FX rate で換算、為替差損益を OCI / IS Other Income で別途計上。

### 12.9 IO 期間を recurring assumption にする

- "IO 6 ヶ月だから 6 ヶ月後に extend できる" 仮定は **危険**。Lender の裁量。
- IO 終了で amortization 開始 → 月次返済 cash が 5〜8x に増加 → cash crunch。
- IO 期間中に next round / refi の準備を実態として進めるべき。

### 12.10 RBF cap を到達しない前提で借入

- Growth 想定 (50%/y) が達成できないと cap reach が 24 → 36 ヶ月に伸び、effective IRR は変わらず元本だけ拡大。
- **正しい実装**: Growth scenario 3 ケース (low / base / high) で cap reach 月を計算、effective IRR の range を提示。

### 12.11 Convertible Note の利息を BS から落とす

- 転換時に元本だけ APIC に振替、accrued interest を skip するのは誤り。
- **正しい処理**: `Convertible Notes Payable + Accrued Interest = Total transferred to APIC`。利息分も equity に含む (税務 implication あり)。

### 12.12 Multiple tranches の Cross-default を無視

- 1 つの facility が trip しただけでも全 tranche が default 扱いになる場合、cash 同時要求で破綻。
- Modeling で `OR(Tranche_1_Default, Tranche_2_Default, ...)` で全体 trigger を判定。

### 12.13 Backend / Maturity Fee を IS から漏らす

- Venture Debt の Backend fee 2〜3% は maturity 時に **lump sum** で払うが、effective interest method で **期間按分** が正しい GAAP 処理。
- 漏らすと最終期に大きな fee 計上、IS が歪む。

### 12.14 Unused Commitment Fee を BS にしか計上しない

- Commitment fee は **当期費用** (Other interest expense)。BS の Accrued Liability に置きっぱなしは不正。
- 月次 / 四半期で IS に流す。

### 12.15 Personal Guarantee を model 外と扱う

- Founder の personal balance sheet に latent liability。万が一 default 時、創業者 個人 を debt で破綻させる。
- ガイドライン適用のもと **personal guarantee なし** を交渉、または PG 額を明示的に scenario 化。

---

## 13. 投資判断視点での Debt

### 13.1 Lender の視点

3 つの core question:

1. **"Can they service this debt under base case AND downside?"**
   - Base case: ICR > 2.5x, FCCR > 1.20x, Cushion > 25%。
   - Downside (revenue −20%, EBITDA −30%, rate +200bp): ICR > 1.5x, FCCR > 1.05x。
   - 両方クリアして初めて pricing 確定。

2. **"What's my recovery in default scenario?"**
   - 担保 LTV (collateral / debt) > 70% (first lien)、> 50% (second lien)。
   - Liquidation analysis で各層 recovery rate を計算。
   - Going concern value も併記。

3. **"What's my upside via warrants / kickers?"**
   - Warrant の Black-Scholes value、coverage の % facility。
   - All-in IRR target 15〜18% (venture debt)、20〜25% (mezz)、12〜14% (TLB)。

### 13.2 Equity 投資家の視点

#### 13.2.1 IRR 改善効果

- Debt が WACC < ROIC なら **leverage で equity IRR が上昇**。
- LBO の典型: ROIC 15%、WACC 8%、Debt-Equity 60/40 → Equity IRR 25%。
- スタートアップは ROIC 不安定、leverage 慎重に。

#### 13.2.2 Dilution 影響

- Warrant dilution 1〜3% は equity issuance (~10〜20%) より **大幅低**。
- 小〜中ティケットの venture debt は dilution savings として価値高。

#### 13.2.3 Downside risk

- Covenant trip で control loss (board change, sponsor wipe-out)。
- "Equity investor が debt で殺される" 典型: leverage 過剰 + market shock + covenant trip。

#### 13.2.4 Next round terms 影響

- Existing debt のせいで next round 投資家が pari passu / subordination の交渉に時間。
- Warrant 持つ existing lender が new round の dilution に文句を言う場合あり (anti-dilution 条項)。

### 13.3 創業者の視点

#### 13.3.1 Equity dilution savings

- Same dollars を equity vs debt で取った場合の dilution 比較を model に。
- Series B 以降、dilution savings は founder のお金。

#### 13.3.2 Cash flow service burden

- 月次 amort が burn を 20〜30% 押し上げる。
- IO 期間後の cash crunch を **明示的に** plan。

#### 13.3.3 Operational restriction (covenant)

- "No additional debt"、"No M&A without consent"、"No equity issuance above $X" などで自由度低下。
- Strategic flexibility を犠牲にする trade-off を理解。

#### 13.3.4 Personal Guarantee (Japan)

- 経営者保証ガイドラインでなしが default だが、**ある場合は founder personal balance sheet にリスク移転**。
- 廃業時 3 年生計費 + 自宅は protect されるが、それ以上は債権者に。

---

## 14. Term Sheet レビュー

### 14.1 Term Sheet の標準セクション

| セクション | 確認ポイント |
|---|---|
| 1. Borrower / Lender / Facility | 主体・額・purpose |
| 2. Pricing (Coupon, OID, Fees) | All-in cost |
| 3. Tenor / Amortization / IO | Cash schedule |
| 4. Security / Collateral / Guarantees | Lien priority、PG 有無 |
| 5. Financial Covenants | Threshold, cushion |
| 6. Negative Covenants | 制限事項、carve-out |
| 7. Affirmative Covenants | Reporting、audit |
| 8. Cure Rights | Equity cure 回数・cap |
| 9. MAC Clause | 削除 / 限定的か |
| 10. Equity Kickers | Warrant、success fee |
| 11. Penalties / Prepayment | Make-whole、call premium |
| 12. Conditions Precedent | Closing 条件 |
| 13. Information Rights | 月次 / 四半期 / 年次 |
| 14. Defaults / Remedies | Trigger、grace period |
| 15. Governing Law / Jurisdiction | NY / DE / Tokyo / etc. |

### 14.2 Pricing チェック

- Coupon が SOFR + spread か、SOFR Floor の有無。
- OID (1〜3% typical) の有無、effective yield 計算。
- Closing fee + Backend fee の合計が想定範囲内か。
- Prepayment penalty の declining schedule (1y 3% → 2y 2% → 3y 1% → 4y 0% 等)。

### 14.3 Tenor チェック

- Maturity が business plan の **runway を 6〜12 ヶ月超える** か。
- Amortization が IO 期間後に **cash flow capacity 内** か。
- Refi window (maturity 6〜12 ヶ月前) が available か。

### 14.4 Security チェック

- All-asset lien か、specific assets only か。
- IP の取扱 (Negative pledge or affirmative lien)。
- Subsidiary guarantee の範囲。
- Personal Guarantee (Japan) の有無、ガイドライン適合性。

### 14.5 Covenants チェック

- Financial covenant の threshold が **base case + 25% cushion** にあるか。
- Definition of EBITDA に **add-backs (SBC, non-recurring, pro-forma synergies)** が含まれるか。
- Cure rights (equity cure) の回数・cap・mechanism。

### 14.6 MAC Clause チェック

- 「**ない** または quantitative material adverse」が beat。
- 「subjective material adverse」だと lender 裁量で発動可能、リスク高。

### 14.7 Equity Kickers チェック

- Warrant coverage % は market rate (5〜10%) か。
- Strike price が当該 round price か、historical price か (lower better)。
- Cashless exercise 可能か。
- Anti-dilution 条項 (full ratchet vs broad-based weighted average)。

### 14.8 交渉余地のあるポイント

| 条項 | 交渉余地 | 借手有利の方向 |
|---|---|---|
| Coupon | 25〜100bp | down |
| OID | 0〜100bp | down (or 0) |
| Closing fee | 0.25〜0.75% | down |
| Backend fee | 0.5〜1.5% | down (or eliminate) |
| Warrant coverage | 1〜3% | down |
| Strike price | next round / current | higher (lender) vs lower (borrower) |
| MAC clause | ある / なし | delete |
| Min cash | 6m → 4m burn | down |
| ARR floor | 100% → 80% of plan | down |
| Cure rights | 4 / lifetime → 5 / consecutive 2 | up |
| Reporting cadence | monthly → quarterly | longer |

---

## 15. 主要参考文献・データソース

### 15.1 業界データ

- **Pitchbook Venture Debt Reports** (quarterly): https://pitchbook.com/news/reports
- **LCD/Pitchbook Leveraged Loan Market** (weekly): pricing benchmark、cov-lite stats、recovery rates
- **Hercules Capital Quarterly Reports** (HTGC, NYSE listed): venture debt typical structures、portfolio data
- **TriplePoint Capital / Trinity Capital BDC filings**: 公開上場の 10-K、10-Q
- **SVB (historical) Q4 / 10-K**: 2010〜2022 年の venture debt market dominantのデータ。SVB 破綻前の reference として。
- **NVCA (National Venture Capital Association) Yearbook**: VC investment + venture debt 統計

### 15.2 業界レポート / Essays

- **Bessemer Venture Partners — "How to Use Venture Debt"**: BVP 公式サイトに掲載、SaaS 向け recommended structures
- **a16z (Andreessen Horowitz)**: "Bridge Round" 関連 essays、Scott Kupor の本「Secrets of Sand Hill Road」
- **Lighter Capital / Pipe / Capchase blogs**: RBF の典型 structures、benchmark data
- **First Round Capital — "Founder Friendly Standard"**: term sheet 標準

### 15.3 日本 公式

- **日本政策金融公庫 (JFC)**: https://www.jfc.go.jp/ — 商品・利率・上限額の正本
- **中小企業庁**: https://www.chusho.meti.go.jp/ — 経営者保証ガイドライン、補助金・税制
- **金融庁**: https://www.fsa.go.jp/ — 銀行業向け監督指針、金融サービス白書
- **日本ベンチャーキャピタル協会 (JVCA)**: https://jvca.jp/ — VC + venture debt 統計
- **INITIAL**: https://initial.inc/ — 国内ベンチャーデット動向、ファンド調達
- **STARTUP DB**: https://startup-db.com/ — 国内スタートアップ調達データ

### 15.4 Practical Books

- "Venture Capital and Private Equity: A Casebook" (Lerner, Hardymon, Leamon)
- "Venture Deals: Be Smarter Than Your Lawyer and Venture Capitalist" (Brad Feld)
- "Investment Banking: Valuation, Leveraged Buyouts, and Mergers and Acquisitions" (Rosenbaum & Pearl)
- "Distressed Debt Analysis" (Stephen Moyer)
- "中小企業のための事業性融資ハンドブック" (中小企業庁)
- "ベンチャーデットの実務" (青木 英孝, 中央経済社)

### 15.5 Regulatory & Legal Reference

- **Loan Syndications and Trading Association (LSTA)**: standardized credit agreement forms (US)
- **NVCA Model Documents**: term sheet, convertible note templates
- **Loan Market Association (LMA)**: standardized syndicated loan documentation (Europe)
- **金融庁 監督指針**: 銀行業 / 信用金庫 / 信用組合
- **Indenture Trustee Association**: bond indenture standards

### 15.6 Real-time Rate Data

- **NY Fed SOFR**: https://www.newyorkfed.org/markets/reference-rates/sofr
- **CME Term SOFR**: https://www.cmegroup.com/market-data/cme-group-benchmark-administration/term-sofr.html
- **日銀 TONA**: https://www.boj.or.jp/statistics/market/short/tona/
- **Chatham Financial Forward Curves**: SOFR / Treasury yield 予測曲線

---

## 16. Debt Due Diligence チェックリスト

### 16.1 Borrower の財務検証

- [ ] LTM 月次 P&L、四半期 BS、四半期 CFS の取得 (24 ヶ月以上)
- [ ] Audited annual financial の確認 (Big 4 or Top 10)
- [ ] Management adjusted EBITDA の reconciliation (GAAP との差異開示)
- [ ] Add-backs の妥当性検証 (one-time vs recurring)
- [ ] Working capital seasonality と peak-to-trough swing
- [ ] CapEx breakdown (maintenance vs growth)
- [ ] SaaS 指標 (ARR, NRR, GRR, CAC payback, LTV/CAC, Burn Multiple, Rule of 40)
- [ ] Revenue concentration (top 10 customers の % of revenue, > 25% は懸念)
- [ ] Churn pattern (customer level + revenue level)
- [ ] Pipeline と pipeline conversion rate

### 16.2 Capital Structure と Debt Stack

- [ ] Existing debt schedule (各 tranche の terms, maturity, balance)
- [ ] Equity structure (cap table, vested options, warrants)
- [ ] Convertible / SAFE / J-KISS の outstanding 額面 + 想定転換株
- [ ] Off-balance liabilities (operating lease, contingent liability, indemnification)
- [ ] Cross-default clauses 全体 mapping

### 16.3 Lender 観点の credit analysis

- [ ] Synthetic credit rating の calc
- [ ] Total leverage / Senior leverage / Net leverage
- [ ] ICR / Cash ICR / FCCR / DSCR の current + projected 3y
- [ ] Liquidity months ((Cash + RCF) / Burn)
- [ ] Covenant cushion at base / downside
- [ ] Recovery analysis under default scenario

### 16.4 Operational DD

- [ ] Management team の track record (CEO, CFO, COO, VP Eng, VP Sales)
- [ ] Org chart, reporting lines, key person dependency
- [ ] Customer references (top 5)
- [ ] Tech stack & IP ownership
- [ ] Litigation status (pending or threatened)
- [ ] Insurance coverage (D&O, E&O, Cyber, Property)

### 16.5 Documents to Review

- [ ] Existing credit agreements (all)
- [ ] Equity transaction docs (Series A/B/C SPA, SHA, NDA)
- [ ] Audited financials (3 年)
- [ ] Tax returns (3 年)
- [ ] Customer contracts (top 10)
- [ ] Vendor contracts (top 10)
- [ ] Employment agreements (key execs)
- [ ] IP assignment docs
- [ ] Real estate lease

### 16.6 Japan-specific 追加項目

- [ ] 経営者保証ガイドライン適合性チェック (3 要件)
- [ ] 信用保証協会の保証枠 + 保証料率
- [ ] 政策金融公庫の borrowing balance + remaining capacity
- [ ] 中小企業者要件 (資本金 / 従業員数) と税制連動
- [ ] J-GAAP / IFRS / US-GAAP どの会計基準で監査されているか
- [ ] 商業登記簿、不動産登記簿 (担保設定の有無)
- [ ] 動産・債権譲渡登記の有無 (ABL の場合)

---

## 17. Term Sheet レビュー チェックリスト

### 17.1 必須項目 (Must-have)

- [ ] **Facility size, tranche structure** が business plan と一致
- [ ] **Coupon (SOFR + spread)** が市場 benchmark 範囲内
- [ ] **All-in effective cost** (coupon + OID + fees + warrant) が WACD 想定内
- [ ] **Tenor** が runway を 6〜12 ヶ月超え
- [ ] **Amortization schedule** が cash flow projection で sustainable
- [ ] **IO 期間** の長さと、その後の amort 急増が manageable
- [ ] **Min cash floor** が runway plan と整合
- [ ] **Financial covenants** に base case + 25% cushion
- [ ] **MAC clause** が deleted または quantitatively limited
- [ ] **Cure rights** (equity cure 4 回 / lifetime 程度) が確保
- [ ] **Personal guarantee** (Japan) が経営者保証ガイドライン適合

### 17.2 交渉項目 (Negotiate down)

- [ ] **Backend fee** を 2% 以下に
- [ ] **Warrant coverage** を 7.5% 以下に
- [ ] **Warrant strike** を current round price に (歴史的価格回避)
- [ ] **Closing fee** を 1% 以下に
- [ ] **Prepayment penalty** を declining 1y3%/2y2%/3y1%/4y0% に
- [ ] **Reporting cadence** を 月次 → 四半期に
- [ ] **Sub-cap on negative covenants** (RP basket、investment basket etc.)
- [ ] **Affirmative covenants** の cure period (30 → 60 営業日)

### 17.3 Red Flag (Walk away)

- [ ] **Subjective MAC clause** (lender 単独裁量)
- [ ] **Cross-default** が小額 ($X = $0 → $1M 以下)
- [ ] **No cure rights** (covenant trip = immediate default)
- [ ] **Warrant > 12% coverage** (over-market)
- [ ] **Effective cost > 18%** (= warrants + fees で実質 18% 超)
- [ ] **Personal guarantee mandatory** (Japan ガイドライン違反)
- [ ] **Anti-dilution full ratchet on warrant** (extreme dilution risk)
- [ ] **Lender approval on next equity round terms**

### 17.4 Closing 後のメンテナンス

- [ ] **Compliance Certificate**: 四半期、各 covenant の actual vs threshold
- [ ] **Annual covenant review**: definition of EBITDA など update
- [ ] **Warrant exercise tracking**: cap table 上の warrant balance
- [ ] **Maturity countdown alert**: 6〜12 ヶ月前に refi 開始
- [ ] **Cross-default mapping update**: 新規 debt 追加時の連動 trigger 確認
- [ ] **FX risk monitoring**: 通貨別 debt の hedge ratio
- [ ] **Lender relationship**: 月次 / 四半期で health-check call

---

## 18. Multi-Covenant Cross-Default Mechanics

> 監査 C-C-051..056 解消。複数 tranche / 複数 covenant が同時に動く場合の優先順位、cross-default vs cross-acceleration の区別、Equity Cure の上限到達ロジック、PIK toggle 連動、refinance 失敗 → bankruptcy timeline、経営者保証あり/なしの effective cost 差分を集約。

### 18.1 Multi-Covenant 同時 breach

#### 18.1.1 同時 breach の典型 pattern

複数 tranche を保有する borrower で、Tranche A (Senior) と Tranche B (Mezzanine) の covenant 仕様が異なる場合、同一 quarter で同時 breach するシナリオが起こりうる:

| Tranche | Covenant type | Trigger condition | 同時 breach の発動経路 |
|---|---|---|---|
| Tranche A (Senior) | Maintenance covenant (毎四半期 test) | Net Leverage > 4.0x | EBITDA -25% で trigger |
| Tranche B (Mezz) | Incurrence covenant (新規 debt 発生時のみ test) | Pro forma Leverage > 5.5x | Tranche A の amend で increase 発生 → trigger |

#### 18.1.2 優先順位 (Intercreditor Agreement)

複数 lender が存在する場合、**Intercreditor Agreement (ICA)** で優先関係を契約上明示:

- **Lien priority**: 1st lien (Senior secured) → 2nd lien (Junior secured) → Unsecured。Collateral の処分順位を規定。
- **Payment priority (waterfall)**:
  1. Senior secured (interest, then principal)
  2. Junior secured (after senior 完済)
  3. Subordinated unsecured
  4. Trade unsecured
- **Standstill provision**: Junior lender は senior の standstill 期間 (通常 90-180 日) は enforcement action 不可。
- **Buyout right**: Junior lender が senior debt を par で買い取る権利 (実務では行使される稀)。

#### 18.1.3 Cure period (典型 30-90 日)

| Covenant type | Standard cure period | 延長交渉余地 |
|---|---|---|
| Financial maintenance | 30-60 days | additional 30 days × 1 (additional fee 払い) |
| Reporting (delayed delivery) | 30 days | 30 days × 1 |
| Affirmative (e.g., insurance) | 30 days | 60 days |
| Negative covenant breach | 即時 | なし (or material adverse waiver) |

- Cure period 中: lender は acceleration できないが、advance 停止 (revolver の場合) は可能。
- Cure period 経過後: technical default 確定 → cross-default 発動の起算点。

#### 18.1.4 Multi-covenant 同時 breach 時の lender 行動

```
Day 0:    Q4 financial reporting で 2 covenant 同時 breach 確認
Day 1-7:  各 lender が compliance certificate を receive、内部協議
Day 8-14: Senior lender が waiver / amendment proposal を提示
Day 15-30: Borrower 側で waiver fee + amendment fee の交渉
Day 30-60: Cure period 中、equity cure 等の手段検討
Day 60+:  Cure 失敗 → cross-default 発動 → 全 lender 同時 acceleration risk
```

### 18.2 Cross-Default vs Cross-Acceleration

#### 18.2.1 用語定義

- **Cross-default**: A facility (Tranche A) で event of default (EoD) が発生した時点で、B facility (Tranche B) も自動的に default 状態となる。
  - Trigger: 単純に "A で default 発生"。
  - Effect: B 側 lender も immediate enforcement action 可能。
- **Cross-acceleration**: A facility で **acceleration** (即時返済請求) が実行された場合のみ、B facility も accelerate される。
  - Trigger: A の lender が acceleration を行使すること。
  - Effect: A の lender が waive すれば B は影響なし。
  - Borrower 側に有利 (cross-default よりも narrow)。

#### 18.2.2 比較表

| 観点 | Cross-default | Cross-acceleration |
|---|---|---|
| Trigger 範囲 | 広い (single default 即連鎖) | 狭い (acceleration 行使必要) |
| Borrower 視点 | 危険 (small default で全 facility default) | 安全余地大 |
| Lender 視点 | 自己防衛強 | A lender 動向依存 |
| 標準的採用 | 大企業 / Public bond | Venture debt / 中堅 startup |
| Cure 余地 | 限定的 | A の cure で B も自動回復 |

#### 18.2.3 Carve-out threshold

実務では以下の carve-out が一般的:

- **De minimis threshold**: $5M (or 5% of total debt) 以下の default は除外。
- **Material default only**: payment default + acceleration のみが trigger (technical default は除外)。
- **Cure period mirror**: A の cure period 終了後、B の cross-default が発動。
- **Specific carve-out**: 特定 facility (e.g., 公的支援 loan, 保証協会付) は除外。

#### 18.2.4 数値例

```
Borrower: Total debt $50M
  Tranche A (Senior): $30M, payment default at $1M
  Tranche B (Mezz): $20M, cross-default with $5M threshold

Scenario 1: A で $0.8M payment default
  → A 側 default (発生事実)
  → B 側 cross-default 発動せず ($5M threshold 未達)

Scenario 2: A で $30M acceleration 発動
  → A 側 acceleration
  → B 側 cross-acceleration 発動 → $20M 即返請求
  → 合計 $50M 即返必要 → 通常は cash 不足 → Chapter 11 / 民事再生
```

### 18.3 Equity Cure 上限到達

#### 18.3.1 Equity Cure の典型仕様

| 項目 | 標準値 | Lender side argue point |
|---|---|---|
| Cure 回数制限 | **4 quarters out of 12 quarters** | "1 度 cure したら 2 quarters 連続 cure 禁止" 追加 |
| Cure amount cap | **EBITDA の 25%** | 計算 EBITDA に cure を含めない (no double counting) |
| Cure 適用 covenant | Maintenance only | Incurrence covenant への適用は通常拒否 |
| 必要証憑 | New equity 入金確認 (cash receipt) | sub-debt は除外、common equity のみ |
| Cure 適用 timing | 四半期末から **20 営業日以内** に提示 | 即日入金が必要 |

#### 18.3.2 Cure 回数制限の働き

```
Quarter:    Q1   Q2   Q3   Q4   Q5   Q6   Q7   Q8   Q9   Q10  Q11  Q12
Cure used:  ✓    ✓    ✓    ✓    ✗    ✗    ✗    ✗    ✗    ✗    ✗    ✗

Q1-Q4 で 4 回 cure 使用済 → Q5 以降は 12 quarter window 内で cure 不可。
Q5 で再 breach → 即 default (cure 手段なし)。
```

但し、12 quarter rolling window のため、Q13 で Q1 の cure が消滅 → Q13 では再び cure 可能。

#### 18.3.3 Cap on cure amount

```
Pre-cure EBITDA:   $5M
Cure cap:           25% × $5M = $1.25M
Required cure:      $2.0M (for covenant compliance)

→ Cure 不足 ($1.25M < $2.0M)
→ Real default
```

#### 18.3.4 Cure 戦略 (borrower 側 playbook)

- **早期 trigger 検知**: 四半期末 4 週間前に projection で覚知 → 投資家事前打診。
- **Insider bridge**: 既存投資家からの追加 equity が最速 (DD 不要、closing 1 週間)。
- **SAFE / convertible note からの転換**: pending convertible があれば convert で cash inject。
- **Cap 超過時の代替策**: Lender との amendment 交渉 (waiver fee 1-2% + warrant 追加発行)。

#### 18.3.5 Cure 失敗 → real default の連鎖

```
Q4: Covenant test 失敗 → Cure 行使を選択
  ↓
Cure 上限 ($1.25M) で部分 cure → 不足 → Lender notify of "potential default"
  ↓
Lender side: amendment proposal (additional warrant 1%, fee $200K)
Borrower side: 受諾 → temporary 解決
  ↓
Q5: 再度 breach → cure 回数 既に消化 → real default 確定
  ↓
Cross-default 発動 (other facility) → acceleration risk
```

### 18.4 PIK が利息率変動連動 (PIK toggle)

#### 18.4.1 PIK toggle の構造

PIK (Payment-In-Kind) toggle は、特定の trigger 条件下で利払を **cash → PIK (元本加算)** に切替える条項:

| 状態 | Coupon | 支払方法 |
|---|---|---|
| Normal | LIBOR/SOFR + 700 bps | cash |
| Stressed (trigger 発動) | LIBOR/SOFR + 700 bps + **PIK 200 bps premium** | PIK (元本加算) |

#### 18.4.2 Trigger 条件 (典型)

- Leverage Ratio > X.Yx (e.g., 4.5x)
- Min Liquidity < $Z M (e.g., $5M)
- EBITDA YoY -20% 以上
- Lender discretion (subjective trigger は borrower 不利)

#### 18.4.3 LIBOR/SOFR + premium スプレッド

```
Base case (LIBOR=5%):
  Cash coupon = 5% + 7% = 12% per annum, paid in cash

Stress trigger 発動:
  PIK coupon = 5% + 7% + 2% (PIK premium) = 14% per annum, paid in PIK

→ 元本 $20M:
   Year 0: Principal $20M
   Year 1 (stress 発動): Principal $20M × (1 + 14%) = $22.8M
   Year 2 (stress 継続): $22.8M × 1.14 = $25.99M
   Year 3 (stress 継続): $25.99M × 1.14 = $29.63M
```

#### 18.4.4 Compound effect (累積影響)

```
Compound formula:
  Principal_t = Principal_0 × Π_{i=1}^{t} (1 + PIK_rate_i)

Stress 3 期連続の場合:
  Principal_3 = $20M × (1.14)^3 = $29.63M
  Δ vs Cash payment = $29.63M - $20M = $9.63M

→ 通常 cash payment ($20M × 12% × 3 = $7.2M total interest) より
  PIK accumulation の方が約 $2.4M (33%) 多い debt service 負担。
```

#### 18.4.5 PIK toggle の借手 / 貸手視点

- **Borrower 視点**:
  - Pros: cash burn 軽減 (短期 liquidity 改善)
  - Cons: 元本膨張 → maturity 時の refi burden 増 → 真の問題先送り
- **Lender 視点**:
  - Pros: real default 回避、yield up (PIK premium で実質金利増)
  - Cons: collateral cushion 減 (元本増 vs collateral value 不変)

### 18.5 Refinance 失敗時の Bankruptcy timeline

#### 18.5.1 標準的 refinance schedule

| Timing | 行動 |
|---|---|
| **T-12 ヶ月** (maturity の 12 ヶ月前) | Refinance 開始: 既存 lender との extension 打診 |
| **T-9 ヶ月** | New lender 接触 (advisor 起用、information memorandum 作成) |
| **T-6 ヶ月** | 主要 lender 接触: term sheet 取得 |
| **T-3 ヶ月** | 失敗の場合 → DIP financing 検討、advisor を bankruptcy 対応に切替 |
| **T-1 ヶ月** | 最後の attempts (hardship loan 等)、Chapter 11 / 民事再生申立準備 |
| **T-0** | 申立 |

#### 18.5.2 Refinance 失敗 trigger

- **Market closed**: 業界全体で credit market 凍結 (e.g., 2008, 2020 Q1, 2022)
- **Company-specific**: covenant breach + EBITDA 急落 → credit metrics で all lenders rejection
- **Industry-specific**: regulatory shock + 業界全体への credit appetite 喪失
- **Sponsor support 喪失**: PE / VC sponsor が bridge を拒否 → standalone credit profile では refi 不可

#### 18.5.3 T-3 ヶ月: DIP Financing 検討

DIP (Debtor-in-Possession) financing は Chapter 11 申立後 super-priority claim として提供:

| 提供者 | 特徴 |
|---|---|
| Existing senior lender | "Defensive DIP" - 既存債権の roll-up + super-priority 化 |
| Distressed credit fund (e.g., Oaktree, Apollo) | "Offensive DIP" - new money + 高 yield |
| Strategic buyer | 363 sale 経由の acquisition 前提 DIP |
| 公的機関 (日本: REVIC) | 公的再生支援 (限定的) |

DIP financing 条件 (典型):
- Coupon: SOFR + 800-1500 bps
- Original Issue Discount (OID): 2-5%
- Super-priority administrative claim
- DIP budget approval (court oversight)
- Adequate protection for existing secured

#### 18.5.4 T-0: Chapter 11 / 民事再生申立

| 項目 | Chapter 11 (US) | 民事再生 (Japan) |
|---|---|---|
| 経営権 | DIP (経営陣残留) | DIP (経営陣残留が原則) |
| 期間 | 6-24 ヶ月 (再建型 plan) | 6-12 ヶ月 (計画提出) |
| 主要 milestone | DIP financing, 363 sale, plan vote | 再生計画認可 |
| 株主 | 通常 wipe out | 100% 減資が一般 |
| 担保権 | Automatic stay で停止 | 別除権 (実行可能、ただし管財人交渉) |
| Trade creditor | Critical vendor motion で priority 付与可 | 共益債権 |

#### 18.5.5 Maturity wall 戦略

- **Liability management exercise (LME)**: maturity 直前に exchange offer / amendment で延長
  - Up-tier exchange: senior unsecured → 1st lien に格上げ + maturity 延長
  - PIK toggle activation: cash interest → PIK 切替で延命
  - Discounted buyback: par 80% で買戻し (debt reduction)
- **Bridge from sponsor**: VC / PE sponsor から bridge equity (down round 含む)
- **Asset sale**: non-core asset 売却で partial paydown

### 18.6 経営者保証あり vs なしでの effective cost 差

#### 18.6.1 利率差 (US / Japan 共通)

| 構造 | 利率調整 | 備考 |
|---|---|---|
| 経営者保証**あり** | -100 ~ -150 bps | Lender 側 risk 軽減で利率優遇 |
| 経営者保証**なし** | baseline | 創業者個人リスクなし |
| 経営者保証なし + 低利優遇制度 | -50 bps | 日本: 経営者保証ガイドライン適合企業 |

#### 18.6.2 Effective cost の数値比較

```
$5M term loan, 5 年, fixed rate

Case A: 経営者保証あり
  Coupon 6.5% (preferred rate due to PG)
  Total interest cost (5y): $5M × 6.5% × 5 = $1.625M
  + Founder personal risk: $5M (full guarantee)

Case B: 経営者保証なし
  Coupon 8.0% (no PG premium +150 bps)
  Total interest cost (5y): $5M × 8.0% × 5 = $2.000M
  + Founder personal risk: $0
  
  Δ Cost (interest): +$0.375M (= +7.5% of principal over 5y)
  Δ Risk: -$5M (founder side)

→ Founder 視点: $0.375M cost vs $5M risk reduction = **risk-adjusted で経営者保証なしが有利**
→ 但し $0.375M の incremental cost を吸収できる margin 必要
```

#### 18.6.3 創業者個人リスク (経営者保証ありの場合)

- **訴求金額**: 通常 全債務額 (joint and several liability)。
- **連帯保証人複数**: 共同創業者全員が PG する場合、各人 100% 訴求可 (株式持分比率に応じてではない)。
- **訴求 timing**: 法人 default 後、別途訴訟で個人資産差押 (日本: 仮差押 → 本訴)。
- **個人破産時**: PG 債務は dischargeable (US) / 免責許可 (日本) で消滅可能だが、reputation damage 永続。

#### 18.6.4 経営者保証ガイドライン 2023 改定での影響 (日本)

2023 年 4 月施行の改正 Points:

| 改正項目 | 影響 |
|---|---|
| **3 要件 (法人個人分離・財務規律・情報開示) 厳格化** | これらを満たす企業は PG 不要を求めやすい |
| **DD 強化**: lender 側に PG 必要性の合理的説明義務 | "なんとなく PG" は不可、書面理由必要 |
| **公的金融機関 (公庫等) の優先適用** | 日本政策金融公庫は原則 PG なしで融資検討 |
| **保証協会付制度**: PG なし型の信用保証メニュー拡充 | 中小企業の PG なし融資が realistic に |
| **既存 PG の見直し請求権** | borrower は既存 PG の解除を交渉可能 |

#### 18.6.5 Cross-domain 影響

- **Equity 側**: 経営者保証ありの場合、創業者の risk profile が高い → exit 戦略 (M&A / IPO) で投資家から保証解除を condition precedent とすることが一般的。
- **Tax 側**: PG 債務の弁済が個人で発生した場合、債権求償の処理 (法人破綻なら通常 NG) → 個人の bad debt 損失処理。
- **Founder departure 時**: 退任後も PG は継続 (契約が解除されるまで)。投資家が新規 lead 入る際の必須交渉項目。

#### 18.6.6 Decision rule (経営者保証 受諾 vs 拒否)

```
受諾を検討すべき条件 (全て満たすこと):
  - 利率削減幅 ≥ 100 bps
  - 借入額 ≤ 創業者個人純資産の 20%
  - 完済 timeline ≤ 3 年
  - 法人の cash flow visibility 高 (downside scenario でも返済可能)
  - 公庫等の制度融資 (PG なし) では条件が成立しない

拒否すべき条件 (一つでも該当):
  - 借入額 > 創業者個人純資産
  - 5 年以上の長期借入
  - 業績の volatility 高
  - VC 投資家から「保証解除」が exit 条件
  - 経営者保証ガイドライン 3 要件適合 (= 拒否の正当根拠)
```

---

> **本リファレンスのメンテナンス**: 利率水準は SOFR / TONA / JFC 利率の四半期 update を推奨。Venture debt landscape (post-SVB) は引き続き volatile のため、Pitchbook / Hercules quarterly に基づく半年 update。日本固有の規制改正 (経営者保証ガイドライン、税制) は年次 update。

> **本書の参照位置**: `scripts/build_model.py` の `build_debt_schedule()` および `three_statement_builder.py` の `link_debt_to_statements()` から正本として参照される。商品カタログは §1、価格設定 worksheet は §2.7、covenant ロジックは §3、サンプル model は §11 を pythonic に翻訳することで実装が可能。
