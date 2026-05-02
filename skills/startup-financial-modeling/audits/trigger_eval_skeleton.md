# Trigger Eval Skeleton — Phase 7 着手前準備

- **作業日**: 2026-05-02
- **目的**: skill-creator framework の `run_loop.py` で description optimization を回す前の、20 query × should-trigger 期待値を整備
- **入力**: `evals/evals.json` の `trigger_eval_queries_should_trigger` (10 件) と `trigger_eval_queries_should_not_trigger` (10 件)
- **出力**: 各 query の "expected trigger 率"、"should-trigger rationale"、"variation hot keywords"

---

## 1. Should-Trigger 10 query (manual estimated trigger rate)

| # | Query 抜粋 | 予想 trigger 率 | should-trigger rationale | 変動予想 keyword |
|---|---|---|---|---|
| 1 | "うちの SaaS、ARR ¥240M、Series A の調達額と評価額レンジを 14 sheet モデル..." | **95%** | 直接 keyword 多数 (SaaS / ARR / Series A / 14 sheet / cap table / NRR / MRR) | "ARR" / "14 sheet" の重み |
| 2 | "J-KISS 2.0 で ¥150M 調達済み (cap ¥1.2B、disc 20%)、来年 Series A..." | **95%** | J-KISS / Series A / cap / discount / converted shares / 希薄化 waterfall は description で全て list 済 | "J-KISS" は description にあり |
| 3 | "VC のインベストメントメモを書きたい...Rule of 40 = 38、Burn Multiple = 1.8...kill criteria...Football field" | **90%** | IC memo / Rule of 40 / Burn Multiple / Football field / kill criteria | "kill criteria" は description にないが context 強い |
| 4 | "Q4 SaaS forecast、3 年分... Salesforce export...三表 (PL / BS / CF) 突合せ + sensitivity" | **85%** | three-statement / sensitivity / SaaS / forecast | "Salesforce" は分散要因だが context 強い |
| 5 | "Marketplace スタートアップの GMV $100M、take rate 12%...LTV/CAC...IC memo と xlsx 一式を" | **90%** | Marketplace / GMV / LTV/CAC / IC memo / xlsx | description で marketplace 明示 |
| 6 | "うちのスタートアップ、来期から連結に乗る (子会社 持分 70%)。NCI と CTA の処理込みの三表モデル" | **75%** | 連結 / NCI / 三表 (description にないが startup + 三表モデル context) | "NCI" "CTA" は description にない |
| 7 | "DCF で WACC 計算したら g (terminal growth) より低くなった...Mid-stage SaaS...Exit Multiple に切り替えるべき?" | **85%** | DCF / WACC / Mid-stage SaaS / Exit Multiple | "WACC" は description で list 済 |
| 8 | "founder secondary を Series B で 10% やりたい...cap table と税効果両方で trace...日本法人" | **85%** | founder secondary / Series B / cap table / 税効果 / 日本 | "founder secondary" は description で明示 |
| 9 | "venture debt の facility (¥500M, 4-year, JPY+1.8%)...equity との trade-off...IC memo に" | **85%** | venture debt / equity / IC memo | "venture debt" は description で明示 |
| 10 | "fintech (lending) の起業準備中。CAC payback と loan loss provision...3 年 forecast...日本 (貸金業登録前提)" | **80%** | fintech / CAC payback / forecast / 日本 | "loan loss provision" は分散要因 |

**Should-Trigger average: ~86.5%**
**目標: ≥90%** (skill-creator framework 推奨)

---

## 2. Should-NOT-Trigger 10 query (manual estimated non-trigger rate)

