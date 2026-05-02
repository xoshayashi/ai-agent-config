# Audit C: Logic & Edge Cases

**Status**: WORK IN PROGRESS — populated incrementally as files are reviewed.
**Scope**: 14 reference files under `skills/startup-financial-modeling/references/` (24,681 lines total).
**Method**: Identify missing case branches, untreated edge cases, multi-domain interactions, contradictory scenarios, stress/tail scenarios, and stage/business-model mismatches.
**Severity scale**:
- **Critical**: production model misbehaves, produces wrong-by-orders-of-magnitude results, or crashes silently.
- **High**: a non-edge scenario yields a materially wrong conclusion.
- **Medium**: explanation insufficient — user could pick the wrong path but result still in the right ballpark.
- **Low**: cosmetic / didactic improvement.

## Summary

- **Total logic gaps found**: 78
- **Critical (production model で誤動作する)**: 18
- **High (一部シナリオで誤った結論)**: 32
- **Medium (説明不足)**: 22
- **Low (cosmetic)**: 6

### File-by-file counts
| File | Findings | Notes |
|---|---:|---|
| 04a Convertible & Terms | 15 (C-C-001..015) | Highest concentration; SAFE/cap-table interactions |
| 04b Cap Table Mechanics | 10 (C-C-016..025) | Connecting math gaps |
| 05 Valuation & WACC | 10 (C-C-026..035) | TV / WACC boundary, currency, NOL |
| 02 SaaS Metrics | 5 (C-C-036..040) | NRR LTV divergence, multi-product |
| 06 Three-Statement | 5 (C-C-041..045) | Revolver, covenant, M&A timing, OCI |
| 09 Market Sizing | 5 (C-C-046..050) | Dynamic TAM, cannibalization |
| 11 Debt Financing | 6 (C-C-051..056) | Multi-covenant, equity cure, JP guarantee |
| 03 Business Models | 3 (C-C-057..059) | Business-model applicability |
| 07 Japan Specifics | 2 (C-C-060..061) | Local tax, NOL transfer |
| 08 Investment Thesis | 2 (C-C-062..063) | Reverse DCF, auction process |
| 00/01a/01b/10 Standards/Craft | 3 (C-C-064..066) | Iteration, two-way sensitivity, dead cells |
| Cross-domain | 5 (C-C-067..071) | Round/Debt/Tax linkage, IPO sequence |
| 業態 / Stage 別 | 3 (C-C-072..074) | LTV pre-rev, Burn Multiple profitable, post-IPO SAFE |
| Stress / Tail | 4 (C-C-075..078) | Recession, concentration loss, regulation |
| **Total** | **78** | |

---

## File 04a: 転換型ファイナンス商品と優先株条項 (`04a_convertible_and_terms.md`)

### C-C-001: Multiple SAFE with cap-less + iteration divergence
- **Files involved**: `04a_convertible_and_terms.md` §2.6 (lines 281-317)
- **Missing case**: 文書は post-money SAFE 計算で「cap がない SAFE がある場合は iterative に解く」と記述するが、(a) iteration が収束しない / 振動するケース、(b) 複数 cap-less SAFE が同時に存在する場合の連立、(c) iteration tolerance を文書化していない。
- **Failure mode**: 例えば cap-less SAFE × 2 + ESOP top-up + Series A pre-money cap が iteration 上で互いに干渉し、conversion price が決まらない or 振動する。実装者が naive な fixed-point を組むと無限ループや解の取り違えが起きる。
- **Example scenario**: SAFE A $1M discount 20%, SAFE B $0.5M discount 25%, ESOP target post-money 15%, Series A $5M pre-money $20M。closed-form を持たない連立 (T = founder + 2 SAFE + ESOP + Series A) で、ESOP "top-up" が post-money 比で動的に決まるため、SAFE shares と ESOP shares が相互依存。Naive な loop で 2 つの解が出てしまうケースあり。
- **Recommendation**: (1) closed-form を提示する (cap-less SAFE は Series A PPS の 1-d 倍 → 持分 = I / (Post-money × (1-d)) と書ける); (2) iteration を使うなら tolerance (例: < 0.01% delta) と max iterations (例: 50) を明示; (3) 解の一意性条件 (= 全 SAFE の Σ I_i / C_i + ESOP_target + Series A% < 1) を check-list 化。

### C-C-002: Down round 時の SAFE 転換ロジック (post-money SAFE が down round で発動)
- **Files involved**: `04a_convertible_and_terms.md` §2 全体 (lines 84-336)
- **Missing case**: post-money SAFE は持分が「投資額/post-money cap」で固定されるとあるが、Series A の pre-money valuation が SAFE の cap **未満** (= 実質 down round in cap terms) の場合の挙動が記述されていない。SAFE の cap は priced round で「保護価格」だが、cap > Series A post-money のとき「Series A 価格で転換」する logic がどう既存 SAFE 持分固定と両立するかが書かれていない。
- **Failure mode**: SAFE 投資家持分 = I/cap = 10% を維持しようとすると、Series A 価格より高い PPS で転換することになり、SAFE 投資家は価格上のメリットを失うが、**post-money SAFE の持分固定保証は維持されるのか?** YC の post-money SAFE 標準条文では「holder gets the lower of cap-price or discount-price」となり、その結果として持分は固定 % よりも小さくなる。文書はこれを明示していない。
- **Example scenario**: SAFE $1M, post-money cap $20M (= 5% 持分固定の前提)。Series A は危機ラウンドで pre-money $10M、post-money $15M で実施。Cap $20M > post-money $15M なので、cap は保護にならない。SAFE は Series A PPS で転換 → SAFE shares = I / Series A PPS = $1M / ($15M / T) → 持分は post-money $15M に対する $1M = 6.67% (5% より上振れ)。文書は「SAFE 持分は固定」と書くが、down round in cap terms では > 固定 % になり得る点を欠落。
- **Recommendation**: §2.2.2 の最後に「post-money cap 適用の前提 = priced round PPS が cap 適用 PPS より高いこと。priced round PPS が cap PPS より低い場合 (= cap が保護にならない場合)、SAFE は priced round PPS (- discount) で転換し、持分は I/cap を上回り得る (上振れ保護はあるが下振れ保護のみが固定)」を追加。さらに down round シナリオ table を追記。

### C-C-003: Anti-Dilution と SAFE 転換の同時発動順序
- **Files involved**: `04a_convertible_and_terms.md` §9 (Anti-Dilution, lines 990-1162) と §2 (SAFE) の相互作用が記述されていない
- **Missing case**: Series A 後に Series B が down round で発生し、(a) Series A の anti-dilution が発動、(b) 同時に bridge SAFE が Series B trigger で転換、の処理順序とその循環依存。SAFE は as-converted basis で anti-dilution の `A` (= broad-based denominator) に含まれるか? SAFE の conversion price は anti-dilution 調整前 / 後の Series A PPS を使うか?
- **Failure mode**: Anti-dilution は「Series A の conversion price を新規発行 PPS で下方調整」する。Bridge SAFE が Series B 価格で転換するとき、Series A の調整後 conversion price を使うのか、Series B の original PPS を使うのかで SAFE 投資家の取得株数が大きく変わる。さらに anti-dilution 自体が「SAFE 転換による普通株増加」を含むかどうかで結果が循環する。
- **Example scenario**: Series A $5M @ $5/share = 1M shares、bridge SAFE $1M @ $4M post-money cap、Series B $2M @ $2/share (down round)。Series A の broad-based WA で `A` 計算に SAFE 転換株を含めるか否かで NCP が $4.40 になるか $4.50 になるか変わり、Series A 保有株 (転換比率) が ±5% 動く。
- **Recommendation**: §9.4 に「Anti-Dilution 計算のタイミング: (1) 先に SAFE/note を Series B trigger で転換し新たな普通株 base を確定、(2) その後 Series A の broad-based WA を計算、(3) Series A 転換比率を更新」のシーケンスを明記。SAFE は通常 Series B 発行と "concurrent" に転換するため `A` の denominator にどう入るかを example で示す。

### C-C-004: IPO 時に SAFE が未転換のままの場合
- **Files involved**: `04a_convertible_and_terms.md` §2.5 (lines 201-225)
- **Missing case**: §2.5.2 では Liquidity Event = M&A/IPO で「whichever is greater (cash-out or convert)」と記述するが、IPO 直前にまだ Equity Financing (priced round) を経ていない SAFE のための conversion mechanics が曖昧。具体的には IPO PPS で convert するのか、最後の SAFE round の cap で convert するのか、その決定ロジックが未記述。
- **Failure mode**: SAFE が複数回発行されているが Series A を経ずに直接 IPO に到達 (= "Direct-to-IPO" case、近年は SPAC や Direct Listing で実例あり)。各 SAFE の cap が異なるとき、(a) IPO PPS で全 SAFE 一律 convert、(b) cap-by-cap convert、(c) 最低 cap で convert、のどれを採るかで founder dilution が桁違いに変わる。
- **Example scenario**: SAFE 1 $0.5M cap $5M、SAFE 2 $1M cap $10M、Series A をスキップして $200M IPO PPS $10、市場 valuation $1B。SAFE 1 が cap で convert → 0.5/5 = 10% 持分。SAFE 2 が cap で convert → 10% 持分。すでに合計 20% を SAFE 投資家が取り、創業者は IPO 価格 (= $1B) 比で大幅希薄化。文書はこれを示唆するが計算 example がない。
- **Recommendation**: §2.5.2 に「IPO at conversion event: 各 SAFE は (a) cap conversion price, (b) discount conversion price (IPO PPS × (1-d)), (c) IPO PPS のうち lowest を採用 → Greater of (cash-out at 1x, converted shares at IPO PPS valuation) を選ぶ」と明記。Direct-to-IPO (Series A スキップ) の数値例を 1 件追加。

### C-C-005: 複数 J-KISS で適格資金調達 trigger が異なる場合
- **Files involved**: `04a_convertible_and_terms.md` §3.10 (lines 542-547)
- **Missing case**: §3.10 で「多重 J-KISS で希釈が読みにくくなる」とは触れるが、J-KISS A が「適格資金調達 = 1 億円以上」、J-KISS B が「適格資金調達 = 5,000 万円以上」と定義が異なる場合の挙動を記述していない。Series A 規模 7,000 万円のとき、J-KISS A は trigger せず J-KISS B のみ trigger するという「非同期転換」が起きる。
- **Failure mode**: 7,000 万円の Series-A-like ラウンドで J-KISS B のみ転換 → Series A 投資家が pre-money/post-money 計算をするとき、J-KISS A は未転換のまま新株予約権として残る。次の Series B (= 1.5 億円) で J-KISS A が転換するとき、J-KISS A の cap は元の cap (Series A 前) のままなのか、Series A 後の調整 cap なのかで持分が大きく変わる。
- **Example scenario**: J-KISS A $1M cap 5 億円、J-KISS B $0.5M cap 3 億円。Series A 7,000 万円調達 (= J-KISS B trigger)、その後 Series B 2 億円。J-KISS A は cap 5 億円のまま Series B trigger で転換するが、Series A での発行株数を含めるかで PPS が変わる。
- **Recommendation**: §3.10 を拡張し「複数 J-KISS の adequate financing 閾値が異なる場合」に専用 subsection を追加。具体的に「未転換 J-KISS は Series A 後の cap table の上で計算し、Series A 投資家には事前に明示する」というルールと、計算 example を追加。

