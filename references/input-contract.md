# Input Contract

## Accepted inputs

The skill can work from any combination of:

- PPT/PPTX template for style extraction.
- Existing style profile ID under `.ppt-style-profiles/`.
- Outline, manuscript, report text, paper sections, meeting notes, or structured content.
- Style guide text or institutional brand instructions.
- Required images, logos, tables, formulas, citations, and speaker/date/affiliation metadata.

## Minimum information for final deck generation

If missing, infer conservatively and state assumptions:

- Deck purpose.
- Audience.
- Language.
- Approximate slide count or density preference.
- Source content or outline.
- Style profile or template.
- Final output scope: PPTX only, or PPTX plus HTML/report files.

## Mandatory preservation

Preserve exactly:

- Names and institutional branding.
- Dates, sample sizes, numbers, units, p-values, equations, and references.
- User-provided titles and quotes unless asked to rewrite.
- Required language and terminology.
- Template constraints extracted into the style profile.

## Normalized input summary

Before full generation, summarize the task in this form:

```text
Mode: template-direct | creative-preview | profile-only | validate-repair
Style profile: <profile-id or new>
Template source: <file or none>
Deck purpose: <purpose>
Audience: <audience>
Language: <language>
Slide count: <count or flexible>
Inputs: <outline/content/assets>
Output: editable PPTX
```
