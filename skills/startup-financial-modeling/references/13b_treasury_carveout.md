---
name: treasury_carveout
description: ホールディングス構造の Treasury / Cash Pooling / IPO Carve-out / グループ通算制度 / Stage 別 Holdco 戦略 / 連結モデル Excel 設計の正本。SKILL.md dispatch table の "Holdco / 連結 / Carve-out" entry の補完 reference として、`13a` (連結 core) と対で読まれる (Series D 以降 / IPO 準備期前提)。
type: reference
priority: P1
related: [_terminology, 12_tax_strategy, 13a_consolidation_core, 14_ipo_readiness, 11_debt_financing]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: Treasury / Carve-out / グループ通算 / Stage Holdco 戦略は本書を canonical とする
- **Routing**: [`_master_decision_tree.md §A`](_master_decision_tree.md) で「Holdco / Carve-out」が出た場合に `13a` とセットで参照
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (carve-out IS / cash pooling tie / グループ通算) を必ず実行
- **関連 reference**: `13a_consolidation_core` (連結手続核心) / `12_tax_strategy` (グループ通算 + Tax 影響) / `11_debt_financing` (Treasury 借入) / `14_ipo_readiness` (carve-out IPO 観点)

# ホールディングス Treasury / Carve-out / グループ通算 / Stage 戦略 リファレンス (13b)

本書は、ホールディングス (持株会社) 構造を持つスタートアップ・成長企業が IPO 準備期に直面する **Treasury / Cash Pooling / IPO Carve-out / グループ通算制度 / Stage 別 Holdco 戦略 / 連結モデル Excel 設計** の正本である。連結会計の核心 (連結手続・NCI・未実現利益消去・PPA 詳細・在外子会社換算) は 13a に委譲し、本書は **「親が子をどう束ね、どう資金を回し、どう IPO に向けて切り出し、どう税で連結するか」** を扱う。

> **本書の前提と分担**
>
> - 数値・基準・税率は 2026 年 5 月時点で確認した最新値 (令和 7 年度税制改正・令和 8 年度税制改正大綱・OECD Pillar 2 January 2026 side-by-side package・US OBBBA 2025 反映)。
> - 法令・規則の略称:
>   - **法** = 法人税法 / **措置法** = 租税特別措置法 / **会** = 会社法 / **金商** = 金融商品取引法 / **法令** = 法人税法施行令
>   - **ASBJ** = 企業会計基準委員会 / **企業結合会計基準** = 企業会計基準第 21 号 / **連結会計基準** = 企業会計基準第 22 号
>   - **ASC** = FASB Accounting Standards Codification / **IFRS** = 国際財務報告基準 / **IAS** = 国際会計基準
>   - **PCAOB** = Public Company Accounting Oversight Board / **AS** = PCAOB Auditing Standard / **SAB** = SEC Staff Accounting Bulletin
>   - **IRC** = U.S. Internal Revenue Code / **Treas. Reg.** = U.S. Treasury Regulations
>   - **OECD TPG** = OECD Transfer Pricing Guidelines (2022 改訂)
>
> **既存リファレンスとの分担**
>
> | 領域 | 担当ファイル | 本書 (13b) の扱い |
> |---|---|---|
> | 連結手続 / NCI / 未実現利益消去 / 在外子会社換算 / PPA 詳細 / Common Control 基本 | `13a_consolidation_core.md` (別エージェント担当) | 参照のみ。anti-pattern と仕訳例で軽く触れ、derivation は 13a 委譲。 |
> | Section 368 / 338(h)(10) / 適格組織再編の課税仕組み | `12_tax_strategy.md` §3 | 参照のみ。本書は spin-off と Carve-out の **設計判断** を扱う。 |
> | 日本国内 IPO compliance (主幹事 / 監査法人 / 短期審査) | `07_japan_specifics.md` §8 / `14_ipo_readiness.md` | 参照のみ。本書は **Carve-out FS の作り方** に絞る。 |
> | IPO 全体タイムライン (N-5 → N+1) / 3-stage gate / J-SOX | `14_ipo_readiness.md` | 参照のみ。`14` §5 関係会社整理から本書へ詳細委譲。 |
> | DTA/DTL の三表機械的処理 | `06_three_statement.md` §5 Tax Schedule | 参照のみ。本書は **戦略選択 (連結納税のメリ・デメ)** を扱う。 |
> | 法人実効税率 / Pillar 2 / Delaware Flip | `12_tax_strategy.md` §1, §5 | 参照のみ。 |
>
> **本書のスコープ宣言**
>
> 本書は IPO 準備期のホールディングス特有論点に限定する。スコープ内: ① Push-down Accounting の戦略適用判断、② Parent-only FS、③ Group Treasury / Cash Pooling、④ Carve-out FS、⑤ グループ通算制度、⑥ 連結モデル Excel 設計、⑦ Anti-patterns、⑧ DD 視点、⑨ Stage 別 Holdco 戦略、⑩ 数値例。スコープ外: 連結手続そのもの・PPA 計算詳細・NCI 計算・在外子会社換算メカニクス (すべて 13a)。

---

## 目次

1. **Push-down Accounting** — ASC 805-50 適用条件・仕訳・メリ/デメ・J-GAAP/IFRS 比較
2. **Parent-only Financial Statements (単体財務諸表)** — J-GAAP / IFRS / US-GAAP SEC 開示・子会社株式評価・連結 vs 単体差異
3. **Group Treasury / Cash Pooling** — Notional / Physical / ZBA・IC Loan・移転価格・連結織込み
4. **IPO 準備 / Carve-out Financials** — Carve-out FS 3 年・Direct vs Allocated・Stand-alone basis・PCAOB AS 5151・Common Control・US §355 Spin-off
5. **連結納税 / グループ通算制度 (日本)** — 通算制度 (2022.4〜)・移行・適用要件・開始/加入/離脱・5 年継続・開始時評価益・株式評価損否認
6. **連結モデル Excel 設計** — 12 シート構成例・シート間リンク・連結整合性チェック
7. **Anti-patterns** — IC net 表示・未実現利益消去漏れ・PPA intangible 漏れ等 9 項目
8. **投資判断 / DD 視点** — 連結グループ DD・Holdco 構造リスク・典型質問
9. **Stage 別 Holdco 戦略** — Pre-revenue から Post-IPO まで 5 段階
10. **数値例 (Mini Case 4 件)** — Carve-out FS / Cash Pooling / Holdco 分離 IPO / グループ通算開始時評価
11. **連結 DD チェックリスト**
12. **Holdco Structure 設計チェックリスト**

---

## 1. Push-down Accounting

### 1.1 概念と発生場面

**Push-down Accounting (取得価額の押下げ)** とは、被取得会社 (子会社) が、自社の単体財務諸表上で、取得日に **取得会社 (親) が認識した公正価値 (FV) ベースの資産・負債・goodwill を、自身の帳簿に反映させる** 会計処理である。

通常の連結会計では、PPA (Purchase Price Allocation) の結果は **連結 BS 上のみ** に反映され、子会社の単体 BS は従来の簿価のまま残る。Push-down はこれを **子会社単体まで押し下げる** 処理であり、連結と単体の数値乖離を解消する。

発生場面:
- 米国 SEC 登録子会社が親会社の SEC 報告に組み込まれる
- 親会社が IPO 時に Carve-out 対象事業の単体監査を受ける
- グループ内再編 (Common Control) で、新設 Holdco が事業会社を子会社化
- 内部管理上、子会社の単体 P/L を取得後 FV ベースで把握したい

### 1.2 ASC 805-50 適用条件 (US-GAAP)

ASU 2014-17 (FASB) により ASC 805-50 が改正され、**被取得会社の任意選択 (option)** となった。従来の SAB 54 (80% 以上保有時に強制) は廃止。

| 項目 | 改正前 (SAB 54) | 改正後 (ASC 805-50, ASU 2014-17 以降) |
|---|---|---|
| 80% 以上保有 | 強制 push-down | 任意選択 |
| 95% 以上保有 | 強制 push-down + 公開債務発行体は強制 | 任意選択 |
| 80% 未満 | 不可 | 任意選択 (change-in-control event 必要) |
| 選択タイミング | 取得時のみ | 取得時、または翌期 (報告期限内) |
| 一度選択した後の取消 | 不可 | 不可 (irrevocable) |

**適用要件** (ASC 805-50-25-4 〜 25-7):
- (a) Change-in-control event が発生していること (取得・支配獲得)
- (b) 被取得会社自身が選択すること (親が強制できない)
- (c) 選択は取得日の報告期間中に行う

**80% 概念は消えていない**: 米国法人税の連結納税 (consolidated return) では IRC §1504 で **80% vote + value** が要件であり、この閾値で push-down が事実上慣行化している。

### 1.3 仕訳 (子会社単体側)

#### 1.3.1 設例

親 P 社が子 S 社の 100% を 1,200 で取得。S 社の取得日簿価純資産 = 600。FV 評価で:
- 土地の FV up = +200 (簿価 100 → FV 300)
- 顧客関係 (intangible) FV = +150 (簿価 0)
- 開発済技術 (intangible) FV = +100 (簿価 0)
- DTL (実効税率 30% と仮定) = (200 + 150 + 100) × 30% = 135
- 認識可能純資産 FV = 600 + 200 + 150 + 100 - 135 = 915
- Goodwill = 取得対価 1,200 - 認識可能純資産 FV 915 = **285**

#### 1.3.2 子会社単体 (S 社) 側 push-down 仕訳

```
(借) 土地              200
(借) 顧客関係 (無形)   150
(借) 開発済技術 (無形) 100
                    (貸) DTL                      135
                    (貸) 評価差額金 (Push-down APIC)  315

(借) Goodwill          285
                    (貸) Push-down APIC           285

→ 結果: Push-down APIC 合計 = 315 + 285 = 600 (= goodwill + step-up 分)
```

ポイント:
- 反対勘定は **Additional Paid-in Capital (APIC)**。P/L には流さない。
- 親が支払った対価 1,200 そのものは子会社に現金流入していない (株式売買は旧株主との取引) ため、子会社の現金は動かない。push-down は会計上の調整。
- DTL は 取得日 FV と税務簿価の差から計算 (ASC 740-10-25-3(d) の例外で goodwill には DTL を立てない)。

