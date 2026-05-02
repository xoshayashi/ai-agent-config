---
name: design_consistency_rules
description: モデル全体の単位表示 (円 / 千円 / 百万円 / 億円) と背景色 / 文字色の用途別 canonical rule。各 builder / sheet / line item で何を選ぶかを一意に決定する SSoT。`_terminology.md` の IB Color と `00_design_guidelines.md` の Act ブランドルールを統合し、Phase 6 補強として「いつ何を使うか」「いつ塗ってよく、いつ塗ってはいけないか」を canonical 化する。
type: reference
priority: P0
related: [_terminology, 00_design_guidelines, 17_chart_design, 01a_modeling_standards, 15_input_schema]
---

# Design Consistency Rules (単位表示 + 色付け 統一ルール SSoT)

> 本書は reference 群 (00-17 + `_terminology` / `_master_decision_tree`) 横断の **「いつ何を使うか」 を司る正本** である。`_terminology §1` は IB Color の **what** を、`00_design_guidelines` は **how (実装値)** を、本書は **when / where** を司る。3 者の役割を踏み外さないこと。
>
> 用語注: 本書では「Operating System / OS」を避け、「描画エンジン」「環境」「閲覧環境」と表現する (個人ルール)。時系列の数値データは原則として markdown table で表形式に揃える。

---

## このドキュメントの位置づけ

- **正本 (SSoT)**: モデル中の cell が「どの scale (円 / 千円 / 百万円 / 億円) で表示されるか」「どの background fill / font color で塗られるか」 の **判定ルール** は本書が canonical。`scripts/ib_format.py` の `apply_*` helper はこの判定の実装である。
- **Routing**: `_master_decision_tree.md` の各 entry でモデルを生成する判断が立った瞬間、まず `_terminology` で用語を確認、次に本書で scale / color を確定、最後に各 builder を呼ぶ。Phase 6 補強として `_terminology` と `_master_decision_tree` のあいだに位置する SSoT 層。
- **Self-review**: 本書を使ったあとは `_self_review_protocol.md` の design 関連 check (scale 混在禁止 / 余分 fill 検知 / IB Color Legend 違反 / 1 シート色使用上限) を必ず実行。
- **関連 reference**: `_terminology §1` (IB Functional Color) / `_terminology §3` (Sheet 順) / `00_design_guidelines §3, §4, §6` (色彩 / Typography / Chart) / `01a_modeling_standards §4` (number_format) / `15_input_schema` (assumptions / driver schema) / `17_chart_design §2` (Chart Palette)。
- **違反検知**: 本書のルール違反は `sanity_checks.py` の D check に対応 (D5 余分 fill / D7 sensitivity 不統一 / D11 IB Color Legend / 新 D 候補 = scale 混在)。

---

## 目次

