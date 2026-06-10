# Generation Modes

## Mode selection

Default to `template-direct` unless the user clearly asks for creative exploration.

Use `template-direct` when:

- The user specifies a template style profile.
- The user asks to follow, match, imitate, or preserve a template.
- The user prioritizes speed or final PPTX generation.
- The request has no explicit preview or style comparison requirement.

Use `creative-preview` when:

- The user says they want innovation, options, preview, exploration, or comparison.
- The user asks for three design directions.
- The template is a reference rather than a strict style requirement.
- The user wants `frontend-slides`-like visual exploration.

Use `profile-only` when:

- The user only wants template analysis or reusable style extraction.

Use `validate-repair` when:

- The user provides an existing PPTX and asks to inspect, validate, or repair it.

## Template direct mode

Purpose: generate a deck that faithfully follows a specified reusable style profile.

Steps:

1. Load `profile.json`, `style-guide.md`, and `master-summary.md`.
2. Generate slide plan from outline and content.
3. Map each slide to a known layout family: cover, section, content, comparison, table, formula, summary.
4. Write full `deck.html` directly.
5. Export to PPTX and validate.

Do not generate three previews unless the user requests them.

## Creative preview mode

Purpose: combine template constraints with creative visual exploration.

Steps:

1. Load the style profile as non-negotiable constraints.
2. Use `frontend-slides` design reasoning to create exactly three first-slide HTML previews.
3. Each preview must use real deck content, not placeholders.
4. Do not put labels such as "Option A", "Preview", or "Generated" inside the slide canvas.
5. Wait for user selection or mix instruction.
6. Generate the full deck using the selected direction.

At least one preview may be bolder, but all previews must remain compatible with `dom-to-pptx` export.
