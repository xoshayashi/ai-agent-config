---
name: sensitivity_and_implications
description: 感応度分析の網羅性 (impact 上位 driver の cumulative ≥ 80% カバー) と示唆解釈 (numbers → decision-grade narrative) の正本。Tornado / Scenario / Threshold / Break-even の各手法に加え、結果を「だから何」レベルで logical に説明する narrative template を体系化。IC memo の "Implications" section、management discussion、investor communication に直接使用
type: reference
priority: P0
related: [22_driver_based_modeling, 09_DCF § Sensitivity, 18_customer_value_and_pricing, 19_ma_exit_for_founders, 08_ic_memo, _self_review_protocol, _master_decision_tree]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 「感応度分析の網羅性 protocol (top-N driver で cumulative impact ≥ 80% カバー)」「Bull / Base / Bear scenario 整合性」「threshold / break-even / margin of safety」「示唆解釈 narrative の 5 要素 frame と template」「visual storytelling (IC memo の Implications page layout)」「cross-driver correlation と doomsday scenario」「sensitivity 関連 sanity_checks (S11-S14)」は本書を canonical とする。`22_driver_based_modeling` は driver tree decomposition と tornado の **mechanics** を canonical とし、`09_DCF § Sensitivity` は xlsx 上の **sensitivity sheet 実装** を canonical とするが、本書はそれらの **結果を「だから何」レベルで logical に解釈し IC memo の Implications section に inject する narrative の正本** である。
- **Routing**: [`_master_decision_tree.md §C 4 段ゲート`](_master_decision_tree.md) の Stage D (sensitivity & implications) では本書 §2 (coverage protocol)、§4 (Bull/Base/Bear)、§5 (threshold)、§6 (narrative template) を必須適用する。Quick mode でも top-3 driver の implication narrative は省略不可。Standard / Comprehensive mode では §2.2 の coverage rule (IC memo: cumulative 90%) と §6.3 の executive summary template を全 critical output に適用する。
- **Self-review**: 本書に従って sensitivity & implications を構築したあと、[`_self_review_protocol.md §8`](_self_review_protocol.md) の check 11-14 (本書 §9 で sanity 連携: S11 Coverage / S12 Concentration / S13 Threshold MoS / S14 Top-down × Bottom-up reconciliation) を必ず実行する。
- **関連 reference**: `22_driver_based_modeling` (driver tree、tornado mechanics、Tier 1-4 source) / `09_DCF § Sensitivity` (sensitivity sheet 実装、本書 §3 / §7 の visual layout に従う) / `18_customer_value_and_pricing` (pricing driver 感応度の interpretation 例) / `19_ma_exit_for_founders` (exit valuation sensitivity の founder 視点) / `08_ic_memo` (本書 §6 narrative template が IC memo "Implications" section に直接 inject) / `_self_review_protocol` (S11-S14) / `_master_decision_tree` (Stage D ゲート)。

> 用語注: 本書では「Operating System」「OS」表記を避け、「処理系」「経営の仕組み」と表現する (個人ルール、`MEMORY.md` 参照)。時系列の数値データは原則として markdown table に揃える。
>
> 出典規律: 全 sensitivity range / threshold / margin of safety の値は **`_benchmark_protocol`** の Tier 1-4 規律に従い、本文または `15_input_schema` の `source_url` field に一次出典を併記する。レンジが分かれる場合は **平均化せずレンジで提示** し、推奨は中央値ではなく **保守側 (悲観側)** を採用する。
>
> 範囲外: tornado mechanics の python 実装詳細 (`compute_tornado`、driver tree node 構造) は `22_driver_based_modeling §6` を canonical、sensitivity sheet の cell layout / Excel formula / named range は `09_DCF § Sensitivity` を canonical、Tier 1-4 source 分類の詳細運用は `_benchmark_protocol` を canonical、IC memo 全体の構成は `08_ic_memo` を canonical とし、本書では触れない。本書は **「coverage 担保」「scenario 整合」「threshold defensibility」「示唆 narrative」** に特化する。

---

# 23. Sensitivity & Implications — 「網羅性 + 解釈 narrative」の正本

> 本ドキュメントは、財務モデリングにおいて **感応度分析の最後の 1 マイル**、すなわち「重要 driver を取りこぼさず網羅したか (coverage)」「Bull / Base / Bear が driver dependency に整合するか (scenario consistency)」「thesis が崩れる境界はどこか (threshold / margin of safety)」「結果を意思決定に直結する narrative にどう translate するか (implication)」を定義する **decision-grade interpretation の正本** である。
>
> **対象読者**: Claude (xlsx 13 / 22 系の sensitivity 出力を IC memo の "Implications" / "Risks" / "Defense" section に変換するエージェント、`build_model.py` から coverage check を呼び出すエージェント、scenario 整合 check を実装するエージェント)、それを review する人間バンカー / VC partner / founder / IC member。
>
> **Scope (INCLUDE)**: 「数字 → 示唆 → 意思決定」3 段の設計原則、coverage protocol (top-N auto-detection、stage 別 coverage rule、long-tail 処理、variable interaction 検出)、Tornado chart best practices (layout、annotation、Pareto cumulative line)、Scenario analysis (Bull / Base / Bear、driver dependency 整合 check、segment 別、probability-weighted output)、Threshold / Break-even (cash runway / profitability / valuation / kill criteria、solver-based finding、margin of safety table)、**Implication narrative templates (核心)** (5 要素 frame、per-driver template、top-3 implications template、4-quadrant decision frame、5 つの common pattern library)、Visual storytelling (IC memo の "Sensitivity & Implications" page layout、color principle、annotation 多用)、Cross-driver correlation (pairwise stress、doomsday scenario、triple-point scenario)、Quantitative checks (S11 Coverage / S12 Concentration / S13 Threshold MoS / S14 Top-down × Bottom-up reconciliation)、Mini cases (Series A SaaS / Marketplace / Bio / D2C / AI / 失敗事例 / Fintech)、Anti-patterns (1-2 driver only、pretty chart no narrative、single scenario、arbitrary range、vague implication、uncoupled implications)、関連 reference 整合 cross-link。
>
> **Scope (EXCLUDE — 別 reference 担当)**:
>
> | 領域 | 担当 reference | 本書の扱い |
> |---|---|---|
> | driver tree decomposition、leaf 規律、業態別 driver tree skeleton | `22_driver_based_modeling §2-§3` | 触れず。本書は **decomposed driver の sensitivity 結果解釈** のみ。 |
> | tornado mechanics (low/high 計算、`compute_tornado` python) | `22_driver_based_modeling §6` | 触れず。本書 §3 は **tornado の見せ方と解釈** のみ。 |
> | sensitivity sheet の cell layout、Excel formula、named range | `09_DCF § Sensitivity` | 触れず。本書 §7 は **IC memo page layout 設計** のみ。 |
> | Tier 1-4 source 分類の詳細、citation 規律 | `_benchmark_protocol` | 触れず。本書 §6.2 は **narrative 内の Tier 表記方法** のみ。 |
> | IC memo 全体構成 (Executive summary / Thesis / Risks / Recs) | `08_ic_memo` | 触れず。本書 §6.3 は **"Implications" sub-section の narrative** のみ。 |
> | DCF / WACC / probability-weighted valuation の formula | `05_valuation_wacc` | 触れず。本書 §4.4 は **scenario × probability の運用ルール** のみ。 |
> | metric formula (NRR / Burn Multiple / LTV/CAC) | `02_saas_metrics` | 触れず。本書は **metric 値が振れた時の implication** のみ。 |
> | xlsx の color、font、sheet naming | `_design_consistency_rules` / `_named_ranges` | 触れず。本書 §7.2 は **chart 上の color principle** のみ。 |
>
> **数値の出典**: 本文中に明示。Bain (sensitivity と tornado の運用に関する thought leadership)、a16z (growth team の cohort-driven scenario 設計)、Bessemer (cloud business の sensitivity 規律)、McKinsey (driver tree / value driver 概念)、BCG (decision frame)、Goldman Sachs / Morgan Stanley / J.P. Morgan (IB equity research の sensitivity & implications page)、Damodaran NYU Stern (narrative and numbers の橋渡し)、IPO prospectus 標準 (Risk Factors の sensitivity discipline)。primary source URL と観測時点を併記する。
>
> **思想的継承**: 本書の方法論は、IB (Goldman Sachs / Morgan Stanley / J.P. Morgan の equity research の "Implications page")、Bain (sensitivity tornado を意思決定 narrative に translate する規律)、a16z (Bull/Base/Bear scenario を thesis defense に使う運用)、McKinsey (4-quadrant decision frame: Manageable × Controllable)、Damodaran NYU Stern ("narrative and numbers" — 数字に narrative を必須付加)、IPO prospectus の Risk Factors 規律 (threshold + mitigation を pair で記述) の合流点に位置づける。本書はこれらの実務知を **startup IC memo の "Implications" section の正本** として 1 本に束ね、`build_model.py` から呼び出される narrative generator として再構成したものである。

---

## 目次

