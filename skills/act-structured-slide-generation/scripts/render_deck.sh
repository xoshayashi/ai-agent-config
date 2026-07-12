#!/bin/sh
# Render a .pptx to per-slide PNGs for visual QA.
# Usage: render_deck.sh <deck.pptx> [outdir]   (default outdir: <deck dir>/render)
set -eu
PPTX="$1"
OUT="${2:-$(dirname "$PPTX")/render}"
BASE="$(basename "$PPTX" .pptx)"
mkdir -p "$OUT"
OUT_ABS="$(cd "$OUT" && pwd)"
# 前回レンダーの成果物を .prev/ へ退避してから描く: pdftoppm の連番ゼロ埋めは総ページ数
# 依存(9枚以下=deck-1.png、10枚以上=deck-01.png)のため、枚数が変わる再レンダーで
# 旧 PNG が残ると下流の lint/eval/contact-sheet が新旧混在のリストを拾う
PREV="$OUT_ABS/.prev"
mkdir -p "$PREV"
find "$OUT_ABS" -maxdepth 1 \( -name "$BASE-*.png" -o -name "$BASE.pdf" \) \
  -exec mv -f {} "$PREV/" \;
# UserInstallation を分離: 既存の LibreOffice インスタンスがあると soffice が
# exit 0 のまま何も生成しない既知挙動があるため、専用プロファイルで独立起動する
soffice "-env:UserInstallation=file://$OUT_ABS/.lo-profile" \
  --headless --convert-to pdf --outdir "$OUT_ABS" "$PPTX" >/dev/null
if [ ! -f "$OUT_ABS/$BASE.pdf" ]; then
  echo "render_deck.sh: soffice produced no PDF at $OUT_ABS/$BASE.pdf" >&2
  echo "(LibreOffice が別プロセスで起動中でないか、pptx パスが正しいか確認)" >&2
  exit 1
fi
pdftoppm -png -r 110 "$OUT_ABS/$BASE.pdf" "$OUT_ABS/$BASE"
python3 "$(dirname "$0")/contact_sheet.py" "$OUT_ABS" --headers
echo "rendered: $OUT_ABS/${BASE}-NN.png"
