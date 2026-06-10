# Workflow

## Artifact layout

Use this project-local layout when a task involves both template extraction and deck generation:

```text
input/
├── outline.md
├── content.md
├── style-guide.md
└── template.pptx            # optional if a profile already exists
.ppt-style-profiles/
└── <profile-id>/
    ├── raw-evidence.json
    ├── cleaned-profile.json
    ├── ai-style-summary.json
    ├── style-guide.md
    ├── master-summary.md
    ├── pptx-unpacked/
    └── assets/
build/
├── slide-plan.json
├── math-manifest.json       # present when formulas are detected
├── math/
│   ├── math-001.svg
│   └── ...
├── preview-1.html           # creative mode only
├── preview-2.html           # creative mode only
├── preview-3.html           # creative mode only
├── deck.html
├── deck.pptx
└── validation-report.json
```

## End-to-end flow

1. Run read-only dependency preflight.
2. Extract raw XML evidence from the PPT/PPTX template or load a named existing profile.
3. Clean and normalize the extracted evidence deterministically.
4. Use AI to summarize style intent and cleanup decisions from the cleaned evidence.
5. Normalize the outline, content, audience, language, page count, assets, and formulas.
6. Produce `build/slide-plan.json`.
7. Produce `build/math-manifest.json` when formulas are present.
8. Route to template direct mode or creative preview mode.
9. Author clean fixed-size HTML under `#pptx-export-root`.
10. Export PPTX through `dom-to-pptx`.
11. Validate PPTX package integrity and formula asset references.
12. Deliver `.pptx`, validation report, and profile metadata.

## Slide plan contract

Before writing visual HTML, create a slide plan with this minimum shape:

```json
{
  "deck_title": "",
  "audience": "",
  "language": "zh-CN",
  "style_profile_id": "",
  "mode": "template-direct",
  "slides": [
    {
      "index": 1,
      "type": "cover",
      "title": "",
      "claim": "",
      "content_blocks": [],
      "visual_intent": "",
      "template_layout": "cover",
      "required_assets": [],
      "speaker_notes": ""
    }
  ]
}
```

Formula blocks should reference manifest IDs:

```json
{
  "kind": "formula",
  "math_id": "math-001",
  "caption": "Einstein mass-energy relation"
}
```

## Density rules

- Prefer claim-like slide titles.
- Keep dense research or technical material structured with tables, formula boxes, comparison panels, timelines, and compact callouts.
- Put large hero treatments primarily on cover, section, and summary slides.
- Never compress content until it becomes unreadable; split into more slides when necessary.
