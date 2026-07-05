# python-pptx 落とし穴とルール(レンダラー改修時に読む)

出典: anthropics/skills 公式 pptx スキル、コミュニティ CJK スキル、本スキル構築時の実地検証。

## 日本語フォント(最重要)

1. `run.font.name` は `<a:latin>` のみ書き換える。日本語 run には `<a:rPr>` 配下に
   `<a:ea typeface="Noto Sans JP"/>` を明示挿入する(build_deck.py の `_set_run_fonts` が実装)。
   怠ると PowerPoint 実機で日本語だけ MS 明朝等に化ける。
2. チャート内テキストも `<c:txPr>` 配下の `defRPr` に `<a:ea>` が必要(`_chart_ea_fonts` が実装)。
   テーブルセルの run も同様(`_table_font` → `_set_run_fonts` 経由で対応済み)。
3. weight 600 は bold フラグでは出せない。"Geist SemiBold" / "Noto Sans JP SemiBold" という
   別ファミリー名で指定する(600 静的インスタンスをインストールしておく前提)。700 は bold=True。
4. フォント埋め込みは python-pptx 非対応。配布先で Geist / Noto Sans JP が無い環境では
   代替表示になる。tokens.json の fallback_ea (Yu Gothic) はその保険。

## 寸法・XML

5. 1 inch = 914,400 EMU、1 pt = 12,700 EMU。16:9 = 12,192,000 x 6,858,000 EMU。
   `Inches()/Pt()/Emu()` ヘルパー必須、生 int 直書き禁止。
   XML の `sz` は centipoint(`sz="1800"` = 18pt)。pt と混同すると 100 倍ズレる。
6. XML 操作は lxml(python-pptx 内部が lxml)。`xml.etree.ElementTree` は名前空間を壊すので不可。
7. z-order API はない。spTree 内の XML 順序が重なり順 = **背景・下敷きは先に add する**。
8. 透明度 API はない(`<a:alpha>` を fill XML に挿入)。8桁 hex に透明度を混ぜるとファイル破損。
9. scripts/ に `io.py` `types.py` `inspect.py` 等 stdlib と衝突する名前を置くと lxml が
   循環 import で死ぬ。
10. スライド削除・並べ替え API はない。**修正は deck.json を直して全量再ビルド**が原則。

## テキスト・オーバーフロー

11. `fit_text()` / autofit を信用しない。fit_text はフォントパス必須で CJK メトリクスが不正確、
    normAutofit は PowerPoint が開くまで再計算されない。サイズ確定は
    verify_deck.py の Pillow 実フォント計測(実 TTF の getlength)で行い、確定値のみ書く。
12. 溢れたら自動縮小しない。文字数バジェット(validate_spec.py)超過は spec 修正へ差し戻す。
    タイトルのみ 2 行フォールバック(build_deck.py が自動処理)。
13. 箇条書き API はない。本スキルはプレーンテキストボックス+行頭「・」で統一
    (プレースホルダー由来の buChar と重複しないので二重ビュレットは起きない)。

## チャート

14. chartEx 系(ネイティブ waterfall 等)は生成不可。waterfall / roadmap / 2x2 map /
    market funnel はシェイプ合成で描く(データ編集不可だが図形単位で編集可能)。
    標準チャート(column/bar/line/donut)はネイティブで生成しデータ編集可能性を残す。
15. 細部書式は API が薄い。系列色・gap_width・データラベルまでは API、
    それ以外(第2軸等)が要るなら `chart._chartSpace` の XML 手術になる — 原則避ける。
    ポイント単位の塗り・枠線は `series.points[i].format.fill / .line` で可能
    (forecast_from の予実描き分けが使用。LibreOffice でも正しく描画される)。
16. テーブルの列幅は自動調整されない。col_widths(比率)を明示する。
    セル既定余白(左右 0.1in)があるため文字数バジェットは控えめに。

## LibreOffice レンダリング検証の既知の癖

- **LibreOffice 26.2 は column / bar チャートの負値を絶対値(上向き)で描画する**
  (軸レンジは負まで拡張されるのにバーが上に伸びる。line チャートは正常。
  pptx データ自体は正しく、PowerPoint では正常に表示される)。
  → 負値を含む系列は line にするか waterfall パターンか表で見せる。
  validate_spec.py が警告を出す。

## デザイン規律

17. タイトル下の全幅アクセント罫線は「AI 生成スライドの証」として禁止。
    Act のヘッダーは左縦アクセントバーのみ。
18. 本文の中央揃え禁止(表紙・セクション扉・KPI 値を除く)。
19. スマートクォート・プレースホルダー残骸(lorem, xxxx, TBD)は lint で検出して除去。
20. shadow.inherit = False を全シェイプに設定(Act はドロップシャドウ禁止)。