### 1.4 メリット / デメリット

| 観点 | メリット | デメリット |
|---|---|---|
| 連結との整合 | 単体 = 連結 取得後数値が一致。二重計算回避。 | 子会社の **歴史的情報 (history)** が断絶。 |
| 償却負担 | 取得後の単体 P/L が連結と同じ depreciation/amortization。 | 償却費増加で単体利益が低下 → 配当余力低下。 |
| 監査 | 親監査人と単体監査人の調整工数減。 | step-up 後の FV 評価と impairment test 工数増。 |
| 税務 | 米国: 税務基準は別 (税務帳簿は変わらず) → DTL 認識。日本: 単体課税所得への影響なし。 | DTL とブックの一時差異管理が複雑化。 |
| Lender / 既存債権者 | 純資産増加で leverage 比率改善に見える。 | 資本性勘定 (APIC) 増加であり、配当原資にならない (会社法 446 条の分配可能額計算上は除外)。 |

### 1.5 J-GAAP / IFRS との比較

| 基準 | Push-down 概念 |
|---|---|
| **US-GAAP (ASC 805-50)** | 任意選択。Change-in-control 後、被取得会社が選択。 |
| **J-GAAP (企業結合会計基準 21 号)** | 原則として **子会社単体には push-down しない**。連結上のみ FV 反映。例外: 共同支配企業 / 逆取得など特殊ケース。 |
| **IFRS 3** | Push-down 概念は **基準上明示なし**。実務では稀に親 SEC 開示要求から子会社 IFRS FS にも反映する例があるが、IFRS Foundation は中立。 |

> **モデリング上の影響**: US 子会社が SEC 開示対象 (S-1 等) になる場合のみ push-down 検討。日本子会社の単体 FS は通常簿価ベース。連結モデル上、push-down 採否で **05_PPA シートの仕訳を子会社 TB に流すか、連結消去 columns に流すか** が変わる。
> **投資判断観点**: Push-down 採用済 子会社の **単体 ROE は構造的に低下** (分母増・分子は減価償却増)。同業比較時に注意。
> **Stage 別優先度**: Pre-revenue / Early = 不要 / Pre-IPO (US) = 必須検討 / Post-IPO 米子会社 = 採用検討。

---

## 2. Parent-only Financial Statements (単体財務諸表)

### 2.1 各基準の取扱い

| 基準 | 単体 FS の位置づけ |
|---|---|
| **J-GAAP** | **単体 FS が法定** (会社法 435 条 2 項 + 計算規則)。連結 FS は金商法上場会社のみ強制。中小・非上場は単体のみ。 |
| **IFRS (IAS 27)** | Separate Financial Statements は **任意 / 法域要求次第**。連結 FS が主、単体 FS は法令や規制で要求された場合のみ作成。 |
| **US-GAAP** | SEC 登録会社の場合、Reg S-X Rule 5-04 / 12-04 で **Schedule I (Parent-only Condensed FS)** を、子会社の純資産が連結純資産の **25% 超** で配当制限ある場合に提出。 |

### 2.2 子会社株式の評価

#### 2.2.1 J-GAAP (金融商品会計基準 / 企業会計基準 10 号)

**評価方法**: 取得原価 (cost method)。市場価格のない株式 (子会社株式) は時価評価しない。

**減損 test** (基準 21 項):
- 「**実質価額が著しく低下したとき**」減損処理
- 実質価額 = 1 株あたり純資産 (簿価) または時価
- 「著しく低下」= 概ね **50% 程度以上の下落**
- 回復可能性が見込めない場合は減損

**仕訳例**: S 社株式の取得原価 100、実質価額 30 (60% 下落、回復不能)。

```
(借) 子会社株式評価損 70
                     (貸) 子会社株式  70
```

P/L 上は **特別損失** に計上。

**DTL / DTA**:
- 評価損は **損金不算入** が原則 (法人税法 33 条 / 法令 68 条) → 一時差異 → DTA 認識可能性検討
- ただし将来の減資・解散見込み等で損金算入見込めない場合は DTA 計上不可

#### 2.2.2 US-GAAP (Parent-only)

**評価方法**: **Equity method** (ASC 323) を Schedule I で使用。子会社純資産の持分相当 + 子会社利益の持分。

**減損 test**: ASC 323-10-35-32 — Other-than-temporary impairment (OTTI)。

#### 2.2.3 IFRS (IAS 27.10)

**選択肢 3 つ**:
- (a) Cost method
- (b) IFRS 9 (FVTPL or FVOCI)
- (c) Equity method (IAS 28 を準用)

選択は事業 unit ごとに一貫適用。一度選択した方法は継続。

### 2.3 連結 vs 単体 差異 reconciliation

#### 2.3.1 主要差異項目

| 項目 | 連結 | 単体 (J-GAAP) | 差異の方向 |
|---|---|---|---|
| 売上 | グループ外向けのみ | 親会社の売上 + 子会社からの IC 売上 | 連結 < 単体合算 (IC 消去分) |
| 子会社株式 | 消去 | 取得原価 | 連結 < 単体 (株式と純資産消去) |
| Goodwill | 認識 | なし | 連結 > 単体 |
| 子会社 NCI 純資産 | NCI として表示 | 認識せず | 連結 > 単体 |
| 子会社からの受取配当 | 消去 | 営業外収益 | 連結 < 単体 P/L |

#### 2.3.2 数値 reconciliation 例 (純利益)

```
親単体 純利益                                  100
+ 連結子会社 (100% 保有) 純利益                 80
- 子会社からの受取配当 (親 P/L 計上分)         (30)
- 未実現利益消去 (棚卸資産 IC 売買)              (5)
- のれん償却 (J-GAAP のみ)                      (10)
+ NCI 帰属利益除外 (もし NCI あれば)             (0)
─────────────────────────────────────────────
連結 純利益 (親会社株主帰属)                   135
```

(IFRS / US-GAAP では のれん償却なし、impairment 時のみ)

### 2.4 SEC Schedule I 開示 (US 上場時)

**要件** (Reg S-X 5-04 / Rule 12-04):
- 子会社の **制限付純資産 (restricted net assets) が連結純資産の 25% 超** の場合
- 「制限」= 子会社から親への配当・貸付・前払が、現地法・ローン契約・規制で阻まれる場合
- Schedule I は **Condensed BS / IS / CF の 3 表 + 子会社配当受領明細 + 重要な開示事項**

**典型的に発動するケース**:
- 中国子会社 (送金規制) を持つ
- 銀行子会社 (規制資本制約)
- ローン covenant で子会社 → 親の dividend に上限がある

> **モデリング上の影響**: 連結モデルでは連結 FS が主だが、**親単体 P/L (IC 配当受取・IC 利息・株式評価損) のロジック** を別 tab に置くと、配当政策・分配可能額計算で必要になる。
> **投資判断観点**: 「お金が降りない」リスク (子会社 → 親へ送金できない) の早期検出は単体 BS で行う。連結だけ見ているとミスする。
> **Stage 別優先度**: Series A 国内単一法人 = 単体のみで十分 / 海外子会社あり = 単体重要度高 / IPO 準備 = SEC 上場なら Schedule I 検討。

---

## 3. Group Treasury / Cash Pooling

### 3.1 Cash Pooling 3 方式

#### 3.1.1 比較表

| 方式 | 物理的資金移動 | 法的な資金所有 | 利息計算 | 主な利用国 | 連結会計上の注意 |
|---|---|---|---|---|---|
| **Notional Pooling** (バーチャル) | なし | 各子会社のまま | 銀行が グループ合算で計算 | UK / NL / SG / HK | IC 債権債務発生せず。連結消去不要。日本国内は事実上不可 (相殺許認可)。 |
| **Physical (Cash Concentration)** | あり (毎日 sweep) | Master Account (親 or 専用 SPC) | 各 IC ローン残高で計算 | US / EU / JP | IC 債権・IC 債務が日次で発生 → 連結 BS で **同額相殺消去**。 |
| **ZBA (Zero Balance Account)** | あり (営業日末に残高ゼロに sweep) | Master Account | 各 IC ローン残高で計算 | US / JP | Physical の一種。日次残高ゼロ化により日次 IC 残高変動。 |

#### 3.1.2 Notional Pooling のメリ/デメ

メリット:
- 子会社の cash autonomy 維持 (法的所有変わらず)
- 銀行手数料効率
- 為替リスク notional 相殺

デメ:
- 日本では **預金者保護・相殺禁止** の論点で導入困難
- Basel III 以降、銀行側コスト増 (グロス計上要求)
- グループ内連帯保証 (cross-guarantee) を銀行が要求するケースが多い → グループ全体保証で個社の信用力毀損

#### 3.1.3 Physical Pooling のメリ/デメ

メリット:
- 各国 OK (規制クリアしやすい)
- グループ全体の余剰資金を Holdco で運用可能
- 短期借入の機動性

デメ:
- 子会社 → 親 の sweep が **配当ではなく貸付** であることを明確にしないと税務リスク (源泉税・移転価格)
- 各国の **薄資本税制 (thin capitalization)** で IC 利息損金不算入リスク
- 中国・インド等の **資本規制国** は sweep 禁止 / 上限あり

### 3.2 IC Loan (Inter-company Loan) と移転価格

#### 3.2.1 OECD TPG 第 X 章 (Financial Transactions, 2020 追加)

IC Loan の利率設定は **arm's length principle** に従う。CUP (Comparable Uncontrolled Price) 法が原則。

**金利決定要素**:
- (a) Borrower の credit rating (グループ親会社 rating ではなく **stand-alone rating**)
- (b) Loan 期間 / 返済条件 / 担保
- (c) 通貨建て
- (d) Implicit support (親会社の暗黙保証) — OECD は限定的に認める

**金利の構成**:
```
IC 金利 = リスクフリー金利 (国債利回り) + 信用スプレッド + 流動性プレミアム
```

#### 3.2.2 Safe Harbor 比較

