---
name: output_modes
description: スキルが対応する近接タスク (pricing / unit economics / cap table / M&A exit / DCF / burn-runway 等) の use case ごとの sheet bundle 定義正本。フル 14 sheet を一律生成するのではなく、ユーザー intent に応じて必要 sheet のみ生成する flexibility 設計。15_input_schema の output_mode field と SKILL.md dispatch table への statement
type: reference
priority: P0
related: [SKILL.md, 15_input_schema, _master_decision_tree, 18_customer_value_and_pricing, 19_ma_exit_for_founders, 22_driver_based_modeling, 23_sensitivity_and_implications]
---

# Output Modes (Use Case 別 Sheet Bundle 正本)

このドキュメントは startup-financial-modeling skill の **「フル 14 sheet を一律生成するのではなく、ユーザー intent に応じて必要 sheet だけ生成する」flexibility** を司る canonical reference。

> 本 file が対象とするのは「**何 sheet を生成するか**」(scope decision) のみ。「**何を計算するか**」(formula) は `06_three_statement.md` 等個別 reference を、「**どの順で読むか**」(routing) は `_master_decision_tree.md` を、「**用語の正本**」は `_terminology.md` を引く。

## 0. 位置づけと前提

### 0.1 SSoT chain

```
ユーザー prompt
   ↓ intent 抽出
SKILL.md dispatch table (intent → mode)        ← 本 file §5, §8 で拡張
   ↓
15_input_schema.md output_mode field           ← 本 file §4 で field 定義 patch
   ↓
本 file §2 / §3 (mode → sheet bundle 正本)
   ↓
build_orchestrator (scripts/, 将来)             ← 本 file §6 で擬似コード
   ↓
xlsx + IC memo (subset)
```

### 0.2 用語

| 用語 (原語) | 略 | 意味 |
|---|---|---|
| Output mode | mode | 「Pricing」「Cap table only」など use case ラベル。enum 値 |
| Sheet bundle | bundle | mode が canonical 化する sheet の集合 |
| Base bundle | — | mode が定義する default の sheet 集合 |
| Additional sheets | additional | base bundle に追加する sheet |
| Excluded sheets | excluded | base bundle から除外する sheet |
| Deliverable | — | 成果物形式 (xlsx_only / xlsx_with_memo / memo_only / json_only) |
| Full mode | full | 全 14 sheet を生成する mode (default) |
| Subset mode | — | full 以外、base bundle が full の真部分集合 |
| Use case | UC | ユーザーの典型タスク (pricing thesis / cap table / M&A exit 等) |
| Intent routing | — | prompt → mode の自動推定 |

### 0.3 14 Sheet Layout (Stage A 後 canonical)

本 file は **新 14 sheet layout** を canonical 正本として参照する。Stage A code refactor (`aa13f28b`) 完了前後を問わず、本 file の sheet 番号は新 layout で記述する。

| # | Sheet 名 | 役割 |
|---|---|---|
| 00 | `00_Cover` | モデル概要、生成日、対象 entity、output_mode 表示 |
| 01 | `01_Assumptions` | ハードインプット (`#0000FF`)、driver、業態 metric |
| 02 | `02_Revenue` | 収益モデル (driver-based)、segment 別 |
| 03 | `03_OpEx` | 費用モデル (固定 / 変動 / SBC)、headcount |
| 04 | `04_IS` | 損益計算書 (Income Statement) |
| 05 | `05_BS` | 貸借対照表 (Balance Sheet)、Working Capital Schedule (旧 08_WC は 05_BS の sub-section に統合) |
| 06 | `06_CFS` | キャッシュフロー計算書 |
| 07 | `07_Debt` | 借入スケジュール、covenant |
| 08 | `08_CapTable` | 資本政策、SAFE 転換、dilution waterfall |
| 09 | `09_DCF` | DCF バリュエーション、Sensitivity 内蔵 (旧 13_Sensitivity を 09 に統合) |
| 10 | `10_Comps` | 比較分析、football field |
| 11 | `11_KPI_Dashboard` | KPI 可視化、業態 benchmark |
| 12 | `12_SanityChecks` | 整合性監査、三表突合 |
| 13 | `13_IC_Memo` | 投資判断サマリ、thesis、kill criteria |

> 旧 17 sheet (`02_Drivers`, `08_WC`, `13_Sensitivity` 独立) との対応は §11 (Migration) を参照。

### 0.4 関連 reference との分担

| reference | 担当 | 本 file との関係 |
|---|---|---|
| `SKILL.md` | dispatch table、orchestration | §5 で mode 列追加 patch |
| `15_input_schema.md` | input field 仕様 | §4 で `output_mode` 等 field 追加 patch |
| `_master_decision_tree.md` | reference 横断の routing | §B/§C 4 段ゲートは full 前提、subset では skip 可能 check を §12 で documented |
| `_self_review_protocol.md` | 10 check 監査 | §8 で mode 別 self-review variant (例: pricing で BS check skip) を §12 で記述 |
| `_terminology.md` | 用語正本 | 本 file は用語を再定義しない、参照のみ |
| `18_customer_value_and_pricing` | pricing 計算 | `pricing` mode が引く primary reference |
| `19_ma_exit_for_founders` | M&A 計算 | `ma_exit` mode が引く primary reference |
| `22_driver_based_modeling` | driver model | `unit_economics`, `pricing` mode で必須 |
| `23_sensitivity_and_implications` | 感度分析 | `dcf_only`, `pricing` mode で 09_DCF 内 sub-section |

---

## §1. 設計原則 — 「用途に応じた最小 sheet 構成」

### §1.1 何故 subset bundle が必要か

このスキルが当初想定したのは **Series A+ fundraising / IC memo 全体像** が必要なケースで、その用途では「フル 14 sheet」が defensibility を担保する。しかし実際にユーザーが投げる prompt は近接領域に広がっており、**フル 14 sheet を一律生成すると 3 つの害がある**:

1. **Build 時間の浪費** — pricing thesis は revenue + DCF + KPI 5 sheet で完結するのに、BS / CFS / Debt まで生成すると 3-4 倍の build 時間と LLM token を消費する
2. **Cognitive load の増加** — ユーザーは pricing 議論をしたいのに 14 sheet を渡されると「どれを見れば良いか」分からない。Subset 構成なら「この 5 sheet を順に見れば結論」と明示できる
3. **Misuse / 誤解の温床** — pricing analysis に空欄 BS が並ぶと、ユーザーは「BS 設計に問題がある」と誤認しがち。本来は「BS は対象外」だが、生成された以上は audit 対象になる

### §1.2 「Relevant minimum」の 3 利得

本 file が canonical 化する **「relevant minimum bundle」** は以下を達成する:

| 利得 | full (14 sheet) | subset (例: pricing 7 sheet) |
|---|---|---|
| Build 時間 | 約 30 sec (orchestrator 実装後想定) | 約 8 sec |
| LLM token (manual build 時) | 約 100K tokens | 約 35K tokens |
| Self-review check 数 (`_self_review_protocol §8`) | 10 全実行 | 5-7 (mode 関連のみ) |
| User review 負担 | 14 sheet 通読 | 5-7 sheet で結論到達 |
| Misuse 余地 | 高 (空欄 sheet が誤読を招く) | 低 (生成されないので誤解しない) |
| Defensibility (full audit 耐性) | 最大 | mode 範囲内でのみ最大 |

### §1.3 設計三原則

#### §1.3.1 原則 A: Mode は use case を canonical 化する

「pricing thesis を作って」という prompt に対し、毎回異なる sheet 構成が出るのは **再現性の欠如**。本 file が `pricing` mode = `[00, 01, 02, 03, 09, 11, 13]` と canonical 化することで、誰が prompt しても同じ sheet 構成になる。

#### §1.3.2 原則 B: Mode は明示できる、推定もできる

ユーザーが `output_mode: "pricing"` と明示すればそれに従う (deterministic)。明示が無い場合、SKILL.md dispatch table と本 file §8 の routing rule で intent から自動推定する (heuristic)。**自動推定が外れた場合、ユーザーは追従プロンプトで mode を override 可能** にする。

#### §1.3.3 原則 C: Mode は 14 sheet の subset であり、新 sheet を作らない

本 file が canonical 化する 10 mode は **すべて新 14 sheet layout の subset / 組合せ**。Mode 専用の新 sheet (例: `99_PricingDeepDive`) は作らない。Mode は単に「14 sheet のうちどれを生成するか」を決める selector にすぎない。これにより:
- 計算ロジック (06_three_statement 等) は mode 数に関わらず一定
- Mode 追加が低コスト (新 sheet 設計不要)
- Audit / regression test が 14 sheet 単位で済む

### §1.4 Mode が「禁止」する誤解

| 誤解 | 正しい理解 |
|---|---|
| 「pricing mode は pricing sheet が増える」 | No、**14 sheet の subset を選択するだけ**。新 sheet は増えない |
| 「subset mode は full mode の劣化版」 | No、**use case に最適化された**構成。pricing thesis に BS は不要、それは劣化ではなく適合 |
| 「mode を変えれば計算結果も変わる」 | No、**同じ input なら同じ数値**。mode は出力 scope を制御するだけ、計算は不変 |
| 「subset では self-review を skip して良い」 | No、**mode 範囲内の self-review check は全実行**必須 (§12 で list) |
| 「mode は user-only 概念で内部 build には影響しない」 | No、build_orchestrator が mode を読み sheet 生成を分岐する。**internal 第一級概念** |

### §1.5 Mode と Mode の輪郭

Mode 同士の関係 (§2.3 で詳述) の概要:
- **包含関係 (subset)**: `unit_economics` ⊂ `pricing` ⊂ `full`
- **直交 (orthogonal)**: `cap_table` ⊥ `dcf_only` (両者は重なる sheet が少ない)
- **合成 (composition)**: `ma_exit` ≈ `cap_table` ∪ `dcf_only` + IC memo の M&A section
- **退化 (degenerate)**: `comps_only`, `market_sizing` は full の極小 subset

### §1.6 「常に full でも構わない」のはどんな場合か

- ユーザーが「**Series A 評価額の defensibility 全部**」を求める時
- VC IC memo として review board に提出される時
- IPO 準備で監査法人 / S-1 prep の元データになる時
- ユーザーが mode を明示せず、prompt から intent が読み取れない時 (default = full)

逆に **mode が明示された / 強い signal がある場合は subset を選ぶべき**:
- 「Pricing だけ」「Cap table だけ」「DCF だけ」と user が明示
- prompt が pricing 用語 (WTP / value-based pricing / 値上げ余地) のみで構成され、3 表 / cap table の言及が無い
- 既に full mode の build が存在し、pricing thesis 部分だけ更新したい (差分 build)

### §1.7 設計上の trade-off

| trade-off | 採用判断 |
|---|---|
| Mode の数を増やす vs UI complexity | 10 mode で打ち止め (§2.1)。それ以上は `additional_sheets` で組み合わせ |
| Mode を class hierarchy にする vs flat enum | flat enum で実装シンプル。包含関係は §2.3 で document |
| Mode default を `full` vs `auto-detect` | `full` を default、auto-detect は SKILL.md dispatch で intent 推定 (一段上の layer) |
| Mode を input_schema field にする vs CLI flag | input_schema field (§4)、build_orchestrator 引数として一元化 |

