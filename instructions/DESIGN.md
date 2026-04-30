# Act Design Basics

Act の日常アウトプット向け最低限ルール。詳細な UI、スライド、ブランド実装では、Google Drive の `共有ドライブ → プロダクト事業部 → Act → デザインガイドライン` にある正本 `Act_Design_Guidelines_v1.2.md` と `Act_Slide_Patterns_v1.2.md` を参照する。

## Principles

- 静かに、具体的に、必要な場所だけ強調する。
- 煽り語、過剰な装飾、根拠のない最上級を避ける。
- 読者が次に何をすればよいか分かる形で書く。

## Colors

| Role | Color | Use |
|---|---|---|
| Surface | `#ECE9E1` | 背景の基本色 |
| Ink | `#2D332E` | 本文、主要テキスト |
| Primary | `#008A80` | 主 CTA、ブランド強調 |
| Primary deep | `#004F49` | 本文サイズのリンク、強調 |
| Accent | `#ECC85A` | 最重要の一点強調 |
| Navy | `#1F3A66` | 補助リンク、強調ブロック |
| Danger | `#C04A4A` | エラー |
| Success | `#3F8F5E` | 成功 |
| Warning | `#D6913D` | 注意 |

- Accent は 1 画面 1 か所を目安にする。本文色には使わない。
- 純黒 `#0E0E08`、Mustard `#D9B441`、ネオン、強いグラデーションは使わない。
- 色だけで意味を伝えず、テキストやアイコンも添える。

## Type And UI

- 欧文は Geist Sans、和文は Noto Sans JP を基本にする。
- Font weight は 400 / 600 / 700 に絞る。
- 角丸は `0 / 4 / 8 / 12 / Pill` の範囲にする。
- アイコンは Lucide を基本にし、色は `currentColor` に寄せる。
- ドロップシャドウ、ガラス表現、過剰なアニメーションは避ける。
- Motion を使う場合は控えめにし、`prefers-reduced-motion: reduce` を尊重する。
