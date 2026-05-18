# Worked Examples — Equity Story Reference

Two compact, annotated equity stories show the full arc end to end and the
evidence-tagging convention. `> Annotation:` lines explain *why* each move is
made; they are not part of the deliverable.

- **Example 1 — Forgeline** — a US Series B, a custom-manufacturing marketplace.
  The full spine and the evidence-tagging convention.
- **Example 2 — ヤモリ** — a Japanese TSE Growth IPO, a property-management
  vertical SaaS. Adds the Japan-IPO layer: the 成長可能性資料 disclosure mapping,
  想定問答, PSR comparable-company valuation, and Japanese-language generation.

**Both companies are fictional.** "Forgeline" and "ヤモリ", and all their figures,
founders and metrics, are invented for illustration — they are not, and do not
refer to, any real business.

---

# Equity Story — Forgeline

*Series B equity story. Audience: growth-stage venture investors. Geography: US.*

> **Evidence legend.** `[fact]` supplied/verified · `[derived]` computed from
> facts · `[estimate]` inferred · `[open]` a diligence question. No figure is
> invented to fill a gap.

> Annotation: a one-line legend up front lets a sceptical reader separate
> verified facts from inference at a glance. Both the spine and the proof points
> below lean on it.

## Thesis in brief

**Forgeline is a marketplace where companies upload a custom-part design and get
it manufactured by a vetted network of small machine shops — instant quote, one
accountable counterparty, parts shipped.**

Investment highlights:

1. **The contrarian core.** The industry treats machining *capacity* as the
   binding constraint and races to add it; Forgeline's bet is that capacity was
   never scarce — *matching* was. Instant quoting removed the real bottleneck,
   and the winner is whoever clears the market, not whoever owns the machines.
2. **A two-sided marketplace past its cold start.** 2,400 buyers and 600 shops
   transact on the platform `[fact]`; the liquidity that makes a marketplace
   hard to start now works *for* Forgeline, not against it.
3. **The flywheel is showing in the numbers.** GMV grew from $14M to $48M
   annualized in twelve months `[fact]` — a 3.4× year, against the ~40–60%
   typical for a marketplace at this size `[estimate]` — at an 18% take rate
   `[fact]`; buyer net revenue retention is 140% `[fact]`, well above the
   ~110% B2B-marketplace median `[estimate]` — the installed base compounds on
   its own.
4. **Founder-market fit on both sides.** The founders ran operations at a
   contract manufacturer and marketplace operations at a logistics platform —
   the supply side and the marketplace mechanics this business fuses.
5. **A wedge that opens a category.** CNC machining is the entry point; sheet
   metal, injection molding and finishing are the same buyers, the same shops,
   the same engine.

**Carry-home:** *Forgeline is the demand layer for custom manufacturing — the
constraint was never the machines, it was the matching.*

> Annotation: highlight 1 states the contrarian core in one plain sentence — the
> belief the thesis bets against. Highlight 3 puts each load-bearing number next
> to a benchmark, so the reader can weigh it. The carry-home compresses the whole
> thesis into one line a reader can repeat intact.

## Why now

Running a custom-parts marketplace was impractical for one structural reason:
**quoting**. Pricing a machined part means interpreting its geometry, tolerances
and material — historically a day or more of a skilled estimator's time. A
marketplace cannot clear if every quote takes a day.

Two things changed:

- **Instant quoting became real.** Automated geometry analysis now prices a part
  in seconds from the uploaded CAD file. The transaction that used to take days
  is now immediate `[estimate]` — the direction is well established across the
  digital-manufacturing tooling layer.
- **Shop capacity is visibly underused, and supply chains are reshoring.** Small
  shops run below capacity and want fill-in work; buyers burned by long offshore
  lead times are sourcing domestically `[estimate]`.

The inflection that matters is the first: instant quoting removed the friction
that made the marketplace un-runnable. That is why Forgeline is a business now
and was not five years ago.

> Annotation: "why now" is anchored to one concrete, quantified inflection
> (quoting time: days → seconds), placed early, and stated as load-bearing. The
> reshoring tailwind is secondary and tagged `[estimate]`.

