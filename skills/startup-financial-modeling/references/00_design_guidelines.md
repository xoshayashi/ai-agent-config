---
name: design_guidelines
description: IB 品質の財務モデル (xlsx) と pitchbook (pptx) を生成するときに参照するデザイン語彙の正本。色 / 罫線 / 表 / 図 / フォント / レイアウトの spec。SKILL.md dispatch table の各 intent から「色 / 形式」レベルで読まれる。
type: reference
priority: P1
related: [_terminology, 01a_modeling_standards, 06_three_statement, 14_ipo_readiness]
---

## このドキュメントの位置づけ

- **正本 (SSoT)**: 用語・色・閾値は [`_terminology.md`](_terminology.md) を canonical とする。本書のデザイン語彙は `_terminology §1 (IB Color)` / `§3 (Sheet naming)` を実装側として展開
- **Routing**: [`_master_decision_tree.md`](_master_decision_tree.md) の各 entry で「xlsx / pitchbook 出力時」に参照される
- **Self-review**: 本書を使ったあとは [`_self_review_protocol.md §8`](_self_review_protocol.md) の 5 check (特に Hard input = `#0000FF` 等) を必ず実行
- **関連 reference**: `_terminology` (色 / sheet) / `01a_modeling_standards` (formatting 細部) / `06_three_statement` (sheet 構造) / `14_ipo_readiness` (pitchbook)

# IB Financial Model & Pitchbook Design Guidelines v1.0

> **Purpose**: 投資銀行 (Investment Bank, 以下 "IB") 品質の財務モデル (xlsx) と pitchbook (pptx) を生成するときに、Claude が参照する **デザイン語彙の正本 (Single Source of Truth)** である。
>
> **Scope**: ビジュアルデザイン (色、書体、レイアウト、罫線、チャート、頁構成) に特化する。会計の正しさ・モデリングロジックは姉妹文書 `01a_modeling_standards.md` / `01b_integrity_and_anti_patterns.md` に委ねる。
>
> **読者**: Claude (xlsx / pptx を実装するエージェント) と、それを review する人間バンカー / アナリスト。
>
> **使い方**: 後続の `scripts/ib_format.py` (openpyxl / xlsxwriter で xlsx に IB style を適用するライブラリ) は、このドキュメントで定義された色 / 書体 / レイアウト定数を **そのまま** 実装する。値の変更はここで議論し、ここで決定する。

---

## Table of Contents

| # | Chapter | 役割 |
|---|---|---|
| 1 | Visual Hierarchy 哲学 | "Less is more", 静かな威厳 |
| 2 | Typography | フォント、サイズ、weight、italics の階層 |
| 3 | Color Palette | Functional palette と Brand palette の二層構造 |
| 4 | Layout & Grid | 列幅、行高、印刷余白、ヘッダ／フッタ |
| 5 | Border & Cell Styling | 罫線最小主義、subtotal / total の罫線規約 |
| 6 | Chart Design Standards | Football field, sensitivity heatmap, waterfall, bar/line/scatter |
| 7 | Page Composition | Cover, exec summary, divider, TOC, tear sheet |
| 8 | Banker Style Cues | 数字書式、source line、footnote、略語 |
| 9 | バンク別のスタイル特徴 | GS / MS / JPM / Lazard / Evercore / Centerview / HL |
| 10 | 日本の IB / 証券会社のスタイル差 | 野村、大和、みずほ、三菱 UFJ MS、SMBC 日興、フーリハン日本 |
| 11 | Banker Mode vs VC Mode vs PE Mode | 同じ財務モデルでも「文脈」で見せ方が変わる |
| 12 | Pitchbook 連携設計 | xlsx → pptx 貼付時に崩れない設計 |
| 13 | 印刷物 vs スクリーン | ページネーション、ヘッダフッタ繰り返し |
| 14 | アクセシビリティ | カラーブラインド配慮、screen reader |
| 15 | Anti-patterns | やってはいけないデザイン |
| 16 | 成熟した IB Design 原則 40 か条 | 1 行 + rationale の早見表 |
| 17 | Design Audit チェックリスト | 出力前のセルフチェック |

---

## 1. Visual Hierarchy 哲学

### 1.1 "Quiet Authority" — 静かな威厳

IB が出す資料は、**派手さで売らない**。クライアントは数千億円規模の意思決定をしているので、装飾的な資料は逆に「軽い」「真面目さに欠ける」と判定される。

> **原則 1.1**: デザインは目立たない方が良い。読者の目は最終的に **数字** と **結論** に着地すべきで、デザインに目を奪われた瞬間に負け。

**根拠 (Rationale)**:
- IB の資料の本質は「精緻な分析の証拠」を提示することで、装飾はそれを邪魔する。
- M&A の MD (Managing Director) や CFO は分単位で資料を捌くので、装飾的要素は「ノイズ」になる。
- 「シンプル = 手抜き」ではなく「シンプル = 自信」のシグナル。複雑な装飾は不安の裏返しに見える。

```
┌──────────────────────────── 悪い例 ─────────────────────────────┐
│ 【こんなふうに】                                                │
│  ▓▓▓ EBITDA Bridge ▓▓▓ ★Important★                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    │
│   ◆ Revenue Growth      ↑↑↑  +¥250M  🚀                        │
│   ◆ Cost Inflation      ↓↓↓  -¥80M   ⚠️                        │
│   ◆ One-time items      →→→  +¥30M                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    │
│   合計 (Total) ★         💎  ¥200M  💎                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────── 良い例 ─────────────────────────────┐
│ EBITDA Bridge                                                  │
│ (¥M)                                                           │
│                                                                │
│   Revenue growth                                       +250    │
│   Cost inflation                                        (80)   │
│   One-time items                                        +30    │
│                                                       ──────   │
│   Net change                                            200    │
│                                                       ══════   │
│ Source: Management projections (Apr-26).                       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Less is More — 色は機能のためだけに使う

色は「装飾」ではなく「**機能** (function)」のために使う。色そのものに意味があり、別の意味を持たせない。

| 色 | 意味 (固定) | これ以外の用途で使ってはいけない |
|---|---|---|
| Blue (`#0000FF`) | Hard input (ベタ打ち入力) | "強調" のために青字を使うのは禁止 |
| Black (`#000000`) | Formula (同シート計算) | デフォルト本文色も黒、ただし数式と区別不能で良い (それが正しい) |
| Green (`#008000`) | Cross-sheet link (他シート参照) | "OK / 良い" の意味で緑を使うのは禁止 |
| Red (`#FF0000`) | External link (外部ファイル / web 参照) | 単なる「強調」「悪い数字」での使用は禁止 |
| Gray (`#666666`) | Comment / footnote / non-financial label | 本文に混ぜない |

> **原則 1.2**: 一度色に意味を割り当てたら、その意味以外で使わない。意味の二重化はモデルの読み手を混乱させる。

**根拠**:
- IB の慣習色 (Blue/Black/Green/Red) は世界中のバンカーが共有している。これを破ると「素人モデル」と即座にバレる。
- "色覚 = 監査機能" とも言える。Blue が散らばっているシートを見ると「ここ全部 hardcode だな」と一瞥で分かる。

### 1.3 White Space — 空白は情報

「ぎっしり詰める」のは**素人**。プロは行間 / セル間に呼吸を置く。

```
┌─────────────────── 悪い例 (cluttered) ───────────────────┐
│ Revenue                  100  120  144  173  207  248    │
│ COGS                     -40  -48  -58  -69  -83  -99    │
│ Gross profit              60   72   86  104  124  149    │
│ OpEx                     -30  -36  -43  -52  -62  -75    │
│ EBITDA                    30   36   43   52   62   74    │
│ D&A                       -5   -6   -7   -8  -10  -12    │
│ EBIT                      25   30   36   44   52   62    │
└──────────────────────────────────────────────────────────┘

┌─────────────────── 良い例 (breathing) ───────────────────┐
│   Revenue                  100   120   144   173   207   │
│     (–) COGS               (40)  (48)  (58)  (69)  (83)  │
│   Gross profit              60    72    86   104   124   │
│                                                          │
│     (–) OpEx               (30)  (36)  (43)  (52)  (62)  │
│   EBITDA                    30    36    43    52    62   │
│                                                          │
│     (–) D&A                 (5)   (6)   (7)   (8)  (10)  │
│   EBIT                      25    30    36    44    52   │
└──────────────────────────────────────────────────────────┘
```

**実装ガイダンス (xlsx)**:
- セクション間に「空行」を 1 行入れる (height は 8-10pt の薄い行が理想)。
- Sub-line は indent で 1 段下げる。括弧 `(–)` を sign indicator として置く。
- Subtotal / Total の上下に空行は不要 (罫線で区切る)。

### 1.4 Density Targets — 情報密度の目安

「白すぎる」のもダメ、「黒すぎる」のもダメ。**1 ページあたり 30-60% の墨量** が経験則。

| 配置 | 推奨密度 | 失敗例 |
|---|---|---|
| Tear sheet (1 社情報) | 60-70% (情報詰め込み OK) | 30% (スカスカで「何も書いてない」と思われる) |
| Cover page | 10-20% (ほぼ余白) | 60% (派手で軽薄) |
| Executive summary | 40-50% | 80% (読み切れない) |
| 3-statement model sheet | 50-60% | 90% (見出しと数字の判別がつかない) |
| Football field chart | 30-40% (中央に集中) | 70% (チャート以外がうるさい) |

**測り方の目安**:
- Slack や Word 文書で資料の写真を撮り、目を細めて見て「黒い塊」になるかどうか。塊になる = 密度過剰。
- 1 シートに「8 個以上の章」が入っていたら大抵密度過剰。

### 1.5 「読者の視線動線」を設計する

人間の目は **左上→右下** に Z 字 / F 字を描く。重要なものをこの動線上に置く。

```
   ┌──────────────────────────────────────────────┐
   │ [Title]                          [Project ID]│  ← 視線の入口
   │ [Subtitle]                                   │
   │                                              │
   │ Key Takeaways                                │  ← 主張は左上から
   │  • Point 1                                   │
   │  • Point 2                                   │
   │                                              │
   │   ┌─────────────┐    ┌──────────────────┐    │
   │   │ Chart 1     │    │ Table 1          │    │  ← 詳細は中段
   │   └─────────────┘    └──────────────────┘    │
   │                                              │
   │ Source: ...                            [Pg #]│  ← 出典は右下
   └──────────────────────────────────────────────┘
```

> **原則 1.5**: タイトル左上、メッセージ左上、主証拠中段、出典/頁番号右下。


## 2. Typography (タイポグラフィ)

### 2.1 Body Font: Arial 10pt が **業界標準**

xlsx の本文は **Arial 10pt** が IB の de facto standard。これは「Macabacus」「Wall Street Prep」「Training The Street」など主要 IB トレーニングプロバイダがすべて推奨し、GS / MS / JPM の社内テンプレが踏襲している。

**根拠 (なぜ Arial 10pt か)**:
1. **可搬性 (cross-platform)**: Arial は Windows / Mac / Linux すべてに同名で存在し (Mac は Helvetica が代替展開されることもあるが Arial は別途 bundled)、Office 環境でレンダリング差が最小。
2. **数字の判別性**: Arial の数字は等幅に近く、桁が揃いやすい。特に `0` と `O`, `1` と `l` の区別が明確。
3. **歴史**: 1990 年代の Microsoft Office デフォルトが Arial 10pt で、当時のバンクで作られた DCF / LBO モデルがそのまま現代まで「正典」として継承されている。
4. **印刷時の解像度耐性**: 8pt まで縮小しても潰れない。

### 2.2 Calibri (Office 2007+ default) の評価

Office 2007 以降のデフォルトは Calibri 11pt だが、**IB ではほぼ採用されていない**。

| 軸 | Arial 10pt | Calibri 11pt |
|---|---|---|
| 視認性 | 優 (sans-serif, 等幅寄り) | 良 (やや細め) |
| 数字の整列 | 優 | 良 |
| 印刷時 | 優 | やや細い |
| バンク互換 | **完全互換** | 一部 (新世代の deal team) |
| 結論 | **推奨** | 非推奨 (社外向けは Arial に変換すべし) |

> **原則 2.2**: Arial 10pt をデフォルトに。Calibri はクライアント側のテンプレが Calibri ベースの場合のみ追従。

### 2.3 Times New Roman (セリフ系) は古い慣習

- **古いテンプレ** (1990 年代 / 米国の保守的なバルジブラケット系の一部) では Times New Roman 10pt を使う流派があった。
- **現代では非主流**。セリフは画面で読みにくく、画面ファースト時代に合わない。
- ただし「タイトルだけセリフ」(Lazard の cover page など) は今も生きている (見出し用 display font)。

### 2.4 階層 (Hierarchy)

```
┌─────────────────────────────────────────────────────────────────┐
│ FILE TITLE (cover only)        Arial 24pt Bold     #1F3A66      │
│ Section title                  Arial 14pt Bold     #1F3A66      │
│ Sub-section header             Arial 11pt Bold     #2D332E      │
│ Column header (year)           Arial 10pt Bold Italic #2D332E   │
│ Body / numbers                 Arial 10pt Regular  see Ch.3     │
│ Sub-line (indented item)       Arial 10pt Regular  #2D332E      │
│ Footnote / source              Arial 8pt Italic    #666666      │
│ Page number                    Arial 8pt Regular   #666666      │
└─────────────────────────────────────────────────────────────────┘
```

