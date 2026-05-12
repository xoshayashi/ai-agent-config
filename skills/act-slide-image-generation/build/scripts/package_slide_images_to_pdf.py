#!/usr/bin/env python3
"""Package approved slides_final PNG masters into a PDF deck."""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

from package_slide_images_to_pptx import collect_images, validate_review_manifest


def paeth_predictor(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def unfilter_scanlines(data: bytes, width: int, height: int, bytes_per_pixel: int) -> bytes:
    stride = width * bytes_per_pixel
    expected = height * (stride + 1)
    if len(data) != expected:
        raise SystemExit("PNG pixel data size does not match IHDR dimensions.")
    rows: list[bytes] = []
    previous = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = data[offset]
        offset += 1
        row = bytearray(data[offset : offset + stride])
        offset += stride
        for idx, value in enumerate(row):
            left = row[idx - bytes_per_pixel] if idx >= bytes_per_pixel else 0
            up = previous[idx]
            upper_left = previous[idx - bytes_per_pixel] if idx >= bytes_per_pixel else 0
            if filter_type == 1:
                row[idx] = (value + left) & 0xFF
            elif filter_type == 2:
                row[idx] = (value + up) & 0xFF
            elif filter_type == 3:
                row[idx] = (value + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                row[idx] = (value + paeth_predictor(left, up, upper_left)) & 0xFF
            elif filter_type != 0:
                raise SystemExit(f"Unsupported PNG filter type: {filter_type}")
        rows.append(bytes(row))
        previous = row
    return b"".join(rows)


def png_rgb_payload(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"{path} is not a PNG file.")
    offset = 8
    width = height = bit_depth = color_type = interlace = None
    idat_parts: list[bytes] = []
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        start = offset + 8
        end = start + length
        if end + 4 > len(data):
            raise SystemExit(f"{path} has a truncated PNG chunk.")
        payload = data[start:end]
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            idat_parts.append(payload)
        elif kind == b"IEND":
            break
        offset = end + 4
    if width is None or height is None or bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise SystemExit(f"{path} must be an 8-bit non-interlaced RGB/RGBA PNG.")
    bytes_per_pixel = 4 if color_type == 6 else 3
    raw = unfilter_scanlines(zlib.decompress(b"".join(idat_parts)), width, height, bytes_per_pixel)
    if color_type == 6:
        rgb = bytearray()
        for idx in range(0, len(raw), 4):
            rgb.extend(raw[idx : idx + 3])
        raw = bytes(rgb)
    return width, height, zlib.compress(raw)


def pdf_object(body: bytes) -> bytes:
    return body if body.endswith(b"\n") else body + b"\n"


def build_pdf(output: Path, images: list[Path]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payloads = [png_rgb_payload(image) for image in images]
    objects: list[bytes] = []
    page_object_ids: list[int] = []
    for width, height, compressed_rgb in payloads:
        image_id = len(objects) + 3
        content_id = image_id + 1
        page_id = image_id + 2
        objects.extend(
            [
                pdf_object(
                    f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
                    f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(compressed_rgb)} >>\n".encode()
                    + b"stream\n"
                    + compressed_rgb
                    + b"\nendstream"
                ),
                pdf_object(
                    f"<< /Length {len(f'q {width} 0 0 {height} 0 0 cm /Im1 Do Q'.encode())} >>\n".encode()
                    + b"stream\n"
                    + f"q {width} 0 0 {height} 0 0 cm /Im1 Do Q".encode()
                    + b"\nendstream"
                ),
                pdf_object(
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
                    f"/Resources << /XObject << /Im1 {image_id} 0 R >> >> /Contents {content_id} 0 R >>".encode()
                ),
            ]
        )
        page_object_ids.append(page_id)
    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects.insert(0, pdf_object(b"<< /Type /Catalog /Pages 2 0 R >>"))
    objects.insert(1, pdf_object(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>".encode()))
    content = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, body in enumerate(objects, 1):
        offsets.append(len(content))
        content.extend(f"{obj_id} 0 obj\n".encode())
        content.extend(body)
        content.extend(b"endobj\n")
    xref = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode())
    content.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    output.write_bytes(content)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package slides_final PNG masters into a PDF deck.")
    parser.add_argument("images", nargs="+", help="Approved slides_final PNG files or directories.")
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
    if not output.read_bytes().startswith(b"%PDF"):
        raise SystemExit(f"PDF output is malformed: {output}")
    print("pdf_package_status: created")
    print(f"pdf_output_path: {output}")
    print(f"pdf_slide_count: {len(images)}")
    print("pdf_image_mapping:")
    for idx, image in enumerate(images, 1):
        print(f"  {idx}: {image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
