#!/usr/bin/env python3
"""Evaluate the ACT slide image skill for self-contained behavior."""

from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "build" / "evals" / "act_skill_eval.json"
GENERATION_CONTRACT_MAX_BYTES = 6144


@dataclass
class Result:
    name: str
    passed: bool
    detail: str = ""


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def check_geometry_arithmetic() -> list[Result]:
    geometry = json.loads((ROOT / "build" / "references" / "canonical-geometry.json").read_text(encoding="utf-8"))
    shell, header, body, footer = geometry["outer_shell"], geometry["header"], geometry["body"], geometry["footer"]
    insets = shell["insets_px"]
    expected_insets = {"top": 50, "right": 72, "bottom": 17, "left": 72}
    master_shell = (
        shell["profile"] == "equity_story_master"
        and insets == expected_insets
        and shell["x"] == insets["left"]
        and shell["y"] == insets["top"]
        and geometry["basis"]["width"] - shell["right"] == insets["right"]
        and geometry["basis"]["height"] - shell["bottom"] == insets["bottom"]
    )
    grid = geometry["grid"]
    explicit_grid_closes = (
        grid["columns"] * grid["track_px"]
        + (grid["columns"] - 1) * grid["gutter_px"]
        == shell["width"]
    )
    h1_range = header["h1"]["visible_height_px_range"]
    subtitle_range = header["subtitle"]["visible_height_px_range"]
    subtitle_bottom = header["clearance_datum_y"]
    header_fits = (
        h1_range[0] <= header["h1"]["calibrated_visible_height_px"] <= h1_range[1]
        and subtitle_range[0] <= header["subtitle"]["calibrated_visible_height_px"] <= subtitle_range[1]
        and header["pilot_visible_height_tolerance_px"] == 2
        and header["h1"]["point_size"] == 28
        and header["subtitle"]["point_size"] == 20
        and subtitle_bottom < body["target_envelope_with_footer"]["top"]
    )
    utilization_results = []
    unit = geometry["grid"]["unit_px"]
    for mode, envelope in (
        ("without_footer", body["target_envelope_without_footer"]),
        ("with_footer", body["target_envelope_with_footer"]),
    ):
        snapped_top = ((envelope["top"] + unit - 1) // unit) * unit
        snapped_bottom = (envelope["bottom"] // unit) * unit
        available_height_key = "available_height_without_footer" if mode == "without_footer" else "available_height_with_footer"
        ratio = (snapped_bottom - snapped_top) / body[available_height_key]
        range_key = "height_utilization_range_without_footer" if mode == "without_footer" else "height_utilization_range_with_footer"
        lo, hi = body[range_key]
        utilization_results.append(Result(f"geometry_utilization:{mode}", 0 < lo < hi <= ratio <= 1.0, f"reachable_ratio={ratio:.3f}, target_range={lo:.2f}..{hi:.2f}, span={snapped_top}..{snapped_bottom}"))
    centroid_range = body["centroid_y_range_without_footer"]
    footer_centroid_range = body["centroid_y_range_with_footer"]
    centroid_ok = centroid_range == [0.58, 0.62]
    footer_centroid_ok = footer_centroid_range == [0.55, 0.60]
    quiet_without = body["quiet_clearance_range_without_footer"]
    quiet_with = body["quiet_clearance_range_with_footer"]
    quiet_without_ok = 0 < quiet_without[0] < quiet_without[1] and header["clearance_datum_y"] + quiet_without[1] < body["target_envelope_without_footer"]["bottom"]
    quiet_with_ok = 0 < quiet_with[0] < quiet_with[1] and header["clearance_datum_y"] + quiet_with[1] < body["target_envelope_with_footer"]["bottom"]
    footer_master_ok = (
        {key: footer[key] for key in ("x", "y", "width", "height", "point_size", "max_lines", "line_height_px", "vertical_anchor")}
        == {"x": 72, "y": 866, "width": 1528, "height": 48, "point_size": 9, "max_lines": 2, "line_height_px": 14, "vertical_anchor": "center"}
        and footer["baseline_y_by_max_lines"] == {"1": [895], "2": [888, 902]}
    )
    return [
        Result("geometry_equity_story_master_insets", master_shell, str(shell)),
        Result("geometry_explicit_grid_closes", explicit_grid_closes, str(grid)),
        Result("geometry_header_stack", header_fits, f"h1={h1_range}, subtitle={subtitle_range}, max_bottom={subtitle_bottom}"),
        Result("geometry_area_weighted_centroid_range", centroid_ok, f"range={centroid_range}"),
        Result("geometry_footer_area_weighted_centroid_range", footer_centroid_ok, f"range={footer_centroid_range}"),
        Result("geometry_quiet_clearance:without_footer", quiet_without_ok, f"clearance_range={quiet_without}"),
        Result("geometry_quiet_clearance:with_footer", quiet_with_ok, f"clearance_range={quiet_with}"),
        Result("geometry_provenance_footer_master", footer_master_ok, str(footer)),
        *utilization_results,
    ]


def runtime_files(globs: list[str]) -> list[Path]:
    files: set[Path] = set()
    all_files = [p for p in ROOT.rglob("*") if p.is_file()]
    for pattern in globs:
        for path in all_files:
            rel = path.relative_to(ROOT).as_posix()
            if fnmatch.fnmatch(rel, pattern):
                files.add(path)
    return sorted(files)


def check_frontmatter() -> Result:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return Result("frontmatter", False, "SKILL.md does not start with YAML frontmatter")
    try:
        _, frontmatter, _ = text.split("---", 2)
    except ValueError:
        return Result("frontmatter", False, "SKILL.md frontmatter is not closed")
    name = re.search(r"^name:\s*([A-Za-z0-9_-]+)\s*$", frontmatter, re.MULTILINE)
    desc = re.search(r'^description:\s*"(.+)"\s*$', frontmatter, re.MULTILINE)
    if not name:
        return Result("frontmatter", False, "Missing scalar name")
    if name.group(1) != "act-slide-image-generation":
        return Result("frontmatter", False, f"Unexpected skill name: {name.group(1)}")
    if not desc:
        return Result("frontmatter", False, "Missing quoted scalar description")
    return Result("frontmatter", True)


def check_forbidden_patterns(config: dict, files: list[Path]) -> list[Result]:
    results: list[Result] = []
    for item in config["forbidden_patterns"]:
        pattern = re.compile(item["pattern"])
        matches: list[str] = []
        for path in files:
            rel = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    matches.append(f"{rel}:{lineno}: {line.strip()}")
        if matches:
            detail = item["reason"] + "\n" + "\n".join(matches[:20])
            if len(matches) > 20:
                detail += f"\n... {len(matches) - 20} more"
            results.append(Result(f"forbidden:{item['pattern']}", False, detail))
        else:
            results.append(Result(f"forbidden:{item['pattern']}", True))
    return results


def check_required_phrases(config: dict, files: list[Path]) -> list[Result]:
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    results: list[Result] = []
    for phrase in config["required_skill_phrases"]:
        results.append(Result(f"required:{phrase}", phrase in text, "missing" if phrase not in text else ""))
    return results


def check_script_syntax() -> Result:
    for script in sorted((ROOT / "build" / "scripts").glob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            return Result("script_syntax", False, f"{script.relative_to(ROOT)}: {exc}")
    return Result("script_syntax", True)


def check_entrypoint_symlinks() -> list[Result]:
    expected = {
        "scripts/build_act_slide_prompt.py": "../build/scripts/build_act_slide_prompt.py",
        "scripts/eval_act_skill.py": "../build/scripts/eval_act_skill.py",
        "scripts/package_slide_images_to_pdf.py": "../build/scripts/package_slide_images_to_pdf.py",
        "scripts/package_slide_images_to_pptx.py": "../build/scripts/package_slide_images_to_pptx.py",
        "scripts/test_package_slide_images_to_pptx.py": "../build/scripts/test_package_slide_images_to_pptx.py",
    }
    results: list[Result] = []
    for rel_path, target in expected.items():
        path = ROOT / rel_path
        actual = os.readlink(path) if path.is_symlink() else ""
        results.append(
            Result(
                f"entrypoint_symlink:{rel_path}",
                actual == target,
                f"expected {target}, found {actual or 'regular/missing file'}",
            )
        )
    return results


def run_helper_check(check: dict) -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(script), *check["args"]],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    combined = proc.stdout + proc.stderr
    expected = check["expect_exit"]
    if proc.returncode != expected:
        return Result(check["name"], False, f"exit {proc.returncode}, expected {expected}\n{combined[:2000]}")
    for needle in check.get("must_contain", []):
        if needle not in combined:
            return Result(check["name"], False, f"missing output: {needle}\n{combined[:2000]}")
    for needle in check.get("must_not_contain", []):
        if needle in combined:
            return Result(check["name"], False, f"forbidden output: {needle}\n{combined[:2000]}")
    return Result(check["name"], True)


def check_final_generation_prompt_hygiene() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--mode",
            "single-slide-image",
            "--archetype",
            "market-table + supporting-context",
            "--grid-mode",
            "message-led split",
            "--layout-plan",
            "build/evals/sample-layout-plan.json",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    combined = proc.stdout + proc.stderr
    if proc.returncode != 0:
        return Result("final_generation_prompt_hygiene", False, combined[:2000])
    payload = combined
    if "ACT slide image generation contract" not in payload:
        return Result("final_generation_prompt_hygiene", False, "missing lean generation contract")
    forbidden = [
        "review_manifest",
        "weak_slide_regeneration_queue",
        "slides_final/",
        "PPTX package gate",
        "credential_setup_blocker",
        "slides_package/",
        "render_check/",
    ]
    hits = [needle for needle in forbidden if needle in payload]
    if hits:
        return Result("final_generation_prompt_hygiene", False, "forbidden generation-prompt terms: " + ", ".join(hits))
    if "size=2048x1152" not in payload:
        return Result("final_generation_prompt_hygiene", False, "default 2048x1152 image size missing from generation prompt payload")
    if len(payload.encode("utf-8")) > GENERATION_CONTRACT_MAX_BYTES:
        return Result("final_generation_prompt_hygiene", False, f"generation contract exceeds {GENERATION_CONTRACT_MAX_BYTES} bytes: {len(payload.encode('utf-8'))}")
    negative_directives = [
        r"\bdo not\b",
        r"\bnever\b",
        r"\bavoid\b",
        r"\breject\b",
        r"\bblocker\b",
        r"\bwrong\b",
        r"\bmissing\b",
        r"\bmalformed\b",
    ]
    hits = [pattern for pattern in negative_directives if re.search(pattern, payload, flags=re.IGNORECASE)]
    if hits:
        return Result("final_generation_prompt_hygiene", False, "negative directive leaked into generation contract: " + ", ".join(hits))
    return Result("final_generation_prompt_hygiene", True)


def slice_named_block(text: str, start_label: str, end_label: str) -> str:
    start = text.find(start_label)
    if start < 0:
        return ""
    end = text.find(end_label, start)
    if end < 0:
        end = len(text)
    return text[start:end]


def check_deck_plan_output_hygiene() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(script), "--mode", "deck-plan", "--size", "2048x1152"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    combined = proc.stdout + proc.stderr
    if proc.returncode != 0:
        return Result("deck_plan_output_hygiene", False, combined[:2000])
    canvas_contract = slice_named_block(combined, "non_negotiable_canvas_contract:", "planning_scope:")
    planning_scope = slice_named_block(combined, "planning_scope:", "generation_handoff:")
    generation_handoff = slice_named_block(combined, "generation_handoff:", "__END_OF_DECK_PLAN_OUTPUT__")
    if not canvas_contract or not planning_scope or not generation_handoff:
        return Result("deck_plan_output_hygiene", False, "missing scoped deck-plan blocks")
    required_contract = [
        "non_negotiable_canvas_contract",
        "composition_clarity",
        "78-92%",
        "82-94%",
        "grid_contract",
        "flex_contract",
        "layout_tree_gate",
        "58-62%",
    ]
    required_planning = ["argument_closure_lock", "deck_argument_plan", "closure_matrix"]
    required_handoff = ["generation_handoff", "grid_plan", "exact_text"]
    missing = (
        [needle for needle in required_contract if needle not in canvas_contract]
        + [needle for needle in required_planning if needle not in planning_scope]
        + [needle for needle in required_handoff if needle not in generation_handoff]
    )
    if missing:
        return Result("deck_plan_output_hygiene", False, "missing deck-plan terms: " + ", ".join(missing))
    rigid = ["density_tier", "layout_diversity_plan", "mece_support_gate", "icon_density_budget"]
    present = [needle for needle in rigid if needle in canvas_contract + planning_scope]
    if present:
        return Result("deck_plan_output_hygiene", False, "rigid body terms leaked: " + ", ".join(present))
    return Result("deck_plan_output_hygiene", True)


def check_visual_regression_cases() -> Result:
    path = ROOT / "build" / "evals" / "visual-regression-cases.json"
    if not path.exists():
        return Result("visual_regression_cases", False, "missing visual-regression-cases.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases") if isinstance(data, dict) else None
    if data.get("schema_version") != 1 or not isinstance(cases, list):
        return Result("visual_regression_cases", False, "invalid schema")
    classes = {case.get("class") for case in cases if isinstance(case, dict)}
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(cases) < 9 or classes != {"typical", "edge", "adversarial"} or len(ids) != len(set(ids)):
        return Result("visual_regression_cases", False, f"cases={len(cases)} classes={sorted(classes)} unique_ids={len(set(ids))}")
    incomplete = [
        case.get("id")
        for case in cases
        if not case.get("expected_route") or not case.get("hard_gates") or not case.get("pairwise_review")
    ]
    if incomplete:
        return Result("visual_regression_cases", False, "incomplete cases: " + ", ".join(map(str, incomplete)))
    return Result("visual_regression_cases", True)


def check_source_none_contract() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    with tempfile.TemporaryDirectory() as tmp:
        brief = Path(tmp) / "brief.md"
        brief.write_text("H1: サンプル\nsource_line: none\n", encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                str(brief),
                "--mode",
                "single-slide-image",
                "--archetype",
                "process",
                "--grid-mode",
                "16-column hybrid Grid/Flex",
                "--layout-plan",
                "build/evals/sample-layout-plan.json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    required = [
        "source_line: none",
        '"visibility":"none"',
        '"reference_class":"none"',
        "empty provenance keeps the footer quiet",
    ]
    missing = [needle for needle in required if needle not in proc.stdout]
    if proc.returncode != 0 or missing:
        return Result("source_none_contract", False, proc.stderr[:1000] or "missing: " + ", ".join(missing))
    return Result("source_none_contract", True)


def valid_png_bytes(rgb: tuple[int, int, int] = (255, 255, 255), width: int = 2048, height: int = 1152) -> bytes:
    import binascii
    import struct
    import zlib

    def chunk(kind: bytes, data: bytes) -> bytes:
        crc = binascii.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)

    raw_scanline = b"\x00" + (bytes(rgb) * width)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw_scanline * height))
        + chunk(b"IEND", b"")
    )


