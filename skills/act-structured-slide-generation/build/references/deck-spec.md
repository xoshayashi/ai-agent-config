# deck.json 仕様とスライドパターンカタログ

目次: トップレベル / 共通フィールド / パターン 19 種(1 cover・2 agenda・3 section_divider・
4 executive_summary・5 kpi_dashboard・6 chart_insight・7 market_sizing・8 comparison_table・
9 competitive_landscape・10 financial_summary・11 waterfall・12 roadmap・13 two_column・
14 process_flow・15 statement・16 financial_highlights・17 metrics_rows・18 guidance_progress・
19 driver_decomposition)/ チャート仕様 / 執筆規律

deck.json はこのスキルの単一の真実点。LLM はコンテンツと構成だけを決め、
座標・フォント・色は build_deck.py が決定論的に処理する。**色や座標を spec に書かないこと**
(例外: チャート系列の `color` は tokens.json パレット内の hex のみ可)。

## トップレベル

```json
{
  "meta": {
    "title": "デッキタイトル",
    "date": "2026年7月",
    "author": "Act Strategy Team",
    "confidential": "Confidential",   // 表紙右上に表示。不要なら省略
    "lang": "ja"
  },
  "slides": [ { "pattern": "...", ... }, ... ]
}
```

## 全スライド共通フィールド

| field | 説明 |
|---|---|
| `pattern` | 必須。下記 19 種のいずれか |
| `title` | アクションタイトル(結論を言い切る一文)。全角 33 字以内で 1 行、66 字まで 2 行(予算は 25pt×タイトル幅から導出)。サイズは行数によらず常に同一(25pt)— 収まらないなら縮小ではなく短文化か分割 |
| `subtitle` | スコープ行: 対象・指標・期間を中立に特定する(例: 「国内SaaS市場規模の推移(2024-2030年)」)。第2の主張を書かない(主張はタイトルの仕事)。IR・データスライドは title+subtitle で対象/指標/期間が読者に特定できること。コンテンツスライドでは全枚数で有無を揃える |
| `source` | 実在する出典のみ。「Act分析」「各社IR資料を基にAct作成」は可。プレースホルダー禁止 |
| `assumption` | 内部仮定。source と混ぜない(Assumption: として別表示される) |
| `note` | 凡例注記など(Note: として表示) |
| `insight` | 底部のバンド(全角 58 字以内 = tokens.json の insight_max_chars_ja)。**多用禁止** — チャート/表が自明に語る場合は省略。デッキ内 2-4 枚が目安 |
| `insight_style` | `"accent"`(既定。淡黄・左寄せ・非自明な判断)/ `"primary"`(淡緑・中央揃え・スライドの so-what を言い切る結論バンド) |
| `kicker` | タイトル上の小さな問いかけ行(全角 16 字以内。例: 「なぜ今参入すべきか?」)。タイトルがその答えになる構成で使う(任意)。文にしない・タイトルの語を繰り返さない |
| `speaker_notes` | スピーカーノート(任意、日本語の語り原稿) |

## パターン 19 種

### 1. cover — 表紙
```json
{ "pattern": "cover", "title": "...", "subtitle": "...", "date": "2026年7月", "author": "..." }
```

### 2. agenda — 目次(items 最大 6)
```json
{ "pattern": "agenda", "title": "本日の論点",
  "items": [ { "label": "市場環境", "desc": "補足一行" } ] }
```

### 3. section_divider — セクション扉
```json
{ "pattern": "section_divider", "number": 1, "title": "市場環境", "desc": "一行説明" }
```

### 4. executive_summary — 冒頭サマリー(points 最大 4)
```json
{ "pattern": "executive_summary", "title": "<デッキ全体の結論を一文で>",
  "points": [ { "kicker": "市場機会", "heading": "小見出し", "body": "2-3行の根拠文" } ] }
```

### 5. kpi_dashboard — KPI カード(kpis 最大 8、1 行に 4 枚まで)
```json
{ "pattern": "kpi_dashboard", "title": "...",
  "kpis": [ { "label": "ARR", "value": "4.3", "unit": "億円",
              "delta": "+4.3億円 YoY", "delta_dir": "up",  // up/down。色は自動(良い方向=緑)
              "positive_is_good": true, "focal": true,     // focal はタイトルが主役と呼ぶ 1-2 枚のみ(淡ブランド色カード)
              "note": "算出根拠の一行" } ] }
```

### 6. chart_insight — チャート+含意(基本形。左チャート右 takeaways)
```json
{ "pattern": "chart_insight", "title": "...", "layout": "chart_left",  // or "chart_full"
  "chart": { ... チャート仕様は下記 ... },
  "takeaways": [ { "heading": "論点", "body": "根拠と含意の 1-2 文" } ] }  // 最大 3
```

### 7. market_sizing — TAM/SAM/SOM ファネル
```json
{ "pattern": "market_sizing", "title": "...",
  "stages": [ { "label": "TAM", "value": "3.2兆円", "numeric": 32000,
                "name": "市場の名前", "desc": "定義と根拠" } ] }
```
`numeric` は同一単位に揃えた数値(バー幅の比率計算に使用)。

