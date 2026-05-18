#!/usr/bin/env python3
"""Evaluate the ACT slide image skill for self-contained behavior."""

from __future__ import annotations

import ast
import fnmatch
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


@dataclass
class Result:
    name: str
    passed: bool
    detail: str = ""


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


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
    start = combined.find("final_generation_prompt_payload:")
    end = combined.find("\n\nnon_rendered_workflow_qa:", start)
    if start < 0 or end < 0:
        return Result("final_generation_prompt_hygiene", False, "missing final_generation_prompt_payload boundary")
    payload = combined[start:end]
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
    if "image_size 2048x1152" not in payload:
        return Result("final_generation_prompt_hygiene", False, "default 2048x1152 image size missing from generation prompt payload")
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
    block = slice_named_block(combined, "deck_plan_output:", "\n\ntext_to_slide_structure_output:")
    if not block:
        return Result("deck_plan_output_hygiene", False, "missing deck_plan_output block")
    required = [
        "deck_tone_signature_lock",
        "header_identity_lock",
        "header_integrity_blocker_lock",
        "message_box_compactness_blocker_lock",
        "package_delivery",
        "pdf_delivery",
        "pdf_status",
        "pdf_output_path",
        "pdf_slide_count",
        "package_image_mapping",
        "pdf_image_mapping",
    ]
    missing = [needle for needle in required if needle not in block]
    if missing:
        return Result("deck_plan_output_hygiene", False, "missing deck-plan terms: " + ", ".join(missing))
    return Result("deck_plan_output_hygiene", True)


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
    approved_design_statuses = {
        "deck_tone_consistency_status": "approved",
        "illustration_consistency_status": "approved",
        "post_generation_design_balance_status": "approved",
        "whitespace_occupancy_balance_status": "approved",
        "density_balance_status": "approved",
        "typography_balance_status": "approved",
        "color_consistency_status": "approved",
        "outer_padding_consistency_status": "approved",
        "header_integrity_status": "approved",
        "multimodal_design_review_status": "approved",
        "design_balance_gate_status": "approved",
        "occupancy_density_fit_status": "approved",
        "font_scale_unity_status": "approved",
        "palette_role_unity_status": "approved",
        "design_breakage_blocker_status": "approved",
    }
    return {
        "all_generated_images_reviewed": True,
        "weak_slide_regeneration_queue": [],
        "final_image_quality_status": "approved",
        "content_quality_status": "approved",
        "design_quality_status": "approved",
        "deck_unity_status": "approved",
        "completion_ready_status": "approved",
        "review_manifest_status": "approved",
        **approved_design_statuses,
        "slides": [
            {
                "slide_id": str(idx),
                "png_path": str(image),
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
    results.append(check_script_syntax())
    results.extend(check_entrypoint_symlinks())
    for check in config["helper_checks"]:
        results.append(run_helper_check(check))
    results.append(check_final_generation_prompt_hygiene())
    results.append(check_deck_plan_output_hygiene())
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