| 国 | Safe Harbor / Simplification |
|---|---|
| 日本 | 措置法 66 の 5 (過少資本税制): 借入金利息は 自己資本の 3 倍まで損金。措置法 66 の 5 の 2 (過大支払利子): 調整所得 20% 超は損金不算入 (BEPS Action 4 対応)。 |
| 米国 | IRC §163(j): 調整 EBIT (注: TCJA 以降 EBIT ベース) の 30% (OBBBA 2025 以降の取扱は 12 を確認)。 |
| EU | ATAD: EBITDA 30% (各国実装あり)。 |
| OECD | Pillar 2 とは別に、利息損金算入制限を促す勧告 (BEPS Action 4)。 |

#### 3.2.3 IC Loan 仕訳例 (日本)

P 社 (親) → S 社 (子) に 100,000、年利 3%、期間 1 年。

P 社単体:
```
貸付時:
(借) 関係会社短期貸付金 100,000
                     (貸) 現金     100,000

期末利息計上:
(借) 未収利息          3,000
                     (貸) 受取利息 3,000
```

S 社単体:
```
借入時:
(借) 現金             100,000
                     (貸) 関係会社短期借入金  100,000

期末利息計上:
(借) 支払利息          3,000
                     (貸) 未払利息          3,000
```

連結消去仕訳:
```
(借) 関係会社短期借入金 100,000
                     (貸) 関係会社短期貸付金 100,000

(借) 受取利息          3,000
                     (貸) 支払利息          3,000

→ 連結 BS / P/L 上、IC loan は跡形なく消える
```

### 3.3 Cash Sweep / Cash Advance の流れ

```
[日次タイムライン]
09:00 各子会社口座: 顧客入金 / 仕入支払
17:00 営業日末残高確定
17:30 各子会社口座 → Master Account へ自動 sweep
       → 子会社 BS: 現金預金 ↓ / 関係会社短期貸付金 (Holdco 向け) ↑
       → Holdco BS: 関係会社短期借入金 (子会社別) ↑ / 現金預金 ↑ ※実態は同口座管理銀行内
18:00 Holdco がグループ余剰運用 / 短期 MMF 投資
翌 09:00 子会社が支払必要時、Master → 子会社へ Cash Advance (逆方向 IC loan)
```

### 3.4 Centralized Treasury のメリット

| 領域 | 効果 |
|---|---|
| Working capital | グループ全体の余剰・不足を相殺、外部借入 net 額を最小化 |
| 為替 | グループ FX exposure を Holdco で集中ヘッジ (Natural hedge + 残部のみ external) |
| 銀行交渉 | 取引行集約で fee 削減 (年 0.2-0.5% 規模) |
| 資金可視化 | グループ TMS (Treasury Management System) で日次 cash position 把握 |
| 投資運用 | 余剰を Holdco で MMF / 国債運用 (子会社単独より高利回り) |
| KPI ガバナンス | DSO / DPO / Cash Conversion Cycle をグループ統一 KPI で管理 |

### 3.5 連結モデルへの織込み

連結モデル `08_IC_Loans` シート / `09_Cash_Pool` シートでの取扱い:

```
[08_IC_Loans シート]
行: IC pair (P→S1, P→S2, S1→S2 ...)
列: 期末残高 / 期中平均残高 / 利率 / 利息 / 通貨

行レベルチェック:
  Lender 側 受取利息 = Borrower 側 支払利息  (同額)
  Lender 側 期末残高 = Borrower 側 期末残高  (同額)

連結消去 (シート 04_Eliminations へ自動連動):
  IC 貸付金 / 借入金 → BS 同額相殺
  IC 受取利息 / 支払利息 → P/L 同額相殺

→ 連結 BS / P/L 上、IC は完全に消える
```

> **モデリング上の影響**: IC loan 残高が日次変動する physical pooling では、**期末日残高 と 期中平均残高 の両方を持つ** こと (利息は平均、BS は期末)。
> **投資判断観点**: グループ内の cash 移動透明性は、子会社 minority interest 投資家 (NCI 株主・LBO lender) の最大関心事。詳細は §8.2。
> **Stage 別優先度**: Series A 単一法人 = 不要 / B 海外子会社 = 簡易 manual sweep / Pre-IPO = TMS 導入 + 移転価格文書整備。

---

## 4. IPO 準備 / Carve-out Financials

### 4.1 Carve-out Financial Statements とは

**Carve-out FS** = 親会社グループのある事業 (segment / division / subsidiary cluster) を、あたかも独立企業であったかのように切り出して作成する財務諸表。発生場面:

- (a) **IPO**: Holdco の一事業を子会社化して上場 (例: ソフトバンクグループ → Z Holdings、リクルート → Indeed)
- (b) **M&A divestiture**: 親が事業を第三者に売却するため Sell-side が作成
- (c) **Spin-off / Split-off**: 親株主に対象事業の株式を交付
- (d) **規制要請**: SEC Reg S-X 3-05 (significant acquisition の S-1/8-K 開示)

### 4.2 Carve-out FS の 3 年分要件

| 開示先 | 過去年数 | 監査 / レビュー |
|---|---|---|
| 米国 SEC S-1 (IPO) | 3 年 (smaller reporting / EGC は 2 年) | 全期 PCAOB 監査 (要 PCAOB 登録監査人) |
| 米国 SEC 8-K (Significant subsidiary acquisition) | Significance 20-40%: 1 年 / 40-50%: 2 年 / 50%+: 3 年 (Reg S-X 3-05) | PCAOB 監査 |
| 日本 東証 IPO (グロース) | 2 期 (連結) | 監査法人 (公認会計士法) 監査 |
| 日本 東証 (プライム / スタンダード) | 5 期 (要約数値) + 直近 2 期は連結 / 単体 詳細 | 監査法人監査 |
| 日本 短信 / 適時開示 (重要な子会社取得) | 1 期 | レビュー |

### 4.3 Direct Cost vs Allocated Cost

Carve-out FS の最大の論点は **共通コスト (shared cost) の配賦**。Stand-alone basis での実態を表すべきか、過去の親会社配賦実績を反映すべきか。

| Cost 種類 | 性質 | Carve-out 上の取扱い |
|---|---|---|
| **Direct cost** | 対象事業に直接帰属 (人件費・直接 R&D・対象事業専属設備の減価償却) | 全額計上。 |
| **Allocated cost** | 親共通機能 (Group Finance / IT / Legal / HR / 親 IR / 親 Tax / 親 CEO 等の corporate overhead) | **合理的配賦基準** で配賦。基準: 売上高比 / 人員比 / 利用工数比 / 固定資産比 / 従量課金。基準は **一貫適用** + 開示。 |
| **Non-recurring cost** (Carve-out のために 1 回だけ発生) | 例: separation 関連 advisor fee | Carve-out P/L 計上、ただし pro-forma adjustment で除外可。 |
| **Stand-alone cost** (独立後に新たに発生する見込みコスト) | CEO・CFO・上場維持・IR・自社 IT 等 | **Carve-out FS には計上せず**、別途 **pro-forma stand-alone cost adjustment** として開示。 |

#### 4.3.1 Allocated Cost の合理的配賦例

```
親 corporate overhead 1,000 (本社 IT 200 / Legal 150 / HR 200 / Finance 250 / Other 200)

[配賦基準の例]
本社 IT 200      → ユーザー数比     対象事業 30%  →  60
Legal 150        → 契約件数比       対象事業 40%  →  60
HR 200           → 人員数比         対象事業 25%  →  50
Finance 250      → 売上高比         対象事業 35%  →  87.5
Other 200        → 売上高比         対象事業 35%  →  70
─────────────────────────────────────────────
対象事業へ配賦   327.5
```

**SEC SAB Topic 1.B (Allocation of Expenses and Related Disclosures in Financial Statements of Subsidiaries, Divisions or Lesser Business Components of Another Entity)** が公式ガイダンス。

### 4.4 Stand-alone Basis 評価

Carve-out 後、対象事業が独立企業として持続可能かを評価。

```
[Stand-alone P/L 構築フロー]

Step 1: 過去実績の Carve-out P/L (allocated cost 含む)
Step 2: + Stand-alone Adjustment
        + 独立後 必要 corporate function コスト  (CEO / CFO / IR / 上場維持 / 監査法人 / D&O)
        - 親 allocated overhead (Step 1 で計上、独立後は不要)
        ± 独立後 サービス購入価格 (TSA = Transition Service Agreement で親から購入)
Step 3: = Pro-forma Stand-alone P/L
```

**TSA (Transition Service Agreement)**:
- Carve-out 後、一定期間 (通常 6-24 ヶ月) 親が対象事業へ IT / HR / Finance 等のサービスを継続提供
- 価格は arm's length。独立後の真のコスト水準にステップアップ。

### 4.5 監査要件

#### 4.5.1 PCAOB AS 5151 (旧称 / 現状況)

> **注意**: PCAOB AS 5151 は「Carve-out FS の監査」を直接タイトルにした基準ではなく、PCAOB は AS 2 series / AICPA AAG-CAR (Carve-out Financial Statements Audit and Attestation Engagements, 2020 改訂) を実務ガイドとする。米国 SEC 登録目的の Carve-out FS 監査は **PCAOB 監査人** が担当し、AICPA AAG-CAR の枠組み + PCAOB AS 一般基準で実施。

監査論点:
- **完全性**: 対象事業のすべての関連活動・取引が含まれているか
- **配賦の合理性**: 配賦基準の一貫性・開示の十分性
- **未認識資産・負債**: 親 BS 上の特定資産が対象事業に紐づくが従来未配賦のものがないか
- **関連当事者取引**: IC 取引が arm's length で、carve-out 上適切に表示されているか
- **税金費用**: stand-alone basis (separate-return method) または break-out from group return

#### 4.5.2 日本 監基報

監基報 805 (個別の財務表又は財務諸表項目に対する監査) を準用。実務上、IPO 監査では監査法人が **「特別目的の財務諸表」** として Carve-out FS を扱う。

### 4.6 Combination of Entities under Common Control

#### 4.6.1 概念

