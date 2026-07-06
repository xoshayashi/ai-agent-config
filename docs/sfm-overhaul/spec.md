# startup-financial-modeling 品質改修 ＋ milestone-review スキル新設 — 設計仕様

- 作成日: 2026-05-20
- 対象リポジトリ: `ai-agent-config`（`main` に直接コミット・PR/ブランチなし）
- 関連: `docs/sfm-overhaul/plan.md`（実装計画）, `docs/sfm-overhaul/progress.md`（自走進捗）

## 1. 決定（この仕様が支える判断）

`startup-financial-modeling` スキルが生成する投資家向け xlsx の (a) レイアウト/デザインの基礎品質と
(b) 経済カーネルの入力忠実度・整合性を、**今回のケースに個別最適化しない汎用構造**で底上げする。
あわせて、作業の節目で外部レビュアー（advisor / Codex CLI / Gemini CLI）へレビューをルーティング
する汎用スキル `milestone-review` を新設し、他スキルが「呼ぶだけ」で使えるようにする。

調査の根拠は本セッションの2エージェント調査レポート（デザインバグ／モデル品質）。

## 2. スコープと構成（4コンポーネント）

### C0 — 新スキル `milestone-review`（汎用・スタンドアロン）

作業の節目でレビューを適切なレビュアーへルーティングする汎用スキル。他スキルは1行で invoke する。

- `skills/milestone-review/SKILL.md` — 起動条件、ルーティング表、回答検証プロトコル、フロー
- `skills/milestone-review/references/_reviewer_routing.md` — レビュアー別の強み・適性・プロンプト構築規約
- `skills/milestone-review/scripts/route_review.py` — Codex/Gemini CLI を非対話で呼ぶ決定論的ヘルパー
  （タイムアウト、stdout/stderr 取得、終了コード、失敗時の縮退）
- `skills/milestone-review/tests/test_route_review.py` — スモークテスト

ルーティング方針（`_reviewer_routing.md` に明文化）:

| レビュアー | 性質 | 使う場面 | 呼び出し |
|---|---|---|---|
| advisor（ツール） | 本セッションの全 transcript を読む。深い推論 | 全文脈を要するマイルストーン判断（1回） | `advisor()` ツール |
| Codex CLI | 外部プロセス。渡したプロンプトのみ参照 | 特定 diff / コードロジックの実装妥当性。並列可 | `codex exec` |
| Gemini CLI | 外部プロセス。別観点・大規模 context | 横断的整合・別視点の反証 | `gemini -p` |
| self | 即時 | デザイン規律など機械的チェック | — |

各レビュアーへのプロンプトは**背景・対象・問いを明示して構築**する（外部CLIは文脈を持たないため
特に背景を厚く）。回答受領後は必ず (a) 主張に根拠があるか、(b) 一次証拠と矛盾しないか、
(c) 複数レビュアーが食い違う場合の裁定、(d) その回答に基づく次工程の予測が妥当か — を判定する。
盲目的採用も盲目的棄却も禁止。

**ブートストラップ二重チェック**: `milestone-review` は最初に作り、W1-W3 のレビューに使う前に、
`milestone-review` 自体を advisor + Codex + Gemini の3経路で手動実行し、各経路が正常応答を返し
回答検証ロジックが起動することを確認する。

### C1 — ワークブック・レイアウトの汎用化（デザイン基盤）

**中核原則（ユーザー指示）**: 列・幅・スパンの**固定値／ハードコードを撤廃**し、レイアウトを
「役割の意味論」と「実際のコンテンツ（テキスト位置・背景色）」から**汎用構造で動的に決定**する。
今回の不具合に個別対応するのではなく、汎用構造でコードが規律を強制する形にする。

対象不具合（調査で実証済み）と汎用的修正:

1. **罫線がテーブル途中で割れる（最重要）**: `source_plan_builder.py` の `_write_values` の
   bold 分岐が `accent_cols = [label_col, *period_cols]`（C・F-L のみ）で D・E を構造的に除外し、
   さらに `if cell.value is None: continue` で空セルを飛ばす。
   → 修正: `ib_format.py` に `apply_semantic_fill_span` と対をなす **`apply_semantic_border_span`**
   を新設。罫線スパンは、その行が属する**テーブルブロックを、行内のテキスト位置と背景色
   （セマンティック fill）から検出**して決定する。ハードコードの列範囲は使わない。空セルも
   ブロック内なら罫線対象。`_write_values` の罫線適用をこのヘルパーに置換。
