# Dependency Routing

Run dependency detection before reading, transforming, or generating presentation artifacts.

## Detection

From the skill root or project root:

```bash
python3 scripts/check_dependencies.py --cwd . --json
```

Before final PPTX export:

```bash
python3 scripts/check_dependencies.py --cwd . --strict --json
```

## Required runtime dependencies

- Python 3: PPTX zip/XML validation and template profile extraction.
- Node.js: required for `dom-to-pptx`.
- npm or pnpm: project-local dependency installation.
- `dom-to-pptx`: required primary HTML-to-PPTX export package.
- `pptxgenjs`: required as a PPTX generation/repair/fallback utility.
- Playwright or equivalent Chromium path: required for browser-layout-driven export.

## Companion skills

- `frontend-slides`: recommended for creative preview and visual HTML layout guidance.
- `dom-to-pptx`: recommended for package-specific DOM/CSS compatibility guidance.

Companion skills are not npm packages. They must be installed as ChatGPT/Codex skills separately from npm runtime dependencies.

## Setup

After user approval, run:

```bash
python3 scripts/setup_environment.py --cwd .
```

The setup script installs local npm dependencies only. It does not install global packages and does not silently install companion skills.

Equivalent manual install:

```bash
npm install
npx playwright install chromium
```

Use `pnpm install` only if the project already has `pnpm-lock.yaml` or the user requests pnpm.

## Routing rules

- If Python, Node, or npm/pnpm is missing, stop and report the blocker.
- If `dom-to-pptx` is missing, ask to run local setup before final generation.
- If setup is blocked, stop unless the user explicitly accepts an OpenXML-only fallback.
- If `frontend-slides` is missing, continue in template direct mode or use local `frontend-dom-design.md` guidance.
- If the `dom-to-pptx` skill is missing but the npm package exists, proceed using `dom-to-pptx-contract.md`.
- Optional tools such as LibreOffice, Poppler, ImageMagick, and Tesseract improve validation or extraction but must not block generation.
