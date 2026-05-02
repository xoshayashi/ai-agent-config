---
name: convertible_and_terms
description: 転換型ファイナンス (SAFE / J-KISS / Convertible Note) + 優先株条項 (Liquidation / Anti-Dilution / Drag-Along 等) の正本。SKILL.md dispatch table の "SAFE 転換シミュレーション" entry から読まれる。SAFE × Anti-Dilution × Pool Refresh の State Machine も §19 に格納。
type: reference
priority: P1
related: [_terminology, 04b_cap_table_mechanics, 07_japan_specifics, 10_modeling_craft, _master_decision_tree]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: SAFE Discount = `0.20` 表記、J-KISS 2.0 = 2022-04 等の canonical 値は [`_terminology.md §4-5`](_terminology.md) に集約
- **Routing**: [`_master_decision_tree.md §A`](_master_decision_tree.md) (調達) から SAFE / J-KISS / Convertible 関連で第 1 reference として読まれる
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (特に conversion 数値の closed-form 一致) を必ず実行
- **関連 reference**: `04b_cap_table_mechanics` (cap table 計算、§19 とセット運用) / `07_japan_specifics §3` (J-KISS 日本固有) / `10_modeling_craft §19` (wind-down) / `_master_decision_tree §A`

# 転換型ファイナンス商品と優先株条項 専用リファレンス

本書はスタートアップ財務モデリングのうち、**転換型ファイナンス商品 (SAFE / J-KISS / Convertible Note / AngelList Series Seed)** および **優先株条項 (Term Sheet)** の解析に必要な論点を、原語条項・完全展開した数式・数値例とともに体系化した構造化リファレンスである。Cap Table 構造・希薄化計算・exit waterfall は別ファイル (`04b_captable_dilution.md` 等) を参照のこと。

> **重要な前提**
>
> - 数値・税率・金額・条文は 2026 年 5 月時点の最新値で、出典を明記する。
> - 条項名は契約書で実際に使用される原語 (英語) を併記する。
> - 数式は完全展開し、変数定義・適用例・端数処理を明示する。
> - 「投資家観点 / 創業者観点」の併記を全条項で行う。
> - 「モデリング上の影響」は次の 4 軸で記述する: (a) 転換株式数, (b) Pre-money / Post-money cap table, (c) 希薄化, (d) liquidation waterfall。

---

## 目次

1. 転換型ファイナンス商品の全体像
2. SAFE (Y Combinator 公式)
3. J-KISS (Coral Capital 仕様)
4. Convertible Note (米国型)
5. AngelList Series Seed templates
6. 優先株条項 (Term Sheet) 概論
7. Liquidation Preference
8. Dividend
9. Anti-Dilution
10. Conversion Rights
11. Voting / Board Seats / Protective Provisions
12. Redemption Rights
13. ROFR / Co-Sale / Drag-Along / Tag-Along
14. MFN / Information Rights / Pre-emptive Rights
15. その他の補助条項 (Vesting / IP Assignment / No-shop)
16. 投資家観点と創業者観点の整理
17. Term Sheet レビューチェックリスト

---

## 1. 転換型ファイナンス商品の全体像

### 1.1 なぜ転換型を使うのか

シード期は事業実績が乏しく、株価 (= バリュエーション) を確定的に決めるのが困難である。優先株 (priced round) を組成しようとすると、(a) 弁護士費用が 200〜500 万円規模で膨らむ、(b) 種類株式の登記・株主間契約 (SHA) ・投資契約 (SPA) の交渉に 2〜3 ヶ月を要する、(c) バリュエーションを下げると将来のシリーズ A で down round になる、というディレンマが生じる。

転換型ファイナンスは「**今は株価を決めず、将来の priced round で確定する。代わりに早期投資家にプレミアム (cap / discount) を与える**」というアイデアで、上記の問題を回避する。

### 1.2 4 大商品の系譜

| 商品 | 発祥 | 発祥年 | 法的性格 (US) | 法的性格 (JP) | 主たる起草者 |
|---|---|---|---|---|---|
| **Convertible Note** | 米国 | 1990 年代〜 | 社債 (debt) | 新株予約権付社債 (CB) | 各 VC ファーム |
| **SAFE** | 米国 (Y Combinator) | 2013 (pre-money), 2018 (post-money) | 契約上の将来株式取得権 (not debt, not equity) | (日本では類似商品なし、海外子会社で利用) | Carolynn Levy (YC) |
| **KISS** | 米国 (500 Startups) | 2014 | Debt 型と Equity 型の 2 種 | (海外向け) | 500 Startups |
| **J-KISS** | 日本 (Coral Capital, 旧 500 Startups Japan) | 2016 (v1.0), 2022-04 (v2.0) | 該当なし | 新株予約権 (会社法 236 条以下) | Coral Capital |

### 1.3 商品横断比較表

| 比較軸 | Pre-money SAFE (旧型) | Post-money SAFE (現行) | Convertible Note | J-KISS v2.0 |
|---|---|---|---|---|
| 利息 | なし | なし | あり (年 4〜8% 程度) | なし (利息条項を削除した v2 が標準) |
| 満期 | なし | なし | あり (12〜24 ヶ月) | あり (発行から 18 ヶ月、自動転換または当事者間協議) |
| 評価上限 (cap) | pre-money cap | post-money cap | pre-money cap が一般的 | pre-money cap が一般的 |
| 割引率 (discount) | あり (10〜25%) | あり | あり | あり |
| MFN | あり (オプション) | あり (オプション) | あり (任意) | なし (実務で side letter) |
| Pro-rata 権 | side letter | side letter | 契約本体に明記が多い | side letter (任意) |
| 自動転換のトリガ | Equity Financing | Equity Financing | Qualified Financing | 適格資金調達 (1 億円以上が標準) |
| Liquidity Event 時 | キャッシュ or 普通株 | キャッシュ or 普通株 | 元利金償還 or キャッシュ +α | 投資額の 1 倍 or 1 株 1 円で普通株転換 |
| 解散時 | 投資額の払戻し | 投資額の払戻し | 元利金返済 (社債としての地位) | 投資額の払戻し |
| 米国市場での可否 | 標準 (Delaware C-corp) | 標準 (Delaware C-corp) | 標準 | 不可 (日本会社法ベース) |
| 日本市場での可否 | 不可 (会社法上の対応する商品なし) | 不可 | 海外型をそのまま使うか「擬似 SAFE」 | 標準 (日本法準拠) |

### 1.4 転換型と優先株 (priced round) の境界線

```
シード期                               シリーズ A
 ┌──────────────────┐                    ┌──────────────┐
 │ 転換型 (cap だけ決める) │ ──── 自動転換 ───→ │ 優先株 priced │
 └──────────────────┘                    └──────────────┘
   $1〜3M, 数週間で完結                         $5〜15M, 2〜3 ヶ月
```

転換型の "shadow priced round" 問題: cap が暗黙的にバリュエーションのアンカーとなる。投資家は cap 以下に評価することは稀で、"cap で priced する" 圧力がかかる。

---

## 2. SAFE (Simple Agreement for Future Equity)

### 2.1 起源と背景

- **発表**: 2013 年 12 月、Y Combinator の Carolynn Levy が起草。
- **意図**: KISS-style convertible note の煩雑さを解消するため、「**債務 (debt) ではなく、将来の equity を取得する単純な契約**」として設計。
- **2018 改訂**: 同年 9〜10 月に「post-money SAFE」が公開され、pre-money SAFE は事実上廃止された (YC 自身が「post-money を使うべき」と公式に推奨)。
- **公式テンプレート**: 5 種 (cap only / discount only / cap + discount / MFN only / pro-rata side letter) が ycombinator.com/documents で配布。

### 2.2 Pre-money SAFE と Post-money SAFE の違い (本質)

両者の決定的な違いは「**SAFE 投資家の保有割合がいつ確定するか**」である。

#### 2.2.1 Pre-money SAFE (旧型, 2013-2018)

- 「Pre-money valuation cap」を設定。
- SAFE 投資家の持分は、**シリーズ A 時点で他の SAFE / オプションプールがどれだけ追加されるかに依存**する。
- → 後続 SAFE が増えるほど、初期 SAFE 投資家の持分は希釈される。

```
SAFE 投資家の持分 = SAFE 投資額 / (cap + 後続 SAFE 投資総額 + ESOP 増分)
```

#### 2.2.2 Post-money SAFE (2018 〜 現行)

- 「Post-money valuation cap」を設定。
- SAFE 投資家の持分は **発行時点で確定** する (= "ownership %" が固定)。
- → 後続 SAFE による希釈は **創業者と既存普通株主のみ** に降りかかる (これが post-money SAFE の核心)。

```
SAFE 投資家の持分 (固定) = SAFE 投資額 / Post-money cap
```

#### 2.2.3 数値で比較

**ケース**: シード調達 $1M / cap $10M、その後 $500K の追加 SAFE / cap $10M を発行、シリーズ A は $5M / pre-money $20M / ESOP プール 10% を increase。

##### Pre-money SAFE の場合

- 初期 SAFE 投資家の "想定" 持分 = 1M / (10M + 0.5M + 後続 ESOP 約 1.7M) = 1M / 12.2M ≈ **8.20%**
- 後続 SAFE 投資家 = 0.5M / 12.2M ≈ **4.10%**
- 追加 SAFE が発行された分、初期 SAFE 投資家も希釈される。

##### Post-money SAFE の場合

- 初期 SAFE 投資家の持分 = 1M / 10M = **10.00%** (固定)
- 後続 SAFE 投資家 = 0.5M / 10M = **5.00%** (固定)
- 創業者は両方の希釈を吸収する。

→ Post-money SAFE は **投資家にとって有利、創業者にとって不利** な設計。

### 2.3 主要条項

#### 2.3.1 Valuation Cap (評価上限)

転換時の company valuation の上限を定めるパラメータ。実際の priced round の pre-money/post-money valuation が cap を上回った場合、SAFE は cap で計算した株価で転換する。

**Conversion Price (Cap-based)**:

$$
\text{Conversion Price}_{\text{cap}} = \frac{\text{Valuation Cap}}{\text{Company Capitalization}}
$$

- Pre-money SAFE の場合: `Company Capitalization` = pre-money cap で別途定義された分母 (普通株+優先株+option pool exclude SAFE)
- Post-money SAFE の場合: `Company Capitalization` = post-money cap で定義された分母 (普通株+優先株+option pool+全 SAFE/note)

#### 2.3.2 Discount

priced round の株価に対する割引率。標準は 15〜20%。

**Conversion Price (Discount-based)**:

$$
\text{Conversion Price}_{\text{disc}} = \text{Series A Price per Share} \times (1 - d)
$$

ここで `d` = discount rate (例: 0.20)。

注意: `Discount Rate` を 80% と書く契約と、20% と書く契約がある。YC SAFE は **"Discount Rate = (1 - 割引率)"** で定義 (例: 80%) → conversion price = SAFA 価格 × Discount Rate。

#### 2.3.3 両方ある場合: より投資家有利な方を採用

$$
\text{Conversion Price} = \min\left(\text{Conversion Price}_{\text{cap}}, \text{Conversion Price}_{\text{disc}}\right)
$$

**SAFE 投資家が受け取る株式数**:

$$
\text{Shares}_{\text{SAFE}} = \frac{\text{Investment}_{\text{SAFE}}}{\text{Conversion Price}}
$$

#### 2.3.4 MFN (Most Favored Nation)

将来発行される SAFE / note のうち、より投資家有利な条件 (より低い cap, より高い discount, MFN 自体, valuation cap 自体) があれば、既存 MFN SAFE 投資家はその条件を取り入れる権利を有する。

- YC の MFN SAFE は **cap も discount も無し** (= "next round で決まる pure deferral") の純粋形と、cap/discount 付きで MFN を兼備する形がある。
- MFN は通常 priced round (Equity Financing) までに行使する必要がある。

#### 2.3.5 Pro-rata Side Letter

SAFE 投資家がシリーズ A 以降で「自分の持分比率を維持できる金額まで追加投資する権利」。
- 2018 post-money SAFE では本体から削除され、別紙 (side letter) に切り出された。
- side letter は Lead 投資家との交渉で削られることもある (= 弱い権利)。

### 2.4 5 標準テンプレート (YC 配布版)

YC が ycombinator.com/documents で配布している正式テンプレートは以下:

| # | 名称 | 主要条項 |
|---|---|---|
| 1 | SAFE - Valuation Cap, no Discount | cap のみ |
| 2 | SAFE - Discount, no Valuation Cap | discount のみ |
| 3 | SAFE - Valuation Cap and Discount | cap + discount |
| 4 | SAFE - MFN, no Valuation Cap, no Discount | MFN のみ |
| 5 | Pro Rata Side Letter | (本体ではなく side letter) |

### 2.5 Conversion Mechanics: Trigger Events

SAFE の転換は次のいずれかのイベントで発生する。

#### 2.5.1 Equity Financing (Priced Round)

- 定義 (post-money SAFE 版): "the issuance of Standard Preferred Stock by the Company in exchange for cash"
- 旧 pre-money SAFE には minimum threshold ($1M 等) があったが、post-money SAFE では threshold が削除され、**全ての preferred 発行で自動転換** する。
- 転換後の株式は通常 "Safe Preferred Stock" (= series A preferred と同等の経済条件、ただし conversion price 補正版) になる。

#### 2.5.2 Liquidity Event

- M&A、IPO、Direct Listing 等。
- 投資家は次の 2 択 (whichever is greater):
  - **Cash-out**: 投資額をキャッシュで回収 (1x liquidation preference 相当)
  - **Conversion**: cap で計算した株価で普通株に転換し、買収対価を受領
- IPO の場合は通常 "automatic conversion to common stock at the IPO price" が発動。

#### 2.5.3 Dissolution Event

- 解散・清算・債務不履行 etc.
- 投資家は **Purchase Amount (= 投資元本)** を回収。残余があれば普通株主に分配。
- 優先順位: 取引先・債務 > SAFE > 普通株 (ただし SAFE は preferred より下位)。

### 2.6 数値例: Post-money SAFE 完全計算

**前提**:
- Founders 6,000,000 普通株 (post-money 発行前)
- ESOP 設定なし (Series A で 10% ポストマネープール)
- SAFE 1: $500K, post-money cap = $5M
- SAFE 2: $300K, discount = 20% (cap なし)
- SAFE 3: $200K, post-money cap = $8M, discount = 15% (両方)
- Series A: $3M new money, pre-money = $12M, ESOP = post-money 10%

#### Step 1: Pre-money の確定

- Pre-money (Series A) = $12,000,000
- Post-money (Series A) = $12M + $3M = $15,000,000

#### Step 2: 各 SAFE の Conversion Price 算定

**Series A の "見せかけ" PPS (オプションプール拡大前) を仮置き**:
- まず Series A 投資家の持分 = 3M / 15M = 20%
- 既存 (founder + SAFE + ESOP) = 80%

実際の計算は Series A pre-money "in" を SAFE / option pool 計算に展開する **連立方程式** が発生する。Post-money SAFE では計算上「SAFE 投資家の持分 = 投資額 / post-money cap」を維持するため、以下のルールを適用する:

##### 各 SAFE の固定持分

- SAFE 1 持分 = 500K / 5M = **10.00%** (固定)
- SAFE 3 持分 = 200K / 8M = **2.50%** (cap 適用、固定)
- SAFE 2 (cap なし、discount のみ): Series A の PPS で discount を適用 → 持分は固定されない

##### Series A PPS と SAFE 2 持分の連立

`P` = Series A の pre-money price per share (= conversion 後の "official" price)
`S_2` = SAFE 2 投資家の持分 (post-money 比)

SAFE 2 conversion price = P × (1 - 0.20) = 0.8P
SAFE 2 shares = 300,000 / 0.8P
SAFE 2 持分 = (300,000 / 0.8P) / Post-money 株数

post-money の総株数 (`T`) は次で構成:
```
T = Founders + SAFE1 + SAFE2 + SAFE3 + ESOP + SeriesA
```