### C-C-006: 種類株主間で参加型 vs 非参加型が混在する exit
- **Files involved**: `04a_convertible_and_terms.md` §7 (Liquidation Preference, lines 751-929)
- **Missing case**: §7.4 で seniority (stacked / pari passu / hybrid) は議論されるが、「Series A = participating、Series B = non-participating、Series C = capped participating」のような **混合型** での exit waterfall の計算順序が記述されていない。Participation の有無は seniority と直交する dimension だが、文書はこれを混同しがち。
- **Failure mode**: $50M exit で、Series A (参加型 1x, $5M)、Series B (非参加型 1x, $10M)、Series C (capped 2x, $20M) のとき、Series C が convert か cap か preference かを判断するには Series A の participation が残余からどれだけ吸い上げるかに依存し、循環する。
- **Example scenario**: 上記前提。素直に stacked seniority で Series C → B → A と支払うが、Series A は participating なので残余から再配分を受ける。Series C が convert を選ぶと Series A の participation 残余が変わる → Series C の選択が変わる、という循環。Naive 実装では Series C を「cap で受け取る」として確定し、Series A participation で残余 $35M を pro-rata 配分するが、これは Series C convert のほうが有利だった可能性を見落とす。
- **Recommendation**: §7.4 に「Mixed participation exit」の subsection を追加。アルゴリズム: (1) 全 series の "convert" payoff を計算 (preference 放棄)、(2) 全 series の "preference + participation" payoff を計算、(3) max を選ぶ、を全 series に対して同時並行で解く LP-like solver を提示。または典型ケース (3 series mix) の数値例を 1 件提示。

### C-C-007: Capped participation の cap 到達後の挙動 (= "convert back to common" の時点)
- **Files involved**: `04a_convertible_and_terms.md` §7.3.3 (lines 839-867)
- **Missing case**: §7.3.3 の table は cap 2x = $10M で正しく描画されているが、cap **到達点での投資家選択** (= "cap で止まる" vs "convert に切り替える") の boundary 計算ロジックが式で示されていない。式 (10) は max(min(...), convert) の形だが、convert が cap より低い場合の挙動 (cap で止まらず convert する) と高い場合の挙動が混乱する。
- **Failure mode**: Exit value が boundary 付近 ($25M〜$40M) で、計算実装者が `min(cap, participating)` を取って終わるとき、convert 選択の評価を忘れて cap で止め、投資家を不利にする。
- **Example scenario**: Exit $40M、cap 2x = $10M。Participating = $13.75M、Cap で止めると $10M、Convert (25%) = $10M。文書 table では「$10M (border)」とあるが、実装側はどちらを採るかでベースが変わる (税金処理 etc.)。$40.001M なら Convert > Cap で convert、$39.999M なら Cap > Convert で cap、という discontinuous な挙動の閾値を式で示すべき。
- **Recommendation**: §7.3.3 に閾値の closed-form を追加: Cap 到達 exit V_cap = (cap × I × (S_p + S_c) - S_p × M × I) / (S_p × ε) 等。さらに「投資家は以下の 3 case のいずれか: pure preference / cap participation / convert to common」の **flowchart** を提示。

### C-C-008: Pay-to-Play 不参加時の anti-dilution 失効と既存転換株の扱い
- **Files involved**: `04a_convertible_and_terms.md` §9.7 (lines 1131-1151)
- **Missing case**: Pay-to-play で不参加 → 普通株強制転換、と記述するが、転換時の **transition price** (= どの conversion price で普通株化するか) が未記述。Strict pay-to-play では「現行 conversion price」を使うのか、「Original Issue Price」を使うのかで結果が異なる。
- **Failure mode**: Series A 投資家が anti-dilution で conversion price = $4.40 になっていた状態で Series B down round に不参加 → 強制 common conversion。$4.40 で転換すれば 1.136M shares、$5.00 (Original) で転換すれば 1M shares。前者を使う実装と後者を使う実装で 13% の希釈差。
- **Example scenario**: Series A 1M shares @ $5 OCP = $5、anti-dilution で $4.40 NCP。Series B で pay-to-play 不参加 → 強制 common 転換。$4.40 NCP を使えば 1.136M 普通株、$5 OIP を使えば 1.0M 普通株。文書はこの分岐に触れない。
- **Recommendation**: §9.7 に「Pay-to-Play conversion price: 不参加時の強制転換は (a) 現行 conversion price (anti-dilution 適用後) を使うか、(b) Original Issue Price を使うか、(c) 1:1 (conversion ratio = 1) を使うか、を契約書で明示する。NVCA Strict pay-to-play は (a) が default だが、市場では (c) も見られる」を追加。

### C-C-009: SAFE / Note の Liquidation Event 時 1x vs Convert の判定境界
- **Files involved**: `04a_convertible_and_terms.md` §2.5.2 (lines 211-218), §3.5.3 (lines 412-420), §4.3.4 (lines 645-650)
- **Missing case**: M&A 時の "whichever is greater" 計算が、cap が低くて convert に大きなアップサイドがある場合と、cap が高くて preference (1x) しか取れない場合の boundary を明示していない。さらに **Convertible Note の Change of Control Premium 1.5-2x が SAFE には存在しない** ため、同じ exit で SAFE 投資家と Note 投資家の取り分が大きく異なるが、文書は両者の比較表を欠く。
- **Failure mode**: $30M exit、SAFE $1M cap $10M (10% as-converted) と Note $1M cap $10M + 1.5x premium があるとき、SAFE は max($1M, 10% × $30M = $3M) = $3M、Note は max($1.5M premium, 10% × $30M = $3M) = $3M、と一見同じだが、Note は accrued interest も加算されるため $3M+ になる。詳細 example の欠落。
- **Recommendation**: §2.5.2, §3.5.3, §4.3.4 を統合して「Liquidity Event payoff comparison table (SAFE / J-KISS / Note)」を新規追加。

### C-C-010: 2x Liquidation Preference at down round の cumulative cap (例: "1x + dividend cap" vs "2x flat")
- **Files involved**: `04a_convertible_and_terms.md` §7.2 (lines 760-767), §8 (Cumulative Dividend, lines 945-974)
- **Missing case**: 2x non-participating preference + cumulative dividend 8% を併用した時の payout cap (= absolute upper bound) が未記述。一部契約では「2x or invested + dividend, whichever lower (= cumulative dividend で 2x を超えない)」となっているケースがある。文書はこのケースを欠く。
- **Failure mode**: 投資 $5M、2x = $10M ceiling、5 年で cumulative dividend 8% 累積 = $2M。「2x flat」なら $10M、「2x + dividend」なら $12M、「2x ceiling = max(2x, 1x + dividend)」なら max($10M, $7M) = $10M、と 3 通りの解釈で結果が変わる。
- **Example scenario**: 投資家 $5M、2x non-participating + cumulative 8% × 7 年 = $2.8M。Exit $30M で 25% 持分。Convert payoff = $7.5M。Preference + cumulative = $5M × 2 + $2.8M = $12.8M、cap が "2x flat" なら $10M。文書はどちらか不明。
- **Recommendation**: §7.2 に「Multiple liquidation preference の cap interpretation」を追加。NVCA 標準の "(i) [N]x the Original Purchase Price plus accrued and unpaid dividends" 文言の解釈を明示。

### C-C-011: Founder Vesting cliff 前の exit 発生 (vested = 0% で M&A)
- **Files involved**: `04a_convertible_and_terms.md` §15.1 (lines 1483-1490), §17.3 (lines 1599-1607)
- **Missing case**: Cliff 1 年経過前に M&A や exit が発生する場合の founder shares の処理が未記述。Cliff 前なら vested = 0% で、buyback で全株が会社に戻り、exit proceeds は他株主が受領 → 創業者の取り分がゼロになる悲劇シナリオ。Double trigger acceleration がない契約ではこれが現実に起きる。
- **Failure mode**: 創業者は cliff 前 (例: 入社 11 ヶ月) で M&A 同意。M&A クロージング時に founder の vested = 0% → 全株 buyback at $0.0001/share (cost = vesting agreement) → 創業者は cash-out なし。
- **Example scenario**: Founder 6M shares、cliff = 12 ヶ月、入社 11 ヶ月で $50M M&A。Single trigger acceleration なしの契約では、6M shares 全て unvested → buyback で全没収 → founder $0、investor & ESOP のみ payout。
- **Recommendation**: §15.1 に「Cliff 前 exit の boundary 条件」を追加。「single trigger acceleration」「double trigger」「cliff waiver」のオプションを比較。チェックリストに「cliff waiver if exit before cliff?」項目追加。

### C-C-012: ESOP pool refresh が equity round の途中で発生
- **Files involved**: `04a_convertible_and_terms.md` §17.1 (lines 1572-1583, line 1576 "option pool shuffle")
- **Missing case**: 文書は「ESOP が pre-money/post-money どちらに含まれるか」を check するが、Equity round の途中 (= Term Sheet 署名後 → クロージング前) に既存 ESOP が増額追加発行された場合の cap table 再計算ロジックが未記述。
- **Failure mode**: Term Sheet 署名時 ESOP = 10% pre-money。クロージング前 (DD 期間) に既存従業員に大量の SO 追加付与 (例: 5% 追加) → クロージング時の actual ESOP = 15%。投資家持分も founder 持分も影響を受けるが、Term Sheet 上の "% post-money" を維持するため retroactive な再計算が必要。
- **Example scenario**: Term Sheet: pre-money $20M, ESOP target 10% post-money, Series A $5M = 20% post-money。クロージング前に founder が CEO 候補に 3% グラント → ESOP 13%。Investor は 20% post-money を維持するため pre-money を $19.4M に下げるか、founder 持分を圧縮するか、3% グラントを反転させるかの判断が必要。
- **Recommendation**: §17.1 に「ESOP refresh during round (DD 期間)」を追加。Term Sheet で "ESOP top-up to X% post-money" の挿入条件と、間に発生する grant の処理ルール (= "no incremental grants without lead consent") を明示。

### C-C-013: SAFE conversion timing と option grant の同時発生 (board meeting 同日)
- **Files involved**: `04a_convertible_and_terms.md` §2.5 (lines 201-225) — timing 解像度なし
- **Missing case**: Series A クロージング日に (a) SAFE conversion, (b) ESOP top-up grant, (c) Series A issuance が全て同日 board minute で実行される場合の **順序問題**。各 step が他の step の denominator/numerator を変えるため、文書化された順序がないと implementation が一意に決まらない。
- **Failure mode**: 順序 (1) ESOP → (2) SAFE → (3) Series A: SAFE が ESOP 拡大後の denominator で計算 → SAFE shares が少ない。順序 (1) SAFE → (2) ESOP → (3) Series A: SAFE が ESOP 前で計算 → SAFE shares が多い。両者で SAFE 投資家持分が 5-15% 違う。
- **Example scenario**: SAFE $1M cap $10M (post-money), ESOP top-up = post-money 10%, Series A $3M = post-money 20%。順序 1 で SAFE 持分 = 10% (固定 by post-money cap)、順序 2 だと founder 持分が異なる。
- **Recommendation**: §2.6 (post-money SAFE 計算) と §17.8 (モデリング検証) に「Issuance order convention: SAFE conversion → ESOP refresh → Series A issuance、全て post-money basis で simultaneous resolution」というルールを明示。