---

## §2. Output Mode Taxonomy

本章は本 file の中核。10 の canonical mode を定義し、それぞれの use case と sheet bundle を表にまとめる。

### §2.1 Mode 一覧 (10 mode)

| Mode (enum) | Use Case | Sheet bundle (新 14 sheet 番号) | 推定 build 時間 | Rationale |
|---|---|---|---|---|
| **`full`** | Series A+ fundraising / IPO prep / IC memo 全体 / 監査法人 review | `00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13` (全 14) | ~30 sec | full defensibility、IC board 提出可能水準 |
| **`pricing`** | Pricing thesis / WTP / value-based pricing / 値上げ余地分析 | `00, 01, 02, 03, 09 (Sensitivity 内蔵), 11, 13 (Pricing Thesis section)` (7 sheet) | ~8 sec | DCF まで含めて pricing が valuation に与える影響を示す |
| **`unit_economics`** | LTV/CAC / CAC payback / Magic Number / Cohort 分析 | `00, 01, 02, 03, 11, 12` (6 sheet) | ~5 sec | metric ベース、BS / CF / Cap Table 不要 |
| **`cap_table`** | SAFE 転換 / J-KISS post-money cap / dilution waterfall / founder-net | `00, 01, 08, 11, 13` (5 sheet) | ~5 sec | equity structure のみ、3 表不要 |
| **`ma_exit`** | M&A exit modeling / 株式交換 / earn-out / lock-up / liquidation pref | `00, 01, 08, 09 (Sensitivity 内蔵), 10, 13 (M&A Exit Thesis section)` (6 sheet) | ~10 sec | exit valuation + cap table waterfall + comps cross-check |
| **`dcf_only`** | Pure DCF valuation / WACC sensitivity / terminal value 議論 | `00, 01, 02, 09 (Sensitivity 内蔵), 10` (5 sheet) | ~6 sec | revenue → DCF → multiple cross-check の最小 path |
| **`burn_runway`** | Cash runway / monthly burn / breakeven path / 資金不足月 | `00, 01, 02, 03, 04, 06, 11` (7 sheet) | ~8 sec | cash trajectory のみ、equity / valuation 不要 |
| **`three_statement`** | 三表統合 audit / sanity check / 監査法人渡し | `00, 01, 02, 03, 04, 05, 06, 07, 12` (9 sheet) | ~15 sec | 三表突合 + debt + sanity、valuation 抜き |
| **`market_sizing`** | TAM / SAM / SOM / 市場浸透率 / 市場成長率 | `00, 01, 02 (sub: market sizing), 11` (4 sheet) | ~4 sec | 09_market_sizing 内容を Revenue 内 sub-section で展開 |
| **`comps_only`** | Public comps / private deal benchmark / EV/Revenue multiple | `00, 01, 10, 11` (4 sheet) | ~4 sec | benchmark + comps の最小構成、自社 financials は最小限 |

### §2.2 Bundle override / extension の declarative 指定

各 mode の base bundle に対し、ユーザーは `additional_sheets` / `excluded_sheets` で override できる。

#### §2.2.1 Additional (追加) パターン

```yaml
output_mode: "pricing"
additional_sheets: ["12_SanityChecks"]
# → pricing base 7 sheet + 12_SanityChecks = 8 sheet
```

典型用途:
- pricing analysis に sanity check を強化したい
- unit_economics に CapTable を加えて hire ramp を resource 制約で見たい
- dcf_only に IS を加えて EBITDA bridge を見たい

#### §2.2.2 Excluded (除外) パターン

```yaml
output_mode: "full"
excluded_sheets: ["07_Debt"]
# → full 14 sheet − 07_Debt = 13 sheet
```

典型用途 (rare、特殊ケース):
- full 想定だが debt を組まない pure equity startup
- IPO prep で comps を別資料管理しているため 10_Comps を本ファイルから外す
- 業態特殊 (Bio で IS だけ多 phase 出力したい等) で本来 mode に無い形に近づけたい

> **Anti-pattern 警告**: `additional_sheets` / `excluded_sheets` を多用して mode の base bundle と全く異なる構成にするのは、**mode 選択ミスの signal**。例えば `cap_table` に 6 sheet 追加して 11 sheet にするくらいなら `full` を選んで `excluded_sheets` で 3 sheet 削るほうが意図が明確 (§10.5 参照)。

#### §2.2.3 Mode 未指定時の default

```yaml
# output_mode 指定なし
output_mode: "full"  # ← implicit default
```

input_schema で `output_mode` が unset の場合 **default = `full`**。これは backward compatibility (Phase 6 以前のモデル) を保つ意図 (§11)。

#### §2.2.4 Deliverable field との組合せ

`deliverable` field (§4) は xlsx 生成可否 / IC memo 同梱可否を制御する:

| deliverable | xlsx | IC memo (.md) | json | 用途 |
|---|---|---|---|---|
| `xlsx_with_memo` (default) | ✓ | ✓ | ✗ | 標準 |
| `xlsx_only` | ✓ | ✗ | ✗ | xlsx 単体 |
| `memo_only` | ✗ | ✓ | ✗ | 短い IC memo / 議事録向け |
| `json_only` | ✗ | ✗ | ✓ | API 連携 / downstream 用 |

mode と deliverable は直交。例: `output_mode: "pricing", deliverable: "memo_only"` で「pricing thesis の IC memo だけ、xlsx 不要」が可能。

### §2.3 Mode 間の関係 (集合論的整理)

#### §2.3.1 包含関係

```
full ⊇ pricing ⊇ unit_economics
```

- **`unit_economics` (6 sheet)** = `[00, 01, 02, 03, 11, 12]`
- **`pricing` (7 sheet)** = unit_economics + `[09, 13]` − `[12]` = `[00, 01, 02, 03, 09, 11, 13]`
- **`full` (14 sheet)** ⊇ pricing ∪ {`04, 05, 06, 07, 08, 10, 12`}

> 厳密には `pricing` から `12` が抜け、`13` が加わる差し替えがあるため真部分集合ではない。意味的包含 (use case の包含) として扱う。

#### §2.3.2 直交 (orthogonal) ペア

| Mode A | Mode B | 共通 sheet | Rationale |
|---|---|---|---|
| `cap_table` | `dcf_only` | `00, 01` のみ | 一方は equity structure、他方は valuation。重なりは Cover / Assumptions だけ |
| `cap_table` | `burn_runway` | `00, 01` のみ | 一方は equity、他方は cash trajectory |
| `comps_only` | `three_statement` | `00, 01` のみ | 一方は benchmark、他方は社内三表 |

#### §2.3.3 合成 (composition)

| 合成 mode | 構成要素 |
|---|---|
| `ma_exit` | `cap_table` ∪ `dcf_only` + 13_IC_Memo の M&A Exit Thesis section |
| `full` | 全 mode の union (近似)、加えて 04-07 三表完備 |

#### §2.3.4 退化 (degenerate / 極小)

| Mode | sheet 数 | 退化理由 |
|---|---|---|
| `comps_only` | 4 | 自社財務は最小限、外部 benchmark 中心 |
| `market_sizing` | 4 | 市場側数字のみ、損益詳細は scope 外 |
| `cap_table` | 5 | equity 機構のみ |
| `dcf_only` | 5 | valuation のみ |

### §2.4 Mode 選択 decision matrix

ユーザー prompt から mode を選ぶときの決定木:

```
Q1: prompt に「全体」「fundraising」「IC memo」「IPO」等の signal あり?
├── Yes → full
└── No →
    Q2: pricing / WTP / value-based の signal あり?
    ├── Yes → pricing
    └── No →
        Q3: cap table / SAFE / dilution の signal あり?
        ├── Yes →
        │   Q3a: exit / M&A の signal も併記?
        │   ├── Yes → ma_exit
        │   └── No  → cap_table
        └── No →
            Q4: DCF / valuation 単体 の signal?
            ├── Yes → dcf_only
            └── No →
                Q5: runway / burn / cash の signal?
                ├── Yes → burn_runway
                └── No →
                    Q6: 三表 / sanity / audit の signal?
                    ├── Yes → three_statement
                    └── No →
                        Q7: TAM / SAM / SOM / market 規模 の signal?
                        ├── Yes → market_sizing
                        └── No →
                            Q8: comps / benchmark / 比較 の signal?
                            ├── Yes → comps_only
                            └── No →
                                Q9: LTV / CAC / unit economics の signal?
                                ├── Yes → unit_economics
                                └── No  → full (fallback)
```

### §2.5 Mode 一覧の完全性 (closure check)

10 mode が以下を漏れなく cover することを確認:

| 業務領域 | Cover する mode |
|---|---|
| Fundraising 全体 | `full` |
| Pricing & 顧客価値 | `pricing`, `unit_economics` |
| 資本政策 | `cap_table`, `ma_exit` |
| Valuation | `dcf_only`, `comps_only`, `ma_exit`, `full` |
| Cash 管理 | `burn_runway` |
| Audit / Sanity | `three_statement`, `full` |
| Market 分析 | `market_sizing` |
| Benchmarking | `comps_only` |
| Metric 監視 | `unit_economics`, `full` |

> 漏れがあった場合は新 mode を追加するのではなく、既存 mode の `additional_sheets` で対応する設計 (§1.3.3 原則 C)。

---

## §4. Input Schema Extension (`15_input_schema.md` への patch)

本章は `15_input_schema.md` (現行 2,837 行) に追加すべき field を定義する。Patch 適用先は `15_input_schema §4 共通 input` の末尾、または新 section `§4.6 Output Mode` として独立させる。

### §4.1 追加 field 一覧

| Field 名 | Type | Default | 必須 | 説明 |
|---|---|---|---|---|
| `output_mode` | enum (10 値) | `full` | No | Use case 別の sheet bundle 選択 |
| `additional_sheets` | list[string] | `[]` | No | Mode の base bundle に追加する sheet |
| `excluded_sheets` | list[string] | `[]` | No | Mode の base bundle から除外する sheet (rare) |
| `deliverable` | enum (4 値) | `xlsx_with_memo` | No | 成果物形式 |

### §4.2 YAML schema (canonical)