post-money valuation = $15M、PPS (post-money) = $15M / T
ESOP は post-money の 10% = 0.10T
Series A 投資家持分 = 20% = 0.20T (= 3M / PPS_postmoney = 3M / (15M/T))

SAFE 1 持分 = 10% = 0.10T
SAFE 3 持分 = 2.5% = 0.025T

→ Founders + SAFE 2 持分 = 1 - 0.10 - 0.025 - 0.10 - 0.20 = 0.575 = 57.5%

SAFE 2 の持分 `s_2` を post-money cap 換算で表現すると、SAFE 2 は cap がないので Series A PPS で評価される:
```
SAFE 2 持分 = 300,000 / (0.8 × P × T)
```
ただし P = 15M / T × (T / pre-money 株数) なので、計算は **YC SAFE Primer の公式 worksheet** に従って iterative に解く。

実務では下記の closed-form で解ける:

##### Post-money SAFE 計算の closed-form

post-money SAFE が n 個ある場合、その投資家の合計持分:

$$
\sum_{i=1}^{n} \frac{I_i}{C_i}
$$

ここで `I_i` = 投資額, `C_i` = (i 番目の SAFE の) post-money cap (cap がない場合は、Series A の pre-money + 当該 SAFE 投資額 で代替し、discount を適用)。

**結論として** SAFE 1, 3 と Series A, ESOP は固定持分を持ち、残余 = founder dilution + cap なし SAFE。

#### Step 3: 数値展開

| 株主 | 持分 (%) | 株式数 (T = 10,000,000 と仮置き) |
|---|---|---|
| Founders | (1 - 0.10 - x_2 - 0.025 - 0.10 - 0.20) | 残余 |
| SAFE 1 | 10.00% | 1,000,000 |
| SAFE 2 | x_2 | 計算 |
| SAFE 3 | 2.50% | 250,000 |
| ESOP | 10.00% | 1,000,000 |
| Series A | 20.00% | 2,000,000 |

`x_2` は SAFE 2 が discount = 20% で、Series A PPS = $1.50 (= 15M / 10M T) のとき:
- SAFE 2 conversion price = $1.50 × 0.8 = $1.20
- SAFE 2 shares = 300,000 / 1.20 = 250,000
- x_2 = 250,000 / 10,000,000 = 2.50%

→ Founders 持分 = 100% - 10% - 2.5% - 2.5% - 10% - 20% = **55.00%** (= 5,500,000 株)

検算: 5,500,000 (founder) + 1,000,000 (SAFE1) + 250,000 (SAFE2) + 250,000 (SAFE3) + 1,000,000 (ESOP) + 2,000,000 (SeriesA) = 10,000,000 ✓

ただし founders の **元の株数は 6,000,000 株** だったので、stock split 等の調整が必要。実務では founder 株数を維持して `T` を逆算する。Founders 6M / 0.55 = `T` ≈ 10,909,091 株 → Series A PPS = 15M / 10.91M ≈ $1.375。

### 2.7 投資家観点と創業者観点

| 観点 | 投資家 (SAFE 投資家) | 創業者 |
|---|---|---|
| Pre vs Post | post-money の方が **持分が固定されて有利** | pre-money の方が後続 SAFE 希釈を投資家にも分担できて **有利** |
| Cap | 低い方が有利 (= 有利な株価) | 高い方が有利 |
| Discount | 高い方が有利 (例 25%) | 低い方が有利 (例 10〜15%) |
| MFN | あった方が安全 | なくしたい (簡素化したい) |
| Pro-rata | あった方が follow-on で参加できる | 削除して残余パイを Lead に渡したい場合がある |
| 満期 (SAFE にはない) | あれば返済を要求できる | ない方が長期保有できる |

### 2.8 SAFE の日本市場での扱い

- 日本会社法には SAFE そのものに該当する制度がない。
- **代替手段**:
  1. **J-KISS** (新株予約権ベース、後述) を使う。
  2. **Delaware Flip** (= 米国 C-corp を親会社化) してから米国 SAFE を使う。シンガポール Holdco でも類似。
  3. 「擬似 SAFE」 (= 民事契約のみで将来株式取得権を約す) を結ぶ → 法的有効性に懸念があり、実務ではほぼ使われない。

### 2.9 Founder 交渉 Rule of Thumb (Pre-money vs Post-money) — E-C-002 解消

`§2.2` の Pre-money / Post-money の **計算上の違い** とは別に、**創業者が交渉テーブルで何を要求すべきか** の実務 rule をまとめる。
監査 E (Strategy) finding **E-C-002** 解消: SAFE 投資家有利条項を founder が無批判に受け入れる事例 (特に「stacked Post-money SAFE」) を、本節の rule で防ぐ。

#### 2.9.1 Pre-money vs Post-money 再掲 (founder 視点)

```
Pre-money SAFE (旧):
  - Cap = 投資後の 「pre-money valuation」 を意味
  - 後続 SAFE が追加で発行されると、創業者と既存 SAFE 投資家が両方薄まる
  - 創業者メリット: 後続 SAFE の希薄化を投資家にも分担させられる
  - 投資家デメリット: 後続 SAFE で持分が一見しないうちに薄まる

Post-money SAFE (2018 〜 現行 default):
  - Cap = 投資後の 「post-money valuation」 を意味、SAFE holder の最終持分が確定
  - 後続 SAFE が追加されても、追加分は **創業者側からのみ** 希釈される
  - 投資家メリット: 持分が固定されて読める
  - 創業者デメリット: 「stacked SAFE」で気づかぬうちに大幅希薄化
```

#### 2.9.2 Founder 交渉 5 ルール

```
Rule 1: 複数 SAFE を発行する見込みがあるなら必ず Pre-money SAFE を選ぶ
        理由: 後続希薄化を投資家側にも負担させ、Stacked SAFE の創業者罠を回避。
        ただし米 lead VC が Post-money 一択を要求してきたら、累計 SAFE 残額を
        想定 post-money の 25% 以下に抑え、4 件目以降は priced round に切り替える。

Rule 2: Cap は「次回 priced round で目指す 7-10x ARR multiple」を上限に置く
        例: ARR $1M で Series A 目標 $40M post-money → SAFE cap は $30-40M を上限に。
        Cap が低すぎると投資家にとって非常に有利な希薄化を許す。
        Cap が無い (= MFN only) は意味が異なる、§2.3.4 を参照。

Rule 3: Discount は 20% を default、25% は譲歩、30% 以上は警告
        20% は YC SAFE のデファクト。25% を要求された場合は market 比較で交渉余地。
        30% 超は「creditworthiness が崩れている」 サインで、bridge であってもこれを許容
        するくらいなら priced down round を検討した方が cap table 的に健全。

Rule 4: MFN (Most Favored Nation) の取り扱い
        - Pre-money SAFE では MFN を投資家に与えても創業者影響は小さい (= 後の SAFE が
          有利な条件なら既存 SAFE も同条件にバンプアップ)。
        - Post-money SAFE では MFN は dangerous: 「Cap 自体が一律最低値で再ピン留め」
          されると投資家持分が雪だるま式に膨れる。
        - 実務: Post-money では MFN を「Cap を除く discount + 期間 + pro-rata のみ」 に
          限定する side letter で受ける。

Rule 5: Pro-rata side letter は最大投資家のみに限定
        - Pro-rata 権 = 後続 round で持分を維持するために投資する権利。
        - これを SAFE 投資家全員に付与すると、Series A の lead が「party round」化を
          嫌って投資を見送る (signaling risk)。
        - 実務: 累計投資 $X 以上 (例 $250K) の SAFE holder にのみ side letter で付与。
        - YC SAFE 標準 template は pro-rata なし、必要なら side letter として別添。
```

#### 2.9.3 5 ルールの数値検証 (worked example)

ARR $1M、想定 Series A post-money $30M、SAFE 累計 $4M を発行する場合:

| Variable | Pre-money SAFE | Post-money SAFE |
|---|---|---|
| Cap | $20M (pre) | $20M (post) |
| 投資家持分 (Series A 後) | 約 13.5% | 20.0% (固定) |
| 創業者持分 (Series A 後) | 約 49.5% | 約 43.0% |
| 後続 SAFE $1M 追加時の founder 影響 | -1.7pt | -3.3pt |

Post-money の場合、後続 SAFE 1 件追加で **founder の希薄化が約 2 倍** に膨らむことが分かる。
複数 SAFE 予定時に Rule 1 が効く根拠。

#### 2.9.4 Term sheet review チェックリスト (founder 用)

SAFE term sheet を投資家から受領した直後に確認するチェック:

- [ ] Pre-money / Post-money どちらか明示されているか? (default は Post-money)
- [ ] Cap 値は「次回 round 想定 7-10x ARR」 の範囲か?
- [ ] Discount 値は 20-25% に収まっているか?
- [ ] MFN 条項が Post-money SAFE で Cap 含む包括的なものではないか?
- [ ] Pro-rata side letter が全 SAFE holder に付与されていないか?
- [ ] 「累計 SAFE 残額 / 想定 post-money」 が 25% を超えていないか?
- [ ] Cross-default や redemption 条項が SAFE 標準を逸脱して追加されていないか?
- [ ] Lawyer review に少なくとも 2 営業日確保したか?

#### 2.9.5 「複数投資家・順次クロージング」の罠

SAFE は「都度 close」 が可能なため、founder が「あと $500K 入れたい投資家がいる」 と段階的に
発行を続けると、知らぬ間に Stacked SAFE が累積する。これを防ぐ運用 rule:

```
- 半年に 1 回しか SAFE を発行しない (cadence rule)
- 累計 SAFE 残 / 想定 post-money が 25% に達したら必ず priced round に切り替え
- 異なる Cap の SAFE を 3 種類以上混ぜない (= 計算負担と利害衝突を避ける)
- Side letter (MFN, pro-rata) を出す相手は累計 ≥ $250K 投資家のみ
- Cap を引き下げる (= 投資家有利方向に動く) 修正は既存 SAFE holder への通知必須
```

これらを守らないと、Series A 直前に「pre-money valuation を SAFE で先食いした」 状態となり、
新規 lead VC が「dirty cap table」 として見送る原因となる。`_master_decision_tree.md §G.4` の anti-pattern。

---

## 3. J-KISS (日本版 Keep It Simple Security)

### 3.1 起源と背景

- **公開**: 2016 年 4 月、Coral Capital (旧 500 Startups Japan) が公開。
- **着想**: 米国 KISS (500 Startups, 2014) の日本会社法準拠版。
- **法的構成**: 「**新株予約権**」(会社法 236 条以下) として発行する。新株予約権付社債ではなく、純粋な新株予約権で、debt 性は持たない (= equity-like)。
- **リポジトリ**: github.com/CoralCapital/J-KISS で .docx 形式で公開、誰でも自由に利用できる。

### 3.2 バージョン履歴

| バージョン | 公開時期 | 主要変更点 |
|---|---|---|
| **v1.0** | 2016 年 4 月 | 初版。利息条項あり (年 1%)、評価上限・割引、適格資金調達 1 億円 |
| **v1.1** | 2017 年頃 | 軽微な文言修正 |
| **v2.0** | 2022 年 4 月 | 利息条項削除、優先株転換時の経済条件を Series A と同等に揃える明示化、転換上限 (= cap) の単位を「次回ラウンド企業価値 = post-money cap」で明確化 |
| **v2 派生** | 2021〜2024 | bridge 用途、複数バリエーション (cap only / discount only / cap + discount) が実務で使い分けられる |

### 3.3 法的構造: なぜ新株予約権か

- **会社法上の問題**: 株式発行は「払込期日」「発行価額 (1 株あたり)」を決議で確定する必要がある (会社法 199 条)。SAFE のように「将来確定する株価で発行」は素直にはできない。
- **解決**: 新株予約権 (= ワラント) として発行し、行使条件で「適格資金調達発生時に、後述の式で行使価額を計算」とする。これで会社法に準拠しつつ SAFE 類似の経済効果を実現できる。
- **募集事項**: 新株予約権の内容として、(a) 行使価額、(b) 行使期間、(c) 行使条件、(d) 取得条項 (= 強制償還) を契約書 (新株予約権発行要項) に記載する。
- **登記**: 新株予約権の発行は登記事項 (会社法 911 条 3 項 12 号)。

### 3.4 主要パラメータ

| パラメータ | 標準値 | 説明 |
|---|---|---|
| 払込金額 (発行価額) | 投資額 (例: 5,000 万円) | 投資家が払い込む現金 |
| 評価上限額 (Valuation Cap) | 例: 5 億円 | 適格資金調達時の pre-money valuation 上限 |
| 割引率 (Discount) | 80% (= 20% off) | 適格資金調達時の優先株価格に乗じる係数 |
| 適格資金調達 | 1 億円以上の優先株式発行 | 自動転換のトリガ |
| 満期 | 発行日から 18 ヶ月 | 任意転換 / 満期償還の起点 |
| 利息 | 0% (v2.0 以降) | v1 では 1% だったが v2 で削除 |
| 取得条項 (償還) | M&A / 解散時に投資額の 1 倍を支払 | "1x liquidation preference" 相当 |

### 3.5 転換メカニズム

#### 3.5.1 自動転換 (Automatic Conversion) — 適格資金調達

「**適格資金調達**」(= Qualified Financing) が発生した場合、J-KISS は **A 種優先株** に自動転換する。

##### 適格資金調達の定義 (標準ひな形)

> 当社が発行する優先株式 (種類株式) を 1 回または複数回の発行で **総額 1 億円以上**、株式 1 株あたりの払込金額が一定の方法 (= pre-money 評価が成立) で発行されること

##### 行使価額 (= conversion price) の式

```
行使価額 = min(
    A 種優先株の 1 株あたり払込金額 × Discount Rate,
    Valuation Cap ÷ 完全希釈後株式数 (J-KISS 行使前)
)
```

- `Discount Rate` = 0.80 (= 20% 割引)
- 「完全希釈後株式数 (J-KISS 行使前)」= 普通株 + 既発行優先株 + 行使済 SO + ESOP プール (J-KISS と本回新規優先株は除く)

##### 投資家が取得する優先株式数

```
取得株式数 = 投資額 ÷ 行使価額
```

#### 3.5.2 任意転換 (Optional Conversion) — 満期到来

満期 (発行日から 18 ヶ月) が到来し、自動転換が発生していない場合:

- 投資家は **「投資額 ÷ 評価上限額に基づく株価」** で **A 種類似の優先株 (満期時優先株 / Deemed Series A)** に任意転換できる。
- または、当事者間協議で延長することも可。

#### 3.5.3 取得 (Buy-back / Redemption) — M&A・解散時

M&A、解散、清算、その他流動性イベントが発生した場合 (= 適格資金調達ではない):

- 投資家は次のうち高い方を受領:
  - **投資額の 1 倍** (= 1x liquidation preference)
  - **評価上限ベースで普通株転換した場合の取り分**

実務では「M&A 時には 1 倍償還が標準。Series A 転換相当の上振れも認める two-track 設計」となっている。

### 3.6 数値例

**前提**:
- 創業者 800,000 株 (普通株)
- ESOP 100,000 株 (発行済 SO)
- J-KISS 投資額 = 50,000,000 円 (5,000 万円)
- 評価上限 = 500,000,000 円 (5 億円)
- Discount Rate = 80%
- 適格資金調達: シリーズ A pre-money 800,000,000 円 (8 億円)、新規発行 200,000,000 円 (2 億円)

#### Step 1: J-KISS 行使前の完全希釈株式数

```
発行済株式数 = 800,000 (普通) + 100,000 (ESOP) = 900,000 株
```

#### Step 2: シリーズ A の 1 株あたり払込金額 (PPS)

```
PPS_seriesA = 8 億円 / 900,000 株 = 約 888.89 円/株
```

(注: 実際は J-KISS 転換と ESOP プール拡大を含めた連立で求める。ここでは簡略化のため J-KISS 行使前の株数で計算)

#### Step 3: J-KISS 行使価額の算定

