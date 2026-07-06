# sfm-overhaul 自走進捗ログ

自走ループはこのファイルを毎ターン読み、現在地・各ループの結論・ブロッカーを追記する。
fresh context が復帰できるよう、状態は会話でなくこのファイルに残す。

参照: `spec.md`（仕様）, `plan.md`（実装計画）, `design-research.md`（C2 研究）。

## 状態

- 現在のフェーズ/タスク: **Phase 2 完了 — 全 K-test (K1/K2/K4/K5/K7) 緑、Phase gate review (advisor + Codex + Gemini) で出た 4 件指摘を 1 follow-up コミットで吸収。Task 2.5 (onboarding YAML) は plan deferred。**
- 終了状態: — （フェーズ単位で完了 / 要人間判断 / 反復上限到達 を区別して記録）

## 反復カウンタ

- Phase 0: **3 / 4 完了**
- Phase 1: **6 / 6 消費** (Task 1.1 / 1.2 / mid-fix / 1.3a / 1.3b / 1.4)
- Phase 2: **7 / 8 消費** (Task 2.1 / 2.2 / 2.3 / 2.4 / 2.6 audit / 2.6 schema / 2.7 review+fix)
- Phase 3: 0 / 6

## ログ

### 2026-05-25 — 前段クリーンアップ

着手前ワークツリーに 7 ファイルの未コミット差分があり、SFM 6 ファイルは plan の C1
方向と整合する「indent 列 canonical 化」前段作業、`shell/.zshrc` は無関係な
Antigravity IDE PATH 追加だった。advisor 指摘に従い、上書きせず2コミットに分割保存。

- `7ec147a` Canonicalize indent column rule across SFM workbook builder
  - `ib.INDENT_COL_WIDTH` + `apply_indent_column_widths()` / `audit_indent_column_widths()`
    を新設、`_set_column_widths` は indent 列上書きを ValueError 拒否、
    非期間シート（Guide/Driver Tree/Exit Waterfall/Benchmarks）を C 起点シフト、
    test_build_model はそれに追従 + `test_every_sheet_pins_indent_block_to_google_sheets_20px`
    を新設。
- `254a74c` Add Antigravity IDE bin directory to shell PATH

これにより Phase 1 着手時は SFM 既存テスト全緑のクリーン状態から開始可能。

### 2026-05-25 — Phase 0 Task 0.1: milestone-review scaffold + helper (TDD)

- `cb6dea9` Add milestone-review skill scaffold and route_review helper
  - `skills/milestone-review/{SKILL.md(scaffold), scripts/route_review.py, tests/test_route_review.py}`
  - `ReviewResult` dataclass + `run_reviewer(reviewer, prompt, *, timeout)` —
    codex→`codex exec`, gemini→`gemini -p`, `DEFAULT_TIMEOUT_SECONDS=180`、
    すべての CLI 失敗（timeout / FileNotFoundError / 非ゼロ exit）を
    `status="error"` に縮退、未知の reviewer 名は `ValueError`。
  - 9 contract tests 全緑（assert + print 方式、subprocess module-level 置換で mock）。

### 2026-05-25 — Phase 0 Task 0.2: SKILL.md + _reviewer_routing.md content

- `f6b7e48` Document milestone-review routing, flow, and answer-verification
  - SKILL.md 本文（trigger / 6-step flow / 4-check verification / failure handling /
    anti-patterns）に展開。
  - `references/_reviewer_routing.md` 新設:
    Routing table (Best for / Worst for)、ヒューリスティクス、プロンプト
    Background/Target/Question 3 ブロックルール、回答検証4項目、ワーキング例。

### 2026-05-25 — Phase 0 Task 0.3: bootstrap 3-route dogfood

実地 3 経路（codex / gemini / advisor）で `milestone-review` 自身をレビュー。

**Codex** (route_review.py 経由、`status=ok`, 41.9s) — route_review.py のレビュー
で2点指摘:
- `subprocess.run(text=True)` で `UnicodeDecodeError` が無補足で伝播し、契約違反。
- `except FileNotFoundError` は `OSError` の一サブクラス。`PermissionError` 等
  兄弟例外が伝播する。

