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


def png_bytes() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
        + chunk(b"IEND", b"")
    )


class PackageSlideImagesToPptxTest(unittest.TestCase):
    def test_package_preserves_media_and_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "slide01.png"
            notes = root / "notes.json"
            output = root / "deck.pptx"
            image.write_bytes(png_bytes())
            notes.write_text(json.dumps(["note 1"]), encoding="utf-8")

            images = pptx_packager.collect_images([str(image)])
            slide_notes = pptx_packager.load_notes(str(notes), None, 1, images)
            pptx_packager.build_pptx(output, images, slide_notes)
            pptx_packager.validate_pptx(output, images, slide_notes)

            with zipfile.ZipFile(output) as archive:
                self.assertIn("ppt/media/image1.png", archive.namelist())
                self.assertIn("note 1", archive.read("ppt/notesSlides/notesSlide1.xml").decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