```
行使価額_discount = 888.89 × 0.80 = 711.11 円/株
行使価額_cap     = 500,000,000 / 900,000 = 555.56 円/株
行使価額         = min(711.11, 555.56) = 555.56 円/株 (cap 適用)
```

#### Step 4: J-KISS 投資家の取得株式数

```
取得株式数 = 50,000,000 / 555.56 ≈ 90,000 株
```

#### Step 5: シリーズ A 投資家の取得株式数

```
取得株式数_seriesA = 200,000,000 / 888.89 ≈ 225,000 株
```

#### Step 6: 転換後の cap table

| 株主 | 株式数 | 持分 |
|---|---|---|
| 創業者 (普通) | 800,000 | 65.31% |
| ESOP (普通) | 100,000 | 8.16% |
| J-KISS → A 種優先株 | 90,000 | 7.35% |
| シリーズ A 優先株 | 225,000 | 18.37% (= 持分 18.4%) |
| **合計** | 1,225,000 | (端数誤差あり) |

実投資 → 持分換算:
- J-KISS: 5,000 万円 → 7.35% (cap が低かったため Series A 投資家より安い株価で多くの株式を取得)
- Series A: 2 億円 → 18.4% (≒ 2 億円 / (8 億円 + 2 億円) = 20% から、J-KISS 転換による希釈を反映)

### 3.7 利息の扱い (v1.0 → v2.0 の論点)

- **v1.0**: 「**払込金額 + 利息**」で行使価額を計算する条項あり (年 1%)。
- **v2.0**: 利息条項削除。理由は (a) スタートアップ会計上の手間 (発生主義での未払利息計上)、(b) 米国 SAFE が無利息であることとの整合性、(c) 18 ヶ月での利息額が小さく実務上の意義が薄い。

### 3.8 会計処理

#### 3.8.1 発行時 (発行会社側)

```
(借方) 現金預金     50,000,000
       (貸方) 新株予約権 (純資産の部)  50,000,000
```

- **新株予約権**は純資産の部「Ⅲ. 新株予約権」に表示する (会社計算規則 76 条 1 項 2 号)。
- 負債計上ではない (= debt ではなく equity-like の扱い)。

#### 3.8.2 自動転換時 (適格資金調達)

```
(借方) 新株予約権  50,000,000
       (貸方) 資本金        25,000,000
              資本準備金    25,000,000
```

- 通常、払込金額の 1/2 を資本金、残りを資本準備金に計上 (会社法 445 条 2 項)。
- 「J-KISS の払込金額」がそのまま新株式の払込金額として振り替えられる。

#### 3.8.3 任意転換時 (満期到来)

転換価額が確定しないため「みなし優先株」として転換するが、税務上は適格資金調達と同様に処理する。

#### 3.8.4 失効時 (満期到来して転換も買戻しもされない)

```
(借方) 新株予約権  50,000,000
       (貸方) 新株予約権戻入益  50,000,000 (特別利益)
```

- 法人税法上、新株予約権戻入益は **益金算入** される (法法 22 条 2 項)。
- ただし J-KISS では満期到来 = 任意転換 or 当事者協議のいずれかが標準で、失効ケースはほぼ発生しない。

### 3.9 税務上の取扱い

#### 3.9.1 発行会社

- 新株予約権の発行は **資本等取引** で、益金にも損金にも算入しない (法法 22 条 5 項)。
- 自動転換時の払込金額も資本等取引で同様。
- 利息条項がある v1.0 の場合、未払利息は損金算入されない (新株予約権の評価額の一部とみなされる解釈)。

#### 3.9.2 投資家 (法人)

- 新株予約権の取得 → 取得価額 = 払込金額 (法法 61 条の 3 第 1 項)。
- 行使時 → 取得した株式の取得価額 = 新株予約権簿価 + 行使払込金額 (J-KISS は行使払込金額がゼロ、すなわち発行時払込金額がそのまま株式取得価額)。
- 含み損益の認識は行わない (= 行使までは時価評価対象外)。

#### 3.9.3 投資家 (個人 / エンジェル税制)

- **エンジェル税制 (措置法 41 条の 19)** の適用を受けるためには「取得時点で**株式**であること」が要件。J-KISS は **新株予約権**なので、発行時点ではエンジェル税制の優遇は **受けられない**。
- 自動転換で優先株式に変わった時点で、当該株式の取得価額に対してエンジェル税制を適用できる解釈もあるが、保守的な税理士は否定する。
- 最新の措置法を要確認。

### 3.10 J-KISS をブリッジに使う場合の注意点 (Coral Capital の公式注意点)

1. **多重 J-KISS 累積で希薄化が読みにくくなる**: シード後にブリッジで J-KISS を 2-3 回重ねると、cap が異なる J-KISS が層をなして、Series A 時の創業者持分計算が極めて複雑になる。
2. **cap の暗黙バリュエーション化**: ブリッジ J-KISS の cap が低すぎると、Series A の事実上の上限 anchor になる。
3. **Series A 投資家との交渉でブリッジ条件を再交渉される**: 「ブリッジ J-KISS 投資家には Series A の 1.0x preference は認めるが participating は外す」など。
4. **任意転換期日の管理**: 18 ヶ月期日を過ぎると当事者間協議が発生し、bridge round 中の投資家排出につながる。

### 3.11 投資家観点と創業者観点

| 観点 | 投資家 (J-KISS 投資家) | 創業者 |
|---|---|---|
| Cap 設定 | 低くしたい (例 3 億円) | 高くしたい (例 8 億円) |
| Discount | 高くしたい (75% = 25% off) | 低くしたい (90% = 10% off) |
| 適格資金調達閾値 | 低くしたい (5,000 万円) → 早期に転換 | 高くしたい (1 億円以上) → ブリッジ柔軟性 |
| 満期 | 短くしたい (12 ヶ月) | 長くしたい (24 ヶ月) |
| 1x preference (M&A 時) | 必須 | 受け入れる (標準) |
| エンジェル税制適合性 | 求めない (機関投資家) | 個人投資家のニーズに応えたい |

---

## 4. Convertible Note (米国型)

### 4.1 概観

Convertible Note は米国シード期で SAFE 登場前に標準であった商品。現在も、(a) SAFE が使えない州法環境、(b) 投資家が debt 性 (満期償還、利息) を要求するケース、(c) Series A bridge round で残余を整理する場面、で使われる。

法的性格は「**社債 (Promissory Note)**」で、発行会社にとっては負債計上、投資家にとっては debt 性資産。優先株転換のオプションが付いている点が convertible たる所以。

### 4.2 主要パラメータ

| パラメータ | 標準値 | 説明 |
|---|---|---|
| Principal Amount | 投資額 (例: $1,000,000) | ノートの元本 |
| Interest Rate | 年 4〜8% (単利が多い、まれに複利) | 元本に対する利息 |
| Maturity Date | 発行から 12〜24 ヶ月 | 満期 |
| Valuation Cap | $5M〜$15M (pre-money) | 評価上限 |
| Discount Rate | 15〜25% off | 適格資金調達時の割引 |
| Qualified Financing | $1M〜$5M 以上の preferred 発行 | 自動転換のトリガ |
| MFN | あり (任意) | より有利な条件への乗り換え権 |
| Change of Control Premium | 1.5x〜2.0x | M&A 時の上乗せ |

### 4.3 転換メカニズム

#### 4.3.1 Qualified Financing (自動転換)

```
Conversion Price = min(
    Series A PPS × (1 - Discount Rate),
    Valuation Cap / Pre-money Fully Diluted Shares
)

Conversion Amount = Principal + Accrued Interest

Shares Issued = Conversion Amount / Conversion Price
```

#### 4.3.2 数値例

**前提**:
- Principal = $1,000,000
- Interest Rate = 6% (単利)
- 発行から転換まで 18 ヶ月
- Discount Rate = 20%
- Valuation Cap = $10M (pre-money)
- Series A: pre-money = $25M、PPS = $2.50/share、Pre-money 株数 = 10,000,000

##### Step 1: Accrued Interest

```
Interest = $1,000,000 × 6% × (18/12) = $90,000
Conversion Amount = $1,000,000 + $90,000 = $1,090,000
```

##### Step 2: Conversion Price

```
Conversion Price (discount) = $2.50 × 0.80 = $2.00
Conversion Price (cap) = $10,000,000 / 10,000,000 shares = $1.00
Conversion Price = min($2.00, $1.00) = $1.00 (cap が有利)
```

##### Step 3: Shares Issued

```
Shares = $1,090,000 / $1.00 = 1,090,000 shares
```

##### Step 4: Effective Pre-money Valuation

```
Effective Valuation = 1,090,000 × $2.50 = $2,725,000 worth
... but investor only paid $1,000,000 + $90,000 → ROI ≒ 2.5x (= cap effect)
```

#### 4.3.3 Maturity (満期未転換)

満期までに Qualified Financing が発生しなかった場合、契約上の選択肢:
- **Repayment**: 元本 + 利息を現金で返済
- **Optional Conversion**: 投資家の選択で、cap or 別途定めた "Maturity Conversion Price" で普通株または "Maturity Stock" に転換
- **Extension**: 当事者間協議で満期延長

実務上は extension で延長されるか、Series A の bridge note として整理されるケースが多い。

#### 4.3.4 Change of Control / Liquidity Event

M&A や IPO 等の場合、投資家は次のいずれかを選択:
- 元本 + 利息の返済 (= 1x debt return)
- 1.5x〜2.0x premium の return ("change of control premium")
- cap で計算した株価で普通株に転換し、買収対価を受領

### 4.4 SAFE との比較

| 比較軸 | Convertible Note | SAFE |
|---|---|---|
| 法的性格 | 社債 (debt) | 契約上の equity 取得権 |
| 利息 | あり (4〜8%) | なし |
| 満期 | あり | なし |
| 会計処理 (発行) | 負債 (Note Payable) | (米国 GAAP) Equity または Mezzanine |
| 倒産時の優先順位 | debt > preferred > common | 投資家が SAFE 投資額の払戻し (preferred より下、common より上) |
| 弁護士費用 | 高 (法的精緻) | 低 (テンプレート化) |
| 利息計上の手間 | 月次で利息発生 | なし |

**Decision rule (E-H-006 解消):** どちらを選ぶかは下記 trigger で判定する。
- **Note を選ぶ条件 (いずれか 1 つでも該当):** (a) 投資家が distressed scenario での creditor 保護 (満期償還、利息、倒産優先順位) を明示要求、(b) 発行体が Delaware 以外で設立されており、SAFE の州法上の execution 可能性に疑義がある (E-H-029 参照、CA / WY / TX 等)、(c) Bridge round で次ラウンド失敗時の早期 exit を投資家が要求、(d) 既存債権者との subordination agreement が必要な structured down-round。
- **SAFE を選ぶ条件 (default):** 上記いずれにも該当しない場合。Cap table の単純化と発行コスト最小化を優先。Pre-seed〜Seed の Y Combinator 系 round では SAFE が de facto standard。
- **両者を Cap が同水準で並記された場合:** SAFE は会計上 equity 扱いで cap table 反映、Note は負債計上で利息累積後の `(元本 + 累積利息) ÷ Cap` で持分確定するため、**Note は同 Cap でも持分が大きく** なる (利息分)。投資家側の有利性は Note。

### 4.5 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Note vs SAFE | Note が債権者保護を含み有利 | SAFE が会計簡素 |
| 利息 | 4〜8% を要求 | 利息なし or 1〜2% に交渉 |
| 満期 | 短く (12 ヶ月) | 長く (24 ヶ月) |
| Change of Control premium | 1.5〜2.0x を要求 | 1.0x に抑える |
| Subordination | senior position を要求 | (debt 投資家 vs operating creditors の議論) |

---

## 5. AngelList Series Seed Templates

### 5.1 概観

AngelList が公開している軽量な Series Seed (= 非常にシンプルな優先株式) テンプレート。NVCA Model Documents (Series A 向け、200 ページ規模) と比較して、Series Seed は 30〜50 ページに簡略化されている。

主要バリエーション:
- **Series Seed Preferred Stock Investment Agreement** (Lead 投資家との SPA)
- **Certificate of Incorporation (Series Seed)** (定款)
- **Investor Rights Agreement (Series Seed)** (情報請求権・登録請求権を含む)
- **Right of First Refusal and Co-Sale Agreement**
- **Voting Agreement** (議決権合意)

### 5.2 NVCA との主な違い

| 項目 | NVCA Model (Series A) | AngelList Series Seed |
|---|---|---|
| 文書数 | 5+ documents, 200+ ページ | 4-5 documents, 30-50 ページ |
| Liquidation Preference | 1x non-participating (default) | 1x non-participating |
| Anti-Dilution | Broad-based weighted average | 多くのテンプレートで省略 or simplified |
| Board 構成 | 詳細 | 簡略 (1 director + 1 observer 等) |
| Protective Provisions | 詳細リスト | 簡略リスト |
| 想定調達額 | $5M+ | $500K - $3M |
| 弁護士費用 | $30K - $80K | $5K - $15K |

### 5.3 主要派生形

- **YC Series A SAFE Conversion Documents** (= SAFE が転換した先の Series A 標準書類)。AngelList と互換性あり。
- **Cooley GO Series Seed**: 同様の seed-friendly priced round テンプレート。AngelList と並ぶ事実上のスタンダード。
- **Wilson Sonsini Term Sheet Generator**: NVCA ベースで自動生成。

### 5.4 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| 文書の薄さ | 慣れた template なら OK、未知の条項挿入は嫌う | 弁護士費用を抑えたい → AngelList 推奨 |
| Lead 投資家の有無 | Lead がいないと document 改変リスクあり | Solo angel 中心の場合は適合 |

---

## 6. 優先株条項 (Term Sheet) 概論

### 6.1 Term Sheet とは

Term Sheet は priced round (= 優先株式での資金調達ラウンド) における主要条件を 2〜10 ページに要約した non-binding (一部 binding) な文書。Lead 投資家が起草し、創業者と署名した後、3〜8 週間かけて以下の definitive document に展開される:

- **Stock Purchase Agreement (SPA)** = 株式購入契約 / 投資契約
- **Amended and Restated Certificate of Incorporation** = 改訂定款 (= AOI) / (日本では定款 + 種類株式設計書)
- **Amended and Restated Investors' Rights Agreement** = 投資家の権利契約 (= IRA)
- **Right of First Refusal and Co-Sale Agreement** = ROFR/Co-Sale 契約
- **Voting Agreement** = 議決権合意
- **Management Rights Letter** = (該当する場合) ERISA 対応

### 6.2 Term Sheet の構造 (NVCA 標準)

NVCA Model Term Sheet は次の階層で構成される:

