#!/usr/bin/env python3
"""Evaluate the ATOM slide image skill for self-contained behavior."""

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


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "evals" / "atom_skill_eval.json"


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
    if name.group(1) != "atom-slide-image-generation":
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


def check_required_phrases(config: dict) -> list[Result]:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    results: list[Result] = []
    for phrase in config["required_skill_phrases"]:
        results.append(Result(f"required:{phrase}", phrase in text, "missing" if phrase not in text else ""))
    return results


def check_script_syntax() -> Result:
    for script in sorted((ROOT / "scripts").glob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            return Result("script_syntax", False, f"{script.relative_to(ROOT)}: {exc}")
    return Result("script_syntax", True)


def run_helper_check(check: dict) -> Result:
    script = ROOT / "scripts" / "build_atom_slide_prompt.py"
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


def valid_png_bytes(rgb: tuple[int, int, int] = (255, 255, 255)) -> bytes:
    import binascii
    import struct
    import zlib

    def chunk(kind: bytes, data: bytes) -> bytes:
        crc = binascii.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)

    raw_scanline = b"\x00" + bytes(rgb)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw_scanline))
        + chunk(b"IEND", b"")
    )


def approved_review_manifest(images: list[Path]) -> dict[str, object]:
    return {
        "all_generated_images_reviewed": True,
        "weak_slide_regeneration_queue": [],
        "final_image_quality_status": "approved",
        "content_quality_status": "approved",
        "design_quality_status": "approved",
        "deck_unity_status": "approved",
        "completion_ready_status": "approved",
        "review_manifest_status": "approved",
        "slides": [
            {
                "slide_id": str(idx),
                "png_path": str(image),
                "image_review_status": "approved",
                "final_image_quality_status": "approved",
                "blockers": [],
                "majors": [],
            }
            for idx, image in enumerate(images, 1)
        ],
    }


def run_pptx_package_check() -> Result:
    script = ROOT / "scripts" / "package_slide_images_to_pptx.py"
    png_bytes = valid_png_bytes()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        image1 = tmp_path / "slide01.png"
        image2 = tmp_path / "slide02.png"
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


def check_no_old_files() -> list[Result]:
    old_paths = [
        ROOT / "references" / "act-slide-patterns-essentials.md",
        ROOT / "scripts" / "build_act_slide_prompt.py",
    ]
    results = [Result(f"old_file_absent:{path.relative_to(ROOT)}", not path.exists(), "exists" if path.exists() else "") for path in old_paths]
    pycache_dirs = [p.relative_to(ROOT) for p in ROOT.rglob("__pycache__") if p.is_dir()]
    results.append(Result("no_pycache_dirs", not pycache_dirs, ", ".join(str(p) for p in pycache_dirs)))
    return results


def main() -> int:
    config = load_config()
    files = runtime_files(config["runtime_scan_globs"])
    content_files = [path for path in files if path.relative_to(ROOT).as_posix() != "scripts/eval_atom_skill.py"]
    results: list[Result] = []
    results.append(check_frontmatter())
    results.extend(check_no_old_files())
    results.extend(check_forbidden_patterns(config, content_files))
    results.extend(check_required_phrases(config))
    results.append(check_script_syntax())
    for check in config["helper_checks"]:
        results.append(run_helper_check(check))
    results.append(run_pptx_package_check())

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
