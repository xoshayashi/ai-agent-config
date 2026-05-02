# Audit A: Cross-reference Consistency

> Scope: 14 ファイル (合計 24,681 行) の reference corpus 内部の整合性監査。WebSearch なし、内部 cross-reference のみ評価。
> 対象: `skills/startup-financial-modeling/references/{00..11_*}.md`
> 監査者: Claude (Opus 4.7 1M context), 2026-05-01

## Summary

- **Total issues found**: 92
- **Critical**: 6 (deal-breaker, fix immediately)
- **High**: 24 (impacts model correctness)
- **Medium**: 38 (style / consistency)
- **Low**: 24 (cosmetic / stylistic)

監査軸: (1) 定義の矛盾、(2) 数式の矛盾、(3) ベンチマーク値の矛盾、(4) 投資判断閾値の矛盾、(5) 用語の矛盾、(6) 出典の矛盾、(7) 構造的矛盾、(8) 数値整合性、(9) 日本語表記揺れ。

ファイル略号:
- `00` = `00_design_guidelines.md`
- `01a` = `01a_modeling_standards.md`
- `01b` = `01b_integrity_and_anti_patterns.md`
- `02` = `02_saas_metrics.md`
- `03` = `03_business_models.md`
- `04a` = `04a_convertible_and_terms.md`
- `04b` = `04b_cap_table_mechanics.md`
- `05` = `05_valuation_wacc.md`
- `06` = `06_three_statement.md`
- `07` = `07_japan_specifics.md`
- `08` = `08_investment_thesis.md`
- `09` = `09_market_sizing.md`
- `10` = `10_modeling_craft.md`
- `11` = `11_debt_financing.md`

---

## Critical Issues
### A-C-001: Hard input の色 — `#0000FF` (Pure Blue) と `#004F49` (Primary deep, teal/green) で衝突
- **Files involved**: `00_design_guidelines.md` L82, L321, L328, L441, L2038 / `01a_modeling_standards.md` L481, L1156 / `01b_integrity_and_anti_patterns.md` L675, L1170
- **Inconsistency**: 00 と 01a は IB 機能色の正本として **Hard input = `#0000FF` (青、RGB 0,0,255)** を全文書で繰り返し定める (例: 00 §3.1 表、原則 3.1)。一方 01b §6 (L675) は色凡例の例示で `Blue text Hard-coded input (#004F49 primary deep)` と明記し、§A.6 チェックリスト L1170 でも `Input セルは青文字 (#004F49 等)` と書く。`#004F49` は Act DESIGN.md の Primary deep (teal/green) であって青ではない。
- **Impact**: モデル生成時に input セルが #004F49 で塗られると IB 慣習色 (色 = audit 機能) が完全に崩れる。実装が 01b 側を採用すれば、レビュアは「これは青じゃない、cross-sheet link?」と読み違える。`scripts/build_model.py` がどちらを参照するか不明な状態は致命的。
- **Recommendation**: 機能色 (Hard input/Formula/Cross-sheet/External) は 00 §3.1 + 01a §4.1 の **`#0000FF` を絶対正本**として固定。01b の `#004F49` 記述は `「装飾色 (Cover タブ・section header) のみで使う Act ブランド色であり、本文の機能色 (Hard input) には使用しない」` と書き換える。ブランド色と機能色の絶対分離原則 (00 §3.7) を 01b 内でも明示する。

### A-C-002: Cover シートの tab color が「黒」(01a) と「Primary deep `#004F49`」(01b) で矛盾
- **Files involved**: `01a_modeling_standards.md` L701, L738 / `01b_integrity_and_anti_patterns.md` L541, L1160
- **Inconsistency**: 01a §5.1 表で Cover の tab color を **黒** とし、§5.3 で `黒 | Cover (権威)` と再掲。01b §3.1 (L541) は「タブ色は Primary deep (`#004F49`)」、§A.6 (L1160) は「Cover=Primary deep」と書く。さらに 00 §6.2 系の `Sheet tab color: Cover=Navy` (L601) も加わり 3 通りある。
- **Impact**: `scripts/build_model.py` が xlsx 生成時にどの色を tab に塗るかが不確定。レビュアが複数モデルで色違いを目撃すれば「テンプレ未統一」と判定。
- **Recommendation**: 01a を正本として **Cover = 黒 (`#000000` または濃い navy `#1F3A66`)**で統一。01b §3.1 の Primary deep 記述は削除または「Surface 色 + Ink テキスト」へ変更。あわせて 00 L601 の "Cover=Navy" も `#1F3A66` で 01a と整合させる。

### A-C-003: Discount Rate 定義の混乱 — 04a 内部で同一概念が `d` (例 0.20) と `Discount Rate` (例 0.80) の二系統で並走
- **Files involved**: `04a_convertible_and_terms.md` L155-160, L162, L371, L391, L396, L429, L554, L578, L589, L604
- **Inconsistency**: §2.3.2 (L155-160) では `Conversion Price = Series A PPS × (1 - d)` で `d` = discount rate (0.20 = 20%)。同じ §2.3.2 L162 で「**YC SAFE は "Discount Rate = (1 - 割引率)" で定義 (例: 80%)** → conversion price = SAFE 価格 × Discount Rate」と注記。J-KISS §3.4 (L371, L396) では `Discount Rate = 80%` (= 20% off)、`行使価額 = ... × Discount Rate` (引き算なし)。一方 §6.4 系 (L578, L589, L604) では `Discount Rate = 15〜25% off`、`Series A PPS × (1 - Discount Rate)`、`Discount Rate = 20%` と定義が再反転。同一ドキュメント内で `Discount Rate` が **(a) 割引額そのもの (0.20)** と **(b) 1 − 割引額 (0.80)** の両義で使われている。
- **Impact**: SAFE / J-KISS の conversion price 計算式を読み違えれば、株式数が **4 倍** ずれる (例: $300K / $1.20 = 250K 株 vs $300K / $0.30 = 1M 株)。Cap table 全体が崩壊。投資家持分の希薄化計算が壊れ、実投資家との衝突に直結。
- **Recommendation**: 04a 全体で 1 つの定義に統一。本書の用語表 (§1.3 商品横断比較表) と §2-§6 を相互整合させる。推奨: **`Discount Rate` = 割引率そのもの (例 0.20)** とし、計算式は常に **`× (1 − Discount Rate)`** に統一 (Wall Street Prep / NVCA 標準)。L162 の「YC は (1-割引) で定義」のような注釈は本書の正本式から外し、別表の「契約書での表記揺れ」に切り出す。

### A-C-004: 01a の self-reference rot — 存在しないファイルへの参照と章の重複・空白
- **Files involved**: `01a_modeling_standards.md` L4, L1231 / `01b_integrity_and_anti_patterns.md` L3, L1275
- **Inconsistency**:
  (a) 01a 冒頭 L4 と末尾 L1231 が「別エージェント `01b_*`, `01c_*`」を参照するが、references/ 配下に **`01c_*` ファイルは存在しない** (`01a` と `01b` の 2 本のみ)。
  (b) 01b L3 と L1275 が **`01_modeling_principles.md`** を参照するが、これは旧名で現在のファイル名は **`01a_modeling_standards.md`**。
  (c) 01a 自身が章番号 §4 / §6 / §7 / §9 / §10 を **2 回ずつ** 含む (L473 / L687 / L1037 / L1043 / L1235 などに `本章は次のコミットで追記` の placeholder が残存)。実体のある §4 (L473〜) と stub の §4 (L687) が共存。
- **Impact**: 読者が `01c` を探して時間を消費。01b → 01a の cross-link が壊れ、新規メンテ者が「フロント工程の正本」を見失う。01a 内の章番号衝突は markdown TOC や footnote 参照を壊す可能性大。Skill 配信時にレビュアの信頼を即座に損なう。
- **Recommendation**:
  (1) 01a L4, L1231 を「別ファイル `01b_integrity_and_anti_patterns.md` を参照。`01c` は廃止」に書き換え。
  (2) 01b L3, L1275 の `01_modeling_principles.md` を `01a_modeling_standards.md` に置換 (replace_all 可)。
  (3) 01a の重複章 (placeholder stub) を削除し、TOC を最終形に整える。

### A-C-005: Snowflake の NRR 数値が同一 corpus 内で 131% / 150% / 178% の 3 通り
- **Files involved**: `02_saas_metrics.md` L348, L1411 / `10_modeling_craft.md` L219, L221, L225, L1276
- **Inconsistency**: 02 §3.3 表 L348 は `Snowflake | 131% (FY24), 127% (FY25 Q2) | 出典: Snowflake 10-Q` と明示。同じ 02 §11.2 L1411 は `Snowflake は一時 NRR 150%+`。10 §2.3 の悪い例文 L219 は `Snowflake は NRR 178% だった`、L225 は「Snowflake 178%」、L1276 maxim も「Snowflake の NRR 178%」。
- **Impact**: 同一企業の同一指標が 3 通りで提示されれば、benchmark calibration の Tier 2 (10 §1.1) として参照できなくなる。Skill 出力で 178% を base に置く誤用を誘発し、creator バイアス検出 (10 §2.2) のクロスチェックが効かない。
- **Recommendation**: Snowflake の歴史的ピーク (FY22 に 178%、IPO 直後) と直近 (FY25 Q2 に 127%) は **時点付きで併記**し、単一値として書かない。10 §2.3 の例文を「Snowflake は IPO 直後に NRR 178% を記録 (FY22)、直近では 127% (FY25 Q2、出典: Snowflake 10-Q FY25Q2)」に書き換え。02 §11.2 の `150%+` は時点不明のため削除または時点付きに修正。