**Gemini** (route_review.py 経由、`status=ok`, 36.9s) — リーク観点で問題なしと
判定するも、volunteer で同じ `UnicodeDecodeError` を指摘し `errors="replace"`
を推奨。**Codex と独立に同一バグへ収束** — 強いシグナル。

**advisor** (host tool) — 構造レビュー:
- 4-check verification protocol が初回で実バグを捕捉、設計が機能している。
- ユニットテストは「想定した失敗モードしか mock していない」coverage shape の
  欠陥。指摘を新規 regression test として固定すべき。
- `_reviewer_routing.md` に欠落あり (stakes ↔ route count、長尺プロンプト
  truncation TODO、Codex sandbox posture limitation)。

→ 回答検証4項目を適用:
1. **Grounded** — 両 CLI とも `route_review.py:75` を引用。advisor は transcript
   全体を引用。
2. **Primary evidence と整合** — `FileNotFoundError ⊂ OSError`、`text=True` の
   デフォルトは strict、両方 Python 公式仕様で確認。
3. **裁定** — 両 CLI 同一指摘で食い違いなし、advisor も整合。
4. **予測可能** — 失敗テスト追加→失敗→修正→緑、と段階予測通り進行可能。

すべての指摘を採用し TDD で修正:

- `bdcf9f4` Close two contract gaps surfaced by milestone-review bootstrap
  - `tests/test_route_review.py`: 3 件追加
    (`test_run_reviewer_returns_error_status_on_permission_error`,
     `test_run_reviewer_returns_error_status_on_unicode_decode_error`,
     `test_subprocess_run_receives_errors_replace_for_resilient_decoding`).
  - `scripts/route_review.py`:
    - `subprocess.run` に `errors="replace"` 追加（第一防衛線）。
    - `except FileNotFoundError` → `except OSError` 拡張。
    - `except UnicodeDecodeError` belt-and-suspenders 追加。
  - `_reviewer_routing.md`: 「Stakes ↔ route count」「Known limitations
    (Codex sandbox / 長尺プロンプト truncation TODO / shell alias 非追従)」追記。
  - 12 / 12 tests pass.

### 2026-05-25 — Phase 1 Task 1.1: `detect_table_block` ヘルパー (TDD)

- `fb3e0e7` Add detect_table_block helper to derive table bounds from cell content
- `ib_format.detect_table_block(ws, row, *, header_row=None)` →
  `(start_col, end_col)`。検出ロジック:
  1. `row` 以上の最上位行で `BG_TABLE_HEADER` 塗りがある cell の min/max
     col を返す（空中間 cell も block 内）。
  2. ヘッダが無ければ target row の content bounds をフォールバック。
  3. どちらも無ければ `ValueError`。
- 注記列（period block の右、`BG_TABLE_HEADER` 無し）は自然に排除。
- caller `header_row` 上書き対応で nested sub-table にも対応。
- 6 tests, 全 SFM suite 152 / 152 緑。

### 2026-05-25 — Phase 1 Task 1.2: `apply_semantic_border_span` ヘルパー (TDD)

- `d477941` Add apply_semantic_border_span symmetric to fill-span helper
- `ib_format.apply_semantic_border_span(ws, row, *, top=None, bottom=None,
  header_row=None, border_start_col=None)`。
- スパンは `detect_table_block` から内部で取得 — `start_col` / `end_col`
  引数は意図的に非公開（hard-code 復活を防止）。
- block 内空セル（D, E 等）にも罫線、indent 列は `border_start_col` で
  借景外へ。Border merge は left/right/diagonal を保存 (idempotent)。
- 5 tests, 全 SFM suite 157 / 157 緑。
- Phase 1 中間 milestone-review: Codex（interior task gate = 1 route per
  `_reviewer_routing.md`）で実行中、結果は次セクション。

### 2026-05-25 — Phase 1 mid-checkpoint review (Codex)

Task 1.3 着手前のヘルパー回帰チェック。`route_review.py` 経由で Codex に
detect_table_block + apply_semantic_border_span をレビュー (status=ok, 47.5s)。

**指摘3件**:
1. **Pre-header rows** — `row` がヘッダ確定前 (row 5 より上) の場合、フォール
   バックで target row の content bounds を返す。Note 列があれば誤って block
   に含む。→ 受容: caller は `_write_period_header` の後にしか呼ばないため、
   実コードパスには現れない。docstring に注意は明記済み。