**Common Control 取引** = 同一支配下にある entities 間の組織再編 (親 → 子 / 子 → 子 / Holdco 設立)。

**会計処理の選択** (主要基準):

| 基準 | 取扱い |
|---|---|
| **US-GAAP (ASC 805-50)** | 取得法 (acquisition method) を **適用しない**。Carrying value (簿価) で承継。Pooling-of-interests like。 |
| **J-GAAP (企業結合会計基準 21 号 / 結合分離 33 号)** | 共通支配下の取引は **適正な簿価** で受入。差額は資本取引。 |
| **IFRS** | IFRS 3 適用除外。実務は **predecessor method** (親会社簿価) または **acquisition method** の選択 (会計方針)。 |

#### 4.6.2 仕訳例 (J-GAAP / 子会社化のための新設 Holdco)

旧構造: 個人株主 → 事業会社 A (簿価純資産 500)
新構造: 個人株主 → Holdco (新設) → 事業会社 A

**株式交換** (会社法 767 条):

```
[Holdco 側]
(借) 子会社株式  500  (※ 適正な簿価 = A 社簿価純資産)
                     (貸) 資本金 / 資本準備金  500

[A 社側]
仕訳なし (株主のみ変更、A 社の貸借対照表は不変)
```

#### 4.6.3 表示

**Carve-out FS では、Common Control 配下の事業統合は遡及的に統合表示** が一般的。
- US-GAAP: 全期間遡及して統合 (as-if pooling)
- J-GAAP: 統合した期から prospective が原則だが、IPO Carve-out 文脈では 3 期遡及表示が要請されるケース多

### 4.7 Spin-off / Split-off (US Section 355)

#### 4.7.1 取引パターン

| パターン | 内容 | 株主への影響 |
|---|---|---|
| **Spin-off** | 親が子会社株式を **既存株主に按分配当** (既存株主は親 + 子の両方を保有) | Holding 増加 |
| **Split-off** | 既存株主が **親株式を子会社株式と交換** (希望株主のみ) | Holding 振替 |
| **Split-up** | 親会社解散 + 複数子会社株式を株主に交付 | 親消滅 |
| **Sponsored Spin-off** | Spin と同時に第三者に少数持分売却 | 第三者参加 |

#### 4.7.2 IRC §355 Qualified (Tax-free) 要件

**5 大要件** (非課税適用条件):
- (a) **Control**: 親が子会社の **80% vote + 80% value** を spin 直前に保有
- (b) **Active Trade or Business (ATB)**: 親・子ともに spin 直後に **5 年以上継続している ATB** を有する
- (c) **Distribution**: 子会社株式 **すべて** または **支配持分 (80%)** を分配
- (d) **Not a Device**: 利益配当の代替 (device) でない
- (e) **Continuity of Interest / Business Enterprise**: COI / COBE 維持

非充足の場合、親・株主双方に **二重課税** 発生 (親に内在含み益課税、株主に配当課税)。

#### 4.7.3 Morris Trust / Reverse Morris Trust

Spin-off + 第三者との合併を組み合わせた節税スキーム。Spin-off で分離した子会社が第三者と合併する場合、§355(e) (anti-Morris Trust 規定) で **50% 超の支配権変動** が 2 年以内に発生すると親に課税。Reverse Morris Trust は子会社が小さい第三者を吸収合併し、子会社の旧株主が支配を維持する形で §355(e) を回避。

> **モデリング上の影響**: Spin-off モデルでは **親 BS から事業簿価分を減額**、株主資本側で「現物配当」として処理。Spin 後の親と子の pro-forma 3 表を別々に作成。
> **投資判断観点**: §355 qualified か否かで税負担が桁違い (qualified なら 0、non-qualified なら 35-50%)。Tax opinion (大手法律事務所の意見書) は必須。
> **Stage 別優先度**: Pre-IPO で米事業を切り出す場合 = 高 / 国内のみ Holdco 化 = 適用なし (日本は会社分割 + 税制適格組織再編で別法令)。

### 4.8 日本: 適格会社分割 (税制適格)

法 2 条 12 の 11 / 法令 4 条の 3。Carve-out で日本の事業を切り出す場合:

**適格要件 (新設分社型 100% 子会社化)**:
- (a) 金銭等不交付 (株式交付のみ)
- (b) 主要資産・負債の移転
- (c) 従業員の概ね 80% 引継
- (d) 事業の継続見込
- (e) 完全支配関係継続見込

適格 = 簿価承継 (課税繰延)。非適格 = 時価譲渡課税。

詳細は 12_tax_strategy.md §3 に委譲。

---

## 5. 連結納税 / グループ通算制度 (日本)

### 5.1 制度の沿革

| 期間 | 制度 | 主な特徴 |
|---|---|---|
| 〜 2002.3 | なし | 単体課税のみ |
| 2002.4 〜 2022.3 | **連結納税制度** (旧) | グループ全体で 1 つの確定申告。グループ通算した所得で申告。 |
| **2022.4 〜** | **グループ通算制度** | 各社別個に申告、ただし損益通算・税額計算で連動。電子申告。 |

旧連結納税は事務負担が重く、単体修正があると親含む全社が再計算という課題。グループ通算制度はこの欠点を改善した「individual filing + 損益通算」のハイブリッド。

### 5.2 通算法人 (適用対象) 判定

**要件** (法 64 の 9):
- (a) 内国法人で **完全支配関係 (100%)** を有する親法人
- (b) 親法人および当該完全支配関係にあるすべての内国法人 (子法人) が対象
- (c) 親法人は普通法人または協同組合等 (公益法人・人格のない社団等を除く)

**完全支配関係**:
- 直接 + 間接で 100% (※ 99.99% でも非該当)
- 従業員持株会等の例外で **5% 未満** の他社持分は無視可

**外国法人**: 子に外国法人がいても、その外国法人は **通算対象外** (日本の通算には参加しない)。

### 5.3 開始 / 加入 / 離脱

#### 5.3.1 開始

- 親法人が国税庁長官に **承認申請** (適用開始事業年度開始日の 3 ヶ月前まで)
- 承認後、完全支配関係にあるすべての国内子法人が **強制加入**
- 一度開始すると **5 年間継続義務** (法 64 の 10 III)

#### 5.3.2 新規加入

- 通算グループ親が新たに 100% 子会社を取得 → 取得日の事業年度から加入 (時点 join)
- 加入子は加入直前事業年度終了までで一旦区切り (みなし事業年度)

#### 5.3.3 離脱

- 100% 関係解消 (持分 99% 等への希薄化、第三者売却) → 離脱
- 離脱後 5 年間は再加入不可 (再加入制限)

### 5.4 5 年継続要件

**法 64 の 10 III**: 通算法人は、原則として継続して **5 年間** 適用しなければならない。やむを得ない事情で取消が認められるのは:
- 経済情勢の著しい変化
- グループ再編
- 国税庁長官の承認

**実務**: 開始判断は不可逆と捉えるのが安全。

### 5.5 開始時 / 加入時 評価益課税

**重要論点**: グループ通算開始 / 加入時に、子会社の **時価評価対象資産** が **時価で評価益・評価損** を計上し課税。

#### 5.5.1 時価評価対象法人

**評価対象**: 通算開始時 / 加入時の子法人 (加入時の親はそのまま簿価)。

**例外 (時価評価不要)**:
- (a) 親法人との間に完全支配関係を **5 年超** 継続している場合
- (b) いずれかの主要事業を継続することが見込まれる、かつ加入直前の従業員数 80% 以上が引続き従事すること、等の要件を満たす場合 (法 64 の 11 / 64 の 12)

#### 5.5.2 時価評価対象資産

| 資産 | 取扱い |
|---|---|
| 固定資産 (土地・建物・機械等) | 時価評価 |
| 棚卸資産 (一定の棚卸資産) | 時価評価対象 |
| 有価証券 (売買目的・満期保有除く) | 時価評価 |
| 金銭債権 (一定額以上) | 時価評価 |
| 繰延資産 | 時価評価 |
| **少額・含み損 5 千万円未満等の例外** | 時価評価対象外 |

#### 5.5.3 評価益の取扱い

```
時価評価益 = 時価 - 簿価
→ 加入直前事業年度の益金算入 (課税)
→ 評価減 (時価<簿価) は損金算入

[仕訳]
(借) 固定資産  XXX
                (貸) 評価益 (益金) XXX

→ その後の連結通算所得計算で他社の損失と通算可能
```

**留意**: 簿価が低く時価が高い (含み益) 子会社を新規買収して即時通算加入させる場合、**買収直後に評価益課税** が発生する。タイミング設計が重要。

### 5.6 子会社株式 評価損 否認

**法 33 条 5 項**: 通算グループ内の **通算子法人株式 (通算グループ内法人の株式)** について、原則として **評価損を計上しても損金算入不可**。

理由: グループ内で損失通算が可能なため、株式評価損で重ねて損金算入することを防止。

例外: 通算離脱直前など、特定要件で損金算入可能なケースあり。

### 5.7 損益通算と税額計算

#### 5.7.1 通算プロセス

```
Step 1: 各通算法人が 単体 所得 / 欠損金 計算
Step 2: グループ内で 所得法人 と 欠損金法人 の間で 損益通算
        - 欠損法人の欠損 → 所得法人の所得から控除
        - 配賦は 各法人の所得比 / 欠損比
Step 3: 通算後 個社所得 で 個社別 法人税額計算 (各社が申告)
Step 4: 試験研究費税額控除 / 外国税額控除 等は グループ単位 で計算後、個社配賦
Step 5: 個社別 確定申告 (e-Tax)
```

#### 5.7.2 損益通算の仕訳例

3 社グループ: P (親) 所得 +500、S1 所得 -200、S2 所得 +100。