### 8. comparison_table — 比較表
```json
{ "pattern": "comparison_table", "title": "...",
  "table": { "headers": ["評価軸", "当社", "A社"], "col_widths": [0.3, 0.35, 0.35],
             "align": ["l", "c", "c"], "emphasis_col": 1,  // 自社列の強調(0始まり、ヘッダー除くデータ列指定)
             "rows": [["...", "...", "..."]] } }
```

### 9. competitive_landscape — 2x2 ポジショニングマップ
```json
{ "pattern": "competitive_landscape", "title": "...",
  "x_axis": { "low": "単機能特化", "high": "統合スイート" },
  "y_axis": { "low": "小規模企業", "high": "大企業" },
  "players": [ { "name": "当社", "x": 0.72, "y": 0.5, "focal": true } ],  // 座標は 0-1
  "notes_heading": "ポジショニングの含意",
  "notes": [ { "heading": "...", "body": "..." } ] }
```

### 10. financial_summary — 財務表+チャート複合(table と chart 両方指定で左右分割)
```json
{ "pattern": "financial_summary", "title": "...",
  "table": { ...comparison_table と同形式。emphasis_row で行強調... },
  "chart": { ... } }
```

### 11. waterfall — ブリッジチャート(シェイプ合成)
```json
{ "pattern": "waterfall", "title": "...", "unit": "億円",
  "items": [ { "label": "FY27\nARR", "value": 4.3, "kind": "start", "display": "4.3" },
             { "label": "新規顧客", "value": 22.0, "display": "+22.0" },   // kind 省略 = delta
             { "label": "解約", "value": -2.8, "display": "△2.8" },       // 負値は自動で Danger 色。表示は IR 慣行の△
             { "label": "FY31\nARR", "value": 68.0, "kind": "end", "display": "68.0",
               "forecast": true } ] }   // 計画・予想のバーは forecast で淡色塗り+枠(実績と描き分け)
```
最初は `kind:"start"`、最後は `kind:"end"` 必須。`\n` でラベル改行可。到達点が計画値なら
`forecast: true` を付ける(実績と同じソリッド塗りにしない)。

### 12. roadmap — フェーズロードマップ(phases 最大 4)
```json
{ "pattern": "roadmap", "title": "...",
  "phases": [ { "label": "Phase 1: 参入", "period": "FY27-28" } ],
  "focal_phase": 0,          // 濃色で強調するフェーズ(任意)
  "rows": [ { "label": "プロダクト", "cells": ["フェーズ1の内容", "フェーズ2の内容", "..."] } ] }
```
`rows` 省略時は各 phase の `items: ["...", ...]` を縦に並べる。

### 13. two_column — 2 案比較(Option A/B、Before/After)
```json
{ "pattern": "two_column", "title": "...",
  "left":  { "heading": "Option A: 自社開発", "items": [ { "heading": "...", "body": "..." } ] },
  "right": { "heading": "Option B: M&A(推奨)", "focal": true, "items": [ ... ] } }
```
`focal: true` の側がヘッダー濃緑になる(推奨案)。
悪い例/良い例の対比には `mark: "cross"`(灰ヘッダー+×)と `mark: "check"`(濃緑ヘッダー+○)を
左右に指定する(Before/After 型)。

### 14. process_flow — ステップフロー(steps 最大 5)
終端ステップだけソリッド primary(途中は淡色)で到達点を示す。items はカードあたり 3 個以内。
```json
{ "pattern": "process_flow", "title": "...",
  "steps": [ { "label": "Step 1: 体制構築", "items": ["...", "..."],
               "outcome": "このステップの帰結を一行(任意。カード下部に ▼ 付きで表示)" } ] }
```

### 15. statement — 結論・引用の全面ステートメント
28pt ヒーロー(60 字超は 24pt)で光学中心に組まれる。statement は 100 字以内を目安に言い切る。
```json
{ "pattern": "statement", "title": "結論", "statement": "2-3 文の言い切り", "attribution": "...",
  "recap": [ { "label": "ARR目標", "value": "68", "unit": "億円" } ] }  // 締めに主要数値を再掲(任意、2-4個)
```

### 16. financial_highlights — 決算ハイライト
ドットラベル付きグループ+太字の主張+ビッグナンバー群。決算・報告デッキの冒頭に最適。
```json
{ "pattern": "financial_highlights", "title": "...",
  "groups": [ { "label": "業績", "claim": "太字の主張文(20字前後)",
                "metrics": [ { "label": "売上高", "value": "32.4", "unit": "億円",
                               "delta": "+28% YoY", "delta_dir": "up" } ],   // 2-4 個/グループ
                "note": "定義・補足の一行(任意)" } ] }   // groups は 1-2 個
```

### 17. metrics_rows — 数値サマリ行(ラベル|大数値+小単位|YoY)
ヘアライン区切りの行で構成する決算サマリ。グリッド表より軽く、数字が主役のときに使う。
```json
{ "pattern": "metrics_rows", "title": "...",
  "columns": [ { "heading": "FY26 Q2 会計期間",
                 "rows": [ { "label": "売上高", "value": "804", "unit": "百万円",
                             "delta": "+31.2%", "delta_dir": "up" } ] } ] }  // columns は 1-2 個
```

