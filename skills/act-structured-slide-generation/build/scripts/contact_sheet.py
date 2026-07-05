#!/usr/bin/env python3
"""Assemble rendered slide PNGs into one contact sheet for whole-deck review.

Usage: contact_sheet.py <render_dir> [-o contact-sheet.png] [--cols N] [--headers]

Individual PNGs remain the unit for close reading; the contact sheet is for the
checks that only work at deck level: tone uniformity, density balance across
slides, layout rhythm, and accent-color frequency. One Read of the sheet shows
the whole deck at a glance.

--headers additionally writes header-strip.png: the top band of every slide
stacked full-width. Headers must be identical in position, size, and bar
geometry across slides — stacking them makes any drift (title size mixing,
subtitle presence, bar height) jump out in a single Read.

Exit 0 = sheet written, 1 = no slide PNGs found.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from deck_text import token_rgb as _token_rgb

THUMB_W = 480
GAP = 16
MARGIN = 24
LABEL_H = 18
BG = _token_rgb("surface", (0xEC, 0xE9, 0xE1))
INK = _token_rgb("ink", (0x2D, 0x33, 0x2E))


HEADER_FRAC = 0.22  # kicker + accent bar + 2-line title + subtitle の下端(1.63in/7.5in)を含む帯


def header_strip(ims: list, out: Path) -> None:
    strips = []
    for im in ims:
        w = 1100
        # crop 先行: 帯だけを LANCZOS 対象にする(全面リサイズ→crop は約8割を捨てる)
        src_h = round(im.height * HEADER_FRAC)
        strips.append(im.crop((0, 0, im.width, src_h))
                        .resize((w, round(src_h * w / im.width)), Image.LANCZOS))
    strip_h = strips[0].height
    sheet = Image.new("RGB", (MARGIN * 2 + 1100 + 44,
                              MARGIN * 2 + len(strips) * (strip_h + GAP) - GAP), BG)
    draw = ImageDraw.Draw(sheet)
    for i, s in enumerate(strips):
        y = MARGIN + i * (strip_h + GAP)
        draw.text((MARGIN, y + strip_h // 2 - 6), f"{i + 1:02d}", fill=INK)
        sheet.paste(s, (MARGIN + 44, y))
    sheet.save(out)
    print(f"header strip: {out} ({len(strips)} slides)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("render_dir", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=None)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--headers", action="store_true",
                    help="also write header-strip.png (stacked top bands)")
    args = ap.parse_args()

    # ゼロ埋め幅が揃わない場合も正順になるよう、スライド番号の数値でソートする
    pngs = sorted((p for p in args.render_dir.glob("*.png")
                   if p.stem.rsplit("-", 1)[-1].isdigit()),
                  key=lambda p: int(p.stem.rsplit("-", 1)[-1]))
    if not pngs:
        print(f"no slide PNGs in {args.render_dir}", file=sys.stderr)
        return 1
    ims = [Image.open(p).convert("RGB") for p in pngs]  # decode once for strip + thumbs
    if args.headers:
        header_strip(ims, args.render_dir / "header-strip.png")

    thumbs = []
    for im in ims:
        h = round(im.height * THUMB_W / im.width)
        thumbs.append(im.resize((THUMB_W, h), Image.LANCZOS))

    cols = max(1, args.cols)
    rows = -(-len(thumbs) // cols)
    cell_h = max(t.height for t in thumbs) + LABEL_H
    sheet = Image.new(
        "RGB",
        (MARGIN * 2 + cols * THUMB_W + (cols - 1) * GAP,
         MARGIN * 2 + rows * cell_h + (rows - 1) * GAP),
        BG,
    )
    draw = ImageDraw.Draw(sheet)
    for i, t in enumerate(thumbs):
        x = MARGIN + (i % cols) * (THUMB_W + GAP)
        y = MARGIN + (i // cols) * (cell_h + GAP)
        sheet.paste(t, (x, y))
        draw.text((x, y + t.height + 3), f"{i + 1:02d}", fill=INK)

    out = args.out or args.render_dir / "contact-sheet.png"
    sheet.save(out)
    print(f"contact sheet: {out} ({len(thumbs)} slides, {cols} cols)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
