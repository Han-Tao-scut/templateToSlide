# PPTX Validation

Validate every generated PPTX before delivery.

## Package Checks

- Open as a zip archive.
- Run `ZipFile.testzip()` or equivalent.
- Parse all XML parts.
- Count `ppt/slides/slide*.xml` files.
- Count slide relationships from `ppt/presentation.xml` and `ppt/_rels/presentation.xml.rels`.
- Ensure slide count matches the requested deck when expected count is provided.
- Ensure `[Content_Types].xml` has no stale slide or notes overrides.
- Ensure every image relationship target exists.
- Report unused notes slides unless the user requested speaker notes.

## Visual Checks

When available:

- Open or render the PPTX through PowerPoint, LibreOffice, or another renderer.
- Compare the first slide against the selected HTML preview.
- Inspect at least cover, one dense content slide, one table/formula slide, and the summary slide.
- Check for clipped text, missing images, wrong fonts, broken line height, and shifted page numbers.

## Repair Rules

Use OpenXML targeted repair for:

- broken relationships
- missing media targets
- wrong slide count
- stale content types
- theme/master/layout reuse
- package cleanup after using a template PPTX as the base

Do not use OpenXML as the primary design generator unless `dom-to-pptx` is unavailable and the user explicitly accepts the fallback.

## Validation Report

The validator emits:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "counts": {
    "slides": 0,
    "presentation_relationships": 0,
    "media": 0
  }
}
```