### A-C-006: シート命名規約の二系統並走 — `01a` の `00_Cover/...11_PL/12_BS` 接頭辞 vs `06`/`11` の素朴名 `IS/BS/CFS/DebtSchedule/SanityChecks`
- **Files involved**: `01a_modeling_standards.md` L699-720, L728, L1121 / `06_three_statement.md` L5, L14, L807, L1234, L1270 / `11_debt_financing.md` L5, L852
- **Inconsistency**: 01a §5.1 はスタートアップ向けシート命名の **正本** として `00_Cover` / `01_Control` / `02_Time` / `03_Assumptions` / ... / `11_PL` / `12_BS` / `13_CF` / `98_Checks` / `99_Glossary` を表で固定 (L699-720)、§5.2 命名規則・§9.1 統合チェックでも繰り返し強制 (L1121 `Sheet 順が ... 98_Checks → 99_Glossary`)。一方 06 (L5, L14, L1234) は **`IS / BS / CFS / Schedules / SanityChecks`** を生成物として宣言、11 (L5, L852) は **`DebtSchedule`** を生成物として宣言。01a 規約に従えば PL は `11_PL`、BS は `12_BS`、Checks は `98_Checks` のはずだが、06/11 の生成物は接頭辞ナシかつ綴りも違う (`SanityChecks` ≠ `98_Checks`、`DebtSchedule` は対応シート不明)。
- **Impact**: `scripts/build_model.py` が複数 reference を読んでシート名を決める際、矛盾するソースのどれを採るか定まらない。生成された xlsx が 01a §9.1 のチェックリストを通らない (`Sheet 順が 00_Cover → ... → 98_Checks` を機械で検査すれば fail)。06/11 を真とすれば、01a §5.1 の表全体が無意味化。
- **Recommendation**: 01a §5.1 を **唯一の正本**として固定。06 と 11 の `想定アウトプット` 行を以下に書き換え:
  - 06 L5: `xlsx の 11_PL / 12_BS / 13_CF / (各 Schedule sheet 例: 04_Drivers, 07_WC, 08_PPE, 09_Debt) / 98_Checks シート` 
  - 11 L5: `xlsx の 09_Debt シート (01a §5.1 に従う命名)`
  - `SanityChecks` → `98_Checks`、`DebtSchedule` → `09_Debt` に統一。

---

## High Issues
### A-H-001: NRR の閾値フレームが file 間で 3 系統 (segment-based / global-quartile / quartile-distribution)
- **Files involved**: `02_saas_metrics.md` L359-365 / `08_investment_thesis.md` L477-482 / `10_modeling_craft.md` L156-164, L207-213
- **Inconsistency**: 02 §3.3 解釈基準 (L359-365) は global で `<90% Warning / 100-110% Healthy / 110-130% Top quartile / >130% Elite`。08 §4.1.2 (L477-482) は **segment-別** で `SMB >105% / Mid >115% / Enterprise >125%`。10 §2.1 (L156-164) は **distribution 表** で `Bottom25% 95% / Median 110% / Top25% 125% / Top5% 140%+`、§2.4 (L207-213) は **stage 別** で `Series A 100-110%, Series B 110-120%, ...`。同じ NRR 指標で 4 つの異なる切り方が併存し、Skill が「PASS/WATCH/FAIL を判定」する際にどれを使うか不確定。
- **Impact**: judgment-side (08) の閾値と build-side (02) の解釈基準が一致しないため、同じ NRR 値 (例 108%) でも `02 = Healthy / 08 = Mid SMBで FAIL` と相反判定が出る。投資判断の dual verification が機能しない。
- **Recommendation**: 02 を「指標の **定義と意味解釈** の正本」、08 を「**閾値判定** の正本」、10 を「**distribution 観察値** の正本」と役割分担を明文化。各 file の冒頭に `Threshold framing は 08 §4.1.2 を参照` のクロスリンクを置く。さらに 08 の表に "Distribution context" 列 (10 §2.1 から導出) を加え、`SMB >105% は SMB 中の Top25%相当` と注記。

### A-H-002: GRR ベンチマークが 02 と 08 で衝突
- **Files involved**: `02_saas_metrics.md` L316-322 / `08_investment_thesis.md` L487-491, L1841
- **Inconsistency**: 02 §3.2 表 L316-322 は `Best-in-class 90%+ / Median private 90% / SMB 80-85% / Enterprise 90-95%`。08 §4.1.3 L487-491 は `SMB GRR PASS >85% / Mid >90% / Enterprise >95%`、§ケース L1841 では汎用閾値として `PASS >90% / WATCH 85-90% / FAIL <85%`。SMB の PASS が 02 では `80-85% (median)`、08 では `>85%` と重なるが、08 の汎用閾値 (PASS >90%) は SMB を完全に弾く。
- **Impact**: 投資判断 (08) で SMB SaaS の GRR 87% は `PASS (segment-specific) = ✓ / FAIL (汎用) = ✗` と二重判定。
- **Recommendation**: 08 §4.1.3 を正本とし、汎用閾値 (L1841) は削除または「Mid-market default として」と限定明記。02 の `SMB 80-85% (median)` は出典 OpenView 2023 のため `OpenView SMB sample median: 80-85% (= Bottom-Mid quartile)` と再表記。

### A-H-003: CAC Payback ベンチマークが 4 系統で並走
- **Files involved**: `02_saas_metrics.md` L616-633 / `08_investment_thesis.md` L27 / `10_modeling_craft.md` L161, L186, L1281
- **Inconsistency**:
  (a) 02 §4.3 表 L616-633: `Best-in-class < 12mo / Good 12-18 / Concerning 18-24 / Critical >24`、KeyBanc 中央値 20mo、SMB 8-12 / Mid 14-18 / Ent 18-24。
  (b) 10 §2.1 表 L161: `Bottom 24 / Median 18 / Top 25% 12 / Top 5% 6` (months)。
  (c) 10 §2.2 anti-rule L186: `SaaS SMB で <6mo, Enterprise で <12mo` を flag (= 「あり得ない速さ」と疑う)。
  (d) 10 maxim L1281: `CAC payback <6mo は SMB でのみ成立する`。
- **Impact**: 02 (SMB の `Best-in-class 8-12 月`) と 10 (`SMB <6 月は Top5% 異常値`) の間で 4-6 月の幅で食い違う。同一サンプルで 02 は「優秀」と判定、10 は「flag = 怪しい」と判定。
- **Recommendation**: 全体ベンチマーク (Best/Good/Concerning) は 02 §4.3 を正本とし、`SMB best <8 月、Mid best <14 月、Ent best <18 月` を表に加える。10 の anti-rule (L186) は `flag` の閾値を `SMB <4 月、Ent <8 月` に下げて「異常検知」用と「ベンチマーク評価」用を分離。

### A-H-004: Burn Multiple ステージ別ベンチマーク値の衝突
- **Files involved**: `02_saas_metrics.md` L763-778 / `10_modeling_craft.md` L163
- **Inconsistency**: 02 §5.2 (L763-769) は `<1x Amazing / 1-1.5 Great / 1.5-2 Good / 2-3 Suspect / >3 Bad` (Sacks 原典)。同 §5.2 (L772-778) で stage 別: `ARR $0-$10M: <1.1x / $10-$50M: <1.0x / $50M+: <0.5x`。一方 10 §2.1 quartile 表 (L163) は global で `Bottom 3.0 / Median 1.5 / Top25 0.8 / Top5 0.5`。02 の stage 別「<1.1x」と Sacks の「<1x Amazing」を直結すると、$10M 以下では `0.8x = Top25%` (10) ≒ `<1.1x = healthy` (02 stage)、すなわち概ね一致するが、`>3x Bad` (02) と `Bottom 25% = 3.0x` (10) はちょうど境界線で `Bottom25 = Bad` という排他関係。10 (statistical) と 02 (judgment) の framing 差。
- **Impact**: 同じ Burn Multiple 2.0 が 02 では `Suspect` (= 警告)、10 では `Median と Bottom25 の中間` (= 普通) と読める。
- **Recommendation**: 10 §2.1 表に「分布値 ≠ healthy 閾値」と注記し、`Median 1.5 = Sacks の Great / Bottom 25% = Sacks の Suspect-Bad 境界` の対応を明示。02 と 10 のフレーム関係を 10 §2 冒頭に書く。

### A-H-005: Magic Number formula の `×4` の有無が 02 と 10 で分かれる潜在
- **Files involved**: `02_saas_metrics.md` L703-711, L726-728 / `10_modeling_craft.md` L162, L1389
- **Inconsistency**: 02 §5.1 formula L704: `Magic Number = (Rev_q − Rev_{q-1}) × 4 / S&M_{q-1}` (annualized)、L710 ARR ベース版も `× 4` で annualize。これは Scale VP / Wall Street Prep 標準。一方 10 §2.1 quartile 表 (L162) は `Bottom 25% 0.4 / Median 0.7 / Top 25% 1.1 / Top 5% 1.5+` で値の絶対水準を載せるが、計算式の `× 4` 言及なし。10 §2.4 例 (L259) や Q&A は値だけで式を示さない。
- **Impact**: ARR ベース (年次) で計算した Magic Number と quarterly-annualized で計算した値は **値が同じ** (linear)。実際は `×4` の有無で値が同じになるため数式は等価だが、**月次データを quarterly-annualize せず使う** 誤用が発生しやすい。10 が式を再掲しないと「式は別 file 参照」が読者に伝わらない。
- **Recommendation**: 10 §2.1 の表脚注に `Magic Number は 02 §5.1 の formula (Net New ARR × 4 / 前期 S&M) で計算する quarterly-annualized 値` と明記。月次値で計算しない注意を追加。