| # | Query 抜粋 | 予想 non-trigger 率 | should-NOT-trigger rationale | False trigger リスク keyword |
|---|---|---|---|---|
| 1 | "競合 SaaS 上場企業 (Sansan) の直近決算...business model の解説してほしい。モデル作る必要はない" | **90%** | "モデル作る必要はない" 明示 + 解説のみ | "SaaS" / "business model" → false trigger リスク |
| 2 | "個人事業主 (フリーランス) の家計簿を Excel...月次の収支と確定申告" | **95%** | startup ではなく家計簿、xlsx 業務一般 | "Excel" / "月次" は分散要因低い |
| 3 | "上場企業 (Snowflake) の 10-K から ARR と NRR を抽出して csv にまとめて" | **80%** | "csv にまとめる" データ抽出 task、財務モデル化しない | "ARR" / "NRR" / "Snowflake" → false trigger リスク高 |
| 4 | "Series A の term sheet 雛形が欲しい。NVCA model documents の文面そのままで" | **75%** | term sheet 文面のみ、数値計算なし | "Series A" / "model documents" は false trigger リスク |
| 5 | "VC 向け pitch deck (10 slide) を作りたい...financials (1 slide だけ summary)" | **80%** | pitch deck メイン、`document-skills:pptx` 領域 | "financials" / "VC" → false trigger リスク |
| 6 | "TAM/SAM/SOM の市場規模算定だけ知りたい。Bottom-up で。財務モデルは別途作る" | **70%** | "別途作る" 明示、市場規模単体 | "TAM/SAM/SOM" / "財務モデル" → false trigger リスク高 |
| 7 | "M&A の deal book / virtual data room を整理...VDR の folder structure と DD checklist" | **85%** | VDR 整備、財務モデル本体は target 側 | "M&A" / "DD" は description で list されてない |
| 8 | "Cap table を入力する SaaS (Carta / Pulley) の比較してほしい。料金と機能で" | **80%** | Cap table tool 比較、財務モデル生成しない | "Cap table" / "SaaS" → false trigger リスク高 |
| 9 | "会社設立の手続き (株式会社、資本金 ¥1M)...定款 / 公証役場 / 法務局" | **95%** | 法務手続のみ、数値モデル不要 | low |
| 10 | "Series A の調達がうまくいかない。VC への cold reach の文面を 5 つ書いて" | **90%** | cold reach 文面、数値計算なし | "Series A" / "VC" → false trigger リスク |

**Should-NOT-Trigger average: ~84%**
**目標: ≥90%** (skill-creator framework 推奨)

---

## 3. 重点的に最適化が必要な query (Phase 7 run_loop で focus)

### 3.1 false-trigger 高リスク (should-NOT-trigger だが trigger しそう)

| # | Query | リスク要因 | description 改善案 |
|---|---|---|---|
| 3 | Snowflake 10-K から ARR/NRR 抽出 | "ARR" "NRR" 強キーワード | "Do NOT trigger for: ... data extraction from 10-K filings without numerical model" 追加 |
| 4 | Series A term sheet 雛形 | "Series A" 強キーワード | "term sheet drafting (legal text only, no numbers)" 除外条件追加 |
| 6 | TAM/SAM/SOM 単体 | "TAM/SAM/SOM" + "財務モデル" 言及 | "market sizing standalone (without quantitative model build)" 除外条件追加 |
| 8 | Carta / Pulley 比較 | "Cap table" "SaaS" 強キーワード | "cap table software comparison" 除外条件追加 |

### 3.2 under-trigger 高リスク (should-trigger だが trigger しなそう)

| # | Query | リスク要因 | description 改善案 |
|---|---|---|---|
| 6 | 連結会計、NCI / CTA 処理 | "NCI" "CTA" "連結" は description にない | description に "consolidation / NCI / CTA / holdco" 追加 (`13a` corpus に対応) |

---

## 4. Phase 7 着手手順 (run_loop.py)

```bash
# 0. baseline trigger 率測定
cd skills/startup-financial-modeling/
python <document-skills-cache>/skills/skill-creator/scripts/run_loop.py \
  --skill-path . \
  --eval-path evals/evals.json \
  --max-iterations 0  # baseline only

# 1. 5 iteration で description 最適化
python .../run_loop.py \
  --skill-path . \
  --eval-path evals/evals.json \
  --max-iterations 5

# 2. 結果 review
open eval_review.html
```

**期待値**: baseline 86%/84% → 最適化後 92%/92% (累計 92%)。

---

## 5. Variation Hot Keywords (run_loop が触る可能性高い語彙)

description で sensitivity 高い語彙:
- "IC memo" — should-trigger #3 / should-NOT-trigger #5 で対立、判定基準 "with quantitative output" を強化
- "cap table" — should-trigger #1, #2, #8 / should-NOT-trigger #8 で対立、"build / model" vs "compare / discuss" を識別
- "業態" / "SaaS" — should-trigger 全件 / should-NOT-trigger #1, #3, #8 で頻出、"build" 動詞の有無を強化
- "Series A" — should-trigger #1, #2 / should-NOT-trigger #4, #10 で対立、"valuation / model" が共起するか判定

run_loop で "build" / "model" / "三表" / "希薄化 waterfall" 等の動作系語彙を強化する方向の最適化を期待。

---

## 6. 改訂履歴

| Date | Action |
|---|---|
| 2026-05-02 | Wave 2 で初版作成。20 query の expected trigger 率と Phase 7 run_loop 準備 |