```yaml
# 15_input_schema.md §4.6 Output Mode に追加

output_mode:
  type: enum
  values:
    - full           # 全 14 sheet (default)
    - pricing        # Pricing thesis (7 sheet)
    - unit_economics # LTV/CAC / Magic Number (6 sheet)
    - cap_table      # SAFE / dilution (5 sheet)
    - ma_exit        # M&A exit (6 sheet)
    - dcf_only       # Pure DCF valuation (5 sheet)
    - burn_runway    # Cash runway / burn (7 sheet)
    - three_statement # 三表 audit (9 sheet)
    - market_sizing  # TAM/SAM/SOM (4 sheet)
    - comps_only     # Comps benchmark (4 sheet)
  default: full
  description: |
    Use case 別の sheet bundle 選択。`full` は全 14 sheet。
    それ以外は subset で、対応する use case の最小構成。
    詳細は `_output_modes.md §2.1` を参照。

additional_sheets:
  type: list[string]
  values: # 14 sheet の名前のいずれか
    - "00_Cover"
    - "01_Assumptions"
    - "02_Revenue"
    - "03_OpEx"
    - "04_IS"
    - "05_BS"
    - "06_CFS"
    - "07_Debt"
    - "08_CapTable"
    - "09_DCF"
    - "10_Comps"
    - "11_KPI_Dashboard"
    - "12_SanityChecks"
    - "13_IC_Memo"
  default: []
  description: |
    Mode の base bundle に追加する sheet 名 list。
    例: `output_mode: "pricing", additional_sheets: ["12_SanityChecks"]`
    で pricing 7 sheet + sanity = 8 sheet。
    base bundle に既に含まれる sheet は重複指定しても idempotent。

excluded_sheets:
  type: list[string]
  values: # 14 sheet の名前のいずれか
    - "00_Cover"      # ※ excluded 不可、§10.3 参照
    - "01_Assumptions"
    - "02_Revenue"
    - "03_OpEx"
    - "04_IS"
    - "05_BS"
    - "06_CFS"
    - "07_Debt"
    - "08_CapTable"
    - "09_DCF"
    - "10_Comps"
    - "11_KPI_Dashboard"
    - "12_SanityChecks"
    - "13_IC_Memo"
  default: []
  description: |
    Mode の base bundle から除外する sheet 名 (rare、特殊ケース)。
    例: `output_mode: "full", excluded_sheets: ["07_Debt"]` で pure equity startup。
    `00_Cover` は除外不可 (validation rule §4.4 で禁止)。
    `additional_sheets` と同時指定された sheet は excluded が優先。

deliverable:
  type: enum
  values:
    - xlsx_with_memo  # default、xlsx + IC memo (.md)
    - xlsx_only       # xlsx 単体
    - memo_only       # IC memo のみ、xlsx 不要 (短文用)
    - json_only       # JSON 出力のみ (API 連携)
  default: xlsx_with_memo
  description: |
    成果物形式。`memo_only` は xlsx 不要 (短い分析メモのみ)。
    `json_only` は downstream system 連携用、build_orchestrator が
    機械可読な構造化 JSON を返す。
```

### §4.3 JSON Schema 形式 (build_orchestrator 用)

```json
{
  "type": "object",
  "properties": {
    "output_mode": {
      "type": "string",
      "enum": ["full", "pricing", "unit_economics", "cap_table", "ma_exit",
               "dcf_only", "burn_runway", "three_statement", "market_sizing",
               "comps_only"],
      "default": "full"
    },
    "additional_sheets": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["00_Cover", "01_Assumptions", "02_Revenue", "03_OpEx",
                 "04_IS", "05_BS", "06_CFS", "07_Debt", "08_CapTable",
                 "09_DCF", "10_Comps", "11_KPI_Dashboard", "12_SanityChecks",
                 "13_IC_Memo"]
      },
      "default": []
    },
    "excluded_sheets": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["01_Assumptions", "02_Revenue", "03_OpEx",
                 "04_IS", "05_BS", "06_CFS", "07_Debt", "08_CapTable",
                 "09_DCF", "10_Comps", "11_KPI_Dashboard", "12_SanityChecks",
                 "13_IC_Memo"]
      },
      "default": []
    },
    "deliverable": {
      "type": "string",
      "enum": ["xlsx_with_memo", "xlsx_only", "memo_only", "json_only"],
      "default": "xlsx_with_memo"
    }
  }
}
```

### §4.4 Validation rules

#### §4.4.1 Hard validation (build 失敗 → エラー)

| Rule | 違反例 | エラーメッセージ |
|---|---|---|
| `output_mode` は enum 10 値のいずれか | `output_mode: "pricing_v2"` | `Unknown output_mode: pricing_v2. Valid values: full, pricing, ...` |
| `additional_sheets` の各要素は 14 sheet のいずれか | `["99_NewSheet"]` | `Unknown sheet: 99_NewSheet. Sheets are 00_Cover...13_IC_Memo` |
| `excluded_sheets` も同上、加えて `00_Cover` は除外不可 | `["00_Cover"]` | `Cannot exclude 00_Cover (always required, see _output_modes §10.3)` |
| `deliverable` は enum 4 値のいずれか | `deliverable: "pdf"` | `Unknown deliverable: pdf. Valid: xlsx_with_memo, xlsx_only, memo_only, json_only` |
| `memo_only` 時に `13_IC_Memo` が bundle に含まれない | `output_mode: "comps_only", deliverable: "memo_only"` | `memo_only deliverable requires 13_IC_Memo in final bundle. Add via additional_sheets or change mode.` |

#### §4.4.2 Soft validation (warning のみ、build は継続)

| Rule | 警告例 | メッセージ |
|---|---|---|
| `additional_sheets` で 5 個以上追加 | pricing + 5 sheet = 12 sheet | `WARN: 5+ additional sheets — consider using 'full' mode instead` |
| `excluded_sheets` で 4 個以上除外 | full − 4 sheet = 10 sheet | `WARN: 4+ excluded sheets — base bundle deviation high` |
| `additional_sheets` ∩ `excluded_sheets` ≠ ∅ | both `["12_SanityChecks"]` | `WARN: 12_SanityChecks is both added and excluded; excluded wins` |
| Mode と deliverable 不整合 (例: three_statement + memo_only) | three_statement は 13_IC_Memo を bundle に持たない | `WARN: three_statement default has no 13_IC_Memo. memo_only requires it; auto-adding.` |

#### §4.4.3 Auto-correction rules

build_orchestrator は以下を自動補正する (warning は出すが build 継続):

1. **`memo_only` + 13_IC_Memo 不在** → `13_IC_Memo` を additional_sheets に自動追加
2. **`xlsx_only` + bundle 内に 13_IC_Memo あり** → IC memo (.md) は出力しない (xlsx 内 sheet として残る)
3. **mode 未指定** → `full` を assign、warning 不要
4. **`json_only`** → 全 mode で xlsx も memo も生成しない、JSON のみ

### §4.5 Patch 適用箇所 (`15_input_schema.md` へ)

具体的に `15_input_schema.md` のどこに patch を適用するか:

| 場所 | 内容 |
|---|---|
| §4 共通 input の末尾 | 新 sub-section §4.6「Output Mode」として §4.1-§4.4 全体を追加 |
| §10 Schema 完全形 (YAML / JSON Schema / Pydantic) | 既存 schema に `output_mode`, `additional_sheets`, `excluded_sheets`, `deliverable` を追加 (Pydantic は `OutputMode(str, Enum)` 等) |
| §11 Routing 表 | 「output_mode → 必読 reference」列を追加 (例: `pricing → 18_customer_value, 23_sensitivity`) |
| §13 Example Input Sets | 各 mode の minimal input example を 1 個ずつ追加 (10 例) |
| §14 Build_model.py 統合手順 | mode 分岐の擬似コード (本 file §6 と整合) |

### §4.6 Backward compatibility

既存 input (output_mode 未指定) は **default = `full`** が assign され、Phase 6 以前と同じ挙動。Migration 不要。

### §4.7 Field 命名の rationale

| 候補 | 採用 / 不採用 | 理由 |
|---|---|---|
| `output_mode` | **採用** | use case 「Pricing」「Cap table」を「mode」と表現するのが直感的 |
| `output_type` | 不採用 | type は `xlsx_only` 等の deliverable と紛らわしい |
| `bundle` | 不採用 | 内部用語、user-facing にしない |
| `scope` | 不採用 | 業務スコープと誤読される |
| `sheets` | 不採用 | sheet 名直接指定なら mode の意味なし |
| `additional_sheets` | **採用** | mode に対する additive override が直感的 |
| `extra_sheets` | 不採用 | "extra" は重要度低を示唆、ニュアンス違い |
| `excluded_sheets` | **採用** | excluded は明確な「除外」 |
| `dropped_sheets` | 不採用 | drop は process 中の脱落を示唆 |
| `deliverable` | **採用** | 「成果物」を一語で表す業界標準語 |
| `output_format` | 不採用 | format は内部表現 (xlsx vs xlsx) と紛らわしい |

---

## §5. SKILL.md Dispatch Table 拡張

本章は `SKILL.md` の既存 dispatch table (現行 §「Reference Dispatch Table」) に **「Mode」列を追加** するための patch 仕様。

### §5.1 拡張後の dispatch table (canonical)

`SKILL.md §Reference Dispatch Table` に新列「Mode」を加え、以下の table に置き換える:

| ユーザー発話の例 | Mode | 第 1 reference (sub-section anchor) | 補完 reference |
|---|---|---|---|
| "Series A 評価額を defensibility 込みで" | `full` | `_master_decision_tree.md §B` | `05 §1.6.3, §21.1, §22, §23` |
| "Series A/B fundraising モデル一式" | `full` | `_master_decision_tree.md §A` | `04a §6, 04b §3, 05 §10` |
| "IPO 準備のフルモデル" | `full` | `14_ipo_readiness.md` | `01a §3.2, 13b` |
| "IC memo + 三表 + 感度" | `full` | `08 §17.1` | `06 §12, 23` |
| "Pricing thesis / WTP / 顧客 ROI / value-based pricing" | `pricing` | `18_customer_value_and_pricing.md §3, §4` | `02 §6 (LTV/CAC), 16, 23 (sensitivity)` |
| "値上げ余地を WTP boundary で" | `pricing` | `18 §4.1 (gainsharing 0.20-0.30)` | `_self_review_protocol §8.7` |
| "Customer ROI quantify して price ceiling" | `pricing` | `18 §3.1` | `09_DCF, 23` |
| "LTV/CAC / unit economics review" | `unit_economics` | `02_saas_metrics.md` | `_terminology §6.1, 22` |
| "CAC payback / Magic Number" | `unit_economics` | `_terminology §6.1, §6.3` | `02 §5.1` |
| "Cohort retention curve" | `unit_economics` | `02 §5.2` | `22` |
| "Cap table simulation / SAFE 転換" | `cap_table` | `04a §2 (SAFE), §19.1, §19.2` | `04b §12.1-12.4, 19_ma §6` |
| "J-KISS post-money cap で converted shares" | `cap_table` | `07 §3.1-3.3` | `04a §3.4, _terminology §5` |
| "Founder ownership が exit でどうなるか" | `cap_table` | `04b §10` | `19_ma §6` |
| "M&A exit / 株式交換 / earn-out / lock-up" | `ma_exit` | `19_ma_exit_for_founders.md §6, §11` | `04b §10, 12_tax, 08` |
| "Strategic acquirer vs financial buyer" | `ma_exit` | `19 §3` | `08 §6.4, 19 §11` |
| "Liquidation preference + earn-out 込み founder net" | `ma_exit` | `19 §6` | `04b §10, 12_tax` |
| "DCF だけ作って" | `dcf_only` | `05_valuation_wacc.md §1-§3` | `23 (sensitivity)` |
| "WACC sensitivity / terminal method 比較" | `dcf_only` | `05 §1.6.3, §21.1` | `_terminology §6, 23` |
| "Pure DCF / 3 表は他で" | `dcf_only` | `05 §1` | `22 (revenue ramp)` |
| "Cash runway / burn 分析 / breakeven" | `burn_runway` | `02 §5 (Burn Multiple), 16` | `06 §5 (CFS)` |
| "Monthly cash flow / runway months" | `burn_runway` | `02 §5.1` | `_terminology §6.1` |
| "三表突合 / Sanity check / 監査法人渡し" | `three_statement` | `06 §12.1-§12.3` | `01b §6` |
| "BS が tie しない、audit して" | `three_statement` | `06 §12.1` | `01b §6, 12_SanityChecks sheet 仕様` |
| "Market sizing TAM/SAM/SOM" | `market_sizing` | `09_market_sizing.md` | `08 §7.4` |
| "市場サイズ + 浸透率" | `market_sizing` | `09 §1, §3` | `02 §1` |
| "Comps benchmark / public SaaS" | `comps_only` | `10_Comps` (sheet 仕様) | `05 §10` |
| "Peer 比較 EV/Revenue multiple" | `comps_only` | `05 §10.2` | `_terminology §6` |
| "WACC が g 以下になった" | `dcf_only` (or `full`) | `05 §21.1` | `_terminology §6` |
| "Down round / wind-down シナリオ" | `cap_table` (or `full`) | `10 §19.1, §19.2, §19.4, §19.7` | `_stress_framework §2` |
| "Tax 戦略 (M&A / Pillar 2)" | `ma_exit` (or `full`) | `12_tax_strategy.md` | `07 §2` |
| "Holdco / 連結 / Carve-out" | `full` | `13a_consolidation_core.md` | `13b_treasury_carveout.md` |
| "コスト構造 (固定/変動/SBC)" | `full` (or `unit_economics`) | `16_cost_structure.md` | `02 §5` |
| "業態別 unit economics" | `unit_economics` | `03_business_models.md` (該当業態 §) | (業態別 §) |
| "venture debt vs equity" | `full` | `_master_decision_tree §D` | `11 §1.1, §18.1-§18.6` |
| "業態 × stage で何を読むか" | `full` | `_master_decision_tree §E` | `15_input_schema §11.2` |
| "chart 設計 / waterfall / sensitivity heatmap" | `full` (chart は全 mode で利用可) | `17_chart_design.md` | `00_design_guidelines, 11 (Dashboard)` |