1. **Offering Terms** (Issuer / Securities / Aggregate Proceeds / Investors / Type of Security / Price Per Share / Pre-Money Valuation / Capitalization)
2. **Charter (定款) 条項** (Dividends / Liquidation Preference / Voting Rights / Protective Provisions / Optional Conversion / Anti-Dilution / Mandatory Conversion / Pay-to-Play / Redemption Rights)
3. **Stock Purchase Agreement 条項** (Representations and Warranties / Conditions to Closing / Counsel and Expenses)
4. **Investors' Rights Agreement 条項** (Registration Rights / Information Rights / Right to Participate Pro Rata / Matters Requiring Investor Consent)
5. **Right of First Refusal/Co-Sale Agreement / Voting Agreement** 条項
6. **Other Matters** (Founders' Stock / Employee Pool / Vesting / Confidentiality and Inventions Assignment / No-Shop / Expiration / Counsel)

### 6.3 経済条項 (Economic Terms) と支配条項 (Control Terms)

| 区分 | 主な条項 |
|---|---|
| **経済条項 (Economics)** | Price per Share, Pre-Money Valuation, Liquidation Preference, Dividend, Anti-Dilution, Pay-to-Play, Redemption |
| **支配条項 (Control)** | Voting Rights, Protective Provisions, Board Composition, Drag-Along, Information Rights |

経済条項は exit 時の "誰がいくら受け取るか"、支配条項は "誰が決めるか" を支配する。

---

## 7. Liquidation Preference (清算優先権 / 残余財産分配権)

### 7.1 定義と目的

**Liquidation Preference** は、Liquidation Event (= 清算 / 解散 / M&A / 一部のケースで IPO) 発生時に、優先株主が普通株主に **先立って** 一定金額を受け取る権利。

NVCA 標準では「**1x non-participating**」が default で、これが市場標準。

### 7.2 倍率 (Multiple)

| 倍率 | 説明 | 市場での頻度 |
|---|---|---|
| **1x** | 投資額の 1 倍を回収 | NVCA 標準、一般的 |
| **1.5x** | 1.5 倍 | 中期 (Series B+) で見られる |
| **2x** | 2 倍 | down round, 危機ラウンドで | 
| **3x** | 3 倍 | 極めて投資家有利、創業者は強く拒否 |

### 7.3 Participation の 3 形態

#### 7.3.1 Non-Participating Preferred (非参加型)

> **The Series A Preferred shall be entitled to receive, in preference to Common Stock, the greater of (i) [1.0]x the Original Purchase Price plus accrued and unpaid dividends, OR (ii) the amount such holder would have received had it converted to Common Stock immediately prior to the Liquidation Event.**

**式**:

$$
\text{Payout}_{\text{non-part}} = \max\left(M \cdot I,\ \frac{S_p}{S_p + S_c} \cdot V\right)
$$

ここで:
- `M` = liquidation multiple (例: 1.0)
- `I` = invested amount
- `S_p` = preferred shares
- `S_c` = common shares (fully diluted, ESOP 含む)
- `V` = total proceeds (exit value)

##### 数値例

- 投資 $5M、Pre-money $15M、Post-money $20M (= 25% 持分)
- 1x Non-participating
- Exit value:

| Exit Value | (i) 1x Pref | (ii) Convert (25%) | 投資家受取 (max) |
|---|---|---|---|
| $5M | $5M | $1.25M | **$5M** (pref 採用) |
| $10M | $5M | $2.5M | **$5M** |
| $20M | $5M | $5M | **$5M** (indifference point) |
| $40M | $5M | $10M | **$10M** (convert 採用) |
| $100M | $5M | $25M | **$25M** |

→ Indifference point (= preference と convert の payoff が等しくなる exit) = `M × I / 持分` = $5M / 0.25 = **$20M**

#### 7.3.2 Fully Participating Preferred (完全参加型 / "Double-Dip")

> **The Series A Preferred shall be entitled to receive, in preference to Common Stock, [1.0]x the Original Purchase Price plus accrued dividends, AND THEREAFTER share in the remaining proceeds with the Common Stock on a pro-rata as-converted basis.**

**式**:

$$
\text{Payout}_{\text{part}} = M \cdot I + \frac{S_p}{S_p + S_c} \cdot (V - \sum M_j \cdot I_j)
$$

(全 preferred 系列の preference を引いた残余を pro-rata で配分)

##### 数値例

- 投資 $5M、25% 持分
- 1x Fully Participating

| Exit | Pref ($5M) | 残余 ($V - $5M) | Investor pro-rata (25%) | 投資家合計 |
|---|---|---|---|---|
| $5M | $5M | $0 | $0 | **$5M** |
| $10M | $5M | $5M | $1.25M | **$6.25M** |
| $20M | $5M | $15M | $3.75M | **$8.75M** |
| $40M | $5M | $35M | $8.75M | **$13.75M** |
| $100M | $5M | $95M | $23.75M | **$28.75M** |

非参加型の同条件と比較:

| Exit | Non-Participating | Participating | 差分 |
|---|---|---|---|
| $5M | $5M | $5M | 0 |
| $20M | $5M | $8.75M | +$3.75M |
| $40M | $10M | $13.75M | +$3.75M |
| $100M | $25M | $28.75M | +$3.75M |

→ 参加型は exit が大きいほど投資家のアップサイドを侵食する。

#### 7.3.3 Capped Participating Preferred

> **... share in the remaining proceeds with the Common Stock on a pro-rata as-converted basis UNTIL such holder has received an aggregate payment of [2.0]x the Original Purchase Price; thereafter, the holder shall convert to Common Stock.**

**式**:

$$
\text{Payout}_{\text{capped}} = \min\left(\text{Cap} \cdot I,\ \text{Payout}_{\text{part}}\right)
$$

ただし、cap を達成すると "convert to common" のオプションが選択可能になり、その後は普通株として分配を受ける (= 大きな exit では convert した方が有利)。

実際の式:

$$
\text{Payout}_{\text{capped}} = \max\left(\min(\text{Cap} \cdot I,\ M \cdot I + \text{pro-rata残余}),\ \frac{S_p}{S_p + S_c} \cdot V\right)
$$

##### 数値例 (Cap = 2x = $10M)

| Exit | Participating | Capped (cap $10M) | Convert (25%) | 投資家最終 |
|---|---|---|---|---|
| $5M | $5M | $5M | $1.25M | **$5M** |
| $20M | $8.75M | $8.75M (cap 未達) | $5M | **$8.75M** |
| $25M | $10M | **$10M** (cap 到達) | $6.25M | **$10M** |
| $40M | $13.75M | $10M (cap) | $10M | **$10M** (border) |
| $50M | $16.25M | $10M (cap) | $12.5M | **$12.5M** (convert) |
| $100M | $28.75M | $10M (cap) | $25M | **$25M** (convert) |

### 7.4 Seniority (優先順位)

複数シリーズの優先株がある場合、優先順位を以下のいずれかで設計:

#### 7.4.1 Standard (Stacked)

> Series C → Series B → Series A → Common

最新シリーズが最も優先 (= "last in, first out")。

#### 7.4.2 Pari Passu

> Series A, B, C が同順位で、各々の preference を pro-rata で按分

新規投資家が前ラウンドの投資家を尊重するメッセージ。

#### 7.4.3 Hybrid (Tiered Stacking)

> Series C, B が同順位 (上位グループ) → Series A → Common

実務では Series A 投資家が後続ラウンドで "pari passu" を要求することが多い。

##### 数値例 (Stacked vs Pari Passu)

- Series A: $5M @ 1x non-part
- Series B: $10M @ 1x non-part
- Exit: $12M

**Stacked (B → A → common)**:
- Series B: $10M (preference 全額)
- Series A: $2M (= $12M - $10M, ただし $5M に満たないので普通株転換せず preference のみ)
- Common: $0

**Pari Passu**:
- Total preference = $15M, exit $12M (不足)
- 投資家全体に按分: B = $12M × ($10M / $15M) = $8M, A = $12M × ($5M / $15M) = $4M
- Common: $0

→ Pari Passu は B の取り分を圧縮し、A を上振れさせる。

### 7.5 Liquidation Event の定義

NVCA 標準で **Liquidation Event** に含まれるのは:

1. 解散・清算・winding-up
2. **Deemed Liquidation Event**:
  - M&A (asset sale 含む)
  - 持分の 50% 超を取得する change of control
  - 全資産の売却 (asset sale)
3. 一部の Series で **IPO は除外** (= IPO 時には automatic conversion で普通株化)

「Deemed Liquidation Event の定義の広さ」が交渉対象になる (例: 株式の交換による合併も含めるか / 子会社化も含めるか)。

### 7.6 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| 倍率 | 1x で十分 (NVCA 標準), down round では 2x を要求 | 1x で抑えたい |
| Participation | Participating で双取り | Non-participating に固執 |
| Capped Participation | 大きな exit で投資家が上振れを失わずに、創業者を救うバランス点 | 上限 (例 2x cap) を低く設定したい |
| Seniority | 後続ラウンドで pari passu を強制 (= dilution を避ける) | 投資家間の交渉に巻き込まれないよう中立を保つ |

---

## 8. Dividend (配当)

### 8.1 配当の 3 形態

#### 8.1.1 Non-Cumulative Dividend (非累積配当)

> **Dividends shall be paid on the Series A Preferred on an as-converted basis when, as, and if paid on the Common Stock.**

NVCA 標準。配当が宣言された場合に支払われるが、累積はしない (= 払われなくても権利は消滅)。

#### 8.1.2 Non-Cumulative Preferred Dividend (年率定義型、非累積)

> **The holders of Series A Preferred shall be entitled to receive non-cumulative dividends, in preference to any dividend on Common Stock, at the rate of [6%] of the Original Purchase Price per annum, when, as, and if declared by the Board.**

宣言されたときのみ払う、年率 6% 等。

#### 8.1.3 Cumulative Dividend (累積配当)

> **The holders of Series A Preferred shall be entitled to receive cumulative dividends at the rate of [8%] per annum, payable in cash upon a Liquidation Event or upon redemption.**

累積し、Liquidation 時 / 償還時に preference に上乗せして支払う。実質的に **debt 性の追加リターン** に相当。

##### 累積配当の式

$$
\text{Accrued Dividend}_t = I \cdot r \cdot t
$$

(単利の場合)

$$
\text{Accrued Dividend}_t = I \cdot \left((1 + r)^t - 1\right)
$$

(複利の場合)

##### 数値例

- 投資 $5M、Cumulative dividend 8% (単利)、5 年保有
- Accrued = $5M × 8% × 5 = $2M
- Liquidation event での payout = $5M (preference) + $2M (accrued) + ... = **$7M** + 残余分配

5 年で投資家のリターンが 1.4x (純粋 preference のみで) 上がる。

### 8.2 PIK Dividend (Payment-in-Kind)

現金ではなく追加株式で支払う配当。down round / late stage で見られる。

### 8.3 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Cumulative vs Non-cumulative | Cumulative で確定リターンを底上げ | Non-cumulative で柔軟性確保 |
| 配当率 | 6〜8% 要求 | 0% (= "if declared") |
| 累積配当 + Participating | 強力なコンボ、投資家リターン最大化 | 強く拒否 |

**累積配当の "事実上 debt 化" 閾値 (E-H-007 解消):**

| 配当率 | hold 期間 | 累積効果 (LP 倍率換算) | 創業者の対応 |
|---|---|---|---|
| 6% | 4 年 | (1.06)^4 ≈ 1.26x | 1.25x Participating Preferred と等価扱い、強く交渉 |
| 8% | 5 年 | (1.08)^5 ≈ 1.47x | 1.5x Participating Preferred と等価、ほぼ拒否 |
| 8% | 7 年 | (1.08)^7 ≈ 1.71x | "事実上 debt convert"。受諾は最後の選択肢 |

**ルール: `(1 + 配当率)^想定 hold 年数` が 1.3x を超える組み合わせは LP overlay として 1.3x Participating と等価扱い** で交渉する (= cumulative 単独でも参加型の 1 種として認識する)。`Cumulative + Participating` の重ね掛けは強力すぎるため、どちらか一方に絞る交渉が原則。

---

## 9. Anti-Dilution (希薄化防止条項)

### 9.1 概観

**Anti-Dilution** は、後続ラウンドで **down round** (= 前ラウンドの PPS より低い PPS で発行) が発生した際に、既存優先株の **conversion price を下方調整** することで、投資家が普通株転換時により多くの株式を受け取れるようにする条項。

主な形式は 3 つ:
- **Full Ratchet** (フルラチェット)
- **Broad-Based Weighted Average** (広基準加重平均) ← NVCA 標準
- **Narrow-Based Weighted Average** (狭基準加重平均)

### 9.2 Conversion Price (転換価額) の前提

優先株は通常 1:1 で普通株に転換できるが、その背景には:

```
転換比率 = Original Issue Price / Conversion Price (現在)
```

新株発行時に Conversion Price が下方調整されると、転換比率が 1:1 を超えて、1 株の優先株が複数株の普通株に転換されるようになる。

### 9.3 Full Ratchet (フルラチェット)

最も投資家に有利な、最も厳格な調整。

> **If the Company issues additional Common Stock or Equivalents at a price per share less than the Conversion Price of the Series A Preferred, the Conversion Price shall be reduced to the price per share of such new issuance.**

**式**:

$$
\text{New Conversion Price}_{\text{ratchet}} = P_{\text{new}}
$$

(`P_new` = 新規発行時の PPS)

##### 数値例

- Series A: 投資 $5M @ $5/share = 1,000,000 shares (Original)
- Conversion price (initial) = $5
- Series B (down round): $2/share

→ New Conversion Price = $2
→ Series A の転換比率 = $5 / $2 = 2.5
→ Series A 転換後の普通株 = 1,000,000 × 2.5 = **2,500,000 shares**
→ Series A 投資家の "ownership" は 1.5x で増加 (= 創業者が代わりに希釈)

### 9.4 Broad-Based Weighted Average (NVCA 標準)

加重平均で調整。希釈の度合い (新規発行が大きいほど) を反映する穏やかな調整。

**式 (NVCA 標準)**:

$$
\text{NCP} = \text{OCP} \times \frac{A + B}{A + C}
$$

ここで:
- `NCP` = New Conversion Price (新しい転換価額)
- `OCP` = Old Conversion Price (旧転換価額)
- `A` = 既発行普通株数 (full diluted basis, **broad-based** = 普通株 + 優先株 (as-converted) + 行使済 / 未行使オプション・ワラント全て)
- `B` = 新株発行で受領した対価 ÷ OCP (= "new money で発行できる旧 PPS 換算の株数")
- `C` = 新株発行で発行した株数

直感的には:
- B = 旧株価で買えるはずだった株数 (= "fair な価格の代理量")
- C = 実際に発行した株数 (= down round で大量発行した実数)
- C > B なら NCP < OCP (= 下方調整)

#### 9.4.1 数値例

**前提**:
- Series A 投資 $5M @ $5/share = 1,000,000 shares (= OCP $5)
- 既発行普通株 (broad-based) = 4,000,000 株 (Series A 含む as-converted)
- 後に Series B 発行: $2M を $2/share = 1,000,000 shares (down round)

```
A = 4,000,000
B = $2,000,000 / $5 = 400,000
C = 1,000,000

NCP = $5 × (4,000,000 + 400,000) / (4,000,000 + 1,000,000)
    = $5 × 4,400,000 / 5,000,000
    = $5 × 0.88
    = $4.40
```

→ Series A 転換比率 = $5 / $4.40 = 1.136x
→ Series A 転換後の普通株 = 1,000,000 × 1.136 = **1,136,364 shares**

#### 9.4.2 Full Ratchet との比較

| 条項 | NCP | 転換後株数 | 追加発行 |
|---|---|---|---|
| Full Ratchet | $2.00 | 2,500,000 | +1,500,000 |
| Broad-Based WA | $4.40 | 1,136,364 | +136,364 |

→ Full Ratchet は約 11x の希薄化を生む。創業者は強く拒否すべき。

### 9.5 Narrow-Based Weighted Average

`A` の定義を狭く (= "**当該シリーズの優先株のみ as-converted**" 等) する。

**式**: 同じ加重平均、ただし `A` が小さいので NCP がより大きく下方調整される。

#### 9.5.1 数値例 (上記前提で)

`A` = 1,000,000 (Series A as-converted のみ) と仮定:

```
A = 1,000,000
B = 400,000
C = 1,000,000

NCP = $5 × (1,000,000 + 400,000) / (1,000,000 + 1,000,000)
    = $5 × 1,400,000 / 2,000,000
    = $5 × 0.70
    = $3.50
```

→ Series A 転換比率 = $5 / $3.50 = 1.428x
→ 転換後株数 = 1,428,571 shares

| 条項 | NCP | 転換後株数 |
|---|---|---|
| Full Ratchet | $2.00 | 2,500,000 |
| Narrow-Based WA | $3.50 | 1,428,571 |
| Broad-Based WA | $4.40 | 1,136,364 |
| なし | $5.00 | 1,000,000 |

### 9.6 Carve-outs (適用除外)

Anti-dilution の対象から **除外される** 発行:

1. ESOP (option pool) のための発行 (board 承認済)
2. M&A の対価としての発行
3. 既存優先株の conversion による発行
4. デット融資の対価としてのワラント (商業的に妥当な範囲)
5. 株式分割 / 株式併合 (これらは別途 mechanical adjustment)

NVCA 標準では carve-outs が広く設定される。投資家が carve-outs を絞る (= "発行プールを最小化") のはディフェンシブな発想で、発行会社にとって厳しい。

### 9.7 Pay-to-Play (参加義務条項)

down round に **既存投資家が pro-rata で参加しない場合**、当該投資家の anti-dilution 権を **失効** させる、または優先株を強制的に普通株に転換させる条項。

> **If any holder of Preferred Stock fails to participate in the next Qualified Financing on a pro-rata basis, all of the Preferred Stock of such holder will automatically convert to Common Stock and lose the benefits of being Preferred (anti-dilution, liquidation preference, voting rights).**

#### 9.7.1 設計バリエーション

| バリエーション | 内容 |
|---|---|
| **Strict Pay-to-Play** | 不参加 → 普通株強制転換 |
| **Soft Pay-to-Play** | 不参加 → anti-dilution のみ失効 (preference は維持) |
| **Shadow Series** | 不参加 → "shadow" preferred (preference 維持、anti-dilution 失効) |

#### 9.7.2 効果

Pay-to-play は:
- Down round で既存投資家全員に "follow on" を強制 → 創業者にとっては資金調達確実性が高まる
- 不参加投資家を懲罰 → 既存ベンチャー間の規律
- ただし「既存投資家が capital constrained」な場合は不公平

### 9.8 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Anti-Dilution の有無 | 必須 | あれば broad-based に限定 |
| Full Ratchet | 強く要求 (down round 不安が高い場合) | 強く拒否 |
| Broad vs Narrow | Narrow が有利 | Broad で抑える |
| Pay-to-Play | 既存投資家全員参加を強制したい | 自動転換に賛成 (新規 Lead 投資家に有利) |
| Carve-outs | 限定 | 広く設定 |

---

## 10. Conversion Rights (転換権)

### 10.1 Optional Conversion (任意転換)

優先株主は **いつでも任意で** 普通株に転換できる。

**式**:

$$
\text{Common Shares Issued} = \text{Preferred Shares} \times \frac{\text{Original Issue Price}}{\text{Current Conversion Price}}
$$

通常、初期 Conversion Price = Original Issue Price なので 1:1。Anti-dilution 発動後は > 1:1 の比率で転換される。

### 10.2 Mandatory (Automatic) Conversion (強制転換 / 自動転換)

特定の条件発動で **強制的に** 普通株転換される。

#### 10.2.1 標準的なトリガ

> **Each share of Series A Preferred shall automatically convert into Common Stock at the then-applicable Conversion Price upon (i) the closing of a firmly underwritten public offering with aggregate proceeds of at least $[50] million and a price per share of at least $[3x Original Issue Price]; or (ii) the consent of the holders of a majority of the then-outstanding Series A Preferred.**

NVCA 標準では:
- **Qualified IPO** (= 一定規模の IPO) で自動転換
- 過半数 (or 2/3) の **株主合意** で自動転換

#### 10.2.2 数値例

- Series A: 投資 $5M、$5/share、Original Conversion Price = $5
- Mandatory conversion thresholds: IPO ≥ $50M proceeds, IPO PPS ≥ $15 (= 3x)

→ IPO で $80M 調達、PPS = $20 で発行 → 全 Series A が automatic conversion (1:1, 1,000,000 株)

### 10.3 Series による Conversion 設計の違い

| Series | Trigger thresholds | 説明 |
|---|---|---|
| Seed (Series Seed) | ≥ $30M proceeds, 2x | 簡素 |
| Series A | ≥ $50M proceeds, 3x | NVCA 標準 |
| Series B+ | ≥ $75M proceeds, 3-5x | 上場準備が現実的な規模 |

### 10.4 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Optional Conversion | 必須 (= upside 取得) | 標準 |
| Mandatory IPO threshold | 高くしたい (= small IPO で convert させない) | 低くしたい (= 全 series convert で simple cap table) |
| Mandatory PPS threshold | 高くしたい (= 高 PPS でなければ convert させない) | 低くしたい |

---

## 11. Voting Rights / Board Seats / Protective Provisions

### 11.1 Voting Rights (議決権)

#### 11.1.1 As-Converted Voting

NVCA 標準: 優先株は **as-converted ベースで普通株と同数の議決権** を持つ。

> **Each share of Series A Preferred Stock shall have a number of votes equal to the number of shares of Common Stock then issuable upon conversion of such share.**

#### 11.1.2 Special Class Voting (種類株主決議)

特定の重要事項については **当該シリーズの過半数承認** を別途必要とする。これが次の "Protective Provisions" と連動する。

### 11.2 Board Composition (取締役構成)

#### 11.2.1 NVCA 標準 (Series A)

> **The Board shall consist of [5] members, comprised of:**
> - [1] director designated by Series A Investors
> - [2] directors designated by holders of Common Stock (typically the founders)
> - [2] independent directors mutually acceptable to both

**5 名構成**: Series A 1 / Founder (Common) 2 / Independent 2 ← "tied" balance

#### 11.2.2 Series B 以降

| ラウンド | Board 構成例 |
|---|---|
| Seed | Founders 2 / Lead investor 1 (+ observer) |
| Series A | Founders 2 / Series A 1 / Independent 2 |
| Series B | Founders 1 / Series A 1 / Series B 1 / Independent 2 |
| Series C | Series A 1 / Series B 1 / Series C 1 / Founder 1 / Independent 1 |

→ ラウンドが進むほど創業者の board 支配力が低下。

#### 11.2.3 Board Observer (オブザーバー)

議決権なし、ただし board meeting に参加可。投資家が "意見表明 + 情報収集" の権利を持ちたいが director 責任を回避したい場合。

### 11.3 Protective Provisions (保護条項 / 拒否権)

優先株主が **過半数の承認なくして実行できない** 重要事項のリスト。

#### 11.3.1 NVCA 標準リスト

> **As long as 25% of the Series A Preferred remains outstanding, consent of the holders of a majority of the Series A Preferred is required for the Company to:**

1. **Charter / Bylaw amendment** (定款・付属定款の変更)
2. **株式 buyback** (例外あり: vesting に基づく従業員株の buyback、ROFR 行使)
3. **Liquidation Event** の承認 (M&A、解散)
4. **新規優先株 (Series A と同等以上) の発行**
5. **Series A の権利義務の変更** (preference の縮小等)
6. **配当の宣言**
7. **取締役会の規模変更**
8. **Subsidiary の設立 / 売却**
9. **Debt 借入 (一定額超)**
10. **IPO の承認** (場合により)
11. **重要な業態変更**

#### 11.3.2 例: M&A の "double trigger"

NVCA 標準では、M&A は (a) 全株主 majority、(b) 当該優先株 majority、の両方が必要 → "double trigger" → 投資家の拒否権を強める。

### 11.4 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Board seats | 必須 (Lead に 1 席) | Founder 過半数を維持したい |
| Independent director | 中立性確保 | "Mutual approval" で創業者拒否権 |
| Protective Provisions | 広いリスト | 短いリスト |
| Voting threshold | 過半数 | 2/3 (= 高ハードル) |
| Board observer | 追加情報アクセス | 議決権なしなら容認 |

---

## 12. Redemption Rights (償還請求権)

### 12.1 概観

特定期間 (典型的には発行から 5-7 年) 経過後、投資家は会社に対して **優先株の買戻し (= 投資元本の現金返金)** を請求できる権利。

### 12.2 NVCA 標準 (近年の傾向)

> **Series A Preferred shall be redeemable at the option of holders of at least a majority of the Series A Preferred commencing any time after the [5th] anniversary at a price equal to the Original Purchase Price plus declared and unpaid dividends. Redemption shall occur in 3 equal annual portions.**

- 償還価格: Original Purchase Price + accrued dividends (= 1x preference 相当)
- 行使開始: 発行から 5 年後
- 分割償還: 3 年に分けて支払 (会社のキャッシュ負担を分散)
- 会社が支払 unable な場合 → 利息加算 / equity 戻入 / penalty

### 12.3 数値例

- Series A 投資 $10M、5 年後償還、3 年分割
- 年 $3.33M の償還キャッシュアウトが 3 年連続発生

→ 会社が IPO や M&A をできない場合の "soft exit" として機能。

### 12.4 トレンド

- 米国 NVCA: 2010 年代以降、redemption rights は **削減傾向**。Equity 投資の本質と矛盾するため。
- 日本 VC: redemption rights を比較的強く要求する慣習がある (= "出口 OR 償還" の強制)。
- 償還可能な現金がない場合、投資家は cumulative dividend と組み合わせて事実上の debt 化を狙う。

### 12.5 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Redemption の有無 | 5 年で出口の保険 | 削除したい |
| 発動可能期間 | 5 年 | 7 年以上に伸ばす |
| 分割償還 | 拒否 (= 一括償還) | 3 年分割を主張 |
| Dividend 加算 | Cumulative + redemption で確定リターン | 分離して交渉 |

---

## 13. ROFR / Co-Sale / Drag-Along / Tag-Along

### 13.1 Right of First Refusal (ROFR / 先買権)

#### 13.1.1 Company-Level ROFR

会社が、**創業者 / 既存普通株主による株式譲渡** の前に、**優先的に同条件で買い取る権利** を持つ。

> **Before any Common Stock holder transfers shares to a third party, the Company shall have the right to purchase such shares on the same terms.**

#### 13.1.2 Investor-Level ROFR (= Right of First Refusal)

投資家が、**会社が拒否した場合**、**同条件で買い取る権利** を持つ。

#### 13.1.3 順序 (NVCA 標準)

1. 創業者が "Notice of Intent to Transfer" を発行
2. 会社が 30 日以内に行使可否を判断 → 行使しない場合 (or 一部のみ行使)
3. 投資家 (Series A 等) が残余を行使可否を判断 → 行使しない場合
4. 創業者が第三者に譲渡

#### 13.1.4 例外 (Permitted Transfers)

- Family member / family trust への譲渡
- ESOP の vesting 行使に伴う譲渡
- Death / disability に伴う相続

### 13.2 Co-Sale Right (共同売却権 / Tag-Along Right)

創業者が第三者に株を売る場合、**投資家も同条件で同比率まで参加できる** 権利。

> **If a Common Stock holder transfers shares to a third party, the Series A Preferred holders shall have the right to participate in such transfer on a pro-rata basis at the same price and terms.**

#### 13.2.1 数値例

- 創業者 7,000,000 株、投資家 3,000,000 株 (= 70% / 30%)
- 創業者が 1,000,000 株を $10/share で第三者に売却したい
- Co-sale 行使後:
  - 創業者: 1,000,000 × 0.70 = 700,000 株を売却
  - 投資家: 1,000,000 × 0.30 = 300,000 株を同条件で売却
  - 合計 1,000,000 株、各 pro-rata 比率で減少

### 13.3 Drag-Along Right (強制売却参加権)

**過半数の投資家 + 創業者** が M&A 売却に同意した場合、**少数株主も強制的に同条件で売却に参加** させる権利。

#### 13.3.1 トリガ (NVCA 標準)

> **If the Board, holders of a majority of the Common Stock, AND holders of a majority of the Series A Preferred approve a Sale of the Company, all stockholders shall vote in favor and execute the transaction documents.**

NVCA は "**Triple Approval**" 方式 (Board + Common majority + Preferred majority)。

#### 13.3.2 保護条項

少数株主保護:
- 同条件性 (= "same form of consideration, same price per share")
- Indemnification cap (= 個人保証は売却対価の範囲内)
- No additional ongoing obligations

#### 13.3.3 数値例

- Series A 投資家 (60% 過半数) + 創業者 (70% common 過半数) + Board 多数 が $50M で M&A 同意
- 反対する小規模投資家 (10%) も強制的に売却参加 → 同 PPS で売却

### 13.4 Tag-Along Right (Co-Sale と類似だが厳密には異なる)

- **Co-Sale Right**: 投資家が、創業者の第三者譲渡時に **pro-rata で参加** できる
- **Tag-Along Right**: 同上だが、より広い場面 (大規模株主の譲渡全般) で発動できることが多い

実務では Co-Sale = Tag-Along として同一視される場合が多い。

### 13.5 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| ROFR | 投資先企業の株式市場をコントロール | 流動性確保のため除外を増やす |
| Co-Sale | 創業者の "secondary sale" 参加権を確保 | Family transfer などを除外 |
| Drag-Along | M&A 強制力で exit 確保 | 過半数閾値を高くする (2/3) |
| Triple Approval | 少なくとも自分のシリーズの majority 必要 | Founder consent を必須化 |

---

## 14. MFN / Information Rights / Pre-emptive Rights

### 14.1 MFN (Most Favored Nation) — Term Sheet 文脈

転換型ファイナンス (SAFE / Note) で見た MFN と類似。**優先株 Term Sheet で "MFN" が使われる場面**:

- Side letter 形式: 特定投資家が "他の投資家により有利な条件があれば適用" を要求
- 主に Lead 投資家以外の小規模投資家が交渉力を補うために要求

### 14.2 Information Rights (情報請求権)

#### 14.2.1 Standard Package (NVCA)

> **The Company shall deliver to each Major Investor:**
> - Annual audited financial statements within 90 days of fiscal year end
> - Quarterly unaudited financial statements within 45 days of quarter end
> - Monthly management financial statements within 30 days
> - Annual operating budget within 30 days prior to fiscal year start
> - Cap table updates upon request

#### 14.2.2 "Major Investor" の定義

通常、**$500K 以上 / 5% 以上** を投資した投資家のみが Information Rights を享受できる (小規模投資家は除外)。

#### 14.2.3 Inspection Rights

> **Each Major Investor shall have standard inspection and visitation rights, allowing them to inspect facilities, books, and records at reasonable times.**

### 14.3 Pre-emptive Rights / Right to Participate Pro Rata (新株引受権)

#### 14.3.1 概観

将来の資金調達で、**既存投資家が pro-rata の比率まで参加** できる権利。"Pro-rata Rights" と同義。

#### 14.3.2 NVCA 標準

> **All Major Investors shall have a pro rata right to participate in subsequent issuances of equity securities of the Company (excluding excluded securities), to maintain their respective ownership percentages.**

#### 14.3.3 Excluded Securities (適用除外)

- ESOP 発行
- M&A 対価
- 既存優先株の conversion
- ワラント行使等

#### 14.3.4 Super Pro-rata

> **Series A Investors shall have the right to purchase up to [150%] of their pro-rata share.**

新規ラウンドで、自分の比率を超えて参加できる権利。Lead 投資家が "double down" する仕組み。

#### 14.3.5 数値例

- Series A 投資家 25% 持分、Series B で $20M 調達
- Pro-rata Right → $20M × 25% = $5M まで参加可能
- Super Pro-rata 150% → $7.5M まで参加可能

### 14.4 投資家観点と創業者観点

| 観点 | 投資家 | 創業者 |
|---|---|---|
| Information Rights | 月次まで要求 | 四半期に抑える |
| Major Investor 閾値 | 低くしたい (例 $250K) | 高くしたい (例 $1M) |
| Pre-emptive Rights | 必須 | 抑える、Lead のみに付与 |
| Super Pro-rata | あれば嬉しい | 拒否 |
| MFN | 小規模投資家には必須 | できれば削除 |

---

## 15. その他の補助条項

### 15.1 Founders' Vesting (創業者株のベスティング)

> **Founders shall be subject to a 4-year vesting schedule with a 1-year cliff. Upon termination, unvested shares shall be subject to a Company repurchase right at the lower of cost or fair market value.**

- 4 年 cliff 1 年が NVCA 標準
- 既存創業者は priced round で **再ベスト** されることもある (= 既往配分のリセット)
- "Double Trigger Acceleration": (a) M&A AND (b) 関与終了 → 残余 vesting を加速

### 15.2 IP Assignment / Confidentiality

> **Each founder and key employee shall execute a Confidential Information and Invention Assignment Agreement (CIIAA / PIIA).**

- 既存業務関連 IP を会社に譲渡
- 競業避止義務 (適用法による有効性)

### 15.3 No-Shop (排他交渉条項)

> **For 30-45 days after signing this Term Sheet, the Company shall not solicit, initiate, encourage, or accept any other proposals for financing.**

- Term Sheet 署名後の 30〜60 日間、他投資家との交渉禁止
- DD のための時間確保

### 15.4 Founder Liquidity / Secondary

> **Up to $[X] of common stock from founders may be repurchased by the Company at the Series A price, subject to Investor consent.**

- Series B 以降で創業者個人に流動性提供
- 通常 $1〜5M 規模

**Founder secondary 持分 floor (E-H-027 解消):** Secondary 後の創業者保有 (common + vested options) は **総株式の 10% 以上** を維持すること。これは (a) operating motivation (= 残り 90% で会社価値を伸ばす経済 incentive) を保つ、(b) governance dilution と「founder is checking out」の signaling 回避、(c) 後続 round で founder bench mark (founder ownership <10% は warning sign) を満たすため。10% を割り込む secondary は VC 側からも reject されることが多い。10-15% range をターゲットに、secondary 規模を逆算する。

### 15.5 Registration Rights

> **Upon IPO, Series A Preferred holders shall be entitled to demand registration, piggyback registration, and S-3 registration rights.**

- Demand: 投資家が IPO 後の resale 登録を要求できる
- Piggyback: 会社主導の登録に乗っかれる
- S-3: 簡略化された登録 (実績ある会社限定)

---

## 16. 投資家観点と創業者観点の整理

### 16.1 経済条項のサマリー (双方の "勝ちポイント")

| 条項 | 投資家有利の極 | 創業者有利の極 | NVCA 標準 |
|---|---|---|---|
| Liquidation Multiple | 3x | 1x | **1x** |
| Participation | Fully Participating | Non-Participating | **Non-Participating** |
| Capped Participation | Cap 3x | Cap 1.5x | (ケースバイ) |
| Dividend | Cumulative 8% | Non-cumulative 0% | **Non-cumulative, if declared** |
| Anti-Dilution | Full Ratchet | なし | **Broad-Based WA** |
| Pay-to-Play | あり | なし | (ケースバイ) |
| Redemption | あり (5 年) | なし | (近年は削減傾向) |

### 16.2 支配条項のサマリー

| 条項 | 投資家有利の極 | 創業者有利の極 | NVCA 標準 |
|---|---|---|---|
| Board | Investor majority | Founder majority | **Tied (1:2:2)** |
| Protective Provisions | 広いリスト | 短いリスト | **NVCA 標準リスト** |
| Drag-Along | Single trigger | Triple trigger | **Triple trigger** |
| ROFR | あり | なし | **あり (Company → Investor)** |
| Pre-emptive | あり (super pro-rata) | なし | **Pro-rata for Major Investors** |

### 16.3 トレードオフの典型パターン

| 創業者が譲歩 → | 投資家が譲歩 → |
|---|---|
| Liquidation 1.5x | Participation を非参加型に |
| Cumulative Dividend を受け入れ | Anti-Dilution を broad-based に |
| Board に Independent 2 名 | Drag-along に Founder consent 追加 |
| Pay-to-Play 受け入れ | Redemption rights 削除 |

**Kitchen-sink rule (E-H-040 解消):** 1 つの Term Sheet に下記 7 項目のうち **3 項目以上** が同時に含まれる場合は **non-market** と認識し、(a) 全項目をまとめて譲歩交渉する、(b) または Term Sheet 全体の renegotiation を要求する、(c) それでも変わらないなら投資家変更を検討する。

1. Cumulative dividend (6%+)
2. Participating preferred (uncapped または 3x cap+)
3. Full ratchet anti-dilution
4. Redemption rights (5 年以内)
5. MFN clause for late-stage round
6. Single-trigger drag-along (Founder consent なし)
7. Founder personal guarantee (in reps & warranties)

これらは個別には妥協可能でも、累積した liquidation overhang は **3-5x** に達することが多く、創業者リターンが事実上消える (`05 §22, §23` の OPM tiebreak 参照)。

### 16.4 シード期 (J-KISS / SAFE) と Series A の比較

| 観点 | Seed (転換型) | Series A (priced) |
|---|---|---|
| 法的精緻 | 軽い | NVCA 標準フル装備 |
| Board | 通常なし | 標準 5 名構成 |
| Liquidation Pref | 1x (転換時に承継) | 1x non-participating |
| Anti-Dilution | なし | Broad-based WA |
| 弁護士費用 | $5K-$15K (米) / 50-100 万円 (日) | $30K-$80K (米) / 300-500 万円 (日) |
| 期間 | 数週間 | 2-3 ヶ月 |

---

## 17. Term Sheet レビューチェックリスト

以下は Term Sheet を受領した創業者 / アドバイザー / 弁護士が、3-5 日のレビュー期間で確認すべきチェック項目である。

### 17.1 経済条項 (Economic Terms)

- [ ] **Pre-money Valuation** が事業実績・comparables・将来計画と整合するか
- [ ] **オプションプール (ESOP)** が pre-money / post-money どちらに含まれるか (= "option pool shuffle")
- [ ] **ESOP 増分** が想定希薄化を超えていないか (10% / 15% / 20%)
- [ ] **Liquidation Preference** が **1x non-participating** か (それ以外なら警戒)
- [ ] **Capped Participation** がある場合、cap が 2x 以下か
- [ ] **Dividend** が **non-cumulative** か (cumulative なら debt 性に注意)
- [ ] **Anti-Dilution** が **Broad-Based Weighted Average** か (Full Ratchet なら強く拒否)
- [ ] **Pay-to-Play** の有無と、不参加時の penalty (普通株転換 / shadow series)
- [ ] **Redemption Rights** が 5 年以降 / 3 年分割で穏やかに設定されているか
- [ ] **MFN** が他投資家に付与されていないか (= 全 SAFE / 全 preferred 一斉再交渉リスク)

### 17.2 支配条項 (Control Terms)

- [ ] **Board** が **founder + investor + independent (2-2-1 or 1-2-2)** で tied か
- [ ] **Independent Director** の選任プロセスが mutual consent か
- [ ] **Voting Rights** が as-converted basis か
- [ ] **Protective Provisions** リストの長さ (NVCA 標準を逸脱していないか)
- [ ] **Liquidation Event** (Deemed) の定義が広すぎないか (= subsidiary 売却まで含むか)
- [ ] **Drag-Along** が **Triple Trigger** (Board + Common majority + Preferred majority) か
- [ ] **Drag-Along の indemnification cap** が売却対価以内か
- [ ] **ROFR** に Permitted Transfers (family / trust / estate) が確保されているか
- [ ] **Co-Sale** に Permitted Transfers が確保されているか
- [ ] **Pre-emptive Rights** が Major Investor のみに付与されているか
- [ ] **Super Pro-rata** が含まれていないか

### 17.3 創業者条項 (Founder Terms)

- [ ] **Founder Vesting** が 4 年 cliff 1 年で標準か
- [ ] **既存ベスティング** がリセットされないか (priced round 時の一斉再ベストの罠)
- [ ] **Double Trigger Acceleration** (M&A + termination) があるか
- [ ] **Founder IP Assignment** が完了しているか (CIIAA 締結済みか)
- [ ] **Non-Compete** の範囲が事業地域・期間で過剰でないか
- [ ] **Founder Liquidity (Secondary)** の枠があるか (Series B 以降)

### 17.4 情報・参加権 (Information & Participation)

- [ ] **Major Investor 閾値** が $500K-$1M で適切か
- [ ] **Information Rights** が四半期 + 年次で標準か (月次は重い)
- [ ] **Inspection Rights** が "reasonable times" に限定されているか
- [ ] **Pro-rata Rights** が Excluded Securities (ESOP / M&A 対価) で適切に carve out されているか

### 17.5 IPO / Exit 関連

- [ ] **Mandatory Conversion (IPO)** の minimum size が $50M+ で標準か
- [ ] **Mandatory Conversion (IPO)** の minimum PPS が 3x Original Issue Price 以下か
- [ ] **Registration Rights** (Demand / Piggyback / S-3) が NVCA 標準範囲か
- [ ] **Lock-up** 期間が 180 日で標準か

### 17.6 法律・手続 (Legal & Process)

- [ ] **No-Shop** 期間が 30-45 日で過剰でないか
- [ ] **Counsel Fees** が会社負担で、上限 ($30K-$50K) が設定されているか
- [ ] **Closing Conditions** に過剰な MAC clause がないか
- [ ] **Reps & Warranties** が標準範囲 (founder reps が個人保証になっていないか)
- [ ] **Indemnification** 条項が standard escrow / cap で抑えられているか
- [ ] **Confidentiality** of Term Sheet 自体の有無 (公表 / 非公表)
- [ ] **Expiration** 日が明示されているか (典型的には 14-21 日)

### 17.7 J-KISS / SAFE 固有のチェック

- [ ] **Cap** が事業実績比で reasonable か
- [ ] **Discount** が 15-25% で標準か
- [ ] **適格資金調達** の閾値 (1 億円 / $1M) が早すぎ・遅すぎないか
- [ ] **満期** (J-KISS 18 ヶ月 / Note 12-24 ヶ月) と次回ラウンド計画が整合するか
- [ ] **MFN** の有無
- [ ] **Pro-rata Side Letter** の有無
- [ ] **複数 SAFE / J-KISS 重畳時の cap 多層化** で想定希薄化が許容範囲か
- [ ] **Liquidity Event 時の payout** (1x cash or convert) が明記されているか
- [ ] (J-KISS) **新株予約権の登記** が予定されているか
- [ ] (J-KISS) **エンジェル税制** 適用可否を税理士と確認したか
- [ ] (Note) **利息**が単利 / 複利 / 5-8% で標準か
- [ ] (Note) **Change of Control Premium** が 1.5x-2x で標準か
- [ ] (Post-money SAFE) 後続 SAFE による創業者希薄化シナリオを cap table モデルで検証したか

### 17.8 数値モデリング検証

- [ ] **Pro-forma cap table** を作成し、転換後の各株主持分を計算したか
- [ ] **Exit waterfall** ($10M / $50M / $100M / $500M) で投資家・創業者・ESOP の取り分を計算したか
- [ ] **Down round シナリオ** (50% 減価) で Anti-Dilution 発動後の希薄化を計算したか
- [ ] **次回ラウンド (Series B) でのバリュエーション必要水準** を逆算したか (= "what does Series A need to be worth at Series B for founders to keep > X%?")
- [ ] **複数 SAFE / J-KISS の連立** を解いたか (cap なし SAFE がある場合は iterative)

### 17.9 弁護士・税理士確認

- [ ] **Series 専属の弁護士レビュー** を受けたか (会社側 vs 投資家側で別弁護士)
- [ ] **税理士** に株式報酬・ストックオプションの税務影響を確認したか
- [ ] **会計士** に種類株式の純資産表示 / 仕訳を確認したか
- [ ] (海外投資家がある場合) **米国法 / Cayman 法等の準拠法整合性**を確認したか
- [ ] **既存契約 (シード期 SAFE / J-KISS / 銀行借入 covenants)** との衝突がないか確認したか

---

## 18. 参考文献・出典

- **Y Combinator** — SAFE Financing Documents. https://www.ycombinator.com/documents
- **Y Combinator** — Primer for Post-Money SAFE v1.1 (PDF)
- **Y Combinator** — The Y Combinator Standard Deal. https://www.ycombinator.com/deal
- **Coral Capital** — J-KISS: 誰もが自由に使える、シード資金調達のための投資契約書. https://coralcap.co/j-kiss/
- **Coral Capital** — J-KISS をブリッジ調達に使うときに気をつけたい 4 つのこと (2022). https://coralcap.co/2022/07/j-kiss-bridge/
- **NVCA** — Model Legal Documents. https://nvca.org/model-legal-documents/
- **AngelList** — Series Seed Documents (open source).
- **Cooley GO** — Series Seed templates.
- **会社法** (法律 第 86 号、平成 17 年) — 第 199 条以下 (募集株式)、第 236 条以下 (新株予約権)、第 445 条 (資本金・資本準備金)、第 911 条 (登記事項)。
- **法人税法** — 第 22 条 (各事業年度の所得の金額の計算)、第 61 条の 3 (有価証券の譲渡損益)。
- **租税特別措置法** — 第 41 条の 19 (エンジェル税制)。
- **会社計算規則** — 第 76 条 (純資産の部の表示)。

---

## 19. SAFE × Anti-Dilution × Pool Refresh State Machine

> **本章のスコープ** — §1〜§18 では SAFE / J-KISS / Note / 種類株式条項を **個別** に解説した。本 § は priced round (Series A/B/...) における **同時発動** (concurrent triggers) を **state machine** として形式化する。具体的には:
> 1. 転換型 (SAFE / J-KISS / Note) の conversion
> 2. 既存優先株の anti-dilution adjustment
> 3. ESOP option pool top-up / refresh
> 4. 新規 priced shares 発行
>
> これらが **同一 board minute / 同一 closing date** で発生するとき、処理順序を文書化しないと implementation が一意に決まらず、各株主の持分が ±5-15% 変動する (= 監査 C で C-C-001..015 として検出された Critical issues)。
>
> 本章は §2 (SAFE)、§3 (J-KISS)、§4 (Note)、§7 (LP)、§9 (Anti-Dilution)、§13 (Drag-Along) と **04b §1-10 (cap table mechanics)** を統合する。

### 19.1 Round Event の canonical 順序 (6-step pipeline)

新規 priced round (= "Round X") が closing するとき、以下の 6-step を **simultaneous resolution** として処理する。**順序は契約と implementation で固定** することが必須 (= NVCA 標準 / YC post-money SAFE 標準)。

#### Step 1: Snapshot pre-round cap table

**Input**: 直前 round (Round X-1) closing 後の cap table。
**Output**: 全株主の保有株数 / 持分 / class を凍結 (= "as of immediately prior to the X Closing")。

| 項目 | 内容 |
|---|---|
| Founder common | F₀ shares |
| Common other | C₀ shares (early angels, advisors, ESOP exercised) |
| Pool reserved | P₀ shares (未付与) + G₀ shares (付与済 unvested + vested unexercised) |
| Series A-1 / J-KISS / Note (preferred / SAFE) | 各 series の as-converted shares (転換価格 ICP_old) |
| Convertible 未転換 | SAFE / J-KISS / Note の **face amount** (= 株式数なし、 trigger 待ち) |

**重要**: Snapshot 時点では SAFE / J-KISS / Note は **株式数を持たない** (= phantom shares または "warrant-like instrument")。Step 2 でのみ株式数を確定する。

#### Step 2: Resolve pending SAFE / J-KISS / Note conversions

**Input**: Step 1 snapshot + Round X の announced PPS (= `PPS_X` を仮置き) + Round X 投資額 (`INV_X`)
**Output**: 各 SAFE / J-KISS / Note の確定転換株式数

各 instrument の conversion price:

```
CP_i = min(
  cap_price_i,          # = cap_i / (Pre-money equivalent FDSO at conversion)
  discount_price_i,     # = PPS_X × (1 - d_i)
  PPS_X                 # MFN trigger なし時の floor
)
```

ただし **post-money SAFE** (YC v1.1 以降) の場合、`cap_i` は **post-money cap** であり投資家持分が固定 = `α_i = I_i / cap_i` (ただし cap が priced round PPS より高い場合は priced round で再計算; §19.4.1 参照)。

**MFN cascade resolution** (C-C-014 解消):
複数 SAFE が MFN を持つ場合、Step 2 内で以下を実行:

```python
# 全 MFN SAFE を最も投資家有利な terms に統一
def resolve_mfn_cascade(safes):
    mfn_eligible = [s for s in safes if s.has_mfn]
    if not mfn_eligible:
        return safes
    # cap / discount / pro-rata / MFN 自体を 4 軸独立に cascade
    best = {
        'cap': min(s.cap for s in safes),
        'discount': max(s.discount for s in safes),
        'pro_rata': any(s.pro_rata for s in safes),
        'mfn': True,
    }
    for s in mfn_eligible:
        s.update(**best)
    return safes
```

**収束**: cap が低い SAFE が discount は高くないなど **属性別に独立 cascade** する (= 属性間の混合 cascade はしない)。これは NVCA / YC の MFN 標準解釈。

#### Step 3: Apply anti-dilution adjustment to existing preferred

**Input**: Step 2 で確定した SAFE 転換株 (= 既に新規 common-equivalent として cap table に存在する状態) + Round X PPS
**Output**: 既存 preferred (Series A-1, A-2, ...) の **conversion ratio 更新** (= 新株発行ではなく ratio adjust が NVCA 標準)

**Series 別 trigger 判定** (C-C-019 解消):

```
for series_j in existing_preferred:
    if PPS_X < ICP_old_j:
        trigger = True
        if mode == "broad-based WA":
            NCP_j = OCP_j × (A + B_eff) / (A + C)
        elif mode == "full ratchet":
            NCP_j = PPS_X
        elif mode == "narrow-based WA":
            NCP_j = OCP_j × (A_narrow + B_eff) / (A_narrow + C)
    else:
        trigger = False  # series_j は不発
```

**`A` (pre-issue FDSO) の定義** (C-C-017 解消):
`A` には以下を **含める**:
- Step 1 snapshot の全 common (F₀ + C₀)
- Step 1 snapshot の existing preferred の as-converted shares (旧 ICP_old での換算)
- Step 1 snapshot の Pool 全部 (reserved + granted)
- **Step 2 で concurrent に転換する SAFE / J-KISS / Note の転換株** (= "Common Stock Equivalents Outstanding immediately prior to Round X")

`A` には以下を **含めない**:
- Round X で発行する新規 priced shares (= `C` に入る)
- Round X 後に追加する pool top-up (= `C` に入る)

**`B_eff`** (C-C-008, C-C-021 解消):
- Broad-based WA standard: `B_eff = INV_X / OCP_j` (= "理論最大 issuable")
- Pay-to-play 不参加 series については **強制 common conversion**: 当該 series の `B_eff` 寄与は 0、かつ当該 series shares は common に move (NVCA standard では現行 NCP で 1:1 conversion → 1:1 ratio で common に reclass; 詳細 §19.4.5)
- 既存 preferred のうち pay-to-play で参加しない series は anti-dilution の保護を失う

#### Step 4: Calculate option pool top-up (post-money basis)

**Input**: Step 3 後の adjusted FDSO (= conversion ratio update 反映済) + Round X target post-money pool % (= `T`)
**Output**: 新規 pool 拡大株数 `ΔP`

**式 (option pool shuffle, post-money basis)**:

```
T × FDSO_post = P₀_remaining + G₀ + ΔP
                        ↑                  ↑
              既存 unallocated + granted      拡大分
FDSO_post = FDSO_pre_with_step3 + ΔP + N_X        ← N_X は Step 5 で確定
```

これは Step 5 (新規 shares 発行) と循環するため、**closed-form** で同時に解く必要がある:

```
ΔP = (T × FDSO_post) - P₀_remaining - G₀
N_X = INV_X / PPS_X
PPS_X = (Pre-money - ESOP_top_up_value) / FDSO_pre_post_AD     # Pool が pre-money に含まれる場合
       OR
PPS_X = Pre-money / FDSO_pre_post_AD                           # Pool が post-money に含まれる場合
```

**Cross-reference**: 詳細な closed-form は **04b §12.2** を参照。本章は ordering の文書化に focus。

**注記 (C-C-012 解消)**: DD 期間中 (= Term Sheet 署名後 → closing 前) に ESOP 追加付与が発生した場合、その grant は Step 1 snapshot の `G₀` に組み込み、Step 4 の `T` 達成計算に反映する。Term Sheet で `T` 自体を再交渉せず、`ΔP` を増やすことで圧縮するのが投資家側のデフォルト要求 (= "no incremental grants without lead consent" clause で制御)。

#### Step 5: Issue new round priced shares

**Input**: Step 4 で確定した `ΔP`, `PPS_X`, `INV_X`
**Output**: Round X investor の保有株数 `N_X = INV_X / PPS_X`

注意: Step 5 は数学的に Step 4 と同時 (連立) に解く。**手続き的には** Step 4 → Step 5 の順序だが、cap table モデル (Excel / code) では closed-form で 1 step として実装する。

#### Step 6: Recalculate fully-diluted shares & reconcile

**Output**:
- FDSO_post = F₀ + C₀ + (existing preferred as-converted at NEW ratio) + ΔP + P₀_remaining + G₀ + N_X + (SAFE 転換株)
- 各株主持分 % = shares / FDSO_post
- Reconcile: Σ % = 100% (= 監査 check)

**順序遵守の重要性** (C-C-013 解消):
**Step 1 → 2 → 3 → 4 → 5 → 6** の順序が canonical。同日 board minute では文書上 1 つの transaction だが、**経済的には逐次** 計算する。代替順序 (例: pool refresh 先 → SAFE conversion 後) は持分が変わるため契約書 / Term Sheet で明示。

### 19.2 Triple-trigger Flow (J-KISS + Anti-Dilution + Pool refresh) — 完全数値例

#### 19.2.1 設定

| 項目 | 値 |
|---|---|
| 創業者 (Founder) | 6,000,000 株 (common) |
| Pool unallocated | 500,000 株 (= P₀_remaining) |
| Pool granted (vested unexercised) | 500,000 株 (= G₀) |
| Series A 既発 | 2,000,000 株 (preferred, OCP_A = ¥83,333/share) |
| Series A 投資額 | ¥166,666,667 (約 1.67 億円) |
| Series A AD mode | Broad-based WA |
| J-KISS 未転換 | ¥100,000,000 (1 億円, cap ¥500M, 20% discount) |
| Round B (priced) Target | Pre-money ¥1,000M, Raise ¥200M, Post-money ¥1,200M |
| Pool target | Round B 後 12% post-money |

**Pre-Round B FDSO (raw)** = 6.0M + 0.5M + 0.5M + 2.0M = 9.0M shares
**J-KISS 転換は phantom** (まだ shares なし)

#### 19.2.2 Step 1: Snapshot

| Holder | Shares | % FDSO (raw) |
|---|---|---|
| Founder | 6,000,000 | 66.7% |
| Pool unallocated | 500,000 | 5.6% |
| Pool granted | 500,000 | 5.6% |
| Series A (as-converted at OCP_A) | 2,000,000 | 22.2% |
| **FDSO_pre raw** | **9,000,000** | **100.0%** |

J-KISS ¥100M は phantom (not in FDSO yet).

#### 19.2.3 Step 2: J-KISS conversion at Round B

仮置き `PPS_B = ¥1,000M / 9,000,000 = ¥111.11/share` (raw)。
J-KISS conversion price 候補:

| 方式 | CP |
|---|---|
| Cap conversion | ¥500M / FDSO_at_cap_basis ※ |
| Discount conversion | ¥111.11 × 0.80 = ¥88.89 |
| Plain | ¥111.11 |

Cap basis: J-KISS pre-money cap ¥500M を **当時の "pre-financing fully-diluted basis"** で按分 → `CP_cap = ¥500M / 9.0M = ¥55.56`
(= J-KISS 投資家が cap で fully diluted ¥500M を base にした PPS で転換)

**Min**: ¥55.56 (cap が最も保護)
**J-KISS 転換株数** = ¥100M / ¥55.56 = **1,800,000 株**

**Updated FDSO with J-KISS (pre-AD, pre-pool, pre-Round B)** = 9.0M + 1.8M = **10,800,000 株**

J-KISS 投資家持分 (post-conversion, pre-Round B) = 1.8M / 10.8M = 16.67%
(これは ¥500M cap @ pre-conversion FDSO 9M を base にした効果的持分: ¥100M / (¥500M + ¥100M) = 16.67% で **ぴったり一致** = sanity check pass)

#### 19.2.4 Step 3: Series A Anti-Dilution

`PPS_B (raw) = ¥111.11`、`OCP_A = ¥83,333/share` × 1,000 で **比較スケール矛盾**。
これは設定を統一して `OCP_A = ¥83.33/share` に修正 (= 旧 round で 2.0M 株 × ¥83.33 = ¥166.7M raise 一致)。

**Trigger 判定**: `PPS_B = ¥111.11 > OCP_A = ¥83.33` → Series A は **不発** (up round)。

> 重要 (C-C-019 解消): Round B が当初の Series A から見て up round の場合、Series A の anti-dilution は trigger しない。実装で全 series 一律発動させる誤りに注意。

**Down round シナリオへの拡張** (§19.4.1 で詳述): 仮に Pre-money B が ¥500M (down) なら `PPS_B_down = ¥500M / 10.8M = ¥46.30 < ¥83.33` → Series A trigger。

このケースでの Broad-based WA:
- `A` = 10.8M (Step 1 snapshot 9M + J-KISS 転換 1.8M = pre-issue FDSO incl. concurrent SAFE conversions)
- `B_eff = INV_B / OCP_A = ¥200M / ¥83.33 = 2.4M`
- `C = INV_B / PPS_B_down = ¥200M / ¥46.30 = 4,319,654 株`
- `NCP_A = ¥83.33 × (10.8M + 2.4M) / (10.8M + 4.32M) = ¥83.33 × 13.2 / 15.12 = ¥72.74`
- Series A conversion ratio = ¥83.33 / ¥72.74 = 1.146× → effective Series A shares = 2.0M × 1.146 = **2,291,667 株** (= 291,667 株の phantom 増加)

#### 19.2.5 Step 4: Pool top-up to 12% post-money (Round B up case)

Up round case で続行:
- FDSO_pre_post_AD = 10.8M (AD 不発なので変化なし)
- Target: pool (granted + unallocated + new) = 12% × FDSO_post

```
Pool_required = 0.12 × FDSO_post
Pool_existing = 500K + 500K = 1,000,000 株
ΔP = Pool_required - Pool_existing
N_B = ¥200M / PPS_B
PPS_B = (¥1,000M - ΔP × PPS_B) / 10.8M    ※ pre-money に pool top-up を含める NVCA 標準
```

これを連立で解く (closed-form):

```
PPS_B × 10.8M = 1,000M - ΔP × PPS_B
ΔP = 0.12 × (10.8M + ΔP + N_B) - 1.0M
N_B = 200M / PPS_B
```

`x = PPS_B` と置く:
- ΔP = 0.12 × (10.8M + ΔP + 200M/x) - 1.0M
- ΔP × 0.88 = 1.296M + 24M/x - 1.0M = 0.296M + 24M/x
- ΔP = (0.296M + 24M/x) / 0.88 = 0.3364M + 27.27M/x

PPS 連立:
- 10.8x = 1000M - 0.3364M × x - 27.27M  (ΔP × x = 0.3364M × x + 27.27M)
- 10.8x + 0.3364x = 1000 - 27.27 = 972.73 (M scale)
- 11.1364 x = 972.73
- **PPS_B = ¥87.35**

逆代入:
- ΔP = 0.3364M + 27.27M / 87.35 = 336.4K + 312.2K = **648,600 株**
- N_B = 200M / 87.35 = **2,289,640 株**
- FDSO_post = 10.8M + 0.6486M + 2.2896M = **13.738M 株**

検算 (pool 比率): (1.0M + 0.6486M) / 13.738M = 1.6486M / 13.738M = **12.00%** ✓
検算 (Round B 持分): 2.2896M / 13.738M = **16.67%** = ¥200M / ¥1,200M ✓

#### 19.2.6 Step 5/6: 持分整理

| Holder | Shares | % FDSO_post |
|---|---|---|
| Founder | 6,000,000 | 43.7% |
| Pool unallocated (new total) | 1,148,600 | 8.4% |
| Pool granted | 500,000 | 3.6% |
| Series A | 2,000,000 | 14.6% |
| J-KISS converted | 1,800,000 | 13.1% |
| Round B investors | 2,289,640 | 16.7% |
| **FDSO_post** | **13,738,240** | **100.0%** |

> Founder 持分推移: 66.7% (pre-J-KISS) → 55.6% (post-J-KISS, pre-Round B) → **43.7% (post-Round B)**

希薄化 24.6% pt (= J-KISS 転換 + Series A 不変 + pool top-up 6.7M→8.4M = 1.7% pt + Round B 16.7%)。

**closed-form 検算** (creditor's algebra):
- Round B 投資家 16.67% (= 200/1200)
- J-KISS 持分は ¥100M / ¥600M = 16.67% (cap base で pre-money 500M post-money 600M ベース) → Round B で希薄化 (1 - 16.67%) = **13.89%**, table の 13.1% に近い (pool refresh 影響で わずかに小さい)
- Founder 計算: 6M / 13.738M = 43.68% ≈ **43.7%** ✓

### 19.3 解の存在 / 一意性

#### 19.3.1 Closed-form vs Iteration の判定 tree

```
SAFE / J-KISS / Note の数 N と各 cap の有無:
├── N = 0: Step 2 skip → closed-form (Step 4-5 の連立のみ)
├── N ≥ 1, 全て cap あり:
│   ├── 全て post-money SAFE: 持分固定 → closed-form
│   ├── 全て pre-money SAFE: cap 比 + Round PPS 比較 → closed-form (linear in PPS)
│   └── Mixed pre/post: closed-form (Step 2 内で each i 独立計算)
├── N ≥ 1, cap-less あり:
│   ├── cap-less SAFE 1 本のみ: closed-form (CP = PPS × (1-d) のみ)
│   └── cap-less SAFE 複数 + cap あり: 連立 → iteration 推奨
└── MFN cascade あり: cascade 後に上記分類 → 通常は closed-form
```

#### 19.3.2 Iteration 解法 (cap-less SAFE 複数 + pool top-up 同時)

**Pseudocode** (C-C-001 解消):

```python
def solve_round(state, target_pool_pct, raise_amount, pre_money,
                tolerance=1e-5, max_iter=50):
    """
    Returns: (PPS, ΔP, conversion_shares per SAFE, new_round_shares)
    Raises: NonconvergenceError if max_iter 超過
    """
    # 初期推定
    PPS = pre_money / state.fdso_pre
    history = [PPS]

    for i in range(max_iter):
        # Step 2: SAFE conversion at current PPS estimate
        conv_shares = {}
        for safe in state.safes:
            if safe.cap:
                cp = min(safe.cap / state.fdso_at_cap_basis,
                         PPS * (1 - safe.discount))
            else:
                cp = PPS * (1 - safe.discount)
            conv_shares[safe.id] = safe.amount / cp

        fdso_with_safe = state.fdso_pre + sum(conv_shares.values())

        # Step 3: AD ratio (skip for simplicity, AD は own iteration)

        # Step 4: Pool top-up + Step 5: New round (closed-form sub)
        # T × (FDSO_with_safe + ΔP + N) = Pool_existing + ΔP
        # N = raise / PPS_new
        # PPS_new × FDSO_with_safe = pre_money - ΔP × PPS_new (NVCA pre-money pool)
        # → PPS_new × (FDSO_with_safe + ΔP) = pre_money
        # → ΔP = T/(1-T) × (FDSO_with_safe + N) - Pool_existing/(1-T)
        # → PPS_new = pre_money / (FDSO_with_safe + ΔP)
        # → N = raise / PPS_new
        # 同時連立 (3 unknowns × 3 equations) を線形に解く
        T = target_pool_pct
        E = state.pool_existing
        # 式変形 (closed-form 部分):
        a = FDSO_with_safe = fdso_with_safe
        # post = a + ΔP + N
        # T × post = E + ΔP → ΔP = T × post - E = T(a + ΔP + N) - E
        #   ΔP(1-T) = T(a+N) - E → ΔP = (T(a+N) - E) / (1-T)
        # PPS = pre / (a + ΔP)
        # N = raise / PPS = raise × (a + ΔP) / pre
        # → N = (raise/pre) × (a + (T(a+N)-E)/(1-T))
        r_p = raise_amount / pre_money
        # N = r_p × (a + (T×a + T×N - E)/(1-T))
        # N = r_p × ((a×(1-T) + T×a + T×N - E) / (1-T))
        # N = r_p × ((a - E + T×N) / (1-T))
        # N(1-T) = r_p × (a - E + T×N)
        # N(1-T) - r_p × T × N = r_p × (a - E)
        # N × ((1-T) - r_p × T) = r_p × (a - E)
        N = r_p * (a - E) / ((1-T) - r_p * T)
        delta_P = (T * (a + N) - E) / (1 - T)
        PPS_new = pre_money / (a + delta_P)

        # 収束判定
        if abs(PPS_new - PPS) / PPS < tolerance:
            return PPS_new, delta_P, conv_shares, N

        PPS = PPS_new
        history.append(PPS)

        # 振動検出
        if i > 5 and abs(history[-1] - history[-3]) / PPS < tolerance:
            raise OscillationError("PPS oscillating between two values")

    raise NonconvergenceError(f"Did not converge after {max_iter} iterations")
```

**Tolerance 推奨**: `1e-5` (= 0.001%)。Production model では `1e-6`。
**Max iter**: 50 (= 通常 5-10 cycles で収束)。

#### 19.3.3 一意性条件 / 振動検出

**一意解が存在する条件** (C-C-001 解消):

```
Σ_i (I_i / cap_i)  +  (T - existing_pool_%)  +  (raise / post_money)  <  1
↑ SAFE 持分合計    ↑ pool top-up 持分    ↑ Round X 持分
```

これは「全 stakeholder の持分合計 < 100%」= founder + 既存 common に正の持分が残ることと同値。違反すると **数学的に解なし** (= founder shares が負)。

**振動の典型サイクル**:
- Cap-less SAFE × 2 + ESOP top-up: 通常 3-5 cycles で収束
- Cap-less SAFE が pool 計算に強く依存する設定では振動 (2-cycle) 検出 → tolerance を緩めるか、pool 計算を SAFE に先行させる代替順序を選ぶ

#### 19.3.4 MFN cascade resolution (詳細, C-C-014)

複数 MFN SAFE が異なる時期に発行された場合、最終 round trigger 直前に **属性別 cascade**:

| 属性 | Cascade rule |
|---|---|
| Cap | 全 MFN SAFE は最低 cap (= 投資家有利) に統一 |
| Discount | 全 MFN SAFE は最高 discount に統一 |
| Pro-rata | いずれか 1 本でも持つなら全員に伝播 |
| MFN itself | True を維持 |

**注意**: MFN を持たない SAFE は cascade 対象外。MFN holder のみが他の SAFE 条件をコピーする。

**Cascade 後の uniqueness**: cascade は idempotent (= 1 回実行で終了)、Series A trigger 前に 1 度のみ実行。

### 19.4 Edge Cases

#### 19.4.1 Down Round + Anti-Dilution + Pool Refresh の triple

**設定** (§19.2 の cap-down variant):
- Pre-money B = ¥500M (down vs 暗黙 ¥800M)
- Raise = ¥200M
- Post-money = ¥700M
- 全 §19.2 設定を継承、Pool target 12% post-money

**Step 2 (J-KISS conversion)**:
PPS_B (raw) = ¥500M / 9.0M = ¥55.56
Cap CP = ¥500M / 9.0M = ¥55.56 (= raw PPS と一致)
Discount CP = ¥55.56 × 0.80 = ¥44.44
**Min**: ¥44.44 (discount)
J-KISS 転換株 = ¥100M / ¥44.44 = **2,250,000 株**

**Step 3 (Series A AD)**:
PPS_B = ¥55.56 < OCP_A = ¥83.33 → Series A trigger
- A = 9.0M + 2.25M = 11.25M
- B_eff = ¥200M / ¥83.33 = 2.4M
- C = ¥200M / ¥55.56 = 3.6M
- NCP_A = ¥83.33 × (11.25 + 2.4) / (11.25 + 3.6) = ¥83.33 × 13.65 / 14.85 = **¥76.59**
- Series A ratio = 83.33 / 76.59 = 1.0879× → effective shares = 2.0M × 1.0879 = **2,175,820 株** (phantom +175,820)

**Step 4-5 (Pool + Round B issuance)**:
FDSO_post_AD_pre_pool = 6.0M (Founder) + 1.0M (existing pool) + 2.0M (Series A face, but phantom +0.176M from AD ratio) + 2.25M (J-KISS) = 11.25M shares (face)
Series A の AD は ratio 調整なので Series A shares 自体は 2.0M で変わらず、effective only。FDSO 計算では effective shares を使う:
FDSO_pre_pool_pre_round = 6.0M + 1.0M + 2.176M + 2.25M = **11.426M**

```
N_B = (200/500) × (11.426 - 1.0) / ((1 - 0.12) - (200/500) × 0.12)
    = 0.4 × 10.426 / (0.88 - 0.048)
    = 4.1704 / 0.832
    = 5.013M shares
ΔP = (0.12 × (11.426 + 5.013) - 1.0) / 0.88
   = (0.12 × 16.439 - 1.0) / 0.88
   = (1.9727 - 1.0) / 0.88
   = 0.9727 / 0.88
   = 1.105M shares
PPS_B = 500 / (11.426 + 1.105) = 500 / 12.531 = **¥39.90**
```

但しここで **Down round + AD cycle** が発生: Series A AD は元 PPS_B = ¥55.56 で計算したが、pool top-up を考慮すると実 PPS_B = ¥39.90 でさらに低い。AD を再計算する必要:
- C_new = 200 / 39.90 = 5.013M
- NCP_A_new = 83.33 × (11.25 + 2.4) / (11.25 + 5.013) = 83.33 × 13.65 / 16.263 = **¥69.94**
- New ratio = 83.33 / 69.94 = 1.1914× → effective Series A = 2.383M shares
- FDSO 再計算 → PPS 再計算 → AD 再計算 → ...

**この cycle は §19.3.2 の iteration で解く**。Cap table モデルでは iteration tolerance 1e-5 で 4-6 cycles 収束。

**最終解 (iteration 後の概算)**:
| Holder | Shares | % |
|---|---|---|
| Founder | 6.0M | ~31% |
| Pool (post-refresh) | ~2.3M | ~12% |
| Series A (effective) | ~2.4M | ~12% |
| J-KISS converted | 2.25M | ~12% |
| Round B | ~5.5M | ~28% |
| FDSO_post | ~19.3M | 100% |

Founder 大幅希薄化 (66.7% → ~31%) = down round + triple trigger の典型ダメージ。

#### 19.4.2 複数 J-KISS で適格資金調達 trigger 不一致

**Scenario** (C-C-005 解消):
- J-KISS A: ¥100M, cap ¥500M, **適格 = ≥ ¥150M**
- J-KISS B: ¥50M, cap ¥300M, **適格 = ≥ ¥80M**
- Series Pre-A 調達: ¥120M

**Trigger 判定**:
- A: 120M < 150M → **未 trigger** (J-KISS A は新株予約権として残存)
- B: 120M ≥ 80M → **trigger** (B は転換)

**Cap table 処理**:
1. Step 2 で J-KISS B のみ転換、J-KISS A は phantom 残存
2. Series Pre-A closing 後の cap table 上では J-KISS A は **footnote として "outstanding convertible" を明示**
3. 次 Series A (例: ¥250M) で J-KISS A trigger 時:
   - J-KISS A の cap ¥500M は **元の cap (Series Pre-A 前の FDSO 基準ではなく、当時の合意 cap)** をそのまま使う
   - 但し cap basis FDSO は Series Pre-A 後の現在 FDSO になる (= "conversion at next qualified financing on then-current FDSO")
   - 投資家持分 ¥100M / ¥500M = 20% は **Series Pre-A 後の post-money に対する 20%** ではなく、**Series Pre-A 後 + Series A 前 + J-KISS A 転換 only** の post-money ベースで計算

**Series A 投資家への開示**: Term Sheet に "Outstanding J-KISS A: principal ¥100M, cap ¥500M, will convert at this Series A closing" と明記。**未開示で closing すると Series A 投資家持分が想定 -3-5% pt 縮む**。

#### 19.4.3 IPO 時に SAFE 未転換 (Direct-to-IPO)

**Scenario** (C-C-004 解消): Series A をスキップして直接 IPO。SAFE 1 (¥50M cap ¥500M)、SAFE 2 (¥100M cap ¥1,000M)、IPO PPS ¥1,000、市場 valuation ¥100B (= 100M shares 想定)。

**転換 logic**:
各 SAFE 独立に以下 3 候補から最低を採用:

| SAFE | Cap CP | Discount CP (20% off) | IPO PPS | Min CP | 転換株 |
|---|---|---|---|---|---|
| SAFE 1 | 500M / 100M = ¥5 | 1000 × 0.80 = ¥800 | ¥1,000 | **¥5** | 50M / 5 = 10M 株 |
| SAFE 2 | 1000M / 100M = ¥10 | ¥800 | ¥1,000 | **¥10** | 100M / 10 = 10M 株 |

合計 SAFE 投資家 = 20M 株 / (100M + 20M) FDSO = 16.7%。
IPO PPS ¥1,000 base で SAFE 投資家価値 = 20M × ¥1,000 = ¥20B = SAFE 投資 ¥150M に対する 133× return。

**比較表 (Liquidity event payoff, C-C-009 解消)**:

| Instrument | M&A 時 | IPO 時 | Direct-to-IPO (Series A skip) |
|---|---|---|---|
| **SAFE** (post-money) | max(1x, as-converted) | 強制 convert at IPO PPS (cap / discount / PPS の min) | 上記 |
| **SAFE** (pre-money) | max(1x, as-converted) | 同上 | 同上、cap basis FDSO は IPO 直前 FDSO |
| **J-KISS** | max(1x or 1.5-2x premium, as-converted) | 強制 convert | 同上 |
| **Convertible Note** | max(principal + accrued + 1.5-2x premium, as-converted) | 強制 convert at IPO PPS | 同上 |

#### 19.4.4 Capped participation の cap 到達 → convert flip

**Scenario** (C-C-007 解消): Series A 投資 ¥100M, cap = 2x = ¥200M。Exit value V を変動させて投資家 payoff を計算。

**3 候補**:
1. **Pure preference**: ¥100M (= 1x LP のみ)
2. **Cap participation**: min(LP + α × (V - LP), cap)
3. **Convert to common**: α × V (= preference 放棄)

ここで `α = Series A as-converted % = 25%` と仮定。

| Exit V | Pure pref | Cap participation | Convert | Best |
|---|---|---|---|---|
| ¥50M | ¥50M (V 制約) | ¥50M | ¥12.5M | ¥50M (pref) |
| ¥200M | ¥100M | ¥100M + 0.25×(200-100) = ¥125M | ¥50M | ¥125M (cap-part) |
| ¥500M | ¥100M | min(¥100M + 0.25×400, 200) = ¥200M | ¥125M | ¥200M (cap) |
| ¥800M | ¥100M | ¥200M (cap 到達) | ¥200M | ¥200M (tie) |
| ¥800.001M | ¥100M | ¥200M (cap) | ¥200.0003M | **¥200.0003M (convert)** |
| ¥1,000M | ¥100M | ¥200M | ¥250M | **¥250M (convert)** |

**Cross-over closed-form** (cap = 2x, α = 25%):
Convert > Cap participation when α × V > cap → V > cap / α = ¥200M / 0.25 = **¥800M**.

> 実装上は `payoff = max(LP, min(LP + α(V-LP), cap), α × V)` の 3-way max で正しく計算。`min(cap, participating)` で止めると convert flip を見逃す。

#### 19.4.5 Pay-to-play 不参加 → conversion price 選択

**Scenario** (C-C-008 解消): Series A 1M shares @ OCP=¥500、AD で NCP=¥440、Series B down round で pay-to-play 発動。Series A 投資家は不参加 → 強制 common 化。

**転換株式数の 3 通り** (契約書で明示要):

| 方式 | Conversion ratio | Common shares 取得 |
|---|---|---|
| (a) NCP base (NVCA strict default) | OCP / NCP = 500/440 = 1.1364 | 1,136,400 株 |
| (b) OIP base | 1.0× | 1,000,000 株 |
| (c) 1:1 forced | 1.0× | 1,000,000 株 |

差: 13.64% (= 約 136K shares)。**契約条文確認必須**。

#### 19.4.6 2x LP + cumulative dividend cap (C-C-010)

**Scenario**: 投資 ¥500M, 2x non-participating, cumulative 8% × 7 年。

| 解釈 | Payoff |
|---|---|
| (i) "2x flat" | ¥1,000M (dividend は cap 内に吸収) |
| (ii) "2x + cumulative dividend (additive)" | ¥1,000M + ¥280M = ¥1,280M |
| (iii) "2x ceiling = max(2x, 1x + dividend)" | max(¥1,000M, ¥500M + ¥280M) = ¥1,000M |

NVCA 標準条文: "(i)x the Original Purchase Price plus accrued and unpaid dividends":
- "(2)x ... plus accrued and unpaid dividends" = 解釈 (ii) (additive)
- "(2)x or accrued, whichever is greater" = 解釈 (iii)

**契約書原文を逐語確認**。「2x LP」とだけ書く foreigners は (i) を意図することが多いが、日本語 Term Sheet では (ii) が標準的。

#### 19.4.7 Founder vesting cliff 前 exit (C-C-011)

**Scenario**: Founder 6M shares, cliff 12 ヶ月、入社 11 ヶ月で M&A ¥5,000M。Single-trigger acceleration なし。

**Vesting state**:
- Vested = 0 株 (cliff 未達成)
- Unvested = 6M 株 → buyback at ¥0.0001/株 (= vesting agreement の repurchase right)
- Founder cash payout = **¥600** (= 0.0001 × 6M)

**回避策** (契約条文):
- **Single-trigger acceleration**: M&A 発生で全 unvested が即座に vest
- **Double-trigger acceleration**: M&A + 退職 (CIC + Termination) で acceleration
- **Cliff waiver clause**: Term Sheet で "cliff waived if exit before cliff" を投資家に交渉

NVCA 標準は double-trigger。VC 投資家は single-trigger を嫌う (= acquirer の retention 圧力減)。

#### 19.4.8 Drag-Along Triple Trigger と少数株主保護 (C-C-015)

**Scenario**: Founder 70% common, ESOP 30% (vested unexercised, voting rights なし), Series A 25% preferred (= 別 class voting)。

Standard Triple Trigger drag-along:
- (i) Board majority (= Series A director + Founder director で OK)
- (ii) Common majority (= Founder 100% で OK, ESOP は voting なし)
- (iii) Preferred majority (= Series A 1 投資家で OK)

→ Founder + Series A 単独で **drag 発動**。Common minority (例: angel SAFE が転換した angel common) は強制売却 with no veto。

**改善条項 (founder-friendly drag)**:
- "Common majority" を **non-investor common majority** に修正 (= founder 単独 trigger 不可)
- **Minimum sale price** clause: drag 発動可能な最低 deal value を設定 (例: ≥ 2x last preferred price)
- **Tag-along** で minority に同条件売却権を保証

### 19.5 Cross-reference

- **§2** (SAFE): conversion mechanics の base
- **§3** (J-KISS): 適格資金調達 trigger
- **§7** (LP): exit waterfall
- **§9** (Anti-Dilution): broad-based WA / full ratchet 公式
- **§13** (Drag-Along): triple trigger
- **§17** (Term Sheet checklist): pool refresh 検証
- **04b §1-2**: cap table FDSO / option pool shuffle
- **04b §4**: anti-dilution 完全数式
- **04b §6**: exit waterfall 数値例
- **04b §10**: 大型 case study
- **04b §12** (本 round 追加): 連立解 boundary 条件 — 数値再現 / 限界条件 (※ ユーザ指定の "§11" は 04b 既存 §11 = "Cap Table DD チェックリスト" との衝突回避のため §12 に rename)

---