def approved_review_manifest(images: list[Path]) -> dict[str, object]:
    deck_only_design_statuses = {
        "deck_tone_consistency_status": "approved",
        "illustration_consistency_status": "approved",
    }
    approved_design_statuses = {
        "post_generation_design_balance_status": "approved",
        "whitespace_occupancy_balance_status": "approved",
        "density_balance_status": "approved",
        "typography_balance_status": "approved",
        "ergonomic_text_minimum_status": "approved",
        "color_consistency_status": "approved",
        "outer_padding_consistency_status": "approved",
        "outer_shell_profile_status": "approved",
        "fixed_zone_grid_status": "approved",
        "header_zone_boundary_status": "approved",
        "content_area_padding_consistency_status": "approved",
        "header_integrity_status": "approved",
        "header_scale_master_status": "approved",
        "source_provenance_status": "approved",
        "message_box_text_only_status": "approved",
        "icon_justification_status": "approved",
        "icon_box_compaction_status": "approved",
        "multimodal_design_review_status": "approved",
        "design_balance_gate_status": "approved",
        "occupancy_density_fit_status": "approved",
        "font_scale_unity_status": "approved",
        "palette_role_unity_status": "approved",
        "design_breakage_blocker_status": "approved",
    }
    return {
        "schema_version": 1,
        "all_generated_images_reviewed": True,
        "weak_slide_regeneration_queue": [],
        "review_evidence": {
            "reviewer": "skill-eval",
            "reviewed_at": "2026-01-01T00:00:00Z",
            "png_sha256_by_slide": {
                str(idx): hashlib.sha256(path.read_bytes()).hexdigest()
                for idx, path in enumerate(images, 1)
            },
        },
        "final_image_quality_status": "approved",
        "content_quality_status": "approved",
        "design_quality_status": "approved",
        "deck_unity_status": "approved",
        "completion_ready_status": "approved",
        "review_manifest_status": "approved",
        **deck_only_design_statuses,
        **approved_design_statuses,
        "slides": [
            {
                "slide_id": str(idx),
                "png_path": str(image),
                "top_visible_margin": 69,
                "bottom_visible_margin": 68,
                "image_review_status": "approved",
                "final_image_quality_status": "approved",
                "content_quality_status": "approved",
                "design_quality_status": "approved",
                **approved_design_statuses,
                "blockers": [],
                "majors": [],
            }
            for idx, image in enumerate(images, 1)
        ],
    }