### A-H-006: Rule of 40 の "margin" 定義が 02 と 05 で相違
- **Files involved**: `02_saas_metrics.md` L805-815, L827-829 / `05_valuation_wacc.md` L1035, L1705
- **Inconsistency**: 02 §5.3 L805-812 は **2 通り** を併記: `Revenue Growth + FCF Margin` または `ARR Growth + Operating Margin (SBC 抜き)`。落とし穴 (L827-829) で「margin の定義 (FCF, EBITDA, Operating margin) を混在」を anti-pattern と明示。05 §10.x L1035 は `Rule of 40 = Revenue Growth (%) + EBITDA / FCF margin (%)`、05 末尾 L1705 は `Rule of 40 = Revenue Growth (%) + EBITDA margin (%)`。05 内部でも `EBITDA / FCF` (or 区切り) と `EBITDA margin` で揺れ、02 の正規 (FCF か Op margin の二択) と整合せず。
- **Impact**: SaaS で SBC 比率が高い企業 (例 SBC = Revenue 10%) で `EBITDA margin` (SBC 控除前) と `Operating margin (SBC 抜き)` と `FCF margin` (SBC 含む) は **5-15pt** 違う。Rule of 40 の判定が分岐。
- **Recommendation**: 02 §5.3 を「**標準は Revenue Growth + FCF Margin**、SBC を含む。EBITDA margin / Operating margin (SBC 抜き) を使う場合は明示」に統一。05 §10.x と末尾 reference を `FCF margin` で書き換え、`EBITDA / FCF margin` 表記は曖昧 (or の意味が読み取れない) のため除去。

### A-H-007: SBC の DCF 取扱いが 05 と 06 で逆向き
- **Files involved**: `05_valuation_wacc.md` L75, L336, L1432-1439 / `06_three_statement.md` L31 (L3 行 L3=SBC L3 add-back), L483-498
- **Inconsistency**: 05 §1.2 L75 と §15.5 L1432-1439 は Damodaran 主張: 「DCF では SBC を **真の希薄化コスト** と見なし、加算戻しをしない (= 現金費用として扱う)」。05 のミニケース (L336) も「§15.5 ルールにより EBIT から戻し入れず費用扱い」を明記。一方 06 §1.1 L31 (L3 = SBC) は CFS で `non-cash add-back` とし、§6 SBC schedule (L483-498) も「CFS で add-back (non-cash)」を IS-GAAP 標準として無条件に採用。
- **Impact**: モデル本体 (06 で組む CFS) では add-back し、DCF 評価 (05) では add-back しない。同一 xlsx で 2 つの異なる FCF が並走し、`scripts/build_model.py` が valuation シートを生成するときどちらの FCF を渡すか不定。
- **Recommendation**: 06 §6 に「**ただし DCF (05 §15.5) で valuation を取る場合、本書の add-back を `逆転` し SBC を現金費用として扱う 'DCF-FCF' を別途 schedule で計算すること**」を追記。CFS の表示自体は GAAP 標準 (add-back) を維持。

### A-H-008: LTV の "method" が 02 で 3 つ、他 file では method 未指定
- **Files involved**: `02_saas_metrics.md` L530-590 / `05_valuation_wacc.md` L1278 / `08_investment_thesis.md` L160 / `10_modeling_craft.md` L1281
- **Inconsistency**: 02 §4.2 は **3 method** (Simple / Cohort-based / DCF-based) を明示し、`LTV/CAC ≥ 3` を「pass/fail 基準にしない」と警告 (L586)。一方 05 (DCF 章末リファレンス)、08 §1.9 (L160 「LTV (gross / contribution / 期間想定)」)、10 (一行格言) はどれも **どの method を採るか指定なし** で `LTV/CAC` を引用。
- **Impact**: NRR > 100% の SaaS で Simple LTV (Method A) は発散、DCF LTV (Method C) は有限。同じ会社で「LTV/CAC = ∞」と「LTV/CAC = 5x」が並走可能。投資判定が壊れる。
- **Recommendation**: 各 file で `LTV` を最初に出す箇所に「02 §4.2 Method B (cohort-based, T=5y) または Method C (DCF) を使う。Method A (simple) は NRR < 100% でのみ valid」と注記。08 §1.9 / §4.1.4 の LTV/CAC 閾値表に `(method = cohort-based with T=5y)` を併記。

### A-H-009: TAM/SAM/SOM 関係式が 08 と 09 で別形
- **Files involved**: `08_investment_thesis.md` L867-888 / `09_market_sizing.md` L13-25, L67-77
- **Inconsistency**: 08 §6.x (L867-888) は SOM 計算式を 3 つ列挙: `SOM = TAM × penetration × win rate`、`SOM = (# target) × ARPU`、`TAM = (target) × pain savings × WTP`。これは TAM/SAM/SOM の **階層関係を無視** した式 (SAM が抜ける)。一方 09 §0.1 と §1 (L13-25, L67-77) は階層関係 `TAM ⊃ SAM ⊃ SOM` を厳格定義し、`Revenue = TAM × SAM% × p × ARPU` の三項モデルを正本とする。
- **Impact**: 投資判断 (08) と market sizing build (09) で SOM 計算が一致せず、同じ会社の SOM が 2 通り出る。08 の `SOM = TAM × penetration` は SAM 絞り込み無しで penetration を直接掛けるため、過大評価バイアス。
- **Recommendation**: 08 §6.x を 09 §1, §2 にリンクし、`SOM = SAM × p` を正本とする (penetration は SAM 内で定義)。08 の独立式は削除または「業界レポートが SAM を分けない場合の簡略形」と限定。

### A-H-010: 出典が 06 (J-GAAP / 中小法人) で 50%、05 (DCF) で日本 ETR 30% という別レイヤーの混在
- **Files involved**: `05_valuation_wacc.md` L70 / `06_three_statement.md` L398 / `07_japan_specifics.md` L295-302
- **Inconsistency**: 05 §1.2 表 L70 は `日本: 約 30% (法人実効税率)`。06 §5.1 L398 は `日本 23.2% (法人税) + 地方 (実効 30-35%)`。07 §2.1.3 L295-302 は最新値 `大企業 (防衛特別法人税適用後) 約 31.52% / 適用前 30.62% / 中小法人 33-35%`。3 つの数値が同じ "日本実効税率" を異なる粒度で語る。
- **Impact**: DCF (05) で `t = 30%` を使い、財務モデル (06) で `30-35%` 帯、運営の正本 (07) は `31.52%` を主張。同じ会社の DCF が 1.5%pt 程度ずれ、equity value で 5-10% の差。
- **Recommendation**: 07 §2.1.3 を **唯一の正本**とし、05 と 06 の日本 ETR 言及はすべて `07 §2.1.3 を参照。base case は大企業 = 31.52% (防衛特別法人税後)、中小法人 = 33-34%` に書き換え。05 §1.2 表は `日本: 約 31.5% (07 §2.1.3 参照、年度・企業区分で変動)` に。

### A-H-011: 「OS」回避ルールが 02 と 09 で宣言されながら 09 で違反
- **Files involved**: User memory (`feedback_terminology_and_data.md`) / `02_saas_metrics.md` L5 / `09_market_sizing.md` L42, L714 / `08_investment_thesis.md` L36, L798, L1720
- **Inconsistency**: User memory が「『OS』を避ける」を明示。02 L5、09 L42、08 L36 がこのルールを冒頭で再宣言。しかし 09 §3.x L714 の network effect 表で `OS + apps` (= "Operating System + apps" の意) を使用。08 L798 の `Dependency / OSS`、L1720 の `OSS 自社 fine-tune` は OSS (Open-Source Software) であり別語だが、L798 の `OSS` は cell label で違反ぎりぎり。
- **Impact**: User-memory 違反として直接的に低 priority だが、宣言したルールを corpus 内で破ると「ガイドライン遵守度」が下がる。
- **Recommendation**: 09 L714 の `OS + apps` を `運営体系 + apps` または `platform + apps` に置換。08 L798/L1720 の OSS は文脈で「Open-Source Software」と分かるため `OSS (Open-Source Software)` と初出時に展開して曖昧性を排除。

### A-H-012: Cover sheet 必須項目数が 9 (01a) / 12 (01b) で不一致
- **Files involved**: `01a_modeling_standards.md` L1123, L758-786 / `01b_integrity_and_anti_patterns.md` L539-577
- **Inconsistency**: 01a §9.1 統合チェック L1123 は `purpose / audience / decision / version / author / date / currency / time scale / scenario の **9 項目**`。01a §5.5 テンプレート (L758-786) は概ねこれと一致。01b §3.1 L543-558 は **12 項目** 表 (`1.Title / 2.Company/Entity / 3.Version / 4.Author / 5.Last modified / 6.Currency unit / 7.Period / 8.Active Scenario / 9.Master Check / 10.Source documents / 11.Recipient / 12.Disclaimer`)。01a の 9 項目は `purpose, audience, decision` を含み、01b は含まず代わりに `Master Check, Source documents, Recipient, Disclaimer` を含む。**両者の和集合は 13 項目**で完全一致しない。
- **Impact**: Skill が cover を生成する際、どちらの list を採用するか不定。01a を採れば `Master Check / Disclaimer` 抜けで 01b §A.4 チェック fail。01b を採れば `Audience / Decision` 抜けで 01a §9.1 fail。
- **Recommendation**: **和集合 13 項目を正本**とし、01a §9.1 と 01b §3.1 を相互参照で同期する。01a §5.5 テンプレートに `Master Check / Source documents / Recipient / Disclaimer` を加え、01b §3.1 に `Purpose / Audience / Decision` を加える。

