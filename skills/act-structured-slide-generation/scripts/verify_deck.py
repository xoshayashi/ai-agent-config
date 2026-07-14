#!/usr/bin/env python3
"""Audit a BUILT .pptx: fonts, colors, overflow (real font metrics), chrome presence.

Usage: verify_deck.py <deck.pptx>
Exit 0 = all checks green, exit 1 = violations found (fix deck.json / builder, rebuild).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from deck_text import MEASURE_OK, _words as words, text_width_in as _measure
from pptx import Presentation
from pptx.util import Emu

TOKENS = json.loads((Path(__file__).resolve().parent.parent / "references" / "tokens.json").read_text())
LINE_BREAK = TOKENS["line_break"]
ALLOWED = {v.upper() for v in TOKENS["colors"].values()}
FORBIDDEN = {v.upper() for v in TOKENS["color_policy"]["forbidden_colors"]}
OK_FONTS = {TOKENS["fonts"]["latin"], TOKENS["fonts"]["latin_semibold"],
            TOKENS["fonts"]["ea"], TOKENS["fonts"]["ea_semibold"], "+mn-lt", "+mj-lt"}
SLIDE_W_IN = TOKENS["slide"]["width_in"]
SLIDE_H_IN = TOKENS["slide"]["height_in"]
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

# 計測は deck_text の単一実装を使う — ビルダーが「どこで切るか」を決めた物差しと、検証が
# 「はみ出すか/重なるか」を判定する物差しは、同じでなければ意味がない
_measure_ok = MEASURE_OK
text_width_in = _measure


def _para_weight(para) -> int:
    """600 (SemiBold) is expressed as a family name, not a bold flag — measure with its own metrics."""
    if any(r.font.bold for r in para.runs):
        return 700
    if any("SemiBold" in (r.font.name or "") for r in para.runs):
        return 600
    return 400


def _run_weight(run) -> int:
    if run.font.bold:
        return 700
    if "SemiBold" in (run.font.name or ""):
        return 600
    return 400


def _text_indent_in(para) -> float:
    """箇条書き段落の字下げ(marL)。本文が使える幅は箱の幅から これを引いた分しかない —
    引き忘れると1行に入る量を多く見積もり、実際は折り返す行を「折り返さない」と数える。"""
    pPr = para._p.find(f"{A}pPr")
    if pPr is None or pPr.find(f"{A}buChar") is None:
        return 0.0
    try:
        return max(0.0, int(pPr.get("marL", "0")) / 914400.0)
    except (TypeError, ValueError):
        return 0.0


def _display_lines(para):
    """段落を「実際に描かれる行」へ割る。<a:br/> はソフト改行なので、幅も行数も
    その手前で切れる — 段落全体を1行として測ると幅を過大に見積もり、折返し数を誤る。"""
    lines, cur = [], []
    for el in para._p:
        if el.tag == f"{A}r":
            cur.append(el)
        elif el.tag == f"{A}br":
            lines.append(cur)
            cur = []
    lines.append(cur)
    return lines


def _para_metrics(tf, w_in):
    """Yield (line_stack_h_in, space_after_in, widest_line_w_in, n_lines) per non-empty
    paragraph. overflow 判定と ink-box 判定が同じ行高モデルを共有するための単一実装。"""
    from pptx.text.text import _Run
    for para in tf.paragraphs:
        text = "".join(r.text for r in para.runs)
        if not text.strip():
            continue
        size = max((r.font.size.pt if r.font.size else 11) for r in para.runs)
        text_w = max(0.05, w_in - _text_indent_in(para))
        widths = []
        for line in _display_lines(para):
            runs = [_Run(r_el, para) for r_el in line]
            widths.append(sum(
                text_width_in(r.text, r.font.size.pt if r.font.size else size, _run_weight(r))
                for r in runs if r.text
            ))
        lines = sum(max(1, -(-int(w * 100) // max(1, int(text_w * 100)))) for w in widths)
        spacing = para.line_spacing if isinstance(para.line_spacing, float) else 1.15
        space_after = para.space_after.pt / 72.0 if para.space_after is not None else 0.0
        yield lines * (size / 72.0) * spacing, space_after, max(widths), lines


def check_natural_wrap(shape, warns, where):
    """その列に収まらない語を拾う。

    行の切れ目は、短いラベルなら文節へ寄せ、それ以外は自然に詰めながら語をまたぐときだけ
    その語を次行へ送る — どちらの経路でも語は割れない。割れるのは「1語が列幅より広い」ときで、
    それは組版ではなくコピーの問題(語を短くするか、列を広げる)。ここで見えるようにする。"""
    tf = shape.text_frame
    w_in = Emu(shape.width).inches - 0.02
    if w_in <= 0.05:
        return
    for para in tf.paragraphs:
        text = "".join(r.text for r in para.runs)
        if not text.strip():
            continue
        size = max((r.font.size.pt if r.font.size else 11) for r in para.runs)
        avail = max(0.05, w_in - _text_indent_in(para))
        weight = _para_weight(para)
        too_wide = [w for w in words(text)
                    if len(w) > 1 and text_width_in(w, size, weight) > avail]
        if too_wide:
            warns.append(f"{where}: 列幅に収まらない語 — '{too_wide[0]}'"
                         f"(語を短くするか列を広げる。語の途中で割れて描かれる)")


def check_overflow(shape, issues, where):
    w_in = Emu(shape.width).inches - 0.02
    h_in = Emu(shape.height).inches
    if w_in <= 0.05:
        return
    used_h = sum(h + sa for h, sa, _, _ in _para_metrics(shape.text_frame, w_in))
    # textboxes are allowed to visually overrun their nominal box a bit (top-anchored,
    # autosize off) as long as they don't collide; flag only meaningful overruns
    if used_h > h_in * 1.35 + 0.22:
        issues.append(f"{where}: text likely overflows box ({used_h:.2f}in used vs {h_in:.2f}in high)")


def _bbox(shape):
    l = Emu(shape.left).inches
    t = Emu(shape.top).inches
    return (l, t, l + Emu(shape.width).inches, t + Emu(shape.height).inches)


def _overlap_frac(a, b) -> float:
    """Intersection area as a fraction of the smaller box."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    inter = w * h
    area = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return inter / area if area > 0 else 0.0