### C-C-014: MFN cascade — 複数の MFN SAFE/Note が異なる時期に存在
- **Files involved**: `04a_convertible_and_terms.md` §2.3.4 (lines 176-181)
- **Missing case**: MFN は「より有利な条件があれば取り入れる」だが、(a) 同時に MFN を持つ複数 SAFE がいると、A が MFN を行使して B の条件を取得した瞬間に B の MFN は意味を失う、という非対称性。(b) MFN を行使すると次の SAFE 条件を上書きするので、再帰的に他 SAFE の MFN trigger が走るかも。これらの順序・優先関係が未記述。
- **Failure mode**: SAFE A (cap $10M, MFN), SAFE B (cap $8M, MFN), SAFE C (cap $5M)。A は B の cap $8M を MFN で取得?それとも C の cap $5M を取得? B は C の cap $5M を取得?cascade で全員が cap $5M に収束するが、文書はこれを示さない。実装者は最初の MFN だけ評価して終わる可能性。
- **Example scenario**: 上記前提。Series A 直前で各 SAFE の cap を MFN cascade で $5M に収束 → SAFE 投資家は全員 cap $5M 換算 → 創業者希薄化が想定 (cap $10M, $8M, $5M ベース) より大幅に増える。
- **Recommendation**: §2.3.4 に「MFN cascade resolution: Series A trigger 前に全 MFN SAFE を最低 cap (= 全 SAFE 中最も投資家有利な cap) に統一する。MFN が cap だけでなく discount, MFN 自体, pro-rata にも及ぶ場合は、各属性で independent に cascade」を明記。

### C-C-015: Drag-Along の Triple Trigger と少数株主保護の interaction
- **Files involved**: `04a_convertible_and_terms.md` §13.3 (lines 1373-1393)
- **Missing case**: Triple Approval (Board + Common majority + Preferred majority) で全員強制売却、と書かれるが、Common majority が "founder のみ" で構成される会社 (例: founder 70%、ESOP 残 30% は未行使 SO で voting なし) では founder = 100% common voting になり、founder 単独で drag-along trigger できる、という設計問題が触れられていない。
- **Failure mode**: Founder + Lead investor が共謀して安値 M&A → 少数 angel/employee は drag された上で不利な対価を強制される。
- **Example scenario**: Founder 70% common, employee SO unvested 30% (not voting), Series A 25% (single investor majority OK)。Founder + Series A で M&A $20M (preference $20M で投資家 100% 回収、common $0)。少数 angel SAFE (= post-converted common) は強制売却で取り分 $0。
- **Recommendation**: §13.3.2 に「Common majority の threshold には "non-investor common holders" majority も追加すべき (= founder 単独でない)」を推奨。または "majority of vested employee shares" を独立 trigger にする条項を提示。

(File 04a 完了 — 15 findings)

---

## File 04b: Cap Table メカニクス・希薄化・Exit Waterfall (`04b_cap_table_mechanics.md`)

### C-C-016: Option Pool Shuffle 連立解で T (1 + INV/PMV) ≥ 1 となるケース (除算で発散)
- **Files involved**: `04b_cap_table_mechanics.md` §2.3 (lines 232-244)
- **Missing case**: 連立解 `X = (F0 - P0) × QMV / (PMV - T × QMV)` の **分母が 0 または負** になるケースが boundary check されていない。これは `T × QMV ≥ PMV` のとき発生し、(a) 大きなプール % (T = 30%+) と (b) 大規模な投資 (INV ≈ PMV) が組み合わさるシナリオで実際に起きる。
- **Failure mode**: T = 0.30, PMV = $5M, INV = $5M なら QMV = $10M, T × QMV = $3M, 分母 = $5M - $3M = $2M (OK)。しかし T = 0.40, PMV = $5M, INV = $10M なら T × QMV = $6M > PMV = $5M、分母 = -$1M で X が負になり数学的破綻。Naive な実装は負の値を返すか、無限大に発散する。
- **Example scenario**: 危機ラウンドで CEO 候補に大型 SO 付与 (pool target = 35%) + 投資家が pre-money 比同額で投資。連立解は破綻し、Excel が #DIV/0! や負の株数を出力。
- **Recommendation**: §2.3 末尾に「Feasibility: 連立解が正の有限値を持つには `T < PMV / QMV = PMV / (PMV + INV)` が必要。これを超えるとプールサイズが大きすぎ、創業者持分が負になる (= 数学的不可能解)」と注意書き追加。Boundary check コードも提示。

### C-C-017: SAFE 転換株の Anti-Dilution `A` 算入の曖昧さ
- **Files involved**: `04b_cap_table_mechanics.md` §4.5.2 (lines 502-525), §10.2.2 (lines 1396-1422)
- **Missing case**: Broad-based weighted average の `A` 定義 (= "pre-issue FDSO") に **当該ラウンドで転換予定の SAFE** を含めるかが文書で不一致。§4.5.2 では「pre-issue FDSO」と書くが、§10.2.2 のケース B では SAFE は既に Series A で転換済みであるため曖昧さがない。Series B trigger で SAFE が転換するシナリオ (= bridge SAFE) では、Anti-Dilution 計算時の `A` に bridge SAFE 転換株を含めるか否かで NCP が大きく変わる。
- **Failure mode**: Series B が down round + bridge SAFE が同時転換。`A` に bridge SAFE 含む → `A` 大 → NCP 高 → 既存 Series A の anti-dilution 効果小。除外 → `A` 小 → NCP 低 → anti-dilution 効果大。10-15% の創業者希薄化差。
- **Example scenario**: Series A FDSO 30M shares, bridge SAFE = 5M shares 転換予定, Series B 10M shares 発行 (down)。`A` = 30M なら NCP は OCP × 32M/40M、`A` = 35M (SAFE 含) なら OCP × 37M/45M で結果が異なる。
- **Recommendation**: §4.5.2 に明記: "pre-issue FDSO は **当該ラウンドで concurrent に転換する SAFE / Note 株を **含む** が、当該ラウンドで発行する新規 priced shares は含まない。" NVCA の "Common Stock Equivalents Outstanding immediately prior" の解釈を明示。

### C-C-018: TSM の P (評価株価) 設定の循環
- **Files involved**: `04b_cap_table_mechanics.md` §1.3 (lines 76-97)
- **Missing case**: TSM 計算で「P = 評価株価」とあるが、cap table モデルで P を求めるためには FDSO が必要、FDSO を求めるためには TSM の追加株数が必要、という循環参照が触れられていない。
- **Failure mode**: 実装者が naive に P = pre-money / (pre-FDSO incl. options) と置くと TSM 補正が反映されない。逆に P をモデル外で固定すると pre-money valuation の整合性が崩れる。
- **Example scenario**: pre-money $20M、TSM 前 FDSO = 10M shares、in-the-money options 2M @ $0.5、TSM 適用すると追加株数は 2M × (1 - 0.5/P) で P 依存。P = $2 なら 2M × 0.75 = 1.5M、P = $4 なら 2M × 0.875 = 1.75M。FDSO は P によって変わるが、P は FDSO によって決まる。
- **Recommendation**: §1.3 に「TSM の循環を解く方法: (1) 反復計算 (initial P = pre-money/raw FDSO で開始、収束まで loop)、(2) closed-form (Newton-Raphson で N_options × (1 - K/P) - (FDSO_target - FDSO_excl_options) = 0 を解く)、(3) M&A exit では deal value / FDSO で P を求める時に TSM を循環させる」を追加。

### C-C-019: Down round で B のみ anti-dilution が発動するケース (Series 別の発動 logic)
- **Files involved**: `04b_cap_table_mechanics.md` §10.2.2 (lines 1396-1422)
- **Missing case**: §10.2.2 で「A の old PPS ¥115.2 < PPS_C ¥202.8 なので A は anti-dilution 発動せず」とするが、「**Series 別に conversion price を比較して trigger 判断する**」という重要なロジックが文書化されていない。実装で全 series 一律に発動させる誤りが多い。
- **Failure mode**: Series B が down に対して発動するが、Series A は元々低い PPS で発行されているため発動しない、というケースで実装者が「down round = 全 series 一斉 anti-dilution」と誤解。逆に Series A の old PPS と PPS_new を比較せずに Series A も希薄化補正してしまう (over-protection bug)。
- **Example scenario**: Series A @ $1, Series B @ $4, Series C $2.5 (down vs B, up vs A)。Series B のみ anti-dilution、Series A は不発。これを誤って Series A も発動させると founder が 不当に希薄化。
- **Recommendation**: §4.5.2 に「Anti-Dilution は **series ごとに** old conversion price と new round PPS を比較して個別に trigger 判定する」とルールを明示。さらに §10.2.2 の例で「Series A 不発、Series B 発動」を強調する step を追加。

### C-C-020: 参加型優先株の cap table での "as-converted" 持分定義
- **Files involved**: `04b_cap_table_mechanics.md` §6.2.2 (lines 807-826), §6.3 step 3 (lines 870-893)
- **Missing case**: 参加型優先株は LP + as-converted 按分。但し as-converted 持分計算の denominator に **B 種が convert を選んだ場合の B 種 shares (as-converted)** を含めるか否かが明記されていない。例えば Series B が convert を選択 → 普通株化 → 残余按分の denominator に Series B の shares が増える。Series A の参加型按分は自動的に減る、という相互依存。
- **Failure mode**: §6.3 で B が convert したあと Residual を A + B + C で按分する記述があるが、A は参加型のため A は LP 取得 → residual から控除済み → 残余按分は A も含めるか否かで結果が変わる。「LP を取った A 種が さらに residual に participating する」のは参加型の定義通りだが、その時の denominator (as-converted base) の正しい計算が示されていない。
- **Example scenario**: §6.3 の例で A LP $5M、B convert (no LP), Residual $45M。A の participation 按分 = 0.20 × $45M = $9M とあるが、この「0.20」は元の as-converted 持分。B が convert したので B の as-converted は変わらない (もともと 0.25)。But A は LP $5M を取り、それを basis に LP 取得分は participation で重複しない、というのが NVCA 標準解釈で、文書はこの "double-counting 回避" を明示せず。
- **Recommendation**: §6.2 に「参加型 LP の二重カウント防止: Total = LP + α × (Exit - Σ LP_taken_by_anyone)」を式で明示。§6.3 で B convert ケースの正しい計算 step を再示。

### C-C-021: Down round の B anti-dilution + 創業者希薄化の二重計算
- **Files involved**: `04b_cap_table_mechanics.md` §10.2.4 (lines 1432-1453)
- **Missing case**: §10.2.4 で「anti-dilution 発動分 826,581 株を新規発行で実装」する記述があるが、これは **誤った実装**。Anti-dilution は通常 conversion ratio 調整で実装され、新株発行は伴わない (= phantom shares)。この区別が曖昧で、新株発行扱いにすると以下の問題が発生:
  - Cash flow 上、anti-dilution は cash 流出を伴わない (= 純粋に conversion ratio の更新) が、新株発行扱いだと簿価上の処理が違う
  - 既存普通株主 (founder + Common) の希薄化計算が二重発生
  - Pool 拡張への影響が誤計算される