### A-H-013: NOL 控除限度の表記混乱 — 06 が 80% (US) を表示、07 が 50% (日本大法人) を表示し base case が不明
- **Files involved**: `05_valuation_wacc.md` L70 / `06_three_statement.md` L429-440, L443-456 / `07_japan_specifics.md` L355-369
- **Inconsistency**: 06 §5.4 L429-440 は **米国 TCJA** (2017 以降の損失) として `控除限度 = 80%` と明示、§5.5 L443-456 は日本 (大法人 50% / 中小 100%) と分離して書く。整合的。**ただし 06 §5.1 L398 が「日本 23.2% (法人税) + 地方 (実効 30-35%)」と書いた直後に NOL 説明が来るため、読者が 80% を日本 NOL と誤認するリスク**。05 §1.2 (L70) は `t = 30%` を日本に当て、NOL 言及なし。
- **Impact**: 日本企業の DCF を組むとき、05 の `t = 30%` と 06 の TCJA 80% を組み合わせると課税所得計算が壊れる (50% 控除限度を見落とし)。
- **Recommendation**: 06 §5.4 / §5.5 のセクション見出しを `5.4 NOL Carryforward — 米国 (TCJA, 80% limit) / 5.5 NOL — 日本 (大法人 50%, 中小 100%)` と国名を冒頭に置き、混同防止。05 §1.2 表に NOL ルールへのクロスリンク `(NOL 詳細 → 06 §5.4-5.5, 07 §2.3)`。

### A-H-014: Discount Rate (cap rate / discount rate) と SAFE/J-KISS 利息の二重カウント潜在
- **Files involved**: `04a_convertible_and_terms.md` L57-65, L156-180, L353-363, L483
- **Inconsistency**: 04a §1.3 比較表 (L57-65) で SAFE 利息「なし」、Convertible Note 利息「あり (4-8%)」、J-KISS v2.0 利息「なし」を整理。§2.3 SAFE conversion (L156-180) は cap + discount のみで利息加算なし (整合)。一方 §3.5.1 J-KISS L390 は `行使価額 = min(PPS × Discount, Cap / FDSO)` で利息なし (整合)、L353 は v1.0 が利息 1% を持っていたが v2.0 で削除と説明 (整合)。問題: §2.6 (L228-318) の Post-money SAFE 計算ステップが、SAFE 1 持分を 「`I/C = 500K / 5M = 10%`」固定で計算しているが、ここで使う `C` (post-money cap) と Series A の `pre-money 800M` の関係が、L483 のシリーズ A 数値と整合しない可能性 (元 6M founder 株を維持して T を逆算する手順が示されるが、結果が L313 (founder 5.5M = 55%) と L317 (founder 6M = T 10.91M = 約 55%) で微妙にずれる)。
- **Impact**: SAFE 計算結果 (持分 %) が本書の数値例で 0.5pt 以上ずれる場合、新規メンテ者が「数値例自体が壊れている」と判定して計算ロジック全体を疑う。
- **Recommendation**: 04a §2.6 数値例の Step 6 (L296-317) を再検算し、`founder 維持 + T 逆算` 系列と `T = 10M 仮置き` 系列を分けて並記。実装時は **YC SAFE Primer worksheet を正本** とし、本書の数値は「説明用 illustrative」と明記。

### A-H-015: SaaS Quick Ratio 閾値が 02 でのみ定義、08 / 10 で参照されるが式・閾値が不在
- **Files involved**: `02_saas_metrics.md` L878-910 / `08_investment_thesis.md` (該当節なし) / `10_modeling_craft.md` (該当言及なし)
- **Inconsistency**: 02 §5.5 で Hamid の Quick Ratio formula と閾値 (`>4 Good`, `2-4 OK`, `<2 投資見送り`) を明示。SaaS 効率の 1 軸として重要だが、08 (judgment-side) には言及なし、10 (craft) にも言及なし。Skill が「効率成長を 3-4 軸で立体評価せよ」と書いているにもかかわらず、Quick Ratio が判断軸に含まれていない。
- **Impact**: judgment 側で SaaS Quick Ratio を「使わない」と意思決定したのか、単に「言及漏れ」なのか不明。Build と Judgment の dual verification の片肺。
- **Recommendation**: 08 §4.1 に SaaS Quick Ratio の PASS/WATCH/FAIL 行を追加するか、明示的に「02 §5.5 は資料整理目的、判断指標としては Magic Number / Burn Multiple で代替」と書く。

### A-H-016: ARR ステージ別レンジが 02 / 08 / 10 で異なる
- **Files involved**: `02_saas_metrics.md` L85-93 / `08_investment_thesis.md` L388-393 / `10_modeling_craft.md` L233-239, L757-759
- **Inconsistency**:
  - 02 §2.1: Series A `$1.0-3.0M` / B `$5-10M` / C `$15-30M` (出典 OpenView/Tunguz/KeyBanc)
  - 08 §3.1: Series A `$1-5M ARR` / B `$5-20M` / C `$20-50M` (出典なし)
  - 10 §2.4 ramp 表: `Y2 $1-3M / Y3 $3-10M / Y5 $20-60M`、§11.3 stage transitions L757: `A→B: ARR $5-15M`
- **Impact**: 同じ ARR $7M の会社が 02 では「Series B 中域」、08 では「Series A 上限」、10 では「A→B 移行」と判定。投資ステージ判定が file 間で異なる。
- **Recommendation**: 02 §2.1 を **正本** (出典明示済み) として、08 §3.1 と 10 §2.4 / §11.3 にクロスリンクを置き、両者を 02 のレンジに合わせる。Stage は ARR 単独で決まらない (調達履歴も影響) ため `ARR は補助シグナル` と注記。

### A-H-017: TAM 必要規模の数値が 09 で `>$1B 下限`、08 で `>$10B Tier1 VC ターゲット` と切り口違い
- **Files involved**: `08_investment_thesis.md` L250 / `09_market_sizing.md` L122-128, L137-156
- **Inconsistency**: 09 §1.4 表 (L122-128) は VC 評価を 5 階層 `<$100M Niche / $100M-$1B Small / $1-10B Standard / $10-100B Large / >$100B Massive`、§1.5 (L137-156) は unicorn 逆算で `TAM ≥ $1B (下限)`。08 §2.1.3 (L250) は a16z late-stage の市場基準として `Market | TAM > $10B`。`$1B` は 09 の最低、`$10B` は 08 の Tier1 ターゲット。両者は「下限」と「ターゲット」で使い分けているが、明示的な対応関係が書かれていない。
- **Impact**: TAM $3B の会社を 09 では「Standard VC scale」と見るが、08 では a16z 的 fail。Skill が「PASS/WATCH/FAIL を判定」する際の物差しが曖昧。
- **Recommendation**: 08 §2.1.3 の `TAM > $10B` に注記 `(a16z late-stage の追加要件、Series A/B では 09 §1.4 の Standard $1B-10B で十分。)` を加え、09 §1.4 表からも `$10B+ = Tier 1 VC late-stage` 列を相互参照。

### A-H-018: TAM の SOM 期間が 09 と 08 で 3-5 年 vs 5 年で異なる
- **Files involved**: `09_market_sizing.md` L75 / `08_investment_thesis.md` L1581
- **Inconsistency**: 09 §1.1 L75 SOM 定義は `短期 (3-5 年) で実際に取得可能な範囲`。08 ケース L1581 は `SOM (5 年): 約 80 億円 (10% シェア仮定)`。
- **Impact**: 各社の SOM を比較するときの時間軸が定まらない。3 年と 5 年では SOM の数値が大きく違う。
- **Recommendation**: 09 §1.1 を `**5 年 (SOM = 5 年到達)** を base、`3 年 (= "near-term SOM")` をオプション` と固定。08 のケース全てを `5 年` で統一。

### A-H-019: NRR 公式 A vs B の選択が file 間で文書化されない
- **Files involved**: `02_saas_metrics.md` L1314-1321, L341 / `08_investment_thesis.md` L477-482 / `10_modeling_craft.md` (NRR 計算式記載なし)
- **Inconsistency**: 02 §3.3 L341 は formula B `(Starting + Expansion - Contraction - Churn) / Starting`。02 §9.7 L1314-1321 は A `期末同 cohort / 12 ヶ月前同 cohort` と B の二系統が「実務で並走」と認め、値が違うことを警告。一方 08 §4.1.2 / 10 は閾値を載せるが「どちらの公式で計算した値か」を指定しない。
- **Impact**: 同じ会社の NRR が `公式 A = 115% / 公式 B = 108%` で 7pt 違う事例あり。閾値判定が壊れる。
- **Recommendation**: 02 を「公式 B (= cohort-equivalent)」を Skill の正本と宣言、`Logo NRR / Dollar NRR / FX-neutral NRR の併記` をベストプラクティスとして 02 §3.3 / §9 に明記。08 / 10 は「公式 B 前提」と冒頭で参照リンク。

