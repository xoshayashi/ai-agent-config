# 設計書: マルチLLMによる開発タスク自動化

## 1. 目的

本設計は、`ai-agent-config` の現在の Hook / Skill / Instructions 基盤を前提に、**複数 LLM を役割分担させながら、開発タスクをより自律的かつ安全に前進させる仕組み**を定義する。

狙いは単純な「複数モデルを同時に回すこと」ではない。狙うのは次の 4 点である。

1. **品質向上**  
   単独モデルでは見落としやすい仕様漏れ、検証不足、過剰実装を減らす。
2. **レイテンシとコストの抑制**  
   毎ターン全モデルを回すのではなく、必要な境界でだけ他モデルを呼ぶ。
3. **状態管理の単純化**  
   実行責任者を 1 つに絞り、分岐や再入で壊れにくい設計にする。
4. **運用可能性の確保**  
   個人環境でもチーム環境でも、Hook の競合・無限ループ・設定破損を起こしにくくする。

## 2. エグゼクティブサマリー

このコードベースの現状は、すでに **Codex を実行ハブに据えたマルチLLMオーケストレーションの最小実用形** になっている。

- **入力前**: `peer-prompt-refinement` Skill が必要時のみ別 LLM でプロンプトを洗練
- **仕様フェーズ**: `multillm_orchestrator.py` が Codex に仕様起草をさせ、`[[SPEC_DONE]]` を境に Claude がレビュー
- **実装フェーズ**: Codex が実装し、`Stop` ごとに Claude が次ステップを提案
- **検証フェーズ**: `[[IMPLEMENTATION_DONE]]` 後は直ちに停止せず、検証・差分確認・セルフレビューへ遷移
- **定期批判**: Gemini が simplification / spec drift を観点に定期レビュー
- **別モード**: `response_strategy_bridge.py` は orchestration とは別に、回答後の 1 ターン継続を補助する

この方向性は妥当である。特に、**「Codex-first / boundary review / periodic critique」** という現在の分離は、毎ターン多モデルを回す方式よりも、実装責任・状態遷移・コストの面で優れている。

一方で、今の実装はまだ **開発タスク自動化の基盤** にとどまる。今後は次の不足を埋めるとよい。

- 仕様の品質判定基準がまだテキスト中心で、テスト・差分・PR 状態との結合が弱い
- Claude / Gemini の出力を「提案」ではなく「検証済み制御信号」にする設計が薄い
- タスク完了判定が `[[..._DONE]]` キーワード中心で、特に `[[IMPLEMENTATION_DONE]]` が終了扱いに寄りすぎると早期停止を招く
- 実装後のテスト、PR 作成、レビュー反映、マージ条件までを一気通貫で結ぶ制御面が未整備

## 3. 現状コードベース分析

### 3.1 主要コンポーネント

#### A. `hooks/scripts/multillm_orchestrator.py`

現在の中核。役割は次の通り。

- `UserPromptSubmit` で **Codex に仕様起草ブリーフを注入**
- `Stop` で Codex の応答を見て、`[[SPEC_DONE]]` が出たら、または後続草案が十分構造化されていれば **Claude に仕様レビュー**
- 仕様承認後は `phase=implementation` に遷移
- 実装中は **Claude の次ステップ提案** と **Gemini の定期批判** を使って継続判断
- ローカル状態を `~/.llm-config/orchestration/<session>.json` に保持

設計上の良い点:

- **単一実行ハブ**: 実行責任者が Codex に固定される
- **明示的な phase 管理**: `spec_authoring -> implementation -> verification -> done`
- **ガードあり**: 再入防止、継続回数上限、同一プロンプト繰り返し検知
- **fail-open 基本**: peer CLI 不調で本体を壊しにくい

注意点:

- state path はセッション ID の置換ベースで、理論上衝突余地がある
- `AI_AGENT_ORCHESTRATOR_TIMEOUT_SECONDS` は現状 `maximum=60`
- 仕様・実装・検証の完了判定はまだキーワード依存が強い
- pre-implementation lock は advisory であり、Hook が phase ベースで編集やコマンド実行を強制停止するわけではない
- 起動条件は heuristic であり、グローバル ON でも複雑タスク寄りの prompt に絞って起動するのが実用的

#### B. `skills/peer-prompt-refinement`