def _ink_bbox(shape):
    """描かれる文字の範囲(インク箱)。段落を積んだ箱では、段落後スペースも文字を押し下げる —
    行の高さだけで測ると、下の段落のぶんが見えず、重なりを見逃す。"""
    box = _bbox(shape)
    if not _measure_ok:
        return box
    w_in = box[2] - box[0]
    max_w, used_h = 0.0, 0.0
    for line_h, space_after, width, _lines in _para_metrics(shape.text_frame, w_in):
        used_h += line_h + space_after
        max_w = max(max_w, min(width, w_in))
    if max_w <= 0:
        return box
    from pptx.enum.text import MSO_ANCHOR as _MA
    y0 = ((box[1] + box[3]) / 2 - used_h / 2
          if shape.text_frame.vertical_anchor == _MA.MIDDLE else box[1])
    x0 = box[0]
    try:
        from pptx.enum.text import PP_ALIGN as _PA
        al = shape.text_frame.paragraphs[0].alignment
        if al == _PA.CENTER:
            x0 = box[0] + (w_in - max_w) / 2
        elif al == _PA.RIGHT:
            x0 = box[2] - max_w
    except Exception:
        pass
    return (x0, y0, x0 + max_w, y0 + used_h)


def check_frame_overlaps(slide, idx, warns) -> None:
    """テキストボックスの「枠」どうしの重なり。描かれる文字が正しくても、枠が重なった pptx は
    編集で掴み違える(下の枠を選べない)。枠は文字を囲むだけの大きさに保つこと。"""
    boxes = [(_bbox(sh), sh.text_frame.text[:16]) for sh in slide.shapes
             if sh.shape_type == 17 and sh.has_text_frame and sh.text_frame.text.strip()
             and sh.left is not None]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][0], boxes[j][0]
            ov_w = min(a[2], b[2]) - max(a[0], b[0])
            ov_h = min(a[3], b[3]) - max(a[1], b[1])
            if ov_w > 0.01 and ov_h > 0.01:
                warns.append(f"slide {idx}: テキストボックスの枠が重なる {ov_h * 72:.1f}pt — "
                             f"'{boxes[i][1]}' × '{boxes[j][1]}'(枠は文字ぶんの大きさに)")


