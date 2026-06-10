# Style Profile Reuse

## Lookup Order

When a user names a style profile, search:

1. `.ppt-style-profiles/<profile-id>/profile.json` in the current project.
2. A user-specified profile path.
3. A workspace-level profile directory, if one is configured.

## Reuse Rules

- Reuse existing profiles by default.
- Do not re-extract a template if the user names an existing profile and does not provide a new template file.
- If both a profile ID and a new template are supplied, ask whether to refresh the existing profile or create a new one, unless the request clearly says refresh.
- If a profile is missing critical fields, refresh it from the original template if available.

## Naming Rules

Use stable lowercase hyphenated IDs:

```text
<organization-or-project>-<style-or-context>-<year>
```

Examples:

```text
bgi-research-2026
population-genomics-lab-2026
thesis-defense-minimal
```

## Profile-to-Deck Binding

Record the profile used for generation in the build output:

```json
{
  "style_profile_id": "bgi-research-2026",
  "style_profile_path": ".ppt-style-profiles/bgi-research-2026/profile.json",
  "mode": "template-direct"
}
```