入力前に他 LLM を使ってプロンプトを洗練する Skill。

- Codex -> Claude
- Claude -> Codex
- Gemini -> Claude

主な性質:

- **必要時のみ使う**
- fail-closed 寄りの運用にしやすい
- transcript 抜粋を添付しつつ secret-like 値を redact
- 単純な雑談や status 的プロンプトは skip

設計上の意味:

- 本体タスク前の **要求明確化** と **見落とし補完**
- ただし毎回 peer CLI を新規起動するため、待機時間は無視できない

#### C. `hooks/scripts/response_strategy_bridge.py`

回答後に「もう 1 ターン回すべきか」を判定する Hook。

- Claude / Codex -> Gemini
- Gemini -> Codex
- `ollama` もオプション対応

主な性質:

- **既定 OFF**
- After-response の補助制御であり、実行ハブではない
- peer 評価スキーマ上は `continue` / `allow_stop` / `needs_human` を扱えるが、実際の Hook 出力は継続するか、メッセージだけ返すかが中心
- 低価値レスポンスは skip し、誤作動を抑える

設計上の意味:

- 主ループを壊さずに、**不足作業の一押し** を自動化できる
- ただし orchestration と同時に強く使うと、責任境界が曖昧になりやすい

### 3.2 現状コードから読み取れる重要制約

1. **Codex では orchestration と response strategy は `Stop` 上で同時主役にしない前提**  
   現在の hook 設定でも orchestration 有効時は response strategy を抑止する方向になっており、将来設計でもこの分離を守るべきである。
2. **Gemini / Claude 側の Hook は reviewer 補助が中心**  
   実行主体ではなく、回答後批評・仕様レビュー補助として使うのが今の設計線である。

#### D. Hook 設定ファイル

- `hooks/codex/hooks.json`
- `hooks/claude/settings.json`
- `hooks/gemini/settings.json`

ここでは次が重要である。

- **Codex のみ orchestration を持つ**
- response strategy は各 CLI に対して登録される
- prompt refinement は Hook ではなく Skill として扱う
- `safe_delete_guard.py` は既定 ON で共通安全策として機能

#### E. 運用・配布レイヤー

- `scripts/setup.sh`
- `scripts/health-check.sh`
- `instructions/AI_AGENT_INSTRUCTIONS.md`
- `instructions/HOOKS.md`
- `README.md`
- `setup.md`

この層は単なる補助ではなく、**実運用上の制御面** である。

- どの Hook が既定 ON / OFF か
- どの env var で有効化するか
- どの CLI に何を配布するか
- 更新や health-check をどう回すか

がここで固定されているため、設計書でも制御面として扱うべきである。

## 4. 現状アーキテクチャの評価

### 4.1 なぜ Codex ハブ方式が妥当か

現在の最重要設計判断は、**「複数 LLM が対等に実行する」のではなく、Codex を実行ハブに固定していること** である。

これは実務的に正しい。

理由:

1. **状態の出入り口が 1 つになる**  
   Hook の stop / continue / block が 1 本のイベント列に集約される。
2. **ツール実行責任が 1 つになる**  
   shell, patch, git, test の主体が固定される。
3. **他モデルを reviewer / critic に寄せやすい**  
   レビューと実行を分離できる。
4. **無限ループの切り分けがしやすい**  
   「誰が次ターンを発火させたか」が追いやすい。

研究的にも、マルチエージェントが常に有利とは限らない。  
`Agentless` は、複雑なエージェント構成よりも **単純な構造が性能とコストで強いケース** を示した。よって本設計でも、**役割追加は明確な勝ち筋がある箇所だけ** に絞るべきである。

### 4.2 現状の強み

- **phase separation が明確**  
  仕様と実装を同一ループに混ぜていない
- **review boundary が自然**  
  `[[SPEC_DONE]]` という明示イベントを Claude review gate に使える
- **latency-aware**  
  毎プロンプトで Claude -> Gemini -> Claude を回す旧案より軽い
- **ops-friendly**  
  既定 OFF の設計なので、導入直後に全員の CLI を重くしない

### 4.3 現状の弱み

#### A. 完了判定がテキスト寄り

`[[SPEC_DONE]]`, `[[IMPLEMENTATION_DONE]]`, `[[VERIFICATION_DONE]]`, `[[TASK_DONE]]` は分かりやすいが、  
**実際にテストが通っているか、PR が整っているか、差分が妥当か** とは独立である。