2. **Blank spacer before header** — pre-header の空行で `ValueError`。
   → 受容: border / fill 適用対象でない（空白だから）。
3. **Nested tables** — `_find_table_header_row` が topmost-from-top で、
   内側 nested 表のヘッダを拾わない。**実バグ**。

検証4項目: grounded (line 引用), primary evidence と整合 (コード確認),
adjudication 不要 (単一指摘), 予測可能 (修正 → テスト緑予測通り) → 全クリア。

**修正** (`eecdedb`):
- `_find_table_header_row` を `range(row, 0, -1)` に変更 (nearest-above)。
- 既存 override テストが誤った挙動を pin していたので書き換え。
- 新規 `test_detect_table_block_uses_nearest_header_above_not_topmost` 追加。
- 158 / 158 緑。

**残課題**: 指摘1, 2 は実コードパスに現れないので Phase 1 内では追加対応
不要。将来 caller が増えた時の再評価対象として `_reviewer_routing.md` に
記録するほどではない (helper docstring が既に明示)。

### 2026-05-25 — Phase 1 Task 1.3a: `_write_values` bold-path 置換

- `41b204d` Replace _write_values bold-path borders with table-block span
- `source_plan_builder._write_values` の bold 分岐から
  `accent_cols = [LAYOUT.label_col, *period_cols]` + `if cell.value is None: continue`
  を撤去。`apply_semantic_border_span(ws, row, top=THIN_LINE,
  border_start_col=_row_rule_start_col(ws))` に置換。bold font は per-cell ループ維持
  (空セルに bold は意味なし)、borders は span-wide。
- **collateral fix 1**: `ib._is_intentional_blank_component_cell` を border 保持にも
  拡張。`clear_blank_cell_styles` が新規 border を消してしまう問題を解消。
- **collateral fix 2**: test helpers (`_styled_blank_cells`,
  `_memo_note_border_violations`) を runtime と同じ意味論に追従。subtotal 行
  (label が bold) の source/note 列は continuous span の通過対象として OK。
- 新規回帰テスト `test_write_values_bold_path_paints_continuous_border_across_d_and_e`
  で実 build (Assumptions "Total headcount" 行 35) の D, E 上罫線 thin を検証。
- 159 / 159 緑。

**Out of scope for 1.3a** (Task 1.3b/c に分割、次セッション着手):
`_highlight_row` (lines 511-526) も同じ accent_cols パターンを持つ。
`_section_band_end_col` (line 445), `_write_period_header` (line 397) の span を
`detect_table_block` 由来に統一。これらは既存
`test_semantic_fill_helper_uses_rectangular_span_including_blanks` (lines 1422-1426)
が old behavior を pin しているため、テスト更新と coupled。

### 2026-05-25 — Phase 1 Task 1.3b: `_highlight_row` 置換

- `aa2384a` Replace _highlight_row borders with table-block span
- `_highlight_row` の `accent_cols = [LAYOUT.label_col, *period_cols]` を撤去。
  `apply_semantic_border_span(ws, row, top=THIN_LINE, bottom=THIN_LINE,
  border_start_col=_row_rule_start_col(ws))` に置換。
- 既存テスト `test_semantic_fill_helper_uses_rectangular_span_including_blanks`
  の highlight-row assertion ブロックを継続 span 期待に書き換え (旧: D/E top None,
  新: D/E top + bottom thin)。
- 新規 `test_highlight_row_paints_continuous_border_across_source_and_unit`。
- 160 / 160 緑。
- Task 1.3c (`_section_band_end_col` / `_write_period_header` の
  `detect_table_block` 統一) は依然未着手 — notes 列扱いを別途検討要。

### 2026-05-25 — Phase 1 Task 1.4: 列幅 content 連動

- `6888e9a` Make label / source / note column widths content-driven
- 新規 primitives:
  - `ib._display_width(value)`: CJK-aware (Hiragana/Katakana/CJK Unified +Ext A
    /fullwidth)。CJK 1文字 = 2幅単位。
  - `ib.ROLE_WIDTH_BOUNDS`: role 別 [min, max] = label/source (54, 90),
    unit (14, 24), period (16, 24), note (72, 120)。
  - `ib.ROLE_WIDTH_PADDING = 2.0`、`ib.autosize_role_columns(ws, role_columns)`。
