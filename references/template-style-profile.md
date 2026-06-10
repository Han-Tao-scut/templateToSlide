# Template Style Profile

A template style profile is the reusable design system extracted from a PPT/PPTX file.

## Default Location

```text
.ppt-style-profiles/<profile-id>/
├── profile.json
├── style-guide.md
├── master-summary.md
├── pptx-unpacked/
└── assets/
```

Use stable lowercase hyphenated IDs such as `bgi-research-2026` or `lab-meeting-minimal`.

## Extraction Command

```bash
python3 scripts/extract_template_style.py input/template.pptx --profile-id <profile-id> --out .ppt-style-profiles
```

## Extracted Information

Minimum fields:

- slide size and aspect ratio from `ppt/presentation.xml`
- theme colors and fonts from `ppt/theme/theme*.xml`
- master and layout counts from `ppt/slideMasters/` and `ppt/slideLayouts/`
- media assets from `ppt/media/`
- cover slide signals: logo, title area, subtitle, speaker/date, background
- content slide signals: title position, body grid, footer, page number, table/callout/formula patterns
- reusable package parts for later repair or theme reuse

## `profile.json` Schema

```json
{
  "id": "profile-id",
  "source_pptx": "template.pptx",
  "created_at": "ISO-8601 timestamp",
  "slide_size": {
    "cx": 12192000,
    "cy": 6858000,
    "width_px": 1280,
    "height_px": 720,
    "aspect": "16:9"
  },
  "fonts": {
    "latin": "",
    "east_asian": "",
    "fallback": "Aptos"
  },
  "colors": {
    "primary": "",
    "secondary": "",
    "accent": [],
    "background": "",
    "text": ""
  },
  "layouts": {
    "master_count": 0,
    "layout_count": 0,
    "slide_count": 0,
    "cover": {},
    "content": {},
    "section": {},
    "summary": {}
  },
  "assets": [],
  "package_parts": []
}
```

## Extraction Principles

- Do not screenshot the template as the design system.
- Convert observed template behavior into reusable layout and style rules.
- Preserve original PPTX parts under `pptx-unpacked/` for later inspection and repair.
- If the template contains multiple style families, describe them in `style-guide.md`.
- Reuse an existing profile unless the user explicitly asks to re-extract or refresh it.