```
[Step 2 通算前]
P 所得   +500
S1 所得  -200  (欠損法人)
S2 所得  +100

[Step 2 通算: S1 の欠損 200 を P, S2 の所得から所得比配賦]
所得法人合計 = 500 + 100 = 600
P へ配賦   = 200 × (500/600) = 166.67
S2 へ配賦  = 200 × (100/600) =  33.33

[通算後 個社所得]
P  所得  500 - 166.67 = 333.33
S1 所得  -200 + 200 = 0
S2 所得  100 -  33.33 =  66.67
─────────────────────────────────
合計     400  (= 元の単純合計)

[各社税額 (法定 23.2% + 地方等 → 簡易に 30% で計算)]
P    100.0
S1     0.0
S2    20.0
合計  120.0  (= 通算前単純合計と同じ; 通算は時間軸の前倒し)
```

> **モデリング上の影響**: 通算採用前後で、欠損子会社のキャッシュ税効果が劇的に変わる。連結モデル `10_Group_Tax` シートで、(a) 各社単体所得、(b) 通算配賦、(c) 通算後個社税額 の 3 段で表示。
> **投資判断観点**: 通算採用済みグループでは、子会社単体 ETR が大きく揺れる (通算後税額 / 通算前所得 で計算するため)。投資先評価では **連結 ETR** に揃える。
> **Stage 別優先度**: Pre-revenue / 単一法人 = 不要 / 国内子会社複数で欠損子と所得子が併存 = 採用検討 / Pre-IPO 国内 holdco 構造 = 採用前提で設計。

---

## 6. 連結モデル Excel 設計

### 6.1 シート構成 (推奨 12 シート)

| Sheet | 名称 | 役割 | 主要 input/output |
|---|---|---|---|
| **00_Cover** | 表紙 / 凡例 / 改訂履歴 / 単位 | モデル全体メタ情報 | 通貨単位 / 期間 / version |
| **01_Group_Structure** | グループ図 / 持株比率テーブル | 子会社一覧、持株比率、連結範囲 | 子会社 ID / 持株 % / 連結方式 (Full / Equity / Cost) |
| **02_Conso_FS** | 連結 BS / IS / CF | 最終アウトプット | sheets 03〜10 から集計 |
| **03_Subsidiaries** | 各子会社 TB (試算表) | 各社単体数値 input | 子会社別 sheet タブ |
| **04_Eliminations** | 連結消去仕訳 | IC 取引・投資資本消去・配当消去・未実現利益消去 | 自動算式 + 手動 entry |
| **05_PPA** | Purchase Price Allocation | のれん・無形資産 step-up・DTL | 取得日 FV / 簿価 / 配分 |
| **06_NCI** | 非支配持分 (Minority Interest) | NCI 計算 | NCI % / NCI 帰属 NI / NCI BS |
| **07_FX** | 在外子会社換算 | CR / AR / HR レート / CTA | 子会社別通貨 / レートテーブル |
| **08_IC_Loans** | IC ローン明細 | 貸借対 / 利息対 | Lender / Borrower / 金額 / 利率 |
| **09_Cash_Pool** | キャッシュプール明細 | 日次 / 月次 sweep | 各社残高 / Master 残高 |
| **10_Group_Tax** | 連結税効果 / 通算 | 通算後税額 / DTA-DTL | 各社 所得 / 配賦 / 税額 |
| **11_Sanity_Checks** | 整合性自動チェック | エラーフラグ表示 | チェックリスト (下記 6.3) |

### 6.2 シート間リンク (主要フロー)

```
[Input layer]
  03_Subsidiaries (TB)
       ↓
  per-entity Trial Balance (BS / PL 科目別)

[Translation layer (在外のみ)]
  03 → 07_FX: BS は CR、PL は AR で換算 → CTA を OCI へ

[Adjustment layer]
  03 → Conso TB (合算)
  + 05_PPA: 取得時 step-up + 償却追加
  + 04_Eliminations:
       投資-資本消去 (Investment in Sub × Sub Equity)
       IC 取引消去 (08 から自動連動)
       未実現利益消去 (棚卸資産・固定資産)
       配当消去 (Sub → Parent dividend を P/L から消去)
  + 06_NCI: NCI 帰属純利益 / NCI 残高
  + 10_Group_Tax: 通算配賦・税効果

[Output layer]
  Conso TB → 02_Conso_FS (BS / IS / CF / SCE)

[Validation]
  11_Sanity_Checks: 各レイヤーで integrity test
```

### 6.3 連結整合性チェック (11_Sanity_Checks)

最低限のチェックリスト (各セルに `=IF(check, "OK", "ERROR")`):

```
[Trial Balance Level]
□ 各子会社 単体 TB の 借方 = 貸方
□ Conso TB の 借方 = 貸方

[BS Equation]
□ 連結 BS: 資産 = 負債 + 純資産 (株主資本 + NCI + AOCI)

[Articulation]
□ 期首純資産 + 包括利益 - 配当 ± 株主取引 = 期末純資産
□ 期首現金 + キャッシュフロー (CF 計算書) = 期末現金 (連結 BS)

[IC Reconciliation]
□ 各 IC pair の Lender 残高 = Borrower 残高
□ 各 IC pair の Lender 受取利息 = Borrower 支払利息
□ 連結 BS 上 IC 残高 = 0 (相殺後)
□ 連結 PL 上 IC 損益 = 0

[Investment Capital Elimination]
□ Σ (Investment in Sub) - Σ (Sub Equity 持分相当) = 累積 goodwill ± impairment
□ 期初 NCI + NCI 帰属 NI - NCI 配当 + NCI 追加投資 = 期末 NCI

[FX Translation]
□ 在外子 期末純資産 (CR 換算) - 期初純資産 (CR 換算) - 当期純利益 (AR 換算) - 配当 = CTA 当期発生額
□ AOCI 期初 + CTA 当期 = AOCI 期末

[Tax]
□ 各社 ETR < 200% かつ > -100% (極端な値の検知)
□ 連結 DTA / DTL は子会社合計とロジック一致
□ 通算配賦合計 = 0 (グループ内で完結)
```

### 6.4 ベストプラクティス

| 領域 | プラクティス |
|---|---|
| 通貨 | 各シートに **通貨タグ列** を持つ。換算前と換算後を別 row で。 |
| 単位 | モデル全体で 1 単位 (千円 / 百万円 / USD millions)。混在禁止。 |
| 符号 | 借方 (+) / 貸方 (-) を一貫。費用・負債を符号反転で表現する場合は凡例で明示。 |
| Hard-code | input セル (黄色) と calculation セル (白) の色分け徹底。 |
| Time series | 列方向に period (月次 or 期次)。行内符号変化禁止。 |
| 監査証跡 | 04_Eliminations の各行に「目的 / 仕訳意味 / 算式参照」コメント必須。 |

詳細な Excel ベストプラクティスは `01a_modeling_standards.md` および `10_modeling_craft.md` を参照。

---

## 7. Anti-patterns

ホールディングス連結モデルで頻発する誤りと、その検出 / 修正方針。

### 7.1 IC を Net 表示

**症状**: 連結 BS 上 「関係会社債権 net = 0」 と表示し、IC 残高を total から完全消去前提で扱う。
**問題**: 単方向ではなく、各社 gross 残高を捕捉できないと、(a) 移転価格文書の根拠を失う、(b) IC 利息計算が double-count される、(c) 通貨ミスマッチが見えない。
**修正**: `08_IC_Loans` シートで gross gross matrix を作成。連結消去は **同額相殺** をシート分離で実施。

### 7.2 未実現利益消去 (Inventory) 漏れ

**症状**: 親 → 子の販売で、子の在庫に未実現マージン (IC profit) が含まれているのに、連結消去で除去せず連結利益が過大。
**問題**: グループ外への売却時点までは認識すべきでない利益を計上。
**修正**: 各期末 子在庫のうち IC 仕入分 × 親マージン率 = 未実現利益。
```
[消去仕訳]
(借) 売上原価 (連結 PL)  XXX
                         (貸) 棚卸資産 (連結 BS)  XXX
```
Detail derivation は 13a に委譲。

### 7.3 PPA で Intangible 認識漏れ → Goodwill 過大

**症状**: 取得時に **顧客関係 / 技術 / トレードネーム** 等の identifiable intangible を認識せず、すべてを goodwill 計上。
**問題**: (a) Goodwill は 償却なし (US-GAAP / IFRS) → 利益が過大、(b) Intangible なら有限耐用で償却、impairment テストも separable (FAS 142 / IAS 36)、(c) 監査人 reject。
**修正**: Big4 の valuation team と連携し、ASC 805-20-25-10 / IFRS 3.B31-B40 の identifiable criteria (separable または contractual-legal) で intangible を全件洗出し。
**13a 参照**: PPA 計算詳細は 13a。

### 7.4 持分変動を P/L 計上 (NCI 取引)

**症状**: 子会社株式の追加取得 (NCI 持分の親への譲渡) や一部売却を、P/L で「子会社株式売却損益」として計上。
**問題**: 支配を維持したままの持分変動は **資本取引** (equity transaction)。連結 PL を経由してはならない。
**修正**: NCI 残高の調整 + 資本剰余金で差額調整。
```
[NCI 5% 追加取得 (現金 50)、NCI 簿価 30]
(借) NCI                30
(借) 資本剰余金         20
                       (貸) 現金                 50
```
**注意**: 支配を失う取引 (50% → 40% 等) は逆に **PL 計上**。一部売却で支配維持なら資本、支配喪失なら PL。

### 7.5 CTA を毎期 P/L へ

**症状**: 在外子会社の換算差額 (CTA = Cumulative Translation Adjustment) を期間損益として P/L 計上。
**問題**: CTA は **OCI (その他の包括利益)** に累積し、子会社 disposal 時に PL へ recycling される (J-GAAP / IFRS)。US-GAAP は ASC 830 で同様。継続期間中は OCI に留まる。
**修正**: 換算差額仕訳は OCI へ。

### 7.6 Cash Pool IC 利息で連結 PL 過大

**症状**: Cash pool 内 IC 利息が消去されず、連結 PL に **支払利息 + 受取利息** の double counting。
**問題**: ネットゼロのはずの IC 利息で、利息収益・利息費用が両方 inflate し、連結 PL の財務収益性が歪む。Interest coverage ratio 等の指標が誤る。
**修正**: `04_Eliminations` で IC interest pair を明示消去 (受取利息 = 支払利息 同額相殺)。