1. [設計原則 — 「数字 → 示唆 → 意思決定」3 段](#1-設計原則--数字--示唆--意思決定-3-段)
2. [Coverage Protocol (網羅性の自動担保)](#2-coverage-protocol-網羅性の自動担保)
3. [Tornado Chart Best Practices](#3-tornado-chart-best-practices)
4. [Scenario Analysis (Bull / Base / Bear)](#4-scenario-analysis-bull--base--bear)
5. [Threshold / Break-even Analysis](#5-threshold--break-even-analysis)
6. [Implication Narrative Templates (核心)](#6-implication-narrative-templates-核心)
7. [Visual Storytelling](#7-visual-storytelling)
8. [Cross-driver Correlation & Multi-variable Stress](#8-cross-driver-correlation--multi-variable-stress)
9. [Quantitative checks (sanity_checks 統合)](#9-quantitative-checks-sanity_checks-統合)
10. [Mini Cases (実例)](#10-mini-cases-実例)
11. [Anti-patterns](#11-anti-patterns)
12. [関連 reference との整合](#12-関連-reference-との整合)

---

<!-- WAVE 1: §1-§4 -->

## 1. 設計原則 — 「数字 → 示唆 → 意思決定」3 段

### 1.1 感応度分析の本質

感応度分析 (sensitivity analysis) の本質は、**「output の不確実性を input driver の不確実性に分解する」** ことである。「どの input が、どれだけ output を動かすか」を定量化し、それを **意思決定** に translate する。これは単なる数学的 exercise ではなく、IC (investment committee) の意思決定 quality を担保する **defense layer** である。

> **感応度分析が果たす 3 つの役割**:
>
> 1. **Risk discovery** — どの assumption が thesis の rerun risk を支配するか
> 2. **Defense preparation** — IC partner の "what if X goes south?" 質問への準備
> 3. **Action translation** — 数字 → management 意思決定 (KPI 監視、tranching、mitigation)

### 1.2 不十分な感応度分析の典型 pattern

実務で繰り返し observed される **failure pattern** を 6 つに分類する:

| Pattern | 内容 | 起きやすい場所 |
|---|---|---|
| **P1: Single-driver tornado** | 1-2 変数だけ振って終わり (典型は WACC のみ) | 急ぎの IC pre-meeting deck |
| **P2: Pretty chart, no narrative** | tornado chart は出すが「だから何」が不在 | analyst 主導の memo |
| **P3: Bull only / Base only** | Bear scenario が無く Bull / Base のみ | founder pitch deck |
| **P4: Arbitrary range** | ±10% で全 driver を一律に振る (Tier 別 range 不在) | first-pass model |
| **P5: Vague implication** | 「important driver なので注意」レベルの非 specific 表現 | senior review なしの memo |
| **P6: Uncoupled implications** | 各 driver の text が independent、cascade 関係なし | 大型 model の analyst 寄せ集め |

本書は **これら 6 pattern を全て排除するための protocol** を提示する。§11 で再列挙し、anti-pattern として detection check も併記する。

### 1.3 感応度分析の必須 5 要素

IC memo / management discussion / investor communication で **defensible な感応度分析** が成立するためには、以下 5 要素が **全て** 揃う必要がある:

1. **Coverage** — 重要 driver を網羅 (cumulative impact ≥ 80%、IC memo は 90%、IPO prospectus は 95%)
2. **Magnitude** — output 変動幅を **金額** (¥M 単位) と **%** の両方で
3. **Threshold** — thesis が崩れる境界 (cash runway / breakeven / valuation / kill criteria)
4. **Scenario** — Bull / Base / Bear の **driver dependency に整合した** 組合せ
5. **Narrative** — 上記 4 つを **logical** に説明する文章 (5 要素 frame、§6.1)

> **defensible とは何か**:
>
> 「IC partner / 監査法人 / IPO 主幹事から challenge された時、数字 + chart + narrative の 3 体で答えられる」状態を defensible とする。1 つでも欠けると、問い詰められて崩れる。

### 1.4 「数字 → 示唆 → 意思決定」3 段モデル

本書の中核 frame は以下の 3 段である:

```
Stage 1: 数字 (Numbers)
        ↓ 何が起きているか
Stage 2: 示唆 (Implication / "So What")
        ↓ それは投資意思決定にどう影響するか
Stage 3: 意思決定 (Action / Decision)
        ↓ Management / IC は何をすべきか
```

各 Stage で出力される deliverable は以下:

| Stage | Deliverable | Source reference |
|---|---|---|
| Stage 1 (数字) | Tornado chart / Scenario table / Threshold table | `22_driver_based_modeling §6` (mechanics) |
| Stage 2 (示唆) | Implication narrative (per-driver / executive summary) | **本書 §6** (canonical) |
| Stage 3 (意思決定) | Action / KPI / Trip-wire / Mitigation plan | **本書 §6.4** (decision frame) |

**重要**: Stage 1 で止めるのが P1-P2 anti-pattern。Stage 3 まで到達して初めて IC memo に inject できる。

### 1.5 IC memo "Implications" section の 3 体構造

IC memo の "Implications" section は、以下 3 体 (3 種類の表現形式) で構成する:

```
┌──────────────────────────────────────────┐
│ 数字 (Numbers)                            │
│ ・Tornado chart (top 8-12 drivers)        │
│ ・Bull/Base/Bear table (3 columns)        │
│ ・Threshold table (5 critical thresholds) │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│ 視覚 (Charts / Visual)                    │
│ ・Pareto cumulative line                  │
│ ・Scenario bar chart                      │
│ ・Margin of safety color (R/Y/G)          │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│ 文章 (Narrative)                          │
│ ・Top 3 implications (executive summary)  │
│ ・Per-driver narrative (5 要素 frame)     │
│ ・Defense Q&A (anticipated IC question)   │
└──────────────────────────────────────────┘
```

3 体が連動することで、glance reader (numbers / visual だけ見る) と deep reader (narrative まで読む) の両方に対応できる。

### 1.6 思想的継承 — narrative and numbers

本書の思想は Damodaran NYU Stern の **"narrative and numbers"** 哲学を直接受け継ぐ。Damodaran は「数字だけ、narrative だけ、どちらも valuation を defensible にしない」と説く。本書はこれを **感応度分析の文脈** に適用し、「sensitivity 数字 → narrative」 の翻訳手続きを **template 化** する。

> Source: Damodaran, A. (2017), *Narrative and Numbers: The Value of Stories in Business*, Columbia Business School Publishing。

加えて、IB equity research の "Implications page" 規律 (Goldman Sachs / Morgan Stanley / J.P. Morgan の sector report 標準)、Bain の sensitivity tornado を意思決定 narrative に translate する規律、a16z growth team の Bull/Base/Bear scenario を thesis defense に使う運用を、startup 特有の文脈 (Tier 1-4 source、segment 別、early-stage の epistemic uncertainty) で再構成する。

---

## 2. Coverage Protocol (網羅性の自動担保)

### 2.1 問題定義 — なぜ 1-2 driver では不十分か

感応度分析の最大の failure mode は **「網羅性不足」** (P1: Single-driver tornado) である。典型例:

- WACC だけ振って sensitivity table 1 枚で終わり
- Top-line growth rate だけ振って bottom-up driver は未検証
- 1 つの metric (例: NRR) だけ振って sales-side driver (productivity / win rate) は固定

これらは **「IC partner が他 driver を聞いた時に答えられない」** 状態を作り、必ず IC で詰まる。本書はこれを **coverage protocol** で systematic に防ぐ。

### 2.2 Top-N driver auto-detection (cumulative ≥ 80%)

全 leaf driver に対して tornado を回し、impact 順に並べたうえで **cumulative impact が target_cumulative (default 80%) に達するまで** top driver を自動選択する:

```python
def coverage_top_n(impacts: list[dict], target_cumulative: float = 0.80) -> list[dict]:
    """Impact 順に sort、cumulative が target_cumulative に達するまで取る.

    Args:
        impacts: list of {"driver": str, "swing": float, "tier": int, ...}
                 swing は high - low の絶対値 (¥M)
        target_cumulative: 取得停止の累積閾値 (0.80 = 80%)

    Returns:
        selected: 上位 driver の list (cumulative ≥ target_cumulative まで)
    """
    sorted_impacts = sorted(impacts, key=lambda x: x["swing"], reverse=True)
    total_swing = sum(x["swing"] for x in sorted_impacts)
    if total_swing == 0:
        return []
    cumulative = 0
    selected = []
    for impact in sorted_impacts:
        selected.append(impact)
        cumulative += impact["swing"]
        if cumulative / total_swing >= target_cumulative:
            break
    return selected
```

> **使い方**:
>
> ```python
> impacts = compute_tornado(driver_tree, output="EV", base_case=base_inputs)
> # impacts = [{"driver": "Sales productivity", "swing": 350, ...}, ...]
> selected = coverage_top_n(impacts, target_cumulative=0.80)
> # IC memo の場合: target_cumulative=0.90
> ```

`compute_tornado` は `22_driver_based_modeling §6.4` の python helper を呼び出す (mechanics は 22 が canonical)。本書は **その出力を coverage 規律で篩い分ける** layer を提供する。

### 2.3 Coverage rule canonical (Stage 別)

IB / VC / IPO 実務での **coverage rule canonical** を以下に固定する:

| Stage | 用途 | Min cumulative coverage | Typical driver count |
|---|---|---|---|
| Internal modeling | analyst 内部の health check | 70% | 4-7 |
| Investor pitch | 一次 fundraising の deck | 80% | 5-9 |
| **IC memo** | **VC / PE の最終 IC** | **90%** | **7-12** |
| Audit / IPO prospectus | 監査法人 / 主幹事 / 当局 review | 95% | 10-18 |

> **規律**: IC memo では **少なくとも cumulative 90% impact までの driver を tornado に表示する**。IPO prospectus では 95%。これは IB 実務での合意水準であり、これを下回ると "long tail of small drivers" が aggregate されず、後で "実は driver Y が大きかった" 事故になる。

#### 2.3.1 Stage 別 coverage の数字根拠

| Stage | なぜこの水準か |
|---|---|
| 70% (internal) | analyst 内部で「主要 driver の感覚を掴む」のが目的、80% を待たずに sanity check できるよう速度優先 |
| 80% (pitch) | investor 1st meeting では time-boxed (30-60 min)、top 5-9 driver で物語が成立 |
| 90% (IC) | IC partner は full discretion を持って意思決定、long tail も infer できる必要 |
| 95% (IPO) | 当局 / 主幹事の **risk factor** disclosure 規律、漏れは法的責任 |

### 2.4 Coverage gap detection と long-tail 処理

top 80% / 90% で止めると、**残り driver の合計** ("long tail") が `Other ±X%` として残る。これを以下のルールで処理する:

#### 2.4.1 Long tail を `Other` で aggregate

tornado chart の最下段に `Other (residual ±X%, n drivers)` の bar を表示する:

```
Driver                     | Impact (¥M)
---------------------------|--------------
Sales productivity         | ████████████  350
ACV                        | ████████      220
Churn rate                 | ██████        160
NRR                        | █████         140
Win rate                   | ████          110
S&M efficiency             | ███           80
Other (residual, 12 drvs)  | ██            55  ← long tail aggregate
```

これにより、**「top driver で説明されない部分」を視覚化** でき、reader は long tail の存在を認識できる。

#### 2.4.2 Long tail が大きい場合の root cause

long tail の合計が **total swing の 20% を超える** 場合、driver decomposition が **不十分** な signal:

| Long tail % | 解釈 | Action |
|---|---|---|
| 0-10% | 健全。top driver で説明力十分 | そのまま採用 |
| 10-20% | 許容範囲。`Other` annotation で透明化 | OK |
| **20-30%** | **WARN**: driver decomposition 不十分 | top driver の sub-decomposition を検討 |
| **> 30%** | **FAIL**: driver tree の root cause analysis が必要 | `22_driver_based_modeling §2` に戻り decompose やり直し |

> **why this rule**: もし `Other` が 30% を占めるなら、それ自体が「単独 driver より大きい cluster」になり、無視できない。実は `Other` の中の特定 driver が dominant かもしれず、それを掘り起こさないと thesis defense できない。

### 2.5 Variable interaction の検出

single-variable tornado は **「他の driver は固定 (ceteris paribus)」** という前提に立つ。しかし真の uncertainty には **cross-correlation** がある:

> **典型 correlation 例**:
> - ARR growth 高 ↔ S&M cost も高 (acquisition spend を増やさないと growth は出ない)
> - Pricing 高 ↔ Win rate 低 (price elasticity)
> - Headcount 高 ↔ Productivity 低 (ramp-time が長い、hire の品質低下)
> - Marketplace GMV 高 ↔ Take rate 圧縮 (大手 merchant の交渉力)

これらを single-variable tornado だけで議論すると、**「楽観 bias の重ね合わせ」** が起きる (Bull で全 driver を high に振ったが、現実には driver A が high なら driver B は low になる)。

#### 2.5.1 Top 5 driver の 2-way interaction matrix

coverage protocol の最後の step として、**上位 5 driver の 2-way interaction matrix** を check する (5 × 5 = 25 cell、対角と上三角は省略可で 10 cell):

| | Sales prod. | ACV | Churn | NRR | Win rate |
|---|---|---|---|---|---|
| Sales prod. | — | + 0.3 | -0.1 | -0.0 | + 0.5 |
| ACV | | — | -0.2 | + 0.4 | -0.6 |
| Churn | | | — | -0.9 | -0.1 |
| NRR | | | | — | + 0.1 |
| Win rate | | | | | — |

> 数値は「同じ direction で動く前提の妥当性」を [-1, +1] で表記。`+0.5` 以上 / `-0.5` 以下は **scenario consistency check** で必須考慮。

##### Interaction strength の運用

| Strength | 運用 |
|---|---|
| `|corr| < 0.2` | 独立 (independent) と扱える、single-variable tornado OK |
| `0.2 ≤ |corr| < 0.5` | 弱い correlation、Bull/Base/Bear scenario で考慮 |
| `0.5 ≤ |corr| < 0.8` | 強い correlation、scenario 内で **必ず同方向 (or 逆方向) に動かす** |
| `|corr| ≥ 0.8` | 同一 driver と扱う、merge 検討 (driver tree の重複) |

#### 2.5.2 Interaction matrix の生成方法

Tier 1 (社内 historical data あり) → 過去 12-24 月の monthly data から corr 計算。Tier 2-3 (industry data) → benchmark report の cross-tab から推定。Tier 4 (founder estimate) → 不可、 `n.a.` で空欄。

```python
def correlation_matrix(top_drivers: list[str], history_df: pd.DataFrame) -> pd.DataFrame:
    """Top driver 間の Pearson corr matrix を返す."""
    if history_df.empty:
        return pd.DataFrame()  # Tier 4 → empty
    return history_df[top_drivers].corr(method="pearson")
```

### 2.6 Coverage check の自動化 — sanity check S11

`scripts/sanity_checks.py` に追加する **S11 (coverage check)** :

```python
def check_S11_coverage(tornado_impacts: list[dict], stage: str = "IC") -> dict:
    """Top driver の cumulative impact が stage 別 threshold 以上か."""
    threshold_map = {"internal": 0.70, "pitch": 0.80, "IC": 0.90, "IPO": 0.95}
    threshold = threshold_map[stage]
    sorted_impacts = sorted(tornado_impacts, key=lambda x: x["swing"], reverse=True)
    total = sum(x["swing"] for x in sorted_impacts)
    if total == 0:
        return {"status": "FAIL", "reason": "no swing detected"}
    # tornado に表示している top-N (default 10) で cumulative を計算
    displayed_n = min(10, len(sorted_impacts))
    cumulative = sum(x["swing"] for x in sorted_impacts[:displayed_n]) / total
    if cumulative >= threshold:
        return {"status": "PASS", "cumulative": cumulative, "threshold": threshold}
    else:
        return {
            "status": "WARN",
            "cumulative": cumulative,
            "threshold": threshold,
            "reason": f"top {displayed_n} drivers cover only {cumulative:.0%}, "
                      f"below {stage} threshold {threshold:.0%}",
            "recommendation": "increase displayed_n or decompose driver tree further",
        }
```

詳細は §9.1 を参照。

---

## 3. Tornado Chart Best Practices

### 3.1 標準 layout (IB equity research style)

tornado chart は **single chart で「どの driver が、どれだけ output を動かすか」を一目で示す** 標準 visual である。layout の canonical は:

```
                        ←  base case  →
                         ↓
                ┌────────────────────────────┐
Sales prod.     │  ████████████████████████  │  ← top 1
ACV             │      ████████████████      │
Churn           │        ██████████          │
NRR             │          ████████          │
Win rate        │           ██████           │
S&M efficiency  │            ████            │
Pricing power   │             ███            │
Other           │              ██            │
                └────────────────────────────┘
              -200      0       +200       +400  (Δ EV ¥M)
```

#### 3.1.1 Axis 規律

| Axis | 規律 |
|---|---|
| **Y 軸** | Driver 名、上位から impact 順 (上が最大) |
| **X 軸** | output 変動幅 (¥M、絶対値) または % (output base case 比) |
| **Center line** | base case output (例: EV ¥1,500M) |
| **Bar の center** | 各 driver の swing range の中点 (通常 base と一致しない場合あり、その時は asymmetric) |
| **Bar の width** | high - low の幅 (impact magnitude) |

> **Why "上位から impact 順"**: reader が左上から読み始める習慣 (F-pattern eye tracking) に合わせ、最重要 driver を真っ先に提示する。

#### 3.1.2 Color (本書 §7.2 と整合)

- **Top 3 bar**: accent color (Navy `#1F3A66` / Teal `#008A80` / Gold `#ECC85A`)
- **Other bars**: muted gray (`#9CA3AF` 程度)
- **Center line**: ink (`#2D332E`)
- **Background**: surface (`#ECE9E1`)

これは Act design の color palette (CLAUDE.md 参照) に整合。

### 3.2 Bar 内 / Bar 周辺の annotation

bar 単独では「どこから / どこまで / どの Tier」が分からない。以下の annotation を **必ず付与** する:

| Annotation | 位置 | 例 |
|---|---|---|
| Driver name | 左 (Y 軸 label) | `Sales productivity` |
| Low value | bar の左端 | `¥15M/rep` |
| High value | bar の右端 | `¥30M/rep` |
| Impact range (¥M) | bar 内 or 右側 | `±¥175M` |
| **Tier (1-4)** | driver name 直下、small font | `Tier 3` |
| Source citation | tooltip / footnote | `Pavilion 2024 SaaS Survey` |

> **Tier 表示の意義**: tornado を見る reader が「この driver の estimate がどの程度 reliable か」を即座に判断できる。Tier 3 が top の場合は narrative で「pilot data 由来の高 uncertainty」と defense する必要。

### 3.3 Cumulative impact line (Pareto chart 風)

Coverage protocol (§2) を visual に統合するため、tornado に **cumulative % impact の 2 軸 line** を重ねる:

```
                ←  base case  →
                 ↓                     Cumulative %
         ┌────────────────────────┐  ┌─────┐
Sales p. │  ████████████████████  │  │  32%│  ← top 1: 32%
ACV      │      ███████████████   │  │  52%│  ← +20% = 52%
Churn    │        ██████████      │  │  66%│
NRR      │          ████████      │  │  78%│
Win rate │           ██████       │  │  86%│
S&M eff. │            █████       │  │  92%│  ← IC threshold 90% 達成
Pricing  │             ████       │  │  96%│
Other    │              ███       │  │ 100%│
         └────────────────────────┘  └─────┘
       -200      0       +200       +400
                                    ←─ 80% / 90% threshold line (red dashed)
```

#### 3.3.1 Threshold line の表示

- **80% line** (orange dashed): pitch 用 minimum
- **90% line** (red dashed): IC 用 minimum
- どこで cumulative line が threshold を cross するかが visible

これにより、**「IC 規律を満たす driver 数」** が一目で分かる (上記の例では top 6 で 92%、IC 90% threshold 満たす)。

### 3.4 Tornado layout の anti-pattern

| Anti-pattern | 何が悪いか | Fix |
|---|---|---|
| **Y 軸が impact 順でない** (alphabet 順 etc.) | 重要度が分からない | impact 順に再 sort |
| **Bar が % のみで ¥M 不在** | magnitude (金額の絶対値) が伝わらない | dual scale (¥M + %) |
| **Tier 表記なし** | reliability 判断不能 | driver name 直下に Tier 1-4 |
| **Cumulative line 不在** | coverage 規律 visual に出ない | Pareto line を追加 |
| **`Other` aggregation 不在** | long tail の存在が hidden | 最下段に `Other ±X%` |
| **Bar color が rainbow** | 重要度の visual hierarchy 崩壊 | Top 3 accent + rest muted gray |

### 3.5 Tornado を読むための reader-side check (IC partner 視点)

IC partner / senior reviewer は tornado を読む時、以下 5 点を **30 秒以内に check** する:

1. **Top 3 が thesis に整合するか** — pitch narrative で言及されている driver と一致するか
2. **Tier 4 が top に来ていないか** — もし来ていれば「founder estimate 一発勝負」のリスク
3. **Cumulative line が IC threshold (90%) を満たすか** — 満たさなければ coverage gap
4. **Bar の対称性 (low ↔ high)** — 極端に asymmetric なら base case が biased
5. **`Other` の比率** — 30% 超なら decomposition 不十分

これら 5 check は **§9 sanity_checks** で自動化 (S11 / S12 / S13)、analyst が忘れても発火する。

---

## 4. Scenario Analysis (Bull / Base / Bear)

### 4.1 3-scenario framework canonical

tornado が **single-variable** の sensitivity を示すのに対し、scenario analysis は **multi-variable で整合的な組合せ** を示す。これは IC で必ず聞かれる "what if" を準備する。

| Scenario | Driver setting (上位 3-5 driver) | Probability (合計 100%) |
|---|---|---|
| **Bull** | 上位 driver を高 (each Tier-based range 内 high) かつ **互いに整合** | 25-30% |
| **Base** | 全 driver を mid (most likely) | 40-50% |
| **Bear** | 上位 driver を低、互いに整合 | 25-30% |

#### 4.1.1 Probability の決め方

Probability は **subjective Bayesian estimate** であり、以下の guideline で配分する:

| 状況 | Bull | Base | Bear |
|---|---|---|---|
| Strong traction (Series B+, NRR > 110%, growth > 50%) | 30% | 50% | 20% |
| Standard (Series A, PMF 仮達成) | 25% | 45% | 30% |
| Early / risky (Pre-seed, pre-PMF) | 20% | 35% | 45% |
| 規制・technical risk 高 (Bio Phase II / hardware MOQ) | 15% | 35% | 50% |

> **規律**: 合計は **必ず 100%**、Bull > 30% / Bear < 20% は通常 over-optimistic と解釈、IC で challenge される。

### 4.2 Scenario consistency check (driver dependency)

scenario の最大 failure mode は **「driver dependency に整合しない fairy tale Bull」** である。例:

> ❌ **Bad Bull**:
> - ARR YoY +200% (very high)
> - Headcount +100 → +120 (moderate)
> - S&M cost +20% YoY (moderate)
> - Churn 5% (mid)
>
> 矛盾: ARR を 3x するのに headcount + S&M が moderate のままは physically 不可能。Sales rep が rep 当たり 3x productivity になるのは Tier 1 source なしには defensible でない。

> ✅ **Good Bull (整合)**:
> - ARR YoY +120% (high but realistic)
> - Headcount +100 → +180 (高、acquire と train が成立すれば)
> - S&M cost +90% YoY (高、acquisition spend を growth に比例)
> - Churn 4% (low、product 成熟仮定)

#### 4.2.1 Driver dependency DAG check

`22_driver_based_modeling §7` の driver DAG を活用し、Bull scenario が以下を満たすか **自動 check** する:

```python
def check_scenario_consistency(scenario: dict, dag: DriverDAG) -> list[dict]:
    """Scenario 内の driver setting が DAG dependency に整合するか check.

    Returns:
        list of inconsistency: [{"parent": str, "child": str, "violation": str}, ...]
    """
    violations = []
    for parent, children in dag.edges.items():
        parent_val = scenario.get(parent)
        for child in children:
            child_val = scenario.get(child)
            expected = dag.expected_relation(parent, child)  # "+" / "-" / None
            actual = sign(child_val - dag.base[child]) * sign(parent_val - dag.base[parent])
            if expected and actual != expected:
                violations.append({
                    "parent": parent,
                    "child": child,
                    "violation": f"{parent} {parent_val} expects {child} to move {expected}, "
                                 f"but scenario has {child} moving opposite",
                })
    return violations
```

> **使い方**: Bull scenario を組んだら必ず `check_scenario_consistency` を回し、violation 0 を確認。violation があれば scenario 再構築。

### 4.3 Scenario per-segment (multi-segment 対応)

multi-segment business (例: SaaS + Marketplace、地域別、product 別) では、segment 別に独立 scenario を組み合わせることが可能:

| Segment | Bull | Base | Bear |
|---|---|---|---|
| SaaS Enterprise (Japan) | ARR ¥800M | ARR ¥600M | ARR ¥400M |
| SaaS Enterprise (US) | ARR ¥1,500M | ARR ¥1,000M | ARR ¥600M |
| Marketplace (Japan) | GMV ¥3B / Take 8% | GMV ¥2B / Take 7% | GMV ¥1.2B / Take 6% |

#### 4.3.1 Blended scenario の組み方

全 segment が **同じ direction で動く** 必要は **ない**。例えば:

- **Realistic Bull**: SaaS US Bull + SaaS Japan Base + Marketplace Bear (US で大型受注、Japan は遅延、Marketplace は競争激化)
- **Realistic Bear**: SaaS US Base + SaaS Japan Bear + Marketplace Bear (Japan の sales chief 退職と marketplace 競合参入)

> **規律**: blended scenario は「全 segment Bull」ではなく、**「macro / 業界 trend が segment 別に独立に降りる」前提** で組むのが defensible。

詳細は `20_multi_segment_modeling` を参照。

### 4.4 Probability-weighted output (Expected Value)

3 scenario が確率付きで揃ったら、**expected output** を計算:

```
E[Output] = P(Bull) × Output_Bull + P(Base) × Output_Base + P(Bear) × Output_Bear
```

例:
- Bull: ¥1,500M (P = 30%)
- Base: ¥1,000M (P = 45%)
- Bear: ¥600M (P = 25%)
- E[Output] = 0.30 × 1,500 + 0.45 × 1,000 + 0.25 × 600 = 450 + 450 + 150 = **¥1,050M**

#### 4.4.1 Risk-adjusted valuation での活用

DCF NPV を probability-weighted で計算する場合:

```
Risk-adjusted EV = E[EV] = Σ P(scenario) × EV(scenario)
```

ただし、以下 2 つの **caveat**:

1. **Tail risk の non-linearity**: 極端な Bear (例: bankruptcy) では EV = 0 になり線形補完できない、別途 "ruin probability" として追跡
2. **Probability の subjective bias**: Bull に 50% 配分するのは典型 over-optimism、IC で challenge

詳細な valuation discount logic は `05_valuation_wacc` を canonical とする。本書は **scenario × probability の運用ルール** のみ規定。

### 4.5 Scenario presentation (IC memo 用 table)

IC memo の scenario page では、以下 standard table を採用:

```markdown
| Metric             | Bear (P=25%) | Base (P=45%) | Bull (P=30%) | E[V]  |
|--------------------|--------------|--------------|--------------|-------|
| ARR Y3 (¥M)        | 600          | 1,000        | 1,500        | 1,050 |
| Gross margin       | 65%          | 72%          | 78%          | 72.0% |
| EBITDA Y3 (¥M)     | -120         | 50           | 220          | 55    |
| Cash runway (mo)   | 9            | 18           | 28           | 19    |
| EV (¥M)            | 1,200        | 4,000        | 9,000        | 4,800 |
| Implied multiple   | 2.0x         | 4.0x         | 6.0x         | 4.6x  |

**Critical drivers per scenario**:
- Sales productivity: ¥10M / ¥18M / ¥28M per rep (Bull / Base / Bear)
- NRR: 95% / 105% / 115%
- Churn: 8% / 5% / 3%
- ACV: ¥1.5M / ¥2.0M / ¥2.5M
```

> **Glance test**: IC partner が table 1 枚を 30 秒見て「Bear で死ぬか / Bull で何が valuation を作るか」即座に分かる構造。

### 4.6 Scenario と tornado の統合 — 「coverage 内で scenario」

Scenario analysis は **tornado coverage で選ばれた top driver で組む** のが原則。これにより:

- Tornado: single-variable で全体 picture
- Scenario: multi-variable で integrated picture
- Both are coverage-protected (top-N driver が必ず含まれる)

> **規律**: scenario の Bull / Bear で振る driver は、tornado top-N (cumulative 80%) の中から選ぶ。tornado に表示されない driver で scenario を組むのは **inconsistent** であり IC で詰まる。


---

<!-- WAVE 2: §5 Threshold + §6 Implication Narrative -->

## 5. Threshold / Break-even Analysis

### 5.1 Critical thresholds — 4 種類の境界線

Threshold 分析は、感応度分析の最終段階で **「thesis が崩れる input 値はどこか」** を探索する。tornado / scenario が **range** を提示するのに対し、threshold は **point (境界値)** を提示する。IC partner が最も知りたいのは「いくらまで悪化したら kill か」である。

#### 5.1.1 Threshold の 4 タイプ

| Type | 定義 | 典型 metric | 計算手法 |
|---|---|---|---|
| **T1. Cash runway threshold** | 資金が枯渇する input 値 | Burn Multiple, Net Burn, Sales productivity | Linear (cash balance = 0) |
| **T2. Profitability threshold** | EBITDA / FCF が 0 になる input 値 | Gross margin, OpEx ratio, ARR growth | Linear (EBITDA = 0) |
| **T3. Valuation threshold** | EV が 投資 round の post-money を割る input 値 | NRR, ACV, Customer count | DCF / multiple based |
| **T4. Kill criteria threshold** | IC が pre-commit で「この値を割ったら exit」と決めた境界 | NPS, Churn, Pilot conversion | Pre-defined absolute |

> **規律**: T4 (kill criteria) は **investment 前に IC で合意** する。investment 後に「何 % 悪化したら諦める」を決めるのは遅すぎる。これは a16z / Sequoia の運用 best practice。

#### 5.1.2 Threshold table の standard format

| Output target | Driver | Threshold value | Current (Base) | Margin of safety | Tier source |
|---|---|---|---|---|---|
| Cash runway = 0 (24 mo 後) | Sales productivity | ¥9.5M / rep / yr | ¥18M / rep / yr | **47%** (margin) | Tier 2 (peer Series A SaaS) |
| EBITDA = 0 (Y3) | Gross margin | 58% | 72% | **19%** (margin) | Tier 1 (own data) |
| EV ≥ post-money (¥4B) | NRR | 98% | 105% | **7pp** (warning) | Tier 2 (peer benchmark) |
| Kill criteria | Pilot conversion | < 15% | 28% | **46%** (margin) | Tier 4 (IC consensus) |

> **読み方**: Margin of safety < 10% (T3 NRR の例) は **WARN**、< 5% は **FAIL** で IC で kill criteria を再検討。S13 sanity check で自動判定 (本書 §9)。

### 5.2 Solver-based threshold finding

線形に近い model なら手計算で求まるが、driver tree が深い場合は **数値求解 (numerical root finding)** が必要。Python `scipy.optimize.brentq` が標準。

#### 5.2.1 標準 implementation

```python
from scipy.optimize import brentq
from typing import Callable

def find_break_even(
    output_fn: Callable[[float], float],
    target: float,
    lo: float,
    hi: float,
    *,
    rtol: float = 1e-6,
    maxiter: int = 100,
) -> float:
    """
    Find driver value where output_fn(driver) == target (root finding).

    Args:
        output_fn: driver value を取り output (cash, EBITDA, EV) を返す closure
        target: 目標 output 値 (cash 0、EBITDA 0、EV = post-money 等)
        lo, hi: 探索 range の下限・上限 (driver value の単位で)
        rtol: 相対許容誤差
        maxiter: 最大反復

    Returns:
        threshold_value: driver の境界値 (output_fn(threshold) == target)。
        Margin of safety は別関数 `margin_of_safety()` を使用 (§5.3.2 で direction 考慮版)。

    Raises:
        ValueError: lo / hi で output_fn が同符号で root が括弧内に存在しない
    """
    f = lambda x: output_fn(x) - target
    f_lo, f_hi = f(lo), f(hi)
    if f_lo * f_hi > 0:
        raise ValueError(
            f"Root not bracketed: f({lo})={f_lo:.4g}, f({hi})={f_hi:.4g}. "
            "Widen lo/hi or check that target is reachable."
        )
    threshold = brentq(f, lo, hi, rtol=rtol, maxiter=maxiter)
    return threshold


def margin_of_safety(current: float, threshold: float) -> float:
    """
    Return margin of safety as a percentage.

    Positive = current is on the safe side; Negative = already in danger zone.
    Direction (driver-bigger-is-better vs. driver-smaller-is-better) は呼び出し側で考慮。
    """
    if current == 0:
        return float("inf") if threshold == 0 else float("-inf")
    return (current - threshold) / current * 100.0


# 使用例: sales productivity の cash runway threshold
def cash_at_month_24(productivity_per_rep: float) -> float:
    """driver value (¥M / rep / yr) を取り 24mo 後の cash balance を返す"""
    # ... model 内部 (本書 §22 driver tree 経由) ...
    rev = productivity_per_rep * num_reps * 2  # 2 yr
    cogs = rev * 0.30
    opex = base_opex * 2
    burn = cogs + opex - rev
    return cash_initial - burn

threshold = find_break_even(
    output_fn=cash_at_month_24,
    target=0.0,                  # cash = 0
    lo=1.0,                      # 探索下限 ¥1M / rep / yr
    hi=30.0,                     # 探索上限 ¥30M / rep / yr
)
mos = margin_of_safety(current=18.0, threshold=threshold)
print(f"Threshold = ¥{threshold:.1f}M / rep / yr, MoS = {mos:.1f}%")
```

#### 5.2.2 Solver が失敗する典型 case

| 失敗 pattern | 兆候 | 対処 |
|---|---|---|
| **Root not bracketed** | `f(lo) * f(hi) > 0` | lo / hi を広げる、または target が達成不可 (model の constraint) を疑う |
| **Multiple roots** | 同じ output に複数 driver 値が対応 (非線形 fixed cost step function 等) | 最も近い root を選び、IC memo に注記 |
| **Discontinuity** | step function (例: 一定 ARR で人員 +1) で root が定義されない | 連続化 (smoothing) するか、stepwise 列挙で最近接値を返す |
| **Convergence failure** | maxiter 到達 | rtol 緩和 (1e-4) か `bisect` に切替 |

> **実務 tip**: brentq は連続関数前提。財務 model は人員 step、debt covenant trigger 等で **不連続** が頻出するため、`output_fn` に対して smoothing (linear interpolation) を 1 段かますと安定。

### 5.3 Margin of safety の解釈規律

#### 5.3.1 MoS の解釈基準

| MoS | 判定 | IC memo での扱い |
|---|---|---|
| > 30% | **Strong** (緑) | "robust" として 1 行記載、討議不要 |
| 10–30% | **Moderate** (黄) | implication narrative §6 で discussion 対象 |
| 5–10% | **WARN** (橙) | mitigation plan を IC memo に必須 |
| < 5% | **FAIL** (赤) | thesis 再検討、investment hold 推奨 |
| Negative | **Already breached** (赤反転) | 即時 escalation、re-underwriting |

#### 5.3.2 Direction-aware MoS

driver には **「大きいほど safe」** と **「小さいほど safe」** の 2 種があり、MoS の符号を揃える:

```python
def margin_of_safety_directional(
    current: float,
    threshold: float,
    bigger_is_better: bool,
) -> float:
    """
    bigger_is_better=True: NRR, gross margin, productivity (上振れが safe)
    bigger_is_better=False: churn, CAC, OpEx ratio (下振れが safe)
    """
    if bigger_is_better:
        return (current - threshold) / current * 100.0
    return (threshold - current) / current * 100.0
```

例:
- NRR: current 105%, threshold 98% → MoS = (105 - 98) / 105 = **+6.7%** (bigger_is_better=True)
- Churn: current 5%, threshold 8% → MoS = (8 - 5) / 5 = **+60%** (bigger_is_better=False)

> **読み違い注意**: churn が「current 5% / threshold 8%」のとき「3pp の余裕」と書くと IC partner は「3% しか余裕がない」と誤読する。**% point ではなく % で書く**、または **絶対値で書く** ことを明示。

### 5.4 Threshold と scenario / tornado の統合

3 手法は **同じ driver universe** で動かすのが規律:

```
Tornado (driver universe, cumulative ≥80%)
   ↓ top driver を抽出
Scenario (Bull/Base/Bear、coverage 内 driver で integrated)
   ↓ Bear の延長線
Threshold (Bear がさらに崩れる境界、kill criteria)
```

> **規律**: tornado に登場しない driver で threshold を語るのは inconsistent。IC partner に「なぜこの driver で threshold だけ語るのか」と詰められる。

詳細 cell layout は `09_DCF § Sensitivity` を参照。本書は **手法統合の運用 rule** のみ規定。

---

## 6. Implication Narrative Templates (核心)

> **本書の核心 section**。tornado / scenario / threshold の数字を、IC memo の "Implications" sub-section に **そのまま inject 可能** な markdown narrative に変換する template 集。

### 6.1 Narrative の 5 要素 frame

全ての implication narrative は、以下 5 要素を **この順序** で記述する:

| # | 要素 | 役割 | 1 文目安 |
|---|---|---|---|
| **F. Finding** | 何を発見したか (定量) | 「tornado top driver は X、impact ¥A〜¥B」 | 1 sentence |
| **I. Implication** | だから何 (意思決定への含意) | 「thesis の defensibility は X に集中している」 | 1-2 sentence |
| **R. Reason** | なぜそうなるか (mechanics) | 「X は revenue formula で linear に効き、segment Y で 60% を占めるため」 | 1-2 sentence |
| **A. Action** | 何をすべきか (具体 action) | 「pre-investment の DD で X を追加検証、post-investment で X 月次 review」 | 1-2 sentence |
| **K. Risk** | 残る不確実性 (mitigation 後の residual) | 「DD でも X の中長期 trajectory は確認不可、mitigation は Y で限定的」 | 1 sentence |

> **記憶 mnemonic**: **F-I-R-A-K** (Finding / Implication / Reason / Action / Risk)。Damodaran の "narrative and numbers" を IC memo 用に operationalize したもの。

#### 6.1.1 5 要素を欠いた narrative の問題

| 欠落 | 症状 | IC review の指摘 |
|---|---|---|
| F のみ | 数字を貼っただけ、意思決定不能 | "So what?" |
| F+I のみ | 言いっぱなし、根拠不明 | "Why do you think so?" |
| F+I+R のみ | 評論で終わる、誰も動かない | "What do we do?" |
| F+I+R+A のみ | risk 隠蔽、over-confidence の印象 | "What can still go wrong?" |
| 5 要素 揃 | decision-grade | (no challenge) |

### 6.2 Per-driver narrative template (穴埋め式)

```markdown
**[Driver name]** (Tornado rank #__, impact ¥__M〜¥__M, Tier __ source)

- **Finding**: Sensitivity analysis で [Driver name] を [Low value]〜[High value] のレンジで振ったところ、[Output metric] は [Low output]〜[High output] (¥__M の幅) で動く。これは tornado top driver 中 #__ に位置し、cumulative impact の __% を占める。
- **Implication**: 本案件の [thesis 要素 (例: "ARR Y3 ¥1B 達成")] の達成可能性は、[Driver name] の trajectory に **集中的に依存** する。[Driver name] が [Low value] に振れた場合、[Output metric] は [Low output] となり、[追加含意 (例: "Series B raise の prerequisite を割る")]。
- **Reason**: [Driver name] は [revenue formula / unit economics / cost structure] で [linear / non-linear / step function] に効き、[該当 segment / customer cohort / product line] で [構成比 __%] を占めるため、small variation でも output に大きく伝播する。Tier __ source ([具体出典名 / URL] (観測時点 [YYYY-MM])) によると、peer は [peer benchmark value] が中央値であり、本案件 base case の [base value] は [上振れ / 中央 / 下振れ] に位置する。
- **Action**: Pre-investment の DD で [具体検証項目 (例: "trailing 12mo の [driver] cohort 別 actual の取得", "顧客 5 社への reference call で [driver] の sustainability を triangulate")] を追加実施。Post-investment では [ガバナンス mechanism (例: "monthly board pack に [driver] を組込", "Q1 / Q2 の [driver] が threshold ([threshold value]) を割った時点で kill criteria を発動")]。
- **Risk**: DD / governance を経ても、[残存リスク (例: "macro 起因の [driver] decline", "competitor の参入による [driver] への structural pressure")] は外生的に発生し得る。Mitigation は [限定的 mitigation 手段] に限られ、IC として [accept / hedge / decline] の判断を求める。
```

#### 6.2.1 Filled example — Series A SaaS, Sales productivity

```markdown
**Sales productivity (¥M / rep / yr)** (Tornado rank #1, impact ¥240M〜¥1,650M, Tier 2 source)

- **Finding**: Sensitivity analysis で sales productivity を ¥10M〜¥28M / rep / yr のレンジで振ったところ、ARR Y3 は ¥600M〜¥1,500M (¥900M の幅) で動く。これは tornado top driver 中 #1 に位置し、cumulative impact の 47% を占める。
- **Implication**: 本案件の "ARR Y3 ¥1,000M、Series B raise at ¥6B post" thesis の達成可能性は、sales productivity の trajectory に **集中的に依存** する。productivity が ¥10M に振れた場合、ARR Y3 は ¥600M となり、Series B raise の prerequisite (ARR ¥800M) を割る。
- **Reason**: Sales productivity は ARR formula (productivity × headcount × ramp) で linear に効き、enterprise segment で売上構成比 70% を占めるため、small variation でも output に大きく伝播する。Tier 2 source (Bessemer State of the Cloud 2024、ICONIQ Growth Top SaaS Benchmarks H1 2025、観測時点 2025-08) によると、peer Series A enterprise SaaS の median productivity は ¥18M / rep / yr であり、本案件 base case の ¥18M は中央に位置するが、Y2→Y3 で ramp 前提 (¥18M → ¥22M) が peer の +5% YoY 並みに依存する点が脆弱。
- **Action**: Pre-investment の DD で trailing 12mo の rep 別 productivity actual の取得 (上位 5 / 下位 5 で分散確認) と、顧客 5 社への reference call で sales motion の sustainability を triangulate を追加実施。Post-investment では monthly board pack に productivity を組込、Q1 productivity が ¥14M を割った時点で kill criteria (founder と再 alignment) を発動。
- **Risk**: DD / governance を経ても、AE の中途離職 1-2 名で productivity は短期に -20% 起こり得、且つ採用市場が逼迫している場合 mitigation は限定的。IC として "productivity ¥14M floor を accept する代わりに pre-money discount 10%" の hedge を提案。
```

> **使い方**: 各 top-N driver (cumulative 80% カバー、§2.2) について、上記 template を 1 つずつ埋める。IC memo の "Implications" section に **そのまま inject**。

### 6.3 Top-3 implications template (Executive Summary)

IC memo の executive summary には、top-3 driver の implication を **3 行 (1 driver = 1 sentence)** で記述する。bullet 中の "Action" のみ抽出:

```markdown
**Top 3 Implications (Executive Summary)**:

1. **Sales productivity が thesis の defensibility を支配する** (top driver, 47% of variance)。
   IC は productivity ¥14M を kill criteria として pre-commit、Q1 review で発動可否を決定。
2. **NRR は Series B valuation の floor を決める** (#2 driver, 23% of variance)。
   Post-investment の Q2 で NRR < 100% なら secondary deal 発動、founder と再 alignment。
3. **Pilot conversion は GTM thesis の reality check** (#3 driver, 18% of variance)。
   DD で過去 12 pilot の conversion actual を取得、Tier 1 source として IC memo に添付。
```

> **規律**: top-3 を超えると executive summary が膨れる。top-4 以降は §6.2 per-driver narrative の本文側に格納。

### 6.4 Decision frame (4 quadrant: Manageable × Controllable)

McKinsey の decision frame を sensitivity 結果の意思決定 mapping に流用。各 driver を以下 2 軸で plot:

```
                  Controllable (会社 / mgmt が動かせる)
                  ┌─────────────────────────┬─────────────────────────┐
                  │                         │                         │
                  │   Q1: Operate           │   Q2: Insure            │
                  │   (動かす経営の中心)     │   (保険 / hedge で対処)  │
   Manageable     │                         │                         │
   (規模が         │   例: sales productivity │   例: gross margin      │
    意思決定に     │       NRR, churn        │       (cost structure)  │
    ぶつかる)      ├─────────────────────────┼─────────────────────────┤
                  │                         │                         │
                  │   Q3: Watch             │   Q4: Accept            │
                  │   (受身で monitor)       │   (織り込み済として受容)  │
   Not manageable │                         │                         │
                  │   例: macro / FX         │   例: regulation         │
                  │       競合 entry        │       (long-tail)       │
                  └─────────────────────────┴─────────────────────────┘
                  Not controllable
```

#### 6.4.1 各 quadrant の運用 rule

| Quadrant | Rule | IC memo での扱い |
|---|---|---|
| **Q1 Operate** | Mgmt incentive と KPI に直結、monthly board review | "Operating priorities" section |
| **Q2 Insure** | 契約 / hedge / supplier 多様化で mitigation | "Risk mitigation" section |
| **Q3 Watch** | 月次 monitoring、threshold breach で escalation | "Monitoring metrics" section |
| **Q4 Accept** | IC 段階で織り込み済として明記、後で揉めない | "Accepted risks" section |

> **規律**: 全 top-N driver は **必ずどれか 1 quadrant に分類** する。「分類できない」driver は driver 定義が曖昧 → driver tree を §22 で再 decomposition。

### 6.5 Common implication patterns (mini-narratives library)

実務で頻出する 4 pattern を、ready-to-use な mini-narrative として提供。

#### 6.5.1 Pattern A: Single-driver 集中 (top driver > 40% of impact)

```markdown
**Pattern A — Single-driver concentration**

Sensitivity の variance の __% が **[Top driver name]** 1 つに集中している (top-2 以下は合計でも __% に留まる)。

これは:
- 良い面: **operational focus が明確**。IC partner と founder で「何を追えば成功か」が単純化。
- 悪い面: **single-point failure risk**。[top driver] が macro / 競合 / regulation で外生的に動くと thesis 全体が崩れる。

**Implication**: monthly board review の **agenda の 50% 以上を [top driver] に配分**、 quarterly に kill criteria 再評価を組み込む。

**Mitigation**: [top driver] を支える sub-driver (例: top driver が "sales productivity" なら "rep tenure / lead quality / pricing") に decomposition し、sub-driver で diversification を図る。
```

#### 6.5.2 Pattern B: Diversified (no driver > 20%)

```markdown
**Pattern B — Diversified driver portfolio**

Top driver も impact の __% に留まり、cumulative ≥80% に top __ driver が必要。これは "no single point of failure" を意味するが、同時に **mgmt attention の分散** を要求する。

**Implication**: weekly ops review で top __ driver を **同時 monitor**。1 driver が悪化しても他で compensate 可能だが、複数 driver が同時に悪化する **多重 stress** に弱い (本書 §8 multi-variable stress 参照)。

**Action**: pairwise correlation matrix (本書 §8.1) で driver 間相関を確認し、相関が高い driver pair (例: NRR と churn) を **1 つの compound driver** として再 decomposition するか、独立に monitor するかを決める。
```

#### 6.5.3 Pattern C: Top-down vs Bottom-up 乖離

```markdown
**Pattern C — Top-down vs Bottom-up divergence**

Top-down approach (TAM × share × monetization) では Y3 ARR が ¥__M、Bottom-up approach (rep × productivity × ramp) では ¥__M。乖離率 __ x。

これは:
- 乖離 < 1.5x: 健全 (model の internal consistency が高い)
- 乖離 1.5x-2x: WARN (driver tree の前提に矛盾、再検証推奨)
- 乖離 > 2x: **FAIL** (S14 sanity check)、thesis の reality check

**Implication**: 乖離が **どの中間 driver で発生しているか** を特定する。Top-down の "share" 前提が aggressive なのか、Bottom-up の "ramp" 前提が aggressive なのかで mitigation が違う。

**Action**: 中間 driver の reconciliation table (top-down 系 vs bottom-up 系で同じ leaf に降りる) を作成、最大乖離 driver を IC memo の "Open question" に明記。
```

> 関連: top-down vs bottom-up の reconciliation 詳細は `22_driver_based_modeling §4` を canonical。

#### 6.5.4 Pattern D: Threshold near base case (MoS < 10%)

```markdown
**Pattern D — Thin margin of safety**

[Output target] = 0 になる [Driver] threshold は [threshold value]、base case は [base value]、margin of safety は **[MoS]%** (< 10%)。

これは "model 上は base で問題ないが、small downward variation で thesis が崩れる" 状態。peer benchmark (Tier __ source) の median variation を見ると、本 driver の YoY 変動は std ±__% であり、**base case の MoS が peer の std の __ 倍以下** であれば実質的に "no margin" と判断。

**Implication**: base case 自体が **already aggressive**。Bull/Base/Bear 設計で Base が peer median ではなく **upper quartile** に置かれていないか再検証。

**Action**: Base case を peer median ベースに再 calibration し、thin MoS が解消するかを確認。解消しない場合は valuation discount (pre-money 10-20%) を提案。
```

### 6.6 Narrative の anti-pattern

| Anti-pattern | 例 | 問題 | 直し方 |
|---|---|---|---|
| **数字羅列** | "ARR は ¥600M〜¥1,500M で動きます" | F のみで I/R/A/K がない | F-I-R-A-K 全要素を埋める (§6.1) |
| **Vague implication** | "重要なので注意が必要です" | I が evergreen で具体性ゼロ | 「何が、誰の、どの意思決定に、どう効くか」を明記 |
| **Reason 不在** | "感応度が高いです (なぜならそうだから)" | R が "感応度が高いから感応度が高い" の循環 | mechanics (formula 上の効き方、構成比、benchmark 位置) を 1-2 sentence で説明 |
| **Action 抽象** | "今後注視します" | A が監視のみで具体 trigger なし | "Q1 の X が Y を割ったら kill" のように **threshold + action** で書く |
| **Risk 隠蔽** | (K を書かない) | over-confidence の印象、IC partner が信用しない | 残存 risk と mitigation の限界を明記 |
| **Implications を coupling せず羅列** | 各 driver で独立 narrative、全体 thesis との接続なし | reader が "結局どう判断すれば" 不明 | top-3 を §6.3 で executive summary に束ね、Q1-Q4 (§6.4) で全体 frame に位置付け |

---

<!-- WAVE 3: §7 Visual Storytelling + §8 Cross-driver Correlation -->

## 7. Visual Storytelling

### 7.1 IC memo "Sensitivity & Implications" page layout

IC memo の sensitivity page は **1 page (横長 A4 / Letter / 16:9)** に **4 pane** で構成。reader は 30 秒で全体把握、3 分で細部を読める設計。

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Page Title: Sensitivity & Implications — ARR Y3 driver decomposition    │
├──────────────────────────────────┬──────────────────────────────────────┤
│ Pane A: Tornado (top-N drivers)  │ Pane B: Scenario table (Bull/Base/   │
│                                   │           Bear) + E[V]               │
│  Productivity ████████████  47%  │                                      │
│  NRR          ██████   23%       │ Metric        Bear   Base   Bull  E[V] │
│  ACV          ████  18%          │ ARR Y3 (¥M)   600   1,000  1,500  1,050│
│  Churn        ██  10%            │ EBITDA Y3      -120   50    220     55 │
│  Headcount    █  6%               │ EV (¥M)      1,200  4,000  9,000  4,800│
│  ─ ─ ─ ─ ─ Pareto 80% line ─ ─ ─ │ Probability    25%   45%    30%       │
│  (cumulative ▲ 80% reached at #4)│                                      │
│                                   │ * Bull/Base/Bear: see §4.1 spec       │
├──────────────────────────────────┼──────────────────────────────────────┤
│ Pane C: Threshold table          │ Pane D: Top-3 Implications (text)    │
│                                   │                                      │
│ Output    Driver  Thr  Cur MoS    │ 1. Productivity が thesis を支配     │
│ Cash=0    Prod    9.5 18  47%     │    (47%, single-point risk)、         │
│ EBITDA=0  GM      58% 72% 19%     │    Q1 ¥14M floor を kill criteria に。│
│ EV<¥4B    NRR     98% 105% 7pp ⚠ │ 2. NRR は Series B floor を決める   │
│ Kill      Pilot   15% 28% 46%     │    (23%)、Q2 で <100% なら secondary。│
│                                   │ 3. ACV は GTM thesis (18%)、DD で過去│
│ ⚠ NRR < 10% MoS → discussion req │    12 pilot conversion を取得。       │
└──────────────────────────────────┴──────────────────────────────────────┘
```

> **layout 規律**: A (tornado) は左上、reader が最初に visual で「impact 大きい driver は何か」を捉える。B (scenario) で integrated picture、C (threshold) で境界、D (narrative) で意思決定。**4 pane が同じ driver universe** で動いているのが内部整合の証。

#### 7.1.1 1-pane fallback (deck slide 用)

IC memo ではなく pitch deck や investment teaser で 1 slide に圧縮する場合:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Slide title: Why Sales productivity is the key driver — and what we do  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐   1. **Finding**: tornado top driver,    │
│  │ Tornado: top-3 only      │      ¥240M〜¥1,650M of ARR Y3 variance   │
│  │  Productivity ████████   │                                           │
│  │  NRR          █████      │   2. **Action**:                          │
│  │  ACV          ████       │       • Pre: trailing 12mo cohort DD     │
│  │  (cumulative 88% by #3)  │       • Post: monthly board KPI         │
│  └──────────────────────────┘       • Q1 < ¥14M → kill criteria        │
│                                                                          │
│  Margin of safety: 47% (¥18M base vs. ¥9.5M cash-runway threshold)      │
└─────────────────────────────────────────────────────────────────────────┘
```

> **規律**: deck slide は **1 driver narrative** に絞る (top driver のみ)。複数 driver を 1 slide に詰めると glance test を通らない。

### 7.2 Color principle

#### 7.2.1 3 系統に絞る

| 用途 | 色 | 適用 |
|---|---|---|
| **Top-3 driver accent** | Primary `#008A80` | tornado bar の上位 3 本、scenario の Base column |
| **Threshold zone** | Success / Warning / Danger 3 段 (`#3F8F5E` / `#D6913D` / `#C04A4A`) | MoS の green > 30%, yellow 10-30%, red < 10% |
| **Scenario** | Bear: `#C04A4A` / Base: Ink `#2D332E` / Bull: Primary `#008A80` | scenario table の column header、line chart |

> **規律**: Accent (`#ECC85A`) は **1 page 1 か所** のみ (例: top driver の最重要 takeaway を囲む annotation box)。本文色には使わない。

#### 7.2.2 避ける色使い

- 純黒 `#0E0E08` を tornado bar に使わない (Ink `#2D332E` を使用)
- ネオン色 / 強グラデーション は IC memo の信頼性を損ねる
- 色だけで意味を伝えず、必ず **テキストラベルとアイコン** を添える (色覚多様性配慮)

### 7.3 Annotation の積極使用

「数字を見せる」だけでは IC partner は読み解かない。**takeaway 文字列を chart 上に直接 annotate** する。

#### 7.3.1 Tornado への annotation

```
  Productivity ████████████████  ¥240M ← ¥1,650M (47%, top driver)
                                          ▲ "single-point risk" ←(annotation)
  NRR          ██████   ¥130M ← ¥600M (23%)
  ACV          ████  ¥80M ← ¥430M (18%)
  ─────────── Pareto 80% line at #3 ───────────
  Churn        ██  ¥40M ← ¥200M (10%)
                ▲ "controllable via CS team" ←(annotation, Q1 quadrant)
  Headcount    █  ¥20M ← ¥120M (6%)
```

#### 7.3.2 Scenario chart への annotation

EV (¥M) の Bull/Base/Bear line chart で:

```
EV (¥M)
9,000 ┤ ●─Bull
        │   "ARR ¥1.5B + multiple 6x assumes top-quartile peer"
4,000 ┤ ●─Base
        │   "Series B at ¥6B prerequisite met"
1,200 ┤ ●─Bear
          "Series B raise blocked, secondary or down-round" ←(critical annotation)
```

#### 7.3.3 Annotation の書き方 rule

| Rule | 良い例 | 悪い例 |
|---|---|---|
| **動詞で書く** | "blocks Series B raise" | "Series B related" |
| **主語を明示** | "founder dilution +12pp" | "dilution increases" |
| **数字を埋め込む** | "MoS 7pp, < 10% threshold" | "low margin of safety" |
| **行動と結びつける** | "Q1 trigger for kill criteria" | "monitor closely" |

> **規律**: annotation は 1 chart に **3-5 個まで**。多すぎると noise。最重要 takeaway のみ。

### 7.4 Chart の format

#### 7.4.1 Tornado specific

- Bar 横並び (horizontal)、driver name は **左寄せ**、impact value は bar の右端外
- Sort: top → bottom で impact 降順 (絶対値 ¥M)
- Pareto cumulative line を右軸に重ね、80% で水平 dashed line
- Y 軸 (driver name) は文字を切らない (省略時は tooltip)

#### 7.4.2 Scenario specific

- Bull/Base/Bear の 3 column を Bear → Base → Bull の順 (左から悪→良)
- Probability を column header の下に italic で
- E[V] は最右 column、太字
- Footnote で "scenario の driver assumptions は §4.1 spec 参照"

#### 7.4.3 Threshold specific

- Output / Driver / Threshold / Current / MoS / Tier source の 6 column
- MoS の cell は色付き (green / yellow / red、§7.2.1 準拠)
- WARN / FAIL は ⚠ アイコン併記、scaled value (例: "7pp ⚠")

### 7.5 Page hierarchy (IC memo full document 内)

IC memo 全体での "Sensitivity & Implications" page の位置:

```
1. Executive Summary (top-3 implications inline、§6.3)
2. Investment Thesis
3. Market & Competition
4. Financial Model Highlights
5. **Sensitivity & Implications** ← 本書の対象 (4 pane layout、§7.1)
6. Risks & Mitigation (§6.4 4-quadrant decision frame に連動)
7. Recommendation (top-3 action から抽出)
8. Appendix (full sensitivity tables、Tier source list)
```

> **規律**: §5 page は **§4 model highlights の直後** に置く。reader は model の数字を見たあとで「robustness」を確認したい flow。

---

## 8. Cross-driver Correlation & Multi-variable Stress

### 8.1 Pairwise correlation matrix

Tornado の前提は **「各 driver は独立に動く」**。実際は driver 間に correlation があり、同時に低下する場合の output impact は単純合算より大きい / 小さい。

#### 8.1.1 Pairwise stress の definition

「2 driver を同時に Low に振った時の output」と「single tornado の和」の差を計算:

```
Interaction(i, j) = Output(L_i, L_j) - [Base + (Output(L_i) - Base) + (Output(L_j) - Base)]
```

- Interaction > 0 (positive): 同時 Low で output が **追加で押し上げ** (例: cost と revenue 両方 down で利益率が偶然守られる)
- Interaction < 0 (negative): 同時 Low で output が **追加で押し下げ** (例: revenue 減と CAC 増で gross margin と marketing efficiency が同時悪化)

#### 8.1.2 Python implementation

```python
import pandas as pd
from typing import Callable, Dict, Sequence

def pairwise_stress(
    drivers: Dict[str, Dict[str, float]],
    output_fn: Callable[[Dict[str, float]], float],
) -> pd.DataFrame:
    """
    Compute pairwise stress and interaction terms for each (driver_i, driver_j) pair.

    Args:
        drivers: {name: {"low": x, "base": y, "high": z}}
        output_fn: dict of driver values を取り output (scalar) を返す

    Returns:
        DataFrame indexed by (driver_i, driver_j) with columns:
            - output_lo_lo: Low-Low の output
            - additive_estimate: tornado-based additive prediction
            - interaction: output_lo_lo - additive_estimate
            - sign: "+" / "-" / "≈0"
    """
    base = {name: vals["base"] for name, vals in drivers.items()}
    output_base = output_fn(base)

    # Single-driver low impacts
    impacts = {}
    for name, vals in drivers.items():
        scenario = base.copy()
        scenario[name] = vals["low"]
        impacts[name] = output_fn(scenario) - output_base

    # Pairwise low-low
    rows = []
    names = list(drivers.keys())
    for i, n_i in enumerate(names):
        for n_j in names[i + 1:]:
            scenario = base.copy()
            scenario[n_i] = drivers[n_i]["low"]
            scenario[n_j] = drivers[n_j]["low"]
            output_lo_lo = output_fn(scenario)
            additive = output_base + impacts[n_i] + impacts[n_j]
            interaction = output_lo_lo - additive
            sign = (
                "+" if interaction > abs(output_base) * 0.01
                else "-" if interaction < -abs(output_base) * 0.01
                else "≈0"
            )
            rows.append(
                {
                    "driver_i": n_i,
                    "driver_j": n_j,
                    "output_lo_lo": output_lo_lo,
                    "additive_estimate": additive,
                    "interaction": interaction,
                    "sign": sign,
                }
            )
    return pd.DataFrame(rows).sort_values("interaction")


# 使用例
drivers = {
    "productivity": {"low": 10.0, "base": 18.0, "high": 28.0},  # ¥M / rep / yr
    "nrr":          {"low": 0.95, "base": 1.05, "high": 1.15},
    "acv":          {"low": 1.5,  "base": 2.0,  "high": 2.5},   # ¥M
    "churn":        {"low": 0.08, "base": 0.05, "high": 0.03},
}

def arr_y3(d: Dict[str, float]) -> float:
    # 簡略版 model
    return d["productivity"] * 50 * d["acv"] * d["nrr"] * (1 - d["churn"])

result = pairwise_stress(drivers, arr_y3)
print(result.to_string(index=False))
```

#### 8.1.3 Interpretation

| Interaction sign | Pattern | IC memo での扱い |
|---|---|---|
| **Negative (--)** | 同時 Low で追加 -% | "compound risk" として明記、doomsday scenario (§8.2) で discussion |
| **Positive (+)** | 同時 Low で追加 +% (rare) | "natural hedge" として記録、ただし誤解されやすいので注釈 |
| **≈0** | 線形性が高い (driver が独立) | tornado の前提が成り立つ、特記不要 |

> **規律**: Negative interaction が `|output_base|` の 5% を超える pair は IC memo に必須記載。`(productivity, churn)` のように "両方の悪化が複利で効く" pair が典型。

### 8.2 "Doomsday" scenario — top-3 同時 Low

Bear scenario を超える extreme stress test。**top-3 driver を全て Low に同時に振る** (cumulative impact の 80%+ を一気に Low 側で realize)。

#### 8.2.1 設計 rule

| Element | 設計 |
|---|---|
| **Driver 選定** | tornado top-3 (cumulative 80% カバーする driver の中から) |
| **値の選び方** | 各 driver の Low 値 (`§4.1` で peer p25 や stress 値) |
| **Probability** | < 5% (Bear の 25-30% よりずっと低い、tail risk) |
| **目的** | 「ruin probability」の特定、kill criteria の妥当性 |

#### 8.2.2 出力例

```markdown
**Doomsday scenario** (P < 5%):

- Productivity: ¥10M / rep / yr (low)
- NRR: 90% (low、Bear の 95% を更に下げ)
- Pilot conversion: 12% (low、Bear の 18% を更に下げ)
- Output: ARR Y3 = ¥350M (Base ¥1,000M の **35%**)
- EBITDA Y3 = -¥320M、Cash runway = 6 mo
- **Interpretation**: P < 5% だが起きた場合 cash 枯渇は 6 mo で確定。
  Mitigation: bridge round の covenant を investment letter に組込、また
  insurance として founder secondary を pre-money の 5% で確保する option を IC で承認。
```

> **規律**: Doomsday は **「もし起きたら何が起きるか」** を文書化することが目的。確率が低いから無視ではなく、確率が低いからこそ pre-defined response が要る。

### 8.3 "Triple-point" scenario (3 driver × 3 値 = 27 cell)

3 driver を Low/Base/High の 3 段で全 combination を探索:

```
                  Driver C = Low      Driver C = Base     Driver C = High
                  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
A=L, B=L: 350     │ A=L, B=B: 480   │ │ A=L, B=H: 620   │ │
A=B, B=L: 580     │ A=B, B=B: 1,000 │ │ A=B, B=H: 1,250 │ │
A=H, B=L: 820     │ A=H, B=B: 1,400 │ │ A=H, B=H: 1,750 │ │
                  └─────────────────┘ └─────────────────┘ └─────────────────┘
                  (1 sheet × 3 sheets = 27 cells)
```

3 driver で **27 cell** (3³)、4 driver なら 81 cell で読みづらくなるため、triple-point は **3 driver 限定**。それ以上は Monte Carlo (本書の scope 外、`05_valuation_wacc` 参照)。

#### 8.3.1 Triple-point の用途

- Bull/Base/Bear の 3 scenario (1 cell ずつ) では覆えない **中間 path** を可視化
- IC partner の "what if A is bad but B and C are good?" 質問に直接回答
- Heatmap で出力すると pattern が視覚的に明瞭

#### 8.3.2 Heatmap layout

```
EV (¥M)              Driver C = Low (Pilot conv low)
                  Productivity Low  Base  High
NRR Low           1,200        1,800  2,600
NRR Base          1,800        2,800  4,000
NRR High          2,400        3,800  5,400

(同 layout × 3 panels for C = Base / High)
```

色分け:
- 緑 (`#3F8F5E`): EV ≥ post-money (¥4B)
- 黄 (`#D6913D`): EV ¥2-4B
- 赤 (`#C04A4A`): EV < ¥2B (Series B raise blocked)

### 8.4 Monte Carlo との関係 (本書 scope 外の boundary)

Monte Carlo simulation (driver の確率分布から N 回 sampling、output 分布を得る) は本書では扱わない:

- Triple-point: deterministic、IC partner が **手で読める** 27 cell
- Monte Carlo: probabilistic、output 分布の percentile (P10 / P50 / P90)

> **使い分け**: IC memo 用には Triple-point が standard。Monte Carlo は valuation page (`05_valuation_wacc`) で DCF NPV の分布を出す用途に限定。

### 8.5 Cross-driver の sanity check 連携

本 section は本書 §9 の S12 Concentration check と連携:

- S12: top driver が impact の 40% 超 → Pattern A (single concentration、§6.5.1) として narrative
- 本 §8: pairwise interaction が 5% 超で negative → Pattern A の **更に深い掘り下げ** が必要

> **規律**: §8 (cross-driver) と §6.5 (pattern library) は **必ず双方向 cross-link** する。Pattern A の narrative に "doomsday scenario で Y mo runway" を追記、doomsday narrative に "Pattern A 集中型として §6.5.1 参照" を追記。

---

<!-- WAVE 4: §9 Quantitative checks + §10 Mini Cases -->

## 9. Quantitative checks (sanity_checks 統合)

`_self_review_protocol.md §8` の自動 sanity_checks に、本書から **S11-S14 の 4 項目** を inject する。本 section は各 check の定義、判定 rule、Python implementation、failure 時の対処を canonical とする。

### 9.1 Check S11 — Coverage check (cumulative ≥ 80%)

#### 9.1.1 定義

Tornado top-N driver の cumulative impact share が **80% 以上** を達成しているか。本書 §2.6 で sanity check 化。

| Stage | 必要 cumulative | 必要 driver 数の典型 |
|---|---|---|
| Pre-Seed | ≥ 70% | top-3 |
| Seed | ≥ 75% | top-3 〜 5 |
| Series A | ≥ 80% | top-5 〜 7 |
| Series B+ / Pre-IPO | ≥ 85% (IC memo: 90%) | top-7 〜 10 |

#### 9.1.2 Python implementation

```python
from typing import Sequence

def check_coverage(impacts: Sequence[float], stage: str) -> dict:
    """
    Args:
        impacts: tornado driver impact 絶対値 (¥M)、降順 sort 済
        stage: "pre_seed" / "seed" / "series_a" / "series_b_plus"

    Returns:
        {"passed": bool, "cumulative": float, "n_drivers": int, "threshold": float}
    """
    thresholds = {
        "pre_seed": 0.70,
        "seed": 0.75,
        "series_a": 0.80,
        "series_b_plus": 0.85,
    }
    threshold = thresholds.get(stage, 0.80)
    total = sum(impacts)
    if total == 0:
        return {"passed": False, "cumulative": 0.0, "n_drivers": 0, "threshold": threshold}

    cumulative = 0.0
    for n, imp in enumerate(impacts, 1):
        cumulative += imp / total
        if cumulative >= threshold:
            return {"passed": True, "cumulative": cumulative, "n_drivers": n, "threshold": threshold}
    return {"passed": False, "cumulative": cumulative, "n_drivers": len(impacts), "threshold": threshold}
```

#### 9.1.3 Failure 時の対処

S11 failure (cumulative < threshold) の典型原因と対処:

| 原因 | 兆候 | 対処 |
|---|---|---|
| Driver tree が浅い | top-3 で 50% 程度しかない | `22_driver_based_modeling §3` で leaf を細分化 |
| Long-tail 過多 | 10+ driver が小さく分散 | sub-driver を bundle (cohort 等で集約) |
| Range 設定が均質すぎ | 全 driver が ±20% で振られている | per-driver の Tier 1-4 source で realistic range を再設定 |

### 9.2 Check S12 — Single-driver concentration

#### 9.2.1 定義

Top driver の impact share が **40% を超える** 場合 WARN、**60% を超える** 場合 FAIL。Pattern A (§6.5.1) として narrative 必須。

| Top driver share | 判定 | 対処 |
|---|---|---|
| ≤ 40% | OK | 特記不要 |
| 40-60% | **WARN** | Pattern A narrative を IC memo に必須記載 |
| > 60% | **FAIL** | sub-driver decomposition で分散、または single-point risk として thesis 再検討 |

#### 9.2.2 Python implementation

```python
def check_concentration(impacts: Sequence[float]) -> dict:
    """
    Top-1 driver の share と判定を返す。

    Returns:
        {"passed": bool, "top_share": float, "level": "OK" / "WARN" / "FAIL"}
    """
    total = sum(impacts)
    if total == 0:
        return {"passed": False, "top_share": 0.0, "level": "FAIL"}
    top_share = impacts[0] / total
    if top_share > 0.60:
        level = "FAIL"
    elif top_share > 0.40:
        level = "WARN"
    else:
        level = "OK"
    return {"passed": level != "FAIL", "top_share": top_share, "level": level}
```

#### 9.2.3 注意

S12 は single-point risk の早期発見が目的。FAIL でも投資不可ではなく、**「この single point を IC で accept するか」** の意思決定 trigger。a16z / Sequoia の典型 SaaS 投資では top driver が 50%+ を占めることは珍しくない。

### 9.3 Check S13 — Threshold margin of safety

#### 9.3.1 定義

各 critical threshold (cash runway / EBITDA / valuation) について、margin of safety (MoS) が **10% 以下** で WARN、**5% 以下** で FAIL。本書 §5.3 で運用ルール定義。

#### 9.3.2 Python implementation

```python
from typing import Iterable

def check_threshold_mos(thresholds: Iterable[dict]) -> dict:
    """
    Args:
        thresholds: [
            {"name": "cash_zero", "current": 18.0, "threshold": 9.5, "bigger_is_better": True},
            {"name": "ebitda_zero", "current": 0.72, "threshold": 0.58, "bigger_is_better": True},
            {"name": "ev_post_money", "current": 1.05, "threshold": 0.98, "bigger_is_better": True},
        ]

    Returns:
        {"passed": bool, "issues": [{"name": ..., "mos": ..., "level": ...}, ...]}
    """
    issues = []
    for t in thresholds:
        cur, thr = t["current"], t["threshold"]
        bib = t.get("bigger_is_better", True)
        if cur == 0:
            mos = float("inf") if thr == 0 else float("-inf")
        elif bib:
            mos = (cur - thr) / cur * 100.0
        else:
            mos = (thr - cur) / cur * 100.0

        if mos < 5:
            level = "FAIL"
        elif mos < 10:
            level = "WARN"
        else:
            level = "OK"
        if level != "OK":
            issues.append({"name": t["name"], "mos": mos, "level": level})

    return {"passed": all(i["level"] != "FAIL" for i in issues), "issues": issues}
```

#### 9.3.3 Failure 時の対処

| Level | 対処 |
|---|---|
| WARN (5-10%) | Pattern D narrative (§6.5.4) を IC memo に inject、mitigation を明記 |
| FAIL (< 5%) | base case を peer median ベースに再 calibration、または valuation discount を IC で議論 |
| Negative MoS | 即時 escalation、re-underwriting または investment hold |

### 9.4 Check S14 — Top-down vs Bottom-up reconciliation

#### 9.4.1 定義

Top-down (TAM × share × monetization) と Bottom-up (rep × productivity × ramp など) の同じ output target (例: ARR Y3) の **乖離率** が:

- < 1.5x: OK
- 1.5x - 2x: WARN
- > 2x: FAIL

詳細は `22_driver_based_modeling §4` を canonical だが、本 check は sensitivity の前提整合として S14 で再評価。

#### 9.4.2 Python implementation

```python
def check_top_down_bottom_up(td: float, bu: float) -> dict:
    """
    Args:
        td: top-down で得た output 値
        bu: bottom-up で得た output 値

    Returns:
        {"passed": bool, "ratio": float, "level": "OK" / "WARN" / "FAIL"}
    """
    if td == 0 or bu == 0:
        return {"passed": False, "ratio": float("inf"), "level": "FAIL"}
    ratio = max(td, bu) / min(td, bu)
    if ratio > 2.0:
        level = "FAIL"
    elif ratio > 1.5:
        level = "WARN"
    else:
        level = "OK"
    return {"passed": level != "FAIL", "ratio": ratio, "level": level}
```

#### 9.4.3 Failure 時の対処

S14 FAIL の場合、Pattern C narrative (§6.5.3) を IC memo に inject。reconciliation table を作成し、最大乖離 driver を "Open question" に明記。

### 9.5 4 check の統合実行

```python
def run_sensitivity_sanity_checks(
    impacts: Sequence[float],
    stage: str,
    thresholds: Iterable[dict],
    td_value: float,
    bu_value: float,
) -> dict:
    """
    本書 §9 の S11-S14 を 1 関数で実行。

    Returns:
        {"S11": {...}, "S12": {...}, "S13": {...}, "S14": {...}, "all_passed": bool}
    """
    s11 = check_coverage(impacts, stage)
    s12 = check_concentration(impacts)
    s13 = check_threshold_mos(thresholds)
    s14 = check_top_down_bottom_up(td_value, bu_value)
    return {
        "S11": s11,
        "S12": s12,
        "S13": s13,
        "S14": s14,
        "all_passed": all([s11["passed"], s12["passed"], s13["passed"], s14["passed"]]),
    }
```

> **規律**: `build_model.py` から本関数を呼び出し、結果を IC memo の "Self-review" appendix に **必ず添付**。1 つでも FAIL があれば IC submission 前に対処。

---

## 10. Mini Cases (実例)

実務で頻出する 7 case を例示。各 case は **Stage / 業態 / driver / tornado 特徴 / scenario / threshold / IC memo narrative の 1 行 takeaway** を含む。

### 10.1 Case 1 — Series A SaaS (sales productivity dominant)

| 項目 | 内容 |
|---|---|
| **Stage** | Series A |
| **業態** | B2B SaaS (enterprise、ACV ¥2M) |
| **目標 output** | ARR Y3 = ¥1,000M |
| **Tornado top-3** | 1. Sales productivity (47%) 2. NRR (23%) 3. ACV (18%) |
| **Pattern** | A (single-driver concentration、productivity 47%) |
| **Scenario** | Bear ¥600M (P 25%) / Base ¥1,000M (P 45%) / Bull ¥1,500M (P 30%) |
| **Threshold** | Cash=0 で productivity ¥9.5M、MoS 47% (緑) |
| **Kill criteria** | Q1 productivity < ¥14M で escalation |
| **Narrative takeaway** | "Productivity が thesis を支配。Q1 ¥14M floor を kill criteria に pre-commit" |

### 10.2 Case 2 — Marketplace (take rate vs GMV growth)

| 項目 | 内容 |
|---|---|
| **Stage** | Series B |
| **業態** | C2C Marketplace (Mercari 系) |
| **目標 output** | Revenue Y3 = $200M |
| **Tornado top-3** | 1. GMV growth (35%) 2. Take rate (30%) 3. Buyer retention (15%) |
| **Pattern** | B (diversified、no driver > 40%) |
| **Scenario** | Bear $120M (P 25%) / Base $200M (P 50%) / Bull $300M (P 25%) |
| **Threshold** | EBITDA=0 で take rate 8.5%、Base 10.5%、MoS 19% (黄) |
| **Kill criteria** | Q2 buyer retention M3 が 35% を割ったら escalation |
| **Narrative takeaway** | "Take rate と GMV growth は trade-off (rate 引上げで GMV 減)。両方を同時に守る operational discipline が thesis core" |

### 10.3 Case 3 — Bio (Phase III probability)

| 項目 | 内容 |
|---|---|
| **Stage** | Pre-IPO (clinical Phase III 直前) |
| **業態** | バイオ pharma |
| **目標 output** | Risk-adjusted NPV ($M) |
| **Tornado top-3** | 1. Phase III success P (50%) 2. Peak sales (20%) 3. Time to peak (15%) |
| **Pattern** | A (PoS が dominant、structural single-point) |
| **Scenario** | Bear $200M (P 60%、Phase III fail) / Base $1,500M (P 30%) / Bull $4,000M (P 10%) |
| **Threshold** | NPV ≥ 0 で Phase III PoS ≥ 25%、現時点 35%、MoS 29% (緑) |
| **Kill criteria** | Phase IIb 中間結果が pre-defined endpoint を miss → 即時開発中止検討 |
| **Narrative takeaway** | "Bio は本質的に binary (Phase III pass/fail)。NPV 計算より option pricing (real options) で再評価推奨" |

> **規律**: Bio で probability-weighted NPV は misleading になりやすい (失敗時 EV ≈ 0 で線形補完不可)。`05_valuation_wacc` の binary scenario discipline を canonical。

### 10.4 Case 4 — D2C (paid CAC by channel)

| 項目 | 内容 |
|---|---|
| **Stage** | Series A |
| **業態** | D2C cosmetics (Shopify-based) |
| **目標 output** | EBITDA Y3 (¥M) |
| **Tornado top-3** | 1. Paid CAC (Meta) (38%) 2. AOV (22%) 3. Repeat purchase rate (18%) |
| **Pattern** | A (CAC 集中) + cross-driver correlation (CAC と LTV) |
| **Scenario** | Bear -¥200M (P 30%) / Base ¥80M (P 50%) / Bull ¥350M (P 20%) |
| **Threshold** | EBITDA=0 で paid CAC ≤ ¥3,200、Base ¥2,400、MoS 25% (緑) |
| **Kill criteria** | Meta CAC が ¥3,000 を 3mo 連続超え → channel mix 再構築 |
| **Narrative takeaway** | "Paid CAC は Meta algo / iOS ATT / 競合入札で外生 (Q3 quadrant: Watch)。channel diversification が defensibility の鍵" |

### 10.5 Case 5 — AI startup (token cost decline)

| 項目 | 内容 |
|---|---|
| **Stage** | Seed / Series A |
| **業態** | AI vertical SaaS (LLM API 依存) |
| **目標 output** | Gross margin Y3 (%) |
| **Tornado top-3** | 1. Token cost decline rate (45%) 2. ACV (25%) 3. NRR (12%) |
| **Pattern** | A (token cost 集中) + macro-dependency |
| **Scenario** | Bear 35% (P 30%、token cost 横ばい) / Base 65% (P 50%) / Bull 80% (P 20%) |
| **Threshold** | GM ≥ 70% で token cost が yearly -40%、Base -50%、MoS 20% (緑) |
| **Kill criteria** | Q4 token cost が前年比 -30% 未満 (decline 鈍化) → vertical product 戦略再考 |
| **Narrative takeaway** | "Token cost decline は外生的 (foundation lab 依存)、Q3 quadrant: Watch。OpenAI / Anthropic / Google の roadmap を quarterly review" |

### 10.6 Case 6 — 失敗事例 (sensitivity 不在 IC で投資失敗)

| 項目 | 内容 |
|---|---|
| **Stage** | Series B (失敗事例) |
| **業態** | Vertical SaaS (logistics) |
| **目標 output** | ARR Y3 (¥M) |
| **失敗 pattern** | tornado なし、Bull case のみ提示、threshold 未計算 |
| **発生事象** | 投資後 Y2 で大型顧客 (ARR の 30%) が解約、ARR は base 比 -45% |
| **Post-mortem 発見** | 「customer concentration」が driver universe に存在せず、感応度未測定 |
| **教訓** | top-N coverage 規律 (§2.2) を pre-investment で必須適用していれば customer concentration が tornado top-3 に登場し、IC で kill criteria 設定可能だった |
| **Narrative takeaway** | "Sensitivity 不在の IC は『投資前に Bull case を信じ、投資後に Bear case を発見する』pattern。本書 §2 coverage protocol が absolute prerequisite" |

> **規律**: 失敗事例の post-mortem は IC の **knowledge asset**。本 case を template として、post-investment monitoring の sensitivity 再評価 cadence (semi-annually) を skill 全体に inject。

### 10.7 Case 7 — Fintech (credit loss correlation)

| 項目 | 内容 |
|---|---|
| **Stage** | Series B |
| **業態** | 消費者金融 (BNPL / personal loan) |
| **目標 output** | Net interest margin (NIM) - cost of risk |
| **Tornado top-3 (independent)** | 1. NIM (38%) 2. Cost of risk (delinquency) (32%) 3. Funding cost (12%) |
| **Cross-driver correlation** | NIM low + Cost of risk high が同時発生 (景気悪化で borrower quality 低下 + repayment 遅延) |
| **Pattern** | Cross-driver compound (Pairwise interaction が -8% で large negative) |
| **Scenario** | Bear -2% (P 30%、recession) / Base 4% (P 45%) / Bull 7% (P 25%) |
| **Threshold** | Net margin ≥ 0% で cost of risk ≤ 6.5%、Base 4.2%、MoS 35% (緑) |
| **Doomsday** | NIM low + Cost of risk high 同時発生で net margin -5%、capital impairment risk |
| **Narrative takeaway** | "Fintech は driver 独立前提が崩れる典型。Pairwise stress (§8.1) と doomsday scenario (§8.2) を IC memo に必須添付" |

### 10.8 Case 比較サマリ

| Case | Pattern | Top driver share | MoS (critical threshold) | Kill criteria 設計 |
|---|---|---|---|---|
| 1 SaaS | A 集中 | 47% | 47% (緑) | Q1 productivity floor |
| 2 Marketplace | B 分散 | 35% | 19% (黄) | Q2 retention M3 |
| 3 Bio | A 構造的 | 50% | 29% (緑) | Phase IIb endpoint |
| 4 D2C | A + correlation | 38% | 25% (緑) | Meta CAC 3mo |
| 5 AI | A + macro | 45% | 20% (緑) | Token cost rate |
| 6 失敗事例 | (sensitivity 不在) | N/A | N/A | (設計なし) |
| 7 Fintech | Cross-driver compound | 38% | 35% (緑) | Cost of risk 累積 |

> **読み方**: Case 6 は他の case と比べて **どの欄も埋まっていない**。これが「sensitivity 不在 IC」の symptom。本書を適用していれば全 case で 6 column が埋まる。

---

<!-- WAVE 5: §11-§13 (Anti-patterns / Cross-link / Revision history) -->

## 11. Anti-patterns

実務で IC review が止まる典型 anti-pattern。本書を skill として運用する際は **以下 6 pattern を check list として `_self_review_protocol §8` に統合**。

### 11.1 Anti-pattern 1 — 1-2 driver だけの tornado

| Pattern | "tornado に top-2 driver しか出ていない" |
|---|---|
| 症状 | ARR sensitivity が "ACV と headcount だけ" で示されている、cumulative impact 60% 程度 |
| 原因 | driver tree を decomposition せず、思いついた driver を並べただけ |
| 結果 | NRR / churn / pilot conversion 等の dominant driver を取りこぼし、IC partner が "what about NRR?" で詰まる |
| 直し方 | §2.2 top-N auto-detection で cumulative ≥ 80% を必ず満たす |

### 11.2 Anti-pattern 2 — Pretty chart no narrative

| Pattern | "tornado / scenario chart は美しいが、Implications section が空 / 1 行" |
|---|---|
| 症状 | 「Sales productivity の感応度が高いです」のみで終わる |
| 原因 | F-I-R-A-K のうち F だけ書いて I/R/A/K がない (§6.1) |
| 結果 | reader は「だから何」が不明、意思決定 input にならない |
| 直し方 | §6.2 per-driver template を top-N driver 全てに適用、§6.3 top-3 を executive summary に inject |

### 11.3 Anti-pattern 3 — Single scenario only

| Pattern | "Bull case しか提示されていない (Bear / Base 不在)" |
|---|---|
| 症状 | "ARR Y3 = ¥1,500M、上場後 ¥10B 評価" と Bull のみ提示 |
| 原因 | founder / sponsor partner が thesis を売り込みたい motivation で Bear を意図的に省略 |
| 結果 | post-investment で Bear 起こると pre-defined response がなく、kill criteria が間に合わない |
| 直し方 | §4.1 3-scenario framework canonical (Bull/Base/Bear が prerequisite)、Bear 不在で IC submission 拒否 |

### 11.4 Anti-pattern 4 — Range arbitrary (Tier 1-4 source なし)

| Pattern | "Low/High range が ±20% で機械的、根拠なし" |
|---|---|
| 症状 | 全 driver が Base から ±20% で振られている、Tier 1-4 source 記載なし |
| 原因 | Excel の data table で機械的に変動、peer benchmark や own data の検証を省略 |
| 結果 | range の defensibility なし、IC partner が "why ±20%?" で止まる |
| 直し方 | §2.3 / §3 で per-driver の Tier 1-4 source ベース range を必須、`_benchmark_protocol` 規律遵守 |

### 11.5 Anti-pattern 5 — Implication vague (evergreen 表現)

| Pattern | "重要な driver なので注視します" の連発 |
|---|---|
| 症状 | implication が "今後も継続的にモニタリング" "重要 KPI として管理" 等 evergreen で具体性ゼロ |
| 原因 | F-I-R-A-K の A (Action) が抽象的、threshold + trigger + action の 3 点 set がない |
| 結果 | "monitor" するだけで kill criteria が発動しない、post-investment で漸減 |
| 直し方 | §6.2 narrative template の Action 欄に **threshold + trigger + concrete action** を必ず明記 (例: "Q1 productivity < ¥14M で kill 発動") |

### 11.6 Anti-pattern 6 — Implications を coupling せず羅列

| Pattern | "各 driver で independent に narrative、全体 thesis との接続なし" |
|---|---|
| 症状 | implication が driver 別 bullet 列挙のみ、top-3 統合や Q1-Q4 quadrant 分類が欠落 |
| 原因 | §6.3 executive summary template と §6.4 4-quadrant decision frame を skip |
| 結果 | reader が "結局 thesis is robust か fragile か" 判断できず、IC vote で混乱 |
| 直し方 | top-3 を §6.3 で 1 page summary、Q1-Q4 で全 driver を 1 frame に位置付け、IC memo の "Recommendation" section に直結 |

### 11.7 Anti-pattern check list (`_self_review_protocol` 統合)

```python
def detect_sensitivity_anti_patterns(model_artifacts: dict) -> list[str]:
    """
    Args:
        model_artifacts: {
            "tornado_drivers": [...],   # tornado に出ている driver list
            "cumulative_share": float,  # cumulative impact share
            "scenarios": [...],          # Bull/Base/Bear の有無
            "narrative_per_driver": {name: text},
            "tier_sources_per_driver": {name: tier_str},
            "executive_summary": str,
            "quadrant_classification": dict,
        }

    Returns:
        list of detected anti-patterns (empty list if all OK)
    """
    issues = []
    if model_artifacts["cumulative_share"] < 0.80:
        issues.append("AP1: 1-2 driver tornado, cumulative < 80%")
    for d, narr in model_artifacts["narrative_per_driver"].items():
        if not all(k in narr for k in ["Finding", "Implication", "Reason", "Action", "Risk"]):
            issues.append(f"AP2: '{d}' narrative missing F-I-R-A-K element")
    if len(model_artifacts["scenarios"]) < 3:
        issues.append("AP3: < 3 scenarios (Bear/Base/Bull all required)")
    for d, tier in model_artifacts["tier_sources_per_driver"].items():
        if tier == "" or tier == "N/A":
            issues.append(f"AP4: '{d}' has no Tier 1-4 source")
    for d, narr in model_artifacts["narrative_per_driver"].items():
        action = narr.get("Action", "")
        if not any(kw in action for kw in ["threshold", "trigger", "Q1", "Q2", "Q3", "Q4", "kill"]):
            issues.append(f"AP5: '{d}' Action lacks threshold/trigger/concrete")
    if not model_artifacts.get("executive_summary") or not model_artifacts.get("quadrant_classification"):
        issues.append("AP6: missing executive summary or 4-quadrant frame")
    return issues
```

> **規律**: `build_model.py` から本関数を呼び出し、anti-pattern が 1 つでも検出されたら IC submission 前に対処。

---

## 12. 関連 reference との整合

本書は他 reference との **役割分担と引用方向** を明示し、知識の重複と矛盾を防ぐ。

### 12.1 Cross-reference matrix

| 関連 reference | 担当領域 | 本書の参照方向 | 重複 / 委譲 |
|---|---|---|---|
| `22_driver_based_modeling §6` | tornado mechanics (`compute_tornado` python、low/high 計算、driver tree node) | 本書 §3 から参照 | 本書は **interpretation のみ**、mechanics は委譲 |
| `09_DCF § Sensitivity` | sensitivity sheet の cell layout、Excel formula、named range | 本書 §7 から参照 | 本書は **IC memo page layout のみ**、xlsx 実装は委譲 |
| `08_ic_memo` | IC memo 全体構成 (Executive summary / Thesis / Risks / Recs) | 本書 §6 / §7 が "Implications" sub-section を inject | 本書は **narrative template のみ**、memo 全体は委譲 |
| `_self_review_protocol §8` | sanity_checks 全 10+ 項目 (P/L 整合、cash 連続性、etc.) | 本書 §9 で S11-S14 を inject | 本書は **sensitivity 関連 4 check のみ**、その他は委譲 |
| `05_valuation_wacc` | DCF / WACC、probability-weighted valuation の formula | 本書 §4.4 / §8.4 で参照 | 本書は **scenario × probability 運用 rule のみ**、formula は委譲 |

### 12.2 引用方向の規律

| 規律 | 説明 |
|---|---|
| **本書 → 他 reference** | mechanics や formula は他 reference を canonical として引用、本書には **要約せず参照 link のみ** |
| **他 reference → 本書** | 「coverage」「Bull/Base/Bear」「threshold MoS」「F-I-R-A-K narrative」「Q1-Q4 quadrant」「Pattern A-D」を扱う場合は本書を canonical として引用 |
| **重複の禁止** | 同じ概念を本書と他 reference で別文字列で記述しない (drift の元)、本書 §1.1 の "正本 (SSoT)" を遵守 |

### 12.3 `build_model.py` の呼び出し規律

`startup-financial-modeling/build_model.py` から本書の content を呼び出す統合 entry point は以下 3 つ:

```python
# Sensitivity & Implications の build pipeline
from references._sensitivity_23 import (
    compute_coverage,           # §2.2 (mechanics は §22)
    find_break_even,            # §5.2
    pairwise_stress,            # §8.1
    detect_sensitivity_anti_patterns,  # §11.7
    run_sensitivity_sanity_checks,     # §9.5
)

# IC memo narrative の build pipeline
from references._narrative_23 import (
    render_per_driver_narrative,    # §6.2 template inject
    render_top3_executive_summary,  # §6.3 template inject
    classify_to_quadrant,           # §6.4 4-quadrant
    detect_pattern_a_b_c_d,         # §6.5 mini-narrative library
)
```

> **規律**: 上記関数 signature を変更する際は、本書 §6 / §9 / §11 の template / check 定義を **同時に更新**。drift を防ぐため `_master_decision_tree` Stage D の routing を pre-commit hook で validate。

### 12.4 Skill 全体での本書の位置

```
[startup-financial-modeling skill]
   │
   ├── _master_decision_tree (Stage A-D ゲート)
   │       └── Stage D: sensitivity & implications
   │             └── 本書 (23) を必須適用
   │
   ├── _self_review_protocol §8
   │       └── S11-S14 (本書 §9) を inject
   │
   ├── 22_driver_based_modeling (mechanics)
   │       └── 本書 §3 / §9 で interpretation 経由参照
   │
   ├── 09_DCF § Sensitivity (xlsx 実装)
   │       └── 本書 §7 で IC memo 用 layout として参照
   │
   └── 08_ic_memo (memo 全体構成)
           └── 本書 §6 narrative template を "Implications" section に inject
```

---
