#!/usr/bin/env python3
"""Extract a reusable style profile from a PPT/PPTX template.

The extractor focuses on stable package-level style signals that are useful for
reusing a template: slide size, theme colors, fonts, master/layout structure,
media assets, and a human-readable style guide. It does not screenshot slides.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
EMU_PER_INCH = 914400
PX_PER_INCH = 96


def safe_profile_id(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "template-profile"


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        data = zf.read(name)
    except KeyError:
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        return None


def emu_to_px(value: str | int | None) -> int | None:
    if value is None:
        return None
    try:
        return round(int(value) / EMU_PER_INCH * PX_PER_INCH)
    except (TypeError, ValueError):
        return None


def detect_aspect(width_px: int | None, height_px: int | None) -> str:
    if not width_px or not height_px:
        return "unknown"
    ratio = width_px / height_px
    if abs(ratio - 16 / 9) < 0.03:
        return "16:9"
    if abs(ratio - 4 / 3) < 0.03:
        return "4:3"
    if abs(ratio - 16 / 10) < 0.03:
        return "16:10"
    return f"{ratio:.3f}:1"


def extract_slide_size(zf: zipfile.ZipFile) -> dict[str, Any]:
    root = read_xml(zf, "ppt/presentation.xml")
    if root is None:
        return {"cx": None, "cy": None, "width_px": None, "height_px": None, "aspect": "unknown"}
    sld_sz = root.find("p:sldSz", NS)
    if sld_sz is None:
        return {"cx": None, "cy": None, "width_px": None, "height_px": None, "aspect": "unknown"}
    cx = sld_sz.get("cx")
    cy = sld_sz.get("cy")
    width_px = emu_to_px(cx)
    height_px = emu_to_px(cy)
    return {
        "cx": int(cx) if cx and cx.isdigit() else cx,
        "cy": int(cy) if cy and cy.isdigit() else cy,
        "width_px": width_px,
        "height_px": height_px,
        "aspect": detect_aspect(width_px, height_px),
    }


def get_scheme_color_values(scheme: ET.Element) -> dict[str, str]:
    colors: dict[str, str] = {}
    for child in list(scheme):
        name = child.tag.rsplit("}", 1)[-1]
        srgb = child.find(".//a:srgbClr", NS)
        sysclr = child.find(".//a:sysClr", NS)
        if srgb is not None and srgb.get("val"):
            colors[name] = "#" + srgb.get("val", "").upper()
        elif sysclr is not None and sysclr.get("lastClr"):
            colors[name] = "#" + sysclr.get("lastClr", "").upper()
    return colors


def extract_theme(zf: zipfile.ZipFile) -> dict[str, Any]:
    theme_files = sorted(name for name in zf.namelist() if name.startswith("ppt/theme/theme") and name.endswith(".xml"))
    result: dict[str, Any] = {"theme_files": theme_files, "colors": {}, "fonts": {}}
    if not theme_files:
        return result

    root = read_xml(zf, theme_files[0])
    if root is None:
        return result

    scheme = root.find(".//a:clrScheme", NS)
    if scheme is not None:
        raw = get_scheme_color_values(scheme)
        result["colors"] = {
            "raw_scheme": raw,
            "background": raw.get("lt1") or raw.get("bg1") or raw.get("dk1"),
            "text": raw.get("dk1") or raw.get("tx1"),
            "primary": raw.get("accent1"),
            "secondary": raw.get("accent2"),
            "accent": [raw.get(f"accent{i}") for i in range(1, 7) if raw.get(f"accent{i}")],
        }

    major_latin = root.find(".//a:fontScheme/a:majorFont/a:latin", NS)
    minor_latin = root.find(".//a:fontScheme/a:minorFont/a:latin", NS)
    ea_major = root.find(".//a:fontScheme/a:majorFont/a:ea", NS)
    ea_minor = root.find(".//a:fontScheme/a:minorFont/a:ea", NS)
    result["fonts"] = {
        "latin": (major_latin.get("typeface") if major_latin is not None else "") or (minor_latin.get("typeface") if minor_latin is not None else ""),
        "latin_body": minor_latin.get("typeface") if minor_latin is not None else "",
        "east_asian": (ea_major.get("typeface") if ea_major is not None else "") or (ea_minor.get("typeface") if ea_minor is not None else ""),
        "east_asian_body": ea_minor.get("typeface") if ea_minor is not None else "",
        "fallback": "Aptos",
    }
    return result


def count_parts(zf: zipfile.ZipFile, prefix: str, suffix: str = ".xml") -> int:
    return len([name for name in zf.namelist() if name.startswith(prefix) and name.endswith(suffix)])


def list_parts(zf: zipfile.ZipFile, prefix: str, suffix: str | None = None) -> list[str]:
    names = [name for name in zf.namelist() if name.startswith(prefix)]
    if suffix:
        names = [name for name in names if name.endswith(suffix)]
    return sorted(names)


def extract_media(zf: zipfile.ZipFile, assets_dir: Path) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for name in list_parts(zf, "ppt/media/"):
        if name.endswith("/"):
            continue
        target = assets_dir / Path(name).name
        target.write_bytes(zf.read(name))
        assets.append({"source": name, "file": str(target.relative_to(assets_dir.parent)), "bytes": target.stat().st_size})
    return assets


def extract_text_signals(zf: zipfile.ZipFile, limit: int = 5) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    slide_files = list_parts(zf, "ppt/slides/slide", ".xml")[:limit]
    for slide in slide_files:
        root = read_xml(zf, slide)
        if root is None:
            continue
        texts = [node.text.strip() for node in root.findall(".//a:t", NS) if node.text and node.text.strip()]
        signals.append({"slide": slide, "texts": texts[:20]})
    return signals


def write_style_guide(profile: dict[str, Any], path: Path) -> None:
    colors = profile.get("colors", {})
    fonts = profile.get("fonts", {})
    lines = [
        f"# Style Guide: {profile['id']}",
        "",
        f"Source template: `{profile['source_pptx']}`",
        f"Created: {profile['created_at']}",
        "",
        "## Slide Size",
        "",
        f"- Aspect: {profile['slide_size'].get('aspect')}",
        f"- Size: {profile['slide_size'].get('width_px')} x {profile['slide_size'].get('height_px')} px equivalent",
        "",
        "## Fonts",
        "",
        f"- Latin heading/body: {fonts.get('latin') or 'not detected'} / {fonts.get('latin_body') or 'not detected'}",
        f"- East Asian heading/body: {fonts.get('east_asian') or 'not detected'} / {fonts.get('east_asian_body') or 'not detected'}",
        f"- Fallback: {fonts.get('fallback') or 'Aptos'}",
        "",
        "## Colors",
        "",
        f"- Background: {colors.get('background') or 'not detected'}",
        f"- Text: {colors.get('text') or 'not detected'}",
        f"- Primary: {colors.get('primary') or 'not detected'}",
        f"- Secondary: {colors.get('secondary') or 'not detected'}",
        f"- Accents: {', '.join(colors.get('accent') or []) or 'not detected'}",
        "",
        "## Layout Guidance",
        "",
        "- Use the extracted slide size as the fixed HTML stage.",
        "- Treat master/layout counts and media assets as template constraints.",
        "- Reuse logos, repeated decorative assets, and theme colors before introducing new visual elements.",
        "- Keep cover, section, content, table, formula, and summary slides visually consistent with the source template.",
        "",
        "## Text Signals From Early Slides",
        "",
    ]
    for signal in profile.get("text_signals", []):
        lines.append(f"- {signal['slide']}: " + " | ".join(signal.get("texts", [])[:6]))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_master_summary(profile: dict[str, Any], path: Path) -> None:
    layouts = profile.get("layouts", {})
    package_parts = profile.get("package_parts", [])
    lines = [
        f"# Master Summary: {profile['id']}",
        "",
        f"- Slides: {layouts.get('slide_count')}",
        f"- Masters: {layouts.get('master_count')}",
        f"- Layouts: {layouts.get('layout_count')}",
        f"- Themes: {len(profile.get('theme_files', []))}",
        f"- Media assets: {len(profile.get('assets', []))}",
        "",
        "## Package Parts",
        "",
    ]
    for part in package_parts:
        lines.append(f"- `{part}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def extract_profile(pptx_path: Path, profile_id: str, out_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    if not pptx_path.exists():
        raise FileNotFoundError(f"Template not found: {pptx_path}")
    if not zipfile.is_zipfile(pptx_path):
        raise ValueError(f"Not a valid PPTX zip package: {pptx_path}")

    profile_id = safe_profile_id(profile_id)
    profile_dir = out_dir / profile_id
    if profile_dir.exists() and not overwrite:
        raise FileExistsError(f"Profile already exists: {profile_dir}. Use --overwrite to refresh it.")

    if profile_dir.exists():
        shutil.rmtree(profile_dir)
    assets_dir = profile_dir / "assets"
    unpacked_dir = profile_dir / "pptx-unpacked"
    assets_dir.mkdir(parents=True, exist_ok=True)
    unpacked_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(pptx_path) as zf:
        zf.extractall(unpacked_dir)
        slide_size = extract_slide_size(zf)
        theme = extract_theme(zf)
        assets = extract_media(zf, assets_dir)
        package_parts = [
            *list_parts(zf, "ppt/theme/", ".xml"),
            *list_parts(zf, "ppt/slideMasters/", ".xml"),
            *list_parts(zf, "ppt/slideLayouts/", ".xml"),
            *list_parts(zf, "ppt/media/"),
        ]
        profile: dict[str, Any] = {
            "id": profile_id,
            "source_pptx": str(pptx_path),
            "created_at": dt.datetime.now(dt.UTC).isoformat(),
            "slide_size": slide_size,
            "fonts": theme.get("fonts", {}),
            "colors": theme.get("colors", {}),
            "theme_files": theme.get("theme_files", []),
            "layouts": {
                "master_count": count_parts(zf, "ppt/slideMasters/slideMaster"),
                "layout_count": count_parts(zf, "ppt/slideLayouts/slideLayout"),
                "slide_count": count_parts(zf, "ppt/slides/slide"),
                "cover": {},
                "content": {},
                "section": {},
                "summary": {},
            },
            "assets": assets,
            "package_parts": package_parts,
            "text_signals": extract_text_signals(zf),
        }

    (profile_dir / "profile.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_style_guide(profile, profile_dir / "style-guide.md")
    write_master_summary(profile, profile_dir / "master-summary.md")
    return profile


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a reusable style profile from a PPTX template")
    parser.add_argument("template", help="Path to template .pptx")
    parser.add_argument("--profile-id", default=None, help="Stable profile ID. Defaults to the template filename stem.")
    parser.add_argument("--out", default=".ppt-style-profiles", help="Directory that contains profile directories")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing profile directory")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    template = Path(args.template).resolve()
    profile_id = args.profile_id or template.stem
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        profile = extract_profile(template, profile_id, out_dir, overwrite=args.overwrite)
        if args.json:
            print(json.dumps({"ok": True, "profile": profile, "profile_dir": str(out_dir / safe_profile_id(profile_id))}, indent=2, ensure_ascii=False))
        else:
            print(f"Created profile: {out_dir / safe_profile_id(profile_id)}")
            print(f"Slides: {profile['layouts']['slide_count']}")
            print(f"Aspect: {profile['slide_size']['aspect']}")
            print(f"Assets: {len(profile['assets'])}")
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