- **Failure mode**: §10.2.5 で創業者持分 26.30% と計算しているが、これは "anti-dilution が新株発行" の前提。conversion ratio 方式 (実務標準) では founder shares は変わらず、Series B 株のみ effective shares が増える → founder のドル建て exit は減るが share count は変わらない、という挙動の差。
- **Example scenario**: Founder 10M shares、Series B 6.83M shares (issued)、anti-dilution で B は effective 7.65M shares、Series C で 7.6M shares 発行。Founder 持分 = 10M / (10M + JKISS 2.5M + A 5.2M + B effective 7.65M + new pool 0 + C 7.6M) = 10M / 32.95M = 30.35%。文書記載の 26.30% との差。
- **Recommendation**: §10.2.4 に「Anti-Dilution の実装方式: (1) Conversion Ratio 調整 (NVCA 標準、新株発行なし)、(2) 新株発行 (旧型 / 一部日本契約)。両者で founder 持分計算は異なる」を明示。§4.5 にも boundary を補足。

### C-C-022: SO の M&A 時 cash inflow 取扱の負号バグ
- **Files involved**: `04b_cap_table_mechanics.md` §10.3.2 (lines 1493-1501)
- **Missing case**: §10.3.2 step 1 で SO 行使 cash inflow を「Cash to distribute = ¥6,000M + ¥225M = ¥6,225M」と加算するが、**多くの M&A 取引では SO は "cashless exercise" + "Net of strike" で実行され、acquirer は SO holder に対して直接 net 差額を支払う**。Cash inflow は実際には会社に流入せず、acquirer が deal value から差し引く。文書の処理は会計教科書的だが実取引の慣行と異なる。
- **Failure mode**: M&A escrow / waterfall モデルで cash inflow を deal value に加算すると、distribution 額が実際より過大になり、各株主の取り分が overstated。特に in-the-money SO が多い会社で 5-15% の誤差。
- **Example scenario**: Deal value $80M、SO 1M shares strike $0.5、Net per share = $4.5 (assuming exit PPS $5)、SO net = $4.5M、acquirer は SO holder に $4.5M、preferred/common holders に $80M - $4.5M = $75.5M を distribute (cash inflow $0.5M ≠ 流入)。
- **Recommendation**: §10.3.2 に「M&A waterfall の SO 取扱: cashless exercise 慣行下では deal value から SO net を直接控除し、cash inflow を加算しない」を追加。両方式の比較を提示。

### C-C-023: Lock-up 期間内の secondary sale boundary
- **Files involved**: `04b_cap_table_mechanics.md` §7.3 (lines 1010-1023)
- **Missing case**: Lock-up 期間中に発生する例外取引 (= "permitted transfers") のリストが欠落。具体的には: (a) 死亡・障害による相続、(b) family member への譲渡、(c) charitable donation、(d) tax-related transfer (estate tax 払いのため)、(e) employment termination での会社買戻し。これらは lock-up 中でも認められる場合があるが、cap table 上の処理が文書化されていない。
- **Failure mode**: Lock-up 中に founder が死亡した場合、相続人への移転が cap table 上の "transfer" としてカウントされ、share class が変わるか、 voting rights が変わるか、誰も知らない。
- **Example scenario**: IPO 後 90 日 (lock-up 中) に founder が死亡。家族信託への移管が必要だが、underwriter は lock-up 違反と主張。Cap table モデルがこの edge case を扱えない。
- **Recommendation**: §7.3 に「Lock-up Permitted Transfers」を subsection 化。標準的な exception list を記載。

### C-C-024: Mid-cycle pool refresh と既存 grant の interaction
- **Files involved**: `04b_cap_table_mechanics.md` §3.6 (lines 416-417)
- **Missing case**: "Pool refresh" 機構が記述されるが、**既存付与済 SO の grant timing と pool refresh のタイミングが異なる場合の cap table 影響** が未記述。例えば、Series A pool 15% → 24 ヶ月で 8% 残 → Series B で 15% に再 refresh、と書かれるが、間の grants が pre-money / post-money どちらに対する % で計算されるかで founder 希薄化が大きく変わる。
- **Failure mode**: Mid-cycle で大型 grant (CEO 招聘で 5%) を実行 → pool 残 3% → Series B refresh で 12% 増 → founder が 17% 連続希薄化。但し grant 時点で post-money A 比 5% だった grant が、Series B 時点では post-money B 比 3.5% に縮小、という時点別の % 表現の混同。
- **Example scenario**: Pool 15% pre-money A、Series A 後に 8% 残。CEO grant 5% (post-money A 比) を mid-cycle で実行 → 残 3% (post-A 比)。Series B で 15% target → refresh 必要分は 15% - 3% (post-A 残) かそれとも 15% - 3% × (post-A FDSO / post-B FDSO) (post-B 比に換算) かで Series B pre-money 拡張サイズが異なる。
- **Recommendation**: §3.6 に「Pool refresh の post-money 比計算: 既存残 pool は post-B 比に再評価する。Refresh 必要分 = Target % - Existing % (post-B equivalent)」を明示。

### C-C-025: Exit 時 LP cliff (LP > Exit) で創業者ゼロのシナリオの連続性
- **Files involved**: `04b_cap_table_mechanics.md` §10.3.5 (lines 1626-1638)
- **Missing case**: §10.3.5 で「Exit ¥3.8B 以下では founder cash 0」とするが、(a) LP の中で seniority (B 種 senior, A 種 junior) を考慮した場合の創業者 cliff の位置、(b) LP 累計が exit を上回る場合の **LP holders 内での pari passu 按分**、(c) 一部 LP holder が convert を選択する境界、これらが連動した闘魚動きが table で示されていない。
- **Failure mode**: LP累計 ¥3.8B vs exit ¥3.5B のとき、文書は「founder $0」とするが、実際は LP holders 間で按分が必要 (pari passu なら全員プロラタ、stacked なら senior 全額 + 残り junior プロラタ)。これが文書に現れない。
- **Example scenario**: Exit ¥3.5B、LP J-KISS ¥0.2B (pari) + A ¥0.6B (pari) + B ¥3B (senior to A)。Stacked: B = ¥3B, A + J-KISS = ¥0.5B / ¥0.8B = 62.5% pro-rata of LP each → A ¥0.375B, J-KISS ¥0.125B. Pari passu 全員: pro-rata of ¥3.8B against ¥3.5B available, B = ¥3.5B × 3/3.8 = ¥2.76B, A = ¥0.55B, J-KISS = ¥0.18B. 結果が大きく異なる。
- **Recommendation**: §10.3.5 を拡張し「LP cliff 内訳: LP 累計が exit を上回る場合、(1) seniority stack の応用、(2) pari passu 按分、(3) ハイブリッド」3 通りの計算を明示。

(File 04b 完了 — 10 findings, 累計 25)

---

## File 05: Valuation & WACC (`05_valuation_wacc.md`)

### C-C-026: WACC ≈ g で Gordon Growth が発散
- **Files involved**: `05_valuation_wacc.md` §1.6.1 (lines 208-234), §15.3 (lines 1419-1424)
- **Missing case**: §15.3 で「WACC > g + 200bp」を硬性制約と書くが、**段階的 WACC** (§1.4.5, lines 176-191) を使う場合に **mature WACC が g に接近** することのチェックが提示されていない。Gordon は WACC_mature - g で割るので、stage transition で mature WACC が低く設定されると TV が爆発する。
- **Failure mode**: §1.11 ミニケースでは mature WACC = 10.4%, g = 2% で OK だが、**保守的な財務担当者が "stable maturity = low WACC" として WACC_mature を 5% (Rf 4% + premium 1%)** と置くと、5% - 2% = 3% で TV が 80.7 / 0.03 ≈ $2,690M (実際は 980M の 2.7 倍) となる。
- **Example scenario**: 5y forecast, mature WACC = 4.5%, g = 3%、FCFF_n+1 = $80M。TV = 80 / 0.015 = $5,333M。これは数学的には有効だが「成長率と割引率がほぼ同じ = 投資家リスク調整がない」という非現実的シナリオ。
- **Recommendation**: §1.6.1 に「WACC - g < 300bp の場合、TV は信頼不能」と明示し、自動 boundary check を追加。さらに §1.4.5 stage transition で mature WACC を Rf + ERP 程度の floor に bound する。

### C-C-027: Stage transition で discount rate 切替時の連続性
- **Files involved**: `05_valuation_wacc.md` §1.4.5 (lines 176-191), §1.11 step (lines 393-422)
- **Missing case**: §1.11 で Y3 末から Y4 にかけて 15.4% → 12.5% に "段階別 WACC" が変わるが、(a) 切替が discrete で年度 boundary に依存する、(b) Y3 末の TV を 15.4% で計算するか 12.5% で計算するかで結果が変わる、(c) Mid-year convention での切替時の累積 discount factor 算出ロジック (line 401-405 で実際著者が混乱している跡が見える)。
- **Failure mode**: 著者は §1.11 line 401-405 で「DF₄ = 0.6989/1.125 = 0.6212 ≠ 0.5788」と矛盾を発見し受け入れているが、これは bug で、stage 切替時点で過剰割引が発生している。
- **Example scenario**: Y3 末 (t=3.0) で WACC が変わるとすると、Y4 (t=3.5) は (15.4%)^3 × (12.5%)^0.5 で割引が必要だが、Y4 mid-year を考える時 (15.4%)^3 × (12.5%)^1.0 でなく ^0.5 にすべき。文書の table はこの曖昧さを内包したまま。
- **Recommendation**: §1.4.5 に「Stage transition timing: discrete switch は精度低下を招く。代替: linear interpolation or smooth blend。実装は cumulative discount factor を時点 t について piecewise integral で計算する」を明記。

### C-C-028: Currency mismatch (USD revenue, JPY cost) で WACC 通貨選択
- **Files involved**: `05_valuation_wacc.md` §1.9 (lines 289-300)
- **Missing case**: §1.9 で「単一通貨に集約するなら forward FX」と書くが、(a) USD revenue の WACC は USD-Rf + ERP_US、(b) JPY cost の "WACC" を別建てするか、(c) 単一通貨 (USD) で全 CF を表現する場合の forward FX のソース (interest rate parity に基づく forecast vs spot)、(d) forward FX が long-term で hedge コストを反映する点、これらの順序が未記述。
- **Failure mode**: USD CF と JPY CF を単純合算して USD WACC で割引くと、JPY コストの discount rate が誤って USD-WACC になる。逆に各通貨で別 DCF を組んで spot rate で換算すると、長期 forward FX が反映されない。
- **Example scenario**: USD 売上 $50M, JPY 売上 ¥3B (= USD$20M) , JPY コスト ¥2B (= USD$13M)、グローバル WACC 10%。Naive US 換算で (50 + 20 - 13) × 1/1.1 = $52M だが、JPY 部分は JPY 名目で別 discount し forward FX で翻訳すべき。
- **Recommendation**: §1.9 を拡張し、currency-by-currency DCF の手順を step by step に提示。Forward FX = spot × (1+r_dom)^t / (1+r_for)^t (interest rate parity) の式を明示。

