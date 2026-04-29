# Act Design — エージェント向け基本作法

このドキュメントは、Act ブランドの **デザイン言語の "基本的なお作法"** を、AI エージェントが日常のアウトプット（テキスト・コード・チャット返答・ドキュメント・図解の指示など）で守るべき水準まで圧縮したものです。

サイト構築・スライド制作・本格的な UI 実装などは **後日別スキルで扱う**。本書ではトークン値の網羅や CSS スニペットは省き、判断軸のみを残しています。詳細仕様や実装値が必要になった場合は、必ず正本を参照すること。

## 使い分けの目安

- 日常のチャット返答、README、PR 説明、通常ドキュメントでは、**1. 3つの原則** と **2. ボイス & トーン** と **9. Do / Don't** を主に使う。
- **3. カラー** から **8. アクセシビリティ** までは、実際に色・タイポ・アイコン・UI・スライド・画面表現を決めるときの **reference-level detail** として扱う。
- その task が色トークン、タイポスケール、アイコン方針、余白、focus 表現まで必要としていないなら、その詳細を working brief に持ち込まない。

- **正本（Single source of truth）:** Act デザインガイドライン v1.2（**v1.1 の純黒 Ink・Teal・Mustard 体系から、Forest Charcoal + Petrol + Honey 体系に再構築済み**）
  社内 Google Drive: **共有ドライブ → プロダクト事業部 → Act → デザインガイドライン → `Act_Design_Guidelines_v1.2.md`**
  （ローカルにマウントされた Google Drive のフルパスは利用者ごとに異なるため、ここでは Drive 上の論理パスのみを記載）
- **スライドパターン:** 同フォルダ `Act_Slide_Patterns_v1.2.md`（スライド制作時はこちらも参照）
- **代表コンポジット:** 同フォルダの `composite_light.png` / `composite_dark.png`

---

## 1. 3つの原則（最優先）

| 原則 | エージェントの行動への翻訳 |
|---|---|
| **Calm intelligence** | 装飾・誇張・煽りを避け、**重さと余白で語る**。絵文字・派手な強調・ドロップシャドウ的"映え"を足さない。 |
| **Industrial-strength softness** | 工業的な直線・Pill 形状と、医療由来のクリーム背景・控えめな角丸を組み合わせる。硬すぎず甘すぎないトーン。 |
| **Quiet by default, loud when it matters** | アクセント（Honey）は **1 画面 1 ヶ所** が原則。デフォルトの主 CTA は **Petrol**、最重要コンバージョンのみ Honey Featured Pill に昇格。 |

迷ったら **「静かに・自信をもって・必要な所だけ強調」** に倒す。

---

## 2. ボイス & トーン（テキスト生成時）

| 場面 | やる | やらない |
|---|---|---|
| 見出し・キャッチ | 並列構造で短く、動詞の現在形（"See. Think. Act."） | "革命的"・"次世代"・"驚異の"等の煽り語 |
| プロダクト/機能説明 | 短い断定、能動態 | 過剰な比喩、長い受動態 |
| 数字 | `99.4%` `+12pt` `8h` のように事実を直接出す | "驚異の" 等の修飾語を被せる |
| エラーメッセージ | 事実だけ（"Please enter a valid email address."） | 過剰な謝罪、絵文字の連発 |
| 空状態 | 1 行のヒント + 控えめな CTA | 長文の説明 |

医療領域の語彙: `patient-aware`, `human-grade`, `quietly intelligent`。
NG ワード: `miracle`, `magic`, `revolutionary`, "次世代", "業界初" 等の根拠なき最上級。

絵文字は **ユーザーが明示的に求めた場合のみ** 使用する。デフォルト出力には入れない。

---

以下は **visual / UI / slide implementation が実際に scope に入っているときだけ** 深く参照する。

---

## 3. カラーの最低限ルール

実装値の網羅は正本を見ること。ここでは **役割と運用のみ**（v1.2 で全面改訂）：

- **Surface（クリーム `#ECE9E1`）と Ink（Forest Charcoal `#2D332E`）が主役**（合計で 80–94%）。**純黒 `#0E0E08` は v1.2 で撤廃済み**。
- **Primary（ブランド主色）= Petrol**（深いティール系）。5 段スケール:
  - `Petrol-Deep #004F49` — 本文サイズの強調・リンク（AAA on Cream）
  - `Petrol-Mid #006B65` — Slide H1、Wordmark ≤24px
  - `Petrol #008A80` — **Primary CTA fill**、縦線、Wordmark ≥32px（Cream 文字は ≥18px / bold ≥14px のみ AA-large）
  - `Petrol-Light #3FBAB1` — 装飾・viz の 2 色目
  - `Petrol-Tint #B3DDD9` — ヒーロー帯、面塗り背景
- **Secondary = Navy `#1F3A66`**。本文リンク、white を載せた強調塊。
- **Accent = Honey `#ECC85A`**（旧 Mustard `#D9B441` から置換、v1.2 で **明度 +7pt** で透明感を確保）。
  - **1 画面 1 ヶ所** の Featured Pill 等、シグネチャアクセント限定。
  - クリーム上の **本文テキストとして使わない**（1.7、コントラスト不足）。
  - 文字を載せる時は **Ink を載せる**（Featured Pill は Ink on Honey で 9.4 AAA）。
  - **明滅・点滅アニメ禁止**（WCAG 2.3.1 配慮）。