### §5.2 「Mode 推定不能 / 曖昧」 fallback policy

| ユーザー発話 | 推定 | 確認質問 (mode 確定前) |
|---|---|---|
| "財務モデルを作って" | `full` (default) | (確認なし、full で開始) |
| "モデル作って、急ぎ" | `full` (default) | (確認なし、full で開始) |
| "Pricing 関連で何かほしい" | `pricing` 候補だが曖昧 | 「pricing thesis (mode=pricing) ですか、unit economics 中心 (mode=unit_economics) ですか?」 |
| "Cap table と pricing 両方」 | mode 単体では cover 不可 | 「full mode ですか? もしくは cap_table を base に additional_sheets で pricing 用 sheet を加えますか?」 |
| "短く済ませたい、ARR と burn だけ」 | `burn_runway` 寄り | mode 確定後に build |

### §5.3 SSoT chain における mode の位置

```
ユーザー prompt
   ↓
[Layer 1] SKILL.md dispatch table → mode 推定
   ↓
[Layer 2] _output_modes §2 → mode → sheet bundle (canonical)
   ↓
[Layer 3] 15_input_schema §4.6 → field validation
   ↓
[Layer 4] _master_decision_tree §B/C → mode 範囲内の reference 順序
   ↓
[Layer 5] build_orchestrator (§6) → bundle に従い sheet 生成
   ↓
[Layer 6] _self_review_protocol §8 → mode 別 self-review
   ↓
xlsx + IC memo (subset)
```

### §5.4 Mode 列追加の SKILL.md patch サマリ

`SKILL.md` に必要な変更:

1. **§Reference Dispatch Table** の table に Mode 列を追加 (本 file §5.1 の table に置き換え)
2. **§基本ワークフロー** の Step 1「Mode 選択」を「Output mode 推定 + Build mode (Quick/Standard/Comprehensive)」に拡張
3. **§17 Sheet Layout** を **§14 Sheet Layout** に renumber、本 file §0.3 の table に統一
4. **§必須 Self-Review** の冒頭に「Mode に応じて check 項目を絞る (`_output_modes §12`)」を加える
5. **§関連 reference** に `_output_modes.md` を追加

---

## §7. Mode 別 Mini Cases

本章は 7 個の mini case を通じて、mode 選択 → input → output deliverable の一連を例示する。各 case は input YAML、生成 sheet、IC memo focus、self-review 結果の縮約を含む。

### §7.1 Case 1: 「Pricing analysis をして」 (mode = `pricing`)

#### §7.1.1 Context

SaaS startup、Series B、ARR ¥500M、NRR 110%、ターゲット顧客 50 社。CFO から「現行 pricing で WTP に対して取りこぼしが無いか defensible に」依頼。

#### §7.1.2 Input

```yaml
output_mode: "pricing"
deliverable: "xlsx_with_memo"

entity:
  name: "AlphaSaaS Inc."
  currency: JPY
  business_model: "SaaS"
  stage: "Series B"

revenue:
  arr_current_jpy: 500_000_000
  nrr_pct: 110
  customer_count: 50
  arpu_jpy: 10_000_000  # ARR / customer count
  segment: "Mid-market"

pricing:
  current_price_per_seat_jpy: 50_000
  wtp_ceiling_estimate_jpy: 75_000  # customer survey 値
  gainsharing_pct: 0.25  # _self_review §8.7 内
  customer_roi_estimate: 5.0  # 顧客 ROI 5x

dcf_inputs:
  wacc_pct: 11
  terminal_growth_pct: 2.5
```

#### §7.1.3 Output (7 sheet xlsx + IC memo)

| sheet | 主要内容 |
|---|---|
| `00_Cover` | "AlphaSaaS Pricing Thesis Model"、生成日、output_mode = pricing |
| `01_Assumptions` | ARPU ¥10M、WTP ceiling ¥15M (per seat ¥75K)、gainsharing 25% |
| `02_Revenue` | base / +20% price / +50% price の 3 scenario revenue |
| `03_OpEx` | gross margin 78% (SaaS standard)、S&M ramp |
| `09_DCF` | base case EV ¥4.5B、+20% price → EV ¥5.8B、+50% → EV ¥7.2B、Sensitivity (price × WACC) |
| `11_KPI_Dashboard` | LTV uplift +25%、payback 12 → 9 mo、Rule of 40 改善 |
| `13_IC_Memo` | Pricing Thesis 主軸、WTP boundary、Customer ROI、競合比較 |

#### §7.1.4 IC memo focus

- Pricing Thesis: 「WTP ¥75K に対し現行 ¥50K = 取りこぼし 33%、+20% 値上げが reasonable」
- WTP analysis: 顧客 ROI 5x の 25% (gainsharing 0.25) を vendor に取り、価格 ¥62.5K が defensible
- Customer ROI: payback period 24 → 19 mo に伸びるが、5x ROI 維持
- Competitive: 競合 X 社 ¥45K、Y 社 ¥55K、+20% で Y 社上回るが ROI で defensive

#### §7.1.5 実行時間 / Self-review

- Build 時間: 約 8 sec (full の 1/4)
- Self-review: 7 check (BS / CF / Debt 関連 3 check は skip、§12)
- gainsharing 0.25 が `[0.20, 0.30]` boundary 内 → check 7 PASS

### §7.2 Case 2: 「Cap table だけ」 (mode = `cap_table`)

#### §7.2.1 Context

US Delaware C-corp、founders 10M shares、Series A pre-money $20M、$5M raise、option pool 10% target post-round。Founder から「Series A 後の dilution waterfall を見たい」。

#### §7.2.2 Input

```yaml
output_mode: "cap_table"
deliverable: "xlsx_with_memo"

entity:
  name: "BetaTech Corp."
  currency: USD
  jurisdiction: "Delaware C-corp"

cap_table:
  founders:
    - name: "Founder A"
      shares: 6_000_000
    - name: "Founder B"
      shares: 4_000_000
  rounds:
    - name: "Pre-Seed"
      type: "SAFE"
      amount: 500_000
      valuation_cap: 5_000_000
      discount: 0.20
    - name: "Series A"
      type: "Equity"
      pre_money: 20_000_000
      round_size: 5_000_000
      option_pool_target_post: 0.10
```

#### §7.2.3 Output (5 sheet xlsx + IC memo)

| sheet | 主要内容 |
|---|---|
| `00_Cover` | "BetaTech Cap Table Simulation" |
| `01_Assumptions` | round event timeline、SAFE 条項 (cap $5M、disc 20%)、Series A pre-money $20M、option pool 10% |
| `08_CapTable` | Pre-Seed / Series A 別 cap table、SAFE 転換 (¥1.25M shares @ $4.0/share)、option pool refresh、dilution waterfall |
| `11_KPI_Dashboard` | Founder A ownership 60% → 39%、Founder B 40% → 26%、Series A investor 20%、option pool 10% |
| `13_IC_Memo` | Dilution Analysis 主軸、Founder-net at exit ($100M = $25M Founder A) |

#### §7.2.4 Self-review

- 5 check (3 表 / valuation / debt / sanity 5 check は skip)
- SAFE Discount 0.20 = 20% off (`_terminology §4` 通り)、PASS
- Series A pre-money + raise = post-money $25M、option pool 10% は post-money base、PASS

#### §7.2.5 実行時間: 約 5 sec

### §7.3 Case 3: 「Burn / Runway 分析」 (mode = `burn_runway`)

#### §7.3.1 Context

Pre-Seed SaaS、current cash $5M、monthly burn $400K (gross $500K − revenue $100K)、ARR ramp 想定。CEO から「runway をどう延ばせるか」。

#### §7.3.2 Input

```yaml
output_mode: "burn_runway"
deliverable: "xlsx_with_memo"

entity:
  name: "GammaApp Inc."
  currency: USD
  stage: "Pre-Seed"

cash:
  current_balance: 5_000_000
  monthly_gross_burn: 500_000
  monthly_revenue_current: 100_000

revenue:
  monthly_growth_pct: 15
  arpu: 1_000
  initial_customers: 100

opex:
  headcount_current: 12
  loaded_cost_per_head_monthly: 35_000
  saas_tooling_monthly: 30_000
  hire_plan: "+1 / month for 6 months, then hold"
```

#### §7.3.3 Output (7 sheet xlsx + IC memo)

| sheet | 主要内容 |
|---|---|
| `00_Cover` | "GammaApp Burn-Runway Model" |
| `01_Assumptions` | cash $5M、monthly burn、headcount ramp +1/mo |
| `02_Revenue` | monthly customer ramp、ARPU $1K、growth 15% MoM |
| `03_OpEx` | monthly headcount × $35K、SaaS tooling $30K |
| `04_IS` | monthly P&L、operating loss trend |
| `06_CFS` | monthly cumulative cash、breakeven month identifier |
| `11_KPI_Dashboard` | runway = 12.5 mo、breakeven = month 18 (但し cash 不足)、burn multiple 2.1x → 1.4x |

