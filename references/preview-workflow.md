# Preview Workflow

Use this only in innovation preview mode.

## Trigger

Generate three previews when the user asks for:

- innovation
- design options
- style alternatives
- more creative treatment
- preview before full deck
- comparison of visual directions

## Rules

- Generate exactly three first-slide HTML previews.
- Each preview must use real title, speaker/date/affiliation if available, and actual topic content.
- Do not write internal labels such as `Option A`, `Preview`, `Template`, or `Generated` inside the slide canvas.
- Previews should be visually distinct enough to support a real decision.
- At least one preview may be bolder or more experimental when appropriate.
- All previews must respect the template style profile.
- All previews must remain compatible with later `dom-to-pptx` export.
- Wait for the user's chosen preview or mix instruction before generating the full deck.

## Deliverable

Save previews as:

```text
build/preview-1.html
build/preview-2.html
build/preview-3.html
```

The selected direction becomes the visual system for the full export HTML.