2. **セクション帯と合計行の右端不一致**（帯=col3-13、合計=col3-12）:
   → 修正: 帯・合計・期間ヘッダのスパンを、すべて同一の「テーブルブロック検出」関数に統一。
3. **ラベル列が固定幅 54.0**（`COL_LABEL_WIDTH`）でオートフィットなし:
   → 修正: 列幅を**コンテンツ長連動**にする。全データ書込み後、各役割列について列内セル値の
   最大表示長（CJK=2幅換算）を測り、役割別 [min, max] で clamp して幅を設定する後処理を追加。
4. **階層インデント列が 1 本固定**（`hierarchy_cols=1` ハードコード）:
   → 修正: 階層深度をモデル構造から動的に算出し、必要本数のインデント列を生成。
   `label_col` 以降は自動で右シフト。列番号直書き箇所を点検し汎用化。

加えて、**プロンプト層**（`build/references/_layout_canonical.md`,
`_ib_workbook_design_system.md`）の文言を、逃げ道のない明示表現に強化する。
**コード層**で汎用構造として強制し、プロンプトとコードの両面で縛る。

C2（デザイン研究）の成果を本コンポーネントの参照文言・ルールに取り込む。

### C2 — デザイン・ベストプラクティス研究

IB/PE/VC/FP&A の財務モデル・スプレッドシートのデザイン標準（列幅・罫線・階層・カラー・フォント・
数値書式・構成・レンダリング体裁）を広く調査し、`_layout_canonical.md` /
`_ib_workbook_design_system.md` に汎用ルールとして反映する。研究は spec 承認待ちの間に並列
エージェントで実行済み／実行中。

### C3 — 経済カーネル整合性修正

**Tier 1（必達）**:

- A: ユーザー指定の `customers`（installed base）を経常収益の一次ドライバーにする。
  `churn_rate` 入力を `ending_units` のフリート churn に実際に効かせる
  （現状ハードコード `0.02+idx*0.005` は profile 既定としてのみ残す）。
- C: NOL（繰越欠損金）を税計算に実装。`taxable = max(0, ebt - nol_balance)`、
  `nol_balance` をロールフォワード。`Financing` シートの NOL 残高行を実フォーミュラに。
- E: mechanic profile でオフメカニクス行を抑制。hardware/RaaS プランで
  transaction revenue / take rate / GMV / net retention / deferred revenue を
  ゼロ化または非生成（マーケットプレイス証拠がある場合のみ生成）。
- F: one-time / オンボーディング収益を明示 YAML ドライバー化
  （`onboarding_months` または `one_time_revenue_per_unit_yen`）。未指定時のみ profile 既定
  `price×3` を適用し、その場合 evidence_status を `placeholder` とラベル。
- I: `audit_economic_coherence` に経済整合チェック（K1-K8 相当）を追加。
- J: `SKILL.md` または新規 `_input_schema.md` に YAML 入力スキーマ全キーを列挙し、
  未指定時の profile 既定挙動を併記。

**Tier 2（Tier 1 緑＋既存テスト全緑のあと、自走を継続して着手）**:

- B: 全ファイナンス手段（lease / converts / grants / customer advances / secondary）を
  equity 自動サイジングと FCF 投影に統合（現状 `debt_raise_yen` のみ反映）。
- D: debt / lease の約定弁済スケジュール（残高＝累積 drawn − 累積 repaid、利息は逓減残高基準）。
- G: 減価償却の期央（half-year）コンベンション。
- H: governor（粗利目標へのコストスタック逆算）の透明化。範囲外 `target_gross_margin` の
  無言クランプを警告化。

`build/evals/evals.json` に計算/ロジック検証 assertion を追加（K1-K8）。

## 3. eval 観点（K1-K8）