### A-H-020: J-KISS の利息: v1.0 が 1% / v2.0 が 0% を 04a で詳述、04b と 11 では言及なし
- **Files involved**: `04a_convertible_and_terms.md` L353-363, L480-484 / `04b_cap_table_mechanics.md` L131-138 (J-KISS 例) / `11_debt_financing.md` L195-211
- **Inconsistency**: 04a §3.7 (L480-484) で v2.0 は無利息と明示。04b L131-138 の cap table 例は J-KISS 1 億円・cap 8 億円・Discount 20% で利息言及なし (整合的に v2.0 を仮定)。11 §1.3 L195-211 の J-KISS 説明では「形式は新株予約権、利息なし (v2.0)」と書くが、SAFE/J-KISS の利息有無を一貫表で示しておらず、Convertible Note (利息あり) との切替条件が曖昧。
- **Impact**: モデルで J-KISS を計上するとき、`v1.0 = +1%/年 を 18 ヶ月で +1.5%`、`v2.0 = 0%` の差。元本 1 億円なら 150 万円差 (現実的に小さいが、複数 J-KISS が並走する場合は累積する)。
- **Recommendation**: 04b §J-KISS 例と 11 §1.3 J-KISS 行に `バージョン: v2.0 (無利息)` を明記。04a §3 の利息推移をビュー表で要約 (v1.0 = 1% / v2.0 = 0%) を 04b と 11 にリンク。

### A-H-021: Sensitivity Analysis の「主要 driver」設計が 01b と 10 で異なる
- **Files involved**: `01b_integrity_and_anti_patterns.md` L335-432 / `10_modeling_craft.md` L368-410
- **Inconsistency**: 01b §2 (L335-432) は Excel Data Table / Tornado / Scenario Manager / Toggle pattern を **手段**として詳述するが、driver 選定の指針なし。10 §4 (L368-410) は **`Top 5 drivers を Tornado で識別、High impact × High uncertainty を最優先`** と判断軸を明示し、「Tornado を装飾ではなく decision-making 道具に」と書く。両者は補完的だが、01b §A の Anti-pattern 表に「driver の優先順位なし sensitivity」が含まれていない。
- **Impact**: 01b だけ読んだ実装者が「全 driver を ±10% で振る」装飾 sensitivity を生成し、10 の判断軸が適用されない。
- **Recommendation**: 01b §2.2 (Tornado Chart) の冒頭に `driver 選定基準は 10 §4.1 を参照` を明示。10 §4 の冒頭に `(具体的 Excel 実装は 01b §2 を参照)` を加える。

### A-H-022: cohort 起点定義が 02 §3.3 と 02 §6 で揺れる
- **Files involved**: `02_saas_metrics.md` L370, L430, L962-981, L1314-1321
- **Inconsistency**: 02 §3.3 落とし穴 (L370): 「`12 ヶ月前の顧客`とするか`期初時点`とするかで値が変わる」。§3.4 落とし穴 (L430): 「期初 cohort で計算するか、各月の cohort weighted で計算するか」。§6.1 (L962): 「ある月 (cohort 起点) に獲得した顧客群の起点を 100% としたその後の revenue 推移」。§9.7 (L1314-1321) で「12 ヶ月前同 cohort vs 期初」を並記。同じ corpus 内で cohort 起点が `12 ヶ月前 / 期初時点 / 月次 cohort weighted / acquisition-based` の 4 通り。
- **Impact**: NRR / cohort retention / LTV (Method B) は cohort 定義に強く依存。同じ会社で値が ±5pt で動く。
- **Recommendation**: 02 §1 (前提と用語整理) に「**標準: monthly acquisition cohort** (顧客獲得月で cohort 確定)、**集計時は trailing 12mo で分母統一**」と単一 convention を宣言。各メトリクスの計算式に `cohort 起点 = 02 §1 標準` を脚注で確認。

### A-H-023: 03 と 02 の SaaS retention 数値の重複・微差
- **Files involved**: `02_saas_metrics.md` L319-322 / `03_business_models.md` L1.x (SaaS 章なし、SaaS 言及は §1.1 内)
- **Inconsistency**: 02 §3.2 GRR ベンチマーク `Best 90%+ / Median 90% / SMB 80-85% / Ent 90-95%`。03 は SaaS 章を 02 に外注しており直接の閾値はない (整合)。問題: 03 §1.x (Marketplace) の cohort GMV retention `Year 2 で 60-80% Median, >100% Great` (L160-165) と 02 SaaS の NRR (`100-110% Healthy, >130% Elite`) が **異なる物差し** で書かれている。両者は「SaaS の NRR (revenue ベース、expansion 込み) ≠ Marketplace の GMV retention (取引額ベース)」と業態が異なるため数値も異なるが、`02 で 110% は Healthy / 03 で 110% は Great` と読める。
- **Impact**: 業態混在の比較で「Marketplace の retention 88% (Year 2 で 88% Median 帯) は SaaS の Healthy 100-110% より低い」と誤読しうる。
- **Recommendation**: 各業態の retention 値を出す行で「**業態間で直接比較しない (SaaS NRR は revenue, Marketplace GMV retention は取引額)**」と注記。03 各業態に「対応指標 (SaaS の NRR とは異なる)」のクロス参照表を加える。

### A-H-024: Default Color of Hex は 4 種だが 01a では 7 色 (紫・灰・橙) を併記、00 と整合せず
- **Files involved**: `00_design_guidelines.md` L321-326 / `01a_modeling_standards.md` L479-487
- **Inconsistency**: 00 §3.1 表 L321-326 は **6 色** (青/黒/緑/赤/灰/Ink) を Functional palette として定義 (Hard input/Formula/Cross-sheet/External/Comment/Ink)。01a §4.1 表 L479-487 は **7 色** (青/黒/緑/赤/紫/灰/橙) で `紫 = named range`、`橙 = scenario lock` を任意で追加。00 は紫・橙を含まないし、01a の `灰 = #808080` は 00 の `灰 = #666666` (IB_COMMENT) と微妙に違う (HEX 異)。
- **Impact**: モデルで named range を紫文字 (`#800080`) で塗ると、00 の Functional palette 規範外の意味が混入し、レビュアが「これ何?」と質問する。
- **Recommendation**: 01a の `紫 (任意)` と `橙 (任意)` を削除、または 00 §3.1 の表に「optional 拡張色」セクションを加え、`#800080` (named range) と `#FF6600` (scenario lock) を正式拡張として登録。同時に灰の HEX を 00 と 01a で統一 (`#666666` を採用)。

---

## Medium Issues
### A-M-001: Freeze pane 位置の言及差
- **Files**: `01a` L796-800 (`G6` 統一) / `01b` L301-305 (Freeze Top Row 言及あり)。01a は `G6` を強制、01b §1.7 Pattern C は `Freeze Top Row` を別目的で使う。読者は「freeze は 1 種類」と読み違える。
- **Recommendation**: 01a §6.1 に注記 `Master check (01b §1.7 Pattern C) 用途では Top Row freeze を併用可。複数 freeze は禁止 (Excel 仕様)`。

### A-M-002: Number format `#,##0;(#,##0);-` の数値ゼロ表示が `-` (01a) と `0` (06) で揺れる
- **Files**: `01a` L555 (ゼロは `-` 表示) / `06` の数値例で `0` が散見 (例 §3.4 inventory 0)。
- **Recommendation**: 01a §4.3 の format string をモデル全体で強制、`0` 値は dash で表示する慣行を 06 にも明記。

### A-M-003: フォントサイズ標準が 00 (Arial 10pt) と 01a (Arial 10pt) で一致するが、後者で「11pt bold header」と書く節あり
- **Files**: `00` L171 (Arial 10pt body) / `01a` L520-528 (`section header Arial 11pt bold`、`sheet title 14pt bold`)。00 §2.4 (L218) は `Section title 14pt`、`Sub-section header 11pt`。01a §4.2 と整合だが、§9.4 L1155 で `Arial 10pt body, Arial 11pt bold header` と簡素化されているため `Section title 14pt` が抜ける。
- **Recommendation**: 01a §9.4 (L1155) に `sheet title 14pt bold` を加えて 00 §2.4 と整合させる。

### A-M-004: Bold rules — 00 と 01a で `Subtotal は bold か否か` が一致しない箇所
- **Files**: `00` L255-276 (Subtotal は bold)、`01a` L527 (`sub-total row Arial 10 regular + top border`)、L639-642 (`Bold = section header, total row, output row, year header`)。01a は Subtotal を bold としていない。
- **Recommendation**: 01a §4.2 の表 L527 を `sub-total row | Arial 10 | regular | top border` から `bold` に修正、`grand total + top single + bottom double` で統一。

### A-M-005: footnote サイズが 8pt (00) と 8pt italic gray (01a) で同値だが、09 / 10 で言及なし
- **Files**: `00` L226 / `01a` L528, L671 / `09 / 10` 該当言及なし。
- **Recommendation**: 09, 10 の出力サンプルにも footnote 記法を再掲、または 00 へクロスリンク。

### A-M-006: ASC 606 / IFRS 15 の言及粒度が 02 / 03 / 06 / 07 で統一されない
- **Files**: `02` L52, L1290 (5-step model 言及)、`03` L130-141 (Principal/Agent 整理、ASC 606)、`06` L660 (適用日のみ)、`07` L80-108 (5 ステップ完全展開)。同じ会計基準を別粒度で 4 箇所記述。
- **Recommendation**: 07 §1.3.1 を「5 step の正本」、02 / 03 / 06 は「07 §1.3.1 を参照」とする 1 行クロスリンクで圧縮。

