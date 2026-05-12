#!/usr/bin/env python3
"""Package approved slide image masters into a PDF deck."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from package_slide_images_to_pptx import collect_images, validate_review_manifest


def build_pdf(output: Path, images: list[Path]) -> None:
    pages: list[Image.Image] = []
    try:
        for image_path in images:
            with Image.open(image_path) as image:
                pages.append(image.convert("RGB"))
        output.parent.mkdir(parents=True, exist_ok=True)
        first, *rest = pages
        first.save(output, "PDF", save_all=True, append_images=rest)
    finally:
        for page in pages:
            page.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package slides_final PNG masters into a PDF deck.")
    parser.add_argument("images", nargs="+", help="Approved slide image files or directories, preferably slides_final/.")
    parser.add_argument("--output", required=True, help="Output PDF path.")
    parser.add_argument("--review-manifest", required=True, help="Approved review manifest JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    images = collect_images(args.images)
    validate_review_manifest(args.review_manifest, images)
    output = Path(args.output).expanduser()
    build_pdf(output, images)
    if not output.exists() or output.stat().st_size <= 0:
        raise SystemExit(f"PDF was not created: {output}")
    print(f"pdf_package_status: created")
    print(f"pdf_output: {output}")
    print(f"pdf_slide_count: {len(images)}")
    print("pdf_image_mapping:")
    for idx, image in enumerate(images, 1):
        print(f"  {idx}: {image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