## The problem

A hardware company's engineer needs 50 custom machined brackets. Today that
means: email the drawing to three or four shops, wait days for quotes back,
compare them, pick one, chase status by phone, and hope the parts arrive on
spec. Every new part repeats the loop. The buyer carries the integration cost of
managing a roster of shops; no single shop is accountable for the whole order.

On the other side, a small machine shop has idle machine-hours but no cheap way
to find the next job — it relies on word of mouth and a handful of repeat
accounts, and quoting eats the owner's evenings.

So the pain is concrete and recurring on both sides: **buyers spend days
sourcing every part and own all the coordination risk; shops have capacity they
cannot fill.**

> Annotation: problem before solution, told from the customer's side, both
> sides of the marketplace. The reader feels the pain before the product
> appears.

## The insight & the solution

**The insight.** The bottleneck was never manufacturing capacity — it was
*matching*. The capacity exists; what was missing was a way to price and route a
job fast enough for a marketplace to clear. Once quoting is instant, a
marketplace can aggregate fragmented demand and fragmented supply that neither
side could find efficiently alone.

**What Forgeline built.** A buyer uploads a CAD file and gets a price in
seconds. Forgeline routes the job to a vetted shop, manages the order, and is
the single accountable counterparty for quality and delivery. The buyer never
manages a roster of shops; the shop gets matched demand without quoting.

> Annotation: the insight is non-obvious (the constraint is matching, not
> capacity) and it is what the "why now" unlocks. The solution follows from it.

## Why this team

- **Manufacturing operations.** One founder ran operations at a contract
  manufacturer — direct, verifiable experience with the supply side: how shops
  price, schedule and fail `[fact]`.
- **Marketplace operations.** The other ran marketplace operations at a
  logistics platform — direct experience building liquidity and trust in a
  two-sided market `[fact]`.

The unfair advantage is the pairing: marketplace skill without manufacturing
depth mis-vets shops; manufacturing depth without marketplace skill cannot build
liquidity. `[open]` The bench below the founders is a fair diligence question.

> Annotation: concrete, verifiable, each founder owns one side of the business.
> The thin spot (the team bench) is named, not hidden.

## Market

Sized **bottom-up**, customers × spend, calculation shown. US manufacturing
output is context, not the TAM — Forgeline earns a take rate on routed orders.

- **SOM — the CNC machining wedge.** US firms regularly buying custom machined
  parts online: ~120,000 `[estimate]`; serviceable custom-parts spend ~$25k per
  firm per year `[estimate]`; at an 18% take rate, SOM ≈ 120,000 × $25k × 18% ≈
  **$540M/year** `[derived]`. Forgeline's ~$8.6M net revenue `[derived]` is a low
  single-digit share of this wedge — proven, with room left.
- **SAM — all digital custom-parts sourcing** (add sheet metal, molding,
  finishing): on the order of **$2–3B/year** of take-rate revenue `[estimate]`.
- **TAM — the category the wedge opens.** With adjacent processes and supply-side
  financial services layered on, **$5–7B/year** `[estimate]`.

The defensible number is the bottom-up SOM; SAM and TAM rest on assumptions
diligence should test. The wedge alone supports this round.

> Annotation: bottom-up, calculation visible, SOM→TAM order, headline output
> figure refused as TAM. Estimates tagged.

## Business model & unit economics

Forgeline takes an **18% take rate** `[fact]` on GMV routed through the platform.

| Metric | Value | What it proves |
|---|---|---|
| GMV | $48M annualized, up from $14M `[fact]` | The marketplace is clearing and accelerating |
| Take rate | 18% `[fact]` | Forgeline captures real value for the coordination it removes |
| Buyer NRR | 140% `[fact]` | Buyers route more parts over time — the base compounds |
| Blended gross margin | 35% `[fact]` | Marketplace economics; thinner than software, normal for managed marketplaces |

`[open]` Gross retention behind the 140% NRR, take-rate durability under
competition, and shop-side retention are the first diligence items.

> Annotation: each number sits next to the claim it proves. Open items named
> rather than papered over.

## Competition & moat

