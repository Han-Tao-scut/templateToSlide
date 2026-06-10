# Math Formula Pipeline

Use LaTeX as the canonical formula representation. HTML preview and PPTX export must render from the same formula source instead of maintaining independent formula outputs.

## Goals

- Keep formulas visually consistent between HTML and PPTX.
- Preserve the original LaTeX for regeneration, search, repair, and accessibility metadata.
- Avoid making PowerPoint-native equation objects the default requirement, because native editable Office math requires a more complex OMML-specific path.
- Keep formula rendering deterministic enough for validation.

## Formula detection

Detect formulas before slide HTML authoring.

Supported source patterns:

- Inline math: `$...$` or `\(...\)`
- Block math: `$$...$$` or `\[...\]`
- Explicit content block objects with `kind: "formula"`

Do not treat currency, shell variables, or ordinary dollar signs as formulas without clear math syntax.

## Math manifest

Create `build/math-manifest.json` when a deck contains formulas.

```json
{
  "renderer_policy": {
    "html": "katex-or-mathjax",
    "pptx": "svg",
    "fallback": "png",
    "preserve_latex_metadata": true
  },
  "items": [
    {
      "id": "math-001",
      "latex": "E = mc^2",
      "display": false,
      "source_slide": 2,
      "semantic_role": "formula",
      "style": {
        "font_size_px": 28,
        "color": "#111111"
      },
      "assets": {
        "svg": "build/math/math-001.svg",
        "png": null
      }
    }
  ]
}
```

Slide plans and HTML should reference formula IDs instead of duplicating renderer-specific output.

## HTML representation

Use stable LaTeX-backed nodes:

```html
<span
  class="math math-inline"
  data-math-id="math-001"
  data-math-type="inline"
  data-latex="E = mc^2"></span>

<div
  class="math math-block"
  data-math-id="math-002"
  data-math-type="block"
  data-latex="\int_0^1 x^2 dx = \frac{1}{3}"></div>
```

HTML preview may render these nodes with KaTeX, MathJax, or a project-local renderer. The rendered HTML must remain inside the export slide node and must not depend on external network assets.

## PPTX representation

Default PPTX policy:

1. Render LaTeX to SVG using the selected local math renderer.
2. Insert the SVG as a replaceable image asset in PPTX.
3. Preserve the original LaTeX in alt text, notes, or custom metadata where the exporter supports it.
4. Fall back to PNG only when SVG import is unsupported by the target exporter.

This default prioritizes visual fidelity and package stability. Native PowerPoint equation objects may be added later as an advanced path, but they must not block the base formula workflow.

## Validation

Formula validation should check:

- every math node has a matching manifest item
- every manifest item has a non-empty LaTeX source
- every PPTX formula asset referenced by the manifest exists in the package or build directory
- SVG assets are parseable XML
- unsupported or failed formulas are reported with their `math-id` and slide number

## Failure behavior

- If a formula cannot be parsed, preserve the raw LaTeX text and report the failure.
- If SVG generation fails, try PNG fallback only when a local renderer is available.
- If all rendering fails, insert a visible text fallback such as `[formula: <latex>]` and include the error in the validation report.
