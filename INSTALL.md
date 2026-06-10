# Manual Installation

This project intentionally avoids automatic installation. Users must install runtime software, npm packages, browsers, and companion Skills manually before generating a final PPTX.

## Required software

Install these on your machine or runtime image:

- Python 3.10 or newer
- Node.js 20 or newer
- npm or pnpm
- Playwright Chromium, or another Chromium executable compatible with the exporter

Optional tools for stronger validation or repair:

- LibreOffice, exposed as `libreoffice` or `soffice`
- `zip` and `unzip`
- ImageMagick, exposed as `magick` or `convert`

## Install project npm dependencies

Use npm by default:

```bash
npm install
npx playwright install chromium
```

Use pnpm only when the workspace already uses pnpm or you explicitly prefer it:

```bash
pnpm install
pnpm exec playwright install chromium
```

## Install companion Skills manually

Companion Skills are not npm packages. Install them through the ChatGPT/Codex skill installation flow.

Recommended companion Skills:

- `frontend-slides`: visual design guidance for optional creative preview mode
- `dom-to-pptx`: package-specific DOM and CSS conversion guidance

The project must not try to install these Skills through scripts.

## Verify installation

Run the checker after manual installation:

```bash
python3 scripts/check_dependencies.py --cwd . --strict --json
```

The checker is read-only. It reports missing commands, missing local npm packages, missing optional tools, and missing companion Skills. It does not install or modify anything.

## Policy for missing dependencies

- Missing Python, Node.js, npm/pnpm, `dom-to-pptx`, `pptxgenjs`, or Playwright blocks final PPTX export.
- Missing `frontend-slides` does not block template direct mode.
- Missing `dom-to-pptx` companion Skill does not block export if the npm package is available.
- Missing optional tools should be reported as reduced validation or repair capability, not as a generation failure.
