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
    ├── profile.json
    ├── style-guide.md
    ├── master-summary.md
    ├── pptx-unpacked/
    └── assets/
build/
├── slide-plan.json
├── preview-1.html           # creative mode only
├── preview-2.html           # creative mode only
├── preview-3.html           # creative mode only
├── deck.html
├── deck.pptx
└── validation-report.json
```

## End-to-end flow

1. Run dependency preflight.
2. Extract a style profile from the PPT/PPTX template or load a named existing profile.
3. Normalize the outline, content, audience, language, page count, and assets.
4. Produce `build/slide-plan.json`.
5. Route to template direct mode or creative preview mode.
6. Author clean fixed-size HTML under `#pptx-export-root`.
7. Export PPTX through `dom-to-pptx`.
8. Validate PPTX package integrity.
9. Deliver `.pptx`, validation report, and profile metadata.

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

## Density rules

- Prefer claim-like slide titles.
- Keep dense research or technical material structured with tables, formula boxes, comparison panels, timelines, and compact callouts.
- Put large hero treatments primarily on cover, section, and summary slides.
- Never compress content until it becomes unreadable; split into more slides when necessary.
