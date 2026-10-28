#!/usr/bin/env python3
"""Lucide アイコンを PowerPoint のネイティブ図形(フリーフォームの線)として描く。

画像ではなく編集できるベクター図形にする: 色はテンプレートの色の役割で塗り替えられ、どの大きさでも
線がにじまない。アイコンは assets/icons/*.svg(Lucide の一部を同梱、ISC ライセンス)から読む。

Lucide の設計規則(https://lucide.dev/contribute/icon-design-guide): 24px の格子、2px の線、丸い端と
角。ここでは線の太さを「24 分の 2 × アイコンの大きさ」に保つ — 同じ大きさのアイコンは同じ線の太さに
なる(拡大縮小で線だけ太る・細るを起こさない)。

アイコンは意味の印であって飾りではない: 並列の項目(要約の点・柱・KPI・周辺)の全部に付けるか、
どれにも付けない。必ずラベルと一緒に使う(validate_spec が検査する)。
"""
from __future__ import annotations

import functools
from pathlib import Path

ICON_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"
GRID = 24.0                 # Lucide の格子
STROKE_UNITS = 2.0          # 格子上の線の太さ
CURVE_STEPS = 18            # 曲線 1 区間を折れ線に直す刻み(円は 4 区間 × 18 = 72 角で、48pt でも角が見えない)


def available() -> list[str]:
    return sorted(p.stem for p in ICON_DIR.glob("*.svg"))


def suggest(name: str, n: int = 5) -> list[str]:
    """名前の近いアイコン(打ち間違いの手当て)。"""
    import difflib
    return difflib.get_close_matches(str(name), available(), n=n, cutoff=0.4)


@functools.lru_cache(maxsize=256)
def polylines(name: str) -> tuple:
    """アイコンを格子座標(0-24)の折れ線の列にする。各要素は (点列, 閉じているか)。"""
    import svgelements as se
    path = ICON_DIR / f"{name}.svg"
    if not path.exists():
        raise KeyError(name)
    svg = se.SVG.parse(str(path), reify=True)
    out = []
    for el in svg.elements():
        if not isinstance(el, se.Shape) or isinstance(el, se.Group):
            continue
        p = se.Path(el)
        for sub in p.as_subpaths():
            sp = se.Path(sub)
            pts = []
            closed = False
            for seg in sp:
                if isinstance(seg, se.Move):
                    if seg.end is not None:
                        pts.append((seg.end.x, seg.end.y))
                    continue
                if isinstance(seg, se.Close):
                    closed = True
                    continue
                if isinstance(seg, se.Line):
                    pts.append((seg.end.x, seg.end.y))
                else:                                  # 曲線・円弧は刻んで折れ線にする
                    for k in range(1, CURVE_STEPS + 1):
                        q = seg.point(k / CURVE_STEPS)
                        pts.append((q.x, q.y))
            if len(pts) >= 2:
                out.append((tuple(pts), closed))
    return tuple(out)


def _strip_style(sh) -> None:
    """<p:style> を外す。残すと LibreOffice / PowerPoint がテーマの効果(影)をフリーフォームに当てる。"""
    el = sh._element
    st = el.find("{http://schemas.openxmlformats.org/presentationml/2006/main}style")
    if st is not None:
        el.remove(st)


def _round_line(sh) -> None:
    """線の端と角を丸める(Lucide の stroke-linecap / linejoin: round)。python-pptx に API が無いので XML で。"""
    from lxml import etree
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    ln = sh.line._get_or_add_ln()
    ln.set("cap", "rnd")
    for tag in ("round", "bevel", "miter"):
        for old in ln.findall(f"{A}{tag}"):
            ln.remove(old)
    etree.SubElement(ln, f"{A}round")


def add_icon(slide, name: str, x: float, y: float, size: float, color) -> object:
    """アイコンを (x, y) 左上・一辺 size インチの正方形に描き、グループ図形を返す。
    color は RGBColor(テンプレートの色の役割から渡す)。"""
    from pptx.util import Emu, Inches, Pt
    lines = polylines(name)
    group = slide.shapes.add_group_shape()
    # フリーフォームの局所座標は整数に丸められる。0-24 の格子のままだと点が 1 単位に吸着して円が多角形に
    # なるので、1000 倍の細かい格子で組み、尺度で戻す
    FINE = 1000.0
    unit = Inches(size) / GRID / FINE                  # 細かい格子 1 単位あたりの EMU
    stroke_pt = size * 72.0 * STROKE_UNITS / GRID      # 24 分の 2 × 大きさ(pt)
    for pts, closed in lines:
        fine = [(px * FINE, py * FINE) for px, py in pts]
        fb = group.shapes.build_freeform(fine[0][0], fine[0][1], scale=unit)
        fb.add_line_segments(fine[1:], close=closed)
        sh = fb.convert_to_shape(Emu(int(Inches(x))), Emu(int(Inches(y))))
        sh.fill.background()
        sh.line.color.rgb = color
        sh.line.width = Pt(stroke_pt)
        sh.shadow.inherit = False
        _strip_style(sh)                               # テーマの既定スタイル(影)を外す
        _round_line(sh)
    group.name = f"icon:{name}"
    return group
