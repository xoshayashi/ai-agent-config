#!/usr/bin/env python3
"""Install Geist / Noto Sans JP static instances (400/600/700) into ~/Library/Fonts.

The builder needs: "Geist", "Geist SemiBold", "Noto Sans JP", "Noto Sans JP SemiBold"
(600 as separate families because PowerPoint style-linking only knows Regular/Bold).
Skips work if all six files already exist. Requires fonttools (scripts/requirements.txt).

Usage: setup_fonts.py [--check]
"""
from __future__ import annotations

import sys
import tempfile
import urllib.request
from pathlib import Path

FONT_DIR = Path.home() / "Library" / "Fonts"
SOURCES = {
    "Geist": "https://github.com/google/fonts/raw/main/ofl/geist/Geist%5Bwght%5D.ttf",
    "NotoSansJP": "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf",
}
TARGETS = [f"{fam}-{w}.ttf" for fam in SOURCES for w in (400, 600, 700)]


def installed() -> bool:
    return all((FONT_DIR / t).exists() for t in TARGETS)


def fix_names(path: Path, family: str, sub: str, weight: int, bold: bool) -> None:
    from fontTools.ttLib import TTFont

    t = TTFont(path)
    name = t["name"]
    full = f"{family} {sub}".replace(" Regular", "") or family
    ps = full.replace(" ", "") + ("-Bold" if bold else "-Regular")
    for nid, val in [(1, family), (2, sub), (3, f"{full};{weight}"), (4, full), (6, ps)]:
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    for nid in (16, 17):
        name.removeNames(nameID=nid)
    os2, head = t["OS/2"], t["head"]
    os2.usWeightClass = weight
    if bold:
        os2.fsSelection = (os2.fsSelection & ~0x40) | 0x20
        head.macStyle |= 0x01
    else:
        os2.fsSelection = (os2.fsSelection & ~0x20) | 0x40
        head.macStyle &= ~0x01
    t.save(path)


def main() -> int:
    if installed():
        print("fonts OK:", ", ".join(TARGETS))
        return 0
    if "--check" in sys.argv:
        print("MISSING fonts — run setup_fonts.py without --check to install")
        return 1
    from fontTools.varLib.instancer import instantiateVariableFont
    from fontTools.ttLib import TTFont

    with tempfile.TemporaryDirectory() as td:
        for fam, url in SOURCES.items():
            var_path = Path(td) / f"{fam}.ttf"
            print(f"downloading {fam} ...")
            urllib.request.urlretrieve(url, var_path)
            base = "Geist" if fam == "Geist" else "Noto Sans JP"
            for w in (400, 600, 700):
                out = FONT_DIR / f"{fam}-{w}.ttf"
                font = TTFont(var_path)
                instantiateVariableFont(font, {"wght": w}, inplace=True)
                font.save(out)
                family = f"{base} SemiBold" if w == 600 else base
                sub = "Bold" if w == 700 else "Regular"
                fix_names(out, family, sub, w, bold=(w == 700))
                print("installed", out.name, "->", family, "/", sub)
    print("done. Restart PowerPoint/LibreOffice to pick up new fonts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
