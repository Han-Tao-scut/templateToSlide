# Template to Slide

`template-to-slide` is a ChatGPT Skill for extracting reusable style profiles from PPT/PPTX templates and generating native editable PPTX decks from those profiles, outlines, and content.

## Core idea

1. Extract a reusable template style profile.
2. Reuse that profile for future decks.
3. Generate `dom-to-pptx` compatible HTML.
4. Convert HTML to editable PPTX.
5. Validate the PPTX package before delivery.

## Modes

- **Template direct mode**: default. Follow a specified style profile and generate the deck directly.
- **Creative preview mode**: optional. Combine the profile with `frontend-slides` design guidance and generate three first-slide previews before full deck generation.
- **Profile-only mode**: extract and save style information for reuse.
- **Validate/repair mode**: inspect a PPTX package and report structural problems.

## Setup

```bash
python3 scripts/check_dependencies.py --cwd . --json
python3 scripts/setup_environment.py --cwd .
python3 scripts/check_dependencies.py --cwd . --strict --json
```

## Extract a profile

```bash
python3 scripts/extract_template_style.py input/template.pptx --profile-id my-template
```

## Validate a PPTX

```bash
python3 scripts/validate_pptx.py build/deck.pptx --expected-slides 12 --json
```
