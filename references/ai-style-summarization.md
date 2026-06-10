# AI Style Summarization

Template style extraction must be evidence-first. XML parsing and deterministic cleaning produce the facts; AI summarizes those facts into reusable style guidance and cleanup notes.

## Position in the pipeline

```text
PPTX OpenXML package
  -> raw XML evidence
  -> deterministic cleaning and normalization
  -> AI style summarization
  -> reusable profile overlay
```

AI must not read a template screenshot and invent a design system. AI must not overwrite raw XML facts.

## Inputs to AI

Provide compact cleaned evidence, not the entire unpacked PPTX package.

Recommended input bundle:

- slide size and aspect ratio
- theme color tokens and observed color frequencies
- theme fonts and observed text runs
- master/layout inventory
- placeholder geometry summaries
- title/body/footer patterns
- table, callout, chart, image, and formula style observations
- repeated assets and logo candidates
- rule-based outlier notes

## Output contract

AI should produce a profile overlay with this shape:

```json
{
  "style_summary": "Concise description of the template's visual language.",
  "layout_principles": [
    "Reusable layout rule derived from evidence."
  ],
  "typography_guidance": {
    "title": "How titles should be used.",
    "body": "How body text should be used.",
    "caption": "How small labels or captions should be used."
  },
  "color_guidance": {
    "primary_use": "How primary colors should be applied.",
    "accent_use": "How accent colors should be applied.",
    "avoid": ["Color usage to avoid."]
  },
  "component_guidance": {
    "tables": "Table style rules.",
    "callouts": "Callout style rules.",
    "figures": "Figure and image placement rules.",
    "formulas": "Formula box and math notation style rules."
  },
  "do": ["Positive rule."],
  "avoid": ["Negative rule."],
  "confidence": {
    "palette": 0.0,
    "typography": 0.0,
    "layout": 0.0,
    "components": 0.0
  },
  "evidence_gaps": ["Missing or weak evidence."],
  "cleanup_notes": ["Normalization or outlier decision to preserve for audit."]
}
```

## Rules

- Cite evidence keys or summaries in cleanup notes when decisions are non-obvious.
- Do not introduce colors, fonts, logos, or layout roles that were not present in the cleaned evidence unless explicitly marked as a recommendation.
- Keep the output reusable: rules should guide future slides, not merely describe individual source slides.
- Separate observed facts from interpretive guidance.
- Assign lower confidence when the template has few slides, inconsistent layouts, or missing master/theme information.

## Artifacts

For each profile, preserve three layers:

```text
.ppt-style-profiles/<profile-id>/
├── raw-evidence.json
├── cleaned-profile.json
├── ai-style-summary.json
├── style-guide.md
├── pptx-unpacked/
└── assets/
```

`raw-evidence.json` and `cleaned-profile.json` are deterministic artifacts. `ai-style-summary.json` and `style-guide.md` are interpretive overlays.
