# Slide Plan Schema

Generate a slide plan before writing HTML.

## Minimal Schema

```json
{
  "deck_title": "",
  "audience": "",
  "purpose": "",
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
      "notes": ""
    }
  ]
}
```

## Content blocks

Use a small controlled vocabulary for content block kinds. Formula blocks must reference `math-manifest.json` entries.

```json
{
  "kind": "formula",
  "math_id": "math-001",
  "caption": "Optional caption",
  "placement": "callout"
}
```

Do not place renderer-specific KaTeX, MathJax, SVG, or PNG output directly in the slide plan.

## Slide Types

Use a small controlled vocabulary:

- `cover`
- `agenda`
- `section`
- `content`
- `comparison`
- `table`
- `figure`
- `method`
- `formula`
- `timeline`
- `summary`
- `appendix`

## Planning Rules

- Use claim-like titles for research decks.
- Keep each slide focused on one message.
- Put dense evidence into structured tables, figure panels, formula boxes, or callouts.
- Map every slide to a template layout role.
- Preserve important numbers, terms, citations, and notation.
- Preserve formulas through math manifest IDs when formulas are present.
- Avoid vague placeholders such as `TBD` unless the user explicitly requests placeholders.
