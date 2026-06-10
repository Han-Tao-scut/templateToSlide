# Dependency Routing

Run dependency detection before reading, transforming, or generating presentation artifacts. Dependency detection is read-only and must not install software, npm packages, browsers, or companion Skills.

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

- Python 3.10 or newer: PPTX zip/XML validation and template profile extraction.
- Node.js 20 or newer: required for browser-driven rendering and `dom-to-pptx` export.
- npm or pnpm: required to install project-local npm dependencies manually.
- `dom-to-pptx`: required primary HTML-to-PPTX export package.
- `pptxgenjs`: required as a PPTX generation/repair/fallback utility.
- Playwright Chromium or an equivalent Chromium path: required for browser-layout-driven export.

## Companion Skills

- `frontend-slides`: recommended for creative preview and visual HTML layout guidance.
- `dom-to-pptx`: recommended for package-specific DOM/CSS compatibility guidance.

Companion Skills are not npm packages. They must be installed manually through the ChatGPT/Codex skill installation flow. Project scripts must not attempt to install them.

## Manual setup

See `INSTALL.md`. The canonical npm setup is:

```bash
npm install
npx playwright install chromium
```

Equivalent pnpm setup when the workspace uses pnpm:

```bash
pnpm install
pnpm exec playwright install chromium
```

Do not run installation commands implicitly. If dependencies are missing, report the missing items and point the user to `INSTALL.md`.

## Routing rules

- If Python, Node, or npm/pnpm is missing, stop and report the blocker.
- If required npm packages are missing, stop before final PPTX export and request manual installation.
- If Playwright Chromium or another usable Chromium executable is missing, stop before browser-layout-driven export and request manual installation.
- If `frontend-slides` is missing, continue in template direct mode or use local `frontend-dom-design.md` guidance.
- If the `dom-to-pptx` companion Skill is missing but the npm package exists, proceed using `dom-to-pptx-contract.md`.
- Optional tools such as LibreOffice, Poppler, ImageMagick, and Tesseract improve validation or extraction but must not block generation.