| 階層 | フォント | サイズ | Weight | Style | 色 |
|---|---|---|---|---|---|
| Cover title | Arial | 24pt | Bold | Regular | `#1F3A66` (navy) |
| Cover subtitle | Arial | 14pt | Regular | Regular | `#2D332E` (ink) |
| Section title (シート見出し) | Arial | 14pt | Bold | Regular | `#1F3A66` |
| Sub-section header | Arial | 11pt | Bold | Regular | `#2D332E` |
| Column header (year, period) | Arial | 10pt | Bold | **Italic** | `#2D332E` |
| Body label | Arial | 10pt | Regular | Regular | `#2D332E` |
| Body number | Arial | 10pt | Regular | Regular | functional color (see Ch.3) |
| Sub-line item | Arial | 10pt | Regular | Regular | `#2D332E` |
| Subtotal label | Arial | 10pt | **Bold** | Regular | `#2D332E` |
| Total label | Arial | 10pt | **Bold** | Regular | `#2D332E` |
| Footnote / source | Arial | 8pt | Regular | **Italic** | `#666666` (gray) |
| Page number | Arial | 8pt | Regular | Regular | `#666666` |

### 2.5 Italics の意味 — 5 つの限定用途のみ

Italic は乱用しないが、以下の 5 用途は **慣習的に italic を使う**:

1. **Year / Period header**: `2024A`, `2025E`, `2026P` (column header の年)
2. **Footnote / Source line**: `Source: Company filings, FactSet (as of Apr-26).`
3. **Non-financial label**: 比率や `n.a.`, `nm` などの定性ラベル
4. **Variable / placeholder**: `[Project Falcon]`, `[Target name]`
5. **Cross-reference**: `(see page 12)`, `(refer to Section 3.2)`

> **原則 2.5**: Italic は意味を持つときだけ。装飾目的の italic は禁止。

```
良い例:    Revenue            2024A    2025E    2026E    2027E
                              ──────   ──────   ──────   ──────
           Subscription         100      125      156      195
           Services              25       30       36       43
                              ──────   ──────   ──────   ──────
           Total                125      155      192      238
           
           Source: Company management projections (Apr-26).

悪い例:    *Revenue*           *2024A*  *2025E*   *2026E*   *2027E*  ← italic 多用
              Subscription       *100*    *125*    *156*    *195*    ← 数字を italic
```

### 2.6 Bold の使い方 — Subtotal, Total, セクションタイトル のみ

Bold は **構造の信号** であり、強調のための装飾ではない。

| 使う | 使わない |
|---|---|
| Subtotal 行のラベルと数字 | 「重要だから」と本文を bold |
| Total 行のラベルと数字 | "Hard input だから" の理由で bold (色で表現する) |
| セクションタイトル | 列ヘッダ全体 (italic で十分) |
| Sub-section header | チャートの全 data label |
| Cover title | TOC の章名すべて (現在頁のみ bold が許容) |

```
悪い例 (bold abuse):
   **Revenue**             **100**   **125**   **156**     ← 全部 bold
   **COGS**                 **(40)**  **(48)**  **(58)**
   **Gross profit**          **60**    **77**    **98**

良い例 (bold for structure):
    Revenue                   100      125      156
    COGS                      (40)     (48)     (58)
    **Gross profit**          **60**    **77**    **98**     ← subtotal だけ
```

### 2.7 Underline は禁止 (例外: ハイパーリンク)

下線は **罫線で代替できる** ので Excel では使わない。Web 文化からの「下線 = link」の刷り込みがあり、財務モデルの「強調」用途で下線を使うと読み手は link と誤認する。

| 場面 | 推奨 |
|---|---|
| Subtotal の上線 | **罫線** (cell border top, 1px black) で表現 |
| Total の二重線 | **罫線** (cell border bottom, double black) で表現 |
| ハイパーリンク (TOC からシート遷移) | 下線 OK (Excel default styling 任せ) |
| 強調 | bold か色で表現、下線は使わない |

### 2.8 Number 内のフォント整合性

数字は同じシート内では **同じフォント・同じサイズ・同じ書式** で揃える。

```
悪い例 (フォントサイズ混在):
   Revenue        100   ← Arial 10
   Growth         12%   ← Arial 9 (違う!)
   EBITDA          25   ← Arial 10
   EBITDA margin  25.0% ← Arial 11 (違う!)

良い例:
   Revenue        100
   Growth         12%
   EBITDA          25
   EBITDA margin  25.0%   ← 全部 Arial 10
```

ただし **% と倍数 (x) は本文と同じサイズで OK**, **章見出しは大きく**, **footnote は 8pt** という階層の中での「**水平方向の混在を避ける**」という意味。


## 3. Color Palette (色彩設計)

IB の色は **二層構造** で設計する:
- **Functional palette** (機能色): 全 IB 共通。色 = 数値の出自を意味する。
- **Brand palette** (ブランド色): 各 IB のアイデンティティ。表紙 / セクションヘッダ / ロゴ周辺で使う。本文には侵食しない。

### 3.1 Functional Palette — 全 IB 共通の「監査色」

| ID | 用途 | RGB | HEX | 適用 |
|---|---|---|---|---|
| `IB_HARD_INPUT` | Hard input (ベタ打ちセル) | (0, 0, 255) | `#0000FF` | 数式に使われていない、人間が直接打った数値 |
| `IB_FORMULA` | Formula (同シート計算式) | (0, 0, 0) | `#000000` | `=A1+B1` のような式 |
| `IB_LINK_INTRA` | Cross-sheet link (他シート参照) | (0, 128, 0) | `#008000` | `=Assumptions!B5` |
| `IB_LINK_EXTERNAL` | External link (別ファイル / API) | (255, 0, 0) | `#FF0000` | `=[Comps.xlsx]Sheet1!A1` |
| `IB_COMMENT` | Comment / non-financial label | (102, 102, 102) | `#666666` | "n.a.", "Memo:", footnote inline |
| `IB_INK` | 本文テキスト (label) | (45, 51, 46) | `#2D332E` | ラベル / 章タイトル |

> **原則 3.1**: Hard input は青、formula は黒、cross-sheet link は緑、external link は赤。**この 4 色の意味は普遍**。

**根拠**:
- バンカーは他人のモデルを 5 分以内に "audit" する必要がある。色だけで「ここは入力か計算か」を識別する。
- レビュー時に "I see all the blues — those are your assumptions" と指差せる。これが業界の暗黙の言語。
- 外部 link が赤なのは「**注意:依存が外にある**」のシグナル。

```
┌─────────── 良い例 (色で意味が分かる) ────────────────┐
│   Revenue growth (input)              15.0%   ← 青   │
│   Prior year revenue                   100    ← 緑   │
│   This year revenue                    115    ← 黒   │
│   Comp avg from FactSet                 18%   ← 赤   │
└──────────────────────────────────────────────────────┘
```

### 3.2 Brand Palette (8 大 IB)

各 IB がカバー / セクションヘッダ / フッター / ロゴ周辺で使うブランド色。本文の機能色とは混ぜない。

| Bank | Primary | HEX | Secondary | HEX | Notes |
|---|---|---|---|---|---|
| Goldman Sachs | Light navy | `#7399C6` | Black | `#000000` | サブライトブルー帯。罫線控えめ |
| Morgan Stanley | MS Blue | `#015DAA` | White / Gray | `#FFFFFF` | フッター帯ロゴ、青基調 |
| JP Morgan | JPM Brown | `#9E2A2B` | Cream | `#F5F0E1` | クラシック、罫線多 |
| Lazard | Lazard Orange | `#FF6E00` | Black | `#000000` | 上品、黒基調 + 差し色 |
| Evercore | Evercore Navy | `#001F3F` | White | `#FFFFFF` | モダン、ネイビー単色主義 |
| Centerview | Burgundy | `#6A1B2D` | Beige | `#E8DDC9` | 高級、シックなワインレッド |
| Houlihan Lokey | Maroon | `#7C2027` | Gray | `#7E7E7E` | 中堅向け、堅実感 |
| Rothschild | Rothschild Red | `#A8112A` | Black | `#000000` | 欧州伝統、ロゴカラー |

**原則 3.2**: ブランド色は **章タイトルバー、cover, footer ロゴ帯** にのみ使う。本文 (functional palette) を侵食しない。

```
┌──────────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ #015DAA (MS Blue) ▓▓▓▓▓▓▓▓▓▓▓▓▓▓│   ← header band
│ Section 1.  EBITDA Analysis                                   │
│                                                              │
│   Revenue                100   125   ...   ← 黒 formula      │
│   Growth %               15%   ...         ← 青 hard input  │
│                                                              │
│ Source: ...  (italic, gray)                                  │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 ボストン・コンサル / マッキンゼー由来 (PE / ストラテジー混在)

KKR / Blackstone / Bain Capital など PE 系は、ファウンダ出身が McKinsey / BCG だったりするので、**コンサル流の色設計** が混ざる:

| 色 | HEX | 用途 |
|---|---|---|
| Slate | `#6B7280` | サブテキスト / 軸ラベル |
| Pale Blue | `#A6BCD8` | チャートの主系統色 |
| Soft Green | `#7FB069` | 「成長」「ポジティブ」帯 |
| Soft Red | `#D08585` | 「縮小」「ネガティブ」帯 |
| Gold accent | `#C9A227` | 1 点強調のみ |

これらは **彩度を落とした** ペールトーンを使うのがコンサル流。本ガイドラインは IB ベースなので採用しないが、PE / strategy 文脈では許容する。

### 3.4 Background (背景色)

| 用途 | 色 | HEX | 補足 |
|---|---|---|---|
| Default sheet background | 純白 | `#FFFFFF` | 印刷を前提とすれば必ず白 |
| Section header band | 薄ネイビー | `#1F3A66` (text white) | バンクのブランド色で代替可 |
| Sub-section header band | 中グレー | `#404040` (text white) | 用途を絞る |
| Total row banding | 薄グレー | `#F2F2F2` | 行の塗りつぶし |
| Subtotal row banding | 極薄グレー | `#F8F8F8` | optional, 無くても可 |
| Working area / TODO | 薄イエロー | `#FFF9C4` | 「未確定」シグナル, 提出前に消す |
| Sensitivity hot zone | 薄レッド | `#F5C8C8` | hi end |
| Sensitivity cool zone | 薄ブルー | `#C8DCEF` | lo end |

> **原則 3.4**: 背景色は「機能シグナル」または「行構造の可読性向上」に限定する。装飾目的の塗りは禁止。

### 3.5 アクセント色 (1 点強調)

「ここだけ目立たせたい」という1 点強調は、**ページに 1 か所** が原則。

| 用途 | 推奨色 | HEX |
|---|---|---|
| Highlight (working) | Mustard Yellow | `#FFFF00` |
| Action item (TODO) | Mustard Yellow | `#FFFF00` |
| 1 点強調 (Cover の 1 単語など) | Accent Gold | `#C9A227` |
| Final answer / key number | Bold black + 罫線 (色不要) | — |

> **原則 3.5**: 「Final answer は色で目立たせない、構造で目立たせる」。罫線や太字、配置で目立たせる方が IB 流。

### 3.6 避けるべき色

| 色 | なぜダメか |
|---|---|
| Neon green / pink / purple | 装飾的すぎ、印刷で潰れる、若々しすぎ |
| 虹色 (chart の自動色) | 意味の階層が壊れる |
| 強いグラデーション | 印刷で帯状の縞模様になる、LCD で見ると ugly |
| 純黒 (`#000000`) を背景に | コントラストが強すぎ、他テキスト色と協調しない (ただし**フォーミュラの数字は純黒で OK**) |
| 高彩度 (Saturated >80%) の本文色 | 目に痛い、長時間レビュー不可 |
| 背景透過 (transparent, semi-transparent) | 印刷で予期しない結果になる |
| Mustard `#D9B441` | Act ガイドライン的に避ける (ただし IB アクセントの `#C9A227` は OK) |

### 3.7 Functional vs Brand の **絶対分離原則**

```
┌──────────── ❌ 悪い例 (functional と brand を混ぜた) ──────────┐
│                                                                │
│  Revenue (input)         15.0%   ← MS Blue #015DAA で書かれている│
│                                  → これは hard input なので青で  │
│                                    あるべきだが、ブランド色を    │
│                                    使ったため意味が崩壊         │
└────────────────────────────────────────────────────────────────┘

┌──────────── ✅ 良い例 (分離) ────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ EBITDA Analysis ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ← header に MS Blue │
│                                                              │
│  Revenue (input)         15.0%  ← Hard input は青 #0000FF     │
│  Revenue (formula)       115    ← Formula は黒 #000000        │
└──────────────────────────────────────────────────────────────┘
```

> **原則 3.7**: ブランド色は「装飾レイヤー」、機能色は「本文レイヤー」。**絶対に混ぜない**。


## 4. Layout & Grid (レイアウトとグリッド)

### 4.1 Column 構造の標準形

財務モデルの典型的な列構造:

```
   A     B                    C   D   E   F   G   H   I   J   K
  ┌──┬───────────────────────┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
  │  │ Label (科目名)        │$M │24A│25A│26E│27E│28E│29E│30E│31E│
  │  │                       │   │A  │A  │E  │E  │E  │E  │E  │E  │
  ├──┼───────────────────────┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
  │  │ Revenue               │   │100│125│155│190│230│275│320│370│
  │  │   Subscription        │   │ 80│100│125│155│190│230│270│315│
  │  │   Services            │   │ 20│ 25│ 30│ 35│ 40│ 45│ 50│ 55│
  │  └───────────────────────┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
  │
  └─ A: 左マージン (空)
     B: ラベル列 (~ 35-45 char)
     C: 単位 (¥M, $M, …)
     D-K: 期間列 (年 / 四半期)
```