1. [単位表示ルール (Unit Display Rule)](#1-単位表示ルール-unit-display-rule)
   - 1.1 [基本原則](#11-基本原則)
   - 1.2 [Scale 階層 canonical](#12-scale-階層-canonical)
   - 1.3 [Decision Rule (ARR / 売上規模 → scale)](#13-decision-rule-arr--売上規模--scale)
   - 1.4 [シート別 default scale](#14-シート別-default-scale)
   - 1.5 [単位ラベル表示規約](#15-単位ラベル表示規約)
   - 1.6 [ARR-scale 自動判定 helper](#16-arr-scale-自動判定-helper)
   - 1.7 [USD / 多通貨対応](#17-usd--多通貨対応)
   - 1.8 [number_format トークン canonical 表](#18-number_format-トークン-canonical-表)
   - 1.9 [scale 切り替え時のリスクと回避](#19-scale-切り替え時のリスクと回避)
2. [色付けルール (Color Application Rule)](#2-色付けルール-color-application-rule)
   - 2.1 [基本原則](#21-基本原則)
   - 2.2 [Font Color Rule (IB Color Legend 拡張)](#22-font-color-rule-ib-color-legend-拡張)
   - 2.3 [Background Fill Rule (canonical)](#23-background-fill-rule-canonical)
   - 2.4 [塗っていい場所 / 塗ってはいけない場所](#24-塗っていい場所--塗ってはいけない場所)
   - 2.5 [1 シート上の色使用上限ルール](#25-1-シート上の色使用上限ルール)
   - 2.6 [ダークモード / B&W 印刷耐性](#26-ダークモード--bw-印刷耐性)
   - 2.7 [WCAG AA コントラスト検証](#27-wcag-aa-コントラスト検証)
   - 2.8 [色覚多様性配慮](#28-色覚多様性配慮)
3. [統合: ib_format.py での実装ガイダンス](#3-統合-ib_formatpy-での実装ガイダンス)
   - 3.1 [既存 helper との整合](#31-既存-helper-との整合)
   - 3.2 [number_format との整合](#32-number_format-との整合)
   - 3.3 [Sentinel 命名規則](#33-sentinel-命名規則)
   - 3.4 [helper の signature リファレンス](#34-helper-の-signature-リファレンス)
4. [Mini case (5 例)](#4-mini-case-5-例)
4.5 [Anti-patterns (やってはいけない例)](#45-anti-patterns-やってはいけない例)
4.6 [Decision FAQ (よくある判断疑問)](#46-decision-faq-よくある判断疑問)
5. [関連 reference との整合](#5-関連-reference-との整合)
6. [違反検知 (sanity_checks.py との連携)](#6-違反検知-sanity_checkspy-との連携)

---

## 1. 単位表示ルール (Unit Display Rule)

### 1.1 基本原則

本節の 5 原則は、Phase 6 までに頻発した **「scale 混在による monetary value 不整合」** を構造的に排除するための canonical ルール。

**原則 1 — cell value は必ず通貨単位の生数値**

Excel cell の **raw value (数式バー上の値)** は、常に **通貨の最小単位 (JPY なら 円、USD なら ドル)** で保存する。千円・百万円・億円表示は、あくまで `number_format` 文字列の `,###,` 等の桁省略表現で **見せ方** を変えているにすぎない。

```
正: cell.value = 1_234_567_890       # 12.3 億円を「円」で保存
    cell.number_format = FMT_JPY_MILLION   # 表示は「¥1,235」(百万円単位、四捨五入)

誤: cell.value = 1_234.57            # 「百万円単位」で raw 値を保存 (NG)
    cell.number_format = FMT_JPY_MILLION
```

**理由**: 千円表示シートと百万円表示シートを **同じワークブック内で混在** させても、cross-sheet 参照 (例: `=02_Revenue!C5`) で計算が壊れない。raw 値が常に「円」なら、参照側で勝手に scale 変換する必要がない。

**原則 2 — scale 選定は ARR / 売上規模で決定**

scale は審美ではなく数値規模で決まる。原則 §1.3 (Decision Rule) に従う。「読みやすそうだから百万円にしよう」 のような恣意的判断は禁止。

**原則 3 — mixed scale 禁止 (シート単位)**

1 シート内で「Cell A は千円、Cell B は百万円」 は不可。シート単位で scale を統一する。例外は §1.4 の `mixed` と明示されたシート (例: `08_CapTable` で shares = 整数 / value = 百万円 / PPS = 円)。

**原則 4 — 単位ラベルは必ず明示 (B2 セル)**

各シートの **B2 (top-right area)** に「(単位: 百万円)」を必ず明示する。`apply_unit_label(cell, currency, scale)` helper で挿入。閲覧者が「この数字は何単位か」 を 0.5 秒で判別できることを担保する。

**原則 5 — 有効桁数 (significant figures) は scale 選定に従属**

scale が大きくなるほど (千円 → 百万円 → 億円)、丸め幅も大きくなる。意思決定上の有効桁数 3 桁 (例: ¥1,235M = ¥1.235B、誤差 0.1% 以下) を維持できる scale を選ぶ。意思決定の解像度より細かい scale (Pre-IPO で円単位) は禁止、粗い scale (Pre-Seed で億円単位) も禁止。

### 1.2 Scale 階層 canonical

| Scale name | number_format key | 表示例 (raw = 1,234,567,890) | 主用途 | 丸め幅 |
|---|---|---|---|---|
| **actual (円)** | `FMT_JPY_YEN` | `¥1,234,567,890` | Per-share metrics、株式数小計、税額計算等 | ¥1 |
| **thousand (千円)** | `FMT_JPY_THOUSAND` | `¥1,234,568` (千円単位) | Pre-Seed / Seed (ARR < ¥100M)、補助計算 | ¥1,000 |
| **million (百万円)** | `FMT_JPY_MILLION` | `¥1,235` (百万円単位) | Series A〜C (ARR ¥100M〜¥10B)、デフォルト | ¥1,000,000 |
| **hundred_million (億円)** | `FMT_JPY_HUNDRED_MILLION` | `¥12.35` (億円単位、近似) | Pre-IPO / Late stage (ARR > ¥10B) | ¥100,000,000 |

`FMT_JPY_*` トークンの実体 (Excel number_format 文字列) は §1.8 を参照。

**Scale name は内部 enum**:

```python
# scripts/ib_format.py での想定 enum
SCALE_ACTUAL          = "actual"            # ¥1
SCALE_THOUSAND        = "thousand"          # ¥1,000
SCALE_MILLION         = "million"           # ¥1,000,000
SCALE_HUNDRED_MILLION = "hundred_million"   # ¥100,000,000
```

**英語表記との対応**:

| 内部 enum | 日本語ラベル | 英語ラベル | Excel format hint |
|---|---|---|---|
| `actual` | 円 | ¥ | `¥#,##0;[Red](¥#,##0)` |
| `thousand` | 千円 | ¥K | `¥#,##0,;[Red](¥#,##0,)` (1 カンマで × 10⁻³) |
| `million` | 百万円 | ¥M | `¥#,##0,,;[Red](¥#,##0,,)` (2 カンマで × 10⁻⁶) |
| `hundred_million` | 億円 | ¥B (近似) | `¥#,##0.00,,,;[Red](¥#,##0.00,,,)` 等 + 100 倍補正 |

> 億円 scale は Excel 標準 number_format でそのまま `,,,` (3 カンマ = 10⁻⁹) を使うと「兆円」 になってしまう。**億円 (10⁸) は Excel の自然な単位ではない** ため、`#,##0.00,,` (10⁶ 単位) に **× 0.01** の値変換を併用するか、`scripts/ib_format.py` で「raw 値 / 10⁸」の formula 列を別に持たせるかの 2 択。後者を推奨 (cell value は raw 円のまま、隣接列に「億円換算」 列を作る) が、scale 切り替えで simple display を優先するなら前者も許容。詳細は §1.8。

### 1.3 Decision Rule (ARR / 売上規模 → scale)

```
if ARR < ¥10M:                  scale = "thousand"           # 万円スケール、千円で表記
elif ARR < ¥100M:               scale = "thousand"           # 千円スケール
elif ARR < ¥10B:                scale = "million"            # 百万円スケール (default)
elif ARR < ¥100B:               scale = "hundred_million"    # 億円スケール
else:                           scale = "hundred_million"    # 兆円は別途検討 (現状 hundred_million で押し通す)
```

ARR (年間経常収益、`_terminology §6.1` の canonical 定義) 規模で `scale` を一意に決定する。境界値は 1 桁刻みで覚えやすく設計してある。

**カテゴリ別 override** (cell 単位で scale を上書きするべきカテゴリ):

| カテゴリ | scale override | 理由 |
|---|---|---|
| Cap Table (株式数) | `FMT_INTEGER` | 株式数は整数。1,000 万株以上は千株表記 (`#,##0,`) や `M shares` 表記検討 |
| Per-share metrics (PPS / Liquidation Pref / 行使価格) | `FMT_JPY_YEN` | 円単位 raw、scale 不変 (1 円 = 意思決定上の最小単位) |
| Comps / Multiples (EV/Revenue 等) | `FMT_MULTIPLE_1X` / `FMT_MULTIPLE_2X` | 倍数は scale 無関係 (例: `12.3x`) |
| Ratios (NRR, GM%, Churn) | `FMT_PCT_0` / `FMT_PCT_1` / `FMT_PCT_2` | パーセント、scale 無関係 |
| WC days (DSO / DPO / DIO) | `FMT_INTEGER` | 整数 days |
| Headcount (人数) | `FMT_INTEGER` | 整数人 |
| Date / Period (年月日) | `FMT_DATE_YYYYMMDD` | 日付、scale 無関係 |
| Sanity check raw value | `FMT_JPY_YEN` or `FMT_SCIENTIFIC` | check は raw で表示、scale 違反検知のため |

**境界値の rationale**:

- `¥10M` (1 千万円): 個人事業主から法人移行する規模、Pre-Seed の年商目安。ここまでは千円単位が読みやすい (例: ARR ¥8M = 「¥8,000 千円」)。
- `¥100M` (1 億円): Series A の入口目安 (`_terminology §6.2`: $1-3M ≈ ¥150-450M)。ここを越えると千円単位は桁が冗長になる (¥150,000 千円より ¥150 百万円の方が読みやすい)。
- `¥10B` (100 億円): Pre-IPO への入口目安。百万円単位だと 5 桁 (例: ¥10,000)、億円単位だと 3 桁 (¥100) に収まる。
- `¥100B` (1,000 億円): Late stage / Mega round の規模。億円単位でも 4 桁 (¥1,000) に収まる。

### 1.4 シート別 default scale (14-sheet layout)

| Sheet | Default scale | 理由 / 補足 |
|---|---|---|
| `00_Cover` | `million` | 全モデル概要。規模に合わせ override 可。Cover の hero metric 1 つだけ `actual` で円桁まで見せるのは許容 |
| `01_Assumptions` | `mixed` | hard input 主体。rate→`%`、count→`integer`、price→`actual`、amount→`million`。Pre-Seed では amount を `thousand` に縮小 |
| `02_Revenue` | `million` | 売上額。3 期以下のスタートアップで ARR < ¥100M なら `thousand` |
| `03_OpEx` | `million` | 費用。給与は `thousand` でも可だが mixed 禁止のため統一 |
| `04_IS` | `million` | 損益。trace 比較で BS / CFS と scale 揃える |
| `05_BS` | `mixed` | BS 主体は `million`、Working Capital Schedule sub-section (rows 56-69) は `mixed` (amount→`million`、days→`integer` で DSO/DPO/DIO) |
| `06_CFS` | `million` | CF |
| `07_Debt` | `million` | 借入残高、利息、principal |
| `08_CapTable` | `mixed` | shares→`integer`、value→`million`、PPS→`actual` (円単位)、percentage→`%` |
| `09_DCF` | `million` | EV / Equity Value、FCF projection。末尾 Sensitivity & Stress sub-section の EV grid も同 scale で揃える |
| `10_Comps` | `mixed` | multiple→`multiple_1x` / `multiple_2x`、value→`million`、ratio→`%` |
| `11_KPI_Dashboard` | `mixed` | rate→`%`、value→`million` (or 規模に応じ scale)、count→`integer`。旧 `02_Drivers` の driver display も本 sheet に統合 |
| `12_SanityChecks` | `actual` or `scientific` | check 値は raw で表示。scale 違反を検知するため敢えて生数値を出す |
| `13_IC_Memo` | `million` (text 主体) | 文章中の数値は本文 inline で `¥1.5B` 等の表記を許容 (近似) |

`mixed` シートは「同じシート内で複数の number_format を許容するが、各 cell カテゴリが §1.3 のカテゴリ別 override に従う」 という意味。任意の cell が任意の scale を取れる、という意味ではない (= mixed scale 禁止原則 §1.1 とは別)。

### 1.5 単位ラベル表示規約

各シートの **B2 セル (top-right area、または title row 直下の左肩)** に「(単位: 百万円)」を必ず明示する。`apply_unit_label(cell, currency="JPY", scale="million")` helper で挿入する。

**format**:

| ロケール | actual | thousand | million | hundred_million |
|---|---|---|---|---|
| 日本語 | `(単位: 円)` | `(単位: 千円)` | `(単位: 百万円)` | `(単位: 億円)` |
| 英語 | `(Unit: ¥)` | `(Unit: ¥K)` | `(Unit: ¥M)` | `(Unit: ¥B)` |
| バイリンガル | `(単位: 百万円 / Unit: ¥M)` | (同上) | (同上) | (同上) |

**配置**:

- B2 セル固定 (B 列 = 第 2 列、左に空白 1 列ある状態)。これは IB pitchbook 慣習 (ヘッダ行 1 = タイトル、ヘッダ行 2 = サブタイトル / 単位ラベル) に揃える。
- font: `Geist Sans 9pt` (英語) または `Noto Sans JP 9pt` (日本語)、color = `IB_COMMENT` (#666666)、italic 推奨。
- mixed シートでは「(単位: 百万円、shares は株、ratio は %)」 と複合表記を許容するか、個別カテゴリの header 行に inline で「(株)」「(%)」を出す。後者を推奨。

**B&W 印刷耐性**: 単位ラベルは色だけでなく **テキストそのものが識別子** であるため、greyscale 印刷でも問題なし。

### 1.6 ARR-scale 自動判定 helper

`scripts/ib_format.py` に以下の helper を追加することを推奨:

```python
def auto_scale_for_arr(arr_money: float, currency: str = "JPY") -> str:
    """ARR 額から推奨 scale を自動判定.

    Args:
        arr_money: ARR の raw 値 (currency の最小単位、JPY なら 円)
        currency: 通貨コード ("JPY" / "USD" / "EUR" 等)

    Returns:
        scale enum: "actual" / "thousand" / "million" / "hundred_million"

    Example:
        >>> auto_scale_for_arr(80_000_000_000)  # ¥80B
        'hundred_million'
        >>> auto_scale_for_arr(800_000_000)     # ¥800M
        'million'
        >>> auto_scale_for_arr(30_000_000)      # ¥30M
        'thousand'
    """
    if currency != "JPY":
        # USD / EUR は million default、後続で USD 専用 thresholds に拡張可
        return "million"
    if arr_money < 100_000_000:        # < ¥100M
        return "thousand"
    elif arr_money < 10_000_000_000:   # < ¥10B
        return "million"
    else:                              # ≥ ¥10B
        return "hundred_million"
```

**呼び出しタイミング**:

- 各 builder (`three_statement_builder.py`, `cap_table_builder.py`, `valuation_builder.py`) の **build 開始時 1 回だけ** 呼ぶ。返値の `scale` を build 中ずっと使う。途中で scale を変えない。
- 例外: `08_CapTable` の `mixed` シートでは shares / PPS だけは override する (§1.4)。

**自動判定の境界例外**:

- ARR が判定境界値ピッタリ (例: ¥99,999,999 = ¥100M-1) のときは、`auto_scale_for_arr` は厳密に `<` で判定するため `thousand` を返す。これは意図的 (1 円少なくても境界以下は小規模 stage 扱い)。境界の振動を避けたいユーザーは、`auto_scale_for_arr` を呼ばずに明示指定する。
- ARR が 0 や負値のとき (early-stage で revenue 未計上)、`thousand` を返す (最小 scale)。これは defensive default。

### 1.7 USD / 多通貨対応

JPY 以外の通貨での scale ルールも下記の通り canonical 化する。

| 通貨 | actual | thousand | million | billion |
|---|---|---|---|---|
| USD | $ (1 ドル) | $K (1 千ドル) | $M (1 百万ドル) | $B (1 十億ドル) |
| EUR | € | €K | €M | €B |
| JPY | ¥ | ¥K (千円) | ¥M (百万円) | ¥B (10 億円ではなく 1 億円) ※ |

※ JPY の 「¥B」 表記は曖昧 (10 億円なのか 1 億円なのか)。本書では **「¥B = 億円 (10⁸)」 を canonical** とする。USD の B (10⁹) と桁が違うため、混乱を避ける必要があれば常に「億円」「百万円」 を日本語表記する。

**USD ARR 規模の境界 (参考)**:

```
if USD ARR < $1M:        scale = "thousand"        # $K
elif USD ARR < $1B:      scale = "million"          # $M
else:                    scale = "billion"          # $B (10⁹)
```

USD では JPY と違い「億」相当の単位 (10⁸) がない (10⁹ = billion が次)。境界も $1M / $1B のシンプルな 3 桁刻み。

### 1.8 number_format トークン canonical 表

`scripts/ib_format.py` で定義される format 文字列の **canonical 表**。00_design_guidelines §4.2 (Number Format) と整合。

| Token name | 用途 | Excel format 文字列 (positive; negative; zero;text) | 表示例 (raw = 1234567890) |
|---|---|---|---|
| `FMT_JPY_YEN` | 円単位 | `¥#,##0;[Red](¥#,##0);"-";@` | `¥1,234,567,890` |
| `FMT_JPY_THOUSAND` | 千円単位 | `¥#,##0,;[Red](¥#,##0,);"-";@` | `¥1,234,568` |
| `FMT_JPY_MILLION` | 百万円単位 | `¥#,##0,,;[Red](¥#,##0,,);"-";@` | `¥1,235` |
| `FMT_JPY_HUNDRED_MILLION` | 億円単位 (近似 2 桁) | `¥#,##0.00,,;[Red](¥#,##0.00,,);"-";@` (raw × 0.01 必要) | `¥12.35` (要 raw 補正) |
| `FMT_USD_DOLLAR` | ドル単位 | `$#,##0;[Red]($#,##0);"-";@` | `$1,234,567,890` |
| `FMT_USD_THOUSAND` | 千ドル単位 | `$#,##0,;[Red]($#,##0,);"-";@` | `$1,234,568` |
| `FMT_USD_MILLION` | 百万ドル単位 | `$#,##0,,;[Red]($#,##0,,);"-";@` | `$1,235` |
| `FMT_USD_BILLION` | 十億ドル単位 | `$#,##0.00,,,;[Red]($#,##0.00,,,);"-";@` | `$1.23` |
| `FMT_INTEGER` | 整数 | `#,##0;[Red](#,##0);"-";@` | `1,234,567,890` |
| `FMT_PCT_0` | パーセント (整数) | `0%;[Red](0%);"-";@` | (raw 0.123 → `12%`) |
| `FMT_PCT_1` | パーセント (1 桁) | `0.0%;[Red](0.0%);"-";@` | `12.3%` |
| `FMT_PCT_2` | パーセント (2 桁) | `0.00%;[Red](0.00%);"-";@` | `12.35%` |
| `FMT_MULTIPLE_1X` | 倍数 (1 桁) | `0.0"x";[Red](0.0"x");"-";@` | `12.3x` |
| `FMT_MULTIPLE_2X` | 倍数 (2 桁) | `0.00"x";[Red](0.00"x");"-";@` | `12.35x` |
| `FMT_DATE_YYYYMMDD` | 日付 | `yyyy-mm-dd;@` | `2026-05-02` |
| `FMT_SCIENTIFIC` | 科学表記 (sanity check 用) | `0.00E+00;[Red](0.00E+00);"-";@` | `1.23E+09` |

**Excel カンマ表記の解読**:

- Excel の `#,##0` の末尾カンマは **× 1,000⁻¹ の桁省略** を意味する。
  - `#,##0` (カンマなし末尾) → そのまま (1 倍)
  - `#,##0,` (カンマ 1 つ末尾) → / 1,000 (千単位)
  - `#,##0,,` (カンマ 2 つ末尾) → / 1,000,000 (百万単位)
  - `#,##0,,,` (カンマ 3 つ末尾) → / 1,000,000,000 (十億単位)
- 億円 (10⁸) は Excel の自然な単位にないため、**raw 値 / 10⁸ → format 上は `0.00,,` (10⁶ 単位)** という 2 段階補正が必要。`apply_hard_input(cell, value=raw_yen, scale="hundred_million")` 内部で `cell.value = raw_yen / 100` (raw を百万円換算) + format `FMT_JPY_HUNDRED_MILLION` を組み合わせる、または `cell.value = raw_yen` のまま format に `0.00,,` (上記 raw を 10⁶ 単位で表示するが、それは「百万円」 になる) では **億円表示にならない** ことに注意。
- **推奨**: 億円表示を要するシート (Pre-IPO 規模) では、raw cell value を **「百万円単位」 で保存し、format を `0.00,,` (10⁶ 単位、つまり「億円」 ではなく「百万円」 になる)** ではなく、**raw cell value は「億円単位」 で保存し、format `0.00` (そのまま小数 2 桁)** を使う簡素化を許容。これは原則 §1.1 (cell value は raw 円) を **億円 scale でのみ例外的に破る** が、IB 慣習でも億円・billion 表記の cell は raw 値も billion 単位で保存する慣習がある (例: pitchbook の football field chart)。
- **代替案**: cell value は常に raw 円のまま、隣接列に `=A5/100000000` の formula 列を作り、その列に `0.00 "億"` の format を当てる。display も計算もずれない。複雑性とのトレードオフで選択。

> どちらを選ぶかは builder の `scale` 引数で分岐する。`apply_hard_input(cell, value, scale="hundred_million")` の内部実装は **後者 (formula 列方式)** を default、前者は `scale="hundred_million_simple"` で opt-in 可能とする。

### 1.9 scale 切り替え時のリスクと回避

scale を build 開始時に決め、build 中ずっと使うのが原則 §1.6 だが、**stage が変わるモデル** (例: Pre-Seed → Series A の 5 年 projection) では年次で scale が変わる可能性がある。



**ケース 1: 単一モデル内で stage が変わる**

- Y1 (ARR ¥30M) は thousand、Y5 (ARR ¥1.5B) は million が「読みやすい」 が、シート単位で scale を統一する原則 §1.1 から、**1 シート 1 scale**。
- 解: Y5 終端 ARR で `auto_scale_for_arr` を呼び、`million` を採用。Y1 が `¥30` (百万円単位) と粗く見えても許容。
- **rationale**: 5 年プロジェクションは「Y5 で何を達成するか」 が意思決定の主目的。Y1 の精度は assumption sheet (1_Assumptions) で千円単位 hard input すれば足りる。display sheet (3_Revenue / 5_IS) は将来規模に揃える。

**ケース 2: 複数シナリオで scale が異なる**

- Base case (Y5 ARR ¥1.5B) は million、Bear case (Y5 ARR ¥80M) は thousand が望ましい。
- 解: scenario_picker で base case の Y5 ARR で scale を決め、全 scenario 同じ scale を使う。Bear case で「¥80」 (百万円単位、近似 ¥80M) と粗く見えても scenario 比較がしやすい。
- 例外: scenario sheet を物理的に分ける場合 (sheet 5a_IS_Base, 5b_IS_Bear) は各シート独立の scale を許容。ただし dashboard で並べる場合は scale 統一推奨。

**ケース 3: M&A / 連結で母体規模が大きく変わる**

- standalone (¥500M) と pro-forma 連結 (¥80B) で 100 倍以上違うとき。
- 解: standalone は million、pro-forma は hundred_million。**シートを分ける**。
- **NG**: 同じシートに standalone と pro-forma を並べて scale を片方に揃えると、片方がほぼ 0 か桁あふれする。

---

## 2. 色付けルール (Color Application Rule)

### 2.1 基本原則

色は **意思決定の補助** であり、装飾ではない。本節の 5 原則は Tufte の data-ink minimization (チャート junk 排除) と Macabacus の cell formatting 規範を統合した canonical ルール。

**原則 1 — 色は意味に紐付ける (semantic)**

装飾目的の色付けは禁止。「全体的に華やかにしたいから」「上司の好みだから」 は許容しない。色を使うときは必ず以下の意味を持つ:

- **Cell value type** (font color): hard input / formula / link / external / comment。`_terminology §1` (IB Functional Color)。
- **Row / Section role** (background fill): section header / subtotal / grand total / year header / callout。
- **Status** (background fill): pass / warn / fail / note / warning / critical / success。

**原則 2 — 1 セルに 1 色 (font + fill の組み合わせは canonical pair)**

font color と background fill の組み合わせは下表 (§2.5 末尾の pair table) に挙げる **canonical pair のみ** を使用。任意の組み合わせを禁止。

**原則 3 — 色覚多様性配慮**

色だけで意味を伝えない。テキスト・icon・border の併記必須。例:

- check pass/fail: 色 (緑 / 赤) だけでなく「PASS」「FAIL」 のテキストを併記
- 矢印で trend を示す場合: 色 (緑 = up / 赤 = down) だけでなく ↑ ↓ 記号
- 主要 callout: 色 (黄 = warning) だけでなく「注意」「Warning」 ラベル

**原則 4 — WCAG AA 準拠**

文字色 / 背景色のコントラスト比は **4.5:1 以上 (本文)**、**3:1 以上 (太字 18pt+)** を確保。検証は §2.7。

**原則 5 — 色を使うほど価値が下がる (data-ink minimization)**

1 シートに色を付ける数には上限がある (§2.5)。色を一面に塗ると、どこが重要か見分けがつかなくなる。Tufte の data-ink ratio: ink (色 / 線) の使用は data の解釈に貢献する分だけが許容される。

### 2.2 Font Color Rule (IB Color Legend 拡張)

`_terminology §1` の IB Functional Color を canonical として、本書では以下の拡張を加える。

| Cell value type | Font color | Hex | Tag | 補足 |
|---|---|---|---|---|
| Hard input (生数値) | Blue | `#0000FF` | `IB_HARD_INPUT` | ユーザー入力。bold 推奨 |
| Formula intra-sheet | Black | `#000000` | `IB_FORMULA` | デフォルト。シート内の式 |
| Cross-sheet link | Green | `#008000` | `IB_LINK_INTRA` | 同じ workbook 内のシート参照 |
| External link | Red | `#FF0000` | `IB_LINK_EXTERNAL` | 外部 file 参照 (非推奨、極力避ける) |
| Comment / footnote | Gray | `#666666` | `IB_COMMENT` | 注記、italic |
| Brand accent (hero number) | Brand deep | `#004F49` | `BRAND_PRIMARY_DEEP` | Cover hero / IC memo の最重要数値 |
| Disabled / deprecated | Light gray | `#999999` | `IB_DISABLED` | 旧バージョン残存 cell、参考表示 |
| Negative value | Red (format-driven) | (via `[Red]` in number_format) | (format) | 上記 negative format 文字列で自動制御 |

**Font color の優先順位** (1 つ選ぶ):

1. **Cell value type に基づく IB Color** (default、`#0000FF` / `#000000` / `#008000` / `#FF0000` / `#666666` のどれか)
2. **Brand accent** は **シート 1 つにつき 1〜2 か所限定** (Cover の hero metric、IC memo の最終 valuation 等)
3. **Disabled / deprecated** は monitoring のみ、本番モデルでは削除推奨

**font color が決まる decision tree**:

```
cell に値を入れた直後:
├── ハードコード (=,*,+,/ 等の数式記号なし) → IB_HARD_INPUT (#0000FF)
├── 数式 (= で始まり、シート参照なし) → IB_FORMULA (#000000)
├── 数式 (= で始まり、別シート参照あり) → IB_LINK_INTRA (#008000)
├── 数式 (= で始まり、外部 file 参照あり) → IB_LINK_EXTERNAL (#FF0000)
├── コメント / 注記 (テキスト主体) → IB_COMMENT (#666666)
└── Cover の hero metric → BRAND_PRIMARY_DEEP (#004F49) (1 シート 1〜2 か所)
```

### 2.3 Background Fill Rule (canonical)

新 canonical の background fill table。`00_design_guidelines §3` の Act ブランドカラーと、Macabacus 系の subtotal / grand total 慣習を統合。

| 用途 | Color name | Hex | Font color (推奨) | Usage |
|---|---|---|---|---|
| **Section header band** (太字 row) | `BG_SECTION_HEADER` | `#1F3A66` (Navy) | `#FFFFFF` (white) | 各 sheet の主要 section 区切り |
| **Year header row** | `BG_YEAR_HEADER` | `#E5E5E5` (light gray) | `#000000` | Y1, Y2... 列 header row |
| **Subtotal row** | `BG_SUBTOTAL` | `#F2F2F2` (very light gray) | `#000000` (bold) | gross profit, EBITDA 等 中間集計 |
| **Grand total row** | `BG_GRAND_TOTAL` | `#1F3A66` (Navy) | `#FFFFFF` (white、bold) | NI, Total Assets, Equity 等 最終 |
| **Sensitivity base case** | `BG_BASE_CASE` | `#FFF3CC` (light yellow) | `#000000` (bold) | sensitivity matrix の中央セル |
| **KPI hero card** | `BG_KPI_HERO` | `#ECE9E1` (Surface beige) | `#2D332E` (Ink) | dashboard の重要 KPI box |
| **Check pass** | `BG_CHECK_PASS` | `#DFF2DF` (light green) | `#1F5132` (deep green) | sanity check で PASS |
| **Check warn** | `BG_CHECK_WARN` | `#FFF3CC` (light yellow) | `#8B6914` (deep amber) | sanity check で WARN |
| **Check fail** | `BG_CHECK_FAIL` | `#FFD9D9` (light red) | `#8B1F1F` (deep red) | sanity check で FAIL |
| **Note callout** | `BG_NOTE` | `#E8F4F8` (light blue) | `#1F3A66` (Navy) | 注釈 box |
| **Warning callout** | `BG_WARNING` | `#FFF3CC` (light yellow) | `#8B6914` (deep amber) | 注意喚起 box |
| **Critical callout** | `BG_CRITICAL` | `#FFD9D9` (light red) | `#8B1F1F` (deep red) | 重大 issue box |
| **Success callout** | `BG_SUCCESS` | `#DFF2DF` (light green) | `#1F5132` (deep green) | 成功表示 |
| **Zebra stripe** (alternate row) | `BG_ZEBRA` | `#FAFAFA` (5% gray) | `#000000` | 大型 table の偶数行 (>10 行のみ) |
| **Empty / N/A** | (none) | white | `#000000` | 値なし cell は塗らない |
| **Input region marker** (任意) | `BG_INPUT_REGION` | `#FFFBE6` (very light yellow) | (font は IB_HARD_INPUT) | hard input 範囲を弱く可視化 (opt-in) |

**Hex の選定根拠**:

- `#1F3A66` (Navy) = Act ブランドの Navy。section header / grand total に使用、強い hierarchy を表す。
- `#E5E5E5` (light gray) = Year header row に使用、column 構造を示す軽い識別。
- `#F2F2F2` (very light gray) = Subtotal、grand total よりひとつ弱い hierarchy。
- `#FFF3CC` (light yellow) = Mustard (`#D9B441`) ではなく、Accent (`#ECC85A`) の sub-tint。注意 / sensitivity base case 共通。
- `#DFF2DF` / `#FFD9D9` / `#E8F4F8` = pass / fail / note の status トリオ。彩度を抑え、コントラスト 4.5:1 以上を確保。
- `#ECE9E1` (Surface beige) = Act の Surface 色。KPI hero card で「ブランドの呼吸」 を出す唯一の用途。

**font color と背景色の canonical pair**:

下表は §2.2 の font color と §2.3 の background fill の **許容組み合わせ** 表。これ以外の組み合わせは禁止。

| Background | Allowed font color |
|---|---|
| (none) | `IB_HARD_INPUT` / `IB_FORMULA` / `IB_LINK_INTRA` / `IB_LINK_EXTERNAL` / `IB_COMMENT` / `BRAND_PRIMARY_DEEP` |
| `BG_SECTION_HEADER` (Navy) | `#FFFFFF` (white、bold) のみ |
| `BG_YEAR_HEADER` (light gray) | `IB_FORMULA` (黒 bold) または `IB_COMMENT` (gray) |
| `BG_SUBTOTAL` (very light gray) | `IB_FORMULA` (黒 bold) |
| `BG_GRAND_TOTAL` (Navy) | `#FFFFFF` (white、bold) のみ |
| `BG_BASE_CASE` (light yellow) | `IB_FORMULA` (黒 bold) |
| `BG_KPI_HERO` (Surface beige) | `#2D332E` (Ink) または `BRAND_PRIMARY_DEEP` |
| `BG_CHECK_PASS` (light green) | `#1F5132` (deep green) |
| `BG_CHECK_WARN` (light yellow) | `#8B6914` (deep amber) |
| `BG_CHECK_FAIL` (light red) | `#8B1F1F` (deep red) |
| `BG_NOTE` (light blue) | `#1F3A66` (Navy) |
| `BG_WARNING` (light yellow) | `#8B6914` (deep amber) |
| `BG_CRITICAL` (light red) | `#8B1F1F` (deep red) |
| `BG_SUCCESS` (light green) | `#1F5132` (deep green) |
| `BG_ZEBRA` (5% gray) | `IB_FORMULA` のみ (zebra 上に hard input 等を置かない) |
| `BG_INPUT_REGION` (very light yellow) | `IB_HARD_INPUT` のみ |

### 2.4 塗っていい場所 / 塗ってはいけない場所

**塗っていい場所 (semantic 用途)**:

1. **Section header / Year header / Subtotal / Grand total**
   - 各シート構造を hierarchy で示す唯一の手段。data-ink ratio を維持する範囲で。
2. **Sensitivity matrix (heatmap conditional formatting)**
   - WACC × g grid 等。3-color scale (green→yellow→red) の conditional formatting で gradient 表示。
3. **KPI hero card**
   - Dashboard / Cover の最重要 KPI 1-3 個に限定 (§2.5)。
4. **Check status (pass/warn/fail)**
   - SanityChecks シート、または dashboard 内の compact check row。
5. **Callout box (note/warning/critical/success)**
   - 注釈 / 警告。1 シートに 0-3 個まで (§2.5)。
6. **Brand accent (hero number)**
   - Cover sheet、IC memo の hero metric。font color で `BRAND_PRIMARY_DEEP` を使う 1〜2 か所。
7. **Zebra stripe (大型 table のみ)**
   - 10 行以上の table で、cohort layer cake / 月次 ARR / 大型 schedule のみ。

**塗ってはいけない場所**:

1. **通常の data cell (calculated value)**
   - formula で計算される普通の数値 cell には背景色を付けない。font color は IB Color (黒 / 緑 / 赤) のみ。
2. **通常の label cell (line item name)**
   - 「Revenue」「OpEx」 等の row label。section header に該当しない普通の label には背景色を付けない。
3. **Empty cell**
   - 値なし cell は塗らない (white = 暗黙のデフォルト)。
4. **「装飾目的」の塗り**
   - 「全体的に華やかにしたいから」 全 cell 塗る、「上司の好みだから」 ピンクにする、等は禁止。
5. **F 列など data 範囲外への余分な塗り** (ユーザー feedback Finding 7)
   - data がある範囲 (例: B5:E20) を超えて F 列以降に塗りが残るのは余分。`apply_*` helper の bounds 引数で範囲を厳密に指定する。
6. **印刷範囲外への余分な塗り**
   - print area の外に塗りがあると、印刷時に余白に色が出ることがあり混乱の原因。
7. **行 / 列全体への塗り (full row / full column fill)**
   - 「行 5 全体を青く」 のような塗りは絶対禁止。範囲は `B5:E5` 等の bounded range で指定する。Excel ファイルサイズが膨れる原因にもなる。

### 2.5 1 シート上の色使用上限ルール

| Element | 上限 / 推奨数 (1 シートあたり) | 例外 |
|---|---|---|
| Section header band | 3-7 個 (シート規模に応じ) | 大型 schedule (cap table dilution waterfall 等) は 10 個まで許容 |
| Subtotal row | 各 section に 0-1 個 | 階層が深い場合 sub-subtotal を 1 段だけ追加可 (font weight で hierarchy 区別) |
| Grand total row | 1 シートに 1 個 | IS の NI、BS の Total Assets / Total Liab+Equity の 2 個並列は許容 (BS の場合) |
| Brand accent (BRAND_PRIMARY_DEEP) | 0-2 か所 | Cover / IC memo は 1-2、その他シートは 0 |
| Callout box | 0-3 個 | SanityChecks / IC memo は例外的に 5-8 個まで |
| Sensitivity matrix | 全 sheet で 1-3 個 | DCF + EV/Revenue + Football field の 3 種類が上限 |
| Zebra striping | 大型 table のみ (>10 行) | 短い table (5-9 行) では striping 不要 |
| KPI hero card | 1-3 個 | Cover / Dashboard のみ。他シートは 0 |

> 上限を超えるときは **「色が多すぎてどこが重要か分からない」** サインなので、シート分割を検討。

**rationale (data-ink minimization 適用)**:

- Tufte の data-ink ratio を spreadsheet に応用すると、「色を使うほど価値が下がる」 という非線形関係になる。1 つの色は 100% の注意を引くが、3 つの色は 33% ずつ、10 個の色はそれぞれ 10% 以下しか注意を引けない。
- IB pitchbook 標準は 1 ページあたり 3-5 色まで。spreadsheet は 1 シート = 1 ページ相当と考える。
- 例外は sensitivity matrix (gradient で連続値を表現) と zebra striping (構造識別、極めて弱い色)。これらは 「色」 というより 「visual structure」 として data-ink ratio を侵さない。

### 2.6 ダークモード / B&W 印刷耐性

**ダークモード (dark theme での閲覧環境)**:

- 各 background color は **dark theme でも判別可能** であることを前提に設計してある。Navy (#1F3A66) → 暗い背景でも青みで識別、light gray (#F2F2F2) → 暗い背景では灰色のまま (描画エンジンが auto invert しない場合)。
- 注意: Excel の Office 365 dark theme は cell fill 色を **そのまま** 表示する (反転しない)。Light theme で設計した color が dark theme で過度に暗く見える可能性。事前検証を推奨。
- 推奨: 重要 element (grand total, section header) は dark theme でもコントラストが十分高い色 (Navy + 白文字) を使う。light theme 専用の色 (very light gray 等) は装飾用途のみに留める。

**B&W 印刷耐性**:

- 各 background color は **greyscale 変換時に hierarchy が保たれる** ことを確認済:
  - `BG_SECTION_HEADER` (Navy #1F3A66) → 暗い灰 (約 30% gray)
  - `BG_GRAND_TOTAL` (Navy #1F3A66) → 暗い灰 (同上)
  - `BG_SUBTOTAL` (very light gray #F2F2F2) → 薄い灰 (約 95% gray)
  - `BG_YEAR_HEADER` (light gray #E5E5E5) → 薄い灰 (約 90% gray)
  - これらが識別できる contrast を確保。
- B&W 印刷時は **bold font / border** で hierarchy を補強:
  - Section header: bold + white-on-darkgray (greyscale 後)
  - Grand total: bold + double bottom border + dark fill
  - Subtotal: bold + single top border (細線) + light fill
- カラー印刷想定でも、コピー用紙で読まれる機会が多いため B&W 検証必須。

**Greyscale check 表**:

| Background | RGB greyscale 変換値 | 識別可能性 |
|---|---|---|
| `BG_SECTION_HEADER` (#1F3A66) | ~37 (暗い灰) | 高 (白文字でも視認性良) |
| `BG_GRAND_TOTAL` (#1F3A66) | ~37 (暗い灰) | 高 |
| `BG_YEAR_HEADER` (#E5E5E5) | ~229 (薄い灰) | 中 (border 併用推奨) |
| `BG_SUBTOTAL` (#F2F2F2) | ~242 (極薄灰) | 中 (bold font 必須) |
| `BG_BASE_CASE` (#FFF3CC) | ~239 (薄い灰、わずかに黄) | 低 (border 必須) |
| `BG_CHECK_PASS` (#DFF2DF) | ~233 (薄い灰、わずかに緑) | 低 (text "PASS" 必須) |
| `BG_CHECK_FAIL` (#FFD9D9) | ~227 (薄い灰、わずかに赤) | 低 (text "FAIL" 必須) |
| `BG_KPI_HERO` (#ECE9E1) | ~234 (薄い灰、わずかにベージュ) | 低 (border 必須) |

> 薄色系 (light yellow / light green / light red) は greyscale 変換で識別困難になる。**必ずテキスト併記 (PASS/FAIL/Warning 等)** で意味を補強。

### 2.7 WCAG AA コントラスト検証

WCAG AA 基準 (Web Content Accessibility Guidelines 2.1 Level AA) を spreadsheet にも適用:

- **本文 (regular text)**: コントラスト比 4.5:1 以上
- **太字 18pt 以上 (large bold text)**: コントラスト比 3:1 以上

各 canonical pair (§2.3 末尾の表) は事前に検証済:

| Background | Font color | コントラスト比 | 判定 |
|---|---|---|---|
| `BG_SECTION_HEADER` (#1F3A66) | `#FFFFFF` | 11.4:1 | AAA pass (large) / AA pass (regular) |
| `BG_GRAND_TOTAL` (#1F3A66) | `#FFFFFF` | 11.4:1 | AAA pass |
| `BG_YEAR_HEADER` (#E5E5E5) | `#000000` | 17.4:1 | AAA pass |
| `BG_SUBTOTAL` (#F2F2F2) | `#000000` | 18.5:1 | AAA pass |
| `BG_BASE_CASE` (#FFF3CC) | `#000000` | 18.0:1 | AAA pass |
| `BG_KPI_HERO` (#ECE9E1) | `#2D332E` (Ink) | 13.7:1 | AAA pass |
| `BG_CHECK_PASS` (#DFF2DF) | `#1F5132` (deep green) | 7.5:1 | AA pass |
| `BG_CHECK_WARN` (#FFF3CC) | `#8B6914` (deep amber) | 5.6:1 | AA pass |
| `BG_CHECK_FAIL` (#FFD9D9) | `#8B1F1F` (deep red) | 6.4:1 | AA pass |
| `BG_NOTE` (#E8F4F8) | `#1F3A66` (Navy) | 9.0:1 | AAA pass |

**検証 tool**: `scripts/ib_format.py` に `check_contrast(bg_hex, fg_hex) -> float` helper を追加し、CI で自動検証。

### 2.8 色覚多様性配慮

色覚多様性 (色弱 / 色盲) は人口の約 5-8% に存在。色だけで意味を伝えない設計を canonical 化する。

**redundant cue (色 + テキスト / icon の併記)**:

| 用途 | 色 | テキスト / icon |
|---|---|---|
| Check pass | green | "PASS" / ✔ |
| Check warn | yellow | "WARN" / ⚠ |
| Check fail | red | "FAIL" / ✘ |
| Trend up | green | ↑ |
| Trend down | red | ↓ |
| Sensitivity heatmap | gradient | base case に枠線 + "Base" ラベル |
| Negative value | red | カッコ表記 `(1,234)` ([Red] format で自動) |

**deuteranopia (赤緑色弱) 対応**:

赤と緑が区別困難な viewer に対しては、形・テキスト・border で補強:

- check pass/fail を「左側に縦帯 + テキスト」 で表現 (横並びで色だけで判断させない)
- chart の series 区別は line style (solid / dashed / dotted) を併用

**tritanopia (青黄色弱) 対応**:

- BG_NOTE (light blue) と BG_WARNING (light yellow) が混同される可能性 → テキストラベル必須
- BG_BASE_CASE (light yellow) と BG_KPI_HERO (light beige) も混同しうる → border / position で区別

---

### 2.9 Sheet Tab Color Rule (canonical)

#### 2.9.1 Why role-based tab color

14 sheet の workbook で投資家・founder が **3 秒で navigation 把握** するための visual cue。各 sheet 個別 color 選択は visual chaos、role-based 6 色制限が IB best practice (Macabacus / Wall Street Prep)。

実装 helper: `ib_format.set_tab_color(ws)` (sheet name から role 自動判定)、`ib_format.apply_canonical_tab_colors(wb)` (全 sheet 一括適用)。

#### 2.9.2 Canonical 6 role × 14 sheet mapping

| Role | Color (Hex) | Sheets | Rationale |
|---|---|---|---|
| **Cover** | Navy `#1F3A66` | 00_Cover | Document title page (1 sheet 専用色) |
| **Input** | Brand deep `#004F49` | 01_Assumptions | User-editable hard inputs (編集対象 highlight) |
| **Driver** | Brand primary `#008A80` | 02_Revenue, 03_OpEx, 11_KPI_Dashboard | Calculated drivers / KPI / metrics (旧 02_Drivers の driver display は 11_KPI_Dashboard に吸収) |
| **Output** | Slate `#666666` | 04_IS, 05_BS, 06_CFS, 07_Debt, 08_CapTable, 09_DCF, 10_Comps | Calculated outputs (3-statement / valuation、neutral)。05_BS は Working Capital Schedule (旧 08_WC) を sub-section として吸収、09_DCF は Sensitivity & Stress (旧 13_Sensitivity) を sub-section として吸収 |
| **Check** | Warning `#D6913D` | 12_SanityChecks | Attention area / sanity status |
| **Memo** | Accent `#ECC85A` | 13_IC_Memo | IC thesis prose (最終 deliverable) |

正本 mapping は `scripts/ib_format.py` の `SHEET_ROLE_MAPPING` + `TAB_COLOR_BY_ROLE` 定数。本表と乖離した場合 ib_format.py が canonical (sanity_checks D10 が ib_format 経由で検証)。

#### 2.9.3 Edge cases

- **Optional sheet** (例: `17_MA_Exit_Analysis`、`20a-z` segment、`98_Logs` 等) は role assignment で延長。新規 sheet 追加時は SHEET_ROLE_MAPPING に entry 追加必須
- **Multi-segment** (`_named_ranges §2`) で各 segment sheet は **driver** role default、SOTP_Valuation は **output** role
- **業態 / stage 別 sheet** も role を pre-assign して visual chaos 回避
- **Glossary / Reference / Logs** 系の補助 sheet は role 未割当 (default 無色) で OK

#### 2.9.4 Anti-patterns

- 14 sheet で 14 色 → visual chaos、navigation cue 機能不全
- 全 sheet 無色 → navigation cue 不在、investor が迷子
- 突発的な「目立たせたい」色付け (e.g., red emphasis on 単一 sheet) → role canonical 違反、後続 review で混乱
- role を変更 (例: 09_DCF を output → driver に変更) → reference 改訂 + sanity_checks D10 update が同期必須

#### 2.9.5 sanity_checks D10 連携

`scripts/sanity_checks.py` の D10 (Tab color compliance) が **14 sheet 全体** を canonical mapping と比較:
- 一致: `pass`
- tabColor 未設定: `info` (sheet 存在するが role 不問の場合許容)
- 不一致: `soft_warn` + violation list (例: `"04_IS: expected 666666 (output), got 008A80"`)

> **連携**: ib_format.py の `SHEET_ROLE_MAPPING` を更新したら sanity_checks D10 が自動追従 (両者が同一 source 参照)。reference doc は **可視化目的の二次表現** で、code が canonical SSoT。

---

## 3. 統合: ib_format.py での実装ガイダンス

### 3.1 既存 helper との整合

既存 helper と本書 §2.3 の background color tag の対応:

| Helper | 内部で使う background tag | 用途 |
|---|---|---|
| `apply_year_header(cell, year_label)` | `BG_YEAR_HEADER` | Y1, Y2... 列 header |
| `apply_subtotal(cell, label, value)` | `BG_SUBTOTAL` | gross profit, EBITDA, etc. |
| `apply_grand_total(cell, label, value)` | `BG_GRAND_TOTAL` + bold + double bottom border | NI, Total Assets |
| `apply_section_header(cell, label)` | `BG_SECTION_HEADER` + white font + bold | "Revenue", "OpEx" 等 |
| `apply_alert(cell, kind, message)` | `BG_NOTE` / `BG_WARNING` / `BG_CRITICAL` / `BG_SUCCESS` | callout box |
| `apply_check_status(cell, status, value)` | `BG_CHECK_PASS` / `BG_CHECK_WARN` / `BG_CHECK_FAIL` | sanity check status |
| `apply_kpi_hero(cell, label, value)` | `BG_KPI_HERO` + Ink font + larger size | Cover / Dashboard |
| `apply_base_case_marker(cell)` | `BG_BASE_CASE` + bold border | sensitivity 中央 |
| `apply_zebra_stripe(range)` | `BG_ZEBRA` (alternate rows only) | 大型 table |
| `apply_input_region(range)` | `BG_INPUT_REGION` (opt-in) | hard input bound 可視化 |

**新規 helper として追加候補**:

```python
def apply_unit_label(cell, currency: str = "JPY", scale: str = "million", locale: str = "ja"):
    """B2 セルに「(単位: 百万円)」を挿入."""

def auto_scale_for_arr(arr_money: float, currency: str = "JPY") -> str:
    """ARR 額から推奨 scale を判定 (§1.6)."""

def fmt_for_currency(currency: str, scale: str) -> str:
    """通貨 + scale から number_format トークンを返す (§1.8)."""

def check_contrast(bg_hex: str, fg_hex: str) -> float:
    """WCAG コントラスト比を計算 (§2.7)."""

def apply_hard_input(cell, value, scale: str = "million", currency: str = "JPY"):
    """Hard input cell に IB_HARD_INPUT font + scale-aware format を適用."""
```

### 3.2 number_format との整合

`apply_hard_input(cell, value, fmt=fmt_for_currency(currency, scale))` のように **scale を auto inject** する pattern を canonical 化:

```python
# 推奨パターン
def build_three_statement(arr: float, currency: str = "JPY"):
    scale = auto_scale_for_arr(arr, currency)              # build 開始時 1 回
    fmt   = fmt_for_currency(currency, scale)
    label = f"(単位: {SCALE_LABEL_JA[scale]})"

    apply_unit_label(ws["B2"], currency=currency, scale=scale)
    apply_hard_input(ws["C5"], value=arr, scale=scale)
    apply_subtotal(ws["C20"], label="Gross Profit", value=...)
    # 以降、build 全体で scale / fmt を使い回す
```

**避けるべきパターン**:

```python
# 反パターン: 個別 cell で scale を変える
apply_hard_input(ws["C5"], value=arr, scale="thousand")          # Y1
apply_hard_input(ws["D5"], value=arr_y5, scale="million")        # Y5
# → 同じシートで scale が混在、原則 §1.1 違反
```

### 3.3 Sentinel 命名規則

`ib_format.py` で定義する sentinel (定数) の canonical 命名規則:

```python
# Scale enum
SCALE_ACTUAL          = "actual"
SCALE_THOUSAND        = "thousand"
SCALE_MILLION         = "million"
SCALE_HUNDRED_MILLION = "hundred_million"

# Currency enum
CURRENCY_JPY = "JPY"
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"

# Number format tokens (§1.8)
FMT_JPY_YEN              = "¥#,##0;[Red](¥#,##0);\"-\";@"
FMT_JPY_THOUSAND         = "¥#,##0,;[Red](¥#,##0,);\"-\";@"
FMT_JPY_MILLION          = "¥#,##0,,;[Red](¥#,##0,,);\"-\";@"
FMT_JPY_HUNDRED_MILLION  = "¥#,##0.00,,;[Red](¥#,##0.00,,);\"-\";@"
# (USD / EUR 同様)

# Background fill tags (§2.3)
BG_SECTION_HEADER  = "#1F3A66"
BG_YEAR_HEADER     = "#E5E5E5"
BG_SUBTOTAL        = "#F2F2F2"
BG_GRAND_TOTAL     = "#1F3A66"
BG_BASE_CASE       = "#FFF3CC"
BG_KPI_HERO        = "#ECE9E1"
BG_CHECK_PASS      = "#DFF2DF"
BG_CHECK_WARN      = "#FFF3CC"
BG_CHECK_FAIL      = "#FFD9D9"
BG_NOTE            = "#E8F4F8"
BG_WARNING         = "#FFF3CC"
BG_CRITICAL        = "#FFD9D9"
BG_SUCCESS         = "#DFF2DF"
BG_ZEBRA           = "#FAFAFA"
BG_INPUT_REGION    = "#FFFBE6"

# Font color tags (§2.2)
IB_HARD_INPUT          = "#0000FF"
IB_FORMULA             = "#000000"
IB_LINK_INTRA          = "#008000"
IB_LINK_EXTERNAL       = "#FF0000"
IB_COMMENT             = "#666666"
BRAND_PRIMARY_DEEP     = "#004F49"
IB_DISABLED            = "#999999"

# Allowed font colors per background (§2.3 末尾 pair table)
ALLOWED_PAIRS = {
    None: [IB_HARD_INPUT, IB_FORMULA, IB_LINK_INTRA, IB_LINK_EXTERNAL, IB_COMMENT, BRAND_PRIMARY_DEEP],
    BG_SECTION_HEADER: ["#FFFFFF"],
    BG_GRAND_TOTAL:    ["#FFFFFF"],
    BG_YEAR_HEADER:    [IB_FORMULA, IB_COMMENT],
    BG_SUBTOTAL:       [IB_FORMULA],
    BG_BASE_CASE:      [IB_FORMULA],
    BG_KPI_HERO:       ["#2D332E", BRAND_PRIMARY_DEEP],
    BG_CHECK_PASS:     ["#1F5132"],
    BG_CHECK_WARN:     ["#8B6914"],
    BG_CHECK_FAIL:     ["#8B1F1F"],
    BG_NOTE:           ["#1F3A66"],
    BG_WARNING:        ["#8B6914"],
    BG_CRITICAL:       ["#8B1F1F"],
    BG_SUCCESS:        ["#1F5132"],
    BG_ZEBRA:          [IB_FORMULA],
    BG_INPUT_REGION:   [IB_HARD_INPUT],
}
```

### 3.4 helper の signature リファレンス

主要 helper の canonical signature:

```python
def apply_hard_input(
    cell,
    value: Union[float, int],
    scale: str = "million",
    currency: str = "JPY",
    bold: bool = True,
) -> None:
    """Hard input cell に IB_HARD_INPUT font + scale-aware format を適用."""

def apply_section_header(
    cell,
    label: str,
    span: Optional[Tuple[str, str]] = None,
) -> None:
    """Section header band を適用 (BG_SECTION_HEADER + 白文字 bold).
    span が与えられた場合 merge cells も実施 ((B5, E5) 等)."""

def apply_subtotal(
    cell,
    label: str,
    formula: str,
    scale: str = "million",
    currency: str = "JPY",
) -> None:
    """Subtotal row (BG_SUBTOTAL + bold + 細い top border)."""

def apply_grand_total(
    cell,
    label: str,
    formula: str,
    scale: str = "million",
    currency: str = "JPY",
) -> None:
    """Grand total row (BG_GRAND_TOTAL + 白文字 bold + double bottom border)."""

def apply_alert(
    cell,
    kind: Literal["note", "warning", "critical", "success"],
    message: str,
) -> None:
    """Callout box を適用 (BG_NOTE / BG_WARNING / BG_CRITICAL / BG_SUCCESS)."""

def apply_check_status(
    cell,
    status: Literal["pass", "warn", "fail"],
    value: Union[float, int, str],
    label: str = "",
) -> None:
    """Sanity check status cell (BG_CHECK_* + テキスト併記)."""

def apply_unit_label(
    cell,
    currency: str = "JPY",
    scale: str = "million",
    locale: Literal["ja", "en", "bilingual"] = "ja",
) -> None:
    """B2 セル (or 指定 cell) に単位ラベルを挿入."""

def apply_kpi_hero(
    cell,
    label: str,
    value: Union[float, int],
    scale: str = "million",
    currency: str = "JPY",
) -> None:
    """KPI hero card (BG_KPI_HERO + Ink font + 大きめ size)."""

def apply_base_case_marker(cell) -> None:
    """Sensitivity matrix の base case cell (BG_BASE_CASE + 太枠)."""

def apply_zebra_stripe(
    ws,
    range_str: str,
    skip_rows: int = 1,
) -> None:
    """大型 table (>10 行) に zebra striping (BG_ZEBRA、偶数行)."""
```

---

## 4. Mini case (5 例)

### Case 1: Pre-Seed SaaS (ARR ¥30M)

- **Stage**: Pre-Seed、調達直後
- **ARR**: ¥30,000,000 (¥30M)
- **scale 判定**: `auto_scale_for_arr(30_000_000) = "thousand"`
- **単位ラベル**: `(単位: 千円)`
- **IS!C5 (Revenue)**:
  - cell value = `30_000_000` (raw 円)
  - number_format = `FMT_JPY_THOUSAND` = `¥#,##0,;[Red](¥#,##0,);"-";@`
  - display = `¥30,000` (千円単位、つまり「3 万千円 = ¥3,000 万円」 の表記)
- **section header**: `BG_SECTION_HEADER` (Navy) + 白文字 bold = "Revenue"
- **grand total (NI)**: `BG_GRAND_TOTAL` (Navy) + 白文字 bold + double bottom border
- **brand accent**: 0 (Cover sheet にのみ 1 か所)

### Case 2: Series A SaaS (ARR ¥800M)

- **Stage**: Series A、Y3
- **ARR**: ¥800,000,000 (¥800M)
- **scale 判定**: `auto_scale_for_arr(800_000_000) = "million"`
- **単位ラベル**: `(単位: 百万円)`
- **IS!C5 (Revenue)**:
  - cell value = `800_000_000` (raw 円)
  - number_format = `FMT_JPY_MILLION` = `¥#,##0,,;[Red](¥#,##0,,);"-";@`
  - display = `¥800` (百万円単位)
- **section header**: `BG_SECTION_HEADER` (Navy) + 白文字 bold = "Revenue", "OpEx", "EBITDA Bridge", "Below the Line", "Tax & NI" の 5 個
- **subtotal**: Gross Profit, EBITDA, Operating Income の 3 行 (`BG_SUBTOTAL` + bold)
- **grand total**: Net Income (`BG_GRAND_TOTAL` Navy + 白文字 bold + double bottom border)
- **callout**: 0 (IC memo シートで 2 個)
- **sensitivity matrix**: 09_DCF § Sensitivity に WACC × g grid 1 個

### Case 3: Pre-IPO SaaS (ARR ¥30B)

- **Stage**: Pre-IPO、上場準備中
- **ARR**: ¥30,000,000,000 (¥30B = 300 億円)
- **scale 判定**: `auto_scale_for_arr(30_000_000_000) = "hundred_million"`
- **単位ラベル**: `(単位: 億円)`
- **IS!C5 (Revenue)**:
  - cell value = `300` (raw 億円、§1.8 末尾の「億円表示は raw value も億円単位で保存」 の例外を適用)
  - number_format = `FMT_JPY_HUNDRED_MILLION` = `¥#,##0;[Red](¥#,##0);"-";@` (そのまま整数表示)
  - display = `¥300` (億円単位)
- **代替実装**: cell value = `30_000_000_000` (raw 円) を維持し、隣接列に `=A5/100000000` の formula 列を作る方法 (推奨だが複雑)
- **section header**: 5-7 個 (規模が大きいので section が増える、cap structure / convertible bonds / IPO scenario 等)
- **grand total**: 1 個 (NI)
- **brand accent**: Cover sheet の hero metric "EV ¥300B" を `BRAND_PRIMARY_DEEP` で表示
- **callout**: IC memo に 3 個 (key thesis、key risks、recommendation)

### Case 4: Cap Table (Founder 10M shares)

- **Sheet**: 08_CapTable (mixed scale)
- **株式数 cell** (Founder shares):
  - cell value = `10_000_000` (raw 株)
  - number_format = `FMT_INTEGER` = `#,##0;[Red](#,##0);"-";@`
  - display = `10,000,000` (10 million shares)
- **PPS (Price Per Share) cell** (Series A round price):
  - cell value = `87` (raw 円)
  - number_format = `FMT_JPY_YEN`
  - display = `¥87`
  - rationale: PPS は 1 円が意思決定の最小単位、scale 不変
- **Equity value cell** (founder の equity 評価額 = 10M × ¥87 = ¥870M):
  - cell value = `870_000_000` (raw 円)
  - number_format = `FMT_JPY_MILLION`
  - display = `¥870` (百万円単位)
- **Ownership %**:
  - cell value = `0.42` (raw 比率)
  - number_format = `FMT_PCT_1`
  - display = `42.0%`
- **section header**: "Founders", "Investors (Seed)", "Investors (Series A)", "ESOP", "Total" の 5 個
- **grand total**: "Total" 行 (`BG_GRAND_TOTAL` Navy)
- **mixed の判定**: 各 cell カテゴリ (shares / value / PPS / %) が §1.3 のカテゴリ別 override に従っているので原則 §1.1 違反ではない

### Case 5: Sensitivity matrix (WACC × g)

- **Sheet**: 09_DCF § Sensitivity
- **scale**: million (DCF と一致)
- **単位ラベル**: `(単位: 百万円)`
- **matrix 内 cell** (例: WACC=10%, g=3% → EV ¥1,500M):
  - cell value = `1_500_000_000` (raw 円)
  - number_format = `FMT_JPY_MILLION`
  - display = `¥1,500` (百万円単位)
- **base case (中央 cell)**:
  - 上記 cell + `BG_BASE_CASE` (light yellow) + bold border
  - rationale: base case は 「(WACC=10%, g=2.5%) → EV ¥1,500M」 の 1 か所のみ
- **heatmap conditional formatting**:
  - 3-color scale (green→yellow→red) で gradient
  - min: 紫っぽい色 (低 EV)、mid: 黄、max: 緑 (高 EV)
  - Excel 標準の conditional formatting 機能を使用
- **section header**: "WACC × g", "WACC × Exit multiple" の 2 個 (sensitivity が複数あれば)
- **grand total**: なし (sensitivity は終端値ではなく分布)
- **callout**: 0 (sensitivity 自体が「視覚的注意喚起」 なので追加 callout 不要)

---

## 4.5 Anti-patterns (やってはいけない例)

本書のルールに対する違反パターンを 12 件 canonical 化する。各パターンに対して **「症状」「なぜ NG か」「正しい対応」** を提示。

### AP-1: 千円単位 cell と百万円単位 cell が同じシートに混在

- **症状**: シート 5_IS の Y1 cell が `¥80,000` (千円単位)、Y5 cell が `¥1,500` (百万円単位)。
- **なぜ NG**: 閲覧者が「Y1 と Y5 のどちらが大きいか」 を即時判定できない。`SUM(C5:G5)` のような horizontal aggregation も意味を成さない (raw 値が円単位で同じだとしても、display 上は混乱)。さらに display 上 number_format が違うと cell-by-cell の差分も見えない。
- **正しい対応**: §1.4 の sheet 別 default scale に従い 1 シート 1 scale。ARR 規模に応じて `auto_scale_for_arr` で 1 つ選び、build 中ずっと使う。Y1 が「¥80」 (百万円単位) と粗く見えても許容。

### AP-2: number_format で `¥#,##0,,` を使うが cell value は百万円単位

- **症状**: cell.value = `1234` (千円単位だと 123 万円のつもり)、format = `FMT_JPY_MILLION` (`¥#,##0,,`)。display = `¥0` (1234 円 ÷ 10⁶ = 0.001234 → 切り捨て)。
- **なぜ NG**: cell value は **常に raw 通貨単位** で保存する原則 §1.1 違反。format は display 補正、value は raw。
- **正しい対応**: cell.value = `1_234_000_000` (raw 円、12.3 億円) + format = `FMT_JPY_MILLION` → display = `¥1,234`。

### AP-3: F 列以降の余分な fill

- **症状**: data 範囲 B5:E20 に塗りを当てたつもりが、`apply_section_header` の bounds 指定ミスで F 列まで青くなる。
- **なぜ NG**: 印刷時に余白に色が出る。Excel ファイルサイズが膨れる。閲覧者が「F 列に何かあるのか?」 と誤解する。
- **正しい対応**: helper には bounds 引数を必須とし、`apply_section_header(cell, label, span=("B5", "E5"))` のように **明示的に終端列を指定**。

### AP-4: 行全体への fill (full row fill)

- **症状**: row 5 全体 (A5:XFD5) を `BG_SECTION_HEADER` で塗る。
- **なぜ NG**: Excel ファイルサイズが急膨張する (数百 KB 増)。data 範囲外への塗り余裕も発生。印刷範囲外にも色が出る。
- **正しい対応**: data 範囲のみに塗る。`ws.merge_cells("B5:E5")` で merge するか、明示的に B5:E5 の範囲だけ塗る。

### AP-5: 装飾目的の fill (アクセント無関係)

- **症状**: 「全体的に華やかにしたいから」 全 cell に薄い色を付ける。「上司の好みだから」 ピンクや紫を多用。
- **なぜ NG**: 色が semantic 意味を持たなくなり、読者が hierarchy を判別不能。data-ink ratio が破綻。
- **正しい対応**: §2.4 「塗っていい場所」 のみに限定。装飾目的は禁止。

### AP-6: 1 シートに section header が 15 個以上

- **症状**: 細かく区切りすぎて、section header 行が画面の半分を埋める。
- **なぜ NG**: 「全部が重要」 = 「何も重要でない」。色を使うほど価値が下がる原則 §2.5 違反。
- **正しい対応**: 上限 7 個 (大型 schedule で 10 個まで)。シートを分割するか、section の階層を見直す。

### AP-7: hard input cell を黒で書く

- **症状**: ARR の hard input cell が黒文字 (`IB_FORMULA` 色)。
- **なぜ NG**: 監査者が「このセルは数式か入力か」 を判別不能。modeling standards (FAST, JM) 違反。`_terminology §1` の IB Color Legend canonical を破る。
- **正しい対応**: hard input は `IB_HARD_INPUT` (#0000FF、青)。`apply_hard_input` helper を使う。

### AP-8: 単位ラベルの欠落

- **症状**: シートに何の単位か書かれていない。ユーザーが「¥1,235 は千円か百万円か億円か」 を判別不能。
- **なぜ NG**: 閲覧者の最初の判定 (単位) ができない。意思決定の解像度が崩れる。
- **正しい対応**: B2 セルに必ず `(単位: 百万円)` を明示。`apply_unit_label` helper を build 開始時に呼ぶ。

### AP-9: 億円 scale で raw 値が「百万円単位」

- **症状**: scale = "hundred_million" だが cell value が `12_345` (百万円単位、raw のつもり)、format = `FMT_JPY_HUNDRED_MILLION`。display = `¥0.00` (raw 12,345 ÷ 10⁶ = 0.012)。
- **なぜ NG**: 億円 scale は Excel 標準カンマ表記の限界 (10⁶ までしか自然に表現できない) のため、特殊扱いが必要。§1.8 末尾の「raw 値も億円単位で保存」 例外を理解しないと壊れる。
- **正しい対応**: 億円 scale では **(a) 隣接列に formula で /10⁸ する**、または **(b) 例外的に raw value を「億円単位」 で保存して format `0.00`** のいずれか。`apply_hard_input(cell, value, scale="hundred_million")` の内部実装で吸収。

### AP-10: WCAG コントラスト比 4.5 未満

- **症状**: light yellow 背景 (#FFF3CC) に黄色文字 (#FFCC00)。コントラスト比 1.8:1。
- **なぜ NG**: 色弱・色覚多様性のある閲覧者が読めない。WCAG AA 違反。
- **正しい対応**: §2.7 の検証済 canonical pair のみを使用。`check_contrast` helper で CI 検証。

### AP-11: 色だけで意味を伝える (テキスト併記なし)

- **症状**: check status row が色 (緑 / 黄 / 赤) のみ、PASS / WARN / FAIL のテキストなし。
- **なぜ NG**: 色覚多様性のある閲覧者が判別不能。B&W 印刷時も判別不能。
- **正しい対応**: §2.8 の redundant cue (色 + テキスト + icon) を必ず併用。

### AP-12: scale 切り替えを年次で勝手に変える

- **症状**: builder が Y1 で `auto_scale_for_arr(Y1_ARR)` = thousand、Y5 で `auto_scale_for_arr(Y5_ARR)` = million を呼び、cell ごとに format を切り替える。
- **なぜ NG**: 1 シート内 mixed scale 禁止原則 §1.1 違反。閲覧者が時系列比較不可。
- **正しい対応**: build 開始時に **Y5 (終端) ARR で scale 決定** → 全期間同じ scale 使用。`auto_scale_for_arr` は 1 回だけ呼ぶ。

---

## 4.6 Decision FAQ (よくある判断疑問)

### Q1: ARR が境界値ピッタリ (例: ¥99,999,999) のとき、scale はどうする?

**A**: `auto_scale_for_arr` は厳密に `<` で判定するため、境界以下は thousand、境界 100M ピッタリも million ではなく thousand (Decision Rule §1.3 に従う)。境界振動を避けたいなら `auto_scale_for_arr` を呼ばずに builder 引数で明示指定する。意思決定上は 1 億円ピッタリと 9999.9 万円は事実上同じなので、どちらの scale でも実害はない。

### Q2: 売上 0 の Pre-Seed (まだ ARR がない) の scale は?

**A**: `auto_scale_for_arr(0) = thousand` (defensive default)。または **将来 Y5 の予測 ARR** で判定する方が実務的。早期 stage で「Y5 に ¥1B」 を目指すなら最初から million を選んで OK。

### Q3: 同じ workbook で 02_Revenue が million、08_CapTable が mixed の場合、整合性は?

**A**: シート単位で scale が違うのは OK (原則 §1.4)。08_CapTable は mixed allowed (§1.4 注釈)。**raw cell value が円単位で保存されている** 限り、cross-sheet 参照 `=02_Revenue!C5` は数値として正しく動く。display が違うだけ。

### Q4: Cover sheet の hero metric だけ「¥30 億円」 と表記したいが、他は「¥3,000」 (百万円単位)。許容?

**A**: Cover sheet の **hero metric 1 つだけ** scale override 許容 (§1.4 注釈)。format は `FMT_JPY_HUNDRED_MILLION`、他のシートは `FMT_JPY_MILLION`。Cover はモデルの「顔」 なので、最重要数値を最も読みやすい scale で表示するのは IB 慣習。

### Q5: 為替 (USD ↔ JPY) を扱うモデルで、scale はどう統一する?

**A**: **シート単位で通貨を分ける** ことを推奨。USD 表記シートは `FMT_USD_MILLION`、JPY 表記シートは `FMT_JPY_MILLION`。同じシート内で `$` と `¥` を混ぜない。為替 cell (例: 為替レート) は `FMT_INTEGER` または `0.00` で円/$表記。

### Q6: section header と subtotal が同じ行に来ることがある。どっちを優先?

**A**: 階層上、section header は subtotal より上位なので **section header を優先**。subtotal は section 内の中間集計なので、section header と同じ行になることは構造的にあり得ない (構造を見直すサイン)。

### Q7: KPI hero card と sensitivity matrix を同じシートに置きたい。色使用上限は?

**A**: §2.5 の上限はそれぞれ別カウント。KPI hero card 1-3 個 + sensitivity matrix 1-3 個 = 同じシートに最大 6 個並ぶことは可能。ただし「色を使うほど価値が下がる」 原則 §2.5 から、hero card と sensitivity を **物理的に離して配置** (上下分割) する。

### Q8: 11_KPI_Dashboard の数値はどの scale を使う?

**A**: KPI Dashboard は mixed allowed sheet (§1.4)。各 KPI のカテゴリに応じて override:

- ARR / MRR / Revenue → million
- NRR / GRR / Churn → percentage
- LTV / CAC → million (or thousand for early stage)
- LTV/CAC ratio → multiple
- Burn Multiple → multiple
- Headcount → integer
- Runway months → integer or 1-decimal

Dashboard 全体での「単位ラベル」 は B2 ではなく、各 KPI tile に inline で「(百万円)」「(%)」 等を併記する。

### Q9: B&W 印刷耐性のため border を増やしたいが、border も使い過ぎ NG?

**A**: 同じ data-ink minimization 原則。border も色と同様 「使うほど価値が下がる」。section header (実線下罫線)、grand total (double bottom border)、subtotal (細い top border) の 3 種類で hierarchy 表現すれば足る。全 cell に grid を引くのは Excel default ですでに弱く出ているので追加不要。

### Q10: scale を変更したい (model レビュー後に Pre-Seed → Series A scale へ昇格) 場合の手順は?

**A**:

1. 全シートの cell value (raw 円) は変えない (これが原則 §1.1 のメリット)。
2. `apply_unit_label(ws["B2"], scale="million")` を再実行 (B2 ラベル更新)。
3. 各 cell の number_format を `FMT_JPY_THOUSAND` から `FMT_JPY_MILLION` に一括置換。
4. cross-sheet 参照は変更不要 (raw 円ベース)。
5. 11_KPI_Dashboard / 13_IC_Memo の inline 表記 (「ARR ¥80M」 等) は手動 update 必要。

---

## 4.7 No-Merge Rule (canonical)

### 4.7.1 Why no merge

Cell merging (`openpyxl.Worksheet.merge_cells` / Excel の「セル結合」) は IB / FP&A best practice (Macabacus, Wall Street Prep) で **明示的に避けるべき** とされている。理由:

1. **Sort / Filter を破壊** — merged range は filter 不可、sort で値が消失することがある。
2. **Range select を破壊** — `Ctrl+Shift+arrow` が想定通り動かず、column 一括選択が破綻。
3. **Formula reference を破壊** — merged の左上 cell のみが値を持ち、他は `None`。`=B5+C5` のような式が壊れる。
4. **Named range と衝突** — merged にまたがる name は不安定、refers_to が不正な範囲に解決される。
5. **Fill / Drag を破壊** — fill handle の挙動が想定外。
6. **Programmatic edit が複雑化** — openpyxl / VBA で `MergedCell` は read-only で書き込み不可、try/except や事前 unmerge が必要。
7. **Print area / repeat title と衝突** — page break / repeat header が merged で乱れる。

### 4.7.2 Allowed alternatives (canonical)

| 用途 | NG (merge) | OK (No-Merge) |
|---|---|---|
| Sheet 上部 section header band | `apply_section_header(...) + merge_cells("B1:Z1")` | `apply_section_header_band(ws, row=1, start_col=2, end_col=N, label=...)` (fill propagation) |
| Year header span (Y1 が 2 cell に渡る等) | `merge_cells("C4:D4")` "Y1" | C4="Y1" alone, D4 は空 (text spillover に任せる) または C4 のみ value、`Alignment(horizontal="centerContinuous")` を C4-D4 に適用 |
| Section divider band (1 行 fill) | merge で band 表現 | 各 cell 個別 fill (ループで `cell.fill = PatternFill(...)`) |
| Row label spanning sub-rows | row 5-6 を merge | row 5 のみ label、row 6 は空 + indent 利用 |
| Sensitivity axis label (column 軸 / row 軸) | column / row を merge | label は単一 cell、隣接 cell は空 (axis としての意味は座標で伝わる) |

**`apply_section_header_band`** は `scripts/ib_format.py` で実装済 (Phase 6 補強)。leftmost cell に `apply_section_header` を適用し、`BG_HEADER_BAND` fill + 同 font を end_col までループ propagation する。merge と視覚的に同一だが、上記 7 項目を一切破壊しない。

### 4.7.3 `centerContinuous` の使いどころ

`Alignment(horizontal="centerContinuous")` は merge せずに連続セルの中央配置を実現する Excel 標準機能。本 skill では **section header (左寄せ) では使わない** が、以下の場合は許容:

- Year header 等で **中央寄せ** を span 表現したいとき (例: C4-D4 に「Y1」 を中央表示したい)
- value は左端 cell のみに置き、`centerContinuous` を span 全 cell に適用

### 4.7.4 Exempt cases

**現状: なし** (`00_Cover` も `write_cover` 実装で merge を使っていない)。例外を作らない方針 = D13 check は全 sheet 一律 0 件を expect。

将来 exempt を追加する場合は本 §4.7.4 にケース + 理由を明記し、`_check_d13_no_merge_cells` の `EXEMPT_SHEETS` を更新すること。

---

## 5. 関連 reference との整合

### 5.1 SSoT chain

```
_terminology.md §1 (IB Color = font color の what)
        ↓
_design_consistency_rules.md §2.2 (font color の when / where)
        ↓
00_design_guidelines.md §3 (Act ブランド色 + 実装値)
        ↓
17_chart_design.md §2 (chart 内 palette)
```

```
_terminology.md §3 (Sheet 順 = sheet naming の what)
        ↓
_design_consistency_rules.md §1.4 (sheet 別 default scale)
        ↓
各 builder script (実装)
```

### 5.2 役割分担

| Reference | 役割 | 本書との関係 |
|---|---|---|
| `_terminology.md §1` (IB Color) | Font color canonical (#0000FF 等) | 本書 §2.2 で同じ canonical を repeat、追加で background color rule (§2.3) を canonical 化 |
| `_terminology.md §3` (Sheet naming) | Sheet 順 (00_Cover, 01_Assumptions...) | 本書 §1.4 で再利用 (sheet 別 default scale) |
| `_master_decision_tree.md` | 意思決定 routing | 本書はその下位 SSoT (display 層) |
| `00_design_guidelines.md §3` (色彩) | Act ブランド色の正本 | 本書はそれを「いつ何に使うか」 に落とし込む |
| `01a_modeling_standards.md §4` (Number format) | number_format の規範 | 本書 §1.8 を canonical 引用元として参照 |

### 5.3 矛盾を見つけたとき

本書と他 reference に矛盾を見つけた場合の resolution rule:

1. **font color (IB Color)** の定義が矛盾: `_terminology §1` を **canonical** とする。本書はそれを引用しているだけ。
2. **background color** の定義が矛盾: 本書 §2.3 を **canonical** とする (本書が新規の SSoT)。
3. **scale 判定** の定義が矛盾: 本書 §1.3 を **canonical** とする。
4. **sheet 順** の定義が矛盾: `_terminology §3` を **canonical** とする。本書はそれを引用。
5. **number_format トークン** の定義が矛盾: `01a_modeling_standards §4` と本書 §1.8 を確認、不一致なら本書 §1.8 に揃え `01a` を update。

---

## 6. 違反検知 (sanity_checks.py との連携)

本書のルール違反は `sanity_checks.py` の D check (design / formatting check) で検知する。既存の D5, D7, D11 + 新 D 候補の連携:

| Check ID | 検知対象 | 本書のルール |
|---|---|---|
| **D5** | 余分 fill 検知 (data 範囲外への塗り) | §2.4 「塗ってはいけない場所 5」 (F 列など data 範囲外) |
| **D7** | Sensitivity table header bg 不統一 | §2.5 上限ルール、§2.3 BG_BASE_CASE |
| **D11** | IB Color Legend 違反 (font color) | §2.2 (Font Color Rule)、`_terminology §1` |
| **D12** | Number format 未設定 (General > 30%) | §1.8 number_format トークン |
| **D13** | Merged cell 検知 (No-Merge Rule 違反) | §4.7 No-Merge Rule |
| **D-new-1** (新規) | scale 混在 (1 シート内で複数 number_format scale) | §1.1 「mixed scale 禁止」 |
| **D-new-2** (新規) | font + bg pair 不一致 (§2.3 末尾の pair table 違反) | §2.3 末尾 |
| **D-new-3** (新規) | 単位ラベル B2 セル欠落 | §1.5 |
| **D-new-4** (新規) | 1 シート色使用上限超過 (§2.5) | §2.5 |
| **D-new-5** (新規) | WCAG コントラスト比不足 | §2.7 |

**D-new-1 (scale 混在検知) の実装ヒント**:

```python
def check_scale_consistency(ws) -> CheckResult:
    """1 シート内で number_format の scale が混在していないかチェック."""
    scales_found = set()
    for row in ws.iter_rows():
        for cell in row:
            nf = cell.number_format
            if "¥" not in nf and "$" not in nf:
                continue
            if nf == FMT_JPY_THOUSAND:
                scales_found.add("thousand")
            elif nf == FMT_JPY_MILLION:
                scales_found.add("million")
            elif nf == FMT_JPY_HUNDRED_MILLION:
                scales_found.add("hundred_million")
            elif nf == FMT_JPY_YEN:
                scales_found.add("actual")
    # mixed 許容シート (08_CapTable, 09_DCF § Sensitivity 等) は除外
    if ws.title in MIXED_ALLOWED_SHEETS:
        return CheckResult(status="PASS", message="mixed allowed")
    if len(scales_found) > 1:
        return CheckResult(
            status="FAIL",
            message=f"Sheet {ws.title} has mixed scales: {scales_found}",
        )
    return CheckResult(status="PASS")
```

**D-new-3 (単位ラベル欠落検知) の実装ヒント**:

```python
def check_unit_label_present(ws) -> CheckResult:
    """B2 セルに単位ラベルがあるかチェック."""
    cell = ws["B2"]
    if cell.value is None:
        return CheckResult(status="WARN", message=f"Sheet {ws.title}: B2 is empty (no unit label)")
    text = str(cell.value)
    if not (("単位:" in text) or ("Unit:" in text)):
        return CheckResult(status="WARN", message=f"Sheet {ws.title}: B2 = '{text}' (does not look like unit label)")
    return CheckResult(status="PASS")
```

---

## 適用ルール

1. 本書は font color / background fill / scale / 単位ラベルの **判定ルール** に関する SSoT。各 builder / sheet / line item で何を選ぶかを一意に決定する。
2. 本書と矛盾する記述を見つけた場合は §5.3 の resolution rule に従う。
3. 新規 builder 追加時、scale 判定と color 適用を本書のルールに従って実装。`scripts/ib_format.py` の helper 群を使用 (直接 cell.fill = ... のような low-level 操作は禁止)。
4. 違反検知は `sanity_checks.py` の D check で行う。新 D check 追加時は §6 を update。
5. ユーザー preference (「OS」 回避 / 時系列数値の表形式) は本書全体で遵守。

---

> 本書は **「いつ何を使うか」 の正本** である。具体実装値 (Hex / number_format 文字列) は引用先の SSoT (`_terminology` / `00_design_guidelines` / `01a_modeling_standards`) を確認すること。判定ルールが「答え」 を持つ唯一の場所は本書。