### 18. guidance_progress — 通期ガイダンス進捗
過去年度バー(グレー)+当期バー(実績をブランド色で塗り、ガイダンスまでの残額を破線の
空箱で上乗せ)+右の進捗ファクト列。進捗を%でなく塗り面積で直感表示する決算デッキの定番。
```json
{ "pattern": "guidance_progress", "title": "...", "unit": "億円",
  "bars": [ { "label": "FY2024", "value": 78.2, "display": "78.2" },
            { "label": "FY2025", "value": 104.5, "display": "104.5" } ],
  "current": { "label": "FY2026", "actual": 64.8, "actual_display": "上期実績 64.8",
               "guidance_low": 132, "guidance_high": 136, "range_display": "132 - 136(予想)" },
  "side_heading": "上期進捗",
  "side": [ { "label": "進捗率", "value": "48%" },
            { "label": "YoY", "value": "+28%" },
            { "label": "調整後営業利益", "value": "2.1億円" } ] }
```

### 19. driver_decomposition — KPI ドライバー分解(数 × 単価 = GMV)
```json
{ "pattern": "driver_decomposition", "title": "...",
  "factors": [ { "label": "利用数", "value": "131.3", "unit": "千SP", "delta": "+14.9% YoY",
                 "note": "補足一行" },
               { "label": "単価", "value": "48.9", "unit": "千円", "delta": "△0.3% YoY", "delta_dir": "down" },
               { "label": "GMV", "value": "6,408", "unit": "百万円", "delta": "+14.6% YoY", "focal": true } ],
  "operators": ["×", "="] }   // 省略時は × … = を自動適用。focal は結果側に付ける
```

## チャート仕様(chart_insight / financial_summary 共通)

```json
{ "type": "column",            // column / stacked_column / bar / line / donut
  "unit": "億円",              // 左上に (億円) と表示される
  "categories": ["FY27", "FY28"],
  "series": [ { "name": "売上高", "values": [3.5, 9.8] },
              { "name": "営業利益", "values": [-18.0, -22.0], "color": "1F3A66" } ],
  "focal_category": 6,         // 単一系列時: この index のみ Primary 色、他はグレー(結論の柱を立てる)
  "value_labels": true,        // 単一系列は既定 on。数字が多すぎるなら false
  "number_format": "0.0",     // データラベルと軸目盛の書式(Excel 書式)
  "axis_number_format": "0",  // 軸目盛だけ別書式にするとき(省略時は number_format と共通)
  "legend": true,              // 複数系列の既定 on
  "y_max": 3.5, "y_min": 0, "hide_value_axis": false,
  "axis_less": true,           // 軸レスの明示上書き。既定は自動(単一系列 column/bar/line + value_labels で軸レス)
  "forecast_from": 3,          // この index 以降を予想値として描画(淡色塗り+ブランド色枠 = IBCS流)。単一系列の column/bar のみ(line は categories の E 表記+注記で区別)
  "annotation": { "yoy": "+30%", "trend_arrow": true } }  // 最新期バーの上に YoY 円形バッジ+成長矢印(時系列の結論スライドで有効)
```
`annotation` は `badge: "3.2兆円"` で任意文言の円形バッジにもできる(yoy と排他)。

ルール:
- 系列は最大 4。2 系列目以降の色は自動(Primary → Navy → グレー → Warning)。
- **結論が指す 1 点を強調し、他を沈める**: 単一系列は `focal_category`、複数系列は主役以外を
  `"color": "B9B5AA"`(グレー)に。
- **実績と予想は塗りで描き分ける**(IBCS): 予想期間の先頭 index を `forecast_from` に指定し、
  該当 categories 名へ "E" / "計画" を付ける。予想を実績と同じソリッド塗りで見せない。
  focal が予想期間にある場合は淡色塗りのまま太い濃枠で強調される(実績のふりをさせない)。

## 執筆規律(バンカーグレードの条件)

1. **アクションタイトル**: 全スライド、主語+変化+含意を含む言い切りの文。体言止め・
   トピックラベル(「市場環境について」)は禁止。タイトルだけを通読して 1 本のストーリーに
   なること(ゴーストデッキテスト)。
2. **タイトルは図表が証明できることしか言わない**。数字はタイトル・本文・図表で一致させる。
3. **1 スライド 1 メッセージ**。2 つ言いたければ分割する。
4. **数値の規律**: 単位・期間・小数桁をデッキ全体で統一(4.3億円 / FY27 / +12% YoY)。
   桁区切りは 1,800。出典のない数字を作らない。
5. **source は実在するもののみ**。内部推計は `assumption` に分離。
6. **insight は例外的に使う**。図表の繰り返しは禁止、非自明な判断・条件だけを書く。
7. 言語は入力に従う(日本語プロンプト→日本語デッキ)。英数字は半角。
8. **speaker_notes は語りを補完する**: スライドの文言の読み上げ再掲は書かない。スライドが
   数字を示し、ノートがその背景・想定問答・つなぎの一言を持つ(スライドとノートは別採点軸)。