def check_collisions(slide, idx, issues) -> None:
    """Rendered-ink collisions: text↔text and large-text↔chart/table overlaps.
    Small overlays on charts (YoY badges etc.) are intentional and skipped."""
    texts, frames = [], []
    for shape in slide.shapes:
        if shape.left is None or shape.width is None:
            continue
        if shape.shape_type == 17 and shape.has_text_frame and shape.text_frame.text.strip():
            texts.append((_ink_bbox(shape), shape.text_frame.text[:18]))
        elif getattr(shape, "has_chart", False) or shape.shape_type == 19:
            frames.append((_bbox(shape), "chart/table"))
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            frac = _overlap_frac(texts[i][0], texts[j][0])
            if frac > 0.25:
                issues.append(
                    f"slide {idx}: テキストの重なり {frac:.0%} — '{texts[i][1]}' × '{texts[j][1]}'")
    for tb, label in texts:
        t_area = max(0.0, (tb[2] - tb[0]) * (tb[3] - tb[1]))
        for fb, _ in frames:
            f_area = (fb[2] - fb[0]) * (fb[3] - fb[1])
            if f_area <= 0 or t_area / f_area < 0.10:
                continue  # small annotation overlay on a chart is by design
            if _overlap_frac(tb, fb) > 0.3:
                issues.append(
                    f"slide {idx}: テキストが図表に重なる — '{label}'")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    path = Path(sys.argv[1])
    prs = Presentation(path)
    issues: list[str] = []
    warns: list[str] = []

    for idx, slide in enumerate(prs.slides, start=1):
        xml = slide._element.xml
        # color audit: every literal srgbClr must be in the Act palette
        for m in set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml)):
            mu = m.upper()
            if mu in FORBIDDEN:
                issues.append(f"slide {idx}: forbidden color #{mu}")
            elif mu not in ALLOWED:
                issues.append(f"slide {idx}: off-palette color #{mu}")
        # font audit
        for m in set(re.findall(r'typeface="([^"]+)"', xml)):
            if m not in OK_FONTS:
                issues.append(f"slide {idx}: off-system font '{m}'")
        # East-Asian coverage: any run holding JP text must have <a:ea>
        for r_el in slide._element.iter(f"{A}r"):
            t = r_el.find(f"{A}t")
            if t is None or not t.text or not any(ord(c) > 0x2E7F for c in t.text):
                continue
            rPr = r_el.find(f"{A}rPr")
            if rPr is None or rPr.find(f"{A}ea") is None:
                issues.append(f"slide {idx}: Japanese run without <a:ea> font: '{t.text[:20]}'")
        # placeholder rot
        low = xml.lower()
        for bad in ("lorem", "ipsum", "xxxx", "placeholder"):
            if bad in low:
                issues.append(f"slide {idx}: placeholder text '{bad}' present")
        # autofit shrink is the canonical header-consistency breaker: nominally
        # identical titles silently render at different sizes per slide
        if "normAutofit" in xml and "fontScale" in xml:
            issues.append(f"slide {idx}: autofit font shrink (<a:normAutofit fontScale>) — サイズ縮小ではなく短文化/分割で収める")
        # geometry + chrome
        n_text = 0
        for shape in slide.shapes:
            if shape.left is None:
                continue
            l, t = Emu(shape.left).inches, Emu(shape.top).inches
            r = l + Emu(shape.width).inches
            b = t + Emu(shape.height).inches
            if l < -0.01 or t < -0.01 or r > SLIDE_W_IN + 0.01 or b > SLIDE_H_IN + 0.01:
                issues.append(f"slide {idx}: shape '{shape.shape_type}' out of slide bounds ({l:.2f},{t:.2f})-({r:.2f},{b:.2f})")
            if shape.has_text_frame and shape.text_frame.text.strip():
                n_text += 1
                if _measure_ok:
                    check_overflow(shape, issues, f"slide {idx}")
                    check_natural_wrap(shape, warns, f"slide {idx}")
        if n_text == 0:
            issues.append(f"slide {idx}: no text at all")
        check_collisions(slide, idx, issues)
        check_frame_overlaps(slide, idx, warns)

    if not _measure_ok:
        warns.append("NotoSansJP-{400,600,700}.ttf not found — overflow measurement skipped (install fonts)")

    for w in warns:
        print(f"WARN: {w}")
    for i in issues:
        print(f"FAIL: {i}")
    n = len(list(prs.slides))
    print(f"\n{n} slides / {len(issues)} failures / {len(warns)} warnings")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
