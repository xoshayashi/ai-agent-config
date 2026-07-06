# startup-financial-modeling 改修 ＋ milestone-review 新設 — 実装計画

> **For agentic workers:** この計画は完全自律 `/loop` で実行する。各タスクは TDD（失敗するテストを先に書く→最小実装→緑→コミット）で進める。進捗・各ループの結論・ブロッカーは `docs/sfm-overhaul/progress.md` に逐次記録し、fresh context が復帰できるようにする。チェックボックス `- [ ]` で追跡。

**Goal:** `startup-financial-modeling` のレイアウト基盤を汎用構造で動的化し、経済カーネルの入力忠実度・整合性を修正し、汎用レビュースキル `milestone-review` を新設する。

**Architecture:** 4フェーズ。Phase 0（`milestone-review` 新設）を最初に行い、以降のフェーズの節目レビューに dogfood する。Phase 1（レイアウト汎用化）、Phase 2（カーネル Tier 1）、Phase 3（カーネル Tier 2）。各タスクは TDD。`main` に直接コミット。

**Tech Stack:** Python 3.14、openpyxl、pytest（テストは直接実行も可）、LibreOffice（soffice、再計算検証）、Codex CLI / Gemini CLI（外部レビュー）、advisor ツール。

参照: `docs/sfm-overhaul/spec.md`。リポジトリ: `ai-agent-config`。スキル基点: `skills/startup-financial-modeling/`、新スキル: `skills/milestone-review/`。

---

## 前提・共通事項

- 既存テストの実行:
  `PYTHONPYCACHEPREFIX=$(mktemp -d) python3 skills/startup-financial-modeling/build/tests/test_build_model.py`
  および `.../test_economic_quality.py`。
- ビルド: `python3 skills/startup-financial-modeling/scripts/build_model.py --input <yaml> --mode full --strict-audit -o <out>`。
- テストを緩めて完了条件を満たすことは禁止。コード側を直す。
- 各フェーズ完了時に `milestone-review` でレビューし、回答の妥当性を判定してから次へ。
- コミットメッセージ末尾に `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`。

---

## Phase 0 — `milestone-review` スキル新設

**完了条件:** 3経路（advisor/Codex/Gemini）で各1回正常応答＋回答検証起動。`test_route_review.py` 緑。反復上限 4。

### Task 0.1: スキル骨格と `route_review.py`

**Files:**
- Create: `skills/milestone-review/SKILL.md`
- Create: `skills/milestone-review/scripts/route_review.py`
- Create: `skills/milestone-review/tests/test_route_review.py`

- [ ] **Step 1: 失敗テストを書く** — `test_route_review.py` に、`route_review.py` の関数 `run_reviewer(reviewer, prompt, *, timeout)` を検証するテスト:
  - `reviewer="codex"` で、CLI を呼ぶコマンド配列が `codex exec` を含むこと（subprocess を monkeypatch / fake で検証）。
  - `reviewer="gemini"` で `gemini -p` 系であること。
  - タイムアウト時・非ゼロ終了時に例外でなく `ReviewResult(status="error", ...)` を返すこと（縮退）。
  - 不正な `reviewer` 値で `ValueError`。
- [ ] **Step 2: テストを実行し失敗を確認** — Run: `python3 skills/milestone-review/tests/test_route_review.py`。Expected: FAIL（モジュール無し）。
- [ ] **Step 3: `route_review.py` 実装** — `run_reviewer` と `ReviewResult` dataclass。Codex は `codex exec <prompt>`、Gemini は `gemini -p <prompt>`、いずれも `subprocess.run` で stdout/stderr/returncode を取得、`timeout` 既定 180s、失敗は `status="error"` で縮退。`advisor`/`self` は外部呼び出し対象外（CLI からは扱わず、SKILL.md の指示で対応）と明記。
- [ ] **Step 4: テスト緑を確認** — Run: 同上。Expected: PASS。
- [ ] **Step 5: コミット** — `git add skills/milestone-review && git commit -m "feat(milestone-review): add review-routing skill scaffold and CLI helper"`。

### Task 0.2: `SKILL.md` と `_reviewer_routing.md`

**Files:**
- Modify: `skills/milestone-review/SKILL.md`
- Create: `skills/milestone-review/references/_reviewer_routing.md`