### 7.7 Push-down 個別 vs 連結 数値ズレ

**症状**: 子会社 push-down 採用済なのに、連結モデルが旧簿価ベースで集計され、PPA 償却が二重計上 / 漏れ。
**問題**: 連結 = 子単体 (push-down 後) + 消去のフローで作るべきなのに、連結独自の PPA を別途乗せて二重。
**修正**: モデル内 **「PPA は子単体 push-down 済か?」** フラグを `01_Group_Structure` に持たせる。Yes なら `05_PPA` シートでの連結独自上乗せを抑止。

### 7.8 Common Control の FV 評価誤り

**症状**: Common control 配下の組織再編で FV (取得法) を適用し、goodwill を過大計上。
**問題**: Common control では US-GAAP / J-GAAP / IFRS のいずれも acquisition method を適用しない (簿価承継・predecessor 法)。FV 適用は基準違反。
**修正**: 取引実態の判定: 同一支配者 (個人 / Holdco) 配下か。Yes なら簿価承継で再編後簿価を引き継ぐ。

### 7.9 グループ通算 開始時評価益 見落とし

**症状**: 国内グループ通算制度開始 / 新規子会社加入時、**時価評価対象資産の評価益課税** を税効果会計上見落とし、開始期に予想外の現金税負担。
**問題**: 法 64 の 11 / 64 の 12 で、5 年超完全支配等の例外に該当しない子会社は、加入直前事業年度に時価評価益が発生し益金算入。これを失念すると IPO 直前期の利益・キャッシュ予測が大きく外れる。
**修正**: `10_Group_Tax` シートに **開始時評価益チェックリスト** を組込み、各子会社の (a) 完全支配 5 年超、(b) 主要事業継続見込、(c) 従業員 80% 引継、(d) 保有資産の含み益、を入力させる。

---

## 8. 投資判断 / DD 視点

### 8.1 連結グループ DD の 6 軸

| 軸 | 質問 | DD 検証手段 |
|---|---|---|
| **連結範囲** | 全子会社・関連会社 / 海外含む / VIE / SPE すべて把握済か | グループ組織図 / Cap table / 主要契約レビュー |
| **IC 取引正常性** | IC 売買 / IC ローン / IC ロイヤルティ / IC マネジメントフィーは arm's length か | 移転価格文書 / TP study / 国別報告書 (CbCR) |
| **VIE / SPE** | 子会社以外の支配 entity (VIE = Variable Interest Entity / SPE = Special Purpose Entity) を連結に含めているか | 契約一覧 / リース / JV / Funding 関係 |
| **海外子会社** | 中国 / インド等の **資本規制** で 親へ送金不能な余剰資金が積み上がっていないか | Trapped cash 分析 / 配当履歴 / 為替送金記録 |
| **Group CFO ガバナンス** | グループ統一会計方針 / 統一 KPI / 統一 monthly close / TMS 導入 | Group Finance manual / Close calendar |
| **連結の質** | 連結消去・PPA・税効果に reasoning と監査証跡があるか | 監査調書レビュー / 連結ワークシート |

### 8.2 Holdco 構造リスク

#### 8.2.1 「お金が降りない」リスク

**現象**: 連結 BS では大量の現金がある (例: 3,000 億円) が、Holdco 単体の現金は薄い (例: 50 億円)。子会社の現金は子の事業運転資金、規制資本、配当規制で動かせない。

**示唆**:
- 配当政策の柔軟性が低い
- 親自身の借入返済原資が限定
- M&A や自社株買いの実行には子会社からの up-stream が必要

**評価指標**: **Holdco-only Free Cash Flow** = 子会社からの 受取配当 + 受取利息 − Holdco 単体運営費 − Holdco 借入利払
**詳細**: `02_saas_metrics.md` のキャッシュ指標は連結ベースなので、Holdco については別途計算。

#### 8.2.2 IC 透明性リスク

**症状**: IC ローン金利が arm's length から大幅乖離 (低金利で資金移動 → 移転価格課税リスク)、IC マネジメントフィーが対価のないグループ全体配賦。

**DD 質問例**:
- 主要 IC 取引の TP method は (CUP / TNMM / RPM のいずれか)
- Local file / Master file / CbCR 提出履歴
- Tax audit での IC 関連指摘履歴

#### 8.2.3 連結の質リスク

**症状**: 連結 PL の **Bottom-up 検証** ができない。各子会社単体 → IC 消去 → PPA → NCI → 連結 PL の一貫トレースが資料化されていない。

**DD 質問**:
- 連結ワークシート (Excel / 連結ソフト export) の提供
- 過去 3 期の 連結 - 単体合算 差異要因分析 表
- 監査調書のうち連結対応セクションのアクセス

### 8.3 投資家の典型質問 (15)

1. 連結子会社・持分法適用会社・VIE / SPE の全件リスト + 持分・連結方式
2. 各子会社の単体 PL / BS (直近 3 期)
3. 主要 IC 取引一覧 (IC 売買・IC ローン・IC ライセンス・IC サービス)
4. 移転価格文書 (Local / Master / CbCR)
5. Cash pooling 構造 / TMS / IC funding policy
6. 海外子会社の trapped cash / 送金実績
7. PPA 詳細 (intangible breakdown / 償却スケジュール / impairment 履歴)
8. NCI 構造 (各子会社別 / NCI 株主 / Put/Call option)
9. 連結納税 / グループ通算採用状況 / 開始時評価益発生履歴
10. Holdco 単体 FS と分配可能額 (会社法 446 条)
11. 子会社配当方針 / 配当規制
12. 親グループ保証 (Cross-guarantee / Comfort letter / Keepwell)
13. 在外子会社の換算方針・主要レート / CTA 累計
14. Holdco 借入の covenant (Consol leverage 等)
15. 連結監査人 / 子会社単体監査人 (Big4 / 中堅 / 内部監査) の組合せ

---

## 9. Stage 別 Holdco 戦略

### 9.1 概観

| Stage | 法人構造 | Treasury | Tax | Carve-out 準備 |
|---|---|---|---|---|
| **Pre-revenue / Pre-seed** | 単一国内法人 | 単一口座、月次 close | 単体課税 | 不要 |
| **Early growth (Seed〜A)** | 国内 + 必要に応じ 海外 1 社 | 主要銀行 集約、簡易 manual sweep | 海外子の単体課税、移転価格 light | Carve-out FS 不要、ただし子会社 TB 月次取得 |
| **Scale (B〜C)** | 海外 subholdco 設置 (SG / NL 等) | TMS 導入、Physical pooling 開始、 hedge policy 整備 | 移転価格文書化、Pillar 2 影響評価 | 段階的 stand-alone FS 整備 |
| **Pre-IPO** | Holdco / Opco 構造確定、連結体固定 | Cash pool 完備、Group CFO setup | グループ通算検討、SOX-readiness | Carve-out FS (3 期遡及) 監査済み |
| **Post-IPO** | M&A 容易化のため Holdco 配下にプラットフォーム子会社 | Group Treasury Department、Cap markets 機能 | 連結納税フル運用、税効果会計 fluent | Carve-out FS 内製運用 |

### 9.2 Stage 別チェックポイント

#### 9.2.1 Pre-revenue / Pre-seed

- 株式構成・creator (個人) ↔ 法人 の関係が明確
- 法人格 1 つで OK。海外法人を Day 1 で作らない (実体・実費負担に見合わない)

#### 9.2.2 Early growth (Seed〜Series A)

- 海外売上比率 30% 超 → 現地子会社設立検討 (PE 課税回避)
- 親 → 海外子の **Initial capitalization** は equity / debt 比率を意識 (薄資本税制)
- 海外子の Bookkeeping は現地 GAAP + 連結用 J-GAAP/USGAAP の dual ledger 管理

#### 9.2.3 Scale (Series B〜C)

- **海外 subholdco** (Singapore / Netherlands / Ireland 等) を地域統括会社に。詳細は 12 の Pillar 2 / Delaware Flip 参照
- **Cash pool** 導入: SG / NL / UK は notional pool 容易、JP / US は physical
- **TMS** (Kyriba / FIS / Coupa Treasury 等) 導入
- 移転価格 文書化開始 (TP study)
- **連結会計ソフト** (DivaSystem LCA / e-Conso / Tagetik / OneStream 等) 検討

#### 9.2.4 Pre-IPO (N-3 → N-1)

- Holdco / Opco 構造の最終確定 (Carve-out 必要なら N-3 で実行)
- **連結体の固定**: IPO 主幹事審査前に連結範囲を確定
- Carve-out FS 3 期遡及作成 + PCAOB / 監査法人監査
- **グループ通算制度** 採用判断 (5 年継続義務に注意)
- J-SOX / SOX 404 構築 (詳細は 14 へ)

#### 9.2.5 Post-IPO

- 連結グループは買収プラットフォーム化
- 子会社株式取得は Holdco 経由で実施 (AP 仕訳 / push-down 検討)
- Group Treasury は Cap markets 機能 (社債発行・自己株買い・自社株報酬の取得) を担う
- 連結 ETR を IR 開示で説明 (連結 ETR が業界平均と乖離する場合の理由)

### 9.3 移行時の典型タイミング

```
Year 0 (Pre-seed)        : 単一法人 国内
Year 1-2 (Seed)          : 海外売上発生 → 海外子会社設立 (US Delaware C-corp / SG Pte Ltd 等)
Year 3-4 (Series A)      : 国内 + 海外子 1-2 社、連結開始 (任意 / 監査要件次第)
Year 4-5 (Series B)      : Subholdco 設置検討、Cash pool start
Year 5-6 (Series C)      : Holdco / Opco 分離検討、Carve-out 準備
Year 6-7 (Pre-IPO)       : Carve-out FS 3 期遡及作成、グループ通算採用判断
Year 7-8 (IPO)           : Filing / Listing
Year 8-   (Post-IPO)     : M&A platform 化
```

---

## 10. 数値例 (Mini Case 4 件)

### 10.1 Case 1: Carve-out FS 作成 (親会社事業切り出し)