#### §7.3.4 IC memo focus

- Cash Trajectory: current $5M、12.5 mo runway @ current burn
- Breakeven: month 18 で monthly cash flow > 0、ただし cash は month 13 で枯渇
- Next Funding: month 9 までに Seed round 必要、target raise $3-5M
- Burn Multiple: current 2.1x (FAIL)、Y2 で 1.4x (WATCH) に改善見込

#### §7.3.5 Self-review

- 6 check (cap table / valuation / debt / IC memo §6-§10 は skip)
- Burn multiple ARR < $100K では undefined、実 ARR $1.2M なので適用可、PASS

#### §7.3.6 実行時間: 約 8 sec

### §7.4 Case 4: 「DCF だけ」 (mode = `dcf_only`)

#### §7.4.1 Context

Series C SaaS、Y5 ARR $300M projection、WACC 12%、g 3%、IPO target Y6。VC partner から「pure DCF で IPO valuation を defend」。

#### §7.4.2 Input

```yaml
output_mode: "dcf_only"
deliverable: "xlsx_with_memo"

entity:
  name: "DeltaSoft Inc."
  currency: USD
  stage: "Series C"

revenue:
  arr_y0: 50_000_000
  growth_curve: [0.80, 0.60, 0.50, 0.40, 0.30]  # Y1..Y5
  # → Y5 ARR = $50M × 1.8 × 1.6 × 1.5 × 1.4 × 1.3 ≈ $295M

dcf_inputs:
  wacc_pct: 12
  terminal_growth_pct: 3
  terminal_method: "gordon"
  exit_multiple_check: 8  # EV/Revenue
  tax_rate: 0.25
  fcf_margin_terminal: 0.30
```

#### §7.4.3 Output (5 sheet xlsx + IC memo summary in 09_DCF)

| sheet | 主要内容 |
|---|---|
| `00_Cover` | "DeltaSoft DCF Valuation" |
| `01_Assumptions` | WACC 12%、g 3%、tax 25%、FCF margin terminal 30% |
| `02_Revenue` | 5 year revenue projection (driver-based) |
| `09_DCF` | DCF table + Gordon TV $X、Exit Multiple TV $Y、Sensitivity (WACC 10/11/12/13/14% × g 2/3/4%)、DCF Summary |
| `10_Comps` | EV/Revenue 公開 SaaS comps median 8x、自社 implied check |

#### §7.4.4 DCF summary (09_DCF 上部)

- Base case EV: $1.8B (Gordon)、$2.4B (Exit Multiple)
- Sensitivity: WACC ±2% で EV ±25%、g ±1% で EV ±15%
- Terminal value 構成比: 78% (warning border、`05 §1.6.3`)
- Comps cross-check: 8x × Y5 $295M = $2.36B、Exit Multiple と一致

#### §7.4.5 Self-review

- 4 check (3 表 / cap table / 5 check skip)
- WACC 12% > g 3%、check 1 PASS (`05 §21.1`)
- Terminal value 78% < 85%、accept with rationale 不要

#### §7.4.6 実行時間: 約 6 sec

### §7.5 Case 5: 「M&A exit シナリオ」 (mode = `ma_exit`)

#### §7.5.1 Context

US strategic acquirer による株式交換、exit value $500M、founder 25%、liquidation preference 1x non-participating、earn-out $50M (Y1+Y2 ARR target に基づく、achievement probability 0.7)、lock-up 1 year。

#### §7.5.2 Input

```yaml
output_mode: "ma_exit"
deliverable: "xlsx_with_memo"

entity:
  name: "EpsilonAI Inc."
  currency: USD

cap_table:
  founders:
    - name: "Founder C"
      shares: 5_000_000
      ownership_pct: 25
  series_a_investor:
    shares: 4_000_000
    invested: 10_000_000
    liquidation_pref: "1x non-participating"
  series_b_investor:
    shares: 3_000_000
    invested: 30_000_000
    liquidation_pref: "1x non-participating"

ma_exit:
  exit_value: 500_000_000
  buyer_type: "strategic"
  consideration: "stock_50_cash_50"
  earn_out_amount: 50_000_000
  earn_out_probability: 0.7
  lock_up_months: 12
  lock_up_discount_annual_pct: 8
  founder_tax_rate: 0.20  # long-term capital gain
```

#### §7.5.3 Output (6 sheet xlsx + IC memo)

| sheet | 主要内容 |
|---|---|
| `00_Cover` | "EpsilonAI M&A Exit Model" |
| `01_Assumptions` | exit $500M、earn-out $50M @ 0.7、lock-up 12 mo |
| `08_CapTable` | exit 時 cap table、liquidation waterfall ($40M LP → 残 $460M を ownership 比 share) |
| `09_DCF` | DCF cross-check (exit valuation が DCF base case と整合か)、Sensitivity (exit value × probability) |
| `10_Comps` | M&A precedent transactions、median EV/Revenue 7-9x |
| `13_IC_Memo` | M&A Exit Thesis、likely buyers (Microsoft / Google / Salesforce)、founder net |

#### §7.5.4 Founder Net 計算

```
Exit value = $500M
- LP (Series A + B 合計): $40M
- 残: $460M
- Founder C share = 25% × $460M = $115M (liquidation pref 後の持分)
+ Earn-out (risk-adjusted): $50M × 25% × 0.7 = $8.75M
- Lock-up discount: $115M × 0.5 (stock 部分) × 8% × 1 yr = $4.6M
- Tax: ($115M + $8.75M − $4.6M) × 0.20 = $23.83M
= Founder Net (after-tax, lock-up adjusted): $95.32M
```

#### §7.5.5 IC memo focus

- Exit Thesis: strategic acquirer として Microsoft / Google / Salesforce が候補、AI capability synergy
- Likely buyers: 過去 5 年の AI startup acquisition precedent (~10 deals)、$300-700M range
- Founder Net (risk-adjusted): $95.3M、tax + lock-up 控除後
- Earn-out: ARR target Y1 $100M / Y2 $150M、achievement probability 0.7 ⇒ expected $35M

#### §7.5.6 Self-review

- 7 check (3 表 3 check skip)
- earn-out probability 0.7 < 1.0、risk-adjusted (`§3.5.6` 通り)、PASS
- founder net で tax 控除済 (`12_tax_strategy`)、PASS

#### §7.5.7 実行時間: 約 10 sec

### §7.6 Case 6: 「Unit economics review」 (mode = `unit_economics`)

#### §7.6.1 Context

PLG SaaS、LTV/CAC 3.5、CAC payback 14 mo、CFO から「LTV と CAC payback が悪化していないか」。

#### §7.6.2 Input

```yaml
output_mode: "unit_economics"
deliverable: "xlsx_with_memo"

entity:
  name: "ZetaPLG Inc."
  business_model: "SaaS - PLG"

unit_economics:
  arpu_annual: 12_000
  gross_margin_pct: 78
  cac_blended: 18_000
  cac_paid: 25_000
  cac_payback_mo: 14
  ltv_method: "cohort"  # _terminology §6.1
  ltv_amount: 63_000
  ltv_to_cac: 3.5
  nrr_pct: 115  # PLG benchmark > 110% PASS
  grr_pct: 92
  magic_number_quarterly: 0.85  # _terminology §6.3
```

#### §7.6.3 Output (6 sheet xlsx + IC memo summary in 11_KPI)

| sheet | 主要内容 |
|---|---|
| `00_Cover` | "ZetaPLG Unit Economics Review" |
| `01_Assumptions` | ARPU $12K、CAC $18K、gross margin 78%、cohort window 5 yr |
| `02_Revenue` | cohort revenue build、Y1-Y5 retention curve (PLG: Y1 90% → Y5 70%) |
| `03_OpEx` | S&M $2.5M、CAC = S&M / new customers |
| `11_KPI_Dashboard` | LTV/CAC 3.5 (PASS、>3x)、CAC payback 14 mo (WATCH、12-18 mo)、Magic Number 0.85 (WATCH、0.4-1.0) |
| `12_SanityChecks` | LTV ≤ ARPU × T 検算、payback ≤ T 検算、cohort math 検算 |

#### §7.6.4 KPI dashboard summary

- LTV (Method B cohort, T=5y): $63K
- CAC (blended): $18K → LTV/CAC = 3.5x (PASS)
- CAC payback: 14 mo (WATCH)
- NRR 115% (PLG PASS、>110%)、GRR 92% (PASS、>90%)
- Magic Number 0.85 (WATCH、healthy)

#### §7.6.5 Self-review

- 5 check (cap table / valuation / debt / IC memo §6-§10 5 check skip)
- LTV method = cohort (canonical、`_terminology §6.1`)、PASS
- Magic Number quarterly-annualized で計算、`_terminology §6.3` PASS

#### §7.6.6 実行時間: 約 5 sec

### §7.7 Case 7: 「Custom: pricing + sanity」 (mode = `pricing` + `additional_sheets`)

#### §7.7.1 Context

Case 1 と同じ AlphaSaaS だが、CFO から「pricing analysis に sanity check も入れて」追加要望。

#### §7.7.2 Input

```yaml
output_mode: "pricing"
additional_sheets: ["12_SanityChecks"]
deliverable: "xlsx_with_memo"

# (Case 1 と同じ entity / pricing / dcf input)
```

#### §7.7.3 Output (8 sheet xlsx + IC memo)

Case 1 の 7 sheet + `12_SanityChecks` = 8 sheet。

`12_SanityChecks` の内容:
- gainsharing_pct 0.25 が `[0.20, 0.30]` boundary 内 PASS
- WTP ceiling ¥75K > current price ¥50K PASS (取りこぼし余地確認)
- Customer ROI 5x > 業態 benchmark (B2B SaaS で 3-5x) PASS
- DCF base case EV ¥4.5B vs comps median (¥4.8B) で ±10% 内 PASS
- Sensitivity grid: WACC 10/11/12% × price +0/+20/+50% で EV all positive PASS

#### §7.7.4 Validation 動作

- input validation: `additional_sheets: ["12_SanityChecks"]` は valid sheet name、PASS
- bundle: pricing base 7 + additional 1 = 8、idempotent (12 が既に base にある場合は重複追加しない)
- soft validation: 1 sheet only addition、warning なし

#### §7.7.5 Self-review

- Case 1 の 7 check + 12_SanityChecks 関連 1 check = 8 check
- PASS rate 8/8

#### §7.7.6 実行時間: 約 9 sec (Case 1 + 1 sec)

---

## §8. Routing Rule (Intent → Mode 自動推定)

本章は **ユーザー prompt から mode を自動推定するための pattern matching rule** を canonical 化する。SKILL.md の orchestration layer (§5.1 dispatch table) と build_orchestrator (§6) を繋ぐ heuristic を本章に集約する。

### §8.1 Keyword → Mode mapping table