- [ ] **Step 1:** `SKILL.md` を書く — frontmatter（`name: milestone-review`、`description:` は「作業の節目でレビューを advisor/Codex/Gemini/self にルーティングし回答を検証する。他スキルから呼ばれる」旨）、起動条件、フロー（節目検出→レビュー種別分類→ルーティング→プロンプト構築→実行→回答検証→次工程予測の妥当性判定→続行/差し戻し）、`scripts/route_review.py` の使い方。
- [ ] **Step 2:** `_reviewer_routing.md` を書く — spec §2 C0 のルーティング表、レビュアー別プロンプト構築規約（外部CLIには背景・対象・問いを厚く明示）、回答検証4項目（根拠/一次証拠整合/裁定/次予測の妥当性）、盲目的採用・棄却の禁止。
- [ ] **Step 3:** プレースホルダ・矛盾を自己点検し修正。
- [ ] **Step 4: コミット** — `git commit -am "docs(milestone-review): SKILL.md and reviewer routing reference"`。

### Task 0.3: ブートストラップ二重チェック（3経路実地検証）

- [ ] **Step 1:** Codex 経路を実地実行 — `route_review.py` 経由で `codex exec` に小さなレビュー依頼（例: `route_review.py` 自体のコードレビュー）を投げ、正常応答を得る。
- [ ] **Step 2:** Gemini 経路を実地実行 — 同様に `gemini -p`。
- [ ] **Step 3:** advisor 経路 — `milestone-review` のフローに従い advisor ツールを起動し、`milestone-review` スキルの設計自体をレビューさせる。
- [ ] **Step 4:** 3経路の回答に回答検証4項目を適用し、結果を `progress.md` に記録。CLI 経路が認証等で失敗する場合は縮退の挙動を確認し、ブロッカーとして記録。
- [ ] **Step 5:** Phase 0 を `milestone-review` 自身の枠組みで総括し、Phase 1 へ。

---

## Phase 1 — レイアウト汎用化（C1）

**完了条件:** 全シートで罫線スパン違反 0（テーブルブロック全幅・空セル含む・途切れなし）。固定列幅ハードコード撤廃＝コンテンツ連動。`apply_semantic_border_span` 存在。`test_build_model.py` 全緑。反復上限 6。
**前提:** C2 デザイン研究レポートを受領し、`_layout_canonical.md` / `_ib_workbook_design_system.md` の文言強化に反映する（Task 1.5）。

### Task 1.1: テーブルブロック検出関数

**Files:**
- Modify: `skills/startup-financial-modeling/build/runtime/ib_format.py`
- Test: `skills/startup-financial-modeling/build/tests/test_build_model.py`（レイアウト系テスト群に追加）

- [ ] **Step 1: 失敗テストを書く** — `detect_table_block(ws, row)` の契約をテストで固定:
  - 与えた行について、属するテーブルブロックの `(start_col, end_col)` を返す。
  - `start_col` / `end_col` は、行のテキスト位置・数値/数式セル・背景色（セマンティック fill）から決定し、ハードコードの列番号に依存しない。
  - 合成ワークブック（ラベル C、空 D・E、値 F-L のヘッダ行＋データ行）で、合計行に対し `end_col` が F-L 群の最右（L）を返し、`start_col` がラベル列（C）を返すこと。
  - 注記列が存在するシートでもブロック右端がデータ表の右端で一致すること（帯と合計の不一致解消の根拠）。
- [ ] **Step 2:** テスト実行→失敗確認。
- [ ] **Step 3:** `detect_table_block` を実装。行が属するブロックを、近傍行のヘッダ/fill とセル内容（非空・数式・period 列）から推定する汎用ロジック。列番号直書きをしない。
- [ ] **Step 4:** テスト緑を確認。
- [ ] **Step 5: コミット**。

### Task 1.2: `apply_semantic_border_span` ヘルパー

**Files:**
- Modify: `skills/startup-financial-modeling/build/runtime/ib_format.py`
- Test: `test_build_model.py`

- [ ] **Step 1: 失敗テストを書く** — `apply_semantic_border_span(ws, row, *, weight, edge)` の契約:
  - スパンは `detect_table_block` から取得（引数で列範囲をハードコードしない）。
  - ブロック内の空セル・中間セル（source/unit 列等）にも同じ罫線が付くこと（`value is None` でスキップしない）。
  - インデント列は罫線面にしない判定が、列番号でなく役割（テキスト位置/fill）から導かれること。