- 統合: `source_plan_builder._autosize_default_layout_columns(wb)` を
  `_disable_wrap_text` と `_clear_blank_cell_styles` の間に挿入。
  default-layout シートの label / source / note 列のみ対象 (period / unit は
  数値カラム=固定リズム維持で spec §2 C1 と整合)。
- 7 新規テスト (display_width / autosize 各 role / 実 build no-clipping 検証)。
- 167 / 167 緑。KPI source 列が 54 → 55 に成長することを実 build で観測 (内容駆動が
  実データで効いている証拠)。

### 2026-05-25 — Phase 1 Task 1.6: Phase gate review (3-route)

`milestone-review` の phase gate 規約に従い 3-route 実行。

**Codex** (route_review.py 経由、status=ok, 202.6s):
> "No findings. **complete**."
> "47 bold/highlight border rows checked, 0 border violations; label/source
> width violations: 0."
> 167 / 167 テスト緑も独立実行で確認。
> embedded side-table header labels (Pricing!25 / KPI!63 / Valuation!36, 46)
> は subtotal/total/highlight ではなく対象外。
> 唯一観察された soffice 再計算 smoke のローカル失敗は環境問題で Phase 1
> ロジック起因ではない。

**Gemini** (route_review.py 経由、status=ok, 63.6s) — future-looking risks 3 件:
1. **Performance**: autosize_role_columns は現状 23 シート × 3 列 × 100 行 ≒ 6,900
   cell accesses (negligible)。1,000 行 + 100 期 + 10 note列 で 250k アクセス、
   2-3 秒オーバーヘッドの可能性。
2. **detect_table_block 副作用**: (a) stray BG_TABLE_HEADER cell が頂上検出をシャドウ。
   (b) side-by-side テーブル (gap ≥ 2 列) が `min/max` で 1 ブロックに融合し
   ガター上もボーダーが引かれる。
3. **Ghost border**: `apply_box_border` で塗ったセルが後で空になっても
   `_is_intentional_blank_component_cell` の border 保持拡張で残存。
   ループで蓄積し sheet が汚れる可能性。

**advisor** (host tool): スコープ通り判定。"Spec §4 completion criteria met ✓.
Plan task list (1.5 / 1.3c) は Phase 2 準備で別途。" Gemini 指摘は future-monitored
risk として progress.md に記録し Phase 1 closure を阻害しない。

**Gemini 指摘の primary-evidence verification** (advisor 提案に従い grep 2 件):
- `apply_box_border` の production caller: 0 件
  (`ib_format.py:1343` 定義 + export のみ、test_build_model.py:1408 がテスト
  フィクスチャ単独使用)。**Ghost border** は現状コードパスに現れない。
- 23 シート全 row 5 の BG_TABLE_HEADER 列ギャップ: ≥ 2 列のギャップ 0 件。
  **Side-by-side テーブル** は現状なし。

**回答検証4項目**:
1. Grounded — Codex は 47 行カウント / 違反0 / 167 緑、Gemini は file:line 引用、
   primary-evidence grep 2 件で全て anchored。
2. Primary evidence と整合 — grep 結果が Gemini の指摘を現状コードパス外と確定。
3. 裁定 — Codex / Gemini 直接対立なし (Codex は as-shipped、Gemini は
   future-looking)。advisor の整理を採用。
4. Predictive — Phase 1 closure → Phase 2 着手で、Gemini 指摘は Phase 2 で
   pathological shape を導入する場合に再評価。

## Phase 1 最終判定: **完了** (6 / 6 反復)

- **Spec §4 完了条件** (Phase 1 closure gate): **すべて met ✓**
  - 罫線スパン違反 0 ✓ (Task 1.3a / 1.3b)
  - `apply_semantic_border_span` 存在 ✓ (d477941)
  - 列幅ハードコード撤廃 = content 連動 ✓ (6888e9a)
  - `test_build_model.py` 全緑 ✓ (167 / 167)