#### B. reviewer 出力の契約がまだ弱い

Claude / Gemini には JSON 返却を求めているが、  
その JSON はまだ **「提案」寄り** で、**厳密な machine-checked protocol** にはなっていない。

#### C. 実装後の downstream automation が薄い

今の流れは主に:

- 仕様作成
- 実装継続
- stop / continue 判定

までであり、

- テスト計画生成
- テスト実行の強制
- PR 生成
- review 取得
- review 反映
- merge readiness 判定

までは 1 本に繋がっていない。

#### D. 長期タスクのメモリ運用はローカル state 中心

`~/.llm-config/orchestration` の JSON state は実装上十分だが、

- 複数セッション横断
- 外部レビューとの同期
- 監査可能な履歴

には弱い。

## 5. To-Be アーキテクチャ

### 5.1 基本方針

目標アーキテクチャは **Hub-and-Review Mesh** とする。

- **Codex**: 実行ハブ兼 state owner
- **Claude**: 仕様レビューと実装ガイダンスの primary reviewer
- **Gemini**: 単純化・spec drift・代替案の critic

重要なのは、これを **対等分散実行** にしないことである。  
分散させるのは判断観点であり、**最終実行主体は常に 1 つ** に保つ。

### 5.3 明示的に避けるべき競合構成

次の構成は避ける。

1. **Codex orchestration と Codex response strategy の常時同時有効化**  
   どちらも stop 後継続判断を扱うため、継続責務が二重化する。
2. **Codex orchestration 中に、入力前 peer 改善を Hook で常時強制する構成**  
   すべての入力前に peer CLI を待たせると、軽量タスクで体験が著しく悪化する。
3. **複数 LLM がそれぞれ continuation prompt を直接返す構成**  
   状態遷移責務が分散し、どの指示が authoritative かが不明確になる。

### 5.2 フェーズ設計

#### Phase 0. Intake

- User prompt 受領
- 必要時のみ `peer-prompt-refinement` Skill
- simple prompt は skip
- orchestration は常時すべての prompt に発火させず、明示ワード・複雑タスク・長文実装依頼などの heuristic で起動

**出口条件**  
Codex が着手可能な要求文になっていること

#### Phase 1. Specification Authoring

- Codex が repo / docs / instructions / hooks を読んで仕様草案作成
- `[[SPEC_DONE]]` までは実装しないことを強く促す

**出口条件**  
仕様に最低限以下があること:

- 目的
- scope / non-goals
- acceptance criteria
- constraints
- risks
- implementation plan

#### Phase 2. Specification Review Gate

- `Stop` で Claude がレビュー
- status は `draft | done`
- 現行実装では、`[[SPEC_DONE]]` がある場合に加えて、十分に構造化された仕様草案に対して deterministic fallback review を走らせてもよい

Claude が見るべき観点:

- 要求の取り違えがないか
- 過剰拘束や過少指定がないか
- 実装前に潰すべきリスクがないか
- 受け入れ条件が検証可能か

Gemini はこの phase に常時入れない。  
ここで reviewer を増やしすぎるとレイテンシが急増するため、**Claude を primary gate** に固定する。

#### Phase 3. Implementation Loop

- Codex が step-by-step で実装
- `Stop` ごとに Claude が次ステップ要否を判定
- 3 ターンごとなどで Gemini が critic として参加
- `[[IMPLEMENTATION_DONE]]` は **終了キーワードではなく、verification への遷移キーワード** として扱う

Gemini の役割:

- もっと単純な方法はないか
- 仕様から逸脱していないか
- 実装の重さが disproportionate になっていないか

#### Phase 4. Verification Loop

ここは最終終了前の必須フェーズとする。

`[[IMPLEMENTATION_DONE]]` が出たら、Codex はここへ遷移して少なくとも次を行う。

1. テスト実行または既存検証コマンドの確認
2. 失敗時の再修正
3. 差分サマリー生成
4. self-review
5. peer review

ここでは **`[[VERIFICATION_DONE]]`** を、検証とセルフレビューが完了した明示シグナルとして使う。  
**最終停止は `[[VERIFICATION_DONE]]` と `[[TASK_DONE]]` の両方が揃った時だけ** 許可する。