- [ ] **Step 2:** 失敗確認。
- [ ] **Step 3:** 実装。`apply_semantic_fill_span` と対称な構造。
- [ ] **Step 4:** 緑確認。
- [ ] **Step 5: コミット**。

### Task 1.3: `_write_values` の罫線をヘルパーに置換

**Files:**
- Modify: `skills/startup-financial-modeling/build/runtime/source_plan_builder.py`（`_write_values` bold 分岐、`_section_band_end_col`、`_write_period_header`、`_highlight_row`）
- Test: `test_build_model.py`

- [ ] **Step 1: 失敗テストを書く** — 実ビルド（小さな YAML）で生成した xlsx を openpyxl で開き、全シートの全小計/合計/セクション帯/ヘッダ行について、罫線スパンが `detect_table_block` 由来のブロック全幅と一致し、途中ギャップ（D・E 等）が無いことを検証。現状コードでは FAIL するはず。
- [ ] **Step 2:** 失敗確認。
- [ ] **Step 3:** `_write_values` の `accent_cols` 手組みと `if cell.value is None: continue` を撤去し `apply_semantic_border_span` に置換。帯・ヘッダ・ハイライトも同一ブロック検出に統一。
- [ ] **Step 4:** テスト緑、かつ既存 `test_build_model.py` 全緑を確認。
- [ ] **Step 5: コミット**。

### Task 1.4: 列幅のコンテンツ連動化（固定幅ハードコード撤廃）

**Files:**
- Modify: `skills/startup-financial-modeling/build/runtime/ib_format.py`（`COL_*_WIDTH` 利用箇所）、`source_plan_builder.py`（`_setup_sheet` / `_set_column_widths`）
- Test: `test_build_model.py`

- [ ] **Step 1: 失敗テストを書く** — 生成 xlsx で、ラベル/ソース/ノート列の幅が、列内セル値の最大表示長（CJK=2幅換算）に連動し役割別 [min,max] で clamp されること。短ラベルのみのシートは過剰幅でなく、長ラベルのシートは見切れない閾値を満たすこと。固定値 54.0 等が出ないこと。
- [ ] **Step 2:** 失敗確認。
- [ ] **Step 3:** 全データ書込み後に走る `autosize_role_columns(ws)` を実装し、固定幅代入を置換。役割別 min/max は定数だが幅自体はコンテンツ連動。
- [ ] **Step 4:** 緑確認＋既存テスト全緑。
- [ ] **Step 5: コミット**。

### Task 1.5: 階層インデント列の動的化＋プロンプト強化

**Files:**
- Modify: `source_plan_builder.py`（`LayoutSpec.hierarchy_cols`、`_setup_sheet`、列番号直書き箇所）
- Modify: `build/references/_layout_canonical.md`, `build/references/_ib_workbook_design_system.md`
- Test: `test_build_model.py`

- [ ] **Step 1: 失敗テストを書く** — 階層深度が異なるモデルで、インデント列本数が深度から動的に決まり `label_col` 以降が正しく右シフトすること。列番号直書きに依存した破綻が無いこと。
- [ ] **Step 2:** 失敗確認。
- [ ] **Step 3:** `hierarchy_cols` を深度から算出。列番号直書き箇所を点検し役割ベースに汎用化。
- [ ] **Step 4:** C2 研究レポートの知見を `_layout_canonical.md` / `_ib_workbook_design_system.md` に、逃げ道のない明示表現で反映（列幅連動・罫線ブロック単位・階層列の扱いを重点）。
- [ ] **Step 5:** 全テスト緑を確認。
- [ ] **Step 6: コミット**。

### Task 1.6: Phase 1 レビュー

- [ ] `milestone-review` 経由で Codex（コード diff の妥当性）＋ advisor（汎用性・退行リスク）にレビュー依頼。回答検証4項目を適用。指摘が妥当なら修正タスクを追加して反復（上限6）。`progress.md` に記録。

---

## Phase 2 — カーネル整合性 Tier 1（C3 Tier 1）

**完了条件:** 新規 eval K1/K2/K4/K5/K7 緑。`test_build_model.py`＋`test_economic_quality.py` 全緑。代表ケースで `--strict-audit` pass。反復上限 8。

### Task 2.1: K1-K2-K4-K5-K7 の失敗テストを先に追加

