---
name: template-to-slide
description: Create reusable PowerPoint template style profiles and generate native editable PPTX decks from those profiles, outlines, and content. Use when the user provides a PPT/PPTX template, names an existing style profile, or asks to generate slides that follow a template. Always run dependency checks first, extract or reuse a template style profile, choose direct template mode by default, use frontend-slides only for optional creative previews, author dom-to-pptx-compatible HTML, export through dom-to-pptx, and validate the generated PPTX.
---

# Template to Slide

## Core contract

- Final deliverable is a native editable `.pptx` unless the user explicitly asks for another format.
- The reusable asset is the template style profile under `.ppt-style-profiles/<profile-id>/`.
- HTML is an intermediate authoring and conversion representation, not the final editing surface.
- Use `dom-to-pptx` as the primary PPTX export path.
- Use `frontend-slides` only as a visual design subsystem for creative preview and high-density HTML layout guidance.
- Do not use screenshot-only PPTX export unless the user explicitly accepts non-editable slides.

## Required first step: preflight

Before template extraction or deck generation, run dependency detection:

```bash
python3 scripts/check_dependencies.py --cwd . --json
```

If the user is about to generate a final PPTX, run strict detection:

```bash
python3 scripts/check_dependencies.py --cwd . --strict --json
```

If runtime dependencies are missing, run `scripts/setup_environment.py` only after user approval. Never perform global or network installation silently. See `references/dependency-routing.md`.

## Operating modes

### 1. Template direct mode, default

Use this when the user specifies a template style/profile and wants a deck that follows it.

Flow: preflight -> extract or reuse profile -> normalize inputs -> slide plan -> dom-to-pptx HTML -> PPTX export -> validation -> delivery.

Do not force three previews in this mode. Prioritize template fidelity, editable output, and deterministic generation.

### 2. Creative preview mode, opt-in

Use this when the user asks to innovate, compare visual directions, or see options.

Flow: preflight -> extract or reuse profile -> normalize inputs -> slide plan -> three first-slide HTML previews -> user selects or mixes directions -> full dom-to-pptx HTML -> PPTX export -> validation -> delivery.

The three previews must still obey the template style profile. `frontend-slides` may expand the visual expression but must not override mandatory template rules.

### 3. Profile extraction / validation / repair mode

Use this when the user only wants to extract a style profile, inspect a template, validate a PPTX, or repair PPTX package issues.

## Main workflow

1. **Preflight dependencies**
   - Run `scripts/check_dependencies.py`.
   - Required: Python 3, Node.js, npm or pnpm, `dom-to-pptx`, `pptxgenjs`, Playwright browser path.
   - Companion skills: `frontend-slides` and `dom-to-pptx` should be installed for best results.
   - See `references/dependency-routing.md`.

2. **Extract or reuse template style profile**
   - If a PPT/PPTX template is provided, extract style before content generation.
   - If the user names an existing profile, reuse it.
   - Default profile location: `.ppt-style-profiles/<profile-id>/`.
   - Extract slide size, theme colors, fonts, masters/layouts, logo/media assets, cover/content patterns, typography scale, table/callout/formula style, and reusable PPTX parts.
   - See `references/template-style-profile.md` and `references/style-profile-reuse.md`.

3. **Normalize input**
   - Collect outline, content source, audience, language, page count, required assets, fidelity requirements, and output scope.
   - Preserve mandatory names, institutional branding, dates, numbers, formulas, citations, and quoted text exactly.
   - See `references/input-contract.md`.

4. **Create slide plan**
   - Convert outline and content into a slide-by-slide JSON plan before writing visual HTML.
   - Each slide must have a type, title, takeaway claim, content blocks, visual intent, and template layout mapping.
   - See `references/workflow.md`.

5. **Choose generation path**
   - Default to template direct mode.
   - Use creative preview mode only when requested or clearly implied.
   - See `references/modes.md` and `references/frontend-dom-design.md`.

6. **Author dom-to-pptx-compatible HTML**
   - Use one clean export root and one fixed 16:9 `.slide` element per slide.
   - Recommended canvas: `1920px x 1080px`.
   - Avoid editor UI, hidden controls, debug labels, hover states, animations, and unsupported CSS effects in the export DOM.
   - See `references/dom-to-pptx-contract.md`.

7. **Export PPTX**
   - Export through `scripts/export_dom_to_pptx.mjs` or a project-local equivalent.
   - Preserve editability: text should remain PowerPoint text where possible; images should remain replaceable PPT images; boxes, tables, and callouts should become editable shapes where supported.

8. **Validate and repair**
   - Run `scripts/validate_pptx.py` on every generated PPTX.
   - Check zip integrity, XML parseability, slide count, relationships, content types, media references, and notes cleanup.
   - Use targeted OpenXML repair only for package-level issues.
   - See `references/pptx-validation.md`.

9. **Deliver**
   - Report final `.pptx` path, style profile used or created, generation mode, export path, validation status, and known fidelity limitations.

## Hard rules

- Always preflight before extraction or generation.
- Ask before network installation, global installation, or destructive file operations.
- Prefer project-local npm packages over global packages.
- Reuse existing style profiles when available instead of re-extracting.
- Default to template direct mode; do not force the preview gate unless the user asks for creative exploration.
- In creative preview mode, generate exactly three first-slide previews and wait for style selection before full-deck generation.
- Never let `frontend-slides` override the template style profile, brand requirements, or mandatory content.
- Never maintain editable HTML and PPTX as two independent final sources unless the user explicitly requests both.

## References

- `references/workflow.md`: end-to-end execution workflow and artifacts.
- `references/slide-plan-schema.md`: controlled slide-plan schema.
- `references/modes.md`: mode selection and routing rules.
- `references/input-contract.md`: expected inputs and normalized project shape.
- `references/dependency-routing.md`: dependency detection, setup, and fallback rules.
- `references/template-style-profile.md`: profile extraction schema and principles.
- `references/style-profile-reuse.md`: profile naming, caching, and reuse.
- `references/frontend-dom-design.md`: how to combine template constraints with frontend-slides design guidance.
- `references/preview-workflow.md`: three-preview rules for creative mode.
- `references/dom-to-pptx-contract.md`: HTML/CSS contract for editable PPTX export.
- `references/pptx-validation.md`: PPTX validation and repair checklist.