#### Phase 5. PR / Review / Merge Readiness（Target Architecture）

将来的にはここまで orchestrate すべきである。  
**現行コードが担保しているのは、spec review gate と implementation continuation まで**であり、このフェーズはまだ roadmap 領域である。

- PR 作成
- Claude / Codex review 取得
- actionable comment の自動反映
- stale thread 判定
- merge readiness 判定

## 6. 設計原則

### 原則 1. 実行主体は 1 つ

複数 LLM は使うが、**実ファイル変更・コマンド実行・状態遷移を担当する主体は 1 つ** に固定する。

### 原則 2. 他モデルは boundary reviewer と critic に寄せる

他モデルを毎ターン executor にしない。  
使う場所は:

- 仕様承認境界
- 実装継続判断
- 単純化批判
- 完了前レビュー

### 原則 3. Hook は deterministic control plane、LLM は advisory plane

Hook 自体は deterministic であるべき。  
LLM は JSON で制御信号候補を返すが、**最終的な state machine は Hook コード側が持つ**。

### 原則 3.5. reviewer とのインターフェースは構造化データ優先

reviewer からの返却は将来的に次へ寄せる。

- 人間向けの長文講評より **短い構造化 JSON**
- `status`, `action`, `confidence`, `risk_level`, `needs_human` などの固定キー
- 自由文は `reason` や `notes` に限定

これにより、プロンプトインジェクションや解釈ブレに対する耐性を上げる。

### 原則 4. 完了判定はキーワードと実検証の二重化

`[[..._DONE]]` は維持してよいが、それだけでは足りない。特に `[[IMPLEMENTATION_DONE]]` は「ここで止まってよい」ではなく「ここから verification に入れ」である。  
次を合わせて見るべき:

- test exit code
- changed files count / shape
- pending review comments
- verification checklist

### 原則 5. fail-open / fail-closed を phase ごとに分ける

- **Skillベースの prompt refinement** は fail-closed 寄りでもよい
- **orchestration peer review** は基本 fail-open
- **destructive or merge-boundary operations** は fail-closed 寄り

## 7. 詳細設計

### 7.1 状態モデル

最低限の state:

- `phase`
- `original_prompt`
- `spec_markdown`
- `implementation_brief`
- `next_step_prompt_for_codex`
- `spec_revision_count`
- `implementation_turn`
- `verification_turn`
- `continuation_count`
- `same_prompt_count`

将来追加候補:

- `verification_status`
- `test_summary`
- `review_status`
- `pr_number`
- `last_artifacts`

### 7.2 制御イベント

現在の実装に沿う主要イベント:

- `SessionStart`
- `UserPromptSubmit`
- `Stop`
- Claude では `SubagentStop`
- Gemini では `BeforeTool` / `AfterAgent`

設計上の原則として、**状態遷移を起こすイベントは増やしすぎない**。  
とくに Codex 側は `UserPromptSubmit` と `Stop` を中心に保つのがよい。

### 7.3 コンテキスト共有

共有するのは次に限る。

- original prompt
- current spec
- latest response
- transcript tail
- current cwd / model / phase

共有しすぎない理由:

- レイテンシ増大
- prompt injection 面の悪化
- reviewer の焦点ぼけ

そのため transcript は全文ではなく **tail-only + redaction** を維持する。

### 7.4 reviewer プロトコル

今後は reviewer 出力を次のように整理するとよい。  
なお、**現行の orchestrator が実際に読むキーはこれより少ない**。

- `status`
- `action`
- `confidence`
- `risk_level`
- `needs_human`
- `next_prompt_for_codex`
- `verification_request`

特に `confidence` と `risk_level` を入れると、
**「続けるべきか」だけでなく「どの強さで続けるか」** を制御しやすい。

### 7.5 Human-in-the-loop 条件

自動継続を止める条件を明確に持つ。

- 仕様変更がユーザー意図を越える
- destructive operation が広範囲
- security / compliance / secrets 周り
- reviewer 間で判断が割れる
- same-prompt / continuation 上限に到達

推奨トリガー一覧:

1. 破壊的変更がリポジトリ全体または多数ファイルに及ぶ
2. secret / auth / 権限 / 本番接続 / 課金影響がある
3. reviewer が `needs_human=true` を返す
4. 同一 continuation prompt が 3 回以上繰り返される
5. 検証コマンドが見つからない、または複数候補で信頼度が低い
6. 仕様変更が original prompt の境界を越える

