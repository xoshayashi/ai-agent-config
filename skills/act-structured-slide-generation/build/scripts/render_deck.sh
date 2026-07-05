#!/bin/sh
# Render a .pptx to per-slide PNGs for visual QA.
# Usage: render_deck.sh <deck.pptx> [outdir]   (default outdir: <deck dir>/render)
set -eu
PPTX="$1"
OUT="${2:-$(dirname "$PPTX")/render}"
mkdir -p "$OUT"
soffice --headless --convert-to pdf --outdir "$OUT" "$PPTX" >/dev/null
BASE="$(basename "$PPTX" .pptx)"
pdftoppm -png -r 110 "$OUT/$BASE.pdf" "$OUT/$BASE"
python3 "$(dirname "$0")/contact_sheet.py" "$OUT" --headers
echo "rendered: $OUT/${BASE}-NN.png"