| Keyword (日本語 + 英語) | 推定 mode | confidence |
|---|---|---|
| "pricing", "WTP", "value-based", "willingness-to-pay", "値上げ余地", "価格戦略", "顧客ROI", "gainsharing" | `pricing` | High |
| "LTV", "CAC", "unit economics", "Magic Number", "cohort", "ARPU", "payback", "ユニットエコノミクス", "コホート" | `unit_economics` | High |
| "cap table", "SAFE", "dilution", "希薄化", "資本政策", "持株比率", "founder ownership" | `cap_table` | High |
| "exit", "M&A", "earn-out", "lock-up", "株式交換", "EXIT", "founder net", "liquidation pref" | `ma_exit` | High |
| "DCF", "valuation only", "WACC sensitivity", "terminal value", "Gordon model", "Exit Multiple" | `dcf_only` | High |
| "runway", "burn", "cash", "breakeven", "資金不足月", "ランウェイ", "バーン" | `burn_runway` | High |
| "三表", "sanity", "audit", "BS check", "CF tie", "三表突合", "監査法人", "整合性" | `three_statement` | High |
| "TAM", "SAM", "SOM", "market sizing", "市場サイズ", "市場規模", "浸透率" | `market_sizing` | High |
| "comps", "benchmark", "peer", "比較", "EV/Revenue", "multiple" | `comps_only` | High |
| "全体", "fundraising", "Series", "IC memo", "IPO prep", "IPO 準備", "投資判断", "model 全体" | `full` | High |

### §8.2 Multi-keyword 衝突時の優先順位

ユーザー prompt が複数 keyword を含む場合の優先順位:

```
priority 1 (highest): "exit", "M&A", "earn-out"   → ma_exit
priority 2:           "三表", "audit", "sanity"     → three_statement
priority 3:           "pricing", "WTP"               → pricing
priority 4:           "cap table", "SAFE"            → cap_table
priority 5:           "DCF", "valuation only"        → dcf_only
priority 6:           "runway", "burn"               → burn_runway
priority 7:           "LTV", "CAC"                   → unit_economics
priority 8:           "TAM", "SAM"                   → market_sizing
priority 9:           "comps", "benchmark"           → comps_only
priority 10:          "全体", "Series", "fundraising" → full
priority 11 (default): keyword 不在 / 弱 signal      → full
```

> Rationale: 上位 (ma_exit, three_statement) は専用 use case で誤推定が起きにくく、下位 (full) は default fallback。

### §8.3 Negation / 強い signal の処理

「pricing **だけ**」「DCF **のみ**」のような negation/exclusion signal は **subset mode を強く示唆**:

| 表現 | 推定 mode |
|---|---|
| "Pricing だけ" / "Pricing のみ" / "Pricing thesis only" | `pricing` (full への fallback 禁止) |
| "Cap table だけ" | `cap_table` |
| "DCF だけ" / "Pure DCF" | `dcf_only` |
| "三表だけ" | `three_statement` |
| "Comps だけ" | `comps_only` |

これらは weight 2x で priority 計算に反映する。

### §8.4 Auto-detect 不能 / Ambiguous の挙動

prompt が短すぎる、または keyword が無い場合:

| Input | 挙動 |
|---|---|
| "モデル作って" | `full` (default) |
| "Series A 評価額" | `full` (signal: Series, 評価額) |
| "教えて" / "見て" / 単独 | mode 推定不能、ユーザーに確認質問 |
| 質問が valuation 関連だが具体性なし | `full` で開始、後で subset に絞れる選択肢提示 |

ambiguous 時の確認質問テンプレ:
> "ご要望を確認させてください。以下のどれに近いですか?
>  - 全体的な財務モデル (full mode、14 sheet)
>  - Pricing thesis に絞る (pricing mode、7 sheet)
>  - Cap table 中心 (cap_table mode、5 sheet)
>  - その他 (mode 一覧から指定)"

### §8.5 Override hierarchy

mode 確定の優先順位 (上が勝つ):

1. **input_schema での明示** (`output_mode: "pricing"`) — 確定
2. **Negation signal** ("〜だけ") — auto-detect で subset を強く示唆
3. **Keyword priority §8.2** — 通常 auto-detect
4. **Default = `full`** — fallback

### §8.6 Mode 推定の audit trail

`build_orchestrator` は推定 trail を log に残す:

```
[INPUT] "Pricing thesis を作って"
[DETECT] keywords: ["pricing", "thesis"] → pricing (priority 3, confidence: high)
[NEGATION] not detected
[DECISION] mode = pricing
[BUNDLE] 7 sheets: 00, 01, 02, 03, 09, 11, 13
[BUILD] 8.2 sec
[REVIEW] 7/7 check pass
```

このログは IC memo の Cover sheet または audit log file (`logs/build_TIMESTAMP.log`) に保存する。

### §8.7 New keyword の追加手順

新 keyword が頻出する場合:
1. 本 file §8.1 の table に追加
2. SKILL.md dispatch table (§5.1) に対応行を追加
3. 必要なら §8.2 priority の見直し
4. test (`tests/test_intent_routing.py`) に新 keyword 例を追加

---

## §9. IC Memo Template の Mode 別 Variant

本章は `13_IC_Memo` sheet の content が mode によってどう変わるかを定義する。**同じ 13_IC_Memo sheet** でも、mode に応じて section 構成 / focus / 用語が切り替わる。

### §9.1 Mode 別 IC memo focus matrix

| Mode | IC Memo focus sections (in order) | 推定 page 数 |
|---|---|---|
| `full` | 1. Investment Thesis (full)、2. Market Sizing、3. Unit Economics、4. Valuation (DCF + Comps)、5. Cap Table、6. Exit Thesis、7. Pricing Thesis、8. Risks、9. Recommendation | 5-8 page |
| `pricing` | 1. Pricing Thesis (主)、2. WTP Analysis、3. Customer ROI、4. Competitive Pricing、5. Pricing Risks (e.g., cannibalization) | 1-2 page |
| `unit_economics` | (IC memo は default で skip) `11_KPI_Dashboard` 上部に Unit Economics Summary | (sheet 内 sub-section) |
| `cap_table` | 1. Dilution Analysis (主)、2. Founder-net at exit、3. SAFE / J-KISS conversion、4. Liquidation preference impact、5. Anti-dilution risks | 1-2 page |
| `ma_exit` | 1. Exit Thesis (主)、2. Likely Buyers、3. Founder Net (risk-adjusted)、4. Earn-out probability、5. Lock-up impact、6. Tax considerations | 2-3 page |
| `dcf_only` | (IC memo は default で skip) `09_DCF` 上部に DCF Summary | (sheet 内 sub-section) |
| `burn_runway` | (IC memo は default で skip) `11_KPI_Dashboard` 上部に Cash Trajectory Summary | (sheet 内 sub-section) |
| `three_statement` | (IC memo は default で skip) `12_SanityChecks` の pass/fail summary | (sheet 内 sub-section) |
| `market_sizing` | (IC memo は default で skip) `11_KPI_Dashboard` 上部に Market Sizing Summary | (sheet 内 sub-section) |
| `comps_only` | (IC memo は default で skip) `11_KPI_Dashboard` 上部に Comps Summary | (sheet 内 sub-section) |

### §9.2 IC memo sheet を含まない mode の deliverable

`unit_economics` / `dcf_only` / `burn_runway` / `three_statement` / `market_sizing` / `comps_only` は default で `13_IC_Memo` を bundle に含めない。代わりに該当 sheet 内 sub-section に summary を埋め込む。

ユーザーが explicit に IC memo を望む場合:
```yaml
output_mode: "dcf_only"
additional_sheets: ["13_IC_Memo"]
```
この時、`13_IC_Memo` は **DCF mode 専用 variant** で生成される (focus = DCF Summary + Comps cross-check)。

### §9.3 Mode 別 IC memo template (Markdown skeleton)

build_orchestrator が `13_IC_Memo` を生成する際の Markdown skeleton を mode 別に示す。

#### §9.3.1 `full` mode

```markdown
# Investment Memo: {entity_name}

## Executive Summary
- Stage / 業態 / ARR
- 投資 thesis 一行
- Recommendation

## 1. Investment Thesis
- Why this company / why now / unique value

## 2. Market Sizing
- TAM / SAM / SOM
- 市場成長率 / 自社 capture rate

## 3. Unit Economics
- LTV / CAC / payback / Magic Number / NRR

## 4. Valuation (DCF + Comps)
- DCF Base case EV
- Comps median multiple cross-check
- Football field

## 5. Cap Table
- 現 ownership matrix
- Series 後の dilution

## 6. Exit Thesis
- Likely buyers / IPO timing
- Founder net at $X exit

## 7. Pricing Thesis
- 現 pricing vs WTP boundary
- Pricing power 評価

## 8. Risks
- (kill criteria 4 段ゲート)

## 9. Recommendation
- Invest / Pass / Pass with conditions
```

#### §9.3.2 `pricing` mode

```markdown
# Pricing Thesis: {entity_name}

## Executive Summary
- 現 ARPU / WTP ceiling / 値上げ余地
- Pricing thesis 一行

## 1. Pricing Thesis
- Why current price is suboptimal (or optimal)
- Recommended pricing change (e.g., +20%)

## 2. WTP Analysis
- Customer survey 結果
- Gainsharing % calibration (0.20-0.30)

## 3. Customer ROI
- ROI vendor / customer split
- Payback period 顧客側

## 4. Competitive Pricing
- 競合価格 list
- 自社 implied premium / discount

## 5. Pricing Risks
- Cannibalization / churn risk
- Customer concentration risk
```

#### §9.3.3 `cap_table` mode

```markdown
# Cap Table & Dilution Analysis: {entity_name}

## Executive Summary
- Current cap table snapshot
- Post-Series-X dilution

## 1. Dilution Analysis
- Round 別 founder dilution
- Option pool refresh effect

## 2. Founder-net at Exit
- Exit value $X assumption
- Founder net (after LP, tax, lock-up)

## 3. SAFE / J-KISS Conversion
- Conversion price = Next Round Price × (1 − Discount)
- Post-money cap impact

## 4. Liquidation Preference Impact
- 1x non-participating vs participating
- Waterfall at $X exit

## 5. Anti-dilution Risks
- Down round impact
- Broad-based weighted formula
```

#### §9.3.4 `ma_exit` mode

```markdown
# M&A Exit Thesis: {entity_name}

## Executive Summary
- Exit value range / likely timing
- Founder net (risk-adjusted)

## 1. Exit Thesis
- Why M&A vs IPO
- Strategic rationale

## 2. Likely Buyers
- Strategic acquirers (top 5)
- Financial buyers (PE)
- Past precedent transactions

## 3. Founder Net (Risk-adjusted)
- Exit value × ownership × (1 - LP) × (1 - tax) × (1 - lock-up discount)
- Earn-out: amount × probability × ownership

## 4. Earn-out Probability
- ARR / EBITDA hurdle
- Achievement probability assessment

## 5. Lock-up Impact
- Lock-up period (typical 12 mo)
- Liquidity discount (annual 5-10%)

## 6. Tax Considerations
- Long-term capital gain treatment
- Section 1202 (US) / 譲渡所得 (Japan)
```