**Column width 標準値** (Excel "width" 単位、Default font Arial 10pt):

| 列 | 用途 | Width | Pixel (≈) |
|---|---|---|---|
| A | 左マージン | 2.0 | 18 px |
| B | Main label | 38-45 | 285-330 px |
| C | Unit (¥M) | 8.0 | 65 px |
| D-N | Period column | 11-13 | 88-100 px |
| Last col | Right margin | 2.0 | 18 px |

> **原則 4.1**: 期間列はすべて **同じ width**。ラベル列は本文の最大文字数 + 余裕で決める。左右に必ず "margin column" を置く。

**根拠**:
- 期間列が揃っていないと「整っていない」感が出る。1 つでも違うと素人感丸出し。
- 左右の margin column はセル選択や印刷時の余白として機能する。
- B 列を 38-45 に保つことで、3-statement 標準項目が改行なく入る。

### 4.2 Row 高さの標準

| 用途 | Height (pt) |
|---|---|
| Default body | 15.0 |
| Spacer row (セクション間空行) | 8.0 |
| Sub-section header | 18.0 |
| Section title row | 22.0 |
| Cover title row | 32.0 |
| Footnote row | 12.0 |

> **原則 4.2**: 行高は「文字サイズ × 1.4-1.6」が目安。Body 10pt なら row 15pt。

### 4.3 Indentation (字下げ)

サブ項目は **1 タブ ≈ 2 半角スペース** または **B 列の indent level +1** で表現する。

```
Revenue                      ← Indent 0  (parent line)
  Subscription               ← Indent 1
    APAC                     ← Indent 2
    EMEA                     ← Indent 2
    Americas                 ← Indent 2
  Services                   ← Indent 1
Total revenue                ← Indent 0  (subtotal)
```

**xlsx 実装**:
- openpyxl: `cell.alignment = Alignment(indent=1)` (1 indent level)
- xlsxwriter: `format.set_indent(1)`
- ハードコードのスペース挿入は禁止 (検索性が落ちる)

### 4.4 Print Area & Margins

A4 横 (Landscape, 297×210 mm) を標準。米国向けは Letter 横 (11×8.5 in)。

| 設定 | 値 |
|---|---|
| Orientation | Landscape (横) |
| Paper size | A4 (日本) / Letter (米国) |
| Top margin | 0.5 inch (1.27 cm) |
| Bottom margin | 0.5 inch |
| Left margin | 0.5 inch |
| Right margin | 0.5 inch |
| Header margin | 0.3 inch |
| Footer margin | 0.3 inch |
| Print scaling | "Fit to 1 page wide" を最優先 |
| Print quality | 600 dpi |

> **原則 4.4**: 印刷時に「1 ページ幅に収める」を最優先。縦の分割は許容、横の分割は禁止 (横で分割されると数字を追えない)。

### 4.5 Header / Footer の標準

すべてのシートに同じ header/footer を入れる。`&[Tab]`, `&[Date]`, `&[Page]` といった Excel field を使う。

**Header (3 分割)**:

```
[左:プロジェクトコード]  [中:シート名]              [右:CONFIDENTIAL]
[Project Falcon]         [DCF Model]                [CONFIDENTIAL]
```

**Footer (3 分割)**:

```
[左:ファイル名]                  [中:日付]              [右:Page X of Y]
[Project_Falcon_Model_v3.4]      [Apr-26]               [Page 5 of 24]
```

**xlsx 実装 (openpyxl)**:
```python
ws.oddHeader.left.text = "Project Falcon"
ws.oddHeader.center.text = "&A"  # sheet name
ws.oddHeader.right.text = "CONFIDENTIAL"
ws.oddFooter.left.text = "&F"  # file name
ws.oddFooter.center.text = "&D"  # date
ws.oddFooter.right.text = "Page &P of &N"
```

### 4.6 Watermark (透かし)

| ステージ | Watermark | 表現 |
|---|---|---|
| Working draft (内部) | "DRAFT" | header の右に薄い赤 (`#F5C8C8`) で大きく |
| Distribution (取引先共有) | "CONFIDENTIAL" | header 右に黒文字、または背景 watermark |
| Final | (なし) | watermark なし、cover に "Final" と明記 |
| Highly sensitive | "PRIVILEGED & CONFIDENTIAL" | header 右に濃い赤、+ password protection |

**実装ヒント**: Excel に直接 watermark 機能はないので、以下の方法を使う:
- ヘッダに `&"Arial,Bold"&20&K00FF00CONFIDENTIAL` のような書式付きフィールドを置く
- 背景透かし: 印刷時にだけ表示するため、ヘッダ画像として PNG (透過、薄い灰色文字) を入れる

### 4.7 Freeze Panes (ウィンドウ枠の固定)

3-statement や DCF のような **横長モデル** では、必ず固定する。

| シートタイプ | Freeze 位置 |
|---|---|
| 3-statement | 行: ヘッダ下 (典型は row 6 or 7) / 列: 期間列の左 (典型は column D) |
| DCF | 同上 |
| Comps | 行: ヘッダ下 / 列: 会社名列の右 (typical: column C) |
| Assumptions | 行: ヘッダ下 / 列: ラベル列の右 |
| Cover, Exec summary | Freeze なし |

> **原則 4.7**: ラベル列と期間ヘッダが常に見えるよう freeze する。スクロール時に「今どこを見てるか」が分からないモデルは未完成。

### 4.8 Gridline と Sheet Tab

| 項目 | 推奨 |
|---|---|
| View > Gridlines | **OFF** (印刷時には常に OFF) |
| View > Headings | ON (作業中)、印刷時 OFF |
| Sheet tab color | 機能で色分け: Cover=Navy, Inputs=Yellow, Calc=White, Output=Green |
| Sheet 名 | `1_Cover`, `2_Summary`, `3_Inputs`, `4_Revenue`, `5_PnL`, `6_BS`, `7_CF`, `8_DCF`, `9_Comps`, `10_Sensitivity` |

> **原則 4.8**: Sheet 名にプレフィックス番号を入れて並びを固定。Sheet tab 色で機能領域が一目で分かるように。


## 5. Border & Cell Styling (罫線とセル装飾)

### 5.1 「No-Border 主義」の原則

財務モデルでは **罫線最小主義** (minimalism) を貫く。罫線は「区切り」のシグナルであり、装飾ではない。

> **原則 5.1**: 罫線は「数値が変わる境目」のみ。グリッド全体に罫線を引くのは **素人の特徴**。

**根拠**:
- 罫線が多いと「**罫線疲れ** (border fatigue)」を起こし、肝心の数字に目が行かない。
- 罫線がないシートは見やすく、印刷コストも低い (インク節約)。
- IB の慣習: gridlines OFF + selective borders で「ある一行が他より重い」を視覚化する。

```
┌─────────── 悪い例 (全セル罫線) ───────────┐
│┌────┬──────┬──────┬──────┬──────┐         │
││科目│2024A │2025E │2026E │2027E │         │
│├────┼──────┼──────┼──────┼──────┤         │
││Rev │  100 │  125 │  155 │  190 │         │
│├────┼──────┼──────┼──────┼──────┤         │
││Sub │   80 │  100 │  125 │  155 │         │
│├────┼──────┼──────┼──────┼──────┤         │
││Svc │   20 │   25 │   30 │   35 │         │
│└────┴──────┴──────┴──────┴──────┘         │
│ ↑ 全部に罫線 = 視線がノイズに引っ張られる │
└────────────────────────────────────────────┘

┌─────────── 良い例 (selective borders) ────┐
│                                            │
│  科目        2024A   2025E   2026E   2027E│
│              ──────  ──────  ──────  ─────│   ← 列ヘッダ下に細線のみ
│  Revenue                                   │
│    Subscription      80     100     125  155
│    Services          20      25      30   35
│              ──────  ──────  ──────  ─────│   ← subtotal 上に細線
│  Total revenue      100     125     155  190
│              ══════  ══════  ══════  ═════│   ← grand total 下に二重線
└────────────────────────────────────────────┘
```

### 5.2 Border の **正典** 5 種

| ID | 用途 | スタイル | 場所 |
|---|---|---|---|
| `BORDER_HEADER` | 列ヘッダ (年など) の下 | 1px solid black | header の bottom |
| `BORDER_SUBTOTAL_TOP` | Subtotal 行の上 | 1px solid black | subtotal の top |
| `BORDER_TOTAL_TOP` | Grand total 行の上 | 1px solid black | total の top |
| `BORDER_TOTAL_BOTTOM` | Grand total 行の下 | **double** black | total の bottom |
| `BORDER_SECTION_DIVIDER` | セクション切り | 1.5px solid `#1F3A66` (navy) | section header の top + bottom |

### 5.3 Subtotal / Total の罫線パターン

**Subtotal** (中間合計) — 上に 1 本線:

```
   Revenue
     Subscription           80      100      125
     Services               20       25       30
                          ─────    ─────    ─────         ← BORDER_SUBTOTAL_TOP
     Total revenue         100      125      155
```

**Grand Total** (最終合計) — 上に 1 本線, 下に二重線:

```
                          ─────    ─────    ─────         ← BORDER_TOTAL_TOP (1px)
     Net income             25       30       38
                          ═════    ═════    ═════         ← BORDER_TOTAL_BOTTOM (double)
```

> **原則 5.3**: "Top single, bottom double" は **会計の世界共通言語**。これを破ると即座に「素人」と判定される。

### 5.4 Section Divider (セクション切り)

複数のセクションが 1 シートにある場合、セクション間は罫線 + 空行で区切る。

```
                          ─────    ─────    ─────
     Total revenue         100      125      155
                          ═════    ═════    ═════
                                                       ← 空行 (height 8pt)
   ▓▓▓▓▓▓▓▓▓▓ COGS ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     ← section header band
                                                       ← 空行 (height 8pt)
     Direct cost           (40)     (48)     (58)
     ...
```

### 5.5 Cell Shading (セル塗りつぶし)

塗りつぶしは **限定用途のみ**:

| 目的 | 塗り色 | 文字色 | 例 |
|---|---|---|---|
| Section header band | `#1F3A66` (navy) | White | "1. Revenue" |
| Sub-section band | `#404040` (dark gray) | White | "1.1 Subscription" |
| Total row banding | `#F2F2F2` (light gray) | Black | "Net income" |
| Working / TODO | `#FFF9C4` (yellow) | Black | "[TBD]" |
| Sensitivity hot zone | `#F5C8C8` (light red) | Black | upper-right of heatmap |
| Sensitivity cool zone | `#C8DCEF` (light blue) | Black | lower-left of heatmap |
| Hard input area (optional) | `#F4F8FB` (very light blue) | Blue (`#0000FF`) | input box の背景 |

> **原則 5.5**: 装飾目的の塗りつぶしは禁止。塗りは「機能信号」または「行構造の可読性」のいずれかでなければならない。

### 5.6 Banding (Zebra striping)

「1 行おきに薄く塗る」の zebra striping は IB では **やらない**。理由:
- 印刷で帯がうるさい
- 罫線最小主義と相反する
- データ量が多い comps テーブルでは許容、ただし `#FAFAFA` のような **極薄** に限る

### 5.7 Conditional Formatting

条件付き書式は以下に限定して使う:

| 用途 | 推奨設定 |
|---|---|
| Sensitivity heatmap | 3-color scale (low=blue, mid=white, high=red) |
| Variance highlight | actual vs budget が ±5% を超えたら yellow fill |
| Negative value emphasis | (本文では `(123)` 表記で十分なので CF 不要) |
| Error trap | balance check が ≠ 0 → red fill (cf. `01b_integrity_and_anti_patterns.md`) |


## 6. Chart Design Standards (チャートデザイン)

> **基底原理 (Tufte 流)**: "Above all else, show the data" — 不要なインク (chart-junk) を削減し、data-ink ratio を最大化する。

### 6.1 共通ルール (全チャート共通)

| 項目 | 推奨 |
|---|---|
| Title | 上部、Arial 12pt Bold, ink (`#2D332E`) |
| Subtitle (unit) | Title 下、Arial 9pt Italic, gray (`#666666`) — 例: `(¥M, FY24A-FY28E)` |
| Axis labels | Arial 8pt, gray, 必要なときのみ |
| Axis tick marks | "inside, minor only" もしくは無し |
| Gridlines | 横方向のみ、薄グレー (`#D9D9D9`)、または完全になし |
| Data labels | **本文と同じ Arial 10pt** で**必ず付ける** (棒グラフ・折れ線) |
| Legend | 右上 or データ脇 (inline)、box は不要 |
| Background fill | 純白 (`#FFFFFF`)、グラデーション・パターン禁止 |
| Border | チャート枠は **無し** (cell の背景色で代替) |
| 3D effect | **完全禁止** |
| Drop shadow | **完全禁止** |

> **原則 6.1**: Data label がない bar / line chart は IB では認められない。読み手が「正確な数字」を取れないチャートは informal。

### 6.2 Football Field Chart (バリュエーションレンジ)

M&A や IPO の **valuation summary** で必ず使われる「ヨコ棒の積み重ね」型。