**Files:**
- Modify: `skills/startup-financial-modeling/build/tests/test_economic_quality.py`
- Modify: `skills/startup-financial-modeling/build/evals/evals.json`

- [ ] **Step 1:** `test_economic_quality.py` に K1/K2/K4/K5/K7 のテストを追加（spec §3 の定義）。`evals.json` に対応する計算/ロジック検証 assertion を追加。
- [ ] **Step 2:** 実行し、現状コードで K1/K2/K4/K5/K7 が FAIL することを確認（バグの存在証明）。
- [ ] **Step 3: コミット** — `git commit -m "test(sfm): add K1-K7 economic-coherence regression tests (currently red)"`。

### Task 2.2: A — `customers`/`churn_rate` を収益に効かせる

**Files:**
- Modify: `build/runtime/economic_kernel.py`（`_period_subtotal_revenue` L1483 近傍、`ending_units` L1169 近傍、`derive_source_facts_from_mapping`）

- [ ] **Step 1:** 経常収益の installed base を、明示指定があれば `facts.customers` 系列から導く（期中平均）。未指定時のみ `ending_units(new_units)` フォールバック。`ending_units` の churn を `churn_rate` 引数で受ける。
- [ ] **Step 2:** K1・K2 が緑になることを確認。
- [ ] **Step 3:** 既存 `test_build_model.py`＋`test_economic_quality.py` を実行し退行が無いか確認。退行があれば原因を直す。
- [ ] **Step 4: コミット**。

### Task 2.3: C — NOL 繰越の実装

**Files:**
- Modify: `economic_kernel.py`（`project_free_cash_flow` の税計算 L1570 近傍）、`source_plan_builder.py`（`Financing` の NOL 残高行、`P&L` の Cash tax 行）

- [ ] **Step 1:** `nol_balance` ロールフォワードで `taxable = max(0, ebt - nol_balance)`、cash tax を NOL 控除後に。`Financing!NOL balance` を実フォーミュラ化。
- [ ] **Step 2:** K4 が緑。
- [ ] **Step 3:** 既存テスト緑、BS バランス維持を確認。
- [ ] **Step 4: コミット**。

### Task 2.4: E — オフメカニクス行の抑制

**Files:**
- Modify: `source_plan_builder.py`（transaction revenue / GMV / net retention / deferred 行の生成ゲート L962-973 近傍）、必要なら `economic_kernel.py`

- [ ] **Step 1:** mechanic profile でオフメカニクス行を抑制（hardware/RaaS で transaction/take rate/GMV をゼロ化または非生成。マーケットプレイス証拠時のみ生成）。
- [ ] **Step 2:** K5 が緑。
- [ ] **Step 3:** 既存テスト緑、依存数式が壊れないこと（`Revenue Build` の合算）を確認。
- [ ] **Step 4: コミット**。

### Task 2.5: F — one-time/オンボーディング収益の YAML 化

**Files:**
- Modify: `economic_kernel.py`（`derive_source_facts_from_mapping` の入力キー、`_period_subtotal_revenue`）、`source_plan_builder.py`（Assumptions L19）

- [ ] **Step 1:** `onboarding_months`（または `one_time_revenue_per_unit_yen`）を入力キーに追加。未指定時のみ profile 既定 `price×3`、その際 evidence ラベルを `placeholder`。
- [ ] **Step 2:** 明示指定が反映され、未指定時は従来挙動になることをテスト。
- [ ] **Step 3:** 既存テスト緑。
- [ ] **Step 4: コミット**。

### Task 2.6: I — `audit_economic_coherence` 強化 ＋ J — YAML スキーマ文書化

**Files:**
- Modify: `economic_kernel.py`（`audit_economic_coherence`）
- Create: `skills/startup-financial-modeling/build/references/_input_schema.md`
- Modify: `skills/startup-financial-modeling/SKILL.md`

- [ ] **Step 1:** `audit_economic_coherence` に K1/K2/K4/K5 違反検出を追加。
- [ ] **Step 2:** K7（監査がこれらを検出する）が緑。
- [ ] **Step 3:** `_input_schema.md` に YAML 入力キー全列挙＋未指定時の profile 既定挙動。`SKILL.md` から参照を張る。
- [ ] **Step 4:** 全テスト緑＋代表ケース `--strict-audit` pass。
- [ ] **Step 5: コミット**。

### Task 2.7: Phase 2 レビュー

