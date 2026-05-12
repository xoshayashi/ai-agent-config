#!/usr/bin/env python3
"""Package generated slide images into an image-only 16:9 PPTX deck."""

from __future__ import annotations

import argparse
import binascii
import json
import posixpath
import re
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape


SLIDE_CX = 12_192_000
SLIDE_CY = 6_858_000
NOTES_CX = 6_858_000
NOTES_CY = 9_144_000
IMAGE_EXTENSIONS = {".png"}
APPROVED_SLIDE_IMAGE_SIZES = {
    (1536, 864),
    (1920, 1080),
    (2048, 1152),
    (2560, 1440),
    (3840, 2160),
}
CONTENT_TYPES = {
    ".png": "image/png",
}
P_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
O_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def validate_png_bytes(data: bytes, label: str) -> tuple[int, int]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"{label} is not a valid PNG: missing PNG signature")
    offset = 8
    seen_ihdr = False
    seen_iend = False
    dimensions: tuple[int, int] | None = None
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        start = offset + 8
        end = start + length
        crc_end = end + 4
        if crc_end > len(data):
            raise SystemExit(f"{label} is not a valid PNG: truncated {kind.decode('latin1', errors='replace')} chunk")
        expected_crc = struct.unpack(">I", data[end:crc_end])[0]
        actual_crc = binascii.crc32(kind + data[start:end]) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise SystemExit(f"{label} is not a valid PNG: CRC mismatch in {kind.decode('latin1', errors='replace')}")
        if kind == b"IHDR":
            seen_ihdr = True
            width, height = struct.unpack(">II", data[start : start + 8])
            dimensions = (width, height)
        if kind == b"IEND":
            seen_iend = True
            if crc_end != len(data):
                raise SystemExit(f"{label} is not a valid PNG: trailing bytes after IEND")
            break
        offset = crc_end
    if not seen_ihdr or not seen_iend:
        raise SystemExit(f"{label} is not a valid PNG: missing IHDR or IEND")
    if dimensions is None:
        raise SystemExit(f"{label} is not a valid PNG: missing dimensions")
    return dimensions


def validate_image_bytes(data: bytes, suffix: str, label: str) -> tuple[int, int]:
    ext = suffix.lower()
    if ext == ".png":
        return validate_png_bytes(data, label)
    else:
        raise SystemExit(f"{label} has unsupported image extension: {suffix}; use PNG slide masters only")


def validate_image_file(path: Path) -> None:
    width, height = validate_image_bytes(path.read_bytes(), path.suffix, str(path))
    if (width, height) not in APPROVED_SLIDE_IMAGE_SIZES:
        allowed = ", ".join(f"{w}x{h}" for w, h in sorted(APPROVED_SLIDE_IMAGE_SIZES))
        raise SystemExit(f"{path} must be an approved 16:9 slide image size; found {width}x{height}. Allowed: {allowed}.")


def validate_master_image_path(path: Path) -> None:
    parts = tuple(part.lower() for part in path.parts)
    if "slides_package" in parts:
        raise SystemExit(f"{path} is under slides_package/. Use the approved slides_final/ PNG master instead.")
    for idx, part in enumerate(parts[:-1]):
        if part == "render_check" and parts[idx + 1] == "pdf_pages":
            raise SystemExit(f"{path} is under render_check/pdf_pages/. Use the approved slides_final/ PNG master instead.")
    if "slides_final" not in parts:
        raise SystemExit(f"{path} is not under slides_final/. Use the approved slides_final/ PNG master instead.")


def natural_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.name.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def collect_images(inputs: Iterable[str]) -> list[Path]:
    images: list[Path] = []
    for item in inputs:
        path = Path(item).expanduser()
        if path.is_dir():
            images.extend(sorted((p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS), key=natural_key))
        elif path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(path)
        else:
            raise SystemExit(f"Unsupported image input: {item}")
    if not images:
        raise SystemExit("No PNG slide images were provided.")
    for image in images:
        validate_master_image_path(image)
        validate_image_file(image)
    return images