- **State 色**: Danger `#C04A4A` / Success `#3F8F5E` / Warning `#D6913D` はコンテクスト依存で控えめに。

### やってはいけない配色
- 純黒 `#0E0E08` をテキストや面色として使う（v1.2 で撤廃。Forest Charcoal `#2D332E` を使う）。
- 旧 Mustard `#D9B441` を Light mode で再採用する（v1.2 で Honey `#ECC85A` に置換）。
- Honey と Petrol を **隣接する塊で同時に主役** にする。
- Petrol をクリーム上の本文サイズ（≤16px）として使う（4.0 = AA-large 限定）。
- Cream を Petrol 上で **文字 ≥18px / bold ≥14px 未満** で使う（4.0 = AA-large 限定）。
- Hedgehog 由来の鮮やかな `#16afaf` をそのまま使う（彩度過多）。
- グラデーション、ガラスモーフィズム、ネオン光彩、ドロップシャドウの濫用。

---

## 4. タイポグラフィの要点

- **欧文プライマリ:** Geist Sans（Vercel, OFL）。Google Fonts には常設配信されていない点に注意。導入は npm（`geist`）または self-host。
- **和文:** Noto Sans JP。OS フォールバックは Hiragino Sans / Yu Gothic UI。
- **採用ウェイトは 400 / 600 / 700 の 3 段のみ**。500 は使わない。1 画面で混在は最大 3 段まで。
- 数字・記号は **常に Geist**（和文フォントのプロポーショナル数字を使わない）。
- 和文に **ネガティブトラッキング（< -0.01em）を適用しない**。`letter-spacing` は 0 か `0.02em`。
- イタリックは原則使わない（引用・学名のみ）。

---

## 5. 形状・余白・モーションの最低限

- **角丸は `0 / 4 / 8 / 12 / Pill(9999px)` のみ**。16/20/24 等の中間値は使わない。
- **ドロップシャドウは原則禁止**。深さは背景色のシフトで表現。
- セクション間の縦余白は 64–96px を目安に **詰めない**。
- モーションは **4–8px のサブトル微動のみ**。Parallax・大きなバウンス禁止。
- `prefers-reduced-motion: reduce` を必ずサポート。

---

## 6. アイコン

- **Lucide 単一系統**（Stroke 1.5px、24×24 グリッド）。
- Phosphor / Material / Heroicons との **混用禁止**。
- 色は `currentColor` のみ。Honey / Petrol の塗りつぶしアイコンは使わない（隣接ドットや短いアンダーラインで代替）。

---

## 7. ロゴ（v1.2 暫定）

- Wordmark は Geist 700 で `ACT`、トラッキング 0.04em。
- 色は **Light: Petrol `#008A80`（≥32px） / Petrol-Mid `#006B65`（≤24px） / Dark: Surface (Cream) 単色**。
- **Petrol 塗りロゴは v1.2 で許容**（v1.1 までは Ink 単色限定だった）。**Honey 塗りは禁止**（シグナル色は塊で使わない）。
- グラデ・アウトライン化・拡縮歪みも禁止。

---

## 8. アクセシビリティの最低ライン

- 本文テキストは WCAG 2.1 **AA 4.5:1 以上** を満たす組み合わせを使う（Cream 上の本文は Forest Charcoal `#2D332E` で 9.6 AAA、または Petrol-Deep `#004F49` で 9.4 AAA）。
- フォーカス指標は **Petrol 2px outline + Honey-tint 4px ハロー** の二重リングが標準。「Honey 単独 outline」は Cream 上で 1.7 と不可視のため禁止。
- 色だけで意味を伝えない（State 色 + アイコン or テキストで冗長化）。

---

## 9. Do / Don't 早見表

### Do
- 余白を恐れない。空けるほどブランドが立つ。
- Honey は Featured Pill or アンダーライン等、**1 か所** に絞る。
- 数字は tabular-nums で淡々と提示。
- 写真・画像はトーンを Cream / Forest Charcoal 寄りに調整、彩度はやや低めに。
- フォーカスは **Petrol 2px + Honey-tint 4px** の二重リング。

### Don't
- 装飾目的のグラデ・ガラスモーフィズム・ネオン光彩・ドロップシャドウ。
- 純黒 `#0E0E08` をテキストや面色として使う（v1.2 で撤廃済）。
- 旧 Mustard `#D9B441` を Light mode で再採用する。
- Honey を本文テキストとして使う（1.7、不可視）。
- Featured Pill（Honey）を 1 ページに 2 つ以上置く。
- フォントウェイトを 4 段以上混在させる。
- アイコンライブラリを混用する。
- 中央揃えを乱用する（ヒーロー・主要セクションは **左寄せが基本**）。

---

## 10. このドキュメントの使い方

- 日常のテキスト出力・チャット返答・README/ドキュメント・PR 説明・コードコメント等では、**本書だけ参照すれば足りる**。
- サイト構築・スライド制作・UI 実装のように **デザイン値を直接扱う作業** が発生したら、専用スキルが整備されるまでは正本（`Act_Design_Guidelines_v1.2.md`、スライドは `Act_Slide_Patterns_v1.2.md` も）と `composite_*.png` を直接参照すること。
- 本書と正本に矛盾がある場合は **正本を優先**し、本書の記述を更新する。
