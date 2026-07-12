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
        "fixed_zone_grid_status": "approved",
        "header_zone_boundary_status": "approved",
        "content_area_padding_consistency_status": "approved",
        "header_integrity_status": "approved",
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
                "png_path": str(path),
                "image_review_status": "approved",
                "final_image_quality_status": "approved",
                "content_quality_status": "approved",
                "design_quality_status": "approved",
                **approved_design_statuses,
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
            slide_notes = pptx_packager.load_notes(notes_json=str(notes), notes_file=None, slide_count=1, images=images)
            pptx_packager.validate_review_manifest(str(manifest), images)
            pptx_packager.build_pptx(output, images, slide_notes)
            pptx_packager.validate_pptx(output, images, slide_notes)

            with zipfile.ZipFile(output) as archive:
                self.assertIn("ppt/media/image1.png", archive.namelist())
                notes_xml = archive.read("ppt/notesSlides/notesSlide1.xml").decode("utf-8")
                self.assertIn('type="sld"', notes_xml)
                self.assertIn("note 1", notes_xml)
                theme_xml = archive.read("ppt/theme/theme1.xml").decode("utf-8")
                self.assertIn('<a:dk2><a:srgbClr val="626A64"/></a:dk2>', theme_xml)

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

    def test_rejects_missing_design_balance_manifest_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            del data["post_generation_design_balance_status"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "missing required key: post_generation_design_balance_status"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_missing_deck_only_design_manifest_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            del data["deck_tone_consistency_status"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "missing required key: deck_tone_consistency_status"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_unapproved_slide_multimodal_design_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["slides"][0]["multimodal_design_review_status"] = "repair_required"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "slide 1 multimodal_design_review_status must be approved"):
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

    def test_rejects_non_2k_slide_master_sizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            legacy_basis = slides_dir / "slide_basis.png"
            fhd = slides_dir / "slide_fhd.png"
            legacy_basis.write_bytes(png_bytes(1672, 941))
            fhd.write_bytes(png_bytes(1920, 1080))

            with self.assertRaisesRegex(SystemExit, "generate a new 2048x1152 slides_final/ master"):
                pptx_packager.collect_images([str(legacy_basis)])
            with self.assertRaisesRegex(SystemExit, "instead of converting or locally redrawing"):
                pptx_packager.collect_images([str(fhd)])

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

    def test_rejects_duplicate_image_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            image.write_bytes(png_bytes())

            with self.assertRaisesRegex(SystemExit, "Duplicate slide image input"):
                pptx_packager.collect_images([str(image), str(image)])

    def test_rejects_duplicate_manifest_png_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image, image])
            manifest.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "Duplicate png_path"):
                pptx_packager.validate_review_manifest(str(manifest), [image, image])

    def test_rejects_missing_review_manifest_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            del data["schema_version"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "schema_version must be 1"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_wrong_review_manifest_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["schema_version"] = 2
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "schema_version must be 1"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_unknown_review_manifest_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["legacy_image_path"] = str(image)
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "review_manifest unknown key"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_unknown_review_manifest_slide_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["slides"][0]["legacy_image_path"] = str(image)
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "slide 1 unknown key"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_missing_review_manifest_slide_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            del data["slides"][0]["blockers"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "slide 1 missing required key: blockers"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_out_of_order_review_manifest_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image1 = slides_dir / "slide01.png"
            image2 = slides_dir / "slide02.png"
            manifest = root / "review.json"
            image1.write_bytes(png_bytes())
            image2.write_bytes(png_bytes())
            data = approved_manifest([image2, image1])
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image1), str(image2)])

            with self.assertRaisesRegex(SystemExit, "slide 1 png_path must match image input order"):
                pptx_packager.validate_review_manifest(str(manifest), images)

    def test_rejects_nonsequential_review_manifest_slide_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides_dir = root / "slides_final"
            slides_dir.mkdir()
            image = slides_dir / "slide01.png"
            manifest = root / "review.json"
            image.write_bytes(png_bytes())
            data = approved_manifest([image])
            data["slides"][0]["slide_id"] = "slide-1"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            images = pptx_packager.collect_images([str(image)])

            with self.assertRaisesRegex(SystemExit, "slide 1 slide_id must be 1"):
                pptx_packager.validate_review_manifest(str(manifest), images)


if __name__ == "__main__":
    unittest.main()
