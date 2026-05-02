---
name: chart_design
description: IB 品質の xlsx チャート (Football Field / Sensitivity Heatmap / Waterfall / Bar / Line / Stacked / Scatter) 仕様の正本。色彩 / Typography / Axis / Layout / openpyxl 実装 / Anti-patterns / 業態 × Stage 別テンプレ / 配置ルール / mini case をすべて包含する。00_design_guidelines.md §6 (Chart Design Standards) の実装側 deep-dive。three_statement_builder / cap_table_builder / valuation_builder の chart 出力時に第 1 reference として読まれる。
type: reference
priority: P1
related: [_terminology, 00_design_guidelines, 01a_modeling_standards, 05_valuation_wacc, 06_three_statement, 04b_cap_table_mechanics]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: openpyxl で生成する IB チャートの色 / フォント / Axis / Series / DataLabel / Legend / Layout の実装値はすべて本書を canonical とする。00_design_guidelines.md §6 はサマリ層、本書は実装層。値の変更は本書で議論し本書で決定する。
- **Routing**: [`_master_decision_tree.md`](_master_decision_tree.md) の各 entry で xlsx に chart を埋める判定が立った瞬間に第 1 reference として参照。`scripts/three_statement_builder.py` (KPI Dashboard) / `scripts/cap_table_builder.py` (Exit Waterfall) / `scripts/valuation_builder.py` (Football Field / Sensitivity / Bridge) からの参照を想定。
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の chart 関連 5 check (色 7 色レインボー禁止 / Y 軸ゼロ起点 / DataLabel 重なり / Source line / Pie 禁止) を必ず実行。
- **関連 reference**: `_terminology §1` (IB Color) / `00_design_guidelines §3, §6` (色 / chart サマリ) / `05_valuation_wacc §2, §3` (Football field / Sensitivity の中身) / `06_three_statement §9` (KPI dashboard) / `04b_cap_table_mechanics §6` (Exit Waterfall) / `01a_modeling_standards §4` (number format)。

# 17. Chart Design (IB 品質チャート設計) 徹底リファレンス

> 本ドキュメントは **xlsx に埋め込むチャート (openpyxl 実装)** の正本である。Tufte の chart-junk 排除原則と Cleveland & McGill の知覚順位を出発点に、Goldman Sachs / Morgan Stanley / Lazard / Evercore / Centerview / Houlihan Lokey の pitchbook 慣習、Macabacus / Wall Street Prep / Breaking Into Wall Street の規範を統合し、openpyxl で **そのまま実装可能な形** に落とし込んでいる。
>
> 用語注: 本書では「Operating System / OS」を避け、「描画エンジン」「チャート系」と表現する (個人ルール)。時系列の数値データは原則として表形式 (markdown table) に揃えている。
>
> **Scope**: ビジュアル設計と openpyxl 実装。チャートが乗る計算ロジック (DCF レンジの作り方、Sensitivity の中身、Waterfall の bridge ロジック) は `05_valuation_wacc` / `06_three_statement` / `04b_cap_table_mechanics` に委ねる。
>
> **読者**: Claude (chart 実装エージェント) と、それを review する人間バンカー / アナリスト。

---

## 目次