- **Plan task list** で deferred な項目 (closure gate ではない):
  - **Task 1.3c**: `_section_band_end_col` / `_write_period_header` の
    `detect_table_block` 統一。notes 列の含有判定を別途検討要。
  - **Task 1.5**: 階層インデント動的化 + C2 prompt 反映
    (`_layout_canonical.md` / `_ib_workbook_design_system.md` の文言強化)。
- **Future-monitored risks** (Gemini 指摘、現状コードパス外):
  - perf at 10× current scale
  - side-by-side tables (`detect_table_block` の min/max 合成リスク)
  - apply_box_border production 利用が増えた場合の ghost border

## Phase 0 最終判定: **完了** (3 / 4 反復)

- C0 完了条件:
  - [x] `milestone-review` を3経路で各1回正常応答 + 回答検証4項目起動
  - [x] `test_route_review.py` 12/12 緑
  - [x] route_review.py のコントラクトギャップを bootstrap 自身が surface し
        修正コミット完了
- 1 反復残し（上限 4）。

### 2026-05-26 — Phase 2 Task 2.1〜2.6: 経済カーネル K-set 実装

5 件の K-test に対応する runtime / audit / docs を 6 コミットで実装。

- `7718562` Task 2.1: K1/K2/K4/K5/K7 失敗テスト + evals.json eval 11 (red)
- `5df2fd0` Task 2.2 (A): `customers` / `churn_rate` honor
  - `ending_units(new_units, *, churn_rate=None)` — 構造化入力では指定 rate、
    未指定では legacy 0.02 + idx × 0.005 schedule。
  - `plan_revenue_series(..., *, installed_base=None, churn_rate=None)` —
    installed_base 指定時は average_units(installed_base) を recurring base に。
  - `calibrate_cost_stack_to_gross_margin` も同 kwarg、calibrate と audit の
    revenue 基底を整合。
  - `SourceFacts.customers_pinned: bool = False` 追加 (`_derive_facts_from_primitives`
    で `prims.demand_pinned` から派生)。narrative path では False を維持して
    legacy 挙動を保存 (SaaS の "logos vs seats" 混同を避ける)。
  - `_facts_installed_base(facts)` helper で K1 gate を 4 呼び出しに供給。
  - 169/172 緑 (K1+K2 green)。
- `869b82f` Task 2.3 (C): NOL carryforward
  - `project_free_cash_flow` に `nol_balance` ロールフォワード追加。
    `taxable = max(0, ebt - nol_balance)`; 損失は `-ebt` を nol_balance に加算。
  - `opening_nol_yen` kwarg と per-period 出力 `ebt` / `tax` / `nol_balance`。
  - 170/172 緑 (K4 green)。
- `277d07c` Task 2.4 (E): Off-mechanics suppression
  - 非 marketplace profile は `gmv_yen = [0]` / `take_rate = [0]` を facts に
    emit。内部の local `gmv` は TAM / headcount sizing 用に保存 (revenue proxy)。
  - `_take_rate_series` の 0.004/period ramp が take=0 でも続く問題を construction
    time で zero out。
  - 171/172 緑 (K5 green)。
- `f1c3ede` Task 2.6 (I) audit hooks: `audit_economic_coherence` に
  K1 customers drift / K4 NOL ceiling (max_rate × max(0, cum_ebt), 1% tolerance) /
  K5 off-mechanics 検出を追加。
  - 172/172 全緑 (K7 green, Phase 2 完了条件 met)。
- `0dbd21c` Task 2.6 (J): `_input_schema.md` 新設 — YAML key 全列挙 + K-set
  audit invariants クロスリファレンス。SKILL.md から参照を追加。

### 2026-05-26 — Phase 2 Task 2.7: Phase gate review (3-route)

`milestone-review` 3-route gate を実行 (advisor + Codex + Gemini)。Phase 2
の closure 判定に4件の具体的指摘を吸収。

**Codex** (status=ok, 155.5s) — "Not complete":
1. K2 が structured kernel path で honor されていない:
   `derive_source_facts_from_mapping` が `churn_rate` parse 前に
   `prims.customers = ending_units(prims.new_units)` を呼んでおり、stated_churn
   が implicit-customers rollforward に反映されない。実地 probe で確認
   (`new_units=[200]*5`, churn 0.02 vs 0.30 → identical customers / revenue)。
