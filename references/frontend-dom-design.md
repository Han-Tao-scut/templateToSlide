# frontend-slides and DOM Design

`frontend-slides` is a design assistant, not the final export path.

## Use It For

- visual exploration
- high-density slide composition
- first-slide previews
- bold layout variations
- typography hierarchy
- visual grouping of tables, formulas, figures, and claims

## Do Not Use It For

- final browser editor runtime
- PPTX export
- dependency installation
- PPTX package repair
- replacing template constraints

## Constraint Priority

Apply constraints in this order:

1. User's mandatory content and branding.
2. Template style profile.
3. `dom-to-pptx` compatibility.
4. frontend-slides design suggestions.

## Design Rules

- Use the template profile's colors and fonts as the default design vocabulary.
- If innovating, vary layout, scale, density, and visual rhythm before inventing new brand colors.
- Keep text editable by using ordinary HTML text nodes.
- Use shapes, rules, panels, and callouts that can map cleanly to PPTX primitives.
- Avoid effects that are likely to rasterize or break export fidelity.