#### §9.3.5 `dcf_only` mode (additional_sheets で 13_IC_Memo 追加時)

```markdown
# DCF Valuation Memo: {entity_name}

## Executive Summary
- Base case EV
- Sensitivity range

## 1. DCF Summary
- WACC / g / terminal method
- 5 year FCF projection
- Terminal value

## 2. Sensitivity
- WACC × g matrix (5x3 grid)
- Conclusions on driver weights

## 3. Comps Cross-check
- EV/Revenue median
- Implied valuation reconciliation
```

#### §9.3.6 (他 mode は §9.2 通り、default で IC memo 不在)

### §9.4 Section 共通要素 (全 mode 共通)

どの mode でも IC memo 末尾に以下を含める (terminology 整合性):
- **Sheet 番号 reference**: 「詳細は `09_DCF` sheet 参照」等
- **Source data**: Hard input (`#0000FF`) cell 一覧
- **生成日 + skill version**: footer
- **Mode 表示**: header に「Output Mode: pricing」明示

### §9.5 IC memo の長さ control

| Mode | Default 長さ | `verbose: true` 時 |
|---|---|---|
| `full` | 5-8 page | 10-15 page (詳細 chart 込み) |
| `pricing` | 1-2 page | 3-4 page |
| `cap_table` | 1-2 page | 3-4 page |
| `ma_exit` | 2-3 page | 5-6 page |
| その他 | sub-section (sheet 内) | 1-2 page (additional_sheets で IC memo 追加時) |

`verbose` field は `15_input_schema` に optional field として追加可能 (Phase 7+ で検討)。

### §9.6 IC memo language

ユーザー言語に応じて出力言語を切り替え:
- 日本語入力 → 日本語 IC memo (canonical 用語は英語併記、例: "投資テーゼ (Investment Thesis)")
- 英語入力 → 英語 IC memo
- mixed → 日本語 default

---

## §10. Anti-patterns

本章は **mode 設計と運用での代表的な anti-pattern** をまとめる。`_self_review_protocol §8` の mode 別 self-review (§12 で詳述) と直結する。

### §10.1 デフォルトで `full` を強制

**症状**: ユーザーが「pricing thesis を」と prompt しているのに 14 sheet 全生成、BS / CFS / Debt 等の不要 sheet が並ぶ。

**害**:
- ユーザーが pricing 議論をしたいのに 14 sheet 通読する負担
- 不要 sheet (BS / CFS) が空欄 / 不完全 → audit 対象になり混乱
- Build 時間 4x、token 3x

**正しい対応**:
- §8 routing rule で intent → mode 自動推定
- `_master_decision_tree` 参照前に mode 確定
- ユーザーが「全体」と明示しない限り subset を選ぶ

### §10.2 Mode を ad-hoc 解釈

**症状**: 同じ pricing prompt で build 毎に異なる sheet 構成が出る (再現性なし)。

**害**:
- ユーザーが build を repeat しても同じ output が得られない
- 監査 / regression test が機能しない
- Skill の信頼性 erosion

**正しい対応**:
- 本 file §2.1 を canonical 化
- `OUTPUT_MODE_BUNDLES` dict は本 file と完全一致
- test (`tests/test_output_modes.py`) で固定

### §10.3 Cap table mode で `00_Cover` を省略

**症状**: 軽量化のため `00_Cover` を excluded、その他 4 sheet のみ生成。

**害**:
- document title が無く、何の model か読み手に伝わらない
- output_mode 表示が無い → 後で見ても mode 不明
- 生成日が無い → version 管理不可

**正しい対応**:
- **`00_Cover` は全 mode で必須** (§4.4.1 hard validation で `excluded_sheets: ["00_Cover"]` を禁止)
- Cover には mode 名、生成日、entity 名、output_mode を必ず記載

### §10.4 Mode 間の seam が曖昧

**症状**: `dcf_only` で `02_Revenue` が含まれない、結果 09_DCF が空欄 / nonsense。

**害**:
- DCF は revenue projection を起点とする、revenue なしでは計算不能
- ユーザーが「DCF」と言ったとき、build 内部では revenue ramp も必要だと skill が判断すべき

**正しい対応**:
- 各 mode の bundle に「計算依存先」必須 sheet (§2.1) を入れる
- `dcf_only` には `02_Revenue` を必ず含める (本 file §2.1 通り)
- bundle 設計時に sheet 間 dependency graph を描く

### §10.5 `additional_sheets` で全 14 個追加

**症状**: pricing mode だが additional に 7 個追加 → 結果 14 sheet (= full と同じ)。

**害**:
- mode 選択の意味喪失
- mode → bundle の SSoT が機能しない
- 「pricing mode + 7 additional = full」の暗黙運用が広まる

**正しい対応**:
- `additional_sheets` 4 個以上で warning (§4.4.2)
- ユーザーが多くを追加したいなら **`full` mode + `excluded_sheets` で減らす** ほうが意図明確
- mode 設計時に「relevant minimum」を見直す (本 file §2.1 update)

### §10.6 Mode を user に伝えない

**症状**: skill が mode = pricing で build したが、output に「Output Mode: pricing」表示なし。

**害**:
- ユーザーが「BS が無いのは bug?」と誤解
- mode 認識のないまま review、後で「全体が欲しかった」と再 build

**正しい対応**:
- `00_Cover` に **「Output Mode: pricing」** 表示必須
- IC memo header にも mode 表示
- chat response でも「pricing mode (7 sheet) で生成しました、全体が必要なら full に変更可」と一文添える

### §10.7 Excluded > Additional 衝突を silent 処理

**症状**: 同じ sheet が `additional_sheets` と `excluded_sheets` の両方に指定、warning なく excluded が勝つ。

**害**:
- ユーザーは additional に書いたつもりが output に含まれない
- silent 失敗で debug 困難

**正しい対応**:
- §4.4.2 で warning 必須: `WARN: 12_SanityChecks is both added and excluded; excluded wins`
- log audit trail に決定経緯を残す

### §10.8 Mode 推定の confidence を無視

**症状**: prompt が ambiguous で mode 推定 confidence が low、それでも skill が勝手に full で build。

**害**:
- ユーザー意図と outpu mismatch
- 「予想と違うものが出た」体験

**正しい対応**:
- §8.4 通り、ambiguous 時はユーザーに確認質問
- low confidence 時は default = full でも「default 適用しました、変更可」と一文添える

### §10.9 Subset mode で reference を無視して LLM が free-form 生成

**症状**: pricing mode で `18_customer_value_and_pricing.md` を読まず、LLM が prior knowledge で WTP boundary を 0.5 (boundary 外) に設定。

**害**:
- skill の SSoT が機能せず、`_self_review_protocol §8.7` で boundary 違反検出
- mode の reference dispatch が機能していない

**正しい対応**:
- mode 確定後、SKILL.md dispatch table の「第 1 reference」を必ず読む
- pricing mode → `18 §3, §4` 必読
- self-review check 7 (gainsharing boundary) で違反を catch

### §10.10 Backward compatibility を破る mode 仕様変更

**症状**: 既存 `full` mode の sheet 構成を勝手に変える (例: 12_SanityChecks を base から外す)。

**害**:
- 過去の build を再現できない
- regression test が壊れる

**正しい対応**:
- 本 file §2.1 を canonical、変更時は git history で trace
- 既存 mode の bundle 変更は major version change として扱う
- 新 mode 追加は backward compat 維持

### §10.11 Mode と業態の混同

**症状**: 「SaaS」と「pricing」を同列の mode として扱おうとする。

**害**:
- 業態 (SaaS / Marketplace) は `15_input_schema §2 業態判定` の domain
- mode (pricing / cap_table) は use case の domain
- 両者の混同で routing が機能不全

**正しい対応**:
- 業態 ≠ mode、明確に分離
- 業態 × mode は 11 業態 × 10 mode = 110 組合せ、全て canonical
- pricing mode for SaaS は `pricing` mode + `business_model: SaaS` で表現

### §10.12 Subset mode で integration check を skip

**症状**: `unit_economics` mode は 3 表 / cap table を含まないので、何も check しない。

**害**:
- 含まれる 6 sheet 内の integrity も unchecked
- mode 範囲内の error が検出されない

**正しい対応**:
- §12 mode 別 self-review check matrix に従い、**mode 範囲内の check は全実行**
- 「subset mode = check 全 skip」ではない
- mode に依存する check のみ適切に skip

---

## §11. Migration / Backward Compatibility

本章は新 14 sheet layout への移行と、既存 17 sheet build との互換性を整理する。

### §11.1 旧 17 sheet vs 新 14 sheet 対応

| 旧 17 sheet | 新 14 sheet | 統合 / 削除 rationale |
|---|---|---|
| `00_Cover` | `00_Cover` | 維持 |
| `01_Assumptions` | `01_Assumptions` | 維持 |
| `02_Drivers` | (`11_KPI_Dashboard` に統合) | KPI Dashboard が driver display 機能を代替 (canonical SSoT: `scripts/ib_format._OLD_TO_NEW_SHEET_MAP`) |
| `03_Revenue` | `02_Revenue` | renumber |
| `04_OpEx` | `03_OpEx` | renumber |
| `05_IS` | `04_IS` | renumber |
| `06_BS` | `05_BS` | renumber、Working Capital Schedule (旧 08_WC) を sub-section として吸収 |
| `07_CFS` | `06_CFS` | renumber |
| `08_WC` | (`05_BS` § Working Capital Schedule sub-section に統合) | BS と WC は会計的に地続き、rows 56-69 sub-section で表示 |
| `09_Debt` | `07_Debt` | renumber |
| `10_CapTable` | `08_CapTable` | renumber |
| `11_DCF` | `09_DCF` | renumber、Sensitivity & Stress (旧 13_Sensitivity) を sub-section として吸収 |
| `12_Comps` | `10_Comps` | renumber |
| `13_Sensitivity` | (`09_DCF` § Sensitivity & Stress sub-section に統合) | Valuation の派生、DCF と同 sheet で表示するほうが直感的 |
| `14_KPI_Dashboard` | `11_KPI_Dashboard` | renumber |
| `15_SanityChecks` | `12_SanityChecks` | renumber |
| `16_IC_Memo` | `13_IC_Memo` | renumber |
| `99_Glossary` | (削除、`_terminology.md` に統合) | reference に正本がある |

### §11.2 Backward compat の方針

| 状況 | 挙動 |
|---|---|
| 既存 input_schema (output_mode 未指定) | default = `full` で完全互換 (動作変わらず) |
| 既存 input_schema (旧 17 sheet 想定) | `full` mode の 14 sheet build に migration、旧 sheet 番号は alias で受ける |
| 新規 input (output_mode 明示) | 本 file §2.1 通り |
| 旧 build code (`build_model.py` v1) | `output_mode = "full"` を明示するか、未指定で default 動作 |

### §11.3 Sheet 番号 migration の alias 表

build_orchestrator は旧 sheet 番号を alias として受け、新番号に内部変換:

