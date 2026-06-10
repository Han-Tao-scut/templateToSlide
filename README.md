# Template to Slide

`template-to-slide` is a ChatGPT Skill for extracting reusable style profiles from PPT/PPTX templates and generating native editable PPTX decks from those profiles, outlines, and content.

## Core idea

1. Extract deterministic style evidence from a PPT/PPTX template by reading the OpenXML package.
2. Clean and normalize the extracted evidence into a reusable template style profile.
3. Use AI only after XML extraction to summarize style intent, layout rules, and cleanup decisions.
4. Generate `dom-to-pptx` compatible HTML from the content, style profile, and slide plan.
5. Preserve LaTeX formulas through a shared math manifest so HTML and PPTX render consistently.
6. Convert HTML to editable PPTX.
7. Validate the PPTX package before delivery.

## Modes

- **Template direct mode**: default. Follow a specified style profile and generate the deck directly.
- **Creative preview mode**: optional. Combine the profile with `frontend-slides` design guidance and generate three first-slide previews before full deck generation.
- **Profile-only mode**: extract and save style information for reuse.
- **Validate/repair mode**: inspect a PPTX package and report structural problems.

## Setup

This project does not automatically install system software, npm packages, browsers, or companion Skills. Install them manually, then run the checker.

Required for the main export path:

- Python 3.10+
- Node.js 20+
- npm or pnpm
- project-local npm dependencies from `package.json`
- Playwright Chromium or an equivalent Chromium executable
- manually installed companion Skills, when used: `frontend-slides` and `dom-to-pptx`

Verify the environment:

```bash
python3 scripts/check_dependencies.py --cwd . --strict --json
```

See [`INSTALL.md`](INSTALL.md) for manual installation steps and [`references/dependency-routing.md`](references/dependency-routing.md) for runtime routing rules.

## Extract a profile

```bash
python3 scripts/extract_template_style.py input/template.pptx --profile-id my-template
```

The profile extraction flow is:

```text
PPTX OpenXML package
  -> raw XML evidence
  -> deterministic cleaning and normalization
  -> AI style summary and cleanup notes
  -> reusable style profile
```

See [`references/template-style-profile.md`](references/template-style-profile.md) and [`references/ai-style-summarization.md`](references/ai-style-summarization.md).

## Formula support

Use LaTeX as the canonical formula source. HTML preview renders formulas through a browser math renderer, while PPTX output should default to SVG math assets with the original LaTeX preserved in metadata.

See [`references/math-formula-pipeline.md`](references/math-formula-pipeline.md).

## Validate a PPTX

```bash
python3 scripts/validate_pptx.py build/deck.pptx --expected-slides 12 --json
```