def load_notes(
    notes_json: str | None,
    notes_file: str | None,
    slide_count: int,
    images: list[Path],
    require_notes: bool = True,
) -> list[str]:
    notes = [""] * slide_count
    if require_notes and not notes_file and not notes_json:
        raise SystemExit("Speaker notes are required by default. Provide --notes-json/--notes-file or pass --no-require-notes.")
    if notes_file:
        raw = Path(notes_file).expanduser().read_text(encoding="utf-8")
        chunks = [chunk.strip() for chunk in re.split(r"\n---SLIDE---\n|\f", raw)]
        if require_notes and len(chunks) != slide_count:
            raise SystemExit(f"--notes-file must contain exactly {slide_count} note chunks; found {len(chunks)}.")
        for idx, chunk in enumerate(chunks[:slide_count]):
            notes[idx] = chunk
    if notes_json:
        data = json.loads(Path(notes_json).expanduser().read_text(encoding="utf-8"))
        if isinstance(data, list):
            if require_notes and len(data) != slide_count:
                raise SystemExit(f"--notes-json list must contain exactly {slide_count} notes; found {len(data)}.")
            for idx, value in enumerate(data[:slide_count]):
                notes[idx] = str(value or "")
        elif isinstance(data, dict):
            missing: list[str] = []
            for idx, image in enumerate(images):
                candidates = [str(idx + 1), image.name, image.stem]
                for key in candidates:
                    if key in data:
                        notes[idx] = str(data[key] or "")
                        break
                else:
                    missing.append(f"{idx + 1}:{image.name}")
            if require_notes and missing:
                raise SystemExit("--notes-json object is missing notes for: " + ", ".join(missing))
        else:
            raise SystemExit("--notes-json must contain a list or object.")
    if require_notes:
        empty = [str(idx + 1) for idx, note in enumerate(notes) if not note.strip()]
        if empty:
            raise SystemExit("Speaker notes are blank for slide(s): " + ", ".join(empty))
    return notes


APPROVED_STATUSES = {
    "final_image_quality_status",
    "content_quality_status",
    "design_quality_status",
    "deck_unity_status",
    "completion_ready_status",
    "review_manifest_status",
}