- [ ] `milestone-review` で Codex（カーネル diff）＋ Gemini（経済整合の別観点）＋ advisor（退行・忠実度）にレビュー。回答検証。反復（上限8）。`progress.md` 記録。

---

## Phase 3 — カーネル整合性 Tier 2（C3 Tier 2）

**完了条件:** B/D/G/H の追加 eval（K3/K6/K8 含む）緑。既存テスト全緑。反復上限 6。
**前提:** Phase 2 完了＋既存テスト全緑が確認できていること。

### Task 3.1: B — 全ファイナンス手段の equity サイジング/FCF 統合

**Files:** Modify: `economic_kernel.py`（`project_free_cash_flow`, `size_equity_rounds`, `derive_source_facts_from_mapping` の Step 移動）

- [ ] **Step 1:** K3 の失敗テストを追加。
- [ ] **Step 2:** lease/converts/grants/advances/secondary を FCF 投影と equity サイジングに統合。利息も付与。
- [ ] **Step 3:** K3 緑＋既存テスト全緑（TDD で慎重に）。
- [ ] **Step 4: コミット**。

### Task 3.2: D — debt/lease 約定弁済スケジュール

**Files:** Modify: `economic_kernel.py`, `source_plan_builder.py`（Capital Stack debt 残高）

- [ ] **Step 1:** 失敗テスト（残高＝累積drawn−累積repaid、利息は逓減残高基準）。
- [ ] **Step 2:** `debt_amortization` プリミティブを追加し実装。
- [ ] **Step 3:** 緑＋既存テスト全緑。
- [ ] **Step 4: コミット**。

### Task 3.3: G — 期央減価償却コンベンション

**Files:** Modify: `economic_kernel.py`（減価償却 L1562 近傍）、`source_plan_builder.py`（P&L D&A 式）

- [ ] **Step 1:** 失敗テスト（取得期は半期償却）。
- [ ] **Step 2:** `depreciation_convention` を実装（既定 half-year）。
- [ ] **Step 3:** 緑＋既存テスト全緑。
- [ ] **Step 4: コミット**。

### Task 3.4: H — governor 透明化 ＋ K6/K8

**Files:** Modify: `economic_kernel.py`（クランプ箇所、`audit_economic_coherence`）、`source_plan_builder.py`（Cost Build/Assumptions 注記行）

- [ ] **Step 1:** 失敗テスト K6（マテリアル収益の出所）/K8（粗利クランプ警告）。
- [ ] **Step 2:** Cost Build に「費目は粗利目標へ governor 再スケール」の注記行。範囲外 `target_gross_margin` を監査で警告化。
- [ ] **Step 3:** K6/K8 緑＋既存テスト全緑。
- [ ] **Step 4: コミット**。

### Task 3.5: 最終検証 ＋ Phase 3 レビュー

- [ ] 全テスト（`test_build_model.py`＋`test_economic_quality.py`）緑、全 eval（K1-K8）緑、代表 YAML で `--strict-audit` pass、soffice 再計算で `data_only` エラー 0。
- [ ] レンダリング検証: 代表モデルを PDF/PNG 化し、罫線・列幅・階層が設計どおりか目視。
- [ ] `milestone-review` で最終レビュー（advisor＋Codex＋Gemini）。回答検証。
- [ ] `progress.md` に最終結果（完了 / 要人間判断 / 反復上限）を記録。

---

## Self-Review（spec 照合）

- spec §2 C0 → Phase 0（Task 0.1-0.3）✓
- spec §2 C1（罫線/帯統一/列幅/階層/プロンプト）→ Phase 1（Task 1.1-1.5）✓
- spec §2 C2 研究 → Task 1.5 Step 4 で反映 ✓（研究は並列実行済み）
- spec §2 C3 Tier1（A/C/E/F/I/J）→ Phase 2（Task 2.2-2.6）✓
- spec §2 C3 Tier2（B/D/G/H）→ Phase 3（Task 3.1-3.4）✓
- spec §3 K1-K8 → Task 2.1（K1/K2/K4/K5/K7）、Task 3.1/3.4（K3/K6/K8）✓
- spec §4 完了条件 → 各 Phase 見出しに明記 ✓
- spec §5 反復上限 → 各 Phase 見出しに明記 ✓
- spec §6 実行モデル（自走/並列/レビュー/progress）→ 前提・各レビュータスク ✓