def run_pptx_package_check() -> Result:
    script = ROOT / "build" / "scripts" / "package_slide_images_to_pptx.py"
    png_bytes = valid_png_bytes()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        slides_dir = tmp_path / "slides_final"
        slides_dir.mkdir()
        image1 = slides_dir / "slide01.png"
        image2 = slides_dir / "slide02.png"
        image1.write_bytes(png_bytes)
        image2.write_bytes(png_bytes)
        notes = tmp_path / "notes.json"
        notes.write_text(json.dumps(["note 1", "note 2"], ensure_ascii=False), encoding="utf-8")
        manifest = tmp_path / "review-manifest.json"
        manifest.write_text(json.dumps(approved_review_manifest([image1, image2]), ensure_ascii=False), encoding="utf-8")
        output = tmp_path / "deck.pptx"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--output",
                str(output),
                "--notes-json",
                str(notes),
                "--review-manifest",
                str(manifest),
                str(image1),
                str(image2),
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined = proc.stdout + proc.stderr
        if proc.returncode != 0:
            return Result("pptx_package_check", False, combined[:2000])
        if "pptx_package_status: created" not in combined or "pptx_slide_count: 2" not in combined:
            return Result("pptx_package_check", False, combined[:2000])
        if "pptx_image_mapping:" not in combined or "pptx_speaker_notes_mapping:" not in combined:
            return Result("pptx_package_check", False, combined[:2000])
        if "review_manifest_status: approved" not in combined:
            return Result("pptx_package_check", False, combined[:2000])
        try:
            import zipfile

            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                note1 = archive.read("ppt/notesSlides/notesSlide1.xml").decode("utf-8")
                note2 = archive.read("ppt/notesSlides/notesSlide2.xml").decode("utf-8")
        except Exception as exc:  # pragma: no cover - defensive eval detail
            return Result("pptx_package_check", False, str(exc))
        required = {
            "ppt/presentation.xml",
            "ppt/slides/slide1.xml",
            "ppt/slides/slide2.xml",
            "ppt/media/image1.png",
            "ppt/media/image2.png",
            "ppt/notesSlides/notesSlide1.xml",
            "ppt/notesSlides/notesSlide2.xml",
        }
        missing = required - names
        if missing:
            return Result("pptx_package_check", False, f"missing entries: {', '.join(sorted(missing))}")
        if "note 1" not in note1 or "note 2" not in note2:
            return Result("pptx_package_check", False, "speaker notes text was not preserved")
    return Result("pptx_package_check", True)