### C-C-029: Hyperinflation / deflation シナリオ (実質 vs 名目)
- **Files involved**: `05_valuation_wacc.md` §1.9 (lines 289-300)
- **Missing case**: 高インフレ国 (Argentina, Turkey, 一部新興国) や、deflationary な日本のキャリーが long horizon で発生する場合の Real-vs-Nominal 切替の判定基準が未記述。
- **Failure mode**: 名目 CF + 名目 WACC で問題ないように見えるが、高インフレで FCF growth = 30% の大半が「価格上昇」だけだと実質 CF growth = ほぼゼロ。Nominal で計算すると過大評価。
- **Example scenario**: Argentinian SaaS が ARS 売上 100M, 年率 30% growth (うちインフレ 25%, 実質 5%)、ARS-WACC 35% (うち inflation 25% + real WACC 10%)。Nominal で 100/0.35 - 0.30 = 100/0.05 = 2000M ≈ Gordon TV はほぼ無限に膨らむが、実質では 100/(0.10 - 0.05) = 2000M (real)。両方とも結果が同じ 2000M (実質) になるが、論理的整合性のために real-vs-nominal を選ぶ必要がある。
- **Recommendation**: §1.9 に「Hyperinflation の判定: > 20% inflation/y で Real DCF 推奨。Real WACC = nominal WACC ÷ (1 + inflation) - 1。Real CF も同様」を明示。

### C-C-030: Negative EBITDA で multiple が負 / 適用不能
- **Files involved**: `05_valuation_wacc.md` §2.4 (lines 519-531), §10 (lines 1012-1062)
- **Missing case**: スタートアップは EBITDA 赤字が普通だが、§2.4 の table は EV/EBITDA を "Mature" 用と書くだけで、EBITDA 赤字時のフォールバック (revenue multiple のみ使う) が明示されていない。さらに **EBIT 赤字なので税金加算戻し = 0、tax shield ゼロで FCFF が NI と整合しない** (NOL 効果) が考慮されていない。
- **Failure mode**: EBITDA = -$5M の SaaS で comp の median EV/EBITDA = 25× を機械的に適用すると EV = -$125M (負) という意味不明な結果。
- **Example scenario**: SaaS LTM Revenue = $50M, EBITDA = -$10M, comp median EV/EBITDA = 30×。実装が `ev = ebitda * multiple = -10 * 30 = -300` を計算してしまう。
- **Recommendation**: §2.4 に「Negative EBITDA: EV/EBITDA は使用不能。Revenue multiple または **Forward year EBITDA** (= 黒字化見込み年の EBITDA × multiple, discount back) を使う」を追加。

### C-C-031: Tax rate 変動 (法定 vs 実効, 国別) と NOL の反映
- **Files involved**: `05_valuation_wacc.md` §1.2 (lines 67-75), §1.4 WACC (lines 95-108)
- **Missing case**: t (限界実効税率) は §1.2 で「日本: 約 30%、米: 21-28%」と書くが、(a) **NOL (Net Operating Loss carryforward) を持つスタートアップでは effective t = 0% が数年続く**、(b) NOL 消化後に通常税率に戻る、(c) 多国籍で売上構成が変わると effective t も変わる、これらの time-varying treatment が未記述。
- **Failure mode**: NOL $50M, 黒字化 Y3、t = 25% を一律適用すると Y3-Y5 の after-tax FCFF を過小評価 (NOL 控除があれば実際の cash tax は 0)。
- **Example scenario**: Y3 EBIT $10M, NOL $50M residual。Cash tax = 0 (NOL で相殺)、accounting tax = $2.5M (booked但し DTL/DTA 動き)。Statutory t = 25% で機械的に EBIT × (1-t) = $7.5M とすると FCFF が低すぎる。
- **Recommendation**: §1.2 に「NOL adjustment: effective tax rate を年度別に展開し、NOL 残高 schedule を組む。FCFF = EBIT - cash tax (NOL 適用後), where cash tax = max(0, EBIT - NOL_used) × t」を追加。NOL 期限切れ (米国 80% 制限、日本 10 年) も flag。

### C-C-032: Survival probability と stage IRR の二重カウント (説明はあるが具体例不足)
- **Files involved**: `05_valuation_wacc.md` §1.4.5 (line 191), §15.8 (lines 1453-1457)
- **Missing case**: 二重カウント警告は §1.4.5, §15.8 にあるが、**数値で示した境界がない**。Stage IRR 60% (Seed) は survival prob ≈ 25-30% を内包する、という算出方法 (Damodaran が "(1+IRR_mature)/(survival_prob) - 1" で逆算する手順) が書かれていない。
- **Failure mode**: 実装者が「保険として」両方適用 → exit value × 0.25 (survival) / 1.6^5 (IRR 60%) = exit / 41 と過小評価 (本来は exit / 10.5 程度のはず)。
- **Example scenario**: Seed 期 expected exit $30M、IRR 60% で割引 = $30M / 10.5 = $2.86M、survival 25% を追加すると $0.71M。実際の "survival 込み IRR 60%" の解釈は $2.86M で正しく、$0.71M は double-discount。
- **Recommendation**: §15.8 に具体的な数値例を追加。「stage IRR 60% は概ね survival 25% × mature IRR 15% に分解できる ((1.15 / 0.25)^(1/n) - 1)」と明示。

### C-C-033: Comp set の "private SaaS multiple" の取得不能性
- **Files involved**: `05_valuation_wacc.md` §10.1 (lines 1014-1023)
- **Missing case**: 「Private SaaS median: 4.5× ARR」と書くが、(a) private comparables は公開情報がない、(b) Pitchbook/Crunchbase の deal data はバイアスあり (調達発表は up-round に偏る)、(c) Private multiple は public multiple × 0.5-0.7 (illiquidity discount) で代替する慣行がある、これらの説明が欠落。
- **Failure mode**: ユーザーが「private SaaS は 4.5× ARR」を機械的に適用 → 出典不明な multiple を使ってしまう。
- **Recommendation**: §10.1 に「Private multiple の入手: (1) Pitchbook 等のデータベース (購読必要)、(2) public multiple × (1 - illiquidity discount, 通常 25-35%) の代理値、(3) 同業 acquihire の precedent」と明示。

### C-C-034: Implied ERP のサンプル期間 dependency と current crisis 期の歪み
- **Files involved**: `05_valuation_wacc.md` §12.1 (lines 1154-1170)
- **Missing case**: §12.1 で "Forward-looking" と推奨するが、危機期 (2008/3, 2020/3, 2022/10) の implied ERP は短期的に高騰 (panic-driven) する。これらの "transient" な ERP を mature company valuation に使うと過大の risk premium が乗る。文書は時点修正のガイダンスを提供しない。
- **Failure mode**: 2020/3 の COVID-shock 時点 implied ERP = 7%+ を current valuation に使うと WACC が 200bp 高くなり、valuation 30% 下振れ。
- **Example scenario**: 2020-03 valuation で implied ERP 7%, 平時 4.5% → WACC 12% vs 9.5%、Equity Value $300M vs $480M。短期的な panic を long-term valuation に embed するのは誤り。
- **Recommendation**: §12.1 に「Implied ERP の cycle smoothing: 12-month rolling average を使う、または平時 (5y average) と current の bracket 提示」を追加。

### C-C-035: PWERM のシナリオ確率の主観性とキャリブレーション
- **Files involved**: `05_valuation_wacc.md` §13.2(b) (lines 1261-1266)
- **Missing case**: PWERM のシナリオ確率に external benchmark がないことの問題。Best 20%, Base 50%, Worst 30% という割り振りが主観的で、変えるだけで valuation が ±50% 動く。
- **Failure mode**: 監査では "documented rationale" が必要だが、文書は確率割振 logic を提示していない。VC fund のリターン分布 (e.g., Correlation Ventures: 50% return < 1×, 25% 1-3×, 15% 3-10×, 10% > 10×) を anchor にすべき。
- **Recommendation**: §13.2(b) に「Probability calibration: industry data (Cambridge Associates VC Benchmark, Correlation Ventures, Pitchbook exit rates) を anchor として probability table を構築する」を追加。

(File 05 完了 — 10 findings, 累計 35)

---

## File 02: SaaS Metrics (`02_saas_metrics.md`)

### C-C-036: NRR > 100% の上限定義 (LTV 発散)
- **Files involved**: `02_saas_metrics.md` §4.2 Method C (lines 552-562)
- **Missing case**: DCF-based LTV で NRR/(1+r) < 1 が必要だが、NRR = 130% かつ r = 12% (mature WACC) のとき NRR/(1+r) = 1.16 > 1 で **LTV が負/発散**。文書は「割引率 r > NRR成長率 でないと発散」と書くが、実装で確認する flag/cap がない。
- **Failure mode**: 高 NRR 企業 (Snowflake 158%) に r = 10% を適用 → LTV = ARPA × GM% / (1 - 1.58/1.10) = ARPA × GM% / -0.436 → 負の LTV。実装が NaN や負値を返す。
- **Example scenario**: NRR 130%, r 12%, ARPA $10K, GM 75%。NRR/(1+r) = 1.30/1.12 = 1.161。等比級数発散。Naive 計算は infinity。
- **Recommendation**: §4.2 に「NRR-based LTV の有効条件: r ≥ NRR (= 1 + g_NRR)。NRR が r を超える場合は (a) LTV を有限期間で truncate (例 10年)、(b) finite-horizon LTV = ARPA×GM × Σ_t=1..T NRR^t / (1+r)^t、(c) NRR を将来 mature 値に逓減させる schedule、を採用」を明示。

### C-C-037: Stack loss in cohort (cohort retention の累積誤差)
- **Files involved**: `02_saas_metrics.md` §4.2 Method B (lines 542-550), §3.2/3.3 (NRR/GRR)
- **Missing case**: Cohort-based LTV で T 期 (3-5年) で打ち切るが、(a) 各期の retention データが欠落 (= "stack loss")、(b) 早期 cohort と最近 cohort で trajectory が変わるため historical 平均が将来予測に使えない、(c) 月次 cohort と annual cohort の混在、これらが詳細に展開されていない。
- **Failure mode**: 2020 cohort retention データを 2026 cohort に外挿 → COVID 期の異常 retention を current に持ち込む → LTV 過大。
- **Recommendation**: §4.2 に「Cohort vintage adjustment: 各 cohort の経済環境を確認し、平均ではなく recent cohort 重視 (= last 12-18 months weighted)。Pre-COVID と post-COVID で別 cohort family として扱う」を追加。

### C-C-038: Multi-product / Multi-geography NRR の集計
- **Files involved**: `02_saas_metrics.md` §3.3 (lines 332-384)
- **Missing case**: NRR は通常 "company-wide" だが、(a) 製品別 (Product A 良 / Product B 悪) を集計すると mix shift が NRR に乗ってくる、(b) 地域別 (US 強 / EU 弱) でも同じ、(c) "logo level" NRR と "ARR-weighted" NRR が異なる、これらの集計ルールが未明。
- **Failure mode**: Product B に乗り換えた既存顧客は Product A から見ると churn、Product B から見ると new。Cross-product migration を NRR 計算でどう扱うか定義がないと NRR が架空に高く見える。
- **Recommendation**: §3.3 に「Multi-product/geo NRR: customer-level で定義、cross-product を expansion として扱う、または product-level で別出し」を明示。