### A-M-007: Deferred Revenue の表記揺れ — `Deferred Revenue` / `契約負債` / `前受金` が混在
- **Files**: `02` L221, L1270 (`Deferred Revenue`)、`06` L150, L644 (`Deferred Revenue / 契約負債`)、`07` L107 (`契約負債`)、`11` L1270 (`Deferred Revenue`)。同一概念を 3 用語で表記。
- **Recommendation**: `Deferred Revenue (契約負債)` を初出時に併記、以後 `Deferred Revenue` に統一。07 内では和文文脈のため `契約負債 (Deferred Revenue)` を許容。

### A-M-008: `(–)` sign indicator の有無が file 間で揺れ
- **Files**: `00` L116-119 で `(–) COGS / (–) OpEx` を推奨、`01a` で `Sign convention` (PL positive、CF signed) を規範化、`06` の PL 表 L62-117 では `Total COGS = SUM` のみで `(-)` 表示なし。
- **Recommendation**: 00 §1.3 の `(–)` 慣行を 01a §4.4 sign convention に取り込み、06 のテンプレ表の各 cost 行に `(–)` を追加 (display only)。

### A-M-009: `EBITDA` の SBC 含む / 含まないの併記が 06 / 02 / 05 で不整合
- **Files**: `06` L97-98 (`EBITDA (excl. SBC)` と `EBITDA (GAAP, incl. SBC)` を 2 行併記)、`02` L815 (Operating margin 派は SBC 抜き)、`05` L525 (`SBC を費用扱いした調整 EBITDA`)。
- **Recommendation**: 06 §2.1 を正本 (`EBITDA (excl. SBC)` = adjusted、`EBITDA (incl. SBC)` = GAAP) として 02, 05 の SBC 議論にクロスリンク。Rule of 40 用 EBITDA も 06 のどちらを参照するか明示。

### A-M-010: `Adjusted EBITDA` 定義の出典なし
- **Files**: `02` L1525 (`Adjusted EBITDA の調整項目に SBC + 訴訟費 + restructuring を全部入れる` を anti-pattern と書く)、`05` L605 (`Adjusted EBITDA +60%` の数値出典なし)。
- **Recommendation**: `Adjusted EBITDA` を出すたびに「(=GAAP EBITDA + SBC + 一時費)」のような調整内訳を一行明記、または 06 §2.1 の標準定義へリンク。

### A-M-011: Net Debt 定義の充実度が 05 と 11 で異なる
- **Files**: `05` L562-572 (operating lease, pension, preferred, NCI, SAFE まで含む完全版)、`11` L1677 (`Net Debt at exit = TLB + Mezz` の限定版)。
- **Recommendation**: 11 §11.x のミニケースで Net Debt を出すたびに「(05 §2.7 完全版に従う、本ケースでは TLB + Mezz のみが該当)」と注記。

### A-M-012: Marketplace の「take rate」の定義 (Net or Gross) が 03 内で揺れる
- **Files**: `03` L54-58 (`Take Rate = Net Revenue / GMV または Gross Revenue / GMV`)、L154-156 (`Ride hail (gross) 22-28%`)。同一指標で Net base と Gross base の両論。
- **Recommendation**: 03 §1.1 で「Default は Net Revenue / GMV、Gross は別途 `Gross Take Rate` と明記」を基本ルールに格上げ。

### A-M-013: `Operating CF` vs `CFO` 表記揺れ
- **Files**: `02` L758 (`Net Burn = Operating cash outflow ...`)、`06` L185 (`Cash Flow from Operating (CFO)`)、`11` 各所 `CFO` 多用。
- **Recommendation**: `CFO (Operating Cash Flow)` を初出時に併記、以後 CFO で統一。02 §5.2 を該当書き換え。

### A-M-014: Mid-year convention の言及範囲
- **Files**: `05` L267-274 (詳細展開)、`06`, `10`, `11` 言及なし。Mid-year は DCF 標準で多用されるが、`build_model.py` の DCF シート生成時に他 file から参照できない。
- **Recommendation**: 06 §11 (DCF schedule 関連節があれば) または `05 §1.7` を Single Source として全 file からリンク。

### A-M-015: `T2D3` (Triple Triple Double Double Double) の解釈が 08 と 10 で不一致
- **Files**: `08` L450-460 (T2D3 軌道表)、`10` L243 (`Year 3 で $30M ARR は top 5%`)。08 の T2D3 は「典型的な top performer の path」、10 はそれを「Series A モデルに base で置くな」と警告。両者は同一指標の別の使い方を強調しているが、cross-link がない。
- **Recommendation**: 08 §4.1.1 と 10 §2.4 を相互参照。`T2D3 を base にすべきか upside にすべきか` の判断は 10 §3 (Hockey stick 検出) の判定軸に従う、と明記。

### A-M-016: `runway` の計算式と最低水準
- **Files**: `02` 言及なし、`08` L29 (`runway > 18 ヶ月`)、`10` L1465 で QA、`11` L107 (Bessemer 標準推奨は `6 ヶ月 burn` floor — これは min cash covenant, runway とは別概念)。`runway` 自体の定義表が一元化されていない。
- **Recommendation**: 06 §7 (Cash schedule) または 10 §7 (Cash / Runway) に `Runway = Cash / Net Monthly Burn` の正本式を置き、各所からリンク。

### A-M-017: Vesting 標準 (4y / 1y cliff) が 04b と 07 で再掲
- **Files**: `04b` L388-394 / `07` L443-447。同じ `4-year vest, 1-year cliff` を 2 回独立に説明。
- **Recommendation**: 04b §3.5 を正本、07 §2.7 から `vesting 設計詳細は 04b §3.5 を参照` のクロスリンクに簡素化。

### A-M-018: `Pre-money / Post-money` 計算が 04a / 04b / 05 / 08 で類似説明が並走
- **Files**: `04a` L97-117 / `04b` L143-170 / `05` L725-740 / `08` L1671。
- **Recommendation**: 04b §2.1-2.3 を「正本」、他は「04b §2 を参照」へ要約。

### A-M-019: `409A` valuation の言及粒度が 04b と 07 で異なる
- **Files**: `04b` L313-323 (OPM 詳細含む)、`07` 言及なし (日本特有の純資産価額方式 / 配当還元方式に切替えていることが明示されない)。
- **Recommendation**: 07 §2.7.1 で「米国の 409A は 04b §3.2 を参照、日本は 2023 年 7 月通達後の純資産価額方式」と対比表を加える。

### A-M-020: 信託型 SO の取扱いが 04b と 07 で重複説明
- **Files**: `04b` L356-371 / `07` L465-477。同じ国税庁 2023 年 5 月見解を 2 回独立に展開。
- **Recommendation**: 07 §2.7.4 を正本、04b §3.3.3 は要約 + 07 へのクロスリンクに圧縮。

### A-M-021: 法人実効税率の例示数値が 06 / 07 / 05 で計算式の有無が異なる
- **Files**: `06` L398 (実効 30-35% を直接) / `07` L274-294 (式と要素を完全展開) / `05` L70 (`日本: 約 30%` と一行)。
- **Recommendation**: 07 §2.1 を正本 (式 + 例)、05 と 06 から参照。

### A-M-022: `M&A` ロールアップ M&A 評価の境界
- **Files**: `05` §3 / `07` §10 / `08` §12 で類似テーマ。`08` §1.14 (L208) では `Strategic M&A revenue × 4-12x`、`07` §10 では適格組織再編で繰越欠損金。両者の交差点が薄い。
- **Recommendation**: 07 §10 の冒頭で「08 §12 (Exit Strategy) と 05 §3 (Precedent Transactions) を併読」。

### A-M-023: VC method の Required IRR が 05 と 08 で別水準
- **Files**: `05` L780-790 (Series A IRR 50%)、`08` (該当節なし)、本ファイルの `05 §1.4.5` (L182-188) で `Series A 40-60%` を載せる。05 内で IRR が `50% (Mini case)` と `40-60% (table)` で揺れる。
- **Recommendation**: 05 §1.4.5 のテーブルを正本、ミニケースは `(レンジ中央値 50% を採用)` と注記。

### A-M-024: `Liquidation preference` の標準が 04a と 04b で表現が違う
- **Files**: `04a` §7 (詳細条項) / `04b` (含む waterfall を §6 に展開、04a と前提が一致するか cross-link なし)。
- **Recommendation**: 04b §6 (waterfall) の冒頭で「04a §7 の経済条項を前提」を明示。

### A-M-025: Stage discount 適用の規則 (重複バイアス警告)
- **Files**: `05` §1.4.5 (L191) の `stage-appropriate discount と probability-weighting を同時に使うのは原則 NG`、`08` L195 で `best/base/worst の確率混合` を推奨。両者は同一手法ではないが、初学者に区別されにくい。
- **Recommendation**: 08 §1.13 sensitivity の説明に `stage discount は 05 §1.4.5 を参照、probability-weighting と二重カウントしない` を加える。

### A-M-026: 出典 OpenView の年版が `2023` 中心だが `2025 (高 Alpha 共著)` の言及がある
- **Files**: `02` L1136 (OpenView 2023 / 2025 共著、Kyle Poyar)、`08` L473 (`2025 SaaS Benchmarks - High Alpha / OpenView`)。`2025` 版の数値は明示されないが URL は `2025` を引用。
- **Recommendation**: 02 §8 と 08 §4.1 で同一出典の年版表記を統一、最新版を base に。