**The competitive map.** The default is the buyer's own roster of shops
(fragmented, manual). Other digital-manufacturing marketplaces exist and compete
directly. Large contract manufacturers serve big accounts but not the long tail.
"No competition" would signal no research.

**Why Forgeline keeps winning** — durability, kept distinct from market size:

- **Network effects (two-sided).** More shops → faster quotes, more capacity,
  better pricing → more buyers → more volume for shops. The 140% buyer NRR
  `[fact]` is early evidence the loop holds.
- **Aggregation Theory.** Forgeline owns the buyer relationship and the demand;
  shop capacity is modular and substitutable. Owning demand is the durable
  position.
- **Switching costs (building).** As a buyer's part history, reorder flow and
  quality record accumulate on Forgeline, re-sourcing elsewhere gets costly.

`[open]` Multi-homing — shops and buyers using several marketplaces — is the
real risk to the network-effects claim and should be diligenced.

> Annotation: opportunity (Market) and durability (here) kept separate. The moat
> is tied to named frameworks and to evidence; the honest risk (multi-homing) is
> stated, per `strategy-frameworks.md`'s warning on network effects.

## What would change our mind

The thesis rests on three load-bearing assumptions. For each, the observation
that would prove it wrong:

- **If**, after a credible attempt to retain them, more than ~30% of new buyer
  cohorts route the majority of their next-12-month volume off-platform within
  six months of first transaction, **then** the two-sided network-effects thesis
  fails — the marketplace is a lead-gen tool, not a network.
- **If** the take rate compresses below 12% under competitive pressure with no
  matching rise in shop-side financial-services revenue, **then** the
  demand-aggregation thesis is wrong and the business is a thin broker.
- **If** buyer NRR retreats below ~110% (the B2B-marketplace median) over two
  consecutive quarters, **then** the embedded-switching-costs claim is overstated.

> Annotation: these are not `[open]` items. `[open]` lists what we *don't yet
> know* and would diligence; a reversal trigger names what, if *observed*, would
> prove the thesis *wrong*. Naming your own kill criteria is the strongest
> credibility signal — see `narrative-craft.md` §6.

## Traction

Shown as a line, not a dot. All figures `[fact]`.

- **GMV $14M → $48M annualized in 12 months** — ~3.4×.
- **2,400 buyers, 600 shops** — real liquidity, past the cold start.
- **Buyer NRR 140%** — the base alone would compound revenue ~40%/year.

`[open]` A quarterly GMV series and cohort-level buyer retention would sharpen
the trajectory; they belong in the data room.

## Financial trajectory & the ask

**The path.** GMV 3.4× in a year at a stable 18% take rate — growth from
liquidity, not from discounting.

**The ask.** $25M Series B `[fact]`. `[open]` Valuation to be set against
current marketplace comparables — managed-marketplace multiples on net revenue,
not GMV.

**What it funds, next 18–24 months:**
1. Adjacent processes (sheet metal, molding) — same buyers and shops.
2. Shop-side financial services (faster payment, capacity financing) — deepens
   the supply side and adds revenue beyond the take rate.
3. Density in existing buyer segments — compounding the 140% NRR motion.

**Why the next round prices higher.** Each milestone retires a risk: adjacent
processes prove the engine generalizes; shop financial services prove revenue
beyond the take rate; density proves the core compounds. Risk retired × upside
ahead.

## Vision

The wedge is CNC machining. The category: **Forgeline as the demand layer for
custom manufacturing** — any process, any part, one accountable marketplace.
Win machining completely enough to be the obvious default, and the same engine —
instant quote, vetted supply, accountable delivery — extends to every adjacent
process.

## Anticipated investor questions

**1. What stops shops and buyers multi-homing?** A real risk. Mitigants:
accumulated part history and reorder flow create switching cost; density gives
the fastest quotes and best capacity. Forgeline does not assume exclusivity — it
earns the default-destination position. `[open]` Multi-homing rates should be
diligenced.

**2. 140% NRR — what is gross retention?** Net figure; gross retention and
whether expansion is concentrated are not in the inputs and are the first
diligence pull.

