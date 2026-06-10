#!/usr/bin/env python3
"""Validate PPTX package structure, XML, relationships, media, and slide count."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
CT_NS = {"ct": "http://schemas.openxmlformats.org/package/2006/content-types"}
P_NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
NOTES_RE = re.compile(r"^ppt/notesSlides/notesSlide(\d+)\.xml$")


def normalize_rel_target(base_file: str, target: str) -> str | None:
    if not target or target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:"):
        return None
    base_dir = posixpath.dirname(base_file)
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(base_dir, target))


def parse_xml(zf: zipfile.ZipFile, name: str, errors: list[str]) -> ET.Element | None:
    try:
        return ET.fromstring(zf.read(name))
    except ET.ParseError as exc:
        errors.append(f"XML parse error in {name}: {exc}")
    except KeyError:
        errors.append(f"Missing XML part: {name}")
    return None


def count_slide_rels(zf: zipfile.ZipFile, errors: list[str]) -> int:
    root = parse_xml(zf, "ppt/_rels/presentation.xml.rels", errors)
    if root is None:
        return 0
    count = 0
    for rel in root.findall("rel:Relationship", REL_NS):
        target = rel.get("Target", "")
        rel_type = rel.get("Type", "")
        if target.startswith("slides/") or rel_type.endswith("/slide"):
            count += 1
    return count


def content_type_overrides(zf: zipfile.ZipFile, errors: list[str]) -> list[str]:
    root = parse_xml(zf, "[Content_Types].xml", errors)
    if root is None:
        return []
    overrides = []
    for override in root.findall("ct:Override", CT_NS):
        part = override.get("PartName")
        if part:
            overrides.append(part.lstrip("/"))
    return overrides


def validate_relationship_targets(zf: zipfile.ZipFile, warnings: list[str], errors: list[str]) -> None:
    names = set(zf.namelist())
    for rels_name in sorted(name for name in names if name.endswith(".rels")):
        root = parse_xml(zf, rels_name, errors)
        if root is None:
            continue
        # ppt/slides/_rels/slide1.xml.rels -> ppt/slides/slide1.xml
        if "/_rels/" in rels_name:
            base_file = rels_name.replace("/_rels/", "/").removesuffix(".rels")
        else:
            base_file = rels_name.removesuffix(".rels")
        for rel in root.findall("rel:Relationship", REL_NS):
            target = rel.get("Target", "")
            target_mode = rel.get("TargetMode", "")
            if target_mode == "External":
                continue
            resolved = normalize_rel_target(base_file, target)
            if resolved and resolved not in names:
                rel_type = rel.get("Type", "")
                message = f"Broken relationship target from {rels_name}: {target} -> {resolved} ({rel_type})"
                if "image" in rel_type or "/media/" in resolved:
                    errors.append(message)
                else:
                    warnings.append(message)


def validate_pptx(path: Path, expected_slides: int | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "file": str(path),
        "ok": False,
        "errors": [],
        "warnings": [],
        "counts": {},
        "details": {},
    }

    if not path.exists():
        report["errors"].append(f"File not found: {path}")
        return report
    if not zipfile.is_zipfile(path):
        report["errors"].append("File is not a valid zip/PPTX package")
        return report

    errors: list[str] = report["errors"]
    warnings: list[str] = report["warnings"]

    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        bad = zf.testzip()
        if bad:
            errors.append(f"Zip corruption detected at {bad}")

        if "[Content_Types].xml" not in names:
            errors.append("Missing [Content_Types].xml")
        if "ppt/presentation.xml" not in names:
            errors.append("Missing ppt/presentation.xml")
        if "ppt/_rels/presentation.xml.rels" not in names:
            errors.append("Missing ppt/_rels/presentation.xml.rels")

        # Parse all XML files.
        xml_files = sorted(name for name in names if name.endswith(".xml") or name.endswith(".rels"))
        for name in xml_files:
            parse_xml(zf, name, errors)

        slide_files = sorted(name for name in names if SLIDE_RE.match(name))
        notes_files = sorted(name for name in names if NOTES_RE.match(name))
        media_files = sorted(name for name in names if name.startswith("ppt/media/") and not name.endswith("/"))
        presentation_rel_count = count_slide_rels(zf, errors)
        overrides = content_type_overrides(zf, errors)

        slide_override_parts = sorted(part for part in overrides if SLIDE_RE.match(part))
        stale_slide_overrides = [part for part in slide_override_parts if part not in names]
        stale_notes_overrides = [part for part in overrides if NOTES_RE.match(part) and part not in names]

        if stale_slide_overrides:
            errors.append("Stale slide overrides in [Content_Types].xml: " + ", ".join(stale_slide_overrides))
        if stale_notes_overrides:
            warnings.append("Stale notes overrides in [Content_Types].xml: " + ", ".join(stale_notes_overrides))

        if expected_slides is not None and len(slide_files) != expected_slides:
            errors.append(f"Slide count mismatch: expected {expected_slides}, found {len(slide_files)}")

        if presentation_rel_count and presentation_rel_count != len(slide_files):
            warnings.append(
                f"Presentation relationship slide count differs from slide files: rels={presentation_rel_count}, files={len(slide_files)}"
            )

        if notes_files:
            warnings.append(f"Notes slides present: {len(notes_files)}. Remove unless speaker notes are required.")

        validate_relationship_targets(zf, warnings, errors)

        report["counts"] = {
            "slides": len(slide_files),
            "slide_overrides": len(slide_override_parts),
            "presentation_relationships": presentation_rel_count,
            "notes_slides": len(notes_files),
            "media": len(media_files),
            "xml_parts": len(xml_files),
        }
        report["details"] = {
            "slide_files": slide_files,
            "notes_files": notes_files,
            "media_files": media_files,
            "stale_slide_overrides": stale_slide_overrides,
            "stale_notes_overrides": stale_notes_overrides,
        }

    report["ok"] = not report["errors"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a PPTX package")
    parser.add_argument("pptx", help="Path to .pptx file")
    parser.add_argument("--expected-slides", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate_pptx(Path(args.pptx).resolve(), expected_slides=args.expected_slides)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"File: {report['file']}")
        print(f"OK: {report['ok']}")
        print("Counts:")
        for key, value in report.get("counts", {}).items():
            print(f"  {key}: {value}")
        if report["errors"]:
            print("Errors:")
            for item in report["errors"]:
                print(f"  - {item}")
        if report["warnings"]:
            print("Warnings:")
            for item in report["warnings"]:
                print(f"  - {item}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