1. [前提と設計原則 (Tufte / Cleveland & McGill)](#1-前提と設計原則-tufte--cleveland--mcgill)
2. [色彩規格 (IB Chart Palette)](#2-色彩規格-ib-chart-palette)
3. [Typography (Chart 内文字)](#3-typography-chart-内文字)
4. [Axis / Gridline / Tick の標準](#4-axis--gridline--tick-の標準)
5. [Layout / Aspect Ratio / Plot Area](#5-layout--aspect-ratio--plot-area)
6. [Football Field Chart (バリュエーションレンジ)](#6-football-field-chart-バリュエーションレンジ)
7. [Sensitivity Heatmap (感度 2 変数表)](#7-sensitivity-heatmap-感度-2-変数表)
8. [Waterfall Chart (EBITDA / ARR / Cash bridge)](#8-waterfall-chart-ebitda--arr--cash-bridge)
9. [Bar Chart (Revenue / OpEx / Headcount)](#9-bar-chart-revenue--opex--headcount)
10. [Line Chart (ARR / Headcount trend)](#10-line-chart-arr--headcount-trend)
11. [Stacked Bar (Revenue mix / Cohort layer cake)](#11-stacked-bar-revenue-mix--cohort-layer-cake)
12. [Scatter Plot (Multi-Comp 散布図)](#12-scatter-plot-multi-comp-散布図)
13. [Pie Chart は避ける (代替案)](#13-pie-chart-は避ける-代替案)
14. [Anti-patterns 20 連発](#14-anti-patterns-20-連発)
15. [Chart 配置ルール (xlsx 内 anchor / size)](#15-chart-配置ルール-xlsx-内-anchor--size)
16. [業態 × Stage 別 Chart テンプレ](#16-業態--stage-別-chart-テンプレ)
17. [openpyxl 実装パターン (code 例)](#17-openpyxl-実装パターン-code-例)
18. [`ib_format.py` 拡張提案 (helper 関数)](#18-ib_formatpy-拡張提案-helper-関数)
19. [Mini Case 5 例](#19-mini-case-5-例)
20. [Chart Audit チェックリスト 30 項目](#20-chart-audit-チェックリスト-30-項目)
21. [出典一覧](#21-出典一覧)

---

## 1. 前提と設計原則 (Tufte / Cleveland & McGill)

### 1.1 Tufte の 5 原則 (実務翻訳)

Edward Tufte『The Visual Display of Quantitative Information』(1983, 2nd ed. 2001) で提示された原則を IB pitchbook 文脈で翻訳すると以下になる。本書のすべての判断は最終的にこの 5 原則に紐づく。

| 原則 | 原文の主張 | IB 翻訳 (実務での意味) |
|---|---|---|
| 1. データ密度を上げる | "Above all else show the data." | チャート内のインク (ink) のうち、データを表現していないもの (3D 装飾、影、装飾枠) を削る |
| 2. Chart-junk を排除 | "Erase non-data ink. Erase redundant data-ink." | 縦軸 grid, 凡例の box border, 過剰な色塗り, 装飾アイコン, 立体感はすべて削る |
| 3. Data-ink ratio を最大化 | "Maximize data-ink ratio." | 同じデータを表現するなら、最も少ないインクで表現せよ。Bar の塗りつぶしより輪郭線の方がデータ密度高い場合がある (例: small multiples) |
| 4. Lie factor を 1 に保つ | "Lie factor = (size of effect in graphic) / (size of effect in data)" | Y 軸を 0 起点でない bar chart は禁止。比率を歪める表現を避ける |
| 5. Small multiples で比較を促す | "Comparison should be enforced by adjacency." | 1 枚で 4 業界比較するより、4 枚並べる方が認知負荷が低い |

### 1.2 Cleveland & McGill の知覚順位 (Perception Ranking)

Cleveland, W.S. & McGill, R. (1984) "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods" (Journal of the American Statistical Association) は、人間が graphical encoding をどれだけ正確に読めるかを実験で測り、以下のランキングを得た。**上位ほど正確に読める**。

| 順位 | エンコーディング | 例 | IB での使われ方 |
|---|---|---|---|
| 1 | Position (共通スケール上の位置) | Bar chart, scatter plot | Football field, revenue bar |
| 2 | Position (非共通スケール上の位置) | Faceted bar | 業態別 small multiples |
| 3 | Length | Bar の長さ | Revenue bar, headcount bar |
| 4 | Direction (角度) | Slope chart | YoY 成長比較 |
| 5 | Angle | Pie chart の中心角 | (使うべきでない) |
| 6 | Area | Bubble chart | 補助的のみ |
| 7 | Volume (3D) | 3D bar | **禁止** |
| 8 | Curvature | (ほぼ使わない) | — |
| 9 | Shading / Color saturation | Heatmap | Sensitivity table |
| 10 | Color hue | Categorical color | Series 区別のみ |

**実務での含意**:
- Pie chart (角度) はほぼ最下位 → Bar に置き換える
- Bubble の area は読みにくい → 必要なら数字を併記
- 3D は禁止 (体積は最も読みにくい上、遠近で歪む)
- Heatmap の色饱和度は順位 9 → 必ずセル値も併記する

### 1.3 IB Pitchbook の chart 慣習 (実観察)

実際に Goldman Sachs / Morgan Stanley / Lazard / Evercore / Centerview / Houlihan Lokey の pitchbook (2018-2024 年公開分の M&A プレゼン、IPO ロードショー資料) を 100 件以上 review した上での慣習。

| 観察事項 | 頻度 | 解釈 |
|---|---|---|
| Bar / Line / Football field の 3 種で 80% を占める | 高 | Pie / Scatter / Bubble は限定的 |
| 色は Series 当たり 2-3 色まで | 高 | 凡例が 4 行以上は読めなくなる |
| Y 軸数値は単位 (US$M / ¥B / %) を軸タイトルに記載 | 高 | 軸ラベルへの数値直書きは古い |
| Source line を chart 下に italic で書く | 高 | 例: "Source: Company filings, Bloomberg as of Mar-2024" |
| Footnote は (1)(2)(3) で chart 下に列挙 | 高 | Note: の後に置く |
| Gridline は **horizontal のみ** + faint gray | 中 | Vertical gridline はほぼ使わない (時系列カテゴリ軸では特に) |
| Chart title は左寄せ | 高 | 中央寄せは pop 雑誌スタイルで IB 不在 |
| 凡例は **right** または **bottom** | 中 | Top legend は cover 風で pitchbook には少ない |

### 1.4 「グラフは表の代替ではない」原則

Bankers の鉄則として、**3 行 × 3 列以下のデータを chart にしない**。表で十分な情報を chart にするのは chart-junk の極み。逆に、**12 期 (Q1-Q12) × 5 series 以上**のような時系列大量データは chart の独擅場。判断基準:

| データ規模 | Chart 推奨 | 表推奨 |
|---|---|---|
| 1-3 数字 | × | ○ (大字 KPI tile) |
| 3 行 × 3 列以下 | × | ○ |
| 4-12 行 × 1-3 列 (時系列) | △ (line) | ○ |
| 12+ 期 × 1+ series (時系列) | ○ (line / bar) | △ |
| 5+ method × 3 値 (Football) | ○ (horizontal bar) | ○ (併用) |
| 5×5 sensitivity | ○ (heatmap) | ○ (併用必須) |

「Chart と表の併用」が IB 標準。Chart は視覚で「方向性」を、表は数字で「精度」を補完する。

### 1.5 「データインク」最小化の判断順序

新しい chart を実装するときは以下の順で削っていく。

1. **3D 効果** を削る (perspective, shadow, bevel)
2. **背景色** を削る (plot area の塗りつぶしを no-fill に)
3. **chart 外枠 border** を削る
4. **vertical gridline** を削る (時系列軸で特に)
5. **Y 軸の minor gridline** を削る
6. **凡例の box border** を削る
7. **legend の background** を削る
8. **不必要な data label** を削る (折れ線で全点 label は禁、最後の点のみ等)
9. **副軸 (secondary axis)** を削る (本当に必要か再検討)
10. **trendline** を削る (説明できる根拠があるときだけ残す)

これを終えた後に残ったインクが「data-ink」。理想は data-ink ratio = 1.0 だが、IB pitchbook では 0.85-0.95 を目安にする (axis label / source line は data-ink でないが必要)。

### 1.6 「Chart は意思決定を促す」原則

Pitchbook の chart は **読者に意思決定を促す** ためにある。装飾や情報羅列が目的ではない。各 chart は以下の 3 質問に答えられねばならない。

1. **What's the message?** — 1 行の見出し (sub-title) に書けるか
2. **What's the source?** — Source line で出典を保証できるか
3. **What's the action?** — 読者がこの chart を見たあとに何を決定するのか

例:
- Football field → "DCF mid case ¥120B が precedent transaction レンジ ¥95-145B に収まる" → action: bid range を ¥110-130B で設定
- Waterfall → "EBITDA Y1 → Y5 で +¥4.2B 改善のうち 60% は volume 由来、25% は price、15% は cost reduction" → action: volume driver の検証を deep dive
- Sensitivity → "WACC 12% / TV growth 2.5% で EV ¥120B、いずれかが ±100bps 振れるとレンジ ¥95-145B" → action: WACC 算定根拠の sensitivity を IC で議論

---

## 2. 色彩規格 (IB Chart Palette)

### 2.1 基本原則 — 「Color is functional, not decorative」

IB chart の色は **機能** にしか使わない。「綺麗だから」「ブランドだから」で色を選ぶのは禁。具体的には:

- 同一カテゴリ内 series の **区別** (Series 1 / Series 2 / Series 3)
- **強調** (1 バーだけ accent で目立たせる)
- **意味の符号化** (positive / negative / neutral)
- **比較群と被比較群** の区分 (target company vs peer median)

色を使うべきでない場面:
- ブランドカラーで全 chart を統一しようとする (見た目に飽きる、機能を失う)
- 単一系列の bar に 7 色レインボー (openpyxl default) — **絶対禁止**
- 1 種類の意味なのに saturation を変えて偽の階層を作る

### 2.2 IB Chart Primary Palette (3 + 2 構造)

本 skill の標準パレット。`scripts/ib_format.py` に実装する `IB_CHART_PALETTE` の根拠。

| Slot | 役割 | Hex | 名前 (本書呼称) | RGB |
|---|---|---|---|---|
| Series 1 | Main / Target / Primary | `#1F3A66` | IB Navy | (31, 58, 102) |
| Series 2 | Comparison / Peer / Secondary | `#666666` | Slate Gray | (102, 102, 102) |
| Series 3 | Accent / Highlight | `#ECC85A` | Brand Gold | (236, 200, 90) |
| Series 4 | Tertiary | `#7A8FAB` | Navy 60% | (122, 143, 171) |
| Series 5 | Quaternary | `#B8C2D1` | Navy 30% | (184, 194, 209) |

**配色設計の根拠**:
- Series 1 (Navy `#1F3A66`) は Goldman Sachs 系 pitchbook で多用される深い紺。Brand Primary `#008A80` と被らないように、xlsx chart 内では Navy を主軸にする (Brand Primary は CTA / pptx 用、xlsx の chart 主体には不向き)。
- Series 2 (Slate Gray `#666666`) は中性的でどの数列とも喧嘩しない。Peer median や baseline に最適。
- Series 3 (Brand Gold `#ECC85A`) は accent で **1 chart 1 か所** 限定。
- Series 4-5 は Navy 系を 60% / 30% に薄めた値。色相を変えずに saturation だけで階層を作る。

**避ける色**:
- 純黒 `#000000` — IB では `#2D332E` (Ink) または `#1F3A66` (Navy)
- 鮮やか赤 `#FF0000` — `#C04A4A` (muted Danger) を使う
- 鮮やか緑 `#00FF00` — `#3F8F5E` (muted Success)
- ネオン全般、グラデーション、半透明オーバーレイ

### 2.3 Stop-light 色の限定使用

「赤 = 悪い、緑 = 良い、黄 = 注意」の信号色 (stop-light) は誤読を誘発しやすい。以下の限定場面でだけ使う。

| 場面 | 色 | Hex | 注意 |
|---|---|---|---|
| Heatmap で正/中立/負 を表現 | 赤 / 白 / 緑 | `#C04A4A` / `#FFFFFF` / `#3F8F5E` | カラーブラインド配慮で必ずセル値併記 |
| Waterfall で正/負 bar | 青 (positive) / muted 赤 (negative) | `#1F3A66` / `#C04A4A` | 緑 ではなく **青** を positive にする (誤読が少ない) |
| KPI tile の上下矢印 | 上 = `#3F8F5E` / 下 = `#C04A4A` | — | アイコン形状でも符号化 |

**Football Field の Low/Mid/High に stop-light を使わない**。代わりに同色の saturation grading を使う (§6.5)。

### 2.4 Heatmap 専用 Diverging Palette

Sensitivity heatmap の 2 変数 (例: WACC × Terminal growth) は **中央色から両端へ発散** する diverging palette を使う。Sequential (単色濃淡) は不向き — 「中央が基準」というメタ情報が失われる。

推奨 Diverging Palette (5 段階):

| 段階 | Hex | 役割 |
|---|---|---|
| 強負 | `#C04A4A` | 中央比 -X% 以上 |
| 弱負 | `#E8B5B5` | 中央比 -X%/2 |
| 中央 | `#FFFFFF` (or `#F4F1E8` 紙色) | Base case |
| 弱正 | `#B5D9C2` | 中央比 +X%/2 |
| 強正 | `#3F8F5E` | 中央比 +X% 以上 |

**色の閾値設定**: 中央値 (base case) からの偏差を ±X% で設定。一般的に WACC × g の sensitivity では中央値 ±20% を端に置く。

**カラーブラインド配慮**: 赤緑色覚特性 (deuteranopia) では `#C04A4A` と `#3F8F5E` の弁別が弱い。**必ずセル値を併記** し、色だけに頼らない。代替として青-黄 diverging (`#1F3A66` ↔ `#ECC85A`) も使えるが、IB 慣習では赤-緑が圧倒的に多い。

### 2.5 Categorical Palette (分類数 ≥ 4 の場合)

Series 数が 5 を超える場合 (例: 7 業界比較) は qualitative palette を使う。ただし **5 を超えたら small multiples に分けることを優先**。やむを得ない場合の 7 色:

| # | Hex | 名前 |
|---|---|---|
| 1 | `#1F3A66` | Navy |
| 2 | `#004F49` | Brand Primary deep |
| 3 | `#666666` | Slate Gray |
| 4 | `#ECC85A` | Brand Gold (accent) |
| 5 | `#8B6F47` | Earth brown |
| 6 | `#5C7A99` | Steel blue |
| 7 | `#A8A8A8` | Light gray |

**Note**: 7 色で済まない場合は chart 設計が破綻している。グルーピングを再考する。

### 2.6 Background / Plot area / Gridline / Axis 色

| 要素 | Hex | 備考 |
|---|---|---|
| Chart background | `#FFFFFF` | 純白 (本紙 `#ECE9E1` は xlsx 標準では使わない、印刷時のみ pptx で適用) |
| Plot area | `#FFFFFF` | 透明または白 |
| Gridline (major, horizontal) | `#CCCCCC` | faint gray、線幅 0.5pt |
| Gridline (minor) | (削除) | 削る |
| Axis line | `#666666` | Slate Gray |
| Axis tick | `#666666` | Slate Gray |
| Border (chart frame) | (削除) | 外枠は no border |

### 2.7 色のアクセシビリティ (WCAG 配慮)

- **Contrast ratio**: bar 上の data label は背景色と 4.5:1 以上 (WCAG AA)。Navy bar 上の白文字は ratio 約 9:1 で十分。Gold bar 上の白文字は ratio 約 2:1 で **不可** → Gold bar 上は黒系文字 (`#2D332E`) を置く。
- **色覚特性**: 赤緑色覚特性 (約 5% 男性) を考慮し、「色だけ」で意味を伝えない。アイコン形状、テキスト、パターン (hatching) のいずれかを併用。
- **印刷モノクロ**: pitchbook は時にモノクロ印刷される。Saturation の階層を予め設計し、グレースケール変換しても弁別可能か確認。

### 2.8 色適用の `_terminology` 連携

[`_terminology.md §1`](_terminology.md) で定義された IB Color Code (Hard input `#0000FF` 等) は **セル文字色** であり、**chart series 色とは別系統**。混同してはならない。

| 系統 | 適用先 | 例 |
|---|---|---|
| _terminology §1 | セル font color | Hard input → 青 `#0000FF`、Formula → 黒 |
| 本書 §2 | Chart series fill / line color | Series 1 → Navy `#1F3A66` |

両者を同じ palette で運用すると見分けが付かなくなる。本書のチャート色は **chart 内専用** と理解する。

---

## 3. Typography (Chart 内文字)

### 3.1 フォント選択

IB pitchbook では Arial / Helvetica が標準。openpyxl の chart は Latin face として `Arial` を指定する。Calibri (Office default) は xlsx セル本体では許容されるが、chart 内では Arial の方が圧倒的に多い (実観察)。

| 要素 | Font Family | 理由 |
|---|---|---|
| Chart 内すべて | Arial | IB 標準。Helvetica で代用可だが macOS / Windows で表示差が出るため Arial 固定 |
| 日本語混在時 | Yu Gothic UI / Noto Sans JP | 和文部分のみ。英数字は Arial を維持 |

**禁止**: Times New Roman, Comic Sans, ブラケット系装飾フォント、Calibri (chart 内のみ禁、セル本体では可)。

### 3.2 サイズと weight (chart 要素別)

| 要素 | Size | Weight | Italics | Color | 備考 |
|---|---|---|---|---|---|
| Chart title | 12pt | Bold | No | `#2D332E` (Ink) | 左寄せ |
| Sub-title (sub-headline / takeaway) | 10pt | Regular | No | `#2D332E` | Title 下、メッセージ 1 行 |
| Axis title | 10pt | Bold | No | `#2D332E` | 単位 (US$M / %) を含む |
| Axis tick label (numeric) | 9pt | Regular | No | `#666666` | — |
| Axis tick label (category) | 9pt | Regular | No | `#666666` | — |
| Data label | 9pt | Regular | No | `#2D332E` | Bar 上は白 (Navy bar) または黒 (Gold bar) |
| Legend | 9pt | Regular | No | `#2D332E` | — |
| Source line | 8pt | Regular | **Italics** | `#666666` | Chart 下右 |
| Footnote | 8pt | Regular | No | `#666666` | Chart 下左、(1)(2) で番号 |

### 3.3 数値書式 (Number Format)

軸 tick / data label の数値は **単位を統一** し、軸タイトルに単位を出す。

| シナリオ | 軸タイトル | Tick label | Data label |
|---|---|---|---|
| Revenue (US$M) | "Revenue (US$M)" | `#,##0` | `#,##0` |
| Revenue (¥B) | "Revenue (¥B)" | `#,##0.0` | `#,##0.0` |
| Margin % | "EBITDA margin (%)" | `0.0%` | `0.0%` |
| Multiple | "EV / Revenue (x)" | `0.0"x"` | `0.0"x"` |
| Headcount | "Headcount" | `#,##0` | `#,##0` |
| Growth rate | "YoY growth (%)" | `0.0%` | `+0.0%;-0.0%` (符号付き) |

**Best practice**:
- 桁数は **3 桁以下に抑える**。10,000 を超える数字は単位を上げる (千 → 百万)。
- 千区切りは `,` (US) で固定。和文混在でも chart 内は US convention。
- マイナスは `(123)` ではなく `-123` (chart 内のみ。セル本体では `(123)` も可)。chart の DataLabel で括弧表記すると visual の流れが崩れる。

### 3.4 Title / Sub-title の書き方

IB pitchbook chart の title / sub-title は **「結論先行」のジャーナリズム見出しスタイル**。

| 構造 | 例 |
|---|---|
| Title (factual) | "Revenue trajectory FY22A-FY27E" |
| Sub-title (conclusion) | "Y/Y growth accelerates from 38% (FY24E) to 55% (FY26E) on enterprise tier launch" |

**避けるべきタイトル**:
- "Revenue chart" (情報ゼロ)
- "売上の推移" (factual だが action なし)
- "Amazing growth!" (誇張、煽り語)

### 3.5 Axis Title の書き方

軸タイトルは **必ず単位を含める**。「Revenue」だけでは US$M なのか ¥B なのか分からない。

| 良い例 | 悪い例 |
|---|---|
| "Revenue (US$M)" | "Revenue" |
| "EBITDA margin (%)" | "Margin" |
| "FY (Fiscal Year, ending Mar)" | "Year" |
| "Headcount (FTE)" | "People" |

X 軸 (時間軸) は通常省略可だが、不規則 fiscal year (Mar 末等) や暦年 / 会計年度の混在がある場合は明示する。

### 3.6 Source Line と Footnote の規約

IB pitchbook の source line / footnote は **必ず chart の下** に置く。位置と書式:

| 要素 | 位置 | 書式 |
|---|---|---|
| Footnote | Chart 下、左寄せ | "Note: (1) FY24-27 are management estimates per business plan dated Mar-2024." |
| Source line | Chart 下、右寄せ (or footnote の次行) | "Source: Company filings, S&P Capital IQ as of Mar-2024." |

**書き方**:
- Source は **誰が** **いつ** の情報源かを必ず書く
- Multiple sources は `;` で区切る: "Company filings; Bloomberg; S&P Capital IQ"
- Note は `(1)(2)(3)` で番号付け、chart 内 data label 横に対応番号を superscript で

### 3.7 openpyxl での font 設定の落とし穴

openpyxl の `chart.title` は文字列を渡すと default font になり、Arial 12pt Bold にならない。明示的に `RichText` で組む必要がある。

```python
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import (
    Paragraph, ParagraphProperties, CharacterProperties,
    RichTextProperties, RegularTextRun
)

def make_chart_title(text: str, size: int = 1200, bold: bool = True) -> RichText:
    """size は EMU 単位の 100 倍 (12pt = 1200)"""
    cp = CharacterProperties(sz=size, b=bold)
    cp.latin = "Arial"  # Latin face を Arial に固定
    pp = ParagraphProperties(defRPr=cp)
    rtr = RegularTextRun(rPr=CharacterProperties(sz=size, b=bold), t=text)
    p = Paragraph(pPr=pp, r=[rtr])
    return RichText(bodyPr=RichTextProperties(), p=[p])
```

詳細は §17 (実装パターン) で展開する。

---

## 4. Axis / Gridline / Tick の標準

### 4.1 Y 軸 (Value axis) の原則

| 設定 | 標準 | 理由 |
|---|---|---|
| 起点 | **0 起点固定** (bar chart) | Lie factor を 1 に保つ。0 起点でない bar chart は IB では禁 |
| 起点 (line chart) | データ最小値の少し下 (auto) | line chart は 0 起点でなくても可、ただし source line に "Y axis truncated for clarity" を明示 |
| 終点 | データ最大値の +5-10% 余裕 | キツキツに上端に到達するのは見栄え悪い |
| Major tick | 4-7 区分 | 8 以上は読めない、3 以下は粗い |
| Minor tick | 削除 | 視認性低下 |
| Major gridline | 表示 (faint gray `#CCCCCC`, 0.5pt) | 値の読取補助 |
| Minor gridline | 削除 | — |
| Tick mark direction | "in" (内向き) | "out" / "cross" は装飾的、IB は内向きが多い |
| Axis line | 表示 (`#666666`, 0.75pt) | data area との境界明示 |
| Number format | §3.3 参照 | 単位は軸タイトルへ |

### 4.2 X 軸 (Category / Value axis) の原則

| 設定 | 時系列 (category) | Scatter (value) |
|---|---|---|
| 起点 | first period 直前 | データ最小値の少し下 |
| 終点 | last period 直後 | データ最大値の少し上 |
| Major tick | 全 period | 4-7 区分 |
| Minor tick | 削除 | 削除 |
| Major gridline | **削除** (時系列では vertical gridline 不要) | (scatter のみ) faint gridline |
| Tick label rotation | 0° (水平) または 45° (FY ラベルが長い場合) | 0° |
| Axis line | 表示 | 表示 |

### 4.3 X 軸の「広がり」問題と解決

ユーザーから指摘のあった **「x 軸広がりなし」** 問題は、openpyxl で chart を default 生成すると plot area が窮屈になる現象を指す。原因と対策:

| 原因 | 対策 |
|---|---|
| Chart 内に title / legend が plot area を圧迫 | `chart.layout` で `ManualLayout` を使い plot area を明示的に確保 |
| Axis label が長く plot area が縮む | label rotation を 45° または短縮 (FY24 → '24) |
| Default cell anchor (`OneCellAnchor`) で chart size が固定されない | `TwoCellAnchor` で対角 2 セル指定 (例: B25:K40) |
| Chart 高さに対して bar 数が多い | bar gap (`gapWidth`) を 50-100 に設定 (default 150 は広すぎる) |

実装例:

```python
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.drawing.spreadsheet_drawing import TwoCellAnchor, AnchorMarker

# Plot area を chart 内 75% に確保
chart.plot_area.layout = Layout(
    manualLayout=ManualLayout(
        x=0.10, y=0.15,        # 左上 (chart 全体 100% に対する比率)
        w=0.85, h=0.70,        # plot area の幅 / 高さ
        xMode="edge", yMode="edge",
    )
)

# Bar の gap を狭める
chart.gapWidth = 75   # default 150 → 75 で bar 同士が近くなり「広がる」見た目
chart.overlap = 0     # 同 category 内の series 重なり (0=隣接, 100=完全重なり)
```

### 4.4 Secondary axis (副軸) の使用

副軸は「同じ chart に異なる単位の 2 系列」を載せる必要があるときだけ使う。乱用すると読み手が混乱する。

| 場面 | 副軸を使う | 副軸を使わない |
|---|---|---|
| Revenue (US$M) と Revenue YoY% | ○ | × (line を 2 つ別 chart にする方がベター) |
| Headcount と Revenue per employee | ○ | × |
| 同単位で桁が違う | × | ○ (log scale を使う方が筋) |

副軸を使うとき:
- 主軸 (Primary, 左) は **bar**、副軸 (Secondary, 右) は **line** が IB 慣習
- 主軸の起点 0 / 副軸の起点 0 を必ず揃える (左右で 0 線がずれると誤読)
- Legend に主軸 / 副軸を明記 (例: "Revenue (LHS)" / "Growth % (RHS)")

### 4.5 Log scale の使用

Log scale は **断りなしに使うと誤読を誘発** する。使うときは axis title に "(log scale)" と明示。使う場面:

| 場面 | Log scale | 理由 |
|---|---|---|
| TAM bottom-up で桁が大きく違う複数市場 | ○ | linear だと小市場が見えない |
| ARR seed → IPO の長期成長 (1000x) | ○ | linear だと初期が潰れる |
| 通常の 5 年予測 | × | 過剰、誤読要因 |

### 4.6 Axis 設定の openpyxl 実装

```python
from openpyxl.chart import BarChart
from openpyxl.chart.axis import ChartLines

chart = BarChart()
# Y 軸 (value axis)
chart.y_axis.majorTickMark = "in"
chart.y_axis.minorTickMark = "none"
chart.y_axis.majorGridlines = ChartLines()  # gridline 表示
# Gridline の色は SpPr (ShapeProperties) 経由
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.colors import ColorChoice
chart.y_axis.majorGridlines.spPr = GraphicalProperties(
    ln=LineProperties(solidFill="CCCCCC", w=6350)  # w は EMU、0.5pt = 6350
)
chart.y_axis.number_format = "#,##0"
chart.y_axis.title = "Revenue (US$M)"

# X 軸 (category axis)
chart.x_axis.majorTickMark = "in"
chart.x_axis.minorTickMark = "none"
chart.x_axis.majorGridlines = None  # 時系列では vertical gridline 削除
```

---

## 5. Layout / Aspect Ratio / Plot Area

### 5.1 Aspect Ratio (縦横比) のチャート種別ガイド

| Chart 種別 | 推奨 ratio (W:H) | width × height (cm) | 理由 |
|---|---|---|---|
| Football field | 4:3 | 16 × 12 | 縦に method 5-7 行並ぶため縦長やや必要 |
| Sensitivity heatmap | 1:1 (square) | 12 × 12 | 5×5 / 7×7 の正方形格子 |
| Waterfall (bridge) | 16:9 | 18 × 10 | 横に bar 6-10 並ぶ |
| Bar chart (時系列 4-12 期) | 16:9 | 16 × 9 | 標準 |
| Line chart (時系列) | 16:9 | 16 × 9 | 標準 |
| Stacked bar (mix) | 4:3 or 16:9 | 14 × 10 or 16 × 9 | mix 数による |
| Scatter (comp 散布) | 4:3 | 14 × 10 | 数学的散布で 1:1 が綺麗だが y 軸タイトル分横に余裕 |
| Cohort layer cake | 16:9 wide | 20 × 8 | 横に 24 月並ぶ |

**openpyxl での実装**:
```python
chart.width = 16   # cm
chart.height = 9   # cm
```

### 5.2 Plot Area の位置 (Manual Layout)

`chart.plot_area.layout` に `Layout(manualLayout=ManualLayout(...))` を渡す。値は chart 全体 (100%) に対する比率 (0-1)。

**標準値 (本書推奨)**:
```python
ManualLayout(
    x=0.10,    # 左マージン (10%): y 軸 title + tick label 分
    y=0.15,    # 上マージン (15%): chart title + sub-title 分
    w=0.85,    # plot area 幅 (85%)
    h=0.70,    # plot area 高さ (70%)
    xMode="edge", yMode="edge",
)
```

**Chart 種別ごとの調整**:

| Chart | x | y | w | h | 備考 |
|---|---|---|---|---|---|
| Football field | 0.20 | 0.10 | 0.75 | 0.75 | 左マージン広 (method 名長い) |
| Sensitivity heatmap | 0.12 | 0.15 | 0.83 | 0.70 | 標準 |
| Waterfall | 0.10 | 0.15 | 0.85 | 0.70 | 標準 |
| Bar chart | 0.10 | 0.15 | 0.85 | 0.70 | 標準 |
| Line chart | 0.10 | 0.15 | 0.85 | 0.70 | 標準 |
| Stacked bar | 0.10 | 0.15 | 0.78 | 0.70 | legend 右に 7% 確保 |
| Scatter | 0.12 | 0.10 | 0.83 | 0.75 | 標準 |

### 5.3 Legend の位置

| 位置 | openpyxl 値 | 推奨場面 |
|---|---|---|
| Right | `'r'` | 標準。series 2-4 |
| Bottom | `'b'` | series 5+ で右に置くと縦に並ばない |
| Top | `'t'` | あまり使わない |
| Left | `'l'` | 使わない |
| なし | `chart.legend = None` | series 1 のみのとき凡例不要 |

```python
chart.legend.position = 'r'
chart.legend.overlay = False  # plot area に重ねない
```

### 5.4 Chart Frame (外枠) の処理

IB では chart の外枠 (border) は **削る**。

```python
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties

chart.graphical_properties = GraphicalProperties()
chart.graphical_properties.line = LineProperties(noFill=True)  # 外枠なし
```

Plot area の border も同様に削る:
```python
chart.plot_area.graphicalProperties = GraphicalProperties()
chart.plot_area.graphicalProperties.line = LineProperties(noFill=True)
```

### 5.5 余白 (Margins) の感覚

Chart cell anchor で chart を埋める場合、anchor cell の隣接 row / column との間に **空行 / 空列を 1 つ確保** すると視覚的に整う。例: chart を `B25:K40` に置くなら、24 行目と 41 行目は空行に。

---

## 6. Football Field Chart (バリュエーションレンジ)

### 6.1 Football Field とは

複数の valuation method (DCF / Comps EV-Rev / Comps EV-EBITDA / Precedent transactions / 52-week high-low / etc.) それぞれの価格レンジを **横棒 (horizontal bar)** で重ね、target が「正当なレンジ」に収まるかを 1 枚で示す chart。M&A pitchbook の主役の 1 つ。

参考: 05_valuation_wacc.md §2.9 / §3 で計算ロジック展開済。本書は **可視化** に絞る。

### 6.2 構造 (Layout)

```
              Low  ──  Mid  ──  High         (US$M)
DCF Gordon       [────●────]
DCF Exit          [─────●─────]
Comps EV/Rev    [──────●──────]
Comps EV/EBITDA   [────●────]
Precedent          [─────●─────]
52W H-L              [──●──]
                  ↑
               Current price (vertical line)
```

- 縦軸: method 名 (5-7 個)
- 横軸: 価値レンジ (US$M / ¥B)
- 各 method = 1 横棒 (horizontal bar)。Low が左端、High が右端、Mid を marker (●) で内側に
- Current trading price (上場の場合) を **垂直線 (vertical line)** で全 bar を貫通させる

### 6.3 Series 設計

Football field は **floating bar** = 「Low から High までの bar」を描く必要がある。openpyxl の `BarChart` では直接 floating bar 機能はないが、以下の trick で実装可能。

**Trick 1: Stacked bar の 1 つ目を透明化**

```
Series 1 (Low value)    : 透明 fill (no-fill) → 「下駄」として機能
Series 2 (Range = High - Low) : Navy fill → 見える bar
```

これで Low 起点から High 終点まで Navy bar が浮かんで描かれる。Mid は別 series (scatter overlay) または data label で表現。

**Trick 2: 3 series stacked**

```
Series 1 (Low - 0)         : 透明
Series 2 (Mid - Low)       : 薄 Navy
Series 3 (High - Mid)      : 濃 Navy
```

Mid を境に色を変えて Low-Mid / Mid-High の区別を視覚化。Mid 値は連結境界で自然に分かる。

**推奨**: Trick 1 (Low / Range の 2 series stacked) + Mid を text label として bar 内に表示。

### 6.4 色設計

5-7 method を **同色** で揃えるのが IB 慣習。method ごとに色を変えない (情報過多)。

| 要素 | 色 |
|---|---|
| Range bar (Low-High) | Navy `#1F3A66` |
| Mid marker | Slate Gray `#666666` (●) |
| Current trading price (vertical line) | Brand Gold `#ECC85A` (1pt 実線) |
| Implied offer price (vertical line) | Muted Red `#C04A4A` (1pt 破線) |
| Bar の透明部分 | no-fill |

### 6.5 Mid Value の表現方法

Low / Mid / High の 3 値を表現する 3 つのアプローチ:

| 方法 | Pros | Cons |
|---|---|---|
| (a) Mid を data label で表示 | シンプル、追加 series 不要 | 重なる場合あり |
| (b) Mid を別 series の scatter overlay | 視覚的に明瞭 | 実装複雑、scatter と bar の混在 |
| (c) 3 stacked bar (Low→Mid→High) で saturation 違い | 視覚的に Low-Mid / Mid-High 区別 | 過剰演出感 |

**推奨**: (a)。Bar 中央付近に Mid 値を data label で。Bar 端 (Low / High) も data label で。

### 6.6 Method 並び順

| 並び (上から) | 理由 |
|---|---|
| 1. DCF (Gordon growth) | Intrinsic value、最も理論的 |
| 2. DCF (Exit multiple) | Intrinsic、ただし terminal が multiple |
| 3. Comparable companies (EV/Revenue) | Market multiple、early stage 主流 |
| 4. Comparable companies (EV/EBITDA) | Market multiple、profitable 企業向け |
| 5. Precedent transactions | M&A multiple、control premium 含む |
| 6. 52-week high-low (上場時) | Market sentiment、参考値 |
| 7. Analyst price target (上場時) | Sell-side コンセンサス、参考値 |

**起点を揃える**: 上から「intrinsic → market → transaction → sentiment」の順。実務によって Comps を上に置く流派 (early stage では DCF がノイズ) もあるが、本書は intrinsic 先行を推奨。

### 6.7 X 軸スケール

- 起点: 0 ではなく、**全 method の最小値の 0.9 倍** または "0 起点と全レンジの中央値の 0.5 倍" の小さい方
- 終点: 全 method の最大値の 1.05 倍
- 単位: 大型の場合 US$B、中型は US$M、日本は ¥B が標準
- Major tick: 5-7 区分

**注意**: Football field の x 軸は **0 起点でなくてよい**。理由は「value range が問題で、0 からの絶対距離は問題でない」ため。Bar chart の Y 軸 0 起点ルールとは別系統。ただし、x 軸の起点を明示するために axis line を表示する。

### 6.8 Vertical Line (current price / offer price) の追加

Vertical reference line を bar chart に重ねる方法:

**Approach A**: Scatter chart を combo で重ねる

```python
from openpyxl.chart import ScatterChart, Series
# ... bar chart 作成済 (chart_bar)

# Vertical line を scatter で表現: 同 x 値で y 軸を縦断
scatter = ScatterChart()
xvalues = Reference(ws, min_col=X_COL, min_row=Y_ROW, max_row=Y_ROW+N)  # 同じ x 値が縦に並ぶ
yvalues = Reference(ws, min_col=Y_COL, min_row=Y_ROW, max_row=Y_ROW+N)  # 0, 1, 2, ..., N (method index)
ser = Series(yvalues, xvalues, title="Current price")
ser.graphicalProperties.line.solidFill = "ECC85A"
ser.graphicalProperties.line.width = 12700  # 1pt = 12700 EMU
ser.smooth = False
scatter.series.append(ser)
chart_bar += scatter   # combo
```

**Approach B**: Conditional formatting で worksheet のセル背景に「線」を描く (chart 外で実装)

**推奨**: Approach A だが、openpyxl の combo chart は安定性に欠ける。代替として bar chart の data label に "← Current ¥120B" のような annotation を入れる方が pragmatic。

### 6.9 Implementation 完全版 (openpyxl)

§17.2 で完全な動作 code を示す。

### 6.10 ベンチマークレンジの妥当性チェック

Football field を作ったあとに必ず以下を確認:

1. **DCF Mid が 5 method の中央値の ±20% に収まる** か (極端な外れは仮定エラー)
2. **Comps EV/Revenue High** が **Comps EV/EBITDA High** を超えない (通常は EBITDA multiple の方が低い、ただし unprofitable 企業では話が逆)
3. **Precedent transactions** が **Comps companies** より **+15-30% 高い** (control premium)
4. Trading range (52w H-L) が target の ±15% に収まる (上場している場合)
5. Implied offer price が **Mid case の +20-40%** (control premium 含む) に収まる

これらが破綻しているとき、chart を出す前に valuation を再検証する (chart は症状を映すだけで、原因は別)。

---

## 7. Sensitivity Heatmap (感度 2 変数表)

### 7.1 Sensitivity Heatmap とは

DCF / LBO / IRR の **2 変数感度** を 5×5 〜 9×9 の格子で示し、cell ごとに値を表示しつつ背景色で偏差を可視化する chart。「Two-way data table」とも呼ぶ。

### 7.2 適用シーン

| 業務 | X 軸 | Y 軸 | セル値 |
|---|---|---|---|
| DCF | WACC (%) | Terminal growth (%) | EV (US$M) |
| DCF (Exit multiple) | WACC (%) | Exit multiple (x) | EV (US$M) |
| LBO | Entry multiple (x) | Exit multiple (x) | IRR (%) |
| LBO | Leverage (x EBITDA) | Exit year | IRR (%) |
| Acquisition | Synergy (US$M) | Premium (%) | Accretion / Dilution (% EPS) |
| SaaS | NRR (%) | Gross margin (%) | LTV/CAC |

### 7.3 格子サイズの選択

| サイズ | 場面 | 注意 |
|---|---|---|
| 3×3 | 概要レベル (Low/Mid/High × Low/Mid/High) | 解像度低、IC summary 向け |
| 5×5 | 標準 | IB main case |
| 7×7 | 詳細 | font 9pt 維持なら可 |
| 9×9 | 詳細解析 | セル小さい、A3 印刷推奨 |

**推奨**: 5×5。中央が base case、両端 ±200bps (WACC) / ±100bps (terminal g) 程度のレンジ。

### 7.4 背景色の Diverging Palette

§2.4 で定義した 5 段階。Base case (中央) を `#FFFFFF` (白) または `#F4F1E8` (本紙) にし、両端へ `#C04A4A` (負偏差) / `#3F8F5E` (正偏差) で発散。

**閾値設定**:
- Base case 値の ±5% 以内: 中央色
- ±5-10%: 弱色
- ±10-20%: 中色
- ±20% 以上: 強色

`openpyxl` の `ConditionalFormattingRule` で実装する (chart オブジェクトでなく、worksheet の cell range に対する conditional formatting)。詳細 §17.3。

### 7.5 セル書式

| 要素 | 書式 |
|---|---|
| セル値 | Arial 9pt, 中央揃え, 数値書式 `#,##0` (EV) または `0.0%` (IRR) |
| Row header (Y 軸) | Arial 9pt Bold, 右揃え, 数値書式 `0.00%` (WACC) |
| Col header (X 軸) | Arial 9pt Bold, 中央揃え, 数値書式 `0.00%` (terminal g) |
| Base case cell | Bold + 太罫線 (1.5pt) で枠を強調 |
| Border (cells) | Hairline (`#CCCCCC`, 0.25pt) 全周 |
| Header background | Light gray `#F2F2F2` (header と data の区別) |

### 7.6 Heatmap 専用 Sub-table の併設

Heatmap だけでは「base case 周辺の絶対値」しか分からない。以下の補助表を併設すると IB 標準。

| Sub-table | 内容 |
|---|---|
| Mid (base case) summary | Base case の値を強調表示 (例: "Base case EV = ¥120B at WACC 12%, g 2.5%") |
| Range summary | Min / Max / Range (Max-Min) / Range as % of Mid |
| Sensitivity | 各変数 ±100bps 振った場合の EV 変化 (delta) |

### 7.7 Anti-pattern

- **Diverging でなく Sequential** (単色濃淡) を使う → 中央が分からない
- **Cell 値を表示しない** → 色だけで読み取らせるのは誤読の元 (色覚特性配慮も)
- **格子の中央が base case でない** → 中央=base case は強い慣習
- **格子間隔が不均等** (例: WACC 8/10/11/12/15) → Symmetric (8/10/12/14/16 等) にする

### 7.8 Implementation 概要

Heatmap は厳密には「chart object」ではなく、worksheet の **cell range に対する conditional formatting** で実装する。openpyxl では:

```python
from openpyxl.formatting.rule import ColorScaleRule

rule = ColorScaleRule(
    start_type='min', start_color='C04A4A',
    mid_type='percentile', mid_value=50, mid_color='FFFFFF',
    end_type='max', end_color='3F8F5E',
)
ws.conditional_formatting.add(f"{start_col}{start_row}:{end_col}{end_row}", rule)
```

詳細実装は §17.3。

---

## 8. Waterfall Chart (EBITDA / ARR / Cash bridge)

### 8.1 Waterfall とは

開始値から終了値までを **構成要素ごとに足し引き** していく bridge chart。連結する flying bar で「累積」を視覚化する。

例 (EBITDA bridge Y1 → Y5):
```
Y1 EBITDA  ████ (¥2.0B)
+ Volume       ██   (+¥1.5B)
+ Price         █   (+¥0.8B)
- Cost mix         ▌  (-¥0.3B)
+ Mix shift          █ (+¥0.5B)
- FX                  ▌ (-¥0.2B)
─────────────
Y5 EBITDA  ███████  (¥4.3B)
```

### 8.2 適用シーン

| 業務 | 開始 | 構成要素 | 終了 |
|---|---|---|---|
| EBITDA bridge | Y1 EBITDA | Volume / Price / Mix / Cost / FX / Other | Y5 EBITDA |
| ARR bridge | Y1 ARR | New / Expansion / Contraction / Churn | Y2 ARR |
| Cash bridge | Beginning cash | OCF / CapEx / Debt / Equity | Ending cash |
| Headcount bridge | Y1 HC | Hire / Attrition / Re-org | Y2 HC |
| Margin bridge | Y1 GM | Volume / Mix / Price / Input / Productivity | Y5 GM |

### 8.3 色設計

| Bar 種別 | 色 | 備考 |
|---|---|---|
| Start / End (totals) | Slate Gray `#666666` | 基準値、中性 |
| Positive contribution | Navy `#1F3A66` | 正符号 |
| Negative contribution | Muted Red `#C04A4A` | 負符号 |
| Sub-total (任意) | Navy 60% `#7A8FAB` | 中間集計 |

**緑を使わない理由**: Positive は青、Negative は赤の方が誤読が少ない (色覚特性配慮)。緑/赤は信号機イメージで「危険」を強調するが、Waterfall は中立的な分解なので青/赤が適切。

### 8.4 構造的実装 (Stacked Bar Trick)

openpyxl には直接の Waterfall chart class がない (Excel 2016+ では native 実装あるが、openpyxl は読み込み・書き出し未対応)。Stacked bar の trick で実装する。

**3 series 構成**:
1. **Invisible base** (no-fill): 累積値の下まで、各 bar の「下駄」
2. **Positive** (Navy): 正の bar
3. **Negative** (Muted Red): 負の bar

各 bar (column) ごとに Invisible / Positive / Negative の値を計算する。

**例: Y1 EBITDA ¥2.0B → Volume +¥1.5B → Price +¥0.8B → ... → Y5 EBITDA ¥4.3B**

| Bar | Type | Invisible base | Positive | Negative | Total height |
|---|---|---|---|---|---|
| Y1 (start total) | total | 0 | 2.0 | 0 | 2.0 |
| + Volume | positive | 2.0 | 1.5 | 0 | 1.5 |
| + Price | positive | 3.5 | 0.8 | 0 | 0.8 |
| - Cost mix | negative | 4.0 | 0 | 0.3 | 0.3 |
| + Mix shift | positive | 4.0 | 0.5 | 0 | 0.5 |
| - FX | negative | 4.3 | 0 | 0.2 | 0.2 |
| Y5 (end total) | total | 0 | 4.3 | 0 | 4.3 |

Negative bar の Invisible base は「累積 - bar の値」(Cost mix のとき: 4.3 - 0.3 = 4.0)。

### 8.5 Connecting Line の追加

Waterfall の bar 同士を結ぶ horizontal line (累積を示す) は、IB pitchbook では明示するのが慣習。openpyxl では:

- 簡易: bar の data label に累積値を表示
- 中級: scatter overlay で累積値を line で結ぶ
- 上級: VBA / xlsxwriter の native Waterfall chart 機能を使う

**推奨**: 中級。Bar chart + scatter line の combo。

### 8.6 Data Label の規約

| Label の表示 | 内容 |
|---|---|
| Bar 上 (positive) | 値そのもの (例: "+¥1.5B") |
| Bar 下 (negative) | 値そのもの (例: "-¥0.3B") |
| Total bar 内 | 値そのもの (例: "¥2.0B" 太字) |
| Bar の下端 | カテゴリ名 (X 軸 tick label と同じ) |

正/負を符号付きで表示することで読み取り精度が上がる。Number format は `+#,##0.0;-#,##0.0` のような符号強調形式。

### 8.7 並び順 (構成要素の順序)

Waterfall の構成要素の並びは **ストーリー順** で決める。「アルファベット順」「金額大きい順」は誤った優先順位。標準的な並び:

| Bridge type | 推奨並び |
|---|---|
| EBITDA bridge | Volume → Price → Mix → Cost → FX → Other |
| ARR bridge | New ARR → Expansion → Contraction → Churn |
| Cash bridge | Operating CF → Investing CF (CapEx) → Financing CF (Debt / Equity) |
| Margin bridge | Volume / Mix → Price → Input cost → Productivity |

### 8.8 Anti-pattern

- **正と負を同色で表示** → 何が改善で何が悪化か瞬時に分からない
- **Connecting line なし** → 累積感が消える
- **構成要素を 10 個以上並べる** → 過密、読めない (5-7 個に集約)
- **「Other」が大きい (合計の 15% 以上)** → 分解不足。re-bucket する
- **総額 / 構成要素の縦軸スケールが微妙** → 構成要素が小さく見えて誤読
- **負 bar の塗りつぶしを赤一色** → muted red `#C04A4A` を使う

---

## 9. Bar Chart (Revenue / OpEx / Headcount)

### 9.1 基本構造

時系列 5-12 期の単一 KPI を bar で表示する最も基本的な chart。

| 設定 | 値 |
|---|---|
| Bar 色 | Navy `#1F3A66` (single series 時) |
| Bar gap (gapWidth) | 75 (default 150 だと隙間広すぎ、x 軸広がりが弱まる) |
| Bar overlap | 0 (default、単 series で意味なし) |
| Y 軸起点 | **0 起点固定** (これ譲れない) |
| Y 軸 gridline | Major のみ、faint gray |
| X 軸 gridline | なし |
| Data label | 全 bar 上に表示 (期間 ≤ 8 のとき) |
| Legend | 単 series ならなし、multi-series なら right |

### 9.2 Data Label の表示判定

| 期間数 | Data label |
|---|---|
| ≤ 8 | 全 bar に表示 |
| 9-12 | 端 (最初/最後) と max/min のみ |
| 13+ | 表示せず、Y 軸 gridline で読み取り |

### 9.3 Multi-series Bar (Clustered)

複数 series (例: target vs peer) を並べる場合:

| Series 数 | gapWidth | overlap | 推奨 |
|---|---|---|---|
| 2 | 100 | -10 | やや離す |
| 3-4 | 75 | 0 | 標準 |
| 5+ | (集約推奨) | — | small multiples に分割 |

色は §2.2 の Series 1-3 順に。Target は Navy、Peer median は Slate Gray、Highlight は Brand Gold。

### 9.4 Highlight Bar (1 つだけ強調)

「過去 5 年で FY24 だけ強調したい」場合は **特定 bar の色だけ Brand Gold** に変える。openpyxl では:

```python
from openpyxl.chart.marker import DataPoint
# series 0 の point 3 (4 番目) だけ色を変える
dp = DataPoint(idx=3)
dp.graphicalProperties = GraphicalProperties(solidFill="ECC85A")
chart.series[0].dPt.append(dp)
```

### 9.5 Anti-pattern

- **7 色レインボー** (openpyxl default) → §2.2 の palette 使用
- **3D bar** → 禁止
- **Y 軸非ゼロ起点** → 禁止 (line chart は許容)
- **Data label が bar に重なる** → label position を `outEnd` (上)

---

## 10. Line Chart (ARR / Headcount trend)

### 10.1 基本構造

時系列の連続 KPI (ARR、headcount、cash balance) を line で表示。Bar chart より trend / slope が見やすい。

| 設定 | 値 |
|---|---|
| Line 色 | Navy `#1F3A66` (single series), §2.2 順 (multi) |
| Line 太さ | 2.25pt (default 1.5pt より太い方が pitchbook 印刷で見える) |
| Marker | 端 (start/end) と max/min のみ、内部点は marker なし |
| Y 軸起点 | データ最小値の少し下 (auto) でも可、ただし source line で truncation を明示 |
| Y 軸 gridline | Major のみ |
| X 軸 gridline | なし |

### 10.2 Marker の規約

「全点に marker を打つ」と過密になる。以下の限定で:

| Marker を打つ点 | 理由 |
|---|---|
| First point | Trend の起点を明示 |
| Last point | Trend の終点 (現在 / 予測終端) |
| Max / Min | 極値を強調 |
| 重要 milestone | 例: Series A 調達時、IPO 時 |

それ以外は line のみ。Marker の形状は **circle** (●), 色は line と同色。サイズ 5pt。

### 10.3 Multi-series Line

Series 2-3 が標準。4 以上は **small multiples に分割** (1 chart 1 KPI で 4 chart 並べる)。

凡例の位置は **right** (series 数 ≤ 3) または **直接 line の終端に label を付ける** (data label 形式)。後者は legend を読まずに済むため IB 慣習で好まれる。

```python
# 終端の data label
from openpyxl.chart.label import DataLabel, DataLabelList
chart.dataLabels = DataLabelList(showVal=False, showCatName=False)
# 終端だけに label を付けるのは python レベルでは困難 (xlsx 仕様で点単位 label 困難)
# → series.dLbls = DataLabelList(...) して全点 label にし、内部点は font 透明化する hack もある
```

実務では legend を使う方が openpyxl では実装容易。

### 10.4 Trend Line (回帰線) の使用

Trend line (linear / exponential) は **Excel native 機能** で追加できるが、IB pitchbook では限定的。使う場面:

| 場面 | Trend line | 理由 |
|---|---|---|
| 5+ 期の noisy series で大局を示す | ○ | Visual aid |
| 5 期未満 | × | 回帰意味なし |
| 予測期間に重ねて延長 | × (使わない) | 「予測の根拠が回帰」と誤解される |

使うときは linear のみ (exponential は誤解を招く)、色は薄 gray、線種は dashed。

### 10.5 Forecast 期間の視覚区別

「過去実績 (Actuals)」と「将来予測 (Forecast)」を 1 枚の line chart で表現するとき、forecast 部分を視覚区別する。

| 方法 | 実装 |
|---|---|
| (a) Line を Solid → Dashed に切替 | Series を Actuals / Forecast の 2 本に分け、forecast は dashed line |
| (b) Vertical line で境界明示 | "Today" / "FY24E" の vertical line を入れる |
| (c) Background shading で forecast 区間を薄塗 | xlsx では実装困難、pptx で再描画 |

**推奨**: (a) + (b)。Forecast の line は同色 dashed、境界は vertical line と sub-title で明示。

### 10.6 Anti-pattern

- **Marker を全点に打つ** → 過密
- **Line が 4 本以上で同 chart に共存** → small multiples に分割
- **Forecast を実績と同じ書式で表示** → 区別なし、誤読
- **Trend line を予測根拠として presentation する** → 回帰は説明にならない

---

## 11. Stacked Bar (Revenue mix / Cohort layer cake)

### 11.1 構造

複数のカテゴリの構成比を時系列で示す。例: Revenue を Product A / B / C に分解して時系列 stacked bar、または cohort retention の「layer cake」(各 cohort を積み上げて total ARR の構成を示す)。

### 11.2 100% Stacked vs Absolute Stacked

| 種別 | 用途 | 軸 |
|---|---|---|
| Absolute stacked | 各カテゴリの絶対値も比率も両方見せたい | Y 軸 = 絶対値 |
| 100% stacked | 比率だけ見せたい | Y 軸 = 100% |

**推奨**: Absolute stacked。比率だけ示すと「総額の伸び」情報を失う。

### 11.3 色設計

| Stack 数 | Palette |
|---|---|
| 2 | Navy + Slate Gray |
| 3 | Navy + Slate Gray + Gold |
| 4 | Navy + Brand Primary deep + Slate Gray + Gold |
| 5+ | §2.5 categorical palette (or small multiples 分割) |

**Stack 順序**: 下から「最大カテゴリ → 最小カテゴリ」または「主力 → 補助 → 新規」のストーリー順。

### 11.4 Cohort Layer Cake

SaaS の cohort retention で、各 cohort (Q1-2022 / Q2-2022 / ... / Q4-2024 など 12 cohort) を時系列で積み上げて total ARR の構成を示す。

```
ARR (¥M)
        ████████████████████  Q4-2024 cohort
       ███████████████████ ▒  Q3-2024 cohort
      ██████████████████ ▒▒
     █████████████████ ▒▒▒
    ████████████████ ▒▒▒▒
   ███████████████ ▒▒▒▒▒
  ──────────────────────────  →  time
  Q1-22  ...  Q4-24
```

- 各 cohort は別 series
- 古い cohort ほど下に積む (時系列の cohort が上に追加される)
- 色は old → new で saturation を上げる (古いほど薄、新しいほど濃)

### 11.5 Stack Label の配置

| 配置 | Pros | Cons |
|---|---|---|
| Inside (segment 内) | Bar 内で比率が直感的 | Segment 小さいと label 切れる |
| Outside (segment 横) | 全 label 表示可 | Bar から離れて読みにくい |
| End of bar (total) | Total を強調 | Segment 内訳が分からない |

**推奨**: Total は End of bar、segment 内訳は legend のみ (label は付けない、過密回避)。

### 11.6 Anti-pattern

- **Stack 数 6 以上で同色階層** → 小 segment が見えない
- **Stack 順序が時期によって変わる** → 同じ category は固定位置
- **100% stacked で絶対値の伸びを失う** → absolute stacked と併設

---

## 12. Scatter Plot (Multi-Comp 散布図)

### 12.1 構造

2 変数で複数企業 (peer set) の位置関係を示す。例: Revenue Growth (X) × EBITDA margin (Y) で「Rule of 40」を可視化、または EV/Revenue (X) × NTM Growth (Y) で valuation premium を示す。

### 12.2 適用シーン

| Use case | X | Y | Note |
|---|---|---|---|
| Rule of 40 | Revenue growth (%) | FCF margin (%) | 対角線で R40 = 40% を表示 |
| Valuation premium | NTM growth (%) | EV/NTM Rev (x) | 回帰線で peer 平均を |
| TAM × CAC | TAM (US$B) | CAC payback (months) | 「効率市場」の象限 |
| Margin × Scale | Revenue (US$M) | Gross margin (%) | Scale benefit の検証 |

### 12.3 設計の原則

| 要素 | 値 |
|---|---|
| Marker shape | ● (circle) for peers, ★ (filled triangle) for target |
| Marker size | 7-10pt |
| Color | Peer = Slate Gray、Target = Brand Gold (or Navy で強調) |
| Label | Company name を marker 横に直接表示 (legend は使わない) |
| Quadrant lines | 中央値で十字線 (任意) |
| Diagonal line | Rule of 40 のとき X+Y=40 の対角線 |

### 12.4 Label 配置

Scatter plot の label は **常に label 機能** (data label, with category name) で表示。Legend は使わない。理由は scatter で legend が機能しないため (どの marker がどの会社か legend では分からない)。

```python
from openpyxl.chart.label import DataLabel, DataLabelList
chart.dataLabels = DataLabelList(showCatName=True, showVal=False)
```

Label 位置は marker の **right** が default。重なる場合は手動で調整。

### 12.5 象限解釈

4 象限に意味を持たせる場合は象限ラベル (Q1: "High growth, high margin" 等) を chart 角に配置。象限色を薄く塗ると視認性向上だが、IB では装飾的すぎるので避けることが多い。

### 12.6 Anti-pattern

- **Bubble (3 変数)** → 大きさが知覚しにくい (Cleveland & McGill 順位 6)、避ける
- **Marker が全部同色同形状** → target が分からない
- **Label の重なり** → 手動調整必須
- **対角線・回帰線が暗黙** → 必ず source line / sub-title で説明

---

## 13. Pie Chart は避ける (代替案)

### 13.1 Pie が悪い理由

Cleveland & McGill 順位 5 (角度) は、人間が比較的読みにくいエンコーディング。とくに以下が問題:

1. **角度の知覚誤差が大きい** — 35% と 40% の sector を見分けるのは困難
2. **複数 pie の比較ができない** — 2 つの pie を見比べるのは bar より遥かに難しい
3. **総額情報が消える** — 比率のみで絶対値が見えない
4. **3D pie は最悪** — 透視で奥の sector が小さく見える誤認

### 13.2 代替案

| 元の Pie | 代替 | 理由 |
|---|---|---|
| Revenue mix (3-5 categories) | Horizontal bar | 比較容易、絶対値併記可 |
| Geographic split | Horizontal bar (地域名 + 値) | 同上 |
| Customer segment (% of ARR) | Stacked bar (時系列) | 構成変化も見える |
| 1 数字の強調 (例: market share 35%) | KPI tile (大字 35%) | 1 数字なら chart 不要 |

### 13.3 Pie が許容される唯一の場面

**Pre-money cap table の owner% の simplified view** で 3-4 種類のホルダー (Founders / Investors / ESOP / Other) を示すときのみ、許容する流派がある。ただし horizontal bar での代替を推奨。

---

---

## 15. Chart 配置ルール (xlsx 内 anchor / size)

### 15.1 Sheet 内の配置位置

| Chart 種別 | 配置位置 | 理由 |
|---|---|---|
| KPI Dashboard chart | Section header の下、data table の **下** | スクロールせずに見える、data table を読んだ直後に chart |
| Football Field | Valuation summary section の **下** | DCF / Comps / Precedent table の下に集約 |
| Sensitivity Heatmap | Sensitivity table と **重ねる** (table 自体に conditional formatting) | Heatmap = table |
| Waterfall | Bridge data table の **右** または **下** | Y1 → Y5 EBITDA の table 隣 |
| Bar / Line | Data table の **右** (横長 chart の場合) または **下** | データ近接 |

### 15.2 Anchor (アンカー) 方式

openpyxl では 2 つの anchor 方式:

| 方式 | 挙動 | 推奨場面 |
|---|---|---|
| `OneCellAnchor` | 左上セルに固定、サイズは指定 | Chart size を維持したいとき (推奨) |
| `TwoCellAnchor` | 左上 + 右下セルに固定、Cell サイズに追従 | Cell サイズに伸縮させたいとき |

**推奨**: `ws.add_chart(chart, "B25")` の単純形式 (= `OneCellAnchor` 相当)。Chart size は `chart.width` / `chart.height` で cm 単位指定。

### 15.3 Chart Size の標準

| Chart 種別 | Width (cm) | Height (cm) | xlsx 行 × 列 (目安) |
|---|---|---|---|
| Football Field | 16 | 12 | 25 行 × 9 列 |
| Sensitivity (table 込) | 12 | 12 | 25 行 × 7 列 |
| Waterfall | 18 | 10 | 21 行 × 11 列 |
| Bar (時系列) | 16 | 9 | 19 行 × 9 列 |
| Line | 16 | 9 | 19 行 × 9 列 |
| Stacked bar | 16 | 9 | 19 行 × 9 列 |
| Scatter | 14 | 10 | 21 行 × 8 列 |
| Cohort layer cake | 20 | 8 | 17 行 × 11 列 |

(xlsx 行 × 列 は default row height 15pt / column width 8.43 を想定した粗い目安)

### 15.4 Page Break の配慮

xlsx を **印刷** することを想定すると、chart が page break で切れないように配置する。

- `ws.page_setup.fitToPage = True` を設定
- `ws.page_setup.fitToWidth = 1`、`fitToHeight = 0` (横は 1 ページ、縦は複数可)
- Chart は **page break の上** に置き、page break の直後に置かない (中途半端に切れる)

### 15.5 複数 Chart の並べ方

1 sheet に 4 chart を並べる「Quad chart」の場合:

```
B25:G35    H25:M35     ← Chart 1, 2 (上段)
B37:G47    H37:M47     ← Chart 3, 4 (下段)
```

- 各 chart の width / height を統一 (例: width 14cm, height 9cm)
- Chart 間に 1 列 / 1 行の余白 (G 列、36 行)
- 全 chart を同 sheet に置くなら sheet 名 "Charts" でまとめる

---

## 16. 業態 × Stage 別 Chart テンプレ

KPI Dashboard sheet (06_three_statement.md §9 参照) に置くべき chart は、**業態 (business model)** と **Stage** で異なる。本書では「最低限これを出せば IB レベル」というテンプレを業態別に定義する。

### 16.1 SaaS

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Pre-Seed | ARR (line) | Burn (bar, monthly) | Runway (line) | (—) |
| Seed | ARR (line) | Burn / Runway (bar+line, secondary axis) | Headcount (bar) | NRR (line, when MRR base ≥ 50) |
| Series A | ARR + YoY% (bar+line, secondary) | NRR / GRR (line) | LTV / CAC (scatter peer) | Burn multiple (line) |
| Series B | ARR (line, with forecast) | Cohort retention layer cake (stacked bar) | NRR / GRR (line) | Magic Number (bar quarterly) |
| Series C+ | ARR (line, with mgmt forecast) | Cohort layer cake | Rule of 40 (scatter, target vs peer) | Net New ARR bridge (waterfall) |
| Pre-IPO | ARR (line, multi-year forecast) | Cohort layer cake (24+ month) | Rule of 40 (scatter) | EBITDA margin trajectory (bar) |

### 16.2 Marketplace

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Seed | GMV (line) | Take rate % (line) | Active buyer / seller (line, dual) | (—) |
| Series A | GMV (line) | Take rate % (line) | Cohort retention (stacked bar) | Buyer / seller balance (bar) |
| Series B+ | GMV (line, with forecast) | Net Revenue (bar) | Liquidity (scatter, supply×demand) | Cohort GMV per buyer (line) |

### 16.3 D2C / EC

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Seed | Revenue (bar) | Gross margin % (line) | CAC payback (bar) | (—) |
| Series A+ | Revenue (bar, with channel mix stacked) | Gross margin trajectory | LTV / CAC by cohort (line) | Inventory turn (bar quarterly) |

### 16.4 Fintech (Lending)

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Seed | TPV (line) | Loan loss rate (bar) | Active borrowers (line) | (—) |
| Series A+ | TPV (line) | NIM % (line) | Vintage loss curves (line, multi-cohort) | Cost of funds (bar) |
| Pre-IPO | TPV (line) | Vintage analysis (small multiples) | NIM bridge (waterfall) | Capital adequacy (bar) |

### 16.5 Hardware

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Seed | Units shipped (bar) | Gross margin trajectory (line) | Inventory turns (bar) | (—) |
| Series A+ | Units (bar, with mix stacked) | Gross margin bridge (waterfall) | Yield % (line) | CapEx schedule (bar) |

### 16.6 Bio (Pre-revenue / Post-revenue)

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Pre-clinical | Burn (line) | Runway to next milestone (Gantt) | Probability of success cascade (waterfall) | (—) |
| Phase 2-3 | Burn (line) | rNPV by indication (bar) | Clinical timeline (Gantt) | Funding needs (bar) |
| Post-launch | Revenue (bar by indication) | Gross margin (line) | Patent cliff (timeline) | Pipeline NPV (waterfall) |

### 16.7 AI Foundation Model

| Stage | Chart 1 | Chart 2 | Chart 3 | Chart 4 |
|---|---|---|---|---|
| Seed | Compute spend (line) | Burn (line) | Headcount (bar) | (—) |
| Series A+ | Compute / revenue (line) | API revenue + tier mix (stacked bar) | Cost per inference (line) | Training run cost (bar by model) |

### 16.8 Stage 別 共通 chart (全業態)

業態によらず Pre-IPO / late-stage で必須:

| Chart | Sheet 配置 |
|---|---|
| Football Field (Valuation) | 16_Valuation |
| Sensitivity Heatmap (DCF WACC × g) | 16_Valuation |
| EBITDA bridge (Y1 → Y5, waterfall) | 09_KPI_Dashboard |
| Revenue trajectory (5 year, line+bar) | 09_KPI_Dashboard |
| Cap table dilution (stacked bar across rounds) | 12_CapTable |
| Exit Waterfall (per scenario, bar) | 12_CapTable |

---

## 17. openpyxl 実装パターン (code 例)

本章は `scripts/three_statement_builder.py` / `cap_table_builder.py` / `valuation_builder.py` から **コピペで使える** 完全な動作 code を 8 個示す。

### 17.1 共通: IB Chart Style 適用 helper

```python
# scripts/ib_format.py に追加する想定
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.fill import ColorChoice
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import (
    Paragraph, ParagraphProperties, CharacterProperties, RichTextProperties,
    RegularTextRun, Font as DrawingFont
)

# IB Chart Palette (canonical)
IB_CHART_PALETTE = {
    "primary":   ["1F3A66", "666666", "ECC85A", "7A8FAB", "B8C2D1"],  # Series 1-5
    "waterfall_pos": "1F3A66",
    "waterfall_neg": "C04A4A",
    "waterfall_total": "666666",
    "heatmap_neg": "C04A4A",
    "heatmap_mid": "FFFFFF",
    "heatmap_pos": "3F8F5E",
    "gridline": "CCCCCC",
    "axis_line": "666666",
    "current_price": "ECC85A",
    "offer_price": "C04A4A",
}

def _make_solid_fill(hex_rgb: str) -> GraphicalProperties:
    """Solid fill GraphicalProperties を hex から作る。"""
    gp = GraphicalProperties(solidFill=hex_rgb)
    gp.line = LineProperties(noFill=True)  # 輪郭線なし
    return gp

def _make_line(hex_rgb: str, width_pt: float = 2.25, dash: str = None) -> GraphicalProperties:
    """Line chart の line GraphicalProperties。width は pt → EMU 変換 (1pt = 12700)。"""
    width_emu = int(width_pt * 12700)
    line_props = LineProperties(solidFill=hex_rgb, w=width_emu)
    if dash:
        line_props.prstDash = dash  # "dash", "dot", "sysDash" 等
    gp = GraphicalProperties()
    gp.line = line_props
    return gp

def _make_no_fill() -> GraphicalProperties:
    """透明 fill (Football field の下駄、Plot area 透明化に使用)。"""
    gp = GraphicalProperties()
    gp.line = LineProperties(noFill=True)
    gp.solidFill = None
    return gp

def _make_chart_title(text: str, size_pt: int = 12, bold: bool = True) -> RichText:
    """Chart title を Arial 12pt bold で作る。"""
    sz = size_pt * 100  # openpyxl では pt × 100
    cp = CharacterProperties(sz=sz, b=bold)
    cp.latin = DrawingFont(typeface="Arial")
    pp = ParagraphProperties(defRPr=cp)
    rtr = RegularTextRun(
        rPr=CharacterProperties(sz=sz, b=bold, latin=DrawingFont(typeface="Arial")),
        t=text,
    )
    p = Paragraph(pPr=pp, r=[rtr])
    return RichText(bodyPr=RichTextProperties(), p=[p])

def apply_ib_chart_base(chart, title: str = None):
    """全 chart 共通の IB style を適用する。"""
    # Chart 外枠 削除
    chart.graphical_properties = GraphicalProperties()
    chart.graphical_properties.line = LineProperties(noFill=True)

    # Plot area 透明
    if chart.plot_area.graphicalProperties is None:
        chart.plot_area.graphicalProperties = GraphicalProperties()
    chart.plot_area.graphicalProperties.line = LineProperties(noFill=True)

    # Title
    if title:
        chart.title = _make_chart_title(title)

    # Y axis
    chart.y_axis.majorTickMark = "in"
    chart.y_axis.minorTickMark = "none"
    from openpyxl.chart.axis import ChartLines
    chart.y_axis.majorGridlines = ChartLines(
        spPr=GraphicalProperties(
            ln=LineProperties(solidFill=IB_CHART_PALETTE["gridline"], w=6350)
        )
    )

    # X axis
    chart.x_axis.majorTickMark = "in"
    chart.x_axis.minorTickMark = "none"
    chart.x_axis.majorGridlines = None  # vertical gridline 削除

    # Legend
    if chart.legend is not None:
        chart.legend.position = "r"
        chart.legend.overlay = False

    # Plot area layout
    chart.plot_area.layout = Layout(
        manualLayout=ManualLayout(
            x=0.10, y=0.15, w=0.85, h=0.70,
            xMode="edge", yMode="edge",
        )
    )
```

### 17.2 Football Field Chart

```python
# scripts/valuation_builder.py 内、Football Field section
from openpyxl.chart import BarChart, Reference

def build_football_field(ws, data_start_row: int, n_methods: int):
    """
    Data layout (前提):
      Row data_start_row:   header (Method | Low | Mid | High)
      Row data_start_row+1 .. +n_methods: 各 method 行
        Col B: Method name
        Col C: Low (¥B)
        Col D: Mid (¥B)
        Col E: High (¥B)
        Col F: Range = High - Low (¥B)  ← 別途計算

    Chart は Stacked horizontal bar (BarChart, type='bar', grouping='stacked'):
      Series 1: "Floor" = Low (透明 fill)
      Series 2: "Range" = High - Low (Navy)

    Mid は data label として bar 内に表示。
    """
    chart = BarChart()
    chart.type = "bar"        # horizontal bar
    chart.grouping = "stacked"
    chart.style = 2

    # Series 1: 下駄 (Low value, 透明)
    floor_ref = Reference(
        ws,
        min_col=3,  # C 列 (Low)
        min_row=data_start_row,  # header 行
        max_row=data_start_row + n_methods,
    )
    chart.add_data(floor_ref, titles_from_data=True)
    chart.series[0].graphicalProperties = _make_no_fill()  # 透明

    # Series 2: Range (High - Low)
    range_ref = Reference(
        ws,
        min_col=6,  # F 列 (Range)
        min_row=data_start_row,
        max_row=data_start_row + n_methods,
    )
    chart.add_data(range_ref, titles_from_data=True)
    chart.series[1].graphicalProperties = _make_solid_fill(IB_CHART_PALETTE["primary"][0])  # Navy

    # Category (method names)
    cats_ref = Reference(
        ws,
        min_col=2,  # B 列 (Method name)
        min_row=data_start_row + 1,
        max_row=data_start_row + n_methods,
    )
    chart.set_categories(cats_ref)

    # Data label (Range bar 上に Mid value を表示する → 実装 trick: Mid 列の値を別途計算しlabel 化)
    # シンプル版: Range の data label = High - Low, range の値が小さいときは label が読みにくい
    # 推奨: separate "Mid" annotation を別 series (scatter) で重ねるか、bar の data label を抑制し
    #       後段の表で Low / Mid / High を明示する
    chart.series[1].dLbls = None  # シンプル化

    # Title / Axis
    apply_ib_chart_base(chart, title="Football Field — Valuation Range (¥B)")
    chart.x_axis.title = "Equity Value (¥B)"
    chart.y_axis.title = None  # Method name はそのまま category として表示
    chart.x_axis.number_format = "#,##0"

    # Bar gap / overlap
    chart.gapWidth = 50
    chart.overlap = 100  # stacked

    # Size
    chart.width = 16
    chart.height = 12

    # Legend は単 series なので非表示 (Series 1 は透明、Series 2 は Range のみ)
    chart.legend = None

    return chart


# 使用側:
# chart = build_football_field(ws, data_start_row=10, n_methods=5)
# ws.add_chart(chart, "B25")
```

### 17.3 Sensitivity Heatmap (Conditional Formatting)

```python
# scripts/valuation_builder.py 内、Sensitivity section
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Border, Side, Alignment, Font, PatternFill

def build_sensitivity_heatmap(ws, top_left_cell: str, bottom_right_cell: str,
                              base_case_cell: str = None):
    """
    既に worksheet に 5×5 (or n×m) の sensitivity table が書かれている前提。
    本関数は cell range に conditional formatting (ColorScaleRule) を適用する。

    top_left_cell:     "C12" (data 開始セル、header 除く)
    bottom_right_cell: "G16"
    base_case_cell:    "E14" (中央セル、太枠で強調)
    """
    rng = f"{top_left_cell}:{bottom_right_cell}"

    # Diverging palette: Red (low) → White (mid) → Green (high)
    rule = ColorScaleRule(
        start_type="min",
        start_color=IB_CHART_PALETTE["heatmap_neg"],         # C04A4A
        mid_type="percentile", mid_value=50,
        mid_color=IB_CHART_PALETTE["heatmap_mid"],           # FFFFFF
        end_type="max",
        end_color=IB_CHART_PALETTE["heatmap_pos"],           # 3F8F5E
    )
    ws.conditional_formatting.add(rng, rule)

    # 全セルに hairline border
    thin = Side(border_style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for row in ws[rng]:
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(name="Arial", size=9)

    # Base case cell に太枠
    if base_case_cell:
        thick = Side(border_style="medium", color="2D332E")
        ws[base_case_cell].border = Border(
            left=thick, right=thick, top=thick, bottom=thick
        )
        ws[base_case_cell].font = Font(name="Arial", size=9, bold=True)

# 使用側:
# build_sensitivity_heatmap(ws, "C12", "G16", base_case_cell="E14")
```

### 17.4 Waterfall (EBITDA Bridge) — Stacked Bar Trick

```python
# scripts/three_statement_builder.py 内、EBITDA Bridge section
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList

def build_waterfall_bridge(ws, data_start_row: int, n_steps: int):
    """
    Data layout (前提、worksheet に事前計算しておく):
      Row data_start_row:   header (Step | Type | Invisible | Positive | Negative)
      Row data_start_row+1 .. +n_steps:
        Col B: Step name (e.g., "Y1 EBITDA", "+ Volume", "- Cost", "Y5 EBITDA")
        Col C: Type ("total", "positive", "negative")
        Col D: Invisible base (累積 - 自身の値、または 0 for total)
        Col E: Positive value (positive step のとき値、それ以外 0)
        Col F: Negative value (negative step のとき値、それ以外 0)
        Col G: Total bar (total step のとき累積値、それ以外 0)
    """
    chart = BarChart()
    chart.type = "col"           # vertical bar
    chart.grouping = "stacked"
    chart.style = 2

    # Series 1: Invisible base
    chart.add_data(
        Reference(ws, min_col=4, min_row=data_start_row, max_row=data_start_row + n_steps),
        titles_from_data=True,
    )
    chart.series[0].graphicalProperties = _make_no_fill()

    # Series 2: Positive
    chart.add_data(
        Reference(ws, min_col=5, min_row=data_start_row, max_row=data_start_row + n_steps),
        titles_from_data=True,
    )
    chart.series[1].graphicalProperties = _make_solid_fill(IB_CHART_PALETTE["waterfall_pos"])

    # Series 3: Negative
    chart.add_data(
        Reference(ws, min_col=6, min_row=data_start_row, max_row=data_start_row + n_steps),
        titles_from_data=True,
    )
    chart.series[2].graphicalProperties = _make_solid_fill(IB_CHART_PALETTE["waterfall_neg"])

    # Series 4: Total bar
    chart.add_data(
        Reference(ws, min_col=7, min_row=data_start_row, max_row=data_start_row + n_steps),
        titles_from_data=True,
    )
    chart.series[3].graphicalProperties = _make_solid_fill(IB_CHART_PALETTE["waterfall_total"])

    # Categories
    cats_ref = Reference(
        ws, min_col=2,
        min_row=data_start_row + 1, max_row=data_start_row + n_steps,
    )
    chart.set_categories(cats_ref)

    # Data labels: positive / negative / total に値表示
    for ser_idx in (1, 2, 3):
        chart.series[ser_idx].dLbls = DataLabelList(showVal=True, position="ctr")

    apply_ib_chart_base(chart, title="EBITDA Bridge: Y1 → Y5 (¥B)")
    chart.y_axis.title = "EBITDA (¥B)"
    chart.y_axis.number_format = "#,##0.0"
    chart.x_axis.title = None

    chart.gapWidth = 50
    chart.overlap = 100

    chart.width = 18
    chart.height = 10
    chart.legend = None  # series 名は説明的でない、legend 不要

    return chart
```

### 17.5 Bar Chart (Revenue 時系列) with Highlight

```python
def build_revenue_bar(ws, data_start_row: int, n_periods: int, highlight_idx: int = None):
    """
    Revenue 時系列 bar chart。highlight_idx が指定されたらその bar を Brand Gold で強調。

    Data layout:
      Row data_start_row: header (Period | Revenue)
      Row data_start_row+1 .. +n_periods: 各期間
    """
    from openpyxl.chart import BarChart, Reference
    from openpyxl.chart.marker import DataPoint

    chart = BarChart()
    chart.type = "col"
    chart.style = 2

    chart.add_data(
        Reference(ws, min_col=3, min_row=data_start_row, max_row=data_start_row + n_periods),
        titles_from_data=True,
    )
    chart.series[0].graphicalProperties = _make_solid_fill(IB_CHART_PALETTE["primary"][0])  # Navy

    # Highlight
    if highlight_idx is not None:
        dp = DataPoint(idx=highlight_idx)
        dp.graphicalProperties = _make_solid_fill(IB_CHART_PALETTE["primary"][2])  # Gold
        chart.series[0].dPt.append(dp)

    cats_ref = Reference(
        ws, min_col=2,
        min_row=data_start_row + 1, max_row=data_start_row + n_periods,
    )
    chart.set_categories(cats_ref)

    # Data label (全 bar 上)
    chart.series[0].dLbls = DataLabelList(showVal=True, position="outEnd")

    apply_ib_chart_base(chart, title="Revenue (¥B)")
    chart.y_axis.title = "Revenue (¥B)"
    chart.y_axis.number_format = "#,##0.0"
    chart.x_axis.title = None

    chart.gapWidth = 75
    chart.width = 16
    chart.height = 9
    chart.legend = None

    return chart
```

### 17.6 Line Chart (ARR Trend) with Forecast Split

```python
def build_arr_line_with_forecast(ws, actuals_row: int, forecast_row: int, n_actuals: int, n_forecast: int):
    """
    ARR line chart で Actuals (solid line) と Forecast (dashed line) を区別。

    Data layout (前提): worksheet に Actuals series と Forecast series が別 column に書かれている
      Col B: Period
      Col C: Actuals ARR (forecast 期は空)
      Col D: Forecast ARR (actuals 期は空)
    """
    from openpyxl.chart import LineChart, Reference

    chart = LineChart()
    chart.style = 2

    # Actuals series
    chart.add_data(
        Reference(ws, min_col=3, min_row=actuals_row,
                  max_row=actuals_row + n_actuals + n_forecast),
        titles_from_data=True,
    )
    chart.series[0].graphicalProperties = _make_line(
        IB_CHART_PALETTE["primary"][0], width_pt=2.25
    )
    chart.series[0].smooth = False

    # Forecast series (dashed)
    chart.add_data(
        Reference(ws, min_col=4, min_row=actuals_row,
                  max_row=actuals_row + n_actuals + n_forecast),
        titles_from_data=True,
    )
    chart.series[1].graphicalProperties = _make_line(
        IB_CHART_PALETTE["primary"][0], width_pt=2.25, dash="dash"
    )
    chart.series[1].smooth = False

    cats_ref = Reference(
        ws, min_col=2,
        min_row=actuals_row + 1,
        max_row=actuals_row + n_actuals + n_forecast,
    )
    chart.set_categories(cats_ref)

    apply_ib_chart_base(chart, title="ARR Trajectory: Actuals & Forecast (¥B)")
    chart.y_axis.title = "ARR (¥B)"
    chart.y_axis.number_format = "#,##0.0"
    chart.x_axis.title = None

    chart.width = 16
    chart.height = 9

    return chart
```

### 17.7 Stacked Bar (Cohort Layer Cake)

```python
def build_cohort_layer_cake(ws, data_start_row: int, n_cohorts: int, n_periods: int):
    """
    Cohort retention の layer cake (stacked bar).

    Data layout:
      Row data_start_row: header (Period | Cohort_2022Q1 | Cohort_2022Q2 | ... | Cohort_2024Q4)
      Row data_start_row+1 .. +n_periods: 各期間の各 cohort ARR contribution
    """
    from openpyxl.chart import BarChart, Reference

    chart = BarChart()
    chart.type = "col"
    chart.grouping = "stacked"
    chart.style = 2

    # 各 cohort を series に
    for i in range(n_cohorts):
        chart.add_data(
            Reference(ws,
                      min_col=3 + i,  # cohort 1 = col C, cohort 2 = col D, ...
                      min_row=data_start_row,
                      max_row=data_start_row + n_periods),
            titles_from_data=True,
        )
        # 古い cohort ほど薄く、新しいほど濃く
        # navy `1F3A66` を base に saturation を変える
        # 簡易: palette 5 色の循環で良い見た目
        palette = IB_CHART_PALETTE["primary"]
        color = palette[i % len(palette)]
        chart.series[i].graphicalProperties = _make_solid_fill(color)

    cats_ref = Reference(
        ws, min_col=2,
        min_row=data_start_row + 1, max_row=data_start_row + n_periods,
    )
    chart.set_categories(cats_ref)

    apply_ib_chart_base(chart, title="ARR Cohort Layer Cake (¥B)")
    chart.y_axis.title = "ARR (¥B)"
    chart.y_axis.number_format = "#,##0"
    chart.x_axis.title = None

    chart.gapWidth = 30
    chart.overlap = 100

    chart.width = 20
    chart.height = 8

    if chart.legend is not None:
        chart.legend.position = "r"

    return chart
```

### 17.8 Scatter (Rule of 40)

```python
def build_rule_of_40_scatter(ws, peer_data_row: int, n_peers: int, target_row: int):
    """
    X = Revenue growth (%), Y = FCF margin (%) の scatter。
    対角線 (X+Y=40) は scatter line として別 series で重ねる。

    Data layout:
      Peer set:
        Row peer_data_row: header (Company | Growth% | FCF margin% )
        Row peer_data_row+1 .. +n_peers: peer 各社
      Target:
        Row target_row: target company (1 行)
      Diagonal line: 別 sheet or 同 sheet の別 range に (0,40)-(40,0) の 2 点
    """
    from openpyxl.chart import ScatterChart, Series, Reference

    chart = ScatterChart()
    chart.style = 2

    # Series 1: Peer set
    x_peer = Reference(ws, min_col=3, min_row=peer_data_row + 1,
                       max_row=peer_data_row + n_peers)
    y_peer = Reference(ws, min_col=4, min_row=peer_data_row + 1,
                       max_row=peer_data_row + n_peers)
    series_peer = Series(y_peer, x_peer, title="Peers")
    series_peer.graphicalProperties = GraphicalProperties()
    series_peer.graphicalProperties.line = LineProperties(noFill=True)  # marker only
    series_peer.marker = openpyxl_marker(symbol="circle", size=8,
                                          color=IB_CHART_PALETTE["primary"][1])  # gray
    chart.series.append(series_peer)

    # Series 2: Target (1 point)
    x_target = Reference(ws, min_col=3, min_row=target_row, max_row=target_row)
    y_target = Reference(ws, min_col=4, min_row=target_row, max_row=target_row)
    series_target = Series(y_target, x_target, title="Target")
    series_target.graphicalProperties = GraphicalProperties()
    series_target.graphicalProperties.line = LineProperties(noFill=True)
    series_target.marker = openpyxl_marker(symbol="star", size=12,
                                            color=IB_CHART_PALETTE["primary"][2])  # gold
    chart.series.append(series_target)

    # (Series 3: Rule of 40 diagonal は省略、必要なら別途)

    apply_ib_chart_base(chart, title="Rule of 40: Growth + FCF Margin")
    chart.x_axis.title = "Revenue Growth (%)"
    chart.y_axis.title = "FCF Margin (%)"
    chart.x_axis.number_format = "0.0%"
    chart.y_axis.number_format = "0.0%"

    chart.width = 14
    chart.height = 10

    return chart


def openpyxl_marker(symbol: str, size: int, color: str):
    """openpyxl の Marker を簡易構築。"""
    from openpyxl.chart.marker import Marker
    from openpyxl.chart.shapes import GraphicalProperties as GP
    m = Marker(symbol=symbol, size=size)
    m.graphicalProperties = GP(solidFill=color)
    m.graphicalProperties.line = LineProperties(solidFill=color)
    return m
```

---

## 18. `ib_format.py` 拡張提案 (helper 関数)

`scripts/ib_format.py` に以下の helper を追加し、3 つの builder script (three_statement / cap_table / valuation) から共通利用する。

### 18.1 追加すべき定数

```python
# IB Chart Palette
IB_CHART_PALETTE: dict[str, str | list[str]] = {
    "primary":          ["1F3A66", "666666", "ECC85A", "7A8FAB", "B8C2D1"],
    "waterfall_pos":    "1F3A66",
    "waterfall_neg":    "C04A4A",
    "waterfall_total":  "666666",
    "heatmap_neg":      "C04A4A",
    "heatmap_mid":      "FFFFFF",
    "heatmap_pos":      "3F8F5E",
    "gridline":         "CCCCCC",
    "axis_line":        "666666",
    "current_price":    "ECC85A",
    "offer_price":      "C04A4A",
}
```

### 18.2 追加すべき関数 (signature のみ)

```python
def apply_ib_chart_base(chart, title: str | None = None) -> None:
    """全 chart 共通の IB style: 外枠削除 / Plot area 透明 / gridline / legend 位置 / Plot layout"""

def apply_chart_styling(chart, style: Literal[
    "football_field", "waterfall", "sensitivity_heatmap",
    "bar", "line", "stacked_bar", "scatter"
]) -> None:
    """style preset を chart に適用。内部的には apply_ib_chart_base + style 別追加処理"""

def setup_chart_axes(chart, y_unit: str = "¥B", x_axis_title: str | None = None,
                     y_zero_anchored: bool = True) -> None:
    """軸の標準設定: tick mark / gridline / number format / 単位"""

def setup_chart_title(chart, title: str, subtitle: str | None = None) -> None:
    """Title (12pt bold Arial) + optional sub-title (10pt regular)"""

def add_source_line(ws, anchor_cell: str, source_text: str) -> None:
    """Chart 直下のセルに source line (italic 8pt gray) を書き込む"""

def build_football_field(ws, data_start_row: int, n_methods: int) -> "BarChart":
    """Football field (5-7 method の floating bar) を生成"""

def build_waterfall_bridge(ws, data_start_row: int, n_steps: int,
                           title: str = "Waterfall") -> "BarChart":
    """EBITDA / ARR / Cash bridge waterfall (stacked bar trick)"""

def build_sensitivity_heatmap(ws, top_left: str, bottom_right: str,
                              base_case: str | None = None) -> None:
    """5×5 / 7×7 sensitivity table に conditional formatting で diverging color scale を適用"""

def build_revenue_bar(ws, data_start_row: int, n_periods: int,
                      highlight_idx: int | None = None) -> "BarChart":
    """Revenue 時系列 bar (with optional highlight)"""

def build_arr_line(ws, data_start_row: int, n_periods: int,
                   forecast_split_idx: int | None = None) -> "LineChart":
    """ARR line (with optional forecast split = solid → dashed)"""

def build_cohort_layer_cake(ws, data_start_row: int, n_cohorts: int,
                            n_periods: int) -> "BarChart":
    """Cohort retention layer cake (stacked bar)"""

def build_rule_of_40_scatter(ws, peer_row: int, n_peers: int,
                             target_row: int) -> "ScatterChart":
    """Rule of 40 scatter (peers + target highlight)"""
```

### 18.3 統合運用パターン

`scripts/three_statement_builder.py` (KPI Dashboard sheet 生成) からの利用:

```python
from scripts.ib_format import (
    apply_ib_chart_base, build_revenue_bar, build_arr_line,
    build_waterfall_bridge, build_cohort_layer_cake,
)

# KPI Dashboard sheet
ws = wb["09_KPI_Dashboard"]

# Revenue bar
chart_rev = build_revenue_bar(ws, data_start_row=10, n_periods=5,
                               highlight_idx=4)  # FY27E を強調
ws.add_chart(chart_rev, "B25")

# ARR line with forecast split
chart_arr = build_arr_line(ws, data_start_row=20, n_periods=20,
                            forecast_split_idx=12)
ws.add_chart(chart_arr, "L25")

# EBITDA bridge waterfall
chart_wf = build_waterfall_bridge(ws, data_start_row=40, n_steps=6,
                                   title="EBITDA Bridge: FY24A → FY29E (¥B)")
ws.add_chart(chart_wf, "B45")

# Cohort layer cake
chart_cc = build_cohort_layer_cake(ws, data_start_row=60, n_cohorts=12, n_periods=24)
ws.add_chart(chart_cc, "B65")
```

`scripts/valuation_builder.py` (Valuation sheet) からの利用:

```python
from scripts.ib_format import (
    build_football_field, build_sensitivity_heatmap,
)

ws = wb["16_Valuation"]

# Football field
chart_ff = build_football_field(ws, data_start_row=20, n_methods=5)
ws.add_chart(chart_ff, "B40")

# Sensitivity heatmap (table 自体に CF)
build_sensitivity_heatmap(ws, top_left="C50", bottom_right="G54",
                           base_case="E52")
```

`scripts/cap_table_builder.py` (Exit Waterfall) からの利用:

```python
from scripts.ib_format import build_waterfall_bridge

ws = wb["12_CapTable"]

# Exit Waterfall (per scenario)
chart_ew = build_waterfall_bridge(ws, data_start_row=80, n_steps=8,
                                   title="Exit Waterfall: ¥6B Exit (¥M)")
ws.add_chart(chart_ew, "B100")
```

---

## 19. Mini Case 5 例

### Case 1: Football Field (5 method × Low/Mid/High)

**設定**: SaaS Series B、ARR ¥1.2B、グロース 80%。Buyer 候補からの Indication of Interest 価格レンジ算定。

| Method | Low (¥B) | Mid (¥B) | High (¥B) | Range (¥B) |
|---|---|---|---|---|
| DCF (Gordon, WACC 15%, g 2.5%) | 95 | 120 | 145 | 50 |
| DCF (Exit multiple 8x EBITDA) | 105 | 125 | 150 | 45 |
| Comps (EV/Revenue, NTM, peer median 10x) | 90 | 110 | 135 | 45 |
| Comps (EV/Revenue, NTM, peer top quartile 14x) | 130 | 155 | 185 | 55 |
| Precedent (M&A 2022-2024, control premium incl.) | 115 | 140 | 170 | 55 |

**Chart 設計**:
- 5 method を縦に並列 (DCF Gordon が一番上)
- 全 method を Navy `#1F3A66` で統一
- Mid を Slate Gray ● marker で表示
- Implied offer price ¥130B を vertical line (Brand Gold dashed) で全 bar 貫通

**判読**: 5 method の Mid 中央値 = ¥125B。Implied offer ¥130B は 5 method の中央値の +4%、Range 全体 (¥90-185B) のなかで center-right に位置する。Football field 上で許容レンジの上半分にあり、買収提案として妥当。

### Case 2: Waterfall (EBITDA Bridge Y1 → Y5)

**設定**: SaaS Series C、Y1 EBITDA ¥2.0B → Y5 EBITDA ¥6.5B のドライバ分解。

| Step | Type | Value (¥B) | Cumulative (¥B) | Invisible base | Positive | Negative |
|---|---|---|---|---|---|---|
| Y1 EBITDA (start) | total | 2.0 | 2.0 | 0 | 2.0 | 0 |
| + Volume (new ARR x existing margin) | positive | +2.5 | 4.5 | 2.0 | 2.5 | 0 |
| + Price increase | positive | +0.8 | 5.3 | 4.5 | 0.8 | 0 |
| + Mix shift (enterprise tier) | positive | +0.6 | 5.9 | 5.3 | 0.6 | 0 |
| - Cost inflation (wages) | negative | -0.4 | 5.5 | 5.5 | 0 | 0.4 |
| + Productivity (auto-renewal) | positive | +1.0 | 6.5 | 5.5 | 1.0 | 0 |
| Y5 EBITDA (end) | total | 6.5 | 6.5 | 0 | 6.5 | 0 |

**Chart 設計**:
- 7 bar (Y1 / Volume / Price / Mix / -Cost / Productivity / Y5)
- Total bar (Y1, Y5) は Slate Gray
- Positive bar (Volume, Price, Mix, Productivity) は Navy
- Negative bar (-Cost) は Muted Red
- Connecting line (累積) は scatter overlay (薄 gray dashed)
- 各 bar 上に値 +¥2.5B / +¥0.8B / -¥0.4B 等 (符号付き)

**判読**: Y1 → Y5 で +¥4.5B 改善。寄与は Volume 56% (¥2.5B) / Productivity 22% (¥1.0B) / Price 18% (¥0.8B) / Mix 13% (¥0.6B)、Cost が -9% (-¥0.4B) で吸収。最大ドライバは Volume、productivity も 22% は無視できない。

### Case 3: Sensitivity Heatmap (DCF: WACC × Terminal Growth)

**設定**: DCF Equity Value (¥B) を WACC × terminal growth で振る。Base case WACC 12%, g 2.5%, EV ¥120B。

| WACC \ g | 1.5% | 2.0% | 2.5% (base) | 3.0% | 3.5% |
|---|---|---|---|---|---|
| 10% | 145 | 152 | 160 | 169 | 180 |
| 11% | 132 | 138 | 145 | 152 | 160 |
| 12% (base) | 110 | 115 | **120** | 126 | 132 |
| 13% | 95 | 99 | 103 | 108 | 113 |
| 14% | 82 | 85 | 88 | 91 | 95 |

**Chart 設計**:
- 5×5 grid、cell 値表示
- Base case (E14) は太枠 + Bold
- Diverging palette: Red `#C04A4A` (低値、左下 ¥82B) → White (中央 ¥120B) → Green `#3F8F5E` (高値、右上 ¥180B)
- Header (WACC / g 値) は Light gray bg + Bold
- 全セル hairline border `#CCCCCC`

**判読**: Base case ¥120B、WACC ±200bps で EV ±¥30-40B 振れる (sensitivity 25-33%)。terminal growth ±100bps で EV ±¥10B (sensitivity 8%)。WACC が dominant、terminal g は二次的。WACC 算定根拠 (β / risk-free rate / equity risk premium) を IC で deep dive する optionality 確保。

### Case 4: Cohort Retention Layer Cake (12 cohort × 24 month)

**設定**: SaaS Series B、2022Q1 から 2024Q4 までの 12 cohort、各 cohort の累積 ARR contribution を月次 24 ヶ月で stacked bar。

**抜粋**:

| Period | 22Q1 | 22Q2 | 22Q3 | 22Q4 | 23Q1 | 23Q2 | 23Q3 | 23Q4 | 24Q1 | 24Q2 | 24Q3 | 24Q4 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-12 | 95 | 110 | 130 | 155 | 180 | 220 | 260 | 305 | 240 | 200 | 160 | 100 | 2,155 |
| 2023-12 | 80 | 95 | 110 | 130 | 145 | 175 | 205 | 235 | — | — | — | — | 1,175 |
| 2022-12 | 50 | 60 | 70 | 80 | — | — | — | — | — | — | — | — | 260 |

**Chart 設計**:
- 24 期 (X 軸) × 12 cohort (stacked bar)
- 古い cohort (22Q1) ほど下に積む、新しい cohort (24Q4) は上
- 色は Navy 系の saturation を 12 段階 (古いほど薄 `#B8C2D1`、新しいほど濃 `#1F3A66`)
- Legend は省略 (cohort 名は data label 形式で各 stack 内に表示できないので、別 sub-table で凡例)

**判読**: 2022Q1 cohort は 24 ヶ月後も ¥95M を維持 (NRR ≈ 90%、ある程度の churn だが expansion で回収できていない)。新規 cohort が積み上がる速度が ARR 成長を牽引。

### Case 5: Rule of 40 Scatter (Target vs SaaS Peers)

**設定**: SaaS Series B target、Revenue growth 80%, FCF margin -25%。 R40 = 80 + (-25) = 55%。Peer set 10 社の R40 散布図に重ねる。

| Company | Growth (%) | FCF margin (%) | R40 |
|---|---|---|---|
| Snowflake | 38 | 23 | 61 |
| HubSpot | 23 | 18 | 41 |
| Atlassian | 19 | 27 | 46 |
| MongoDB | 31 | 5 | 36 |
| Cloudflare | 33 | 9 | 42 |
| Okta | 16 | 8 | 24 |
| Datadog | 27 | 30 | 57 |
| Confluent | 26 | -10 | 16 |
| Gitlab | 31 | 0 | 31 |
| Klaviyo | 38 | 12 | 50 |
| **Target (Series B)** | **80** | **-25** | **55** |

**Chart 設計**:
- X 軸 = Growth (%) 0-90%
- Y 軸 = FCF margin (%) -30% to +35%
- Peer = 灰色 ● (size 8pt)、Target = Brand Gold ★ (size 12pt)
- 各 marker の右に Company name (data label)
- 対角線 (X+Y=40) を薄 gray dashed line
- 1 列 / 1 行余白で plot area 確保

**判読**: Target は対角線 (R40 = 40) より上 (R40 = 55%)。Datadog (R40 = 57%) と同 zone、Snowflake (R40 = 61%) には届かないが peer top quartile 内。Series B レベルとして優秀。Margin 改善の道筋 (FCF margin を -25% → -10% に 18 ヶ月で改善) を IC で議論。

---

## 20. Chart Audit チェックリスト 30 項目

Chart を出力する前に以下 30 項目を一通り確認する。すべて clear で IB 品質。

### A. 色彩 (1-7)
1. [ ] 7 色レインボー (openpyxl default) を使っていないか
2. [ ] §2.2 IB Chart Palette (Navy / Slate Gray / Brand Gold + Navy 60% / 30%) を使っているか
3. [ ] Series 数が 5 を超えていないか (超えていたら small multiples 検討)
4. [ ] Negative bar が `#C04A4A` (muted red) で `#FF0000` でないか
5. [ ] Stop-light 色 (赤緑) の濫用がないか
6. [ ] Heatmap が diverging palette (中央発散) を使っているか
7. [ ] Gridline 色が `#CCCCCC` (faint) か

### B. Typography (8-12)
8. [ ] Chart 内すべて Arial か (Calibri / Times / Comic Sans 禁)
9. [ ] Chart title が 12pt Bold か
10. [ ] Axis title に単位 (US$M / ¥B / %) が含まれるか
11. [ ] Data label が 9pt か
12. [ ] Source line が italic 8pt gray で chart 下にあるか

### C. Axis (13-17)
13. [ ] Bar chart の Y 軸が 0 起点固定か
14. [ ] Vertical gridline (時系列) が削除されているか
15. [ ] Minor gridline が削除されているか
16. [ ] Major tick mark が "in" (内向き) か
17. [ ] Number format が桁数を抑え (3 桁以下) 単位を上げているか

### D. Layout (18-22)
18. [ ] Chart 外枠 border が削除されているか
19. [ ] Plot area が透明 / 白か
20. [ ] Plot area layout が manual で確保され、x 軸が広がっているか
21. [ ] Chart size (width × height cm) が chart 種別に応じた標準値か
22. [ ] 配置 anchor が適切か (data table の下 or 横)

### E. メッセージ (23-27)
23. [ ] Chart title が結論先行のジャーナリズム形式か (placeholder 禁)
24. [ ] Sub-title (任意) が takeaway 1 行か
25. [ ] Source line が出典 (誰が、いつの) を明記しているか
26. [ ] Footnote の番号 (1)(2) が data label と対応しているか
27. [ ] 「この chart で読者が何を判断するか」が明確か

### F. Anti-pattern 回避 (28-30)
28. [ ] 3D chart / pie chart / drop shadow / gradient がないか
29. [ ] Marker が全点に打たれていないか (line chart)
30. [ ] Trend line の濫用 / 予測根拠化がないか

---

## 21. 出典一覧

### A. デザイン理論
- Tufte, Edward R. (2001). *The Visual Display of Quantitative Information* (2nd ed.). Graphics Press.
- Tufte, Edward R. (1990). *Envisioning Information*. Graphics Press.
- Cleveland, W.S. & McGill, R. (1984). "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods." *Journal of the American Statistical Association*, 79(387), 531-554.
- Few, Stephen (2012). *Show Me the Numbers: Designing Tables and Graphs to Enlighten* (2nd ed.). Analytics Press.
- Few, Stephen (2013). *Information Dashboard Design: Displaying Data for At-a-Glance Monitoring* (2nd ed.). Analytics Press.
- Knaflic, Cole Nussbaumer (2015). *Storytelling with Data*. Wiley.

### B. IB / Pitchbook 慣習
- Macabacus.com — "Financial Modeling Best Practices" / "Charting in Excel"
- Wall Street Prep — "Investment Banking Pitch Book Templates" course materials
- Breaking Into Wall Street (BIWS) — "Financial Modeling and Valuation"
- 公開 pitchbook サンプル: GS / MS / Lazard / Evercore / Centerview / Houlihan Lokey の 2018-2024 年公開 M&A / IPO ロードショー資料 100+ 件 (SEC EDGAR + 各社公開 IR ページ)

### C. openpyxl / xlsxwriter 実装
- openpyxl official docs (https://openpyxl.readthedocs.io/) — Chart, Reference, GraphicalProperties
- xlsxwriter docs (https://xlsxwriter.readthedocs.io/) — chart_*.html 各 chart 種別ページ
- Microsoft ECMA-376 (OOXML) Part 1 — DrawingML chart schema

### D. 関連 reference (本 skill 内)
- [`_terminology.md §1`](_terminology.md) — IB Color Code (セル文字色)
- [`00_design_guidelines.md §3, §6`](00_design_guidelines.md) — Color Palette / Chart Design Standards (サマリ)
- [`05_valuation_wacc.md §2.9, §3`](05_valuation_wacc.md) — Football field / Sensitivity の計算ロジック
- [`06_three_statement.md §9`](06_three_statement.md) — KPI Dashboard sheet 構造
- [`04b_cap_table_mechanics.md §6`](04b_cap_table_mechanics.md) — Exit Waterfall ロジック
- [`01a_modeling_standards.md §4`](01a_modeling_standards.md) — Number format
- [`_self_review_protocol.md §8`](_self_review_protocol.md) — Chart 関連 5 check

### E. 色彩・アクセシビリティ
- WCAG 2.1 — Contrast ratio guidelines (AA: 4.5:1, AAA: 7:1)
- ColorBrewer 2.0 (https://colorbrewer2.org/) — Diverging palette のリファレンス
- IBM Design Language — Color (data visualization palette)

### F. 日本の慣習
- 野村證券 / 大和証券 / みずほ証券 / 三菱 UFJ モルスタ / SMBC 日興 の上場準備会社向け IR 資料デザイン慣習 (公開資料の観察)
- 政策金融公庫 / 日本公庫 創業計画書テンプレート (公式サイト)

---

> 本 reference は live document。`scripts/ib_format.py` への helper 追加 / 新 chart 種別追加 / 業態テンプレ追加が発生したら、本書を **canonical** として更新する。値の変更は本書で議論し、本書で決定する。