**3. Is the 18% take rate durable?** It is the value of removing days of
sourcing and the coordination risk. Competitive pressure could compress it;
shop-side financial services add revenue that does not depend on the take rate.

**4. 35% gross margin is thin.** Normal for a *managed* marketplace that owns
quality and delivery. The question is the path of margin as volume scales — a
diligence item for the financial model.

> Annotation: the sharpest objections, each answered directly; open items
> repeated honestly rather than smoothed over. Objections also appear inside the
> body sections — the Q&A collects the sharpest, it does not replace them.

---

## How to read this example

- The **spine** (why now / why us / why this / why this price) is visible in the
  section order — it is not a separate section, it *is* the structure.
- Every material number carries an **evidence tag**; `[open]` items are named as
  diligence questions, never invented.
- **Opportunity** (Market) and **durability** (Competition & moat) are kept in
  separate sections — the story argues the size of the prize *and* the reason
  the company keeps it.
- Strategy frameworks (marketplace flywheel, network effects, Aggregation
  Theory, switching costs) are named and tied to evidence, with the honest risk
  stated — see `strategy-frameworks.md`.
- The **contrarian core** (highlight 1) states in one plain sentence the belief
  the thesis bets against; the **carry-home** compresses the whole thesis to one
  repeatable line. Load-bearing numbers appear next to a benchmark, not naked —
  see `narrative-craft.md`.
- This example is Series B and US; for IPO/public-market framing see
  `stage-playbooks.md`, and for a Japanese IPO see Example 2 below and
  `japan-ipo.md`.

---

# Equity Story — ヤモリ株式会社 (Example 2, Japan Growth IPO)

*東証グロース市場への上場(約10ヶ月後を想定)に向けたエクイティ・ストーリー。
「事業計画及び成長可能性に関する事項(成長可能性資料)」のドラフトを兼ねる。
本文は日本語、`> Annotation:` と evidence legend は英語 — これは SKILL.md の
言語規約の実演である(日本IPOの公式文書相当セクションは日本語で生成する)。*

> **Evidence legend.** `[fact]` 会社提供・検証済 · `[derived]` 事実からの計算値 ·
> `[estimate]` 推定 · `[open]` デューデリジェンス事項。空欄を埋めるための数値の
> 捏造はしない。

> Annotation: the section order is the same standard arc as Example 1 — the
> spine does not change for Japan. What this example adds is the Japan-IPO
> layer: each section is annotated with the 成長可能性資料 disclosure item it
> feeds (per `japan-ipo.md`), and it shows PSR comparables, the Growth→Prime
> path, and an anticipated-Q&A (想定問答) extract.

## 結論(Thesis in brief)

**ヤモリは、中小の賃貸管理会社のためのバーティカルSaaSである。入居者対応・契約
更新・原状回復・オーナーへの送金と報告を一つにつなぎ、いま、その家賃の収納と
送金に組込型決済を載せ始めている。**

投資ハイライト:

1. **コントラリアン・コア。** 業界は賃貸管理を「労働集約な事務」と見て、SaaSを
   その効率化ツールと位置づける。ヤモリの賭けは逆である — 管理業務の核心は事務
   ではなく、**家賃というお金の流れを握ること**にある。SaaSは入口にすぎず、家賃
   の収納・送金がそのまま決済レールになる。
2. **「逃げない契約」が数字に出ている。** NRR 116% `[fact]` — 国内バーティカル
   SaaSのベストインクラス帯(120〜125% `[estimate]`)の一歩手前 — は、ヤモリが
   管理会社の基幹業務に深く食い込んでいる証拠である。
3. **規制と人手不足が重なった「Why now」。** 賃貸管理業の登録制度(2021年施行)
   が適正な管理とオーナー報告を業界の基準へ引き上げ、構造的な人手不足がデジタル
   化を不可避にした。
4. **創業者の業種適合性。** 創業者は賃貸管理会社の現場出身、共同創業者は元SaaS
   企業のプロダクト責任者 `[fact]`。
5. **ウェッジがカテゴリーを開く。** 管理SaaSは入口。家賃決済、そしてオーナー向け
   の収支・確定申告支援が、賃貸管理の「業務×お金のOS」というカテゴリーを開く。