def normalize_manifest_path(value: object, base: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def require_approved_status(data: dict[str, object], key: str) -> None:
    if data.get(key) != "approved":
        raise SystemExit(f"review_manifest {key} must be approved.")


def validate_review_manifest(manifest_file: str | None, images: list[Path]) -> None:
    if not manifest_file:
        raise SystemExit("PPTX package gate requires an approved review manifest. Provide --review-manifest.")

    manifest_path = Path(manifest_file).expanduser()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("review_manifest must be a JSON object.")

    if data.get("all_generated_images_reviewed") is not True:
        raise SystemExit("review_manifest all_generated_images_reviewed must be true.")

    queue = data.get("weak_slide_regeneration_queue")
    if queue not in (None, [], {}):
        raise SystemExit("review_manifest weak_slide_regeneration_queue must be empty.")

    for key in APPROVED_STATUSES:
        require_approved_status(data, key)

    slides = data.get("slides")
    if not isinstance(slides, list):
        raise SystemExit("review_manifest slides must be a list.")
    if len(slides) != len(images):
        raise SystemExit(f"review_manifest slide count {len(slides)} does not match image count {len(images)}.")

    expected_paths = {image.resolve() for image in images}
    manifest_paths: set[Path] = set()
    base = manifest_path.parent
    for idx, slide in enumerate(slides, 1):
        if not isinstance(slide, dict):
            raise SystemExit(f"review_manifest slide {idx} must be an object.")
        for key in ("image_review_status", "final_image_quality_status"):
            if slide.get(key) != "approved":
                raise SystemExit(f"review_manifest slide {idx} {key} must be approved.")
        for key in ("blockers", "majors"):
            findings = slide.get(key)
            if findings not in (None, [], {}):
                raise SystemExit(f"review_manifest slide {idx} has non-empty {key}.")
        path = normalize_manifest_path(slide.get("png_path"), base)
        if path is None:
            raise SystemExit(f"review_manifest slide {idx} is missing png_path.")
        manifest_paths.add(path)

    if manifest_paths != expected_paths:
        missing = sorted(str(path) for path in expected_paths - manifest_paths)
        extra = sorted(str(path) for path in manifest_paths - expected_paths)
        detail = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if extra:
            detail.append("extra: " + ", ".join(extra))
        raise SystemExit("review_manifest image paths must match package images; " + "; ".join(detail))


def rels_xml(relationships: list[tuple[str, str, str]]) -> str:
    items = "\n".join(
        f'  <Relationship Id="{rid}" Type="{escape(kind)}" Target="{escape(target)}"/>'
        for rid, kind, target in relationships
    )
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="{P_REL}">\n{items}\n</Relationships>'


def content_types_xml(images: list[Path]) -> str:
    defaults = [
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
    ]
    for ext in sorted({path.suffix.lower().lstrip(".") for path in images}):
        defaults.append(f'<Default Extension="{ext}" ContentType="{CONTENT_TYPES["." + ext]}"/>')
    overrides = [
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"/>',
    ]
    for idx in range(1, len(images) + 1):
        overrides.append(f'<Override PartName="/ppt/slides/slide{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        overrides.append(f'<Override PartName="/ppt/notesSlides/notesSlide{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>')
    body = "\n  ".join(defaults + overrides)
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n  {body}\n</Types>'


def presentation_xml(slide_count: int) -> str:
    slide_ids = "\n".join(
        f'    <p:sldId id="{255 + idx}" r:id="rId{idx + 2}"/>' for idx in range(1, slide_count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{O_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst>
  <p:sldIdLst>
{slide_ids}
  </p:sldIdLst>
  <p:sldSz cx="{SLIDE_CX}" cy="{SLIDE_CY}" type="wide"/>
  <p:notesSz cx="{NOTES_CX}" cy="{NOTES_CY}"/>
  <p:defaultTextStyle><a:defPPr><a:defRPr lang="ja-JP"/></a:defPPr></p:defaultTextStyle>
</p:presentation>'''


def presentation_rels_xml(slide_count: int) -> str:
    rels = [
        ("rId1", f"{O_REL}/slideMaster", "slideMasters/slideMaster1.xml"),
        ("rId2", f"{O_REL}/notesMaster", "notesMasters/notesMaster1.xml"),
    ]
    rels.extend((f"rId{idx + 2}", f"{O_REL}/slide", f"slides/slide{idx}.xml") for idx in range(1, slide_count + 1))
    return rels_xml(rels)


def slide_xml(idx: int) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{O_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_CX}" cy="{SLIDE_CY}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_CX}" cy="{SLIDE_CY}"/></a:xfrm></p:grpSpPr>
      <p:pic>
        <p:nvPicPr><p:cNvPr id="2" name="Generated slide image {idx}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
        <p:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
        <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_CX}" cy="{SLIDE_CY}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      </p:pic>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def slide_rels_xml(idx: int, image_name: str) -> str:
    return rels_xml(
        [
            ("rId1", f"{O_REL}/image", f"../media/{image_name}"),
            ("rId2", f"{O_REL}/slideLayout", "../slideLayouts/slideLayout1.xml"),
            ("rId3", f"{O_REL}/notesSlide", f"../notesSlides/notesSlide{idx}.xml"),
        ]
    )


def paragraphs(text: str) -> str:
    lines = text.splitlines() or [""]
    return "\n".join(
        f'<a:p><a:r><a:rPr lang="ja-JP" sz="1200"/><a:t>{escape(line)}</a:t></a:r><a:endParaRPr lang="ja-JP" sz="1200"/></a:p>'
        for line in lines
    )


def notes_slide_xml(idx: int, note: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{O_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{NOTES_CX}" cy="{NOTES_CY}"/><a:chOff x="0" y="0"/><a:chExt cx="{NOTES_CX}" cy="{NOTES_CY}"/></a:xfrm></p:grpSpPr>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Slide image placeholder {idx}"/><p:cNvSpPr/><p:nvPr><p:ph type="sld"/></p:nvPr></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="685800" y="457200"/><a:ext cx="5486400" cy="3086100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Speaker notes {idx}"/><p:cNvSpPr/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="685800" y="4572000"/><a:ext cx="5486400" cy="3657600"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
        <p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs(note)}</p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:notes>'''


def notes_slide_rels_xml(idx: int) -> str:
    return rels_xml(
        [
            ("rId1", f"{O_REL}/slide", f"../slides/slide{idx}.xml"),
            ("rId2", f"{O_REL}/notesMaster", "../notesMasters/notesMaster1.xml"),
        ]
    )


def slide_master_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{O_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_CX}" cy="{SLIDE_CY}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_CX}" cy="{SLIDE_CY}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>'''


def slide_layout_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{O_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_CX}" cy="{SLIDE_CY}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_CX}" cy="{SLIDE_CY}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''


def notes_master_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notesMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{O_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{NOTES_CX}" cy="{NOTES_CY}"/><a:chOff x="0" y="0"/><a:chExt cx="{NOTES_CX}" cy="{NOTES_CY}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:notesStyle/><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:notesMaster>'''


def theme_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="ImageOnly">
  <a:themeElements>
    <a:clrScheme name="ImageOnly"><a:dk1><a:srgbClr val="2D332E"/></a:dk1><a:lt1><a:srgbClr val="FCFBF8"/></a:lt1><a:dk2><a:srgbClr val="4D544E"/></a:dk2><a:lt2><a:srgbClr val="F7FBF9"/></a:lt2><a:accent1><a:srgbClr val="0B2F5B"/></a:accent1><a:accent2><a:srgbClr val="C49A2C"/></a:accent2><a:accent3><a:srgbClr val="D6E1EE"/></a:accent3><a:accent4><a:srgbClr val="6E756E"/></a:accent4><a:accent5><a:srgbClr val="071F3D"/></a:accent5><a:accent6><a:srgbClr val="F7EECF"/></a:accent6><a:hlink><a:srgbClr val="0B2F5B"/></a:hlink><a:folHlink><a:srgbClr val="071F3D"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="ImageOnly"><a:majorFont><a:latin typeface="Noto Sans JP"/><a:ea typeface="Noto Sans JP"/></a:majorFont><a:minorFont><a:latin typeface="Noto Sans JP"/><a:ea typeface="Noto Sans JP"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="ImageOnly"><a:fillStyleLst><a:solidFill><a:schemeClr val="lt1"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="dk1"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="lt1"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>'''


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Image-only slide deck</dc:title>
  <dc:creator>slide image generation skill</dc:creator>
  <cp:lastModifiedBy>slide image generation skill</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''


def app_xml(slide_count: int) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>slide image generation skill</Application>
  <PresentationFormat>Widescreen</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Notes>{slide_count}</Notes>
</Properties>'''


def build_pptx(output: Path, images: list[Path], notes: list[str]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(images))
        archive.writestr("_rels/.rels", rels_xml([("rId1", f"{O_REL}/officeDocument", "ppt/presentation.xml")]))
        archive.writestr("docProps/core.xml", core_xml())
        archive.writestr("docProps/app.xml", app_xml(len(images)))
        archive.writestr("ppt/presentation.xml", presentation_xml(len(images)))
        archive.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml(len(images)))
        archive.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        archive.writestr(
            "ppt/slideMasters/_rels/slideMaster1.xml.rels",
            rels_xml(
                [
                    ("rId1", f"{O_REL}/slideLayout", "../slideLayouts/slideLayout1.xml"),
                    ("rId2", f"{O_REL}/theme", "../theme/theme1.xml"),
                ]
            ),
        )
        archive.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        archive.writestr(
            "ppt/slideLayouts/_rels/slideLayout1.xml.rels",
            rels_xml([("rId1", f"{O_REL}/slideMaster", "../slideMasters/slideMaster1.xml")]),
        )
        archive.writestr("ppt/notesMasters/notesMaster1.xml", notes_master_xml())
        archive.writestr(
            "ppt/notesMasters/_rels/notesMaster1.xml.rels",
            rels_xml([("rId1", f"{O_REL}/theme", "../theme/theme1.xml")]),
        )
        archive.writestr("ppt/theme/theme1.xml", theme_xml())
        for idx, image in enumerate(images, 1):
            media_name = f"image{idx}{image.suffix.lower()}"
            archive.write(image, f"ppt/media/{media_name}")
            archive.writestr(f"ppt/slides/slide{idx}.xml", slide_xml(idx))
            archive.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rels_xml(idx, media_name))
            archive.writestr(f"ppt/notesSlides/notesSlide{idx}.xml", notes_slide_xml(idx, notes[idx - 1]))
            archive.writestr(f"ppt/notesSlides/_rels/notesSlide{idx}.xml.rels", notes_slide_rels_xml(idx))


def resolve_relationship_target(rels_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    if rels_part == "_rels/.rels":
        base = ""
    elif "/_rels/" in rels_part and rels_part.endswith(".rels"):
        folder, rel_name = rels_part.rsplit("/_rels/", 1)
        source_part = posixpath.join(folder, rel_name[:-5])
        base = posixpath.dirname(source_part)
    else:
        base = posixpath.dirname(rels_part)
    return posixpath.normpath(posixpath.join(base, target))


def ensure_content_types(archive: zipfile.ZipFile, names: set[str]) -> None:
    root = ET.fromstring(archive.read("[Content_Types].xml"))
    defaults = {
        item.attrib["Extension"].lower(): item.attrib["ContentType"]
        for item in root.findall(f"{{{CT_NS}}}Default")
    }
    overrides = {
        item.attrib["PartName"].lstrip("/"): item.attrib["ContentType"]
        for item in root.findall(f"{{{CT_NS}}}Override")
    }
    for name in names:
        suffix = Path(name).suffix.lower().lstrip(".")
        if not suffix:
            continue
        if name.endswith(".rels") and "rels" not in defaults:
            raise SystemExit("[Content_Types].xml is missing the .rels default.")
        if name.endswith(".xml") and name not in overrides and "xml" not in defaults:
            raise SystemExit(f"[Content_Types].xml is missing an XML type for {name}.")
        if name.startswith("ppt/media/") and suffix not in defaults:
            raise SystemExit(f"[Content_Types].xml is missing media default for .{suffix}.")


def ensure_relationship_targets(archive: zipfile.ZipFile, names: set[str]) -> None:
    for rels_part in sorted(name for name in names if name.endswith(".rels")):
        root = ET.fromstring(archive.read(rels_part))
        for relationship in root.findall(f"{{{P_REL}}}Relationship"):
            if relationship.attrib.get("TargetMode") == "External":
                continue
            target = relationship.attrib.get("Target", "")
            resolved = resolve_relationship_target(rels_part, target)
            if resolved not in names:
                raise SystemExit(f"{rels_part} points to missing package part: {target} -> {resolved}")


def ensure_notes_text(archive: zipfile.ZipFile, notes: list[str]) -> None:
    for idx, expected in enumerate(notes, 1):
        if not expected.strip():
            continue
        root = ET.fromstring(archive.read(f"ppt/notesSlides/notesSlide{idx}.xml"))
        actual = "\n".join(node.text or "" for node in root.findall(f".//{{{A_NS}}}t"))
        missing = [line for line in expected.splitlines() if line.strip() and line.strip() not in actual]
        if missing:
            raise SystemExit(f"Speaker notes text was not preserved for slide {idx}: {missing[0]}")


def image_mapping(images: list[Path]) -> dict[str, dict[str, str]]:
    return {
        str(idx): {
            "png_path": str(image),
            "slide_part": f"ppt/slides/slide{idx}.xml",
            "media_part": f"ppt/media/image{idx}{image.suffix.lower()}",
        }
        for idx, image in enumerate(images, 1)
    }


def notes_mapping(notes: list[str]) -> dict[str, dict[str, object]]:
    return {
        str(idx): {
            "notes_part": f"ppt/notesSlides/notesSlide{idx}.xml",
            "chars": len(note),
            "preview": note.replace("\n", " ")[:100],
        }
        for idx, note in enumerate(notes, 1)
    }


def validate_pptx(output: Path, images: list[Path], notes: list[str]) -> None:
    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        required = {"ppt/presentation.xml", "[Content_Types].xml"}
        required.update(f"ppt/slides/slide{idx}.xml" for idx in range(1, len(images) + 1))
        required.update(f"ppt/media/image{idx}{image.suffix.lower()}" for idx, image in enumerate(images, 1))
        required.update(f"ppt/notesSlides/notesSlide{idx}.xml" for idx in range(1, len(images) + 1))
        required.update(f"ppt/slides/_rels/slide{idx}.xml.rels" for idx in range(1, len(images) + 1))
        required.update(f"ppt/notesSlides/_rels/notesSlide{idx}.xml.rels" for idx in range(1, len(images) + 1))
        missing = required - names
        if missing:
            raise SystemExit(f"PPTX package is missing expected entries: {', '.join(sorted(missing))}")
        for name in sorted(names):
            if name.endswith(".xml") or name.endswith(".rels"):
                ET.fromstring(archive.read(name))
            if name.startswith("ppt/media/"):
                validate_image_bytes(archive.read(name), Path(name).suffix, name)
        ensure_content_types(archive, names)
        ensure_relationship_targets(archive, names)
        ensure_notes_text(archive, notes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", help="PNG slide images or directories containing slide images")
    parser.add_argument("--output", required=True, help="Output .pptx path")
    parser.add_argument("--notes-json", help="Optional JSON list/object with speaker notes")
    parser.add_argument("--notes-file", help="Optional text file split by form-feed or ---SLIDE---")
    parser.add_argument("--no-require-notes", action="store_true", help="Allow PPTX packaging without speaker notes")
    parser.add_argument("--review-manifest", help="Approved post-generation review manifest JSON")
    args = parser.parse_args()

    images = collect_images(args.images)
    output = Path(args.output).expanduser()
    notes = load_notes(args.notes_json, args.notes_file, len(images), images, require_notes=not args.no_require_notes)
    validate_review_manifest(args.review_manifest, images)
    build_pptx(output, images, notes)
    validate_pptx(output, images, notes)
    print(f"pptx_output_path: {output}")
    print(f"pptx_slide_count: {len(images)}")
    print("pptx_image_mapping: " + json.dumps(image_mapping(images), ensure_ascii=False, sort_keys=True))
    print("pptx_speaker_notes_mapping: " + json.dumps(notes_mapping(notes), ensure_ascii=False, sort_keys=True))
    print("review_manifest_status: approved")
    print("pptx_package_status: created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