### A-M-027: KeyBanc 中央値 ARR $26M (02 §2) と Sapphire 共催の数値範囲
- **Files**: `02` L91, L1154 で同一データを 2 回引用。
- **Recommendation**: 02 §2.1 から §8 へ集約。重複削減。

### A-M-028: `Conversion Price` の min 関数の式が 04a で複数表現
- **Files**: `04a` L166 `Conversion Price = min(cap, disc)`、L387-396 `行使価額 = min(PPS × 0.80, Cap / FDSO)`。等価だが書式違い。
- **Recommendation**: 共通フォーマット `min(PPS × (1-d), Cap / FDSO_pre)` で統一。

### A-M-029: `Anti-dilution` の説明粒度
- **Files**: `04a` §9 / `04b` §4.5 (L487-498)。両ファイルで Full Ratchet と Broad-based WA を独立に説明。
- **Recommendation**: 04a §9 を経済条項の正本、04b §4.5 はモデル化に集中 (cross-link)。

### A-M-030: `Working Capital` driver days の標準値の出典
- **Files**: `06` §3.1 (式のみ)、`03` 各業態 (DSO/DIO/DPO 業態別ベンチマーク)。06 がデフォルト値を持たないため、`build_model.py` がどの業態を base にするかで挙動が異なる。
- **Recommendation**: 06 §3.1 表に「default driver = SaaS の場合 DSO 45, DIO 0, DPO 30」を明記し、業態別調整は 03 を参照。

### A-M-031: Burn rate の単位 (年率 vs 月率) 揺れ
- **Files**: `04b` §3.7 L420-427 (`Burn rate = 年間付与 / FDSO` で **option burn**)、`02` L758 / `08` (`Net Burn` = 月次キャッシュ流出) で同じ "burn" だが概念が違う。
- **Recommendation**: 04b §3.7 を `Equity Burn Rate` と命名、`(キャッシュの burn rate と区別)` を併記。

### A-M-032: `Footnote` 表記 — 08 と 09 で同じスタイル URL リンクだが微妙に異なる
- **Files**: `08` L48 `[出典: ... ](URL)` / `09` 同形式。表記は揃っているが、引用日付の有無が混在。
- **Recommendation**: 出典は `[出典: <Title> (YYYY-MM)](URL)` を 08 / 09 / 10 で統一。

### A-M-033: `Magic Number` の denominator (S&M_{q-1} vs S&M_q) の議論
- **Files**: `02` L709 注 (`分母が前期の S&M なのは、当期の ARR 増は前期投資の成果という前提`)。10 / 08 では言及なし。
- **Recommendation**: 02 §5.1 注を全 file 共通の前提として引用 (脚注で OK)。

### A-M-034: 「Series A 中央値 NRR 110%」の出典の重複
- **Files**: `02` (Bessemer 2024 / KeyBanc 2024)、`10` L60 / L790 (Bessemer 中央値 110%)、`08` L1257 (`NRR 約 90%` を基準に置く別ケース)。同一閾値に異なる出典が散在。
- **Recommendation**: 単一の中央値を `02 §3.3 + §8.1` に集約し、各 file は cross-link。

### A-M-035: `SaaS Capital Index` と `Bessemer Cloud Index` の併用
- **Files**: `02` L1077-1080 (両指標を区別、平均値が違う)。`05` L1378 (median EV/NTM Revenue 表)、`08` (該当言及なし)。
- **Recommendation**: 02 §7.4 を正本 (URL/年版/中央値の差を明示)、他は cross-link。

### A-M-036: `Currency` 単位 (USD vs JPY) の混在
- **Files**: `04b` L9 (`為替 1 USD = 150 JPY を仮定`) は明示。一方 `02` `08` `10` で `$M` と `¥M` が混在し、為替前提なし。
- **Recommendation**: 各 file の冒頭に `本書内の為替前提 = 1 USD = 150 JPY (2026-05 時点)` を明記。

### A-M-037: 「OS」表記回避ルールの 09 違反
- **Files**: `09` L42 (回避宣言)、L714 (`OS + apps`) は A-H-011 で既出だが、ルール違反は本来 Medium で別 ID にする方が修正トラッキングしやすい。
- **Recommendation**: A-H-011 の Recommendation に従う。

### A-M-038: 数値整合性 (04a §2.6 数値例の Step 6 で Founder 株数の T 逆算が 5,500,000 vs 6,000,000 で揺れる)
- **Files**: `04a` L313 (`Founders 持分 = 100% - 10% - 2.5% - 2.5% - 10% - 20% = 55.00%`、5,500,000 株)、L317 (`元の株数は 6,000,000 株 → T = 10,909,091 株`)。T が `10M` 仮置き と `10.91M` 逆算で 1 行で並走。
- **Recommendation**: Step 5 と Step 6 の数値を `T = 10.91M` で統一し、Step 4 / 5 の表 (L300-307) も再計算。

---

## Low Issues
### A-L-001: 略号 SBC / SaaS の最初の展開
- **Files**: 02 / 05 / 06 で `SBC` を初出時に `Stock-Based Compensation` と展開する箇所が混在 (06 §6 で展開、02 §4.1 で展開なし)。
- **Recommendation**: 各 file で SBC 初出 = 必ず展開。

### A-L-002: 全角・半角混在 — `「」` と `""` の使い分け
- **Files**: 全 file で日本語クオート (「」) と英語クオート ("") が混在。
- **Recommendation**: 和文は `「」`、英文 (定型句) は `""` を統一。

### A-L-003: `% / %pt / pp / bps` 単位混在
- **Files**: 02 / 08 / 10 で `+10pt` `+10pp` `+10%pt` `+1000bps` が混在。
- **Recommendation**: 「変化幅」は `+1000bps` または `+10pp`、「比率」は `%` で全 file 統一。

### A-L-004: 出典 URL の最終アクセス日不在
- **Files**: 09 / 08 で出典 URL に `(YYYY-MM-DD アクセス)` がない。
- **Recommendation**: 出典は最終アクセス日も付与。

### A-L-005: 章番号スタイル `§1.1.1` vs `1.1.1.` 揺れ
- **Files**: 02 / 03 で `§` の使い方が違う。
- **Recommendation**: 章間参照は `§` 接頭、見出しは `1.1.1` 番号のみ。

### A-L-006: 空行ルール — 表前後の空行が一定でない
- **Files**: 全 file。markdown 表の前後に空行 1 行を置く慣行が一部欠落。
- **Recommendation**: lint で空行ルールを強制。

### A-L-007: bullet `-` と `•` の混在
- **Files**: 03 / 09 で混在。
- **Recommendation**: markdown の標準 `-` で統一。

### A-L-008: 箇条書き内の「。」終止符の有無
- **Files**: 全 file で揺れ。
- **Recommendation**: 短い名詞句は終止符なし、文形は `。` 必須。

### A-L-009: footnote の `(出典: ...)` vs `[出典: ...]` の表記
- **Files**: 02 / 03 / 05 / 09 で混在。
- **Recommendation**: 09 の `[出典: <Title>](URL)` 形式で全 file 統一。

### A-L-010: `(2026-05 時点)` の表記揺れ
- **Files**: 11 / 07 で `(2026.5)` と `(2026-05)` が混在。
- **Recommendation**: ISO `(2026-05)` で統一。

### A-L-011: 通貨記号の前後スペース
- **Files**: `$1M` `$ 1M` `1 M$` が混在。
- **Recommendation**: 英数字直接連結 `$1M / ¥1B` で統一。

### A-L-012: 日本円表記 `¥` と `円` の使い分け
- **Files**: 04b / 07 / 08 で `¥1B` と `1 億円` が混在。
- **Recommendation**: モデル数値・表は `¥`、和文文章中は `円 / 億円`。

### A-L-013: 半角空白 — 数字と単位の間
- **Files**: 02 / 11 で `5M` と `5 M` が混在。
- **Recommendation**: 単位連結はスペースなし、`5M ARR` 形。

### A-L-014: 表見出しの大文字化 (Title Case vs Sentence case)
- **Files**: 02 / 08 で混在。
- **Recommendation**: 表見出しは Sentence case で統一。

### A-L-015: ハイフン と em-dash 混在
- **Files**: 04a `Pre-money / Post-money` と `Pre money / Post money` 揺れ。
- **Recommendation**: 複合語は hyphen 接続。

### A-L-016: footnote 番号 (N1, N2) が 10 のみで使われる
- **Files**: `10` §1.3 (footnote N1, N2 規約)。他 file では使われていない。
- **Recommendation**: 10 §1.3 の規約を全 file の生成テンプレで使う。

### A-L-017: `Q1 / Q2 / Q3 / Q4` のフォーマット — `Q1 26` vs `1Q26` vs `2026Q1`
- **Files**: 01a §4.3 で `\Q0 yy` (`Q2 26`)、05 §1.11 で `Y1` (年単位のみ)、08 で `Q1 2026`。
- **Recommendation**: 表示フォーマットは 01a §4.3 を base、文章中は `Q1 2026`。

### A-L-018: `Pre-Seed / Pre-seed / プレシード` 表記揺れ
- **Files**: 02 L87 (`Pre-Seed`), 08 L84 (`Pre-seed`), 07 L401 (`プレシード`)。
- **Recommendation**: 英表記は `Pre-seed` で統一、和文は `プレシード`。