**設定**:
- 親 P 社 (連結売上 100,000) のうち、SaaS 事業 (売上 30,000) を Carve-out して子会社化 + IPO
- SaaS 事業の 直接費用 (原価・直接 R&D・SaaS 専属人件費) = 18,000
- SaaS 事業 専属設備の減価償却 = 1,200
- 親 corporate overhead 全社合計 = 8,000
- 配賦基準: SaaS 売上 / 親連結売上 = 30%、SaaS 人員 / 親人員 = 25%
- TSA: IPO 後 12 ヶ月、親 IT サービスを 年 2,000 で購入 (現状 allocated 1,500 → 独立後 ステップアップ)

**Step 1: Carve-out P/L (allocated cost ベース)**

```
売上                           30,000
原価・直接費用              (18,000)
直接減価償却                 (1,200)
親 overhead 配賦 (混合配賦)  (1,950)  ※注 1
─────────────────────────────────
営業利益                        8,850
税金 (実効 30%)              (2,655)
─────────────────────────────────
当期純利益                      6,195

注 1: overhead 配賦の内訳
  IT (本社 IT 2,000)         × 25% (人員)  =  500
  Legal (本社 1,500)          × 30% (売上)  =  450
  HR (本社 1,500)             × 25% (人員)  =  375
  Finance (本社 2,000)        × 30% (売上)  =  600
  Other (本社 1,000)          × 25%        =  250  ※簡易
  合計                                       1,950 ※簡易例 (実務はもっと細分化)
```

ここで本社 overhead 8,000 のうち SaaS への配賦は 1,950 (約 24.4%)。

**Step 2: Stand-alone Adjustment**

```
Carve-out 営業利益                                    8,850
+ 親 overhead 配賦 戻し (1,950 = カーブアウト後不要)   1,950
- 独立 corporate function 必要コスト
   CEO/CFO/IR/上場維持/D&O                          (3,500)
- TSA 親からのサービス購入                           (2,000)
- 監査法人 (大手切替コスト)                            (300)
─────────────────────────────────────────────────
Pro-forma Stand-alone 営業利益                        5,000
税金 30%                                            (1,500)
─────────────────────────────────────────────────
Stand-alone 純利益                                    3,500

→ Carve-out FS が示す利益 6,195 vs Stand-alone 3,500 で 約 2,700 のギャップ
→ S-1 / 目論見書では 両方を 開示し、投資家に bridging 提示
```

**示唆**: Carve-out FS だけ見ると独立後の収益力を過大評価する。Stand-alone adjustment で実態を補正。

### 10.2 Case 2: Cash Pooling 導入の連結影響

**設定**:
- グループ: 親 P (JP)、子 S1 (US)、子 S2 (UK)
- 各社 Day 0 現金: P 1,000、S1 500、S2 300
- 各社 月次 net cash flow: P -200 (投資先行)、S1 +400、S2 +150
- Cash pool 導入前: 各社独立、外部短期借入 P が必要時 700 借入 (年利 5%)
- Cash pool 導入後: Master Account に毎月末 sweep、グループ余剰を Holdco で MMF 運用 (年利 3%)

**Before (Cash pool なし)**

```
Day 30 各社残高:
  P:   1,000 + (-200) = 800、ただし投資 invest 1,500 のため 700 を 5% で外部借入
  S1:  500 + 400 = 900 (idle、年利 0.1% 預金)
  S2:  300 + 150 = 450 (idle、年利 0.1% 預金)
  合計 idle 1,350、外部借入 700

年間 利息 (12 ヶ月仮定):
  P 支払利息    700 × 5% = 35
  S1 受取利息   900 × 0.1% = 0.9
  S2 受取利息   450 × 0.1% = 0.45
  ─────────────────────────────
  Net 利息費用 (連結)         33.65
```

**After (Cash pool 導入後)**

```
Day 30 Master Account 残高:
  P sweep:    800 → Master, P 残ゼロ → Master から 700 を P に Cash advance
  S1 sweep:   900 → Master
  S2 sweep:   450 → Master
  Master 残高 = 800 + 900 + 450 - 700 (Cash advance) = 1,450

外部借入: ゼロ (Master が P 必要分を内部 fund)
グループ余剰 1,450 を MMF 3% で運用

IC interest (Master ↔ P, S1, S2) は arm's length 金利 3%:
  P (借入 700)            支払 IC 利息  700 × 3% = 21
  S1 (Master へ預入 900)  受取 IC 利息  900 × 3% = 27
  S2 (Master へ預入 450)  受取 IC 利息  450 × 3% = 13.5
  Master:                 受取 21 (P から) + MMF 1,450 × 3% = 21 + 43.5 = 64.5
  Master:                 支払 27 (S1) + 13.5 (S2)         = 40.5

連結消去後:
  外部 利息 = 0 (借入なし)
  外部 受取 (MMF) = 43.5
  IC 利息は全消去 → 連結 PL 上 IC 利息 = 0
  ─────────────────────────────
  Net 利息収益 (連結)        +43.5

連結効果: Before -33.65 → After +43.5、改善 +77.15
```

**示唆**: Cash pool 導入で外部借入解消 + idle cash 運用化により連結 PL の財務収支が大きく改善。ただし IC 利息 21 (P) / 27 (S1) / 13.5 (S2) / 40.5 (Master) は arm's length 設定 + TP 文書化必須。

### 10.3 Case 3: Holdco / Opco 分離 IPO 準備

**設定**:
- 既存: 個人創業者 Founder → 事業会社 A (簿価純資産 5,000、含み益 R&D 資産 2,000)
- 目標: Holdco H 新設、H が A を 100% 子会社化、H が IPO で東証グロース上場

**手順 1: 株式交換 (会社法 767 条)**

```
[Day 0]
Founder ── 100% ──> A (簿価純資産 5,000)

[Day 1: H 新設、株式交換]
H 設立: 資本金 5,000 (Founder への新株交付)
A 株式は H に拠出される (簿価 5,000)

[Founder 側: 株式の振替]
Founder 持ち株: A 株式 → H 株式 に変更 (簿価 5,000 引継)

[H 側 仕訳 (Common Control = 簿価承継)]
(借) 関係会社株式 (A 社)  5,000
                         (貸) 資本金             2,500
                         (貸) 資本準備金         2,500

[A 側]
仕訳なし (Founder 株主が H に置換のみ)
```

**手順 2: 適格会社分割の判定**

会社分割ではなく株式交換なので、税制適格は **株式交換税制** (法 2 条 12 の 17)。Founder への金銭等不交付 → 適格 → 簿価承継、Founder への譲渡所得課税繰延。

**手順 3: IPO 前 連結 BS (簡易)**

```
[H 連結 BS, IPO 直前]
資産:
  現金預金            300 (H 本社運営費)
  関係会社株式 A     0 (連結消去)
  A 社 資産合計    7,000 (含み益再評価なし、簿価)
  goodwill             0 (Common Control)
  合計             7,300

負債:
  A 社 負債        2,000
  合計             2,000

純資産:
  資本金 (H)       2,500
  資本準備金 (H)   2,500
  利益剰余金 (H)        0 (新設のため)
  + A の 利益剰余金 取り込み (Common Control の as-if pooling)
  → 5,000 (これは A の歴史的 利益剰余金)

  ※ 注: Common Control の表記は、見方によっては資本金等のうち
    「資本剰余金 △2,500」と「利益剰余金 +5,000」など、
    実際の累積を表現する詳細表示 (IFRS predecessor / J-GAAP 共通支配下) になる。
    この例では簡略表記にとどめる。
```

**手順 4: IPO 後の典型構造**

```
新規株主 ← 新規株式発行 ← H ← 100% ── A
Founder ← 既存株式 ────┘

IPO 増資 (公募 1,500、売出は親株式) で:
H 連結現金 = 300 (元) + 1,500 (公募) = 1,800
H 純資産  = 9,500 (元) + 1,500 (公募) = 11,000 (簡易)
```

**示唆**: Holdco / Opco 分離で M&A プラットフォーム化を実現。IPO は H が実施し、A は 100% 子会社で事業継続。日本の株式交換税制で Founder の譲渡課税は繰延 (適格要件充足前提)。

### 10.4 Case 4: グループ通算制度 開始時の評価

**設定**:
- グループ: 親 P (国内)、子 S1 (国内、5 年超完全支配)、子 S2 (国内、加入 2 年)、子 S3 (国内、加入 1 年)
- 通算制度 適用開始日: 2026-04-01 開始事業年度
- 各社 含み益:
  - S1: 土地 含み益 +500、5 年超 完全支配 → **時価評価対象外**
  - S2: 機械装置 含み益 +800、加入 2 年 → 時価評価対象 / 主要事業継続見込 80% 引継 → 例外該当 → **対象外**
  - S3: 機械装置 含み益 +1,200、加入 1 年、主要事業未継続 (廃止予定あり) → 例外不該当 → **時価評価対象**

**Step 1: 開始時評価益 (S3)**

```
S3 機械装置 含み益 +1,200 → 開始直前事業年度に 益金算入
S3 単体 法人税: 1,200 × 30% (実効) = 360 の追加課税

[S3 仕訳]
(借) 機械装置                1,200
                            (貸) 評価益 (益金)        1,200

[税効果]
当期 法人税等 360 を当期計上、ただし
評価益分は その後の減価償却で損金として戻る → DTA 認識可能
(借) DTA                      360
                            (貸) 法人税等調整額       360
→ 当期純利益への影響 ネット 0、ただしキャッシュ税負担 360 発生
```

**Step 2: 通算開始後の損益通算 (1 期目)**

