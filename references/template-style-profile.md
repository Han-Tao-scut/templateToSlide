# Template Style Profile

A template style profile is the reusable design system extracted from a PPT/PPTX file. Extraction is evidence-first: parse OpenXML, clean the resulting facts deterministically, then use AI to summarize reusable style intent.

## Default Location

```text
.ppt-style-profiles/<profile-id>/
├── raw-evidence.json
├── cleaned-profile.json
├── ai-style-summary.json
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

## Layer 1: raw XML evidence

Parse the PPTX package without interpretation. Preserve raw evidence from:

- `ppt/presentation.xml`
- `ppt/theme/theme*.xml`
- `ppt/slideMasters/*.xml`
- `ppt/slideLayouts/*.xml`
- `ppt/slides/*.xml`
- `ppt/_rels/*`
- `ppt/media/*`

Minimum raw fields:

- slide size and aspect ratio
- theme colors and fonts
- master and layout inventory
- placeholder types and geometry
- observed text runs, font sizes, weights, colors, and positions
- shape fills, strokes, shadows, and geometry
- background definitions
- media assets and repeated logo candidates
- chart, table, callout, and formula-like shape observations
- package parts needed for later inspection or repair

## Layer 2: deterministic cleaning

Clean raw evidence before AI summarization.

Required normalization steps:

- convert EMU values to stable internal units
- normalize hex colors and remove near-duplicates
- merge near-identical font sizes into typography bands
- resolve theme font fallback chains
- expand master/layout inheritance where observable
- standardize placeholder roles such as title, subtitle, body, footer, page number, figure, table, and formula
- remove low-frequency artifacts from reusable style rules while preserving them in raw evidence
- cluster layout patterns into cover, section, content, comparison, figure, table, formula, and summary roles

## Layer 3: AI style summary

AI receives cleaned evidence, not the whole PPTX package. AI produces an interpretive overlay:

- visual style summary
- layout principles
- typography guidance
- color usage guidance
- component guidance for tables, figures, callouts, and formulas
- `do` and `avoid` rules
- confidence values
- evidence gaps
- cleanup notes

See `references/ai-style-summarization.md`.

## `cleaned-profile.json` Schema

```json
{
  "id": "profile-id",
  "source_pptx": "template.pptx",
  "created_at": "ISO-8601 timestamp",
  "slide_size": {
    "cx": 12192000,
    "cy": 6858000,
    "width_px": 1920,
    "height_px": 1080,
    "aspect": "16:9"
  },
  "fonts": {
    "latin": "",
    "east_asian": "",
    "fallback": "Aptos",
    "title_band_px": [],
    "body_band_px": []
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
    "roles": {
      "cover": {},
      "section": {},
      "content": {},
      "comparison": {},
      "figure": {},
      "table": {},
      "formula": {},
      "summary": {}
    }
  },
  "components": {
    "tables": {},
    "callouts": {},
    "figures": {},
    "formulas": {}
  },
  "assets": [],
  "package_parts": []
}
```

## Extraction Principles

- Do not screenshot the template as the design system.
- Do not let AI overwrite raw XML facts.
- Convert observed template behavior into reusable layout and style rules.
- Preserve original PPTX parts under `pptx-unpacked/` for later inspection and repair.
- If the template contains multiple style families, describe them in `ai-style-summary.json` and `style-guide.md`.
- Reuse an existing profile unless the user explicitly asks to re-extract or refresh it.