2. K7 audit に K2 branch なし: K1 / K4 / K5 のみ。
3. archetype coherence は維持 ✓ (saas / hardware / marketplace の audit=[])。

**Gemini** (status=ok, 159.3s) — 3 risks:
1. K5 audit が `"marketplace" in label` substring 一致で hybrid プロファイル
   (hardware + platform fee 等) で false-positive のリスク。
2. NOL absorption: risk なし ✓。
3. K1 ratio 0.25-4.0 は `hardware_asset_heavy` (1 sites = 多 units, ~27x)
   で legitimate hardware に false-positive。

**advisor** (host tool) — adjudication:
- K1/K2 を unified message に折りたたむか別 branch にするかを意識的に決め、
  commit に記録すべき。spec §3 K7 wording の解釈次第。
- K1 hardware 50x bound: 現プロファイル群 (max 27.7x) に対し OK だが
  profile-driven であることをコメントすべき。
- closure 前に Codex の正確な probe を **全期間** で再走させて確認すべき。

**4点検証**:
1. Grounded — 全指摘 file:line / 実地 probe 引用 ✓
2. Primary evidence と整合 — Codex probe を私自身が独立再現、ratio 27.7x も
   profile 値から手計算で確認 ✓
3. 裁定 — Codex / Gemini に直接 disagreement なし。advisor は判断軸を整理 ✓
4. 予測 — 修正後に probe 再走で churn 0.02/0.30 が divergent になることを予測、
   実行後に確認 ✓

**修正コミット** `75f029a` Close Phase 2 review findings:
- `derive_source_facts_from_mapping` で `raw_churn` を demand block の **前** に
  パース → `prims.stated_churn` 確定後に `ending_units(prims.new_units,
  churn_rate=prims.stated_churn)` を呼ぶ。
- 新規回帰テスト `test_K2_structured_yaml_churn_rate_moves_terminal_customers_and_revenue`
  で integrated path を pin (low / high churn で terminal customers / revenue
  > 30% / 20% divergent)。
- K1 audit を "K1/K2 customers drift" 統一メッセージに変更し、churn_rate を
  メッセージに含める。K2 violation の唯一 realistic audit signal は
  "rollforward at stated churn ≠ stated customers" であり、K1 drift と機能的に等価
  と判断 (spec §3 K7 の "detect" は別 branch を strict には要求しない解釈)。
- K1 ratio は profile-aware に: hardware / asset / unit_sale → `(0.10, 50.0)`、
  その他 → `(0.25, 4.0)`。
- K5 audit を `facts.mechanics == _profile("marketplace").label` に変更し、
  substring false-positive を排除。

**実地再 probe** (all-periods):
- low churn (0.02): customers [200, 396, 589, 778, 963], revenue 21.6→145.7M
- high churn (0.30): customers [200, 340, 438, 507, 555], revenue 21.6→92.0M
- 全期間で divergent、audit=[] ✓ K2 end-to-end honored

最終: **173 / 173 緑** (Phase 1 167 + Phase 2 K-tests 6 = 173)。

## Phase 2 最終判定: **完了** (7 / 8 反復)

- **Spec §4 完了条件**: すべて met ✓
  - K1 / K2 / K4 / K5 / K7 eval green
  - `test_build_model.py` + `test_economic_quality.py` 全緑 (173 / 173)
  - 代表ケース `--strict-audit` pass (Codex probe 確認済み)
- **Plan task list で deferred な項目**:
  - **Task 2.5** (F): `onboarding_months` / `one_time_revenue_per_unit_yen`
    YAML driver。failing test なし、closure gate 外。Phase 3 着手前か Phase 3
    完了後の polish として残す。
- **Future-monitored risks** (Phase 3 / 将来のプロファイル拡張で再評価):
  - K1 hardware ratio 50x 上限は現プロファイル (max 27.7x) に対し余裕あり。
    100+ units/site の新プロファイル追加時に再評価。

## 次フェーズ: Phase 3 — 経済カーネル Tier 2 (C3 Tier 2)

完了条件 (spec.md §4): B/D/G/H の追加 eval (K3 / K6 / K8 含む) 緑、既存テスト
全緑。反復上限 6。
**前提**: Phase 2 完了 + 既存 173 / 173 緑が維持されていること。