```
[各社 単体所得]
P    1,500
S1     800
S2     200
S3   -300 (構造改革損失で赤字)

通算前単純合計  +2,200

[Step 2 通算]
所得法人 P + S1 + S2 = 2,500
S3 欠損 -300 を所得法人へ配賦 (所得比)
  P 配賦   = 300 × (1,500/2,500) = 180
  S1 配賦  = 300 × (  800/2,500) =  96
  S2 配賦  = 300 × (  200/2,500) =  24

[通算後個社所得]
P    1,500 - 180 = 1,320
S1     800 -  96 =   704
S2     200 -  24 =   176
S3   -300 + 300 =     0
合計             2,200 (= 元の単純合計)

[各社 法人税 30% 簡易]
P    396
S1   211
S2    53
S3     0
合計  660

[通算なしの場合 (比較)]
P 1,500 × 30% = 450
S1  800 × 30% = 240
S2  200 × 30% =  60
S3 (-300 → 翌期繰越欠損 100% 利用前提だが、当期は 税 0)
合計           750

[通算によるキャッシュ削減効果]
通算なし 750 - 通算あり 660 = 90 (= S3 欠損 300 × 30%)
ただし、開始時評価益 360 を考慮すると、初年度ネット効果 = 90 - 360 = -270 (悪化)
※ 評価益 360 は将来の減価償却で取り戻されるため、長期では正
```

**Step 3: 5 年累計効果 (簡易)**

```
仮定: 通算メリット 年 90、評価益 360 は 5 年で 1/5 ずつ減価償却 (= 72 / 年)
評価益 一時課税 360 (Y1 のみ) − DTA 取り崩し 72 × 5 = 360 (Y1 - Y5)
通算メリット      90 × 5 = 450

5 年累計:
キャッシュ流出: 360 (Y1 のみ)
キャッシュ流入: DTA 取り崩しによる税減 72 × 5 = 360
通算メリット:  450
ネット 5 年累計: 450 ※ 評価益分は IO で見ると net zero
```

**示唆**: グループ通算採用判断は (a) 欠損子会社の有無 (大きいほどメリット)、(b) 開始時評価益の規模 (大きいほど初年度負担)、(c) 5 年継続義務の覚悟、を踏まえる。S3 のような新規加入子で含み益・主要事業廃止予定がある場合は、加入タイミングを設計する余地がある。

---

## 11. 連結 DD チェックリスト

| # | カテゴリ | チェック項目 | OK/NG |
|---|---|---|---|
| 1 | 連結範囲 | 全子会社 / 関連会社 / VIE / SPE の網羅リスト取得 | |
| 2 | 連結範囲 | 連結 / 持分法 / Cost method の判定根拠 | |
| 3 | 連結範囲 | 過去 3 期 連結範囲変動 (新規 / 除外) と理由 | |
| 4 | 持株関係 | 各子会社 持株比率 (直接 / 間接) | |
| 5 | 持株関係 | NCI 構造 (NCI 株主 / Put-Call option / 株主間契約) | |
| 6 | 単体 FS | 各子会社 単体 BS / PL 直近 3 期 | |
| 7 | 単体 FS | 親単体 (Holdco) BS / PL / 分配可能額 | |
| 8 | 単体 FS | SEC Schedule I 該当判定 (米上場の場合) | |
| 9 | IC 取引 | IC 売買・サービス・ローン・ライセンス・配当 一覧 | |
| 10 | IC 取引 | IC ローン pair の 借方・貸方 残高一致確認 | |
| 11 | IC 取引 | IC 利息 受取・支払 一致確認 | |
| 12 | 移転価格 | TP method (CUP / TNMM / RPM 等) と root cause | |
| 13 | 移転価格 | Local file / Master file / CbCR 提出履歴 | |
| 14 | 移転価格 | Tax audit 履歴 (TP 関連) | |
| 15 | Treasury | Cash pool 構造 (Notional / Physical / ZBA) | |
| 16 | Treasury | TMS 導入有無、月次 cash position 報告 | |
| 17 | Treasury | Trapped cash (送金規制国の余剰) 分析 | |
| 18 | Treasury | Cross-guarantee / Comfort letter 一覧 | |
| 19 | PPA | 過去 M&A の PPA レポート / Big4 valuation メモ | |
| 20 | PPA | Goodwill / 無形資産 償却スケジュール / 現価分析 | |
| 21 | PPA | Impairment test 直近実施日・結果 | |
| 22 | 未実現利益 | IC 仕入 in 棚卸資産 ロジック / 未実現利益消去額 | |
| 23 | 未実現利益 | IC 売買 固定資産 / 未実現利益消去 | |
| 24 | FX | 換算方針 / 主要為替レート 履歴 | |
| 25 | FX | CTA 累計 / 子会社 disposal 時の recycling 履歴 | |
| 26 | 税 | 連結 ETR と Statutory rate の reconciliation | |
| 27 | 税 | グループ通算採用 (有 / 無) / 開始日 | |
| 28 | 税 | 開始時評価益 / 評価損 履歴 | |
| 29 | 税 | DTA / DTL realizability 評価 (会社別) | |
| 30 | 税 | Pillar 2 (連結売上 750 百万 EUR 超) 該当判定 | |
| 31 | Carve-out | (IPO 想定先) Carve-out FS 3 期遡及作成有無 | |
| 32 | Carve-out | Allocated cost 配賦基準・継続性 | |
| 33 | Carve-out | Stand-alone adjustment 内訳 | |
| 34 | Carve-out | TSA 締結見込 (期間 / 金額) | |
| 35 | 監査 | 連結監査人 / 子会社単体監査人 一覧 (Big4 / 中堅) | |
| 36 | 監査 | 過去 3 期 監査調書での連結関連特記事項 | |
| 37 | 監査 | PCAOB 監査 (米上場想定) 開始時期 | |
| 38 | ガバナンス | Group CFO 設置 / Group Finance manual 整備 | |
| 39 | ガバナンス | 連結会計ソフト (DivaSystem / Tagetik 等) 導入 | |
| 40 | ガバナンス | 月次連結 close リードタイム (BD+X) | |

---

## 12. Holdco Structure 設計チェックリスト

| # | フェーズ | 設問 | 推奨 |
|---|---|---|---|
| 1 | 構造 | 創業時の法人格は 1 つか | Yes (Pre-revenue) |
| 2 | 構造 | 海外売上比率はいくらか | 30% 超で現地子会社検討 |
| 3 | 構造 | 海外子会社設立の jurisdiction 選定 | 12 の §1.1 / §5 参照 |
| 4 | 構造 | Subholdco (地域統括) は必要か | 海外子 3 社以上で検討 |
| 5 | 構造 | Holdco / Opco 分離の必要性 | 多事業 / IPO 前で検討 |
| 6 | 構造 | Common Control 再編の税務適格性 | 簿価承継 + 課税繰延 確認 |
| 7 | Treasury | 主要銀行集約 | 取引銀行 ≤ 3 行 |
| 8 | Treasury | Cash pool 方式選定 | JP/US: Physical / EU: Notional |
| 9 | Treasury | TMS 導入時期 | Series B〜C |
| 10 | Treasury | IC ローン arm's length 設定 | OECD TPG X 準拠 |
| 11 | Treasury | FX hedge policy | 連結 FX 30% 以上で必要 |
| 12 | Tax | グループ通算採用判断 | 5 年継続義務確認 |
| 13 | Tax | 開始時評価益 試算 | Pre-IPO で必須 |
| 14 | Tax | 移転価格文書 (Local / Master / CbCR) | Series B 以降 整備 |
| 15 | Tax | Pillar 2 影響評価 | 連結 750 百万 EUR 接近で必要 |
| 16 | Carve-out | 対象事業の direct/allocated 区分明確化 | N-3 で開始 |
| 17 | Carve-out | Stand-alone basis での 想定 cost 試算 | N-2 |
| 18 | Carve-out | TSA 範囲・期間・金額 | N-1 で締結 |
| 19 | 監査 | 監査法人 (4 大 / 中堅) 選任 | N-3 で短期審査 |
| 20 | 監査 | PCAOB 監査人 選任 (米上場想定) | N-3 |
| 21 | モデル | 連結会計ソフト 選定 | Pre-IPO までに導入 |
| 22 | モデル | 連結 Excel モデル 12 シート構成 | §6.1 参照 |
| 23 | モデル | 連結整合性 sanity check 自動化 | §6.3 参照 |
| 24 | モデル | Holdco-only FCF 別途算出 | Pre-IPO 必須 |
| 25 | ガバナンス | Group CFO 設置 | Series B 以降 |
| 26 | ガバナンス | 子会社 board governance 設計 | 海外子に派遣 director |
| 27 | ガバナンス | グループ会計方針 統一 | Pre-IPO 必須 |
| 28 | ガバナンス | 月次連結 close 完了日 | BD+10 (Pre-IPO) → BD+5 (Post-IPO) |
| 29 | IPO | 連結体固定 (Pre-IPO) | N-2 までに完了 |
| 30 | IPO | Holdco / Opco 役割分担 (IR / Treasury / M&A は Holdco、事業は Opco) | N-1 までに整理 |

---

## 主要参考文献

- ASBJ 企業会計基準第 21 号 (企業結合に関する会計基準)
- ASBJ 企業会計基準第 22 号 (連結財務諸表に関する会計基準)
- 国税庁 「グループ通算制度に関する取扱通達」 (2022.4 〜)
- 法人税法 第 64 条の 9 〜 64 条の 12 (グループ通算)
- 法人税法 第 33 条 (資産の評価損)
- 措置法 第 66 条の 5 (過少資本) / 66 条の 5 の 2 (過大支払利子)
- FASB ASC 805-50 (Common Control / Push-down)
- FASB ASC 830 (Foreign Currency Matters)
- FASB ASC 740 (Income Taxes)
- IFRS 3 (Business Combinations) / IAS 27 (Separate FS) / IAS 28 (Equity Method)
- PCAOB Auditing Standards / AICPA AAG-CAR (Carve-out FS Audit, 2020 改訂)
- SEC Reg S-X 3-05 / 5-04 / Rule 12-04 / SAB Topic 1.B
- IRC §355 (Spin-off) / §1504 (Affiliated Group) / §163(j)
- OECD Transfer Pricing Guidelines for Multinational Enterprises (2022 改訂) Chapter X
- OECD Pillar 2 Model Rules / January 2026 side-by-side package
- Big4 Roadmaps: Deloitte "Roadmap: Business Combinations" / EY "International GAAP" / KPMG "Insights into IFRS" / PwC "Manual of Accounting"

---