**キャリーホーム:** *ヤモリは、賃貸管理会社の事務を肩代わりするのではなく、家賃
というお金の流れを引き受ける。*

> Annotation: the opening is identical in structure to Example 1 — one-sentence
> definition, the contrarian core stated plainly (highlight 1), a benchmarked
> load-bearing number (highlight 2), a carry-home. The craft layer is universal;
> it does not change for Japan.

## Why now — なぜ、いま窓が開いたのか

賃貸管理は長く「人の手で回す」業務だった。それが変わったのは、三つの圧力が同時
に管理会社へ届いたからである。

- **登録制度による「適正化」の基準化(主たる変曲点)。** 賃貸住宅管理業の登録
  制度 — 「賃貸住宅の管理業務等の適正化に関する法律」(国土交通省、2020年公布・
  2021年6月全面施行)`[fact]` — により、管理業務の適正化とオーナーへの定期報告
  が、一部の先進的な会社の取り組みから業界全体の基準へと変わった。手作業の台帳
  では、その基準を会社として満たし続けられない。
- **構造的な人手不足。** 管理戸数あたりの担当者を増やせない以上、事務工数を削る
  以外に選択肢がない `[estimate]`。
- **オーナーの報告高度化要請。** 不動産投資のROIを月次・デジタルで把握したい
  オーナーが増え、紙の収支報告では管理会社が選ばれにくくなっている `[estimate]`。

決定的なのは一つ目だ。登録制度は後戻りしない。**この変曲点が「なぜヤモリはいま
事業として成立し、5年前は成立しにくかったか」を説明する。**

> Annotation: a macro / regulatory claim is attributed to its **primary source**
> — the law's formal name, the issuing ministry, and the enactment year — so a
> diligence reader can verify it, not to a secondary aggregator. The why-now
> still stops at the regime's *existence and direction*: it does not cite a
> specific legal threshold figure, because a fictional example must not assert
> real-law numerics it cannot verify. The company's *own* metrics are invented
> freely and tagged `[fact]` as company-supplied within the fiction.

## 課題と着眼点(The problem & the insight)

賃貸管理会社の月末は、家賃の消し込み、オーナーへの送金、原状回復の手配、収支
報告が、紙・Excel・電話・銀行画面に分断されたまま、人手の転記でつながっている。
着眼点は単純で非自明だ — **この分断の中心にあるのは「お金の流れ」である。** 家賃
の入金から送金までを握れば、管理業務は一本につながり、そこは決済が走るレールに
なる。ヤモリは管理SaaSとして入り、家賃決済をその上に載せた。

> Annotation: problem before solution, told from the manager's side; the insight
> names the non-obvious truth (the flow of money is the centre, not the admin).

## なぜこのチームか

創業者は賃貸管理会社の現場出身で、管理業務とオーナーとの関係を一次情報として
知る。共同創業者は元SaaSプロダクト責任者 `[fact]`。業種理解とプロダクト構築力の
組み合わせが、汎用SaaSが定着しなかった市場での不公正な優位性になっている。

> Annotation: 成長可能性資料 項目① ビジネスモデル is fed by the two sections
> above (the problem/solution and the team) — the disclosure document does not
> need a new draft; it is assembled from this equity story.

## 市場(Market)

市場規模はボトムアップで積み上げ、計算を示す。順序は SOM → TAM。

- **SOM — 獲りにいく楔。** 国内の中小賃貸管理会社のうち現実的な対象は約30,000社
  `[estimate]`。ヤモリの実効単価は ARR 12億円 ÷ 導入1,800社 ≒ 約67万円/年
  `[derived]`。SOM ≒ 30,000社 × 67万円 ≒ **約200億円** `[derived]`。現状ARR
  12億円はその約6% — 楔の中でも初期の浸透段階である。
- **TAM — 楔が開く領域。** 家賃決済(流通する家賃へのテイクレート)とオーナー
  向けサービスを載せると、課金対象が「ソフト利用料」から「家賃というお金」へ
  広がり、TAMはSaaS単体の数倍規模に開く `[estimate]`。