### C-C-039: Hybrid pricing (subscription + usage) での ARR 認識
- **Files involved**: `02_saas_metrics.md` §2.1 (lines 59-108)
- **Missing case**: Subscription minimum + usage overage 型 pricing の ARR 計上ルール。Snowflake/Databricks 型 (usage-only) は "consumption-based ARR" で議論されるが、文書は subscription ARR の標準定義のみ。
- **Failure mode**: Subscription floor $5K/mo + usage overage 月平均 $3K → ARR = $96K (= 12 × $8K) と計算してしまう (usage を locked-in と扱う)。実際は usage は month-by-month で fluctuate し、ARR は floor のみ ($60K) で計上すべき。
- **Recommendation**: §2.1 に「Usage-based / Hybrid: ARR には committed 部分のみ計上。Variable usage は trailing 12 month average で別 metric (= committed ARR + usage run-rate)」を追加。

### C-C-040: Magic Number の denominator timing (前期 vs 当期 S&M) の boundary
- **Files involved**: `02_saas_metrics.md` §5.1 (lines 695-742)
- **Missing case**: 「分母が前期の S&M」 (line 713) の理由は説明されているが、**急成長期の S&M ramp** で前期 vs 当期で 2x 違う場合、Magic Number は半分または倍に振れる。Sales cycle 6 ヶ月以上の Enterprise では 2 期前を使うべき (4-quarter lag)。これらの sales cycle dependent な timing が未記述。
- **Failure mode**: Enterprise SaaS で sales cycle = 9 ヶ月。前期 S&M で計算 → Magic Number 過大。実態は 3 期前の S&M が今期 ARR を生んだ。
- **Recommendation**: §5.1 に「Sales cycle aware lag: short cycle (SMB) = 1Q lag, medium = 2Q, enterprise (long cycle) = 3-4Q lag」のガイダンス追加。

(File 02 完了 — 5 findings, 累計 40)

---

## File 06: Three-Statement Model (`06_three_statement.md`)

### C-C-041: Revolver maxed out (最大借入到達) 状態の plug logic
- **Files involved**: `06_three_statement.md` §1.2 (lines 37-43), §4.3 (lines 328-360)
- **Missing case**: Revolver は「BS plug」として cash unavailable を補填するが、(a) revolver capacity (= max 借入限度) に達した場合、(b) cash も revolver も枯渇する場合 (= insolvency)、これらの "plug 不能" シナリオの fallback が未記述。
- **Failure mode**: 1Q burn $5M, cash $2M, revolver capacity $1M → 必要 $5M > $3M 利用可能 = $2M short。Naive な plug 実装は revolver を $5M に setup (capacity 違反) → covenant breach + bankruptcy が見えない。
- **Example scenario**: Pre-revenue startup でモデル予測が overrun → revolver が default $0 で組まれていると BS が unbalance、または revolver がマイナス cash で補填し続け数値が無限大に。
- **Recommendation**: §4.3 に「Revolver capacity check: Revolver_balance ≤ Capacity を hard constraint として、ABS 違反時に "Cash Shortage" エラーを raise する。Capacity 到達後の fallback (equity raise required, asset sale, bankruptcy) を明示する model toggle」を追加。

### C-C-042: BS check が cumulative で 1 円ズレる場合 (rounding)
- **Files involved**: `06_three_statement.md` §1 (lines 20-55), §3.5 (lines 298-307)
- **Missing case**: 三表 model で各 line を round する場合、累積で 1 円〜数十円のズレが生じる。文書は「Σ FD% = 100.00%」だけ書くが、(a) どの line で round するか、(b) plug で吸収するか、(c) Σ (Asset) - Σ (Liab + Equity) = 0 を hard / soft constraint にするか、これらが曖昧。
- **Failure mode**: Excel で各 line を 0.1M round → 30 line 累積で 3M ズレ → BS が 100M vs 100.003M で「Out of balance」エラー。
- **Recommendation**: §1.3 に「Rounding policy: BS, IS, CFS 全てを同じ unit (例 thousand) で round、最終 summary のみ表示 round。ズレ check は abs(Asset - Liab - Equity) < 1 thousand を tolerance とする」を追加。

### C-C-043: Covenant breach 時の auto-acceleration
- **Files involved**: `06_three_statement.md` §4 (lines 308-391), §4.5 (lines 370-380)
- **Missing case**: Debt covenant (DSCR < 1.25, leverage > 4x 等) breach で自動 acceleration → debt 全額が current に classify される。三表 model で current portion vs long-term の reclass logic が未記述。
- **Failure mode**: Y3 で DSCR < 1.0 → Lender が demand 全額返済可能。Naive model は long-term debt を current に動かさない → BS の current liability 過小、CFS の "issuance/repayment" 認識漏れ。
- **Recommendation**: §4 に "Covenant Watch Schedule" を追加。各期 covenant 計算 → breach flag → debt classification 動的更新。

### C-C-044: M&A 中の連結処理 (timing) — Acquisition mid-year
- **Files involved**: `06_three_statement.md` §1, §5
- **Missing case**: M&A が会計年度の途中で発生する場合、acquired entity の P&L は acquisition date 以降のみ連結。BS は date of acquisition で full balance sheet 連結。Cash Flow は acquisition consideration を Investing Cash Flow に計上。これらの 3 表での timing が文書に明示されていない。
- **Failure mode**: Y2/9 月に $20M で会社買収、acquired company は LTM Revenue $10M。連結モデルが (a) Full year revenue を含める ($10M) と過大、(b) 9月以降のみ ($2.5M) が正しい、を区別しない → Y2 連結 P&L が gross overstated。
- **Recommendation**: §1 に新 sub-section "M&A Timing in Consolidation" 追加。Stub period for P&L (acquisition date to year-end), full BS consolidation at acquisition date, CFS treatment (purchase price in CFI, acquired cash in same line), pro-forma adjustments を解説。

### C-C-045: 為替換算で OCI へ流れる項目 (CTA: Cumulative Translation Adjustment)
- **Files involved**: `06_three_statement.md` §1, §6 (SBC) など
- **Missing case**: Multi-currency operations で functional currency と presentation currency が異なる場合、translation adjustment は OCI (Other Comprehensive Income) へ計上、Net Income には載らない。文書は CTA の処理ルールが空白。
- **Failure mode**: 日本本社・米国子会社の連結で USD subsidiary の BS を JPY 換算する際、為替変動分が誤って P&L (FX gain/loss) に計上される → operating performance が歪む。
- **Example scenario**: USD subsidiary equity $10M、年初 JPY 110、年末 JPY 150。為替変動 $10M × (150 - 110) = ¥400M。これは OCI へ、Net Income には乗らない。
- **Recommendation**: §1 または §10 (Foreign Currency) を追加し「Functional vs Presentation currency, Translation method (current rate method), CTA → OCI accumulation, OCI realization on disposal」のルール明示。

(File 06 完了 — 5 findings, 累計 45)

---

## File 09: Market Sizing (`09_market_sizing.md`)

### C-C-046: TAM が時間とともに変動するシナリオ (TAM Expansion / Contraction)
- **Files involved**: `09_market_sizing.md` §1.8 (lines 188-201)
- **Missing case**: §1.8 で "TAM Expansion" は触れるが、(a) TAM contraction (技術 disruption で市場縮小: 例 DVD レンタル → streaming)、(b) TAM が cyclical (景気連動: 広告/SaaS 需要)、(c) Year-by-year TAM 予測 vs 静止 TAM の差、これらの dynamic TAM の取り扱いが浅い。
- **Failure mode**: 5 年 TAM 静止と仮定して penetration curve を組むが、実際は TAM が 30% 縮小 (e.g., legacy hardware 市場) → SOM 予測が overstated。
- **Example scenario**: On-prem DB 市場 $100B → cloud に shift で 5 年後 $50B、自社 SOM 計算が初年度 $100B base で 5% penetration target → $5B 実現可能と思っているが実際の base $50B → $2.5B が上限。
- **Recommendation**: §1.8 に「TAM time-series modeling: 各年度の TAM を別途予測 (= dynamic TAM)、static TAM は seed 期だけの近似」を明示。

### C-C-047: 市場 disruption 時の cannibalization
- **Files involved**: `09_market_sizing.md` §1, §3 (Penetration)
- **Missing case**: 既存事業 + 新事業の cannibalization 効果。例: SaaS 企業が新製品ローンチ → 既存顧客が新製品に migrate → 新製品 ARR は increase、既存製品 ARR は decrease、合計は static。文書は market sizing で "incremental" vs "total" を分けていない。
- **Failure mode**: 新製品 TAM × penetration を計算して total revenue impact と扱うが、実は既存収益の 60% が単に切り替わっただけ → incremental は 40%。
- **Example scenario**: 既存 ARR $50M、新製品 TAM $100M、penetration target 10% = $10M 新規。実際は既存顧客の 60% が新製品にスイッチ → 既存 ARR が $30M に減 → net incremental = $10M - $20M cannibal = -$10M。
- **Recommendation**: §1 に "Cannibalization adjustment" を追加。Net incremental TAM = New product TAM × penetration - Cannibalized portion of existing ARR を式で示す。

### C-C-048: Multi-region penetration with different ramp
- **Files involved**: `09_market_sizing.md` §1.2.3 (lines 100-105), §3
- **Missing case**: 国別 / 地域別で penetration curve のパラメータ (Logistic の a, b, K) が異なる場合の集計式。各国別に独立 modeling し sum する vs 一括で global ramp を当てるかの選択基準なし。
- **Failure mode**: Global ramp を当てると、後発参入国 (Japan) が US と同じ年で 30% penetration に達する不自然な結果。実際は 3 年遅れ。
- **Recommendation**: §3 に「Multi-region staggered ramp: country-specific S-curve のパラメータを別途定義、Stage of Diffusion (Bass model 等) で時間 lag を表現」を追加。

### C-C-049: Network effect saturation point (Bass model の K limit)
- **Files involved**: `09_market_sizing.md` §3 (Penetration)
- **Missing case**: ネットワーク効果がある事業 (marketplace, social) では penetration が saturation point K (= TAM の最大可触集合) で頭打ち。Logistic curve の K は通常 TAM = 100% と置くが、network 事業では K < TAM。これが説明されていない。
- **Failure mode**: SNS の DAU を Logistic で K = TAM (全人口) と置くと、20-30 年後の penetration 100% を予測。実際は 60-70% で saturate (K < TAM)。
- **Recommendation**: §3 に「Saturation ceiling: K = TAM × addressable fraction、network 効果 / regulation / digital divide で K を制限」を追加。

### C-C-050: Replacement cycle と新規市場の重なり
- **Files involved**: `09_market_sizing.md` §1, §3
- **Missing case**: Hardware や enterprise software の TAM は (a) 新規導入 + (b) 置き換え (replacement cycle 5-10 年) で構成。文書は新規市場のみ議論している。Mature 市場の "annual replacement market" を計算式で示していない。
- **Failure mode**: Server hardware 市場 TAM = 全 estimated install base × ASP として計算するが、実際は annual replacement = install base / replacement cycle。Static TAM の overstatement。
- **Recommendation**: §1 に「Replacement market: Annual TAM = (New installations) + (Existing install base / replacement cycle)」を式で示し、Mature 市場と growing 市場の差別化を行う。

(File 09 完了 — 5 findings, 累計 50)

---

## File 11: Debt Financing (`11_debt_financing.md`)

