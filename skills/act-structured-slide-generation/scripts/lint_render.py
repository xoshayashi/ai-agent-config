#!/usr/bin/env python3
"""Deterministic post-render lint: edge clipping + whitespace balance + readback + diff.

Usage: lint_render.py <render_dir> [--spec deck.json] [--baseline <prev_render_dir>]

Checks, per slide PNG:
1. Edge scan — content pixels touching the outer 6px band of the canvas mean an
   element is clipped by the slide boundary (full-bleed covers/dividers allowed).
2. Whitespace balance — a body block stuck to the top (or bottom) of the content
   band with a large opposite gap is the container/content mismatch the design
   principles ban; the engine centers blocks, so an asymmetric slide is a defect.
3. Readback — every slide title from deck.json must appear in the pdftotext
   extraction of the rendered PDF (catches font substitution / tofu / garbling).
4. --baseline: pixel-diff each slide against the previous render and report which
   slides changed — in a fix loop, verify only the targeted slides moved (回帰検知).
   Informational; does not fail the run.

Exit 0 = clean, 1 = findings.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

from deck_text import HW as _HW, token_rgb as _token_rgb

CANVAS = _token_rgb("canvas", (0xFA, 0xF7, 0xF1))
WHITE = (0xFF, 0xFF, 0xFF)
TOL = 26  # per-channel tolerance: antialiasing over near-white
BAND = 6  # px


def is_ground(px, tol: int) -> bool:
    """地(=何も置かれていない面)か。canvas だけでなく純白も地として扱う — canvas は
    白に近いが白そのものではない(FAF7F1 なら最大差 14)ので、テンプレート背景が抜けて
    白く出たレンダーを「一面コンテンツ」と誤読し、空白系の検査が黙って効かなくなる。
    カード面(surface_tint)は canvas とも白とも差が大きいので、構造として残る。"""
    return all(abs(px[i] - CANVAS[i]) <= tol for i in range(3)) or \
        all(abs(px[i] - WHITE[i]) <= tol for i in range(3))


def is_content(px) -> bool:
    return not is_ground(px, TOL)


def edge_scan(im: Image.Image) -> list[str]:
    w, h = im.size
    p = im.load()
    hits = []
    bands = {
        "top": [(x, y) for y in range(BAND) for x in range(0, w, 3)],
        "bottom": [(x, y) for y in range(h - BAND, h) for x in range(0, w, 3)],
        "left": [(x, y) for x in range(BAND) for y in range(0, h, 3)],
        "right": [(x, y) for x in range(w - BAND, w) for y in range(0, h, 3)],
    }
    for edge, pts in bands.items():
        n = sum(1 for x, y in pts if is_content(p[x, y]))
        # full-bleed edges (cover band / divider rail) light up nearly the whole edge;
        # clipping shows as a partial run of content pixels
        frac = n / len(pts)
        if 0.02 < frac < 0.85:
            hits.append(f"{edge} edge {frac:.0%} content — 端で見切れている要素の疑い")
    return hits


def balance_scan(im: Image.Image) -> list[str]:
    """Vertical whitespace balance inside the body band (below header, above footer).
    許容差は edge_scan(26)より厳しい 8 — surface_tint のカード面(canvas との色差は
    最大 18)は空白ではなく構造なので、バランス判定ではコンテンツとして数える。"""
    w, h = im.size
    p = im.load()
    # 0.23: kicker+2行タイトル+subtitle のヘッダー下端(1.63in/7.5in)より下から走査する
    band_top, band_bot = int(h * 0.23), int(h * 0.92)
    ink_rows = []
    for y in range(band_top, band_bot, 2):
        n = sum(1 for x in range(0, w, 4) if not is_ground(p[x, y], 8))
        if n > w // 4 * 0.02:
            ink_rows.append(y)
    if not ink_rows:
        return ["本文領域にコンテンツが検出できない"]
    band_h = band_bot - band_top
    top_gap = (ink_rows[0] - band_top) / band_h
    bot_gap = (band_bot - ink_rows[-1]) / band_h
    body_extent = (ink_rows[-1] - ink_rows[0]) / band_h
    hits = []
    if body_extent < 0.36 and top_gap > 0.20 and bot_gap > 0.20:
        hits.append(f"本文領域に対してオブジェクトが小さい(占有{body_extent:.0%})— カード/行/主数値を大きくし、余白を設計された密度に戻す")
    if bot_gap > 0.33 and bot_gap > 2.5 * max(top_gap, 0.02):
        hits.append(f"下部に大きな空白(本文帯の{bot_gap:.0%})— 中身が上に張り付いている。分割/統合かパターン変更を検討")
    if top_gap > 0.33 and top_gap > 2.5 * max(bot_gap, 0.02):
        hits.append(f"上部に大きな空白(本文帯の{top_gap:.0%})— ブロックが沈んでいる")
    # 中抜け: コンテンツブロック間の最大空白連続。関係のある要素(本文と直下の結論バンド等)が
    # 大きな空白で分断されると「近い情報は近く」の近接原理が壊れる
    max_run = 0
    prev = ink_rows[0]
    for y in ink_rows[1:]:
        max_run = max(max_run, y - prev)
        prev = y
    if max_run / band_h > 0.32:
        hits.append(f"コンテンツ間に大きな中抜け空白(本文帯の{max_run / band_h:.0%})— ブロックを埋めるか近接させる(フィルルール/スケールアップ)")
    return hits


def diff_frac(a: Path, b: Path) -> float:
    """Fraction of sampled pixels that differ between two renders."""
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        ib = ib.resize(ia.size)
    pa, pb = ia.load(), ib.load()
    w, h = ia.size
    total = changed = 0
    # tol 12: pale-tint fill changes (E2EFED vs surface_tint ≒ Δ19) must register as diffs
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            total += 1
            if any(abs(pa[x, y][i] - pb[x, y][i]) > 12 for i in range(3)):
                changed += 1
    return changed / max(1, total)


def normalize(s: str) -> str:
    # fold full-width alnum first: the builder normalizes them at render time
    # (_HW は deck_text.py の単一実装 — builder の hw() と同一であることが照合の前提)
    return re.sub(r"[\s  、。・,\.\-—〜~()()「」%%+±△▲]", "", s.translate(_HW))


def main() -> int:
    args = sys.argv[1:]
    spec = None
    baseline = None
    if "--spec" in args:
        i = args.index("--spec")
        spec = json.loads(Path(args[i + 1]).read_text())
        del args[i:i + 2]
    if "--baseline" in args:
        i = args.index("--baseline")
        baseline = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__)
        return 1
    render_dir = Path(args[0])
    pngs = sorted((p for p in render_dir.glob("*.png") if re.search(r"-\d+\.png$", p.name)),
                  key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))
    if not pngs:
        print(f"no slide PNGs in {render_dir}")
        return 1
    findings: list[str] = []

    fullbleed: set[int] = set()
    no_balance: set[int] = set()
    if spec:
        for i, s in enumerate(spec.get("slides", []), start=1):
            if s.get("pattern") in ("cover", "section_divider"):
                fullbleed.add(i)
            if s.get("pattern") in ("cover", "section_divider", "statement", "agenda"):
                no_balance.add(i)
    if spec and len(spec.get("slides", [])) != len(pngs):
        findings.append(f"render {len(pngs)} 枚 vs spec {len(spec.get('slides', []))} 枚 — "
                        "枚数不一致。古い PNG の残留か再レンダー漏れを疑う")
    for i, png in enumerate(pngs, start=1):
        if i in fullbleed:
            continue
        im = Image.open(png).convert("RGB")  # decode once, share across both scans
        for hit in edge_scan(im):
            findings.append(f"slide {i}: {hit}")
        # balance needs pattern knowledge (statements/covers are legitimately sparse)
        if spec and i not in no_balance:
            for hit in balance_scan(im):
                findings.append(f"slide {i}: {hit}")

    if spec:
        pdfs = list(render_dir.glob("*.pdf"))
        if pdfs:
            r = subprocess.run(["pdftotext", str(pdfs[0]), "-"], capture_output=True, text=True)
            body = normalize(r.stdout)
            for i, s in enumerate(spec.get("slides", []), start=1):
                title = s.get("title") or s.get("statement") or ""
                if not title:
                    continue
                probe = normalize(title)[:24]
                if probe and probe not in body:
                    findings.append(f"slide {i}: タイトルがレンダリング結果から読み戻せない(フォント化け/欠落の疑い): '{title[:30]}'")
        else:
            print("WARN: no PDF in render dir — readback skipped")

    if baseline is not None:
        changed = []
        for i, png in enumerate(pngs, start=1):
            prev = baseline / png.name
            if not prev.exists():
                changed.append((i, None))
                continue
            frac = diff_frac(png, prev)
            # 0.001: 文字色だけの変更(≈0.2%)も拾う。無変更スライドの実測ノイズは ≤0.03%
            if frac > 0.001:
                changed.append((i, frac))
        if changed:
            for i, frac in changed:
                label = "baseline に無い" if frac is None else f"{frac:.1%} 変化"
                print(f"DIFF: slide {i}: {label}")
            print("→ 意図して直したスライド以外が変化していないか確認する(回帰検知)")
        else:
            print("DIFF: baseline から変化したスライドなし")

    for f in findings:
        print(f"FAIL: {f}")
    print(f"\n{len(pngs)} slides / {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