- K1 入力整合: 構造化入力の `customers[t]`（期末）が経常収益で実際に使われたフリート数と一致。
- K2 churn honor: `churn_rate` を変えるとフリートロールフォワードと終端 ARR が変わる。
- K4 NOL: 累計 cash tax ≤ tax_rate × max(0, 累計税前利益)。欠損金期間に課税が出ない。
- K5 オフメカニクス抑制: hardware/RaaS プランで transaction revenue / take rate / GMV がゼロ。
- K7 監査網羅性: `audit_economic_coherence` が K1/K2/K4/K5 違反を検出できる（監査のメタ eval）。
- K3 ファイナンス整合 / K6 マテリアル収益の出所 / K8 粗利クランプ警告 は Tier 2 と同時に追加。

## 4. 完了条件（コンポーネント別・観測可能）

- **C0**: `milestone-review` を3経路（advisor/Codex/Gemini）で各1回実行し正常応答＋回答検証起動。
  `test_route_review.py` 緑。
- **C1**: openpyxl 検証で全シートの罫線スパン違反 0（行が属するテーブルブロック全幅に
  途切れなく適用、D・E 等の空/中間セルもブロック内なら罫線あり）。`apply_semantic_border_span`
  ヘルパー存在。固定列幅のハードコードが撤廃されコンテンツ連動になっている。
  既存 `test_build_model.py` の strict-audit / 設計監査が全緑。
- **C3 Tier 1**: 新規 eval K1/K2/K4/K5/K7 が全緑。`test_build_model.py` ＋
  `test_economic_quality.py` が全緑。`build_model.py --strict-audit` が代表ケースで pass。
- **C3 Tier 2**: B/D/G/H 各々の追加 eval（K3/K6/K8 含む）が緑。既存テスト全緑。

## 5. 反復上限（自走の停止境界）

- C0: 4 反復。C1: 6 反復。C3 Tier 1: 8 反復。C3 Tier 2: 6 反復。
- 上限超過、または同一失敗の根本原因がコード外（環境・認証等）にある場合は、
  `docs/sfm-overhaul/progress.md` に状況と未解決の問いを記録し、ループを停止して人へ戻す。
- 完了・要人間判断・反復上限到達 は区別して progress.md に記録する。

## 6. 実行モデル

- spec / plan 承認後は**完全自律**で `/loop`（自己ペース）実行。
- 各コンポーネントを独立タスクとして可能な限り並列エージェントへ委託。
- 各コンポーネント完了時に `milestone-review` で実レビュー（C0 は自己 dogfooding 前にブート
  ストラップ二重チェック）。レビュー結果の妥当性を判定してから次へ進む。
- 進捗・ブロッカー・各ループの結論は `progress.md` に逐次記録（fresh context が復帰可能なように）。
- `ai-agent-config` の `main` に直接コミット（PR/ブランチなし）。コミットは
  コンポーネント／論理単位で分割し、メッセージ末尾に Co-Authored-By を付す。

## 7. 既に解決済みの人間判断項目

- 新スキル名: `milestone-review`。
- 罫線スコープ: 列固定をやめ、テキスト位置と背景色から汎用構造で動的決定（B/C の固定二択にしない）。
  他の列固定箇所も同様に汎用化。
- Tier 2: Tier 1 完了後に自走継続で着手。
- ATOM 納品物: 触れない（スキル改修に専念）。本改修で見つかった bug は ATOM モデルにも乗るが、
  差し替えはしない。

## 8. スコープ外

- 今回納品済みの ATOM モデル成果物（`ATOM_収支計画.xlsx` 等）の修正・差し替え。
- `equity-story` ほか姉妹スキルの改修（`milestone-review` の呼び出し線追加を除く）。
- 既存テストの弱体化・削除（完了条件はコード側を直して満たす。テストを緩めない）。

## 9. リスクと留意

- C1 の階層列動的化・列番号汎用化は影響範囲が広い。列番号直書き箇所（特殊レイアウトシート）の
  全点検が必要。段階導入し、各ステップで既存テストの緑を確認。
- C3 Tier 2 の `project_free_cash_flow` 引数増設は既存テストを壊しやすい。TDD で進める。
- 外部 CLI（codex/gemini）はネットワーク・認証に依存。`route_review.py` は失敗時に縮退し、
  ループを止めない設計にする。