> Annotation: 成長可能性資料 項目② 市場環境 maps to this section. Bottom-up,
> calculation shown, headline figures refused as TAM — identical discipline to
> Example 1.

## ビジネスモデルとユニットエコノミクス

SaaS利用料(月額)が現在の主柱。家賃の収納・送金に連動した組込型決済が拡張の
柱で、直近に開始したばかり。NRR 116% `[fact]`(ベストインクラス120〜125%帯
`[estimate]` の一歩手前)、解約率は低い `[fact]`(会社の定性情報 — 定量的な
GRRは下記のとおり `[open]`)。`[open]` CAC・回収期間・粗利率・GRR は財務モデル
(`startup-financial-modeling`)で確定すべき項目。

> Annotation: unit economics not supplied are tagged `[open]` and handed to the
> financial-modeling skill — not invented.

## 競争と堀

競合は、紙・Excelの現状運用(最大の競合)、汎用の会計・送金ツール、不動産テック
他社。「競合なし」とは言わない。堀は **スイッチングコスト(7 Powers)** — 管理
データと入金・送金の履歴が積み上がるほど移行は「データ移行+お金の流れの再構築」
になる。NRR 116%はその実証 `[fact]`。家賃決済の組込みが将来さらに厚みを加える。

> Annotation: 成長可能性資料 項目③ 競争力の源泉. Opportunity (Market) and
> durability (here) kept in separate sections, exactly as Example 1.

## 事業計画・財務トラジェクトリと資金使途

**トラジェクトリ。** ARR 12億円、前年比 約48%成長 `[fact]`(国内バーティカル
SaaSの中規模帯の成長中央値の目安 概ね30〜40% `[estimate]` を上回る)。NRR 116%、
低解約。

**価格の考え方。** 上場価格は主として国内の類似上場企業比準法で形成する。利益率
が公開市場基準では未確定の段階のため、日本の市場慣行に従い **PSR(株価売上高
倍率)を主たる尺度** とし(PSR中央値の目安は概ね4〜5倍 `[estimate]` — 市況で
変動するため上場時に最新のJPX/ピアデータで再確認する)、比較対象は成長率・収益
構造が近い **国内のバーティカルSaaS/不動産テック企業を主軸**、海外の高倍率銘柄は
補助にとどめる。

**Growth→Prime の経路。** 東証グロース上場は通過点であり到達点ではない。継続
上場基準とプライム移行基準(時価総額250億円以上)を見据え、本ストーリーは「時価
総額100億円超 → 250億円」へ向かう中期利益計画として描く。ガバナンス・開示も
上場時水準からプライム水準へ段階的に引き上げる。

**資金使途。** 家賃決済の拡大、隣接サービス(オーナー向け収支・確定申告支援、
原状回復の協力会社マッチング)への展開。公募・売出の規模と想定時価総額は引受
審査の進行と類似会社比準を踏まえ主幹事証券と確定する `[open]`。

> Annotation: 成長可能性資料 項目④ 事業計画. The PSR comparable-company logic,
> the verify-against-current-data note, and the Growth→Prime market-cap path are
> the Japan-specific moves — see `japan-ipo.md`.

## リスク情報

事業計画はトップダウンのストレッチ目標ではなく、ボトムアップ(管理会社数 × 実効
単価 × 決済アタッチ率)で積み上げる。決済事業は実績がまだ薄く、本書では「実証
済みの柱」ではなく「直近開始の拡張軸」として扱う `[open]`。創業者2名へのキー
パーソン依存は、経営チームの拡充と権限移譲の進捗を体制資料で開示する `[open]`。

> Annotation: 成長可能性資料 項目⑤ リスク情報. The plan is built bottom-up — the
> single most common 引受審査 finding is a "stretch-target" budget; this section
> pre-empts it. Weaknesses are named with their countermeasures, not hidden.

## ビジョン

楔は中小賃貸管理会社の業務SaaS。カテゴリーはその先にある — **賃貸管理の「業務と
お金」がヤモリの上で完結する状態**である。家賃の収納・送金を握り、管理データが
蓄積するほど、オーナー向けの収支・与信・資金繰り支援といった、ソフトウェアを
超えた価値が開く。東証グロース上場は、この弧の通過点であって到達点ではない。