```
┌──────────────────── Valuation Football Field (¥B) ──────────────────┐
│                                                                      │
│ Trading comps   ├──────────●──────────┤                              │
│  EV/Revenue     │     8.2  │   12.5   │                              │
│                                                                      │
│ Trading comps   ├────────────●────────────┤                          │
│  EV/EBITDA      │      9.5   │     14.0   │                          │
│                                                                      │
│ Precedent M&A   ├──────────────●─────────────┤                       │
│                 │       11.0    │     16.5   │                       │
│                                                                      │
│ DCF (perp)      ├────●────┤                                          │
│                 │  9.5│ 11.5                                         │
│                                                                      │
│ DCF (exit mult) ├────────●────────┤                                  │
│                 │   10.0  │  13.0                                    │
│                                                                      │
│      Implied    ├ — — — — — — — — ┤                                  │
│      range      │      10.0       15.0                               │
│                                                                      │
│              0    5    10    15    20    25                          │
│                              EV (¥B)                                 │
│                                                                      │
│ Source: Company filings, FactSet (Apr-26).                           │
└──────────────────────────────────────────────────────────────────────┘
```

**書式規約**:
- 各バーの **両端に数字** (low / high)、中央にメッド・ポイント (●)
- バー色は **同じ色** (グラデーション可、ただし brand navy `#1F3A66` 系統)
- 「Implied range」は破線 (dashed) で重ね、別色 (gold accent `#C9A227`)
- X 軸は **EV (¥B)** または **Equity Value**, **share price** など; **タイトルに明記**
- データ脇 (バーの上 or 右) に "low / high / midpoint" を併記

### 6.3 Sensitivity Heatmap (感度表)

WACC × Terminal growth、Multiple × Growth など、**2 軸 × グリッド** で結果がどう変わるかを示す。

```
┌────── Implied Share Price Sensitivity (¥) ──────┐
│                                                 │
│             Terminal Growth Rate                │
│           1.0%  1.5%  2.0%  2.5%  3.0%          │
│         ┌─────┬─────┬─────┬─────┬─────┐         │
│   8.0%  │ 850 │ 920 │1,000│1,090│1,200│ ← red    │
│   8.5%  │ 800 │ 860 │ 930 │1,010│1,100│         │
│  WACC   │ 750 │ 800 │ 870 │ 940 │1,020│         │
│   9.5%  │ 700 │ 750 │ 810 │ 880 │ 950 │         │
│  10.0%  │ 660 │ 710 │ 760 │ 820 │ 890 │ ← blue   │
│         └─────┴─────┴─────┴─────┴─────┘         │
│                                                 │
│ Center value (Base case): 870  [bordered]       │
└─────────────────────────────────────────────────┘
```

**色配分**:
- Center cell (base case) は **太枠で囲む**、塗りは中性 (`#FFFFFF` or `#F2F2F2`)
- Hi end (右上 / 望ましい): 段階的に warm 色 (`#FBEAEA → #F5C8C8 → #ED9F9F`)
- Lo end (左下): 段階的に cool 色 (`#EAF1F8 → #C8DCEF → #9EBED9`)
- Excel の "3-color scale" conditional formatting を使う (red-white-blue)

> **原則 6.3**: Sensitivity table は数値の **方向性が直感的** に分かることが目的。色だけで暗黙の合否を作らないこと (場合によっては low が望ましい)。

### 6.4 Waterfall Chart (Bridge: EBITDA, ARR, Cash bridge)

「ある期から次の期への変化要因を分解」するチャート。

```
┌─────────────────── EBITDA Bridge: FY24A → FY25E (¥M) ───────────────────┐
│                                                                          │
│  300│         ┌─────┐                                                    │
│     │         │+150 │   ┌─────┐                                          │
│  250│         │     │   │ +50 │                                          │
│     │  ┌──┐   │     │   │     │                ┌─────┐                   │
│  200│  │  │   │     │   │     │   ┌─────┐      │     │                   │
│     │  │  │   │     │   │     │   │ -30 │      │     │                   │
│  150│  │  │   │     │   │     │   │     │      │     │                   │
│     │  │  │   │     │   │     │   │     │ ┌──┐ │     │                   │
│  100│  │  │   │     │   │     │   │     │ │-20│ │     │                   │
│     │  │FY│   │ Vol │   │Price│   │ Cost│ │FX │ │ FY  │                   │
│   50│  │24│   │ Up  │   │ Up  │   │  In │ │Hdwn│ │ 25  │                   │
│     │  │A │   │     │   │     │   │     │ │   │ │  E  │                   │
│    0└──┴──┴───┴─────┴───┴─────┴───┴─────┴─┴───┴─┴─────┴───────            │
│       180   +150     +50    -30    -20    330                            │
│                                                                          │
│ Source: Management projections.                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**色規約**:
| カテゴリ | 色 | HEX |
|---|---|---|
| Start / End total bar | Mid gray | `#7E7E7E` |
| Positive contribution (増加) | Navy | `#1F3A66` (or `#3F8F5E` for "growth" framing) |
| Negative contribution (減少) | Soft red | `#C04A4A` |
| Connector line (浮動バーをつなぐ点線) | Light gray | `#BFBFBF` |

> **原則 6.4**: 順序は「左→右の時系列」または「impact 大→小」。意味のない順序は避ける。

### 6.5 Bar Chart (基本)

最もよく使われるチャート。**シンプル・縦棒・data label ON** が基本。

| 項目 | 設定 |
|---|---|
| Bar fill | Navy (`#1F3A66`) もしくは brand primary 1 色 |
| Bar gap | 50-75% (棒が太すぎても痩せすぎてもダメ) |
| Y-axis | 必要に応じて省略可 (data label が全て付いていれば軸不要) |
| Gridline | 横方向、薄グレー (`#D9D9D9`) または **無し** |
| Data label position | "Outside end" (棒の上) |
| Sort order | 値の降順 (時系列でない限り) |

**比較用の色** (2-3 系列):
- 系列 1 (Actual / 主役): Navy (`#1F3A66`)
- 系列 2 (Plan / 比較): Light gray (`#BFBFBF`)
- 系列 3 (Forecast): Pale navy (`#A6BCD8`)

### 6.6 Line Chart

時系列やトレンド表示。

| 項目 | 設定 |
|---|---|
| Line color | Navy (`#1F3A66`) を main、複数は warm/cool で対比 |
| Line width | 2.0-2.5pt (細すぎず太すぎず) |
| Marker | 端点と要所のみ (毎点に丸を打たない) |
| Marker size | 5-7px |
| X-axis label | 年 (`24A`, `25E`...) — italic |
| Legend | 右上、または line の終端に inline label |
| Forecast portion | **破線** (dashed) で表現、forecast 期に切り替わる位置で線種を変える |

```
   ┌─────────────────── Revenue Trajectory (¥M) ─────────────────┐
   │                                                              │
   │   600 │                                          ●─ ─ ─ ─ ●  │
   │       │                                       ●─ ─                ← dashed (forecast)
   │   500 │                                ●                          │
   │       │                            ●                              │
   │   400 │                       ●                                   │
   │       │                  ●                                         │
   │   300 │             ●─                                             │
   │       │        ●                                                  │
   │   200 │  ●                                                        │
   │       │                                                           │
   │   100 │                                                           │
   │       │                                                           │
   │     0 └──────────────────────────────────────────────────────     │
   │        22A   23A   24A   25E   26E   27E   28E   29E   30E       │
   └──────────────────────────────────────────────────────────────────┘
```

### 6.7 Pie Chart は **避ける**

理由:
- 角度の大小判別は人間の知覚上 bar より弱い (Cleveland & McGill 1984)
- 凡例を追わないと意味が取れない
- 印刷で色判別が困難
- 「IB の資料に pie はほぼ出ない」が業界の経験則

**代替**: 横棒で 100% stacked、もしくは降順 bar chart。

### 6.8 Scatter Plot (Comp 散布図)

複数 comp を 2 軸で評価するときに使う (例: Growth vs Margin)。

| 項目 | 設定 |
|---|---|
| Marker | 中サイズの円 (Navy fill, white border 1px) |
| Label | 全マーカーに company ticker をマーカー右隣に配置 (overlap 回避必要) |
| Trend line | 必要に応じて破線、上下帯 ±1σ も可 |
| Quadrant lines | 四象限を切る場合、破線 (中央値) |
| Highlighted target | 別色 (gold accent `#C9A227`) で 1 点強調 |

### 6.9 Chart-Junk 回避 (Tufte 原則)

| やってはいけない | 理由 |
|---|---|
| 3D bar / 3D pie | 比例関係が歪む |
| Drop shadow | 印刷でノイズ、data-ink ratio を下げる |
| Gradient fill | 印刷で帯になる、色の意味が崩れる |
| Pattern fill (斜線・ドット) | モアレが起きる、可読性低下 |
| 余計なグリッド | data に注目が行かない |
| 余計な凡例 box | 装飾、白枠だけで囲む |
| Texture (大理石、紙質感) | 90 年代テンプレ感 |
| アニメーション (pptx 連携時) | バンカー資料は静的 |
| カラフルな全色使い | 意味の階層が壊れる |

> **原則 6.9**: 「印刷した時に **白黒** で意味が伝わるか？」を毎回テスト。色だけに依存したチャートは IB では認められない。


## 7. Page Composition (頁構成)

### 7.1 Cover Page (表紙)

Cover には情報を「載せすぎない」。**プロジェクト名、Subtitle、日付、機密区分、配布先** だけ。

```
┌─────────────────────────────────────────────────────────────────┐
│ [Bank Logo]                                          Project Falcon│
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│   Project Falcon                                                 │
│                                                                  │
│   Strategic Alternatives Review                                  │
│                                                                  │
│   Discussion Materials                                           │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│   April 2026                                                     │
│                                                                  │
│   Strictly Private and Confidential                              │
│                                                                  │
│                                                  [Bank name      │
│                                                   Investment     │
│                                                   Banking]       │
└─────────────────────────────────────────────────────────────────┘
```

| 要素 | 配置 | フォント | 色 |
|---|---|---|---|
| Bank logo | 左上 | (image) | brand color |
| Project code | 右上 | Arial 9pt italic | gray (`#666666`) |
| Title (project name) | 中央左寄せ、上から 1/3 | Arial 28pt Bold | `#1F3A66` (brand) |
| Subtitle | Title 下 | Arial 16pt Regular | ink |
| Document type | Subtitle 下 (e.g. "Discussion Materials") | Arial 12pt Italic | gray |
| Date | 中央左寄せ、下から 1/3 | Arial 11pt | ink |
| Confidentiality stamp | Date 下 | Arial 10pt italic | gray |
| Bank entity name | 右下 | Arial 9pt | gray |

> **原則 7.1**: Cover は「プロジェクトコード、Subtitle、日付、機密区分、bank entity」の **5 点セット** で完結。装飾画像、グラフィック、人物写真は禁止。

### 7.2 Executive Summary (エグゼクティブサマリ)

**1 ページ完結** が鉄則。読み手が EVP / CFO レベルなら、これしか読まない。

```
┌─── Project Falcon — Executive Summary ──────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                                                                  │
│ Situation Overview                                               │
│  • Target: Acme Corp ("Acme") — leading SaaS player in vertical X │
│  • Acme has approached us regarding a potential strategic review │
│  • Process anticipated to launch Q3 2026                          │
│                                                                  │
│ Key Financials (FY24A)                                           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │   Revenue                ¥12.5B    (CAGR 22-24A: +35%)    │    │
│  │   EBITDA                  ¥2.1B    (Margin: 16.8%)        │    │
│  │   Net cash               ¥4.2B                            │    │
│  │   Employees              ~350                              │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│ Preliminary Valuation Range                                      │
│   ¥80B - ¥120B  (8.0-12.0x EV/Revenue, 38-57x EV/EBITDA)         │
│                                                                  │
│ Recommended Process                                              │
│  1. Stage 1 (Apr-May): Management presentation, IOI solicitation │
│  2. Stage 2 (Jun-Jul): Diligence, LOI                            │
│  3. Stage 3 (Aug-Sep): Definitive agreement, closing             │
│                                                                  │
│ Source: Company management, FactSet (Apr-26).                    │
└──────────────────────────────────────────────────────────────────┘
```

**書式規則**:
- セクション数: 3-4 (situation, financials, valuation, process など)
- 各セクションは bullets で 3-5 行
- 数字は **必ず boxed area** で囲む (注目させる)
- 結論は最初か最後に書く (BLUF: Bottom Line Up Front)

### 7.3 Section Divider (章区切り)

長い deck では、章ごとに divider page を挟む。

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│   1.                                                             │
│                                                                  │
│   Market Overview                                                │
│   ───────────────                                                │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                  [Project Falcon]│
└─────────────────────────────────────────────────────────────────┘
```

- 章番号 (大きく、`#1F3A66` navy)
- 章タイトル (Arial 24pt Bold)
- 短い罫線
- それ以外は空白

> **原則 7.3**: Divider page は「呼吸」のためにある。情報を入れない。

### 7.4 Table of Contents (目次)

