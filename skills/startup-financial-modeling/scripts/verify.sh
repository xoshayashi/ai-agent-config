#!/bin/bash
# ビルド→機械検査→再計算→静的リンター→変異→境界値→PDF→納品を一括実行。
# 採点（ルーブリック）に出す前に、必ずこれを通す。
# 使い方: verify.sh <plan.yaml> <outdir> <name> [納品先]
set -euo pipefail
YAML="$1"; OUTDIR="$2"; NAME="$3"; DEST="${4:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "▸ 1/8 ビルド"
python3 "$HERE/build_workbook.py" --input "$YAML" --outdir "$OUTDIR" --name "$NAME"

echo "▸ 2/8 機械検査＋再計算ゲート（IB作法・数式エラーゼロ・総合判定OK）"
python3 "$HERE/inspect_workbook.py" "$OUTDIR/$NAME.xlsx" --recalc

echo "▸ 3/8 静的恒等式リンター（数秒・全列。チェックの依存錐で偽の保証を検出）"
python3 "$HERE/tautology_lint.py" "$OUTDIR/$NAME.xlsx"

# 反復中は QUICK=1 で間引き（数分）。出荷認証は必ず全数（十数分）で通すこと。
echo "▸ 4/8 変異テスト（全行×全列ゼロ化・並列。脱落を総合判定が検知するか）"
if [ "${QUICK:-0}" = "1" ]; then
  python3 "$HERE/mutation_test.py" "$OUTDIR/$NAME.xlsx" --max 150
else
  python3 "$HERE/mutation_test.py" "$OUTDIR/$NAME.xlsx"
fi

echo "▸ 5/8 境界値テスト（期首非ゼロが伝播するか・定義域外で自壊しないか）"
python3 "$HERE/boundary_test.py" "$OUTDIR/$NAME.xlsx"

echo "▸ 6/8 シナリオスイープ（全ケース×スイッチの組合せで配線健全）"
python3 "$HERE/scenario_sweep.py" "$OUTDIR/$NAME.xlsx"

echo "▸ 7/8 スモークテスト（別アーキタイプでエンジンの汎用性を回帰）"
python3 "$HERE/smoke_test.py"

echo "▸ 8/8 PDF生成＋整合保証"
(cd "$OUTDIR" && soffice --headless --convert-to pdf "$NAME.xlsx" --outdir . >/dev/null 2>&1)
python3 - "$OUTDIR/$NAME.xlsx" "$OUTDIR/$NAME.pdf" <<'PY'
import sys, os
x, p = sys.argv[1], sys.argv[2]
assert os.path.exists(p), "PDFが生成されていません"
assert os.path.getmtime(p) >= os.path.getmtime(x), "PDFがxlsxより古い（再生成が必要）"
print("[ok] PDFはxlsxから生成された最新版")
PY

if [ -n "$DEST" ]; then
  mkdir -p "$DEST"
  cp "$OUTDIR/$NAME.xlsx" "$OUTDIR/$NAME.pdf" "$DEST/"
  cp "$YAML" "$DEST/入力ドライバー.yaml"
  echo "[ok] 納品: $DEST"
fi
echo "▸ 全ゲート通過（機械検査・再計算・恒等式リンター・変異(全数)・境界値・スイープ・スモーク・PDF整合）"
echo "▸ ルーブリック採点に進んでよい"