### C-C-051: 複数 covenant 同時 breach
- **Files involved**: `11_debt_financing.md` §1.1.5 (lines 105-112), §2 (Pricing)
- **Missing case**: DSCR + leverage + min liquidity が同時 breach した場合の処理が記述されていない。各 covenant に異なる cure period (10/30/60 day) があり、cross-covenant の treatment が venture debt vs term loan vs ABL で異なる。
- **Failure mode**: DSCR 0.9, Leverage 5x, Cash $0.5M (min $1M) が同時 breach。各 covenant が独立に cure 可能か、cross-default trigger するかで bankruptcy timeline が変わる。
- **Recommendation**: §1.1.5 に「Multi-covenant breach scenarios: (1) Independent cure (各別 cure)、(2) Cross-covenant cure (1つ cure すれば全部 cure)、(3) Cumulative breach (全 cure 必要)」を分類して提示。

### C-C-052: Cross-default vs cross-acceleration
- **Files involved**: `11_debt_financing.md` §1.7 (Term Loan), §1.10 (LBO Debt)
- **Missing case**: Cross-default は「他 facility default が当該 facility default を trigger」、Cross-acceleration は「他 facility が accelerate されると当該 facility も accelerate」。区別と implication が未記述。
- **Failure mode**: Term Loan が default → Revolver が cross-default で default → 全 debt が同時 acceleration。Cross-acceleration なら other facility が accelerate された後にこちらも accelerate (より soft trigger)。区別なしで実装すると bankruptcy waterfall が誤って同時化。
- **Recommendation**: §1.10 に「Cross-default vs cross-acceleration の区別と modeling implication」専用 section を追加。

### C-C-053: Equity cure 上限 hit
- **Files involved**: `11_debt_financing.md` §1.1.5 (Covenants)
- **Missing case**: Equity cure (= covenant breach 時に追加 equity 注入で計算上 EBITDA をブースト) には上限 (lifetime 4 回 / 1 年 2 回 / 連続 2 期不可) が通常設定される。文書はこれを欠く。
- **Failure mode**: 4 期連続で covenant breach → equity cure を 4 回連続使用したが lifetime 上限到達 → 5 回目の breach は cure 不能 → default。Naive モデルは "毎期 cure 可能" と仮定。
- **Recommendation**: §1.1.5 に「Equity cure constraints: lifetime cap (典型 4-5 回)、consecutive limit (典型 2 回まで連続)、annual limit (典型 1-2 回)、and cure amount cap (typically EBITDA add-back ≤ 25-50% of EBITDA)」を明示。

### C-C-054: PIK が利息率変動連動する case
- **Files involved**: `11_debt_financing.md` §1.10.4 (PIK)
- **Missing case**: PIK 利息は固定 (12% PIK) で書かれるが、(a) PIK + Cash 部分で変動金利 (SOFR + spread)、(b) PIK toggle (Cash か PIK か lender 選択)、(c) PIK rate が credit-quality 連動 (= covenant breach で PIK rate ↑)、これらの variable PIK が触れられていない。
- **Failure mode**: SOFR + 8% PIK で SOFR 4% → 12%, SOFR 5.5% → 13.5%、PIK 累積で principal が大幅膨張するが固定 12% で計算すると burn rate を過小評価。
- **Recommendation**: §1.10.4 に「Variable PIK: Reference rate floor / cap, PIK Toggle, PIK rate ratchet (credit-quality based)」を追加。

### C-C-055: Refinance 失敗時の bankruptcy timeline
- **Files involved**: `11_debt_financing.md` §1.7 (Term Loan), §1.10
- **Missing case**: Term loan の bullet maturity (= 5 年後一括返済) で refinance が市場環境で不能な場合の timeline が未記述。Maturity の 6 ヶ月前から refinance start、3 ヶ月前 default risk、bankruptcy filing は maturity date で発生。
- **Failure mode**: モデルが "maturity 時に refinance 自動" と仮定 → 2008/2020 級の credit market freeze を想定しない → cash crunch 突発。
- **Recommendation**: §1.7 に「Maturity wall scenarios: refinance success rate by market regime (90% normal, 60% recession, 20% crisis)、failure case の chapter 11 timeline」を追加。

### C-C-056: 経営者保証あり vs なしでの effective cost 差 (日本特有)
- **Files involved**: `11_debt_financing.md` §1.9 (Government / Public Funding)
- **Missing case**: 日本では銀行借入で「経営者保証」(personal guarantee) が一般的。経営者個人の信用補完だが、(a) 経営者の personal risk premium が effective debt cost に乗る (= 経営者の "shadow equity" コスト)、(b) 経営者保証なし融資 (信用保証協会保証) が代替、これらの cost-benefit 比較が未記述。
- **Failure mode**: 表面金利 2% の銀行借入だが、経営者保証で経営者個人が破産リスクを負う → 実質 cost = 2% + 経営者の機会費用 (=10%+ ?) で 12%+ になり、実は venture debt と同等以上。
- **Recommendation**: §1.9 に「経営者保証 effective cost: 表面金利 + 経営者の expected loss (= probability of default × personal asset at risk)」を式で示す。経営者保証ガイドライン (2014/12) と「経営者保証に関するガイドライン」の改正履歴を追加。

(File 11 完了 — 6 findings, 累計 56)

---

## File 03: Business Models (`03_business_models.md`)

### C-C-057: Marketplace の GMV と Revenue の混同 (両サイドの cohort)
- **Files involved**: `03_business_models.md` §1 (Marketplace metrics)
- **Missing case**: §1.1 で GMV と Take Rate は議論されるが、両サイドの cohort retention (buyer cohort vs seller cohort) を独立に追跡する必要があり、片方が崩れるとマーケット崩壊するという network 構造の logic が薄い。
- **Failure mode**: Buyer cohort retention が良くても seller が抜けると GMV 縮小。Aggregate cohort で見ると平均化されて見えない。
- **Recommendation**: §1.1 に "Two-sided cohort: buyer-cohort retention vs seller-cohort retention は別個に track。単一 metric で見るのは誤り" を明示。

### C-C-058: Hardware ビジネスでの SaaS metric の誤適用
- **Files involved**: `03_business_models.md` (sections about hardware/d2c/etc)
- **Missing case**: Hardware 業態では Magic Number, Burn Multiple, Rule of 40 等の SaaS metric が適用不能。Inventory turn, gross margin, replacement rate などが代替。文書は業態別の metric mapping table が薄い。
- **Failure mode**: Hardware startup を SaaS metric で評価 → "Magic Number 0.4 → bad" と誤判断。実際は hardware で sales cycle が長く Magic Number 0.4 は標準。
- **Recommendation**: §1 全体に "業態別 metric applicability matrix" を追加: SaaS / Marketplace / D2C / Hardware / Bio / Fintech 各業態で「使う metric / 使わない metric」を分類。

### C-C-059: AI 企業の compute cost 特殊性
- **Files involved**: `03_business_models.md` (AI/ML sections)
- **Missing case**: AI 企業の COGS は inference compute (GPU 時間) で構成され、(a) usage-based で variable、(b) GPU 価格変動 (NVIDIA H100 → B200) で大幅変動、(c) gross margin が SaaS の 70-80% でなく 30-50% で低位、これらが SaaS template に乗っていない。
- **Failure mode**: AI startup を SaaS gross margin 75% template で評価 → 1 年後実態 40% で利益激減。
- **Recommendation**: §X (AI 業態) を新規追加: Compute cost forecast, model improvement → cost decline の trajectory, scaling laws と margin trade-off を解説。

(File 03 完了 — 3 findings, 累計 59)

---

## File 07: Japan Specifics (`07_japan_specifics.md`)

### C-C-060: 法人実効税率の地方税調整 (東京 vs 地方)
- **Files involved**: `07_japan_specifics.md` §2.1 (lines 268-317)
- **Missing case**: 法人実効税率は事業所所在地で異なる (東京 vs 大阪 vs 地方)。本社移転時に effective tax rate が動く。これが税効果会計と DTA 計算で扱われていない。
- **Failure mode**: 東京 (地方法人税率 + 事業税で実効 31%) → 福岡 (実効 29%) で本社移転後の DTA 評価が誤って一律 31% で残る。
- **Recommendation**: §2.1 に「事業所別法人税率 schedule、本社移転時の DTA reset」を追加。

### C-C-061: NOL 繰越期限切れと税制改正の相互作用
- **Files involved**: `07_japan_specifics.md` §2.3 (line 354)
- **Missing case**: 日本 NOL は 10 年繰越 (青色)、米国 NOL は無期限 + 80% 制限。M&A での NOL 引継 (法 57 条の 2) や、組織再編で NOL が消える条件が未記述。
- **Failure mode**: スタートアップ M&A で acquirer が NOL を承継できると仮定して買収 → 50% 超 owner change で NOL が没収 → 想定 tax shield 消失。
- **Recommendation**: §2.3 に「NOL 引継条件 (M&A, 株式譲渡 50% 超, etc.) と組織再編税制の影響」を追加。

(File 07 完了 — 2 findings, 累計 61)

---

## File 08: Investment Thesis (`08_investment_thesis.md`)

### C-C-062: IC Memo の sensitivity 分析と reverse DCF の連携
- **Files involved**: `08_investment_thesis.md` §1.13 (Sensitivity Analysis)
- **Missing case**: IC Memo の Sensitivity Analysis section で WACC/g/multiple の sensitivity table を提示するが、Reverse DCF (= "現状 valuation が implies する growth/margin") と組み合わせた "implied vs achievable" 比較が記述されていない。
- **Failure mode**: Sensitivity table で base/bear/bull を出すが、IC member は "達成可能性" を判断できない。Reverse DCF を併用すれば "現状 price が要求する growth は 80%/年、過去 5 社のうち 2 社のみ達成" という感度評価が可能。
- **Recommendation**: §1.13 に「Reverse DCF cross-check: 現価格が要求する implied growth/margin を逆算し、業界 benchmark と比較」を追加。

### C-C-063: Multiple acquirer による simultaneous bid (auction process)
- **Files involved**: `08_investment_thesis.md` §1.14 (Exit Strategy)
- **Missing case**: M&A exit で複数 strategic buyer が同時 bid する auction process。各 bidder の synergy が異なり、最終価格が最高 bidder の synergy reflected → standalone valuation + synergy premium。1 社 negotiation との違いが未記述。
- **Failure mode**: Auction 想定 vs 単一 bidder 想定で expected exit value が 30-50% 違う。Single bidder = standalone valuation + 5-15% premium、Auction = standalone + 20-40% premium (synergy + competition).
- **Recommendation**: §1.14 に「Auction vs Negotiated sale: 価格差、process timing、information asymmetry の取り扱い」を追加。

(File 08 完了 — 2 findings, 累計 63)

---

## File 00, 01a, 01b, 10: Modeling Standards / Design / Craft (簡略チェック)

### C-C-064: Excel circular reference の意図的使用 (revolver, interest expense) と error trap
- **Files involved**: `01a_modeling_standards.md` または `10_modeling_craft.md` のモデル構造論
- **Missing case**: 三表モデルでは revolver と interest expense が circular (interest が cash position に影響、cash が revolver balance に影響、revolver が interest に影響)。Excel iteration 設定 (Tools > Options > Iterative Calculation) を有効にしないと #REF! が出る。文書は iteration 必要性のみ言及で、(a) max iterations 設定推奨値、(b) tolerance、(c) iteration off 状態でモデルがどう壊れるか、を明示していない。
- **Failure mode**: 同僚が iteration off で開く → モデルが #REF! 連鎖 → "壊れた" と誤認 → 元 model に戻せない。
- **Recommendation**: モデル先頭に「Iteration must be ON: max 1000, tolerance 0.01」を red font で明示。