```
┌─── Table of Contents ────────────────────────────────────────────┐
│                                                                  │
│   1.  Executive Summary                                       2  │
│                                                                  │
│   2.  Market Overview                                         5  │
│        2.1  Industry landscape                                6  │
│        2.2  Key trends                                        8  │
│                                                                  │
│   3.  Company Overview                                       10  │
│        3.1  Business profile                                 11  │
│        3.2  Financial performance                            13  │
│                                                                  │
│   4.  Valuation                                              16  │
│        4.1  Methodology                                      17  │
│        4.2  Comparable company analysis                      18  │
│        4.3  Precedent transactions                           20  │
│        4.4  DCF analysis                                     22  │
│                                                                  │
│   5.  Process & Next Steps                                   24  │
│                                                                  │
│   Appendix                                                       │
│        A.  Detailed financial model                          A-1 │
│        B.  Comparable companies detail                       A-5 │
│        C.  Precedent transactions detail                     A-9 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**書式規則**:
- 章: Arial 11pt Bold, ink
- サブ章: Arial 10pt Regular, ink, 1 indent
- ページ番号: 右揃え、Arial 10pt Regular, ink
- リーダー (`....`) は使わない (空白でつなぐ)
- ハイパーリンクは下線 OK (Excel default)

### 7.5 Tear Sheet (1 ページ会社情報)

各 comp の 1 社情報を 1 ページに濃縮した、IB 流の "company profile"。

```
┌──── Acme Corp (TYO: 1234) ───────────────────────────────────────┐
│                                                                  │
│  Description                       │  Financial Highlights (¥M) │
│  ─────────────                     │  ─────────────────────     │
│  Acme Corp is a leading vertical   │            FY22A FY23A FY24A│
│  SaaS provider serving the         │  Revenue   8,200 10,100 12,500│
│  Japanese hospitality industry,    │  Growth %  +28%  +23%  +24% │
│  with ~50,000 SMB customers as of  │  Gross %   72%   74%   75%  │
│  end-FY24A.                        │  EBITDA     980 1,520 2,100 │
│                                    │  Margin    12%   15%   17%  │
│  Founded: 2014                     │  Net cash 2,800 3,400 4,200 │
│  HQ: Tokyo, Japan                  │                            │
│  Employees: ~350                   │  Trading Multiples (NTM)   │
│  Listed: TSE Growth (2022)         │  ─────────────────────     │
│                                    │  EV/Revenue       8.5x      │
│  Investors                         │  EV/EBITDA       45.0x      │
│  ─────────────                     │  P/E             62.0x      │
│  - JAFCO (10%)                     │                            │
│  - Globis Capital (8%)             │  Stock Price                │
│  - SBI Investment (5%)             │  ─────────────              │
│                                    │  Current     ¥3,500         │
│  Management                        │  52w high    ¥4,200         │
│  ─────────────                     │  52w low     ¥2,800         │
│  CEO: Taro Yamada                  │  Mkt cap    ¥85B            │
│  CFO: Hanako Sato                  │  EV         ¥81B            │
│                                    │                            │
│  Source: Company filings, FactSet (as of 30-Apr-26).             │
└──────────────────────────────────────────────────────────────────┘
```

**書式規則**:
- 2 列レイアウト (左: 説明、右: 数字)
- ヘッダ: 会社名 (大) + ティッカー (中)
- 各ブロックの間に細い罫線
- 数字は **NTM (Next Twelve Months)** ベース、または **LTM** ベース、明記する

### 7.6 ページ番号

- 全ページに番号 (cover を除く)
- 表記: `Page 5 of 24` または `5` 単独
- 配置: footer 右下
- フォント: Arial 8pt regular, gray


## 8. Banker Style Cues (細部の美学)

ここからは「微妙だが効く」スタイルの集合。これらが合致しているだけで「IB が出した」と分かる。

### 8.1 数字書式 (Number Formatting)

**基本原則**: 数字は **右揃え**、3 桁ごとカンマ、整数は小数なし、ratio は小数 1-2 桁。

| 種別 | 書式コード (Excel) | 表示例 | 備考 |
|---|---|---|---|
| Money (¥M / $M) | `#,##0;(#,##0);"-"` | `1,250` `(450)` `-` | カンマ + 括弧 + zero dash |
| Money (¥B / $B) | `#,##0.0;(#,##0.0);"-"` | `12.5` `(4.5)` `-` | 小数 1 桁 |
| Percent | `0.0%;(0.0%);"-"` | `15.0%` `(2.5%)` `-` | 小数 1 桁が原則 |
| Multiple (x) | `0.0"x";(0.0"x");"-"` | `8.5x` `(1.2x)` `-` | 小数 1 桁 |
| Per share | `#,##0.00;(#,##0.00);"-"` | `1,250.50` | 小数 2 桁 |
| Year | `0` | `2024` | 4 桁、no comma |
| Count (人数, 件数) | `#,##0` | `350` | small int も OK |
| Date | `mmm-yy` | `Apr-26` | 短縮形 |

> **原則 8.1**: 「unit はヘッダ行に書き、数字本体には書かない」。`¥1,250M` は冗長。`(¥M)` をヘッダに付けて、本体は `1,250`。

### 8.2 Negative Numbers — 括弧表記

赤字 (red font) ではなく **括弧** `(123)` を使う。

```
   悪い例:    Revenue           1,250
              COGS              -450    ← マイナス記号、しかも red
              Gross profit       800

   良い例:    Revenue           1,250
              COGS              (450)   ← 括弧、黒字
              Gross profit        800
```

**根拠**:
- 会計の世界共通言語 (US GAAP / IFRS どちらも括弧が標準)
- マイナス記号はカンマと混同される (`-1,250` → `1,250` と読み間違える)
- 赤字は色覚異常の人に伝わらない

### 8.3 Zero Display — `-` (ダッシュ)

**ゼロは `-` で表示**、`0` をベタ書きしない。

```
   悪い例:    Revenue            1,250
              Other revenue          0    ← 数字の 0
              Total revenue      1,250

   良い例:    Revenue            1,250
              Other revenue          -    ← dash で zero を表現
              Total revenue      1,250
```

**根拠**:
- "0" は「0 と計算した」のシグナル、"-" は「該当なし / N/A」のシグナル
- 視覚的に zero が引き立たない (邪魔にならない)
- format `;;"-"` を使えば数式上は 0 のまま、表示だけ dash

### 8.4 N/A, NM, NMF の使い分け

| 表記 | 意味 | 場面 |
|---|---|---|
| `n.a.` | Not available (データがない) | comp の中で 1 社だけ未開示など |
| `nm` | Not meaningful (数値はあるが意味がない) | 例: 赤字会社の P/E、分母負の比率 |
| `n.m.f.` | Not meaningfully financial (= nm) | nm と同義、米国流 |
| 空欄 | (使わない) | 必ず `n.a.` か `-` を入れる |

> **原則 8.4**: 数値が無い理由を読み手に伝える。空欄を残すのは厳禁。

### 8.5 Footnote 番号 (上付き)

Footnote には**上付き数字** (`¹`, `²`, `³`) を使う。Excel では `Char(185)` for `¹` などを使うか、文字列で上付き化。

```
   Acme Corp                      1,250¹
   Beta Co                          850
   Comp avg (excl. Acme)            720²
   ─────────────────────────
   ¹  Excludes one-time gain of ¥150M from divestiture.
   ²  Adjusted for FY24 pro forma run-rate.
```

### 8.6 Source Line — 必ず付ける

すべての table / chart の下には source line を入れる。これがない資料は **未完成扱い**。

**標準書式**:
```
Source: [Source 1], [Source 2] ([as-of date]).
```

**例**:
```
Source: Company filings, FactSet (as of 30-Apr-26).
Source: Bloomberg (4-May-26), broker research.
Source: Management projections (Apr-26 plan).
Source: S&P Capital IQ (as of 30-Apr-26).
```

**書式**:
- 開始は `Source:` (cap S)、コロンの後にスペース 1 個
- `(as of <date>)` は最後に括弧で
- フォント: Arial 8pt italic, gray (`#666666`)
- 配置: table / chart の左下、table 罫線から 1 行下

### 8.7 Note: 行 — 注釈

数値の解釈に必要な context を `Note:` で付ける。Source の前に置く。

```
   ...table content...
   
   Note: All figures are pro forma for the divestiture of XYZ business completed
         in March 2026. Historical periods restated.
   Source: Company filings, FactSet (as of 30-Apr-26).
```

### 8.8 略語 (Abbreviations)

IB で頻繁に使う略語は、**period (`.`) を付けない** のが現代の流儀。Pre-2010 は dot を付けていたが、現代は no-dot が主流。

| 略語 | 意味 | 備考 |
|---|---|---|
| YoY | Year-over-year | (`Y/Y` 表記もあり、no dot で書く) |
| QoQ | Quarter-over-quarter | (`Q/Q` 表記もあり) |
| MoM | Month-over-month | |
| LTM | Last Twelve Months | trailing 12-month |
| NTM | Next Twelve Months | forward 12-month |
| CY / FY | Calendar Year / Fiscal Year | `CY24`, `FY24` |
| CAGR | Compound Annual Growth Rate | `CAGR 22-24A: +35%` |
| BPS | Basis Points | `100bps = 1.0%` (lowercase `bps` も可) |
| YTD | Year-to-Date | |
| MTD | Month-to-Date | |
| EV | Enterprise Value | |
| MC | Market Cap | (`Mkt cap` 表記が一般的) |
| EBITDA | Earnings Before Interest, Tax, D&A | (period なしで書く) |
| D&A | Depreciation & Amortization | (`&` 推奨, `and` ではなく) |
| NOPAT | Net Operating Profit After Tax | |
| FCF / UFCF / LFCF | Free Cash Flow / Unlevered / Levered FCF | |
| DCF | Discounted Cash Flow | |
| WACC | Weighted Average Cost of Capital | |
| PV / NPV | Present Value / Net Present Value | |
| TV | Terminal Value | |
| LBO | Leveraged Buyout | |
| MOIC | Multiple on Invested Capital | |
| IRR | Internal Rate of Return | |
| ARR | Annual Recurring Revenue | (SaaS) |
| MRR | Monthly Recurring Revenue | (SaaS) |
| GMV | Gross Merchandise Value | (e-commerce) |

> **原則 8.8**: 略語の dot は **付けない** が現代流。一度シート内で使ったら統一する (`Y/Y` と `YoY` の混在禁止)。

### 8.9 Year Header の書き方

| 表記 | 意味 |
|---|---|
| `2024A` | Actual (実績) |
| `2024E` | Estimate (見込み = 当期予測) |
| `2024P` | Projected (予測, やや formal) |
| `2024F` | Forecast (= P) |
| `2024B` | Budget (予算) |
| `LTM` | Last Twelve Months |
| `Pro forma` / `PF` | Pro forma (調整後) |

**書式**:
- 全て **italic**
- 末尾の A/E は **そのまま** italic で書く
- `2024A` は year + suffix の連結 (スペースなし)

### 8.10 Currency / Unit の表記

- Header に `(¥M)`, `($mm)`, `(€'000)` のように unit を明記
- 同シート内で unit を変えない (m と mm を混在させない)
- 数字本体に unit を書かない (`1,250` であって `1,250M` ではない)

| 通貨 | 単位 | Header 表記 |
|---|---|---|
| 円 | 百万円 | `(¥M)` または `(JPY M)` |
| 円 | 十億円 | `(¥B)` |
| 米ドル | 千米ドル | `($'000)` |
| 米ドル | 百万米ドル | `($mm)` または `($M)` |
| 米ドル | 十億米ドル | `($B)` または `($bn)` |
| ユーロ | 百万ユーロ | `(€mm)` |

> **原則 8.10**: Unit は header の一行目 or 二行目に書く。本体に書くのは「unit が混在する単一行」など特殊ケースのみ。

### 8.11 Date 表記

- 短縮: `Apr-26`, `Q1-26`, `1Q26`
- 長: `April 30, 2026`, `30-Apr-26`
- 日本式: `2026年4月` (和文文書のみ)

シート内で **混在させない**。資料全体で 1 種類に統一。

### 8.12 Right-Justification (右揃え) の徹底

数字は **必ず右揃え**、ラベルは **左揃え**。中央揃えは原則使わない (例外: 列ヘッダの年など、列幅に対してラベル幅が狭い時のみ)。

> **原則 8.12**: "Numbers right, labels left, never center." 中央揃えで桁が揃わなくなる例は素人モデルの典型。

### 8.13 Currency Sign の場所

- Header に `(¥M)` と書いたら、本体には `¥` 記号を **付けない**
- 例外: cover page や exec summary の "highlighted figures" で **1 か所だけ** 付ける (`¥12.5B`) — 強調目的
- 本文 table の中で `¥` を毎セルに付けない (冗長)


## 9. バンク別のスタイル特徴 (Bank-Specific Style)

各バンクの「美意識」は微妙に異なる。クライアントの好みやマンデートに応じて bank-specific style を採用することがある。

### 9.1 Goldman Sachs

| 項目 | 特徴 |
|---|---|
| **基調** | 最小主義 (minimalism)、罫線控えめ |
| **色** | Navy `#7399C6` のライトブルー帯、本文は墨黒 |
| **書体** | Arial 10pt、見出しも sans のみ |
| **余白** | やや広め、空白多め |
| **テーブル** | gridline なし、subtotal/total のみ罫線 |
| **チャート** | 1 色基調 (light navy)、最小限の data label |
| **カバー** | 巨大ロゴ + 中央寄せ、装飾なし |
| **クセ** | 「読み手を信じている」造り。脚注やコメントが少ない |

> GS は **「美しさは引き算で作る」** の典型。罫線も色も極力減らす。

### 9.2 Morgan Stanley

| 項目 | 特徴 |
|---|---|
| **基調** | Blue `#015DAA` を強く打ち出す |
| **色** | MS Blue が章ヘッダ band, footer band, ロゴ周りに |
| **書体** | Arial 10pt |
| **余白** | 標準 |
| **テーブル** | header band が strong blue、本文は GS より少し dense |
| **チャート** | MS Blue 主体、補助色は light gray |
| **カバー** | Footer band にロゴ ("Morgan Stanley") を白抜き |
| **クセ** | "Footer ribbon" が見分けポイント。MS は全ページ底にロゴ帯 |

### 9.3 JP Morgan