**着手タスク順** (plan §Phase 3):
1. **Task 3.1 (B)**: 全ファイナンス手段 (lease / converts / grants / customer
   advances / secondary) の equity サイジング / FCF 統合 + K3 eval。
2. **Task 3.2 (D)**: debt / lease の約定弁済スケジュール (`debt_amortization`)。
3. **Task 3.3 (G)**: 期央 (half-year) 減価償却コンベンション。
4. **Task 3.4 (H)**: governor 透明化 + K6 / K8 (マテリアル収益出所 / 粗利クランプ
   警告)。
5. **Task 3.5**: 最終検証 + Phase 3 milestone-review (3-route)。

**Phase 3 着手前ヘルスチェック**:
- `PYTHONPYCACHEPREFIX=$(mktemp -d) python3 -m pytest
  skills/startup-financial-modeling/build/tests/` で 173 / 173 緑
- `sh scripts/validate-repo.sh` 全パス
- `git log --oneline | head -30` で本 overhaul の全コミットを確認

## Phase 3 — カーネル Tier 2（C3 Tier 2）: 実施記録（2026-07-05）

**着手前ヘルスチェック**: 2件のテスト逸脱（invocation protocol の guard phrase 逸脱、
eval 12 の XLSX assertion 欠落）を修正して 174 / 174 緑を回復。`validate-repo.sh` の
`__pycache__` 混入も掃除して全パス。前セッション未コミット分を2コミットに整理
(d89f44f milestone-review host-aware routing / 74130bf sfm rubric+prompt-research)。

**Task 3.1 (B / K3)** — commit 10c4142:
- grants / convertibles / lease / customer_advances / secondary / debt /
  (追って) debt_amortization を Step-5 表示 override から **stated driver** に移動。
  FCF 投影・equity 自動サイジング・ending cash・BS(A=L+E) に統合。
- converts+lease は利子性残高へ(P&L interest = 残高×rate のワークブック式と一致)。
- advances は ap_deferred(運転資本レベル)経由 — CF row 21 の二重計上を解消
  (grants 単独行に変更)。
- audit: secondary が同時ラウンド無しで計上されたら K3 違反。
- K3 テスト5本 + eval K3 assertion + `_input_schema.md` 更新。

**Task 3.2 (D)** / **Task 3.3 (G)** — commit 4dfeec9:
- `debt_amortization_yen`: 残高 = 累積 drawn − 累積 repaid、利息は逓減残高基準。
  Capital Stack row 11 入力行、残高式・CF row 20 が控除。返済超過は audit 違反。
- 減価償却は half-year convention 既定(`depreciation_convention`、kernel と
  P&L D&A 式の両方)。K3 弁済テスト4本 + G テスト2本。

**Task 3.4 (H / K6 / K8)** + **Task 2.5 (F)** — commit 9ec7ac5:
- 非ブロッキング `audit_economic_warnings` 新設: K8 = 5–95% 範囲外
  target_gross_margin のクランプを警告化(導出時に `derivation_warnings` へ収集、
  strict-audit ビルドが [warn] 表示)。K6 = demand 未ピンの重要収益に provenance 警告。
- Cost Build に governor 再スケール注記行。
- one-time / onboarding 収益を YAML driver 化(`onboarding_months` /
  `one_time_revenue_per_unit_yen`)。未指定時のみ price×3、Assumptions 行は
  `placeholder` ラベル。K6/K8/H/F テスト5本。

**Task 3.5 最終検証**:
- 全テスト **190 / 190 緑**(K1–K8 相当の K/G/F/H 系含む)。
- 代表 YAML(全財源 + 弁済 + onboarding 指定)で `--strict-audit` pass。
- soffice 再計算: `data_only` エラー **0**、BS balance check 全期間 0、
  負債残高ロール 200→700→700→550→400M(弁済控除が実数値で一致)。
- PDF レンダリング目視: Revenue Build(one-time = price×4 反映)、CF(Grants 行
  独立・二重計上なし)、People Plan、Capital Stack 各ページの罫線・列幅・階層OK。
- ドメインルーブリック(build/evals/startup-finance-rubric): **100 / 100**(閾値95)。
- `validate-repo.sh` 全パス。
- milestone-review: **advisor ツールは本セッションで利用不可**(呼び出しがエラー)。
  縮退運用として codex + gemini の2外部経路でレビューを実施。

