---
name: startup-financial-modeling
description: Use when the user needs a startup 収支計画 / financial plan xlsx from an equity story, business plan, or driver assumptions — a tight, IB-formatted 10-sheet annual model (Summary / Assumptions / Revenue / Headcount / Opex / PL / Cash / KPI / Cap Table / Valuation) with live formulas, story tie-out checks, and a 95-point rubric gate. Also for auditing or restyling an existing plan against IB conventions.
---

# Startup Financial Modeling（IB流収支計画）

エクイティストーリーや事業計画から、投資銀行流の作法で締まった収支計画xlsxを
生成する。シートは必要十分の10枚（サマリー/前提条件/売上計画/人員計画/費用計画/
損益計画/資金繰り/KPI/資本政策/バリュエーション）に固定し、各シートに1つの
役割と十分なモデリング密度を持たせる。メタシート（Guide等）、フル3表BSは
作らない（根拠は `references/sheet_architecture.md`）。

## ワークフロー

1. **ソースを読む** — エクイティストーリー・事業計画から記載値（顧客数、単価、
   原価、フェーズ別粗利率、ケース）をすべて拾う。記載のない値（調達額、解約率、
   人員、費用率）は仮置きし、必ず「仮置き」と注記する。
   仮置き値の水準とシート中身の設計は、シート別プレイブックの必須ブロック・
   ベンチマーク・チェックリストに従う:
   - `references/playbook_assumptions_revenue.md` — 前提条件・売上計画
     （解約率/NRRベンチマーク、ロールフォワード、ARR vs 認識売上、従量分解）
   - `references/playbook_headcount_costs.md` — 人員計画・費用計画
     （バーデン率、Revenue/FTE、AI推論原価の段階逓減、COGS線引き、費用率水準）
   - `references/playbook_pl_cash_summary.md` — 損益計画・資金繰り・サマリー
     （繰越欠損金の日本ルール、ランウェイ/バーン規律、KPIのステージ適合）
   - `references/playbook_kpi.md` — KPIシート
     （ベンチマーク帯と出典、3段階評価ロジック、除外すべきKPI）
   - `references/playbook_captable.md` — 資本政策シート
     （ラウンドイベント列方式、循環回避の数式チェーン、希薄化・プール帯）
   - `references/playbook_valuation.md` — バリュエーションシート
     （三大手法のレンジ、Exit Value・投資家リターン、フットボールフィールド、感応度）
2. **YAMLに構造化** — `scripts/build_workbook.py` の入力スキーマ
   （セグメント別: ending_customers / churn_rate / fixed_fee_monthly /
   usage_fee_monthly / usage_rate_per_min / implementation_fee / cost_per_min、
   ToCセグメントは cogs_pct_of_revenue。共通: headcount / opex / capex_yen /
   tax_rate / financing / story_checks / scenario_reference）。年次ランプが
   ソースに無ければ最終年目標から逆算設計し、備考に明記する。
3. **生成** — `python3 scripts/build_workbook.py --input plan.yaml --outdir 出力先/`
   （xlsxと入力YAMLコピーを同一フォルダーへ出力。PDFも後続手順で同じフォルダーに置き、
   納品物は必ず1フォルダーに集約する）
4. **機械検査** — `python3 scripts/inspect_workbook.py plan.xlsx`
   （B列起点、行高デフォルト、青字入力・黒字数式・緑字リンク、書式ホワイト
   リスト、フィル制限、結合セル・揮発関数禁止。契約は `references/ib_format_spec.md`）
5. **再計算検証** — LibreOffice `soffice --headless --calc --convert-to xlsx`
   で再計算し、`data_only=True` でエラーゼロ、サマリーの照合ブロック
   （モデル値 vs 記載値）が±1%以内、現金非負チェック0を確認する。
6. **レンダリング目視** — `soffice --headless --convert-to pdf` でPDF化し、
   切れ・重なり・階層崩れを目視する。
7. **プレイブック照合** — 各シートをプレイブックの品質チェックリストで自己検査
   する（ロールフォワード閉合、ARPU検算、Revenue/FTEバンド、粗利軌道とフェーズ
   整合、NOL枯渇年まで税ゼロ、ランウェイ18〜24ヶ月、Burn Multiple等）。
8. **ルーブリック採点** — `references/rubric.md`（100点満点・多面的）で採点し、
   **95点未満なら修正して1に戻る**。独立した複数エージェント（IB / VC / 監査の
   異なるスタンス）に採点させ平均を取ることを推奨。

## 設計原則（要約）

- 収益はセグメント×経済プリミティブ（稼働数ロールフォワード×固定＋従量ARPU、
  新規×導入費）から構築。COGSは稼働分数×原価/分などのドライバーで導出し、
  粗利率は結果として出す（率の直打ちで済ませない）。
- 収益認識の慣行（期末稼働×年額 vs 期中平均）はソースの算式に合わせ、
  備考で明示する。
- 全入力はAssumptionsに青字で集約。導出はすべて生きた数式。定数の数式内
  埋め込み禁止（12か月・365日などの構造定数は除く）。
- 記載値とモデル値のタイアウトはサマリーの照合ブロックで数式化し、
  条件付き書式で±1%超を赤字にする。
- 税は繰越欠損金スケジュール付き。資金繰りは簡易FCFブリッジ＋運転資本＋
  調達＋ランウェイ。
