# Contributing

Every skill in this repository traces back to one chapter of *Technical Writing for Engineers and
Scientists* (ISE). The book's content is primary; the skill format is just structure layered on top so the
book's guidance can be applied programmatically to real drafts via Claude.

## Adding or editing a skill

1. Re-read the relevant chapter before changing its skill. If the change isn't traceable to something the
   chapter actually says, it probably belongs in `skills/experimental/` instead (create that folder if you
   start one), not in an existing chapter's skill.
2. Skills live at `skills/<NN>-<slug>/skill.yaml`, one folder per chapter, numbered to match the book's
   table of contents.
3. Every skill must validate against `schemas/skill.schema.json` and include at least one worked example.
   Run `python tests/validate_skills.py` before committing.
4. Bump `version` per semver: PATCH for prompt wording tweaks, MINOR for new parameters, MAJOR for changes
   that would change existing pipeline output in a breaking way.
5. Update the skill's own `README.md` (checklist + usage) alongside `skill.yaml` -- keep them in sync.
6. Update the table in the top-level `README.md` if you add, rename, or remove a skill.

## Testing a skill by hand

```bash
python tools/apply_skills.py --skill skills/07-instructions/skill.yaml \
    --input draft.md --output revised.md --dry-run --verbose
```

`--dry-run` prints the rendered system/user prompts without calling the API, so you can sanity-check a
prompt change before spending a token on it.

## Composables

A pipeline chains multiple skills in order (e.g. run `style-support.style-mechanics` after
`genres.proposal` so mechanical edits land last). Pipelines live under `composables/` as a YAML file with a
`steps` list of `{skill_id, parameters}`. There is no pipeline in the repo yet -- add one under
`composables/` once you have a real end-to-end use case, rather than speculatively.