### A-L-019: `D&A` 略号の展開
- **Files**: 06 L16 (展開あり)、05 / 02 / 11 (展開なし箇所あり)。
- **Recommendation**: 各 file の初出で `D&A (Depreciation & Amortization)` と展開。

### A-L-020: `K / M / B` (千 / 百万 / 十億) の単位
- **Files**: 02 / 03 で `$5K` `5,000$` `5K$` が混在、06 で `¥1B = 10億` の対応表なし。
- **Recommendation**: 06 §0 に対応表 (`K=千、M=百万、B=十億 / Mn=百万、Bn=十億 表記揺れ` 含む) を追加。

### A-L-021: `Diluted shares` と `FDSO` の混用
- **Files**: 04b L60 (FDSO 定義) / 05 §2.6 (`Diluted Share Count`)。同義だが 2 用語並走。
- **Recommendation**: 04b §1.2 で `FDSO = Fully Diluted Shares Outstanding (= Diluted Share Count)` と併記しておく。

### A-L-022: `:` と `：` (全角コロン) 混在
- **Files**: 07 / 10 で混在。
- **Recommendation**: 和文中も `:` (半角)、ラベル直後の用法に統一。

### A-L-023: `Backlog` と `Order Backlog` 表記揺れ
- **Files**: 02 §2.5 (`Backlog`)、05 §2.6 (`order backlog`)。
- **Recommendation**: SaaS 文脈は `Backlog`、IB 文脈は `Order Backlog` で文脈に応じて。

### A-L-024: `Net Burn` と `Burn (net)` 表記揺れ
- **Files**: 02 / 08 / 10 / 11 で揺れ。
- **Recommendation**: `Net Burn` で統一、`(operating + financing exclusive of fundraising)` を初出脚注。

---

## Cross-cutting Patterns
本監査で複数 issue にまたがる構造的パターンを 7 つ抽出する。これらは個別 issue の修正に加え、**corpus 横断の運営ルール** として確立すべき。

### Pattern 1: 「Single Source of Truth (正本) 原則」の不徹底
**該当 issues**: A-C-006 (シート命名)、A-C-002 (Cover タブ色)、A-H-001 (NRR 閾値)、A-H-002 (GRR 閾値)、A-H-003 (CAC Payback 閾値)、A-H-006 (Rule of 40 margin)、A-H-008 (LTV method)、A-H-010 (日本 ETR)、A-H-012 (Cover 必須項目)、A-M-006/007/009/011/014/021。

同一概念が 2-4 ファイルで独立に定義され、相互整合が取られていない。各 file の冒頭に「**この概念の正本は X」/ 「本書はそれを参照する」**」のいずれかを明示するルールを corpus 規約に加えるべき。具体的な「正本マッピング表」を `references/00_INDEX.md` (新設) または `00_design_guidelines.md` 末尾に置き、概念 → 正本ファイルのリストを集中管理する。

### Pattern 2: 「Build-side と Judgment-side の dual verification」の片肺
**該当 issues**: A-H-001 (NRR), A-H-002 (GRR), A-H-005 (Magic Number 計算), A-H-007 (SBC), A-H-008 (LTV), A-H-015 (Quick Ratio), A-H-019 (NRR 公式 A/B)。

08 (judgment-side) と 02 / 05 / 06 (build-side) で **同一指標の閾値・計算式が独立に書かれ**、相互参照が薄い。Skill が「dual verification」を売りにしているにもかかわらず、build と judgment が一致しなければ意味をなさない。**各 build-side メトリクスは、対応する judgment-side 閾値ブロックの ID を脚注で持つ** ルールを設けるべき (例: 02 §3.3 NRR 計算 → `(判断軸は 08 §4.1.2 を参照)`)。

### Pattern 3: 「IB Functional Color と Act Brand Color の混入」
**該当 issues**: A-C-001 (青 #0000FF vs #004F49)、A-C-002 (Cover タブ色)、A-M-024 / A-M-025 (色 hex 揺れ)。

00 §3.7 で「Functional palette と Brand palette は絶対分離」を原則として宣言しているにもかかわらず、01b §6 (L675) と §A.6 で `Hard input = #004F49 (Primary deep, Act brand)` と機能色レイヤーにブランド色が混入。**00 §3.7 の絶対分離原則を 01b 全体に貫徹** し、01b 内で `#004F49` を引用する全箇所をレビューして「装飾レイヤー (cover, header) のみ」に限定する一括書き換えが必要。

### Pattern 4: 「Stage / Segment 別ベンチマークの粒度不揃い」
**該当 issues**: A-H-001 (NRR), A-H-002 (GRR), A-H-003 (CAC Payback), A-H-004 (Burn Multiple), A-H-016 (ARR ステージ)。

同じメトリクスでも file によって Stage 別 / Segment 別 / Quartile 別 / Single value のいずれかで提示され、cross-comparison が困難。**正本となる 02 §8 (出典別ベンチマーク) を以下 3 軸構造で再構築**:
1. Stage (Pre-seed / Seed / A / B / C / D+)
2. Segment (SMB / Mid / Enterprise)
3. Distribution (Bottom 25% / Median / Top 25% / Top 5%)
の **3 次元マトリクス**を提供し、08 / 10 はこのマトリクスの参照のみに留める。

### Pattern 5: 「日本特有論点の正本化」
**該当 issues**: A-H-010 (ETR), A-H-013 (NOL), A-M-019 (409A), A-M-020 (信託型 SO), A-M-021 (税制)。

07 が日本特有事項の正本としてあるが、05 / 06 / 04b で同じ論点を独立に簡略説明し、07 の最新値 (例 31.52%) と乖離。**07 を「日本論点の唯一の正本」と corpus 規約で宣言し**、他 file の日本関連記述は `(07 §X を参照)` のリンクと数値の最終アップデート日付を併記して `Stale` warning を防ぐ。

### Pattern 6: 「Self-reference rot (リンク腐食)」
**該当 issues**: A-C-004 (01a の `01c_*` 参照、01b の `01_modeling_principles.md` 参照)。

ファイル名が変わった (例 `01_modeling_principles.md` → `01a_modeling_standards.md`) のにクロスリンクが古い名前のまま。**ファイル名変更時の grep + replace チェック** を `scripts/health_check.sh` 等で自動化する。`grep -r "01_modeling_principles\|01c_" references/` のような探知 hook が必要。

### Pattern 7: 「数値 Annotation の不徹底」
**該当 issues**: A-C-005 (Snowflake NRR), A-M-026 / A-M-027 (出典年版), A-L-004 (URL アクセス日)。

数値を引用するときの annotation `(出典: <name> <year>, <as-of date>)` が不徹底。スタートアップ benchmark は 2-3 年で陳腐化するため、**全数値に `(YYYY-MM 時点)` を必須化**するルールが必要。05 §0 で「数値ベンチマークは時点依存であるため YYYY-MM を明記」を宣言しているが、02 / 08 / 10 でこのルールが守られない箇所が散在。

---

## 追加: 修正の優先順位 (運用提案)

| Priority | Action | 影響 file |
|---|---|---|
| **P0 (即時)** | A-C-001 (Hard input 色 #0000FF 統一)、A-C-003 (Discount Rate 定義統一)、A-C-004 (リンク修正) | 00, 01a, 01b, 04a |
| **P0** | A-C-006 (シート命名規約) — `scripts/build_model.py` の出力名と直結 | 01a, 06, 11 |
| **P1 (1 週間以内)** | A-C-002 / A-C-005 (Cover タブ色 / Snowflake NRR の 1 値化) | 00, 01a, 01b, 02, 10 |
| **P1** | A-H-001 〜 A-H-008 (主要 SaaS metric の正本化と相互参照) | 02, 05, 06, 08, 10 |
| **P2 (1 ヶ月以内)** | A-H-010 〜 A-H-024 (Japan ETR, J-KISS, NOL, NRR formula 等の精緻化) | 04a, 04b, 05, 06, 07, 11 |
| **P3 (継続)** | A-M-* / A-L-* (style / 用語揃え) | 全 file (lint hook で半自動化推奨) |

---

## 補遺: Issue 検出済みだが本監査で含めなかったもの (将来監査の候補)

- 数値整合性の **詳細検算** (例: 04a §2.6 全数値、04b §2.3 連立方程式、05 §1.11 mid-year DF 系列、08 §1577 ケースの bottom-up 数値) は audit B (Math Audit) として別建てを推奨。
- **出典 URL の生存性** (リンク切れ) は audit C (Liveness Audit) として別建て (本監査の指示通り内部整合のみに限定)。
- **章番号 / TOC の一致** は本監査でも触れたが、各 file 内部の自己整合は audit D (Internal Consistency) で深掘り推奨。

---

> **監査の限界**: 本監査は corpus 24,681 行のうち、grep + 抜粋読み込みで主要な 30-40% を直接読み取った。全行スキャンではなく、`#[0-9A-Fa-f]{6}` / `NRR` / `Magic Number` 等の概念キーワードに沿った縦断的調査に基づく。残り 60-70% (各章の本文細部) には別の細かい矛盾が潜んでいる可能性があり、本リストは "完全網羅" ではなく "主要な構造的・数値的・閾値的矛盾の検出" に重きを置いた。Skill 配信前のレビューでは、これに加えて (a) 数値検算 audit、(b) URL liveness audit、(c) 各 file 内部の章番号 / TOC 整合 audit を推奨する。
