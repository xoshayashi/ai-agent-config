# Round 2 Fix: Valuation 章 — 修正記録

- **対象ファイル**: `references/05_valuation_wacc.md`
- **解消対象 finding**: C-C-026 .. C-C-035 (10 件), E-C-003, E-C-004
- **作業日**: 2026-05-01
- **完了状態**: 完了
- **既存 §1-20 への影響**: なし (追加のみ)
- **行数変化**: 1767 → 2440 lines (+673 lines)

## 追加された節

| 節 | タイトル | 行範囲 | 解消する finding |
|---|---|---|---|
| §21 | Boundary Conditions (境界条件・例外処理) | 1771-2146 | C-C-026 .. C-C-035 |
| §21.1 | WACC ≈ g 発散 (Gordon Growth の境界) | — | C-C-026, C-C-027 |
| §21.2 | Stage Transition での discount rate 切替 | — | C-C-028, C-C-029 |
| §21.3 | Currency Mismatch | — | C-C-030, C-C-031 |
| §21.4 | Negative EBITDA で multiple | — | C-C-032, C-C-033 |
| §21.5 | Reverse DCF の Boundary | — | C-C-034, C-C-035 |
| §22 | Stage Discount Rate Default (推奨デフォルト) | 2148-2290 | E-C-003 |
| §23 | Liquidation Preference 評価手法選定基準 | 2292-2440 | E-C-004 |

## §21 (Boundary Conditions) 解消ポイント

### 21.1 WACC ≈ g
- 3 段階の境界判定 (spread <= 0 / < 1pt / < 2pt) と自動切替フローを実装
- Exit Multiple Method への自動切替ロジック (業態別 fallback multiple 表)
- g <= long-term GDP nominal 上限の妥当性チェック
- 反例 (WACC 9%, g 8%) と triangulation 必須化

### 21.2 Stage Transition smoothing
- Linear ramp / Convex decay / Probabilistic の 3 アプローチ
- 推奨デフォルト: Linear ramp 2-3 年
- Down round (逆 transition) の扱い
- 経路依存性 (path dependency) 警告ロジック
- 実装サンプル付き

### 21.3 Currency Mismatch
- 通貨整合性 + 名目/実質整合性の 2 軸ルール
- 単一通貨統合 / 二重通貨並列 / PPP の 3 パターン
- Forward FX (interest rate parity 簡易版)
- 通貨タグ付けデータ構造 (CashFlow dataclass)
- FX risk premium 目安 (主要通貨 0.5-1.5% / 新興国 2-5%)

### 21.4 Negative EBITDA fallback
- 業態別 fallback metric 表 (SaaS / Marketplace / Fintech / Biotech / Hardware / Web3 等 12 業態)
- 自動 fallback フロー (擬似コード)
- Forward EV/EBITDA を許容する条件 (Rule of 40 等)
- Growth-adjusted multiple の cross-check 必須化

### 21.5 Reverse DCF Boundary
- 5 段階の implied growth 警告条件 (Critical/High/Medium/Low)
- GDP × 100x、50%、3x GDP、5x risk-free rate の 4 閾値
- 物理的上限 (Damodaran "Apple cannot grow at 20% forever")
- 2 段階モデル (高成長期 + perpetual TV) を実装注意点として明記

## §22 (Stage Discount Rate Default) 解消ポイント

### 22.1 - 22.2 ベース表
- Pre-revenue / Early Revenue / Series A-D / Pre-IPO / Public の 7 stage
- 各 stage の WACC range、Default 中央値、Survival probability を 3 軸 default 化

### 22.3 Risk-Adjusted Method
- 定式化: PV = p × DCF(success) + (1-p) × Distress Value
- Damodaran "Valuing Young Firms" §7 ベース

### 22.4 Stage-only vs Risk-adjusted の差分 (重要)
- **本書の主張**: 単一 discount rate なら risk-adjusted を default、stage-only は legacy へ降格
- **Reason** の定量比較を表形式で示す:
  - Stage-only は exit value sensitivity (50% 半減 → -50%) は反映できる
  - Stage-only は survival sensitivity (50% → 25% への悪化) は反映できない
  - Risk-adjusted は両方を直接モデル化
  - 50% 半減 + survival 半減 = stage-only だと **追加 50% の overvaluation**

### 22.5 - 22.7
- Risk-adjusted method 実装ガイド (Python 擬似コード)
- Survival curve cumulative table (Pre-rev / Early-rev / Series A 開始時)
- Stage-only 容認条件 / 禁止条件
- 信頼性タグ付け (YAML 形式)

## §23 (Liquidation Preference 選定基準) 解消ポイント

### 23.1 - 23.2 Decision Tree
- OPM / PWERM / Hybrid / CVM の 4 手法を 7 状況にマッピング
- 状況別の推奨手法と根拠を表形式で明示

### 23.3 優先順位フロー
- Step 1: IPO 確率の明確性
- Step 2: 業績 forecast 信頼性
- Step 3: Exit scenario の絞り込み度
- Step 4: Down round / volatility 観測可否
- Step 5: 監査 / 409A 提出用かどうか

### 23.4 各手法の長所・短所
- OPM: σ 推定、leverage adjust、DLOM 別建ての注意
- PWERM: 主観性、auditable 性の課題
- Hybrid: AICPA Practice Aid 推奨、二重カウントへの注意
- CVM: 即時清算前提のみ、現代では非推奨

### 23.5 観点別選好
- **創業者観点**: PWERM (capped participation の上限が common stock を増やす)
- **投資家観点**: OPM (LP の floor 効果を full reflect)
- **監査人 / 409A**: Hybrid 強推奨

### 23.6 - 23.7 実装注意点 / 監査済 sample
- Breakpoint transparency、volatility 出典、DLOM 10-30%、評価日 staleness 6M
- 5 ケース (Series A SaaS / Pre-IPO Fintech / Down round marketplace / M&A bid 進行中 / Series B Biotech) の選定例

## 一次ソース参照

- Damodaran A., "Valuing Young Firms" (Stern, 2009-2025)
- Damodaran A., "Investment Valuation" 3rd ed., Ch.23
- Damodaran "Country Risk: Determinants, Measures and Implications"
- AICPA "Valuation of Privately-Held-Company Equity Securities Issued as Compensation" Practice Aid (Aug 2013, 改訂継続)
- ASC 718 / IRC §409A 実務ガイド
- BVP Cloud Index、Meritech Public Comps、Pitchbook
- CB Insights "Startup Failure Post-Mortem"
- Cambridge Associates、NVCA Yearbook 2024-2025

WebSearch は Damodaran と AICPA / 409A 系に限定参照。深追いせず一次ソースの主要テーゼに基づいて記述。

## 検証

- ファイル末尾までの skeleton マーカー消滅: 確認済み (`grep -n skeleton` で 0 件)
- 既存 §1-20 への変更: なし (追加のみ)
- §21, §22, §23 の section header が連番で存在: 確認済み (line 1771 / 2148 / 2292)
- 行数増分: +673 lines (要件 400-700 lines 範囲内)

## 残課題

- 数値ベンチマーク (SaaS multiple、stage WACC、survival prob、CRP) は時点依存。**本リファレンス参照時に最新の一次ソースで再確認**を §20 と同様に運用すること。
- §21, §22, §23 で参照した Damodaran year-2024-2025 data は 2026-05 時点。次回の data file 更新時に数値再確認推奨。