**Phase 3 milestone-review 結果と裁定(host=claude-code、codex+gemini、advisor 縮退)**:

- **Codex(runtime diff レビュー, 316s)** — 指摘4件、全て一次証拠と突合:
  1. stated `debt_interest_rate` が output_pct_series に残りサイジング未到達 →
     **妥当・修正**(stated driver 化、¥2B×25% で sized equity が増えるテスト追加)。
  2. D&A `×12/life` は年次期間前提、monthly/quarterly grain で過大 → **妥当だが
     Phase 3 以前からのカーネル全体の年次前提**(recurring ×12 も同様)。既知の制約
     として `_input_schema.md` の grain 行に明記。将来フェーズ候補。
  3. one-time fee の「正値=stated」判定で kernel/workbook が混在スケジュールで乖離 →
     **妥当・修正**(statedness 契約: facts は未指定時 `[]`、指定時はゼロ含め権威。
     混在スケジュールのテスト追加)。
  4. Financing 行15 小計が advances を含む表示不一致 → **妥当・修正**(SUM(7:11)
     −secondary−amortization に変更、advances は運転資本経由で除外)。
  弁済ロジックの二重計上は「無し」と明言(kernel 検証と一致)。
- **Gemini(会計・ファイナンス処理レビュー, 46s)** — 8項目中 OK 5 / concern 3:
  - Grants→contributed capital(P&L 経由でない): concern。簡略化として
    `_input_schema.md` に明記(Financing 行で可視、A=L+E は維持)。
  - converts を debt と混合(転換希薄化が残高に出ない): concern。転換希薄化は
    cap table / Ownership の責務と整理し、`_input_schema.md` に明記。
  - NOL を累計不等式で計算している: **誤読として棄却** — kernel は期別
    `nol_balance` ロールフォワードで計算(project_free_cash_flow)。累計不等式は
    K4 監査側の上限チェック。一次証拠(コード)優先。
  - founder secondary: 会社キャッシュアウト扱いは redemption 構造のみ妥当、純粋な
    投資家間セカンダリーはゼロインパクトにすべきとの提言 → **採用(文書対処)**:
    `secondary_yen` の意味を「会社資金による liquidity(redemption/facilitated
    buyback)」に限定し、純粋セカンダリーは 0 のまま Ownership で扱うと明記。
    Financing 行13 の source も "company-funded liquidity use" に変更。
- 修正後の回帰: **193 / 193 緑**。代表 YAML 再ビルド strict-audit pass、soffice
  再計算エラー 0、BS balance 全期間 0、Financing 行15 = CF と完全整合
  (p0 1,050M / advances 除外 / 弁済期 −150M)。ルーブリック **100 / 100** 維持。
  `validate-repo.sh` 全パス。

## Phase 3 最終判定: **完了**(反復 2 / 上限 6)

- spec §4 C3 Tier 2 完了条件: B/D/G/H の追加 eval(K3/K6/K8 含む)緑、既存テスト
  全緑 — すべて met ✓(反復1 = Task 3.1〜3.4 + 2.5 実装、反復2 = milestone-review
  指摘3件の修正)。
- 本 overhaul(C0 / C1 / C2 / C3 Tier 1 / C3 Tier 2)はこれで全フェーズ完了。
- 将来フェーズ候補(未着手・要スコープ判断): 非年次 grain のカーネル経済
  (×12 前提の解消)、grants の P&L 経由計上オプション、convertible の
  転換時デット→エクイティ振替の三表連動。

## ブロッカー / 要人間判断

（なし）

## fresh-context 用 リマインド

- ai-agent-config 直下、`main` ブランチ。
- 既存テスト実行: `PYTHONPYCACHEPREFIX=$(mktemp -d) python3
  skills/startup-financial-modeling/build/tests/test_build_model.py` 及び
  `test_economic_quality.py`。両者緑が前提。
- 検証: `sh scripts/validate-repo.sh`。
- milestone-review 経由レビュー実行（次フェーズ完了時）:
  `python3 skills/milestone-review/scripts/route_review.py --reviewer
  codex --prompt "..." --json`。