> Annotation: the Vision section is kept — the output template has it for every
> stage. At IPO stage it is tight and already consistent with highlight 5 and
> the Growth→Prime path, but it is still stated, not dropped.

## 我々が判断を変える条件 — 反証点

本テーゼは2〜3の load-bearing assumption に乗っている。各々について、観測されれば
自説を撤回する条件を明示する。

- **決済の収益化** — 出来高請求に連動した決済のアタッチ率が、上場後おおむね2年
  以内に事業計画の想定水準に届かない場合、「SaaSの上に決済レールを載せる」成長
  物語は誤りであり、評価は決済を除いたSaaS単体のSOM(約200億円)へ retreat する。
- **「記録のシステム」としての定着** — NRRが4四半期連続で100%を下回った場合、
  スイッチングコストによる定着仮説は破綻しており、低解約の構造的根拠を一から
  再検証する必要がある。
- **事業計画の蓋然性** — 上場直前期に予実が下方へ大きく乖離した場合、ボトムアップ
  積み上げの前提(管理会社数・実効単価)自体が楽観であり、成長率の想定を引き下げる。

> Annotation: these are not `[open]` items. `[open]` lists what is *unknown* and
> would be diligenced; a reversal trigger names what, if *observed*, would prove
> the thesis *wrong*. The output template places this section after Vision and
> before the anticipated-Q&A — see `narrative-craft.md` §6.

## 想定問答(抜粋)

引受審査・ロードショーで想定される、最も鋭い問いへの直接的な回答。

**Q. 事業計画の蓋然性をどう担保するのか。**(日本の引受審査で最重要)
A. 計画はボトムアップで積み上げ、KPI(管理会社数・実効単価・決済アタッチ率)と
その前提・感応度を明示する。上場のかなり前から予実精度を示し、上場直前期の下方
修正リスクをゼロに保つ。本書で事実・推定・前提を区別しているのも、この蓋然性の
担保のためである。

**Q. 決済事業はまだ実績がない。語りすぎではないか。**
A. 決済は「実証済みの柱」ではなく「直近開始の拡張軸」として扱い、関連数値は
`[open]` と明記している。上場後の継続開示で流通額・アタッチ率・粗利率を線で示し、
実証の度合いに応じてストーリー上の比重を上げる。

**Q. キーパーソン依存は上場に耐えるか。**
A. 創業者2名への依存は上場準備で正面から扱う論点である。経営チームの拡充、権限
移譲、開発・営業組織の冗長化の進捗を体制資料で開示する。

> Annotation: the 想定問答集 collects the sharpest questions an underwriter or
> institutional investor would ask; the answers also appear inside the body
> sections — the Q&A does not replace them.

## How to read Example 2

- The **section order and the spine** are unchanged from Example 1 — the craft
  and substance standards are universal.
- The **Japan-IPO layer** is what this example adds: each section is annotated
  with the 成長可能性資料 disclosure item it feeds (①〜⑤), so the official
  disclosure document is *assembled from* the equity story, not drafted
  separately.
- **PSR comparable-company valuation**, the **Growth→Prime market-cap path**,
  and the **想定問答 extract** are the Japan-specific moves — see `japan-ipo.md`.
- **Real-law numerics are not asserted.** The regulatory why-now names the
  regime and its direction, not a specific legal threshold. Verify any such
  figure before using it in a live document.
- **The body is Japanese, the annotations are English** — a deliberate
  demonstration of the SKILL.md language rule: in a Japanese IPO context the
  disclosure-document sections are generated in Japanese.
- **Both examples carry a "What would change our mind" section** — the
  load-bearing assumptions, each with the observation that would falsify it.
- **A note on primary sources:** Example 2 demonstrates primary-source citation
  on a real regulatory fact (the law's name, the issuing ministry, the year).
  Example 1 (Forgeline) deliberately does not — Forgeline is fictional, and
  attaching a real source to a fictional company's market claim could be
  misread as evidence for the fiction. In a real equity story, cite the primary
  source for every macro and market claim.