def run_pdf_package_check() -> Result:
    script = ROOT / "build" / "scripts" / "package_slide_images_to_pdf.py"
    png_bytes = valid_png_bytes()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        slides_dir = tmp_path / "slides_final"
        slides_dir.mkdir()
        image1 = slides_dir / "slide01.png"
        image2 = slides_dir / "slide02.png"
        image1.write_bytes(png_bytes)
        image2.write_bytes(png_bytes)
        manifest = tmp_path / "review-manifest.json"
        manifest.write_text(json.dumps(approved_review_manifest([image1, image2]), ensure_ascii=False), encoding="utf-8")
        output = tmp_path / "deck.pdf"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--output",
                str(output),
                "--review-manifest",
                str(manifest),
                str(slides_dir),
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined = proc.stdout + proc.stderr
        if proc.returncode != 0:
            return Result("pdf_package_check", False, combined[:2000])
        if "pdf_package_status: created" not in combined or "pdf_slide_count: 2" not in combined:
            return Result("pdf_package_check", False, combined[:2000])
        if "pdf_output_path:" not in combined:
            return Result("pdf_package_check", False, combined[:2000])
        if "pdf_image_mapping: {" not in combined:
            return Result("pdf_package_check", False, combined[:2000])
        if not output.exists() or output.stat().st_size <= 0:
            return Result("pdf_package_check", False, "PDF output was not created")
        if not output.read_bytes().startswith(b"%PDF"):
            return Result("pdf_package_check", False, "PDF output does not start with %PDF")
        bad_image = tmp_path / "slide-outside-master.png"
        bad_image.write_bytes(png_bytes)
        bad_manifest = tmp_path / "bad-review-manifest.json"
        bad_manifest.write_text(json.dumps(approved_review_manifest([bad_image]), ensure_ascii=False), encoding="utf-8")
        bad_proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--output",
                str(tmp_path / "bad.pdf"),
                "--review-manifest",
                str(bad_manifest),
                str(bad_image),
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if bad_proc.returncode == 0:
            return Result("pdf_package_check", False, "PDF package accepted image outside slides_final/")
        for rel_path in ["slides_package/slide01.png", "render_check/pdf_pages/page-01.png"]:
            derivative_image = tmp_path / rel_path
            derivative_image.parent.mkdir(parents=True, exist_ok=True)
            derivative_image.write_bytes(png_bytes)
            derivative_manifest = tmp_path / f"{derivative_image.stem}-review-manifest.json"
            derivative_manifest.write_text(
                json.dumps(approved_review_manifest([derivative_image]), ensure_ascii=False),
                encoding="utf-8",
            )
            derivative_proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--output",
                    str(tmp_path / f"{derivative_image.stem}.pdf"),
                    "--review-manifest",
                    str(derivative_manifest),
                    str(derivative_image),
                ],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if derivative_proc.returncode == 0:
                return Result("pdf_package_check", False, f"PDF package accepted derivative source path: {rel_path}")
    return Result("pdf_package_check", True)


def check_no_old_files() -> list[Result]:
    # Guard against stale cross-brand artifacts copied into the ACT skill root.
    old_paths = [
        ROOT / "references" / "atom-slide-patterns-essentials.md",
        ROOT / "scripts" / "build_atom_slide_prompt.py",
        ROOT / "scripts" / "eval_atom_skill.py",
        ROOT / "evals" / "atom_skill_eval.json",
    ]
    results = [Result(f"old_file_absent:{path.relative_to(ROOT)}", not path.exists(), "exists" if path.exists() else "") for path in old_paths]
    pycache_dirs = [p.relative_to(ROOT) for p in ROOT.rglob("__pycache__") if p.is_dir()]
    results.append(Result("no_pycache_dirs", not pycache_dirs, ", ".join(str(p) for p in pycache_dirs)))
    return results


def check_current_master_contract() -> list[Result]:
    """Prove the current master reaches the generated scaffold, not only docs."""
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--mode",
            "single-slide-image",
            "--archetype",
            "content-led composition",
            "--grid-mode",
            "content-led alignment",
            "--layout-plan",
            "build/evals/sample-layout-plan.json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = proc.stdout
    if proc.returncode != 0:
        return [Result("master_output_execution", False, proc.stderr[:2000])]
    required = [
        "ACT slide image generation contract",
        "DELIVERABLE",
        "MESSAGE",
        "CANVAS",
        "LAYOUT MAP",
        "EXACT COPY",
        "VISUAL SYSTEM",
        "PRESERVATION STATE",
        "ACCEPTANCE",
        "output_basis=2048x1152",
        "canvas #FCFCFB",
        "shell profile equity_story_master",
        "one 28pt/700 line",
        "one 20pt/400 line",
        "occurrences=1",
        "compiled_render_plan=",
        "visible glyph height 58-61px",
        "visible glyph height 40-43px",
        "source_plan=",
        "message_box_plan=",
        "Header surface=uninterrupted canvas; visible components=[header_h1,header_subtitle]; geometry=0.",
        "Source: appears only for one external reference",
        "every message box is text-only",
    ]
    forbidden = [
        "H1 28-32pt",
        "subtitle 18-21pt",
        "one uniform 38pt/700 line",
        "one 32pt/400 line",
        "body_start_y=105",
        "105/784/52",
        "repair_required",
        "flex_contract:",
        "header_rule",
    ]
    results = [
        Result(f"master_output_required:{needle}", needle in output, "missing from generated scaffold")
        for needle in required
    ]
    results.extend(
        Result(f"master_output_forbidden:{needle}", needle not in output, "stale master leaked into generated scaffold")
        for needle in forbidden
    )
    results.append(Result("master_output_prompt_budget", len(output.encode("utf-8")) <= GENERATION_CONTRACT_MAX_BYTES, f"prompt bytes={len(output.encode('utf-8'))}"))
    results.append(Result("master_output_message_box_scaled_height", '"height_px":89' in output and '"line_height_px":31' in output, "message-box metrics must use the 2048x1152 render basis"))
    results.append(Result("master_output_message_box_no_source_basis_height", '"height_px":73' not in output, "1672-basis message-box height leaked into the render prompt"))
    results.append(Result("master_output_message_box_center_alignment", "anchor=(1024,1019) | alignment=center" in output, "message-box text must use the render-basis center anchor"))
    return results