| 項目 | 特徴 |
|---|---|
| **基調** | クラシック、罫線多め (テーブル外枠 + subtotal) |
| **色** | JPM Brown `#9E2A2B` (ロゴ色) + Cream `#F5F0E1` (背景) |
| **書体** | Arial 10pt、表紙は Times-style serif の場合あり |
| **余白** | やや tight (情報密度高い) |
| **テーブル** | 罫線多め (header underline + section box) |
| **チャート** | brown/cream 系、補助色は navy |
| **カバー** | Cream 背景、brown ロゴ、保守的 |
| **クセ** | 「老舗の重厚さ」を演出。情報を載せ込む |

### 9.4 Lazard

| 項目 | 特徴 |
|---|---|
| **基調** | 上品、エレガント |
| **色** | 黒基調 + Lazard Orange `#FF6E00` を 1 点アクセント |
| **書体** | Arial 10pt body, **見出しに serif** (Times) を使うことも |
| **余白** | 広め、白の使い方が美しい |
| **テーブル** | 罫線最小、空白で区切る |
| **チャート** | 黒 + 1 色アクセント |
| **カバー** | 黒地 + オレンジロゴ、または白地 + 黒文字 |
| **クセ** | 「ヨーロッパの blue blood」感。古典的 + モダン |

### 9.5 Evercore

| 項目 | 特徴 |
|---|---|
| **基調** | モダン、データドリブン |
| **色** | Evercore Navy `#001F3F` 単色主義 (ほぼ navy のみ) |
| **書体** | Arial 10pt、見出しは weight 700 |
| **余白** | 標準、整理整頓 |
| **テーブル** | header band navy、subtotal罫線 |
| **チャート** | navy 基調、tonal variation (濃淡) |
| **カバー** | navy 背景 + 白文字、or 白背景 + navy 文字 |
| **クセ** | 「単色の美学」。色を増やさず濃淡で階層を作る |

### 9.6 Centerview Partners

| 項目 | 特徴 |
|---|---|
| **基調** | 高級、シック |
| **色** | Burgundy `#6A1B2D` + Beige `#E8DDC9` |
| **書体** | Arial / Helvetica 10pt |
| **余白** | 広め |
| **テーブル** | 罫線少、burgundy header band |
| **チャート** | burgundy + beige、ワインレッド系 |
| **カバー** | beige 背景 + burgundy 文字 |
| **クセ** | 「boutique としての差別化」。色で記憶に残す |

### 9.7 Houlihan Lokey

| 項目 | 特徴 |
|---|---|
| **基調** | 中堅向け、堅実 |
| **色** | Maroon `#7C2027` + Gray `#7E7E7E` |
| **書体** | Arial 10pt |
| **余白** | tight (mid-market は数字を細かく見せる) |
| **テーブル** | 罫線多め、データ細密 |
| **チャート** | maroon + gray、保守的 |
| **カバー** | maroon ロゴ、白背景 |
| **クセ** | 「mid-market の信頼感」。情報量を多く、説明を厚く |

### 9.8 Rothschild & Co

| 項目 | 特徴 |
|---|---|
| **基調** | 欧州伝統、保守的 |
| **色** | Rothschild Red `#A8112A` + 黒 |
| **書体** | Arial / serif 混在 (見出し serif) |
| **余白** | 広め |
| **テーブル** | 罫線控えめ、伝統的 |
| **クセ** | 「歴史と格式」。欧州 buy-side との親和性 |

### 9.9 PE Sponsor 系 (KKR / Blackstone / Bain Capital)

| 項目 | 特徴 |
|---|---|
| **基調** | データ密度高い、IC paper 風 |
| **色** | コンサル流のペールトーン (slate, pale blue) も混在 |
| **書体** | Arial 10pt |
| **余白** | tight |
| **テーブル** | 数値細密、注釈多 |
| **チャート** | bar / line / waterfall 多用、scatter で comp 配置 |
| **クセ** | "Investment memo" 風。intent / risks / mitigants が太字で書かれる |

### 9.10 a16z / Bessemer (VC visual style)

| 項目 | 特徴 |
|---|---|
| **基調** | カジュアル、ブランド色強め |
| **色** | a16z = 黒+赤 (ロゴ)、Bessemer = green |
| **書体** | sans-serif (Helvetica, Inter)、見出し大きい |
| **余白** | 広い、white space 多用 |
| **テーブル** | 必要最小限、視覚化重視 |
| **チャート** | カラフル、流線的、bar chart アニメーション (web) |
| **クセ** | "founder-friendly" のトーン。情報より「物語」 |

> **本ガイドラインのデフォルト**: GS / Evercore に近い「**最小主義 + ネイビー基調**」を採用する。理由は ① 全 IB の最大公約数、② 印刷耐性、③ 日本語フォントとの親和性。


## 10. 日本の IB / 証券会社のスタイル差

### 10.1 野村證券 (Nomura)

| 項目 | 特徴 |
|---|---|
| **基調** | 細密、罫線多め、保守的 |
| **色** | Nomura Red `#A4252F` (アクセントのみ) + 黒 |
| **書体** | Arial 10pt + 和文 MS Pゴシック (古典) / Meiryo (新) |
| **テーブル** | 罫線多め (全セル罫線も許容)、subtotal/total に二重線 |
| **クセ** | 注釈 (脚注) が多く、丁寧な定義リストが付く |
| **数字** | カンマ + 括弧、伝統的に「百万円」を多用 |

### 10.2 大和証券 (Daiwa)

| 項目 | 特徴 |
|---|---|
| **基調** | 表組み丁寧、和文混在型 |
| **色** | Daiwa Green `#005831` |
| **書体** | Arial + Meiryo |
| **テーブル** | 罫線中庸、和文の改行に配慮 |
| **クセ** | 和英混在の用語表記 (「売上高 (Revenue)」など) |

### 10.3 みずほ証券 (Mizuho)

| 項目 | 特徴 |
|---|---|
| **基調** | 図表多用、可読性重視 |
| **色** | Mizuho Blue `#1A4F7C` |
| **書体** | Arial + Meiryo / 游ゴシック |
| **テーブル** | 罫線少、figure 多用 |
| **クセ** | 1 ページ 1 メッセージ、説明的 |

### 10.4 三菱 UFJ モルガン・スタンレー (MUMSS)

| 項目 | 特徴 |
|---|---|
| **基調** | MS スタイル準拠 + 和文要素 |
| **色** | MS Blue `#015DAA` 寄り、MUFG Red も併用 |
| **書体** | Arial + Meiryo |
| **テーブル** | MS と同様、header band 強調 |
| **クセ** | 二社合弁ゆえ、Bank ロゴが 2 つ並ぶ cover |

### 10.5 SMBC 日興証券

| 項目 | 特徴 |
|---|---|
| **基調** | 構成シンプル、保守的 |
| **色** | SMBC Green `#00973B` |
| **書体** | Arial + Meiryo |
| **クセ** | 和文比率が他より高い |

### 10.6 GCA / Houlihan Lokey 日本

| 項目 | 特徴 |
|---|---|
| **基調** | 中堅 / 中小型 M&A 向け、明快 |
| **色** | Houlihan Maroon `#7C2027` |
| **クセ** | 定量分析ベタベタ、和文 + 英数字混在 OK |

### 10.7 GLOBIS / グリー / VC 系

| 項目 | 特徴 |
|---|---|
| **基調** | シンプル、creator-friendly |
| **色** | 各 VC のロゴ色 (Globis = 赤、JAFCO = 青) |
| **書体** | Sans-serif、和文は Noto Sans JP / 游ゴシック |
| **クセ** | カジュアル、a16z スタイル寄り |

### 10.8 日本語 (Japanese) Typography

日本語が混在する財務モデルでの注意点:

| 用途 | 推奨フォント | 備考 |
|---|---|---|
| 和文本文 | Meiryo / Noto Sans JP | 明朝より gothic が読みやすい |
| 英数字本文 | Arial 10pt | 和文と高さが合う |
| 旧式 (互換性重視) | MS Pゴシック | Office 2007 以前との互換 |
| 印刷重視 | 游ゴシック | 印刷で潰れにくい |

**和英混在の幅問題**:
- 和文 1 文字 ≈ 英文 2 文字の幅。ラベル列の文字数を計算するときは「半角換算」で。
- 行高は 16-18pt が和文の安全圏 (15pt だと和文の高さがギリギリ)

```
   ❌  Revenue売上高              100   125   ← 半角と全角混じり、整列困難
   ✅  Revenue (売上高)            100   125   ← 半角ベース + 括弧で和文補足
   ✅  売上高 (Revenue)            100   125   ← 和文ベース、初出のみ英語併記
```

> **原則 10.8**: 和文・英文を混ぜる場合、**括弧併記** で 1 行に共存させる。改行や 2 段書きはモデルでは避ける。

### 10.9 数値表現 — 日本特有の流儀

| 米国流 | 日本流 | 推奨 |
|---|---|---|
| `($M)` | `(百万円)` または `(¥M)` | 国際向け = `(¥M)`, 国内向け = `(百万円)` |
| `$1.5B` | `15億円` または `¥1.5B` | 同上 |
| `2.5x` | `2.5倍` または `2.5x` | 同上 |
| `15%` | `15%` または `15.0%` | 同 (% は世界共通) |
| `(1,250)` | `△1,250` または `(1,250)` | **国内向けは `△`** が伝統的、国際向けは括弧 |

> **原則 10.9**: 国際向け資料は **`(¥M)` + 括弧マイナス** 統一、純国内向け資料は `(百万円)` + `△マイナス` も許容。


## 11. Banker Mode vs VC Mode vs PE Mode

**同じ財務モデル** でも、読み手・使用文脈によって見せ方を変える。

### 11.1 Banker Mode (公開市場 / DCM / ECM / M&A advisory)

| 軸 | 設定 |
|---|---|
| 基調 | 形式重視、保守的、minimum decoration |
| 色 | functional palette (青/黒/緑/赤) + brand navy |
| 罫線 | 最小、subtotal/total のみ |
| チャート | football field、sensitivity heatmap、waterfall |
| 数字 | 細密 (¥M unit, 1 decimal for ratios) |
| 出典 | 必須、italic gray |
| ページ数 | 多め (20-50 ページ) |
| ラベル | 厳密 (LTM, NTM, FY 表記をきちんと) |
| 例 | DCF model, comparable companies analysis, M&A pitch |

### 11.2 VC Mode (Early-stage focus)

| 軸 | 設定 |
|---|---|
| 基調 | カジュアル、storytelling 重視 |
| 色 | brand color 強く、accent 色も許容 |
| 罫線 | ほぼなし、空白で区切る |
| チャート | bar chart, growth curve、ホッケースティック許容 |
| 数字 | 直感的 ($1M, $10M, $100M の K/M/B 表記) |
| 出典 | あれば良い (社内データ前提) |
| ページ数 | 短い (10-20 スライド) |
| ラベル | 弱め (ARR, MAU など SaaS 用語直接) |
| 例 | Pitch deck, board update, Series A/B 資料 |

### 11.3 PE Mode (LBO / Buyout / Growth Equity)

| 軸 | 設定 |
|---|---|
| 基調 | モデル中心、color minimal、数値細密 |
| 色 | functional palette + sponsor brand color |
| 罫線 | 標準 |
| チャート | LBO returns chart, IRR sensitivity, value creation bridge |
| 数字 | 超細密 (basis points, decimal precision) |
| 出典 | 必須、CIM 引用も明記 |
| ページ数 | 中 (15-30 ページ) IC paper 風 |
| ラベル | 厳密 + 専門用語 (TEV, MOIC, IRR, LBO returns) |
| 例 | IC memo, LBO model output, fund report |

### 11.4 Strategy Consulting Mode (BCG / Bain / McKinsey)

| 軸 | 設定 |
|---|---|
| 基調 | チャート命、ペルソナ・カスタマージャーニー混在 |
| 色 | コンサル流ペールトーン (slate, pale blue, muted) |
| 罫線 | 中程度 |
| チャート | 2x2 matrix, journey map, value chain, McKinsey horizon |
| 数字 | 中程度 (illustrative) |
| 出典 | 必須、二次調査多 |
| ページ数 | 多い (50+ スライド) |
| ラベル | フレームワーク言語 |
| 例 | Strategy review, market entry, due diligence |

### 11.5 ハイブリッド: Startup-向け IB 品質 (本ガイドラインのターゲット)

スタートアップ向けに **「VC ライト + IB 規律」** のハイブリッド:

| 軸 | 設定 |
|---|---|
| 基調 | IB の規律を残しつつ、storytelling 要素を許容 |
| 色 | IB functional palette + 1 brand accent |
| 罫線 | IB 流の最小主義 |
| チャート | football field + waterfall + cohort chart |
| 数字 | IB 細密 (1 decimal) |
| 出典 | 必須 |
| ラベル | 厳密 (NTM, LTM) + SaaS 用語 (ARR, NRR, CAC) |
| 例 | Series C+ pitch、IPO ready 資料、PE 売却用モデル |

> **原則 11.5**: 「**IB 規律 + SaaS metric 流暢さ**」が本ガイドラインのコアトーン。VC mode のラフさには寄せない、しかし IB の重厚さに比べると挙動軽め。


## 12. Pitchbook 連携設計 (xlsx → pptx)

財務モデル (xlsx) は最終的に pptx の pitchbook に貼り付けられる。**「貼った時に崩れない」** ように設計しておくのが IB 流。

### 12.1 Linked Table (Excel → PowerPoint)

