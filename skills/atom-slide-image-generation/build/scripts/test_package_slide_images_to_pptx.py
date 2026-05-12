#!/usr/bin/env python3
"""Smoke tests for the image-only PPTX packager."""

from __future__ import annotations

import binascii
import importlib.util
import json
import struct
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path


SCRIPT = Path(__file__).with_name("package_slide_images_to_pptx.py")
SPEC = importlib.util.spec_from_file_location("pptx_packager", SCRIPT)
assert SPEC and SPEC.loader
pptx_packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pptx_packager)


def png_bytes(width: int = 2048, height: int = 1152) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)

    row = b"\x00" + (b"\xff\xff\xff" * width)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(row * height))
        + chunk(b"IEND", b"")
    )


def approved_manifest(image_paths: list[Path]) -> dict[str, object]:
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
                "png_path": str(path),
                "image_review_status": "approved",
                "final_image_quality_status": "approved",
                "blockers": [],
                "majors": [],
            }
            for idx, path in enumerate(image_paths, 1)
        ],
    }


class PackageSlideImagesToPptxTest(unittest.TestCase):
    def test_package_preserves_media_and_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            notes = root / "notes.json"
            manifest = root / "review.json"
            output = root / "deck.pptx"
            image.write_bytes(png_bytes())
            notes.write_text(json.dumps(["note 1"]), encoding="utf-8")
            manifest.write_text(json.dumps(approved_manifest([image])), encoding="utf-8")

            images = pptx_packager.collect_images([str(image)])
            slide_notes = pptx_packager.load_notes(str(notes), None, 1, images)
            pptx_packager.validate_review_manifest(str(manifest), images)
            pptx_packager.build_pptx(output, images, slide_notes)
            pptx_packager.validate_pptx(output, images, slide_notes)

            with zipfile.ZipFile(output) as archive:
                self.assertIn("ppt/media/image1.png", archive.namelist())
                notes_xml = archive.read("ppt/notesSlides/notesSlide1.xml").decode("utf-8")
                self.assertIn('type="sld"', notes_xml)
                self.assertIn("note 1", notes_xml)

    def test_requires_review_manifest_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            image.write_bytes(png_bytes())
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaises(SystemExit):
                pptx_packager.validate_review_manifest(None, images)

    def test_rejects_unapproved_review_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["completion_ready_status"] = "blocked"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaises(SystemExit):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_derived_png_input_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_image = root / "slides_package" / "slide01.png"
            render_image = root / "render_check" / "pdf_pages" / "page-01.png"
            package_image.parent.mkdir()
            render_image.parent.mkdir(parents=True)
            package_image.write_bytes(png_bytes())
            render_image.write_bytes(png_bytes())

            with self.assertRaises(SystemExit):
                pptx_packager.collect_images([str(package_image)])
            with self.assertRaises(SystemExit):
                pptx_packager.collect_images([str(render_image)])

    def test_rejects_non_slides_final_input_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "slide01.png"
            image.write_bytes(png_bytes())

            with self.assertRaises(SystemExit):
                pptx_packager.collect_images([str(image)])

    def test_rejects_traversal_out_of_slides_final(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "slides_final").mkdir()
            outside = root / "outside"
            outside.mkdir()
            image = outside / "slide01.png"
            image.write_bytes(png_bytes())
            traversal_path = root / "slides_final" / ".." / "outside" / "slide01.png"

            with self.assertRaises(SystemExit):
                pptx_packager.collect_images([str(traversal_path)])

    def test_rejects_non_slide_sized_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            image.write_bytes(png_bytes(1, 1))

            with self.assertRaises(SystemExit):
                pptx_packager.collect_images([str(image)])

    def test_rejects_legacy_manifest_path_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["slides"][0]["image_path"] = data["slides"][0].pop("png_path")
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaises(SystemExit):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_non_png_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.jpg"
            image.write_bytes(b"\xff\xd8\xff\xd9")

            with self.assertRaises(SystemExit):
                pptx_packager.collect_images([str(image)])


if __name__ == "__main__":
    unittest.main()