| 旧 sheet 名 | alias → 新 sheet |
|---|---|
| `02_Drivers` | → `11_KPI_Dashboard` |
| `03_Revenue` | → `02_Revenue` |
| `04_OpEx` | → `03_OpEx` |
| `05_IS` | → `04_IS` |
| `06_BS` | → `05_BS` |
| `07_CFS` | → `06_CFS` |
| `08_WC` | → `05_BS` (§ Working Capital Schedule sub-section) |
| `09_Debt` | → `07_Debt` |
| `10_CapTable` | → `08_CapTable` |
| `11_DCF` | → `09_DCF` |
| `12_Comps` | → `10_Comps` |
| `13_Sensitivity` | → `09_DCF` (§ Sensitivity & Stress sub-section) |
| `14_KPI_Dashboard` | → `11_KPI_Dashboard` |
| `15_SanityChecks` | → `12_SanityChecks` |
| `16_IC_Memo` | → `13_IC_Memo` |

### §11.4 Stage A code refactor との独立性

走行中の Stage A code refactor agent (`aa13f28b`) は scripts/ 配下の **code refactor** を担当する。本 file は references/ 配下の **新規 file** であり、conflict は発生しない。

但し:
- 本 file が参照する sheet 番号は **新 14-sheet layout**
- Stage A 完了前でも reference 内では新番号 canonical で書く
- Stage A 完了後、code 側 (build_orchestrator) も新番号 canonical に揃う

### §11.5 Phase の順序

| Phase | 内容 | 状態 |
|---|---|---|
| Phase 5 | 24 reference + audit Critical 0 | 完了 |
| Phase 6 | 5 新 reference (17/18/19, _named_ranges, _design_consistency) + dispatch table 拡張 | 完了 |
| Phase 6 拡張 (Stage A) | Code refactor (`scripts/build_model.py` skeleton, 17→14 sheet renumber) | 進行中 (`aa13f28b`) |
| Phase 6 拡張 (本書) | `_output_modes.md` 新設 + 15_input_schema patch + SKILL.md dispatch 拡張 | 本セッション |
| Phase 7 | Description optimization (trigger eval 5 iteration) | 後続 |

### §11.6 Migration test plan

```python
# tests/test_migration_14_sheet.py
def test_old_17_sheet_input_yields_14_sheet_output():
    """旧 17 sheet 番号で input しても新 14 sheet が出る (alias 経由)"""
    schema = {"output_mode": "full"}  # 旧 build code
    result = build_model(schema)
    assert len(result["xlsx"].sheetnames) == 14  # 17 ではなく

def test_alias_maps_correctly():
    """旧 03_Revenue alias が新 02_Revenue に変換される"""
    assert resolve_alias("03_Revenue") == "02_Revenue"
    assert resolve_alias("13_Sensitivity") == "09_DCF"

def test_default_full_mode_when_unspecified():
    """output_mode 未指定 → full default"""
    schema = {}
    result = build_model(schema)
    assert get_mode_used(result) == "full"
```

### §11.7 Rollback 手順

新 14 sheet layout に問題があった場合:
1. `OUTPUT_MODE_BUNDLES` を旧 17 sheet 構成に巻き戻す
2. 本 file §2.1 を旧構成版で update
3. SKILL.md 14 sheet layout 表記を 17 sheet に戻す
4. `_terminology.md §3` の sheet 順を旧版に戻す
5. test 全部 re-run、affected 5 reference を patch

実際の rollback は major version change、user notice 必要。

---

## §12. 関連 Reference との整合 (mode 別 self-review check matrix)

本章は `_self_review_protocol §8` の 10 check が mode によってどう調整されるかを **canonical matrix** として整理する。

### §12.1 Mode 別 self-review check matrix

`_self_review_protocol §8` の 10 check が mode で必須 / skip となる対応:

| # | Check 内容 | full | pricing | unit_econ | cap_table | ma_exit | dcf_only | burn_runway | three_st | market_sz | comps_only |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SanityChecks sheet ✅ | ✓ | skip | ✓ | skip | skip | skip | skip | ✓ | skip | skip |
| 2 | 4 段ゲート閾値通過 | ✓ | skip | skip | skip | ✓ | skip | skip | skip | skip | skip |
| 3 | applicability matrix 誤適用なし | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | terminology canonical 値一致 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | accept with rationale 記録 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | Customer ROI thesis (`18 §3.1`) | ✓ | ✓ | skip | skip | skip | skip | skip | skip | skip | skip |
| 7 | WTP boundary 0.20-0.30 | ✓ | ✓ | skip | skip | skip | skip | skip | skip | skip | skip |
| 8 | M&A Exit thesis (`19 §1`) | ✓ | skip | skip | skip | ✓ | skip | skip | skip | skip | skip |
| 9 | Named range coverage 80%+ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | skip | skip |
| 10 | Design consistency D1-D12 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**凡例**:
- ✓ = 必須 check
- skip = mode 範囲外、check しない (accept with rationale 不要)

### §12.2 Skip rationale (主要 mode)

| Mode | Skip する check (#) | Rationale |
|---|---|---|
| `pricing` | 1, 2, 8 | SanityChecks sheet 不在 / 4 段ゲートは full 専用 / M&A Exit は scope 外 |
| `unit_economics` | 2, 6, 7, 8 | 4 段ゲート / pricing 関連 / M&A 関連は scope 外 |
| `cap_table` | 1, 2, 6, 7, 8 | SanityChecks 不在 / 4 段ゲート / pricing / M&A は scope 外 |
| `ma_exit` | 1, 6, 7 | SanityChecks 不在 / pricing 関連は scope 外 |
| `dcf_only` | 1, 2, 6, 7, 8 | SanityChecks 不在 / 4 段ゲート / pricing / M&A は scope 外 |
| `burn_runway` | 1, 2, 6, 7, 8 | 上記同様 |
| `three_statement` | 2, 6, 7, 8 | 4 段ゲート / pricing / M&A は scope 外 |
| `market_sizing` | 1, 2, 6, 7, 8, 9 | named range は KPI sheet のみ最小限、80%+ 条件は適用外 |
| `comps_only` | 1, 2, 6, 7, 8, 9 | 上記同様 |

### §12.3 Master decision tree との整合

`_master_decision_tree §C 4 段ゲート` は **`full` mode** が前提。subset mode では skip 可能だが、**`ma_exit` mode は exit thesis を defensible にするため §C ゲート 1-3 を実行**:

| Mode | §C 4 段ゲート | 範囲 |
|---|---|---|
| `full` | 全 4 段実行 | gate 1-4 |
| `ma_exit` | gate 1-3 実行 | exit thesis defensibility |
| `pricing` | skip | pricing thesis は §C 範囲外 |
| その他 | skip | mode 範囲外 |

### §12.4 Self-review プロトコル v2 (mode 対応版)

`_self_review_protocol.md §8` を mode 対応に拡張:

```markdown
# §8 Self-Review (mode 対応版)

## §8.1 Mode 確定
build_orchestrator が確定した mode を取得。

## §8.2 Check matrix 適用
本 file `_output_modes.md §12.1` の matrix に従い、mode に対応する check のみ実行。

## §8.3 Check 実行順
1, 2, 3, 4, 5, 6, 7, 8, 9, 10 の順で、mode で ✓ の check のみ。

## §8.4 失敗時の修正 wave
`_self_review_protocol §3 修正 wave` を mode 範囲内で実行。
mode 範囲外の sheet を修正しない。

## §8.5 Pass / fail 判定
全 ✓ check が pass で `mode 内 PASS`。
mode 内のいずれか fail で修正 → 再 review (max 3 iteration)。
```

### §12.5 関連 reference へのフック

| reference | 本 file との関係 | 整合 patch (本 file が要求) |
|---|---|---|
| `SKILL.md` | dispatch table | §5.1 の table に置き換え、Mode 列追加 |
| `15_input_schema.md` | input field | §4 で 4 field 追加 (output_mode, additional_sheets, excluded_sheets, deliverable) |
| `_master_decision_tree.md` | 4 段ゲート | §C 冒頭に「mode = `full` 前提、subset では skip 可能」一文追加 |
| `_self_review_protocol.md` | 10 check | §8 を §12.4 通り mode 対応版に拡張 |
| `_terminology.md` | 14 sheet 順 | §3 の sheet 順を新 14 sheet に update (旧 17 → 新 14) |
| `_named_ranges.md` | named range coverage | mode 別 80%+ 条件は §12.1 check #9 で扱う、market_sizing / comps_only は除外 |
| `_design_consistency_rules.md` | D1-D12 | 全 mode で必須 (check #10) |
| `_stress_framework.md` | applicability matrix | 全 mode で必須 (check #3) |
| `18_customer_value_and_pricing` | pricing 計算 | `pricing` / `full` mode で必読 |
| `19_ma_exit_for_founders` | M&A 計算 | `ma_exit` / `full` mode で必読 |
| `22_driver_based_modeling` | driver | `unit_economics` / `pricing` / `full` mode で必読 |
| `23_sensitivity_and_implications` | 感度分析 | `dcf_only` / `pricing` / `full` mode で 09_DCF 内蔵 |

### §12.6 Cross-reference matrix

```
_output_modes (本 file)
   ├── §2.1 → SKILL.md dispatch (§5)
   ├── §4   → 15_input_schema (4 field)
   ├── §5   → SKILL.md dispatch (Mode 列追加)
   ├── §6   → scripts/build_orchestrator.py (将来)
   ├── §8   → SKILL.md routing rule
   ├── §9   → 13_IC_Memo template (mode 別)
   └── §12  → _self_review_protocol §8 (mode 対応版)
```

### §12.7 Validation checklist (本 file 自体の整合性)

本 file の主張が他 reference と整合しているかの自己 audit:

- [ ] §2.1 の bundle が §6.1 の OUTPUT_MODE_BUNDLES と完全一致
- [ ] §4 の field が §6.1 の build_model 引数と一致
- [ ] §5.1 の dispatch table が §8.1 の keyword mapping と整合
- [ ] §9.1 の IC memo focus が §3 各 mode の focus 記述と一致
- [ ] §12.1 の check matrix が §3 各 mode の self-review check 数と一致
- [ ] §11.1 の旧/新 sheet 対応が `_terminology §3` 新版と一致

---

## 付録: Mode 早見表 (印刷用)

| Mode | Sheets | 時間 | 用途 |
|---|---|---|---|
| `full` | 14 | 30s | Series A+ / IPO / IC memo 全体 |
| `pricing` | 7 | 8s | Pricing thesis / WTP / 値上げ余地 |
| `unit_economics` | 6 | 5s | LTV/CAC / Magic Number / cohort |
| `cap_table` | 5 | 5s | SAFE / dilution / founder net |
| `ma_exit` | 6 | 10s | M&A exit / earn-out / lock-up |
| `dcf_only` | 5 | 6s | Pure DCF / WACC sensitivity |
| `burn_runway` | 7 | 8s | Cash runway / burn / breakeven |
| `three_statement` | 9 | 15s | 三表 audit / 監査法人渡し |
| `market_sizing` | 4 | 4s | TAM / SAM / SOM |
| `comps_only` | 4 | 4s | Comps benchmark / multiple |