PowerPoint で「**Paste Special > Paste Link > Microsoft Excel Worksheet Object**」を使うと、Excel が変わると PPT も自動更新される。

| 留意点 | 対応 |
|---|---|
| Excel と PPT は **同じディレクトリ** に置く | 共有フォルダ前提で運用 |
| Excel の画像コピー領域は **named range** で固定 | `Comps_Output_Area` のように named range にしておく |
| 列幅・行高は固定 | autoSize で動かないように |
| フォントは PPT 側にも同じ Arial を埋め込む | font embedding 必須 |
| 印刷範囲のスケールは 100% 固定 | "Fit to page" で auto scale すると貼付時に崩れる |

> **原則 12.1**: 「**コピー領域 = named range**」「**Linked paste**」「**Font embed**」の 3 点セットで、貼った後の崩れを防ぐ。

### 12.2 PPT に貼るときの 3 つの方法

| 方法 | 利点 | 欠点 | 用途 |
|---|---|---|---|
| Paste as Image (PNG) | 崩れない、軽い | 修正したら貼り直し | Final 版 |
| Paste Special > Linked | 自動更新 | リンク切れリスク | Working draft |
| Paste Special > Embedded | self-contained | ファイル肥大 | アーカイブ用 |

**推奨**:
- Working draft 期: Linked
- 提出版: Image (フリーズして崩れリスクをなくす)

### 12.3 Vector 化のためのチャート構造

PPT で拡大しても綺麗に見せるため、**ベクター** で持ち込む。

- xlsx の chart object を **「Paste as Enhanced Metafile (EMF)」** で貼る → PPT 上でベクターとして拡大耐性
- または **xlsx 上で chart を直接編集** して PPT に Linked 貼り付け
- 画像 (PNG) で貼ると、印刷で **アンチエイリアスのジャギー** が出るので避ける

### 12.4 Font Embedding

PPT 提出時にフォント埋め込みを ON にする:
- File > Options > Save > "Embed fonts in the file" にチェック
- "Embed only the characters used" を選ぶ (ファイル軽量化)

これがないと、相手の PC で Arial がない場合に **代替フォントに置換されて崩れる**。

### 12.5 PPT スライドサイズ

| 用途 | サイズ | 推奨 |
|---|---|---|
| Standard | 4:3 (10×7.5 inch) | 古いプロジェクタ用 |
| Widescreen | 16:9 (13.33×7.5 inch) | 現代の主流 |
| 16:10 | (10×6.25 inch) | 印刷向け、A4 比率に近い |
| Custom (A4 横) | 11.69×8.27 inch | 印刷を前提とする pitchbook |

**IB 標準**: 16:9 widescreen が現代の主流、ただし **印刷前提** の本格 pitchbook は A4 横にカスタムする。

### 12.6 PPT 内の Bank-Branded Master Slide

- **Master slide** に bank ロゴ、footer band、page number、CONFIDENTIAL stamp を仕込む
- 各 slide は master を継承するだけ → 統一感が出る
- 個別 slide で余計な装飾を加えない


## 13. 印刷物 vs スクリーン表示

IB 資料は今でも **「印刷で配布される」** ことが多い (会議室、CFO への手渡し、データルーム保管)。スクリーン表示と印刷の両対応が必須。

### 13.1 ページネーション

| 観点 | スクリーン | 印刷 |
|---|---|---|
| 解像度 | 96-144 dpi | 600 dpi 推奨 |
| Background | 白 / 薄背景 OK | 純白推奨 (インク節約) |
| 罫線 | 細くても OK | やや太め (1-1.5px が安全) |
| 文字サイズ | 10pt 標準 | 10pt が下限、9pt は注意 |
| 色 | RGB | CMYK 変換時の発色を確認 |
| 改ページ | スクロールで連続 | 明示的な page break が必要 |

> **原則 13.1**: 印刷を前提にすると、自動的にスクリーンでも見やすくなる。逆は成立しない。

### 13.2 印刷時のヘッダ・フッタ繰り返し

- xlsx の "Print Titles" 機能で、**先頭行 (列ヘッダ) を全ページで繰り返し印刷** する。
- File > Page Setup > Sheet > "Rows to repeat at top": `$1:$5` (列ヘッダ部分)
- これがないと、2 ページ目以降「数字だけが並んで何の数字か分からない」状態になる。

### 13.3 大型モデルの印刷分割

3-statement のような横長モデルは、**ページ分割線 (page break)** を意図的に置く。

| 分割位置 | 推奨 |
|---|---|
| 列方向 (年) | 5 年単位 (例: 24A-28E と 29E-33E で 2 ページ) |
| 行方向 (科目) | section break (P&L / BS / CF) で改ページ |
| Force page break | View > Page Break Preview で青破線をドラッグ |

### 13.4 PDF 化

最終的に **PDF で配布** することが多い。

| 設定 | 推奨 |
|---|---|
| Output | 600 dpi PDF |
| Color | RGB (画面表示) または CMYK (印刷所) |
| Font | Embed all fonts (subset 推奨) |
| Compression | 中程度 (画像は JPEG 80%) |
| Bookmarks | TOC からシートへ自動生成 |
| Password | 配布先によって設定 |

**xlsx → PDF**:
- File > Export > Create PDF/XPS Document
- "Standard (publishing online and printing)" を選ぶ (size より quality)
- "Document Properties" で Title / Author を設定

### 13.5 Multi-page Wide Model 用ハック

横が広いモデルを 1 ページに収めたい時:

| 方法 | コメント |
|---|---|
| Print scale 80-90% | 文字が小さくなる、9pt 以下にしないこと |
| Landscape (横向き) | 必須 |
| Hide unused columns | 印刷前にグルーピング (Group + Outline) |
| 11×17 (Tabloid) 紙 | 大きい紙、社内配布用 |
| A3 横 (国内) | A3 プリンタが必要 |


## 14. アクセシビリティ (Accessibility)

財務モデルは伝統的に accessibility 配慮が弱いが、現代では **WCAG 2.1 AA** 準拠を意識する。

### 14.1 WCAG 観点で見た IB style

| 基準 | IB style 評価 | 改善点 |
|---|---|---|
| 1.4.3 Contrast (Minimum) | △ Blue `#0000FF` on white = OK (4.5:1 以上)、Green `#008000` on white = ギリギリ | Green を `#006400` に濃くしても OK |
| 1.4.6 Contrast (Enhanced) | ✗ 一部 fail | gray `#666666` を `#595959` に濃くする |
| 1.4.1 Use of Color | ✗ 色だけで意味を伝えがち | 括弧 `(123)` で negative を表現 → 既に OK |
| 1.4.11 Non-text Contrast | △ 罫線が薄すぎることがある | subtotal 罫線は 1.5px |
| 2.4.6 Headings and Labels | ✓ section header / label は明示 | — |
| 1.3.1 Info and Relationships | △ table がプログラム的に認識されない場合あり | ARIA / Excel "Set as Table" 機能を使う |

### 14.2 カラーブラインド配慮

8% の男性、0.5% の女性に色覚多様性 (主に red/green の区別困難) がある。

| 配慮 | 対応 |
|---|---|
| Negative numbers を red で示さない | **括弧 `(123)`** で表現 → OK |
| Positive growth を green で示さない | **数字 + arrow ↑** で表現 |
| 緑/赤の cross-sheet と external link | **shape (●/■)** と組み合わせる、 もしくは凡例を必ず付ける |
| Heatmap (sensitivity) | red/blue の組合せは色覚異常者でも区別可 (red/green は不可) |
| Bar chart の系列色 | navy / gold / gray の **3 色組** が無難 (RG 軸の 2 色は避ける) |

> **原則 14.2**: 「色だけで伝わるな」を貫く。色の意味は **必ずテキストや位置やシンボルでも冗長表現** する。

### 14.3 Screen Reader (財務モデル特有)

財務モデルで screen reader 対応は現実的に難しいが、以下は最低限する:

- **シート名** に意味のある名前を付ける (`Sheet1` ではなく `2_Summary`)
- **A1 セル** にシートのタイトルを置く (screen reader はこれを最初に読む)
- **named range** を使う (`Revenue_FY24` のような名前は読み上げられる)
- Excel の "Alt text" を chart や image に設定する

### 14.4 高 DPI / 拡大表示

- 文字サイズが小さすぎると、4K モニタで縮小表示される
- 既定の Arial 10pt は 1080p で読める下限
- 印刷を 80% scale すると 8pt 相当 → これ以下にしない


## 15. Anti-Patterns (デザインの「やらかし」集)

これらは見ただけで「**素人モデル**」と判定される、典型的な NG パターン。

### 15.1 Typography 系 NG

| NG | なぜダメか | 正しい例 |
|---|---|---|
| Comic Sans を Excel header に | プロフェッショナル感ゼロ | Arial 10pt Bold |
| Papyrus, Curlz MT などディスプレイフォントを本文に | 読めない、笑われる | Arial 10pt |
| 全部 bold | 強調の意味がなくなる | subtotal/total のみ bold |
| 全部 italic | 読みにくい、装飾的 | year header / footnote のみ |
| 文字サイズが行ごとに違う | 「整っていない」感 | 階層内で統一 |
| 下線で「強調」 | リンクと誤認 | bold か罫線で表現 |

### 15.2 Color 系 NG

| NG | なぜダメか |
|---|---|
| 7 色レインボー (chart の自動色) | 意味の階層が壊れる、印刷で潰れる |
| 全テキスト色を変える | 機能色 (blue/green/red/black) の意味が崩壊 |
| 赤を「強調」目的で使う | "external link" と誤認、negative number と誤認 |
| 緑を「OK / 良い」目的で使う | "cross-sheet link" と誤認 |
| 青を「強調」目的で使う | "hard input" と誤認 |
| Neon 色 | 印刷で潰れる、軽薄に見える |
| グラデーション fill | 印刷で帯になる、プロ感ゼロ |
| Mustard yellow `#D9B441` 本文に | 目立ちすぎ、accent 専用 |

### 15.3 Layout 系 NG

| NG | なぜダメか |
|---|---|
| 全セルに罫線 (gridline mode) | 罫線疲れ、data に目が行かない |
| 中央揃えの数字 | 桁が揃わない、見にくい |
| 列幅がバラバラ | 不揃いで素人感 |
| Merged cells 多用 | フィルタや並べ替えで壊れる |
| 印刷範囲が未設定 | 提出時に変な切れ方 |
| Freeze panes なし (横長モデル) | スクロール後どこにいるか分からない |
| Hidden rows / columns 多用 | レビュアーが理解できない |
| 全角スペースで indentation | 検索性低下、フォント間で崩れる |

### 15.4 Visual Effect 系 NG

| NG | なぜダメか |
|---|---|
| 3D bar / 3D pie chart | 比例関係が歪む、Tufte 原則違反 |
| Drop shadow | 装飾的、印刷でノイズ |
| Texture (大理石、紙) | 90 年代テンプレ感 |
| Pattern fill (斜線、ドット) | モアレ、印刷で読めない |
| Smart Art の濫用 | テンプレ感、再利用不可 |
| Image を表に重ねる | レイヤーが壊れる、編集不可 |
| Animation (pptx 連携時) | バンカー資料で禁忌 |
| Transition effect | 同上 |

### 15.5 Information 系 NG

| NG | なぜダメか |
|---|---|
| Source 行なし | 「いつのデータ？」が分からない |
| Unit 表記なし | ¥B か ¥M か分からない |
| `n.a.` / `nm` の使い分けなし | データなしと「意味がない」が混同 |
| 空欄 (data なしのセルが空) | 「data がない」のか「data 取り忘れ」のか分からない |
| Rounded numbers の精度ばらつき | `1.5x` と `1.50x` が同シートに混在 |
| 西暦 / 和暦混在 | `2024年` と `令和6年` を混ぜる |
| Currency 混在 | `¥` と `$` を同シートに無断併用 |

### 15.6 Pitchbook 系 NG

| NG | なぜダメか |
|---|---|
| Cover に人物写真 | 軽い、IB の品位に合わない |
| Cover に立体ロゴ | 装飾的 |
| TOC のページ番号がリーダー (`....`) で繋がる | 古い、空白で十分 |
| Footer に bank 名のフルスペル毎ページ | 冗長、ロゴで OK |
| 1 スライドに 8+ 個のチャート | 読めない、密度過剰 |
| Pie chart 多用 | 角度判別困難、IB では避ける |
| 動的アニメーション | 「テンポラリ感」が出る |

### 15.7 Excel 特有の NG

| NG | なぜダメか |
|---|---|
| Hardcoded 数値が formula 列に混入 | audit 不可能 |
| `=A1+B1+C1` を `=SUM(A1:C1)` で書かない (またはその逆も) | 一貫性なし |
| Circular reference 警告を放置 | モデルが壊れている |
| Volatile function (`OFFSET`, `INDIRECT`) 多用 | 計算が遅い |
| Sheet 名にスペース | `=`Sheet 1`!A1` の引用符が必要 |
| Sheet 名が Sheet1, Sheet2 のまま | 意図が伝わらない |
| 数値をテキスト形式で保持 | SUM できない |
| `%` を文字列で書く | `"15%"` ではなく `0.15` で format `0%` |

### 15.8 「素人 vs プロ」を一目で判定するクイック診断