ただし、これらは **目標とする HITL 条件** であり、現行実装が直接 `needs_human` を受け取って停止するところまではまだ入っていない。  
現状の stop 条件は、主に **continuation cap / same-prompt cap / final completion keyword pair / reviewer の continue 不採用** である。
verification phase にも独立した turn cap を持たせ、検証フェーズだけが無限継続しないようにする。

### 7.6 Verification Loop の主体

Verification Loop の主体は **Codex** とする。  
Orchestrator は verifier 自体ではなく、**Codex に検証指示を返す制御者** として振る舞う。

分担:

- **Codex**: テスト発見、実行、失敗解析、修正、再実行
- **Claude**: 次の検証ステップ提案、検証漏れチェック
- **Gemini**: 過剰検証や spec drift の批判
- **Orchestrator**: phase と continuation の管理

### 7.7 検証コマンド発見ロジック

任意プロジェクトでの verification は、次の順で候補を推定する。

1. repo 直下の既知ファイルから推定  
   `package.json`, `pytest.ini`, `pyproject.toml`, `Makefile`, `justfile`, `cargo.toml`, CI workflow
2. README / setup docs / contributing docs から既定コマンドを抽出
3. lockfile と test ディレクトリ構造から補助推定
4. 候補が複数ある場合は **信頼度** を付与して最上位から試す

信頼度の例:

- 高: `package.json` の `test` script, `make test`, CI で実際に使われるコマンド
- 中: フレームワーク標準 (`pytest`, `npm test`) だが repo 明示は弱い
- 低: ディレクトリ名や依存関係からの推測のみ

低信頼しかない場合は Human-in-the-loop に倒す。

## 8. 実装ロードマップ

### Step 1. 現在方式の安定化

- state path の衝突耐性改善
- verification status の state 追加
- review protocol の JSON schema 明確化
- timeout cap と outer timeout の整合整理

### Step 2. Verification Loop 追加

- repo ごとの検証コマンド推定
- 実行結果の要約
- failure -> repair の 1 サイクル自動化

### Step 3. PR Automation 追加

- PR 作成
- review 取得
- actionable feedback 抽出
- auto-fix

### Step 4. Observability 追加

- orchestration event log
- task phase metrics
- peer call success / timeout 率
- human handoff の発生条件集計

## 9. 推奨事項

### 今すぐ採用すべき

1. **Codex hub 方式は維持**
2. **仕様レビューは Claude 1st gate のまま**
3. **Gemini は periodic critic に限定**
4. **verification loop を次の主開発対象にする**
5. **PR / review automation は verification loop の後に載せる**

### 採用しない方がよい

1. 毎ターン複数 LLM を対等に回す常時多重ループ
2. reviewer が直接コード編集主体になる設計
3. 完了判定をキーワードだけに依存する設計
4. 1 つの Hook に実行・レビュー・PR 制御を全部詰め込む設計

## 10. 根拠と参照

### 一次情報

- OpenAI Codex Hooks  
  <https://developers.openai.com/codex/hooks>
- Claude Code Hooks reference  
  <https://code.claude.com/docs/en/hooks>
- Gemini CLI Hooks reference  
  <https://geminicli.com/docs/hooks/reference/>

### 研究・技術文献

- Agentless: Demystifying LLM-based Software Engineering Agents  
  <https://arxiv.org/abs/2407.01489>
- LLMs Working in Harmony: A Survey on the Technological Aspects of Building Effective LLM-Based Multi Agent Systems  
  <https://arxiv.org/abs/2504.01963>
- MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents  
  <https://aclanthology.org/2025.acl-long.421/>

## 11. 最終結論

このコードベースは、すでに **「複数 LLM を安全に使うための最小実用設計」** を持っている。  
特に、**Codex を実行ハブに固定し、Claude を review gate、Gemini を critic に寄せた構図** は、そのまま中核設計として伸ばしてよい。

次に進むべき重点は、モデル数を増やすことではない。  
**仕様 -> 実装 -> 検証 -> PR / Review** を一続きの state machine として強くすること** が本命である。**

その意味で、本設計の次フェーズは **Verification Loop の実装** と **PR / Review 自動化の接続** である。
