"""Tests for build_deck / validate_spec / verify_deck.

Run: python3 -m pytest skills/act-structured-slide-generation/build/tests
Requires python-pptx + Pillow (scripts/requirements.txt); tests skip if absent.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

pptx = pytest.importorskip("pptx")

SKILL = Path(__file__).resolve().parent.parent.parent
SCRIPTS = SKILL / "build" / "scripts"
SAMPLE = SKILL / "examples" / "sample-deck.json"
SAMPLE_EARNINGS = SKILL / "examples" / "sample-earnings-deck.json"


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True)


def _minimal_deck(**slide_overrides):
    slide = {
        "pattern": "chart_insight",
        "title": "テスト市場は年率10%で拡大し、2030年に1兆円に到達する見込み",
        "chart": {"type": "column", "unit": "億円", "categories": ["2029", "2030"],
                  "series": [{"name": "市場", "values": [1, 2]}]},
        "source": "テスト統計2026",
    }
    slide.update(slide_overrides)
    return {"meta": {"title": "t"}, "slides": [slide]}


@pytest.mark.parametrize("sample", [SAMPLE, SAMPLE_EARNINGS], ids=["proposal", "earnings"])
def test_sample_spec_validates(sample):
    r = run("validate_spec.py", sample)
    assert r.returncode == 0, r.stdout + r.stderr


def test_validate_rejects_unknown_pattern(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(_minimal_deck(pattern="mystery")))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "unknown pattern" in r.stdout


def test_validate_rejects_off_palette_color(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["series"][0]["color"] = "FF00FF"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(deck))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "outside the Act palette" in r.stdout


def test_validate_rejects_double_accent(tmp_path):
    deck = _minimal_deck(insight="一言インサイト")
    deck["slides"][0]["chart"]["series"][0]["color"] = "ECC85A"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(deck))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "Accent" in r.stdout


def test_validate_rejects_waterfall_without_start_end(tmp_path):
    deck = {"meta": {}, "slides": [{
        "pattern": "waterfall",
        "title": "ブリッジは開始と終了で挟まれていなければならないという検証",
        "items": [{"label": "a", "value": 1}, {"label": "b", "value": 2}],
    }]}
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(deck))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "waterfall" in r.stdout


@pytest.mark.parametrize("sample", [SAMPLE, SAMPLE_EARNINGS], ids=["proposal", "earnings"])
def test_build_and_verify_sample(tmp_path, sample):
    out = tmp_path / "deck.pptx"
    r = run("build_deck.py", sample, "-o", out)
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.exists() and out.stat().st_size > 20000
    n = len(json.loads(sample.read_text())["slides"])
    assert len(pptx.Presentation(out).slides._sldIdLst) == n
    r = run("verify_deck.py", out)
    assert r.returncode == 0, r.stdout + r.stderr


def test_verify_catches_forbidden_color(tmp_path):
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Inches

    out = tmp_path / "black.pptx"
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    tb = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
    run_ = tb.text_frame.paragraphs[0].add_run()
    run_.text = "black text"
    run_.font.color.rgb = RGBColor(0, 0, 0)
    prs.save(out)
    r = run("verify_deck.py", out)
    assert r.returncode == 1 and "#000000" in r.stdout


def test_lint_render_clean_canvas_passes(tmp_path):
    from PIL import Image

    Image.new("RGB", (1466, 825), (0xFF, 0xFD, 0xFC)).save(tmp_path / "deck-01.png")
    r = run("lint_render.py", tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_lint_render_detects_edge_clipping(tmp_path):
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (1466, 825), (0xFF, 0xFD, 0xFC))
    # 下端に部分的にかかる濃色ブロック = 見切れ(全幅ではないので full-bleed 扱いにならない)
    ImageDraw.Draw(im).rectangle([300, 790, 900, 824], fill=(0x2D, 0x33, 0x2E))
    im.save(tmp_path / "deck-01.png")
    r = run("lint_render.py", tmp_path)
    assert r.returncode == 1 and "見切れ" in r.stdout


def test_validate_warns_title_line_mixing(tmp_path):
    long_title = "国内SaaS市場は年率13%で成長し、中堅企業セグメントの浸透率拡大が2030年まで続く見込みである"
    deck = _minimal_deck()
    deck["slides"].append({**_minimal_deck()["slides"][0], "title": long_title})
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 0 and "タイトル1行と2行が混在" in r.stdout


def test_validate_warns_subtitle_mixing(tmp_path):
    deck = _minimal_deck(subtitle="市場規模の推移")
    deck["slides"].append(_minimal_deck()["slides"][0])  # subtitle なし
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 0 and "サブタイトルの有無が混在" in r.stdout


def test_lint_render_detects_internal_gap(tmp_path):
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (1466, 825), (0xFF, 0xFD, 0xFC))
    d = ImageDraw.Draw(im)
    d.rectangle([100, 200, 1300, 300], fill=(0x2D, 0x33, 0x2E))   # 上部ブロック
    d.rectangle([100, 700, 1300, 750], fill=(0x2D, 0x33, 0x2E))   # 下部バンド(中抜け大)
    im.save(tmp_path / "deck-01.png")
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(_minimal_deck(), ensure_ascii=False))
    r = run("lint_render.py", tmp_path, "--spec", spec)
    assert r.returncode == 1 and "中抜け" in r.stdout


def test_validate_warns_fat_process_step(tmp_path):
    deck = {"meta": {}, "slides": [{
        "pattern": "process_flow",
        "title": "参入判断後は、90日でローンチ準備を完了させる実行体制を組む",
        "steps": [{"label": "Step 1", "items": ["a", "b", "c", "d"]}],
    }]}
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 0 and "3個超" in r.stdout


def test_contact_sheet_header_strip(tmp_path):
    from PIL import Image

    for i in range(1, 4):
        Image.new("RGB", (320, 180), (240, 240, 240)).save(tmp_path / f"deck-{i}.png")
    r = run("contact_sheet.py", tmp_path, "--headers")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "header-strip.png").exists() and "3 slides" in r.stdout


def test_contact_sheet_builds_grid(tmp_path):
    from PIL import Image

    for i in range(1, 6):
        Image.new("RGB", (160, 90), (200 + i, 200, 200)).save(tmp_path / f"deck-{i:02d}.png")
    (tmp_path / "not-a-slide.png").touch()  # 数字サフィックスなし → 無視される
    r = run("contact_sheet.py", tmp_path, "--cols", 3)
    assert r.returncode == 0, r.stdout + r.stderr
    sheet = tmp_path / "contact-sheet.png"
    assert sheet.exists() and "5 slides" in r.stdout
    im = Image.open(sheet)
    assert im.width > 480 * 3 and im.height > 0


def test_contact_sheet_empty_dir_fails(tmp_path):
    r = run("contact_sheet.py", tmp_path)
    assert r.returncode == 1


def test_validate_outline_mode_prints_titles():
    r = run("validate_spec.py", SAMPLE, "--outline")
    assert r.returncode == 0
    titles = [s.get("title", "") for s in json.loads(SAMPLE.read_text())["slides"] if s.get("title")]
    assert titles[0] in r.stdout and titles[-1] in r.stdout


def test_validate_warns_fullwidth_alnum(tmp_path):
    # １０ = 全角「10」、ＡＲＲ = 全角「ARR」
    deck = _minimal_deck(title="市場は年率１０%で拡大し、ＡＲＲは2030年に1兆円に到達する")
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 0 and "全角英数字" in r.stdout


def test_validate_warns_unmarked_forecast_categories(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["forecast_from"] = 1  # "2030" にE等の予想表記がない
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 0 and "forecast_from" in r.stdout


def test_build_forecast_styling_stays_on_palette(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["categories"] = ["2029", "2030E"]
    deck["slides"][0]["chart"]["forecast_from"] = 1
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(deck, ensure_ascii=False))
    out = tmp_path / "deck.pptx"
    r = run("build_deck.py", spec, "-o", out)
    assert r.returncode == 0, r.stdout + r.stderr
    r = run("verify_deck.py", out)
    assert r.returncode == 0, r.stdout + r.stderr


def test_lint_render_detects_bottom_whitespace(tmp_path):
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (1466, 825), (0xFF, 0xFD, 0xFC))
    # 本文帯の上端だけにブロック → 下部に大きな空白(器と中身の不釣り合い)
    ImageDraw.Draw(im).rectangle([100, 185, 1300, 260], fill=(0x2D, 0x33, 0x2E))
    im.save(tmp_path / "deck-01.png")
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(_minimal_deck(), ensure_ascii=False))
    r = run("lint_render.py", tmp_path, "--spec", spec)
    assert r.returncode == 1 and "下部に大きな空白" in r.stdout


def test_lint_render_baseline_diff_reports_changed_slides(tmp_path):
    from PIL import Image, ImageDraw

    cur, base = tmp_path / "cur", tmp_path / "base"
    cur.mkdir(); base.mkdir()
    for d in (cur, base):
        Image.new("RGB", (733, 412), (0xFF, 0xFD, 0xFC)).save(d / "deck-01.png")
    im = Image.new("RGB", (733, 412), (0xFF, 0xFD, 0xFC))
    ImageDraw.Draw(im).rectangle([100, 100, 400, 200], fill=(0x00, 0x8A, 0x80))
    im.save(cur / "deck-02.png")
    Image.new("RGB", (733, 412), (0xFF, 0xFD, 0xFC)).save(base / "deck-02.png")
    r = run("lint_render.py", cur, "--baseline", base)
    assert "DIFF: slide 2" in r.stdout and "slide 1" not in r.stdout.replace("2 slides", "")


def test_verify_catches_missing_ea_font(tmp_path):
    from pptx import Presentation
    from pptx.util import Inches

    out = tmp_path / "noea.pptx"
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    tb = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
    run_ = tb.text_frame.paragraphs[0].add_run()
    run_.text = "日本語テキスト"
    run_.font.name = "Noto Sans JP"
    prs.save(out)
    r = run("verify_deck.py", out)
    assert r.returncode == 1 and "<a:ea>" in r.stdout


def test_validate_rejects_nonint_forecast_from(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["forecast_from"] = "x"
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "forecast_from" in r.stdout and "Traceback" not in r.stderr


def test_validate_warns_forecast_from_on_multiseries(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["series"].append({"name": "利益", "values": [0.5, 1.0]})
    deck["slides"][0]["chart"]["forecast_from"] = 1
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 0 and "単一系列" in r.stdout


def test_validate_rejects_nonnumeric_series_values(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["series"][0]["values"] = [1, "二"]
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "数値でない" in r.stdout and "Traceback" not in r.stderr


def test_waterfall_auto_label_uses_triangle(tmp_path):
    deck = {"meta": {}, "slides": [{
        "pattern": "waterfall",
        "title": "解約の自動ラベルはIR慣行の三角表記で描画されるという検証",
        "unit": "億円",
        "items": [{"label": "開始", "value": 10, "kind": "start"},
                  {"label": "解約", "value": -2.8},
                  {"label": "終了", "value": 7.2, "kind": "end"}],
        "source": "テスト",
    }]}
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(deck, ensure_ascii=False))
    out = tmp_path / "deck.pptx"
    r = run("build_deck.py", spec, "-o", out)
    assert r.returncode == 0, r.stdout + r.stderr
    texts = []
    for slide in pptx.Presentation(out).slides:
        for sh in slide.shapes:
            if sh.has_text_frame:
                texts.append(sh.text_frame.text)
    joined = " ".join(texts)
    assert "△2.8" in joined and "-2.8" not in joined


def test_validate_rejects_financial_summary_without_table_or_chart(tmp_path):
    deck = {"meta": {}, "slides": [{
        "pattern": "financial_summary",
        "title": "売上高は3年で2.4倍の32.4億円に拡大し、利益率も同時に改善している",
        "source": "テスト",
    }]}
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "financial_summary" in r.stdout


def test_validate_rejects_player_missing_or_out_of_range_xy(tmp_path):
    deck = {"meta": {}, "slides": [{
        "pattern": "competitive_landscape",
        "title": "統合スイート×中堅企業の右上象限は当社のみが占める空白地帯である",
        "x_axis": {"low": "単機能", "high": "統合"},
        "y_axis": {"low": "小規模", "high": "大企業"},
        "players": [{"name": "当社", "y": 0.5}, {"name": "A社", "x": 1.5, "y": 0.2}],
        "source": "テスト",
    }]}
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1
    assert "がない/数値でない" in r.stdout and "範囲外" in r.stdout


def test_validate_allows_primary_insight_with_accent_series(tmp_path):
    # insight_style "primary" は Accent を消費しない — series の ECC85A 1 回は適法
    deck = _minimal_deck(insight="一言インサイト", insight_style="primary")
    deck["slides"][0]["chart"]["series"][0]["color"] = "ECC85A"
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", spec)
    assert r.returncode == 0, r.stdout + r.stderr


def test_validate_rejects_too_many_takeaways(tmp_path):
    deck = _minimal_deck(
        takeaways=[{"heading": f"論点{i}", "body": "根拠"} for i in range(1, 6)])
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "takeaways" in r.stdout


def test_build_handles_null_focal_category_with_annotation(tmp_path):
    # LLM は「focal なし」を null で表現しがち — dict.get のデフォルトでは拾えない
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["focal_category"] = None
    deck["slides"][0]["chart"]["annotation"] = {"yoy": "+12%"}
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(deck, ensure_ascii=False))
    out = tmp_path / "deck.pptx"
    r = run("build_deck.py", spec, "-o", out)
    assert r.returncode == 0, r.stdout + r.stderr


def test_negative_waterfall_stays_inside_slide(tmp_path):
    from pptx.util import Inches

    deck = {"meta": {}, "slides": [{
        "pattern": "waterfall",
        "title": "一過性費用12億円の計上で通期は7億円の赤字に転落する見込みである",
        "unit": "億円",
        "items": [{"label": "期首", "value": 5, "kind": "start"},
                  {"label": "一過性費用", "value": -12},
                  {"label": "期末", "value": -7, "kind": "end"}],
        "source": "テスト",
    }]}
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(deck, ensure_ascii=False))
    out = tmp_path / "deck.pptx"
    r = run("build_deck.py", spec, "-o", out)
    assert r.returncode == 0, r.stdout + r.stderr
    for slide in pptx.Presentation(out).slides:
        for sh in slide.shapes:
            if sh.top is not None and sh.height is not None:
                assert sh.top + sh.height <= Inches(7.51), \
                    f"shape extends past slide bottom: {sh.shape_type}"


def test_section_divider_without_number_has_no_void(tmp_path):
    from pptx.util import Inches

    deck = {"meta": {}, "slides": [{"pattern": "section_divider", "title": "市場環境"}]}
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(deck, ensure_ascii=False))
    out = tmp_path / "deck.pptx"
    r = run("build_deck.py", spec, "-o", out)
    assert r.returncode == 0, r.stdout + r.stderr
    tops = [sh.top for slide in pptx.Presentation(out).slides for sh in slide.shapes
            if sh.has_text_frame and "市場環境" in sh.text_frame.text]
    # number を省いたら 96pt 数字分の空洞は入らない(タイトルが光学中心近くに来る)
    assert tops and min(tops) < Inches(3.5)


def test_lint_render_flags_slide_count_mismatch(tmp_path):
    from PIL import Image

    for i in (1, 2):
        Image.new("RGB", (733, 412), (0xFF, 0xFD, 0xFC)).save(tmp_path / f"deck-{i}.png")
    spec = tmp_path / "deck.json"
    spec.write_text(json.dumps(_minimal_deck(), ensure_ascii=False))
    r = run("lint_render.py", tmp_path, "--spec", spec)
    assert r.returncode == 1 and "枚数不一致" in r.stdout


def test_validate_rejects_unsupported_chart_type(tmp_path):
    deck = _minimal_deck()
    deck["slides"][0]["chart"]["type"] = "area"
    bad = tmp_path / "deck.json"
    bad.write_text(json.dumps(deck, ensure_ascii=False))
    r = run("validate_spec.py", bad)
    assert r.returncode == 1 and "未対応" in r.stdout and "Traceback" not in r.stderr


def test_chart_type_lists_stay_in_sync():
    sys.path.insert(0, str(SCRIPTS))
    try:
        import build_deck
        import validate_spec
        assert set(validate_spec.SUPPORTED_CHART_TYPES) == set(build_deck.CHART_TYPES)
    finally:
        sys.path.remove(str(SCRIPTS))
