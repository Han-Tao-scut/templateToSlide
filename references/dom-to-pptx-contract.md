# dom-to-pptx Contract

Author HTML so it can become editable PPTX. HTML is the intermediate design source; PowerPoint is the final editing surface.

## Slide DOM Shape

Use one clean export container and one fixed-size element per slide:

```html
<main id="pptx-export-root">
  <section class="slide" data-slide="1">...</section>
  <section class="slide" data-slide="2">...</section>
</main>
```

Recommended base CSS:

```css
.slide {
  position: relative;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
  background: #ffffff;
  box-sizing: border-box;
}
```

## Authoring Rules

- Do not use a scaled stage as the export DOM. If a viewport preview uses `transform: scale(...)`, export the unscaled `1920 x 1080` DOM.
- Use pixel units for layout, font size, borders, and spacing.
- Inline or colocate critical styles so computed layout is deterministic.
- Use normal HTML text for editable text. Avoid rasterizing text into images.
- Use explicit `line-height` when line spacing matters.
- Use supported primitives: text blocks, images, SVG, rectangles, gradients, borders, shadows, flex/grid where supported, and absolutely positioned blocks for precise slide geometry.
- Rewrite unsupported CSS effects into simpler exportable shapes.
- Avoid animation-only states; PPTX export should capture the final static slide.
- Avoid editor UI, hidden controls, debug overlays, hover affordances, and preview labels inside the export root.
- Convert external images to data URLs or local accessible paths when needed.
- Keep each slide self-contained; avoid layout that depends on page scroll position.

## PPTX Editability Goals

- Text remains PowerPoint text where possible.
- Background images remain images.
- Color panels, rules, callout boxes, table cells, and formula boxes become editable shapes where possible.
- Tables may be exported as grouped text/shapes if true native PPT tables are not available.
- Formulas may be text boxes unless the user explicitly requires PowerPoint equation objects.

## Export Discipline

- Read the installed `dom-to-pptx` package examples or official skill before adapting the exporter.
- Export only selected `.slide` nodes under `#pptx-export-root`.
- Use the selected preview direction for full-deck HTML in innovation preview mode.
- Validate output after export; do not assume conversion fidelity.