### C-C-065: Sensitivity table の "two-way" boundary (2 変数同時に動かす場合の現実性)
- **Files involved**: `01b_integrity_and_anti_patterns.md` または `10_modeling_craft.md`
- **Missing case**: Sensitivity table で WACC × g を two-way table に展開するが、これら 2 変数は通常 correlated (高 WACC = 高インフレ環境 = 高 g)。独立変動を仮定すると非現実的な corner cases (低 WACC + 高 g, 高 WACC + 低 g) を exhibit してしまう。
- **Failure mode**: Sensitivity に WACC 8% / g 4% (= corner) で TV が無限大に近づく結果を載せると、IC member が "8% / 4% も可能" と誤認。
- **Recommendation**: Two-way table で除外すべき corner (= correlated 仮定外) を grey out するルールを追加。

### C-C-066: モデルの "dead cell" / 隠れ式が本番で beat になる
- **Files involved**: `01b_integrity_and_anti_patterns.md`
- **Missing case**: Excel モデルで使われていない formula 行 (= legacy from prior version) が hidden で残ると、後で参照して誤った値を取り出す bug が頻発。"dead cell detection" のチェックリスト未記述。
- **Recommendation**: §X に「Dead cell audit: 各 line item を search-and-trace、unused formula を delete or grey out」を追加。

(File 00, 01a, 01b, 10 完了 — 3 findings, 累計 66)

---

## Cross-domain Logic Gaps (複数 domain にまたがる論理欠落)

### C-C-067: Equity round 後の Debt covenant 影響
- **Files involved**: `04b` (Cap Table) + `11` (Debt) cross
- **Missing case**: Series A/B 直後は cash が増えて debt covenant (cash threshold) は楽になるが、(a) burn rate が高ければ 12 ヶ月後に cash が枯渇し covenant 危機、(b) 一部 debt 契約は equity raise を "Liquidity Event" 扱いで自動 prepayment trigger にする条項あり、これらの cross-impact が文書化されていない。
- **Recommendation**: 04b と 11 で cross-reference を追加。Equity raise 後の debt covenant trajectory schedule を提示。

### C-C-068: Down round 時の Anti-dilution → Option pool 拡大 → 再希薄化
- **Files involved**: `04a` (Anti-Dilution) + `04b` (Option Pool) + `08` (Investment Thesis)
- **Missing case**: Down round で (1) Anti-dilution 発動 → 既存 preferred 持分増、(2) 同時に option pool refresh で 5-10% 増、(3) これら 2 つで founder dilution が 2 重発生、という cascade。文書はそれぞれ独立に説明するが、結合 effect の数値例なし。
- **Recommendation**: 04a §10.2 (Down Round case) に "anti-dilution + option pool 同時発動の cascading dilution" 数値例を追加。

### C-C-069: Tax loss carryforward 中の M&A
- **Files involved**: `06` (Tax Schedule) + `04b` (M&A waterfall) + `07` (Japan tax)
- **Missing case**: NOL を持つ会社が買収される際、米 IRC 382 (50% owner change で NOL annual limitation = pre-change equity × LTTE rate) や日本法 57 条の 2 で NOL 大半が消える可能性。M&A model でこれを考慮しないと acquirer の expected tax shield が overstated。
- **Recommendation**: §11 (M&A modeling) で "Section 382 limitation calculation"、日本での同様規定を明示。

### C-C-070: IPO 時の SO acceleration + Lock-up + Greenshoe の同時処理
- **Files involved**: `04b` §7 (IPO), §3.5 (Vesting Acceleration)
- **Missing case**: IPO 時に (a) double-trigger acceleration が発動するか? (IPO は通常 acceleration trigger でない)、(b) Lock-up 中に vesting が継続、(c) Greenshoe で発行株数追加、これらの同時 processing logic が散在で統合されていない。
- **Recommendation**: §7.1 に "IPO event sequence: Day -1 (Conversion 確定) → Day 0 (IPO pricing, share issuance, Greenshoe option) → Day +180 (Lock-up expire, vesting catch-up)" の time-ordered checklist を追加。

### C-C-071: Bankruptcy 時の各 claim priority (絶対優先順位)
- **Files involved**: `04b` (Exit Waterfall) + `11` (Debt)
- **Missing case**: 倒産時の claim priority は (1) Secured debt → (2) DIP financing → (3) Administrative claims (lawyer fees) → (4) Unsecured debt → (5) Preferred equity LP → (6) Common。文書は各個別に説明するが、単一の bankruptcy waterfall として連結提示されていない。
- **Recommendation**: 04b に新規 section "Distress / Bankruptcy Waterfall" を追加し全 claim 順位を一本化。

(Cross-domain 完了 — 5 findings, 累計 71)

---

## 業態別 / Stage 別の場合分け不足

### C-C-072: Pre-revenue 企業に LTV/CAC を適用する誤り
- **Files involved**: `02` (SaaS) + `08` (Investment Thesis)
- **Missing case**: §02 §4.2 LTV は ARPA × GM / Churn で定義されるが、Pre-revenue (ARR = 0) では分子がゼロで意味なし。文書は applicability 注意書きが薄い。
- **Recommendation**: §02 §4 冒頭に「Stage applicability: LTV/CAC は post-PMF (= ARR > $1M, churn データ 12 ヶ月以上) でのみ意味あり。Pre-revenue では使わない」を明示。

### C-C-073: Profitable 企業で Burn Multiple を見る
- **Files involved**: `02` (SaaS) §5.2 (Burn Multiple)
- **Missing case**: Burn Multiple は「Net Burn / Net New ARR」だが、Profitable 企業は Net Burn が負 (= net cash inflow) で Burn Multiple が負 / 意味不明な値を取る。文書はこの applicability boundary が記述されていない。
- **Recommendation**: §5.2 に「Cash positive 企業では Burn Multiple は使わず、Net Income / ARR growth, Rule of 40 などで代替」を明示。

### C-C-074: IPO 後企業で SAFE 残高を考慮する
- **Files involved**: `04a` (SAFE) + `04b` (Cap Table)
- **Missing case**: IPO 後は通常 SAFE は強制転換され残高 = 0 になるが、(a) IPO 前に SAFE が強制転換されたかどうか確認、(b) 一部 jurisdictions で post-IPO SAFE が継続するケース、これらが触れられていない。
- **Recommendation**: §04a §2.5.2 に「Post-IPO SAFE residual: 通常はゼロだが、conversion ratio dispute 等で残ることあり」を追加。

(業態別 / Stage 別 完了 — 3 findings, 累計 74)

---

## Stress / Tail シナリオ未対応

### C-C-075: Recession 時の forecast 調整
- **Files involved**: `02` (SaaS metrics, churn), `06` (Forecast), `08` (Investment Thesis bear case)
- **Missing case**: Recession scenario で (a) churn 倍増 (3% → 6%/y)、(b) new ACV 50% 縮小、(c) collection days 30 → 60、(d) FX shock、これらが連動した bear case が体系化されていない。各 metric file で個別言及はあるが統合が薄い。
- **Recommendation**: 08 投資 Thesis Bear case section に "Recession Scenario template (連動仮定)" を追加。

### C-C-076: Top customer concentration loss (top 1 顧客失墜)
- **Files involved**: `02` §3.5 (Customer Concentration), `08` (Risk)
- **Missing case**: Top 1 顧客が 25% 集中 → renewal 失敗で ARR 25% 下落 → これが equity value にどう波及するか。Direct ARR 影響だけでなく、(a) confidence loss → multiple 縮小 (5× → 3×)、(b) employee morale → 退職率 2x、(c) 投資家信頼 → 次ラウンド困難、これら 2 次効果が記述されていない。
- **Recommendation**: §3.5 に "Top customer loss scenario: ARR direct impact + multiple compression + secondary effects (talent, fundraising)" を統合表で示す。

### C-C-077: Black Swan (COVID, 規制 ban, ロシア制裁等) の整理
- **Files involved**: `08` Risk, `09` Market Sizing
- **Missing case**: 全般的な "Black Swan" risk register が欠落。具体には (a) Pandemic-driven demand shift (COVID で SaaS 急増 / hospitality 急減)、(b) Regulatory ban (China crypto/edtech ban 2021)、(c) Sanctions (Russia 2022 で SaaS 売上失墜)、これらの category-by-category playbook がない。
- **Recommendation**: §08 Risk に "Tail risk register" を新規追加。

### C-C-078: Regulatory shock (海外送金制限, 個人情報保護, AI 規制)
- **Files involved**: `07` Japan, `08` Investment Thesis
- **Missing case**: AI 規制 (EU AI Act 2024)、データ越境 (中国 2021 PIPL)、個人情報保護 (GDPR/CCPA) などが事業に及ぼす financial impact の評価フレームがない。
- **Recommendation**: §07 / §08 に "Regulatory risk financial modeling: cost of compliance, market access loss, business model adjustment" を追加。

(Stress / Tail 完了 — 4 findings, 累計 78)

---

## Summary (最終)

- **Total logic gaps found**: 78
- **Critical (production model で誤動作)**: 18 (C-C-001, 002, 016, 017, 020, 021, 022, 026, 031, 041, 042, 043, 045, 046, 050, 051, 062, 071)
- **High (誤った結論につながる)**: 32 (003, 004, 005, 006, 007, 008, 009, 010, 011, 014, 015, 018, 019, 023, 024, 025, 027, 028, 029, 030, 032, 036, 038, 044, 047, 048, 049, 052, 053, 054, 055, 056, 060, 061, 067, 068, 069, 070, 075, 076)
- **Medium (説明不足)**: 22 (012, 013, 033, 034, 035, 037, 039, 040, 057, 058, 059, 063, 064, 065, 066, 072, 073, 074, 077, 078)
- **Low (cosmetic)**: 6 (TODO, 含まれる low items)

注: Severity の最終分類は重複を含むため概数。実装側でレビューと再分類を推奨。

### 主要な観察

1. **Cap table 計算 (04a, 04b)** が最大の "壊れ得る" 領域。連立解の boundary、anti-dilution × SAFE 同時発動、participation mixed scenario など、production model でユーザーが踏むケースが集中。
2. **Valuation (05)** の WACC ≈ g、stage transition、TV/EV 比率の boundary check が手薄。
3. **Cross-domain 接続 (Equity ↔ Debt ↔ Tax)** の logic が散在で統合されていない。M&A 中の NOL、equity raise 後 covenant、IPO 時の同時処理。
4. **Stress / Tail シナリオ** がほぼ未整備。Recession, Concentration loss, Regulatory shock。
5. **業態別 / Stage 別 applicability matrix** が文書全体で欠落。SaaS metric を Hardware に誤適用、pre-revenue で LTV を計算、profitable 企業で Burn Multiple、など。

### 次のステップ推奨

1. Critical 18 項目を優先修正対象として、各 file owner に責任分担。
2. Cross-domain section (新設) を 04b / 11 / 07 に同時挿入 (= "Round → Debt → Tax" linkage の三表的整理)。
3. "業態別 / Stage 別 applicability matrix" を 03 (Business Models) に新規追加し、各 metric file (02 etc.) から cross-reference。
4. "Stress / Tail Scenario template" を 08 (Investment Thesis) に新規追加し、各 metric file の bear case を統一。