def check_layout_plan_geometry_rejections() -> list[Result]:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    base = json.loads((ROOT / "build" / "evals" / "sample-layout-plan.json").read_text(encoding="utf-8"))
    def add_visible_source(plan: dict, *, source_line: str = "Source: Public Report", baseline: int = 895) -> None:
        plan["footer_mode"] = "present"
        plan["source_plan"] = {
            "visibility": "visible",
            "reference_class": "external_publication",
            "publication_title": "Public Report",
            "locator": "https://example.com/public-report",
            "source_line": source_line,
            "annotations": [],
        }
        plan["content_atom_registry"]["atoms"].append({
            "id": "source",
            "exact_text": source_line,
            "semantic_role": "footer",
            "component_id": "footer_master",
            "anchor_line": 1,
            "baseline_step": baseline,
            "max_lines": 1,
            "expected_occurrences": 1,
        })
        plan["model_fit_plan"]["visible_string_count"] += 1

    def add_message_box_icon_atom(plan: dict) -> None:
        plan["content_atom_registry"]["atoms"].append({
            "id": "message_icon",
            "exact_text": "icon",
            "semantic_role": "icon",
            "component_id": "message_box",
            "anchor_line": 10,
            "baseline_step": 832,
            "max_lines": 1,
            "expected_occurrences": 1,
        })
        plan["model_fit_plan"]["visible_string_count"] += 1

    def add_direct_grid_component(plan: dict) -> None:
        plan["component_geometry_plan"]["components"].append({
            "id": "direct_grid_component",
            "type": "module",
            "parent_id": "body",
            "bounds": {"x": 72, "y": 200, "w": 1528, "h": 64},
            "left_anchor_line": 1,
            "right_anchor_line": 17,
            "top_baseline_step": 200,
            "bottom_baseline_step": 264,
            "role": "evidence_region",
            "peer_group": "",
            "padding_px": 24,
        })

    def overlap_quiet_region_with_direct_grid_content(plan: dict) -> None:
        plan["quiet_region"]["bounds"] = {"x": 169, "y": 272, "w": 96, "h": 96}

    def add_unregistered_flex_child_node(plan: dict) -> None:
        plan["layout_tree"]["nodes"].append({"id": "nested_grid", "parent_id": "main", "layout": "grid"})
        plan["flex_plan"]["containers"][0]["children"][0]["id"] = "nested_grid"

    cases: list[tuple[str, callable]] = [
        ("argument_plan_missing", lambda plan: plan.pop("slide_argument_plan")),
        ("argument_evidence_unbound", lambda plan: plan["slide_argument_plan"].update(evidence_atom_ids=["missing_atom"])),
        ("argument_claim_title_drift", lambda plan: plan["slide_argument_plan"].update(claim="別の主張")),
        ("closure_contradiction_present", lambda plan: plan["closure_matrix"].update(unresolved_contradiction_count=1)),
        ("closure_transition_incomplete", lambda plan: plan["closure_matrix"].update(adjacent_slide_transition_coverage=0.8)),
        ("closure_open_row_without_open_item", lambda plan: plan["closure_matrix"]["rows"][6].update(status="open_with_owner_and_due_date")),
        ("container_target_mismatch", lambda plan: plan["occupancy_plan"].update(container_width_target=0.96)),
        ("body_target_exceeds_container", lambda plan: plan["occupancy_plan"].update(body_width_target=0.94)),
        ("body_target_in_range_but_derived_mismatch", lambda plan: plan["occupancy_plan"].update(body_width_target=0.80)),
        ("direct_grid_component_changes_mass", add_direct_grid_component),
        ("quiet_region_over_painted_component", overlap_quiet_region_with_direct_grid_content),
        ("header_geometry_present", lambda plan: plan["header_furniture_plan"].update(visible_geometry_count=1)),
        ("flex_outside_shell", lambda plan: plan["flex_plan"]["containers"][0]["bounds"].update(x=0)),
        ("off_baseline_row", lambda plan: plan["grid_plan"]["regions"][0].update(row_start=250)),
        ("ink_target_out_of_range", lambda plan: plan["occupancy_plan"].update(text_ink_area_share_target=0.90)),
        ("envelope_overflow", lambda plan: [plan["grid_plan"]["regions"][0].update(row_end=864), plan["flex_plan"]["containers"][0]["bounds"].update(h=616)]),
        ("footer_absent_body_too_high", lambda plan: [plan["grid_plan"]["regions"][0].update(row_end=856), plan["flex_plan"]["containers"][0]["bounds"].update(h=568), plan["flex_plan"]["containers"][0]["children"][0]["allocation_bounds"].update(h=568), plan["flex_plan"]["containers"][0]["children"][1]["allocation_bounds"].update(h=568)]),
        ("footer_absent_body_starts_too_low", lambda plan: [plan["grid_plan"]["regions"][0].update(row_start=304), plan["flex_plan"]["containers"][0]["bounds"].update(y=304, h=560), plan["flex_plan"]["containers"][0]["children"][0]["allocation_bounds"].update(y=304, h=560), plan["flex_plan"]["containers"][0]["children"][1]["allocation_bounds"].update(y=304, h=560), plan["occupancy_plan"].update(container_height_target=0.89)]),
        ("sparse_fixed_flex", lambda plan: [child.update(basis_px=10, grow=0) for child in plan["flex_plan"]["containers"][0]["children"]]),
        ("component_anchor_outside_grid", lambda plan: plan["component_geometry_plan"]["components"][0].update(left_anchor_line=0)),
        ("component_anchor_geometry_drift", lambda plan: plan["component_geometry_plan"]["components"][0]["bounds"].update(x=180, w=644)),
        ("peer_module_size_drift", lambda plan: plan["component_geometry_plan"]["components"][0]["bounds"].update(w=620)),
        ("flex_gap_mismatch", lambda plan: plan["flex_plan"]["containers"][0]["children"][1]["allocation_bounds"].update(x=860, w=643)),
        ("flex_cross_axis_underfill", lambda plan: [plan["flex_plan"]["containers"][0]["children"][0].update(min_cross_px=80), plan["flex_plan"]["containers"][0]["children"][0]["allocation_bounds"].update(h=80)]),
        ("flex_invalid_wrap", lambda plan: plan["flex_plan"]["containers"][0].update(wrap="wrpa")),
        ("flex_child_without_registered_geometry", add_unregistered_flex_child_node),
        ("freeform_connector_route", lambda plan: plan["connector_plan"]["connectors"][0].update(route="freeform")),
        ("connector_crossing", lambda plan: plan["connector_plan"]["connectors"][0].update(crossing_count=1)),
        ("connector_endpoint_drift", lambda plan: plan["connector_plan"]["connectors"][0]["waypoints"][0].update(x=800)),
        ("declared_arc_endpoint_drift", lambda plan: [plan["connector_plan"]["connectors"][0].update(route="declared_arc"), plan["connector_plan"]["connectors"][0]["waypoints"][0].update(x=800)]),
        ("connector_waypoint_in_header", lambda plan: plan["connector_plan"]["connectors"][0]["waypoints"][0].update(y=96)),
        ("connector_unknown_port", lambda plan: plan["connector_plan"]["connectors"][0].update(source_port="accent_edge")),
        ("unregistered_rule_parent", lambda plan: plan["structural_rule_plan"]["rules"][0].update(parent_id="missing")),
        ("rule_stroke_out_of_range", lambda plan: plan["structural_rule_plan"]["rules"][0].update(stroke_px=6)),
        ("rule_anchor_point_drift", lambda plan: plan["structural_rule_plan"]["rules"][0]["start_point"].update(x=266)),
        ("grid_rigidity_below_gate", lambda plan: plan["rigidity_plan"].update(edge_registration_score=0.80, grid_rigidity_score=0.912)),
        ("orphan_region_present", lambda plan: plan["rigidity_plan"].update(orphan_region_count=1)),
        ("too_many_visible_strings", lambda plan: plan["model_fit_plan"].update(visible_string_count=24)),
        ("multi_slide_batch", lambda plan: plan["model_fit_plan"].update(generation_batch_size=3)),
        ("unapproved_render_feasibility", lambda plan: plan["model_fit_plan"].update(render_feasibility="split")),
        ("wrong_prompt_basis", lambda plan: plan["model_fit_plan"].update(prompt_compilation_basis="1672x941")),
        ("reading_path_count_mismatch", lambda plan: plan["model_fit_plan"].update(reading_path_steps=3)),
        ("mixed_visual_grammar", lambda plan: plan["clarity_plan"].update(visual_grammar="comparison")),
        ("excess_connectors", lambda plan: plan["clarity_plan"].update(connector_count=3)),
        ("redundant_encoding", lambda plan: plan["clarity_plan"].update(redundant_encoding_count=1)),
        ("invalid_surface_radius", lambda plan: plan["surface_plan"].update(major_radius_px=20)),
        ("monolithic_surface_count", lambda plan: plan["surface_plan"].update(top_level_surface_count=1)),
        ("tone_role_drift", lambda plan: plan["tone_plan"].update(structural_role="unregistered_role")),
        ("tone_assignment_missing", lambda plan: plan["tone_plan"]["role_assignments"].pop()),
        ("tone_target_missing", lambda plan: plan["tone_plan"]["role_assignments"][3].update(target_id="missing")),
        ("mixed_mark_language", lambda plan: plan["clarity_plan"].update(mark_language_consistency=0.70)),
        ("unbalanced_region_distribution", lambda plan: plan["clarity_plan"].update(region_internal_distribution_consistency=0.60)),
        ("copy_occurrence_mismatch", lambda plan: plan["content_atom_registry"]["atoms"][0].update(expected_occurrences=2)),
        ("copy_component_missing", lambda plan: plan["content_atom_registry"]["atoms"][2].update(component_id="missing")),
        ("copy_anchor_outside_owner", lambda plan: plan["content_atom_registry"]["atoms"][2].update(anchor_line=17)),
        ("copy_count_mismatch", lambda plan: plan["content_atom_registry"]["atoms"].pop()),
        ("header_h1_missing", lambda plan: plan["content_atom_registry"]["atoms"].pop(0)),
        ("header_h1_off_master_baseline", lambda plan: plan["content_atom_registry"]["atoms"][0].update(baseline_step=800)),
        ("header_subtitle_wrong_anchor", lambda plan: plan["content_atom_registry"]["atoms"][1].update(anchor_line=2)),
        ("source_footer_mode_mismatch", lambda plan: plan.update(footer_mode="present")),
        ("footer_present_message_box", lambda plan: add_visible_source(plan)),
        ("source_internal_class", lambda plan: plan["source_plan"].update(visibility="visible", reference_class="internal_note", publication_title="Meeting memo", locator="https://example.com/memo", source_line="Source: Meeting memo")),
        ("source_locator_not_traceable", lambda plan: plan["source_plan"].update(visibility="visible", reference_class="external_publication", publication_title="Report", locator="report.pdf", source_line="Source: Report")),
        ("source_prefix_not_exact", lambda plan: plan["source_plan"].update(visibility="visible", reference_class="external_publication", publication_title="Report", locator="https://example.com/report", source_line="Reference: Report")),
        ("source_prefix_only_contained", lambda plan: add_visible_source(plan, source_line="Reference Source: Public Report")),
        ("source_off_canonical_baseline", lambda plan: add_visible_source(plan, baseline=856)),
        ("footer_annotation_bad_prefix", lambda plan: plan["source_plan"].update(annotations=["Memo: internal"])),
        ("footer_annotation_wrong_order", lambda plan: plan["source_plan"].update(annotations=["Note: scope", "Assumption: estimate"])),
        ("footer_annotation_duplicate", lambda plan: plan["source_plan"].update(annotations=["Assumption: one", "Assumption: two"])),
        ("footer_annotation_without_footer_atom", lambda plan: plan["source_plan"].update(annotations=["Assumption: estimate"])),
        ("message_box_icon_child", lambda plan: plan["message_box_plan"]["boxes"][0].update(icon_children=["decorative_icon"])),
        ("message_box_noncanonical_id", lambda plan: plan["message_box_plan"]["boxes"][0].update(component_id="takeaway_box")),
        ("message_box_icon_atom", add_message_box_icon_atom),
        ("message_box_height_not_derived", lambda plan: plan["message_box_plan"]["boxes"][0].update(height_px=120)),
        ("message_box_padding_not_token", lambda plan: plan["message_box_plan"]["boxes"][0].update(vertical_padding_px=20)),
        ("message_box_master_geometry_drift", lambda plan: plan["component_geometry_plan"]["components"][2]["bounds"].update(x=169, w=1334)),
    ]
    results: list[Result] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, mutate in cases:
            plan = json.loads(json.dumps(base))
            mutate(plan)
            path = Path(tmp) / f"{name}.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--mode",
                    "single-slide-image",
                    "--archetype",
                    "content-led composition",
                    "--grid-mode",
                    "hybrid Grid/Flex",
                    "--layout-plan",
                    str(path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            results.append(Result(f"layout_plan_rejects:{name}", proc.returncode == 1, proc.stdout + proc.stderr if proc.returncode != 1 else ""))
    return results


def configure_footer_present_body(plan: dict) -> None:
    """Fit the sample body to the footer-present envelope without a bottom message box."""
    plan["footer_mode"] = "present"
    plan["message_box_plan"]["boxes"] = []
    plan["layout_tree"]["nodes"] = [node for node in plan["layout_tree"]["nodes"] if node["id"] != "message_box"]
    plan["component_geometry_plan"]["components"] = [
        component for component in plan["component_geometry_plan"]["components"] if component["id"] != "message_box"
    ]
    takeaway = next(atom for atom in plan["content_atom_registry"]["atoms"] if atom["id"] == "takeaway")
    takeaway.update(component_id="item_b", anchor_line=12, baseline_step=720)
    plan["grid_plan"]["regions"][0]["row_end"] = 816
    container = plan["flex_plan"]["containers"][0]
    container["bounds"]["h"] = 544
    for child in container["children"]:
        child["allocation_bounds"]["h"] = 544
    for component in plan["component_geometry_plan"]["components"]:
        component["bounds"]["h"] = 544
        component["bottom_baseline_step"] = 816
    for waypoint in plan["connector_plan"]["connectors"][0]["waypoints"]:
        waypoint["y"] = 544
    plan["occupancy_plan"].update(
        body_height_target=0.83,
        container_height_target=0.83,
        allocated_area_target=0.72,
    )


def check_footer_present_layout_plan() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    plan = json.loads((ROOT / "build" / "evals" / "sample-layout-plan.json").read_text(encoding="utf-8"))
    configure_footer_present_body(plan)
    plan["source_plan"] = {
        "visibility": "visible",
        "reference_class": "external_publication",
        "publication_title": "Public Dataset 2026",
        "locator": "https://example.com/public-dataset",
        "source_line": "Source: Public Dataset 2026",
        "annotations": ["Assumption: management estimate"],
    }
    plan["content_atom_registry"]["atoms"].append({
        "id": "source",
        "exact_text": "Source: Public Dataset 2026   Assumption: management estimate",
        "semantic_role": "footer",
        "component_id": "footer_master",
        "anchor_line": 1,
        "baseline_step": 888,
        "max_lines": 2,
        "expected_occurrences": 1,
    })
    plan["model_fit_plan"]["visible_string_count"] += 1
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "footer-present.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--mode",
                "single-slide-image",
                "--archetype",
                "content-led composition",
                "--grid-mode",
                "hybrid Grid/Flex",
                "--layout-plan",
                str(path),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    output = proc.stdout
    required = ['"component_id":"footer_master"', '"x":88', '"y":1060', '"w":1872', '"h":59', '"line_height_px":17', '"baseline_y_by_line":[1087,1104]', '"surface":"transparent_text_frame"', '"painted_geometry_count":0', 'Assumption: management estimate']
    return Result("footer_present_layout_plan", proc.returncode == 0 and all(item in output for item in required), proc.stdout + proc.stderr if proc.returncode else "missing render-basis footer geometry")


def check_nested_flex_layout_plan() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    plan = json.loads((ROOT / "build" / "evals" / "sample-layout-plan.json").read_text(encoding="utf-8"))
    plan["layout_tree"]["nodes"].append({"id": "nested_flex", "parent_id": "main", "layout": "flex"})
    next(node for node in plan["layout_tree"]["nodes"] if node["id"] == "item_b")["parent_id"] = "nested_flex"
    main = plan["flex_plan"]["containers"][0]
    main["children"][1]["id"] = "nested_flex"
    nested_bounds = dict(main["children"][1]["allocation_bounds"])
    plan["flex_plan"]["containers"].append({
        "id": "nested_flex",
        "bounds": nested_bounds,
        "main_axis": "row",
        "wrap": "nowrap",
        "line_plan": [1],
        "gap_px": 16,
        "justify": "start",
        "align": "stretch",
        "children": [{
            "id": "item_b",
            "basis_px": nested_bounds["w"],
            "grow": 1,
            "shrink": 1,
            "min_main_px": 480,
            "min_cross_px": 400,
            "allocation_bounds": dict(nested_bounds),
        }],
    })
    item_b = next(component for component in plan["component_geometry_plan"]["components"] if component["id"] == "item_b")
    item_b["parent_id"] = "nested_flex"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested-flex.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(script), "--mode", "single-slide-image", "--archetype", "content-led composition", "--grid-mode", "nested Grid/Flex", "--layout-plan", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    return Result("nested_flex_layout_plan", proc.returncode == 0, proc.stdout + proc.stderr if proc.returncode else "")


def check_one_line_footer_layout_plan() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    plan = json.loads((ROOT / "build" / "evals" / "sample-layout-plan.json").read_text(encoding="utf-8"))
    configure_footer_present_body(plan)
    plan["source_plan"] = {"visibility": "visible", "reference_class": "external_publication", "publication_title": "Public Report", "locator": "https://example.com/report", "source_line": "Source: Public Report", "annotations": []}
    plan["content_atom_registry"]["atoms"].append({"id": "source", "exact_text": "Source: Public Report", "semantic_role": "footer", "component_id": "footer_master", "anchor_line": 1, "baseline_step": 895, "max_lines": 1, "expected_occurrences": 1})
    plan["model_fit_plan"]["visible_string_count"] += 1
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "one-line-footer.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(script), "--mode", "single-slide-image", "--archetype", "content-led composition", "--grid-mode", "hybrid Grid/Flex", "--layout-plan", str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    required = ['"baseline_y_by_line":[1096]', '"surface":"transparent_text_frame"', 'Source: Public Report']
    return Result("one_line_footer_layout_plan", proc.returncode == 0 and all(item in proc.stdout for item in required), proc.stdout + proc.stderr if proc.returncode else "missing one-line footer contract")


def check_design_token_swap() -> list[Result]:
    """Prove palette replacement changes color output while preserving geometry."""
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    plan = json.loads((ROOT / "build" / "evals" / "sample-layout-plan.json").read_text(encoding="utf-8"))
    tokens = json.loads((ROOT / "build" / "references" / "design-tokens.json").read_text(encoding="utf-8"))
    replacements = {
        "canvas": "#F7F9FC",
        "surface": "#EEF2F7",
        "structural_surface": "#DCE7F2",
        "focal_surface": "#FFF0C2",
    }
    tokens["name"] = "eval-alternate-palette"
    original_colors = tokens["colors"]
    renamed = {token_name: f"custom_{index}" for index, token_name in enumerate(original_colors)}
    tokens["colors"] = {renamed[token_name]: value for token_name, value in original_colors.items()}
    tokens["role_mapping"] = {role: renamed[token_name] for role, token_name in tokens["role_mapping"].items()}
    for original_name, value in replacements.items():
        tokens["colors"][renamed[original_name]] = value
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        token_path = tmp_path / "tokens.json"
        plan_path = tmp_path / "plan.json"
        token_path.write_text(json.dumps(tokens), encoding="utf-8")
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(script), "--mode", "single-slide-image", "--archetype", "content-led composition", "--grid-mode", "hybrid Grid/Flex", "--layout-plan", str(plan_path), "--design-tokens", str(token_path)],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        invalid = json.loads(json.dumps(tokens))
        invalid["role_mapping"].pop("slide_background")
        invalid_path = tmp_path / "invalid-tokens.json"
        invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
        invalid_proc = subprocess.run(
            [sys.executable, str(script), "--mode", "deck-plan", "--design-tokens", str(invalid_path)],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    output = proc.stdout
    return [
        Result("design_token_swap_executes", proc.returncode == 0, proc.stdout + proc.stderr if proc.returncode else ""),
        Result("design_token_swap_reaches_prompt", all(value in output for value in replacements.values()) and "eval-alternate-palette" in output, output[:1200]),
        Result("design_token_swap_preserves_geometry", "shell profile equity_story_master" in output and "one 28pt/700 line" in output and "one 20pt/400 line" in output, output[:1200]),
        Result("design_token_incomplete_schema_rejected", invalid_proc.returncode == 1 and "complete ACT color palette" in (invalid_proc.stdout + invalid_proc.stderr), invalid_proc.stdout + invalid_proc.stderr),
    ]


def check_compiled_prompt_budget_rejection() -> Result:
    script = ROOT / "build" / "scripts" / "build_act_slide_prompt.py"
    with tempfile.TemporaryDirectory() as tmp:
        brief_path = Path(tmp) / "oversized-brief.txt"
        brief_path.write_text("検証" * 1300, encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                str(brief_path),
                "--mode",
                "single-slide-image",
                "--archetype",
                "content-led composition",
                "--grid-mode",
                "hybrid Grid/Flex",
                "--layout-plan",
                "build/evals/sample-layout-plan.json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    output = proc.stdout + proc.stderr
    return Result(
        "compiled_prompt_budget_rejection",
        proc.returncode == 1 and "6144-byte budget" in output,
        output[:1200],
    )


def main() -> int:
    config = load_config()
    files = runtime_files(config["runtime_scan_globs"])
    content_files = [
        path
        for path in files
        if path.relative_to(ROOT).as_posix() != "build/scripts/eval_act_skill.py"
    ]
    results: list[Result] = []
    results.append(check_frontmatter())
    results.extend(check_no_old_files())
    results.extend(check_forbidden_patterns(config, content_files))
    results.extend(check_required_phrases(config, files))
    results.extend(check_geometry_arithmetic())
    results.append(check_script_syntax())
    results.extend(check_entrypoint_symlinks())
    results.extend(check_current_master_contract())
    runtime_guides = [ROOT / "SKILL.md", *sorted((ROOT / "build" / "references").glob("*.md"))]
    stale_header_vocabulary = [str(path.relative_to(ROOT)) for path in runtime_guides if "header_rule" in path.read_text(encoding="utf-8")]
    results.append(Result("header_furniture_runtime_vocabulary", not stale_header_vocabulary, ", ".join(stale_header_vocabulary)))
    visual_cases = json.loads((ROOT / "build" / "evals" / "visual-regression-cases.json").read_text(encoding="utf-8"))["cases"]
    results.append(Result("header_geometry_visual_regression_case", any(case.get("id") == "adversarial_self_generated_header_geometry" for case in visual_cases), "required header-geometry regression case is missing"))
    results.extend(check_layout_plan_geometry_rejections())
    results.append(check_footer_present_layout_plan())
    results.append(check_nested_flex_layout_plan())
    results.append(check_one_line_footer_layout_plan())
    results.extend(check_design_token_swap())
    results.append(check_compiled_prompt_budget_rejection())
    for check in config["helper_checks"]:
        results.append(run_helper_check(check))
    results.append(check_final_generation_prompt_hygiene())
    results.append(check_deck_plan_output_hygiene())
    results.append(check_visual_regression_cases())
    results.append(check_source_none_contract())
    results.append(run_pptx_package_check())
    results.append(run_pdf_package_check())

    failed = [r for r in results if not r.passed]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.name}")
        if result.detail and not result.passed:
            print(result.detail)
    print(f"\nsummary: {len(results) - len(failed)} passed / {len(results)} total")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