| 観察 | プロ判定 | 素人判定 |
|---|---|---|
| Hard input は青？ | ✓ | ✗ |
| Total に二重線？ | ✓ | ✗ |
| 数字は右揃え？ | ✓ | ✗ |
| Negative は括弧？ | ✓ | ✗ |
| Source line ある？ | ✓ | ✗ |
| Unit ある？ | ✓ | ✗ |
| フォント Arial 10pt？ | ✓ | ✗ (Calibri / Times / mix) |
| Chart は 3D / pie ？ | ✗ | ✓ |
| Gridline OFF (印刷)？ | ✓ | ✗ |
| Section break 罫線？ | ✓ | ✗ |

> **原則 15.8**: この 10 項目のうち 8 つ以上が「プロ判定」なら IB 品質の入口に立てる。


## 16. 成熟した IB Design 原則 40 か条

| # | 原則 | Rationale (なぜ) |
|---|---|---|
| 1 | 装飾より構造で目立たせる | 装飾はノイズ、構造は信号 |
| 2 | 色は機能のためだけに使う | 機能色は監査言語、装飾色は混乱の元 |
| 3 | Hard input は青 (`#0000FF`) | バンカーの世界共通言語 |
| 4 | Formula は黒 | デフォルト = 計算式のシグナル |
| 5 | Cross-sheet link は緑 (`#008000`) | 他シート参照を一瞥で識別 |
| 6 | External link は赤 (`#FF0000`) | 外部依存への警告 |
| 7 | Comment / footnote は灰 (`#666666`) italic | 主要情報と区別 |
| 8 | Body フォントは Arial 10pt | 業界標準、可搬性最強 |
| 9 | Year header は italic | "これは時間軸" のシグナル |
| 10 | Source line は italic gray 8pt | 出典を必ず付ける、本文と区別 |
| 11 | 数字は右揃え、ラベルは左揃え | 桁が揃う、読みやすい |
| 12 | Negative は括弧 `(123)` | 会計世界共通言語、色覚配慮 |
| 13 | Zero は `-` 表示 | 0 と「該当なし」を区別 |
| 14 | n.a. / nm を使い分ける | 「データなし」と「意味なし」を区別 |
| 15 | Subtotal は上罫線、Total は上 1 本 + 下二重 | 会計世界共通 |
| 16 | 全セル罫線は素人 | "Border fatigue" を起こす |
| 17 | Gridline は印刷時 OFF | 印刷で罫線が二重化する |
| 18 | 期間列は同 width | "整っている" のシグナル |
| 19 | ラベル列は 38-45 width | 標準項目が改行なく入る |
| 20 | Indentation で sub-line を表現 | 構造の階層化 |
| 21 | Section 間は空行 + 罫線 | "息継ぎ" を作る |
| 22 | 空行は 8pt 高 | 大きすぎず小さすぎず |
| 23 | Header / Footer は全シート統一 | プロジェクト一貫性 |
| 24 | Freeze panes (横長モデル) | 常にラベルが見える |
| 25 | Sheet 名にプレフィックス番号 | 並びを固定 |
| 26 | Chart に必ず data label | 印刷で正確な値を読む |
| 27 | Chart に必ず source line | 出典明記 |
| 28 | Pie chart 不使用、bar 推奨 | 角度判別困難 |
| 29 | 3D chart 禁止 | 比例関係が歪む |
| 30 | グラデーション禁止 | 印刷で帯になる、装飾的 |
| 31 | Drop shadow 禁止 | data-ink ratio を下げる |
| 32 | Italic は 5 用途のみ | year, footnote, n.a., placeholder, cross-ref |
| 33 | Bold は subtotal/total のみ | 強調インフレを防ぐ |
| 34 | Underline は使わない (link 例外) | リンク誤認 |
| 35 | Unit は header に書き、本体には書かない | 冗長を避ける |
| 36 | Currency / unit を混在させない | 1 シート 1 unit |
| 37 | 略語は dot なし (`Y/Y`, `LTM`, `NTM`) | 現代流 |
| 38 | Cover には 5 要素のみ | プロジェクト名, subtitle, date, 機密区分, bank entity |
| 39 | Exec summary は 1 ページ | EVP / CFO は 1 ページしか読まない |
| 40 | 「印刷で白黒で意味が伝わるか」を毎回テスト | 色だけに依存しない |


## 17. Design Audit チェックリスト

xlsx / pptx を出力する **直前** にこのチェックリストを通す。1 つでも fail があれば修正。

### 17.1 Quick Audit (60 秒で判定)

```
□ 1. xlsx 全体で gridline が OFF になっている (View > Gridlines)
□ 2. 全シートで Hard input が青、formula が黒、cross-sheet が緑
□ 3. Footer に Page X of Y が入っている
□ 4. Header に Project name + CONFIDENTIAL が入っている
□ 5. 最初の Cover page と Exec summary がある
□ 6. すべての table に source line がある
□ 7. すべての table に unit (¥M, $M など) がある
□ 8. すべての chart に data label がある
□ 9. Negative numbers が括弧 `(123)` 表示
□ 10. Zero が `-` 表示
```

### 17.2 Typography Audit

```
□ Body フォントが Arial 10pt
□ Section title が Arial 14pt Bold navy
□ Year header が Arial 10pt Bold Italic
□ Footnote が Arial 8pt Italic gray
□ Italic は year/footnote/n.a./placeholder/cross-ref のみ
□ Bold は subtotal/total/section title のみ
□ Underline はハイパーリンク以外なし
□ サイズが行ごとに不均一でない
```

### 17.3 Color Audit

```
□ Hard input: `#0000FF` (Blue)
□ Formula: `#000000` (Black)
□ Cross-sheet link: `#008000` (Green)
□ External link: `#FF0000` (Red)
□ Comment: `#666666` (Gray) italic
□ Body label: `#2D332E` (Ink)
□ Section header band: `#1F3A66` (Navy) — または brand color
□ Total row banding: `#F2F2F2` (Light gray)
□ ブランド色は header/footer/cover のみ、本文なし
□ 7 色以上の chart 色を使っていない
□ グラデーション fill を使っていない
□ Neon 色を使っていない
□ Mustard `#D9B441` を本文に使っていない
```

### 17.4 Layout Audit

```
□ Sheet 名にプレフィックス番号 (`1_Cover`, `2_Summary`...)
□ Sheet tab の色分けがされている
□ 列 A は左 margin (width 2.0)
□ ラベル列 (B) は width 38-45
□ 期間列が **同じ width** で揃っている
□ 行高が 15pt 標準、空行 8pt、section title 22pt
□ Sub-line は indent で 1 段下げ
□ Freeze panes が設定されている (横長モデル)
□ Print area が設定されている
□ Page orientation = Landscape
□ Margins = top/bottom/left/right 0.5 inch
□ Print scale = 100% or "Fit to 1 page wide"
```

### 17.5 Border Audit

```
□ Subtotal 行に上罫線 (1px solid black)
□ Grand total 行に上 1 本 + 下二重線
□ Section divider に thick navy 罫線
□ 全セル罫線になっていない
□ 列ヘッダ (年) の下に細罫線
□ 罫線色は黒 (装飾色は使わない)
```

### 17.6 Chart Audit

```
□ Chart title が上部 Arial 12pt Bold
□ Subtitle (unit) が title 下 Arial 9pt italic gray
□ Data label が **すべて** 付いている
□ Source line が chart 下に italic gray
□ Chart 枠 (border) が無い
□ Background fill が純白
□ Gridline が横方向のみ薄グレー、または無し
□ 3D effect が無い
□ Drop shadow が無い
□ グラデーション fill が無い
□ Pattern fill (斜線・ドット) が無い
□ Pie chart を使っていない
□ Football field chart の bar 色が統一
□ Sensitivity heatmap の center cell が太枠
□ Waterfall の +/- 色が統一 (positive = navy, negative = red)
```

### 17.7 Page Composition Audit

```
□ Cover page に 5 要素のみ (Project, Subtitle, Date, Confidentiality, Bank entity)
□ Cover に装飾画像なし、人物写真なし
□ Exec summary が 1 ページ完結
□ Section divider に章番号 + タイトルのみ
□ TOC のページ番号が右揃え (リーダーなし)
□ Tear sheet が 2 列レイアウト
□ Page number が footer 右下
□ ロゴが master slide で繰り返されている
```

### 17.8 Banker Style Cues Audit

```
□ 数字が右揃え、ラベルが左揃え
□ 千区切りカンマ
□ Negative が括弧
□ Zero が dash
□ n.a. / nm が使い分け
□ Source line が "Source: [src1], [src2] ([as-of date])." 形式
□ Unit が header に書かれ、本体に書かれていない
□ Year suffix (A/E/P/F/B) が italic
□ 略語に dot がない (`Y/Y`, `LTM`, `NTM`)
□ Currency が混在していない
```

### 17.9 Pitchbook Audit (pptx 連携時)

```
□ Linked paste の場合、xlsx と pptx が同フォルダ
□ Font embedding が ON
□ Master slide にロゴ・footer band・page number
□ 1 スライドあたりチャート 3 個以下
□ アニメーションなし
□ Transition なし
□ スライドサイズが 16:9 または A4 横
□ Print scale 設定 OK
```

### 17.10 Accessibility Audit

```
□ 色だけで意味が伝わるところがない (色 + 括弧 / shape / label の冗長)
□ Contrast ratio が 4.5:1 以上 (本文)
□ Alt text が chart / image に設定されている
□ Sheet 名と A1 cell に意味のあるタイトル
□ 拡大しても (Ctrl + scroll) 読める文字サイズ
```

### 17.11 印刷耐性 Audit

```
□ 印刷プレビューで意図通りの表示になる
□ 1 ページ幅に収まっている (横切れなし)
□ Print Titles で列ヘッダが全ページ繰り返し
□ Page break が論理的位置にある
□ 白黒印刷でも意味が伝わる
□ 罫線が薄すぎず、太すぎず
```

### 17.12 Final Sanity Check

```
□ クライアントの会社名のスペルが正しい
□ プロジェクトコード (Project Falcon など) が全シート統一
□ 日付が最新
□ "DRAFT" / working watermark を消した (final 提出時)
□ Hidden rows / columns / sheets を解除した (もしくは意図的に hidden)
□ 個人情報 (excel author) を削除 (File > Info > Inspect Document)
□ External links が解除されている (final 版)
□ ファイル名が standard format (`ProjectName_DocType_v#.#.xlsx`)
```

---

## 付録 A. 主要参照文献

- **Macabacus** (https://macabacus.com/) — Excel-add-in、IB 標準 formatting tool
- **Wall Street Prep** (https://www.wallstreetprep.com/) — IB トレーニングのデファクト
- **Training The Street** (https://trainingthestreet.com/) — 同上、buy-side 寄り
- **Edward Tufte**, *The Visual Display of Quantitative Information* (1983, 2001) — Data-ink ratio, chart-junk
- **Cleveland & McGill** (1984), "Graphical Perception" — bar > pie の科学的根拠
- **Bessemer Venture Partners** "Cloud-based reporting" — VC visual style
- **a16z** "Pitch deck library" — startup pitch visual style
- **CFA Institute** (Ethical guidance on financial reporting)
- 姉妹文書: `01a_modeling_standards.md`, `01b_integrity_and_anti_patterns.md`

## 付録 B. Implementation Constants (scripts/ib_format.py 用)

`scripts/ib_format.py` で参照する定数のサマリ:

```python
# Functional Color Palette
IB_HARD_INPUT = "0000FF"        # Blue
IB_FORMULA = "000000"           # Black
IB_LINK_INTRA = "008000"        # Green
IB_LINK_EXTERNAL = "FF0000"     # Red
IB_COMMENT = "666666"           # Gray
IB_INK = "2D332E"               # Body ink

# Brand Colors (default = navy)
BRAND_NAVY = "1F3A66"
BRAND_GS_NAVY = "7399C6"
BRAND_MS_BLUE = "015DAA"
BRAND_LAZARD_ORANGE = "FF6E00"
BRAND_EVERCORE_NAVY = "001F3F"

# Backgrounds
BG_WHITE = "FFFFFF"
BG_TOTAL_BAND = "F2F2F2"
BG_HEADER_BAND = "1F3A66"
BG_WORKING = "FFF9C4"

# Fonts
FONT_BODY = ("Arial", 10)
FONT_SECTION = ("Arial", 14, "bold")
FONT_SUBSECTION = ("Arial", 11, "bold")
FONT_YEAR_HEADER = ("Arial", 10, "bold", "italic")
FONT_FOOTNOTE = ("Arial", 8, "italic")
FONT_COVER_TITLE = ("Arial", 28, "bold")

# Number Formats
FMT_MONEY_M = '#,##0;(#,##0);"-"'
FMT_MONEY_B = '#,##0.0;(#,##0.0);"-"'
FMT_PERCENT = '0.0%;(0.0%);"-"'
FMT_MULTIPLE = '0.0"x";(0.0"x");"-"'
FMT_PER_SHARE = '#,##0.00;(#,##0.00);"-"'
FMT_DATE_SHORT = 'mmm-yy'

# Layout Constants
COL_MARGIN_WIDTH = 2.0
COL_LABEL_WIDTH = 40.0
COL_UNIT_WIDTH = 8.0
COL_PERIOD_WIDTH = 12.0
ROW_BODY_HEIGHT = 15.0
ROW_SPACER_HEIGHT = 8.0
ROW_SECTION_HEIGHT = 22.0

# Page Setup
PRINT_MARGIN_INCH = 0.5
PRINT_HEADER_INCH = 0.3
PRINT_ORIENTATION = "landscape"
```

---

*End of `00_design_guidelines.md` v1.0*

*このドキュメントは `01a_modeling_standards.md` (規範) と対をなす **ビジュアルデザイン正本** である。値の改定はここで議論し、ここで決定する。*



