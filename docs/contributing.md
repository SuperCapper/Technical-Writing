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

## Output guardrails

Prompts are soft: a skill can ask for a word limit or a required section and still miss it. For anything
objective and cheap to check, declare a hard guardrail instead of trusting the prompt alone:

```yaml
parameters:
  word_limit:
    type: integer
    default: 250
output_constraints:
- type: max_words
  param: word_limit
```

`apply_skill()` checks every declared `output_constraints` entry against the model's real response (not
during `--dry-run`, since there's no real response yet) and calls `sys.exit(1)` with a clear message on the
first violation. In a pipeline this stops the chain immediately -- a violating output never reaches the next
step, and `--output` never gets written from a run that failed partway through.

Only `max_words` exists today (`tools/guardrails.py`'s `VALIDATORS` registry;
`skills/14-abstract-summary/skill.yaml` is the only skill using it so far). To add a new constraint type:
write a function in `guardrails.py` with the signature `(text, constraint, params) -> None` that raises
`GuardrailViolation` on failure, register it in `VALIDATORS`, and add its name to the `type` enum in
`schemas/skill.schema.json`. Keep every validator here deterministic -- string length, counts, regex -- since
it runs on every real invocation and can't afford to be a second, fallible LLM call checking the first one.
Whether the output actually satisfies the chapter's checklist is still a human's job (or a future
Claude-as-judge pass), not this module's.

`tests/validate_skills.py` cross-checks every `output_constraints[].param` against that skill's own declared
`parameters` (catching a typo like `word_limt` at CI time, not at runtime) and every `type` against
`guardrails.VALIDATORS`. `tests/test_guardrails.py` exercises the validators and the `--param`
type-coercion path directly against synthetic input -- no API key required, runs in CI on every push.

## Composables

A pipeline chains multiple skills in order (e.g. run `style-support.style-mechanics` after
`genres.proposal` so mechanical edits land last). Pipelines live under `composables/` as a YAML file with a
`steps` list of `{skill_id, parameters}`. See `composables/proposal-polish.yaml` for a working example, and
`docs/example-use-case.md` for a full walkthrough. Add a new pipeline once you have a real end-to-end use
case, rather than speculatively.

Pipelines only work for skills that transform a whole document into a revised whole document. Not every
skill in this repo is shaped that way -- see the next section before adding an Elements skill to a pipeline.

## Elements skills (Ch. 4-6) are scaffolding, not pipeline steps

`elements.technical-definition`, `elements.mechanism-description`, and `elements.process-description` teach
the building blocks a writer reaches for *while drafting* a genre document -- they are not, themselves, a
document type. That shows up directly in their `target_input`:

- `elements.technical-definition` takes a **term** (`target_input: text`) and returns a definition snippet --
  e.g. `"sample-separation protocol (needs a definition a non-technical funder can use)"` in,
  `"In [domain], a sample-separation protocol is..."` out. It is not shaped like a document revision at all.
- `elements.mechanism-description` and `elements.process-description` take a **stub** (`target_input:
  markdown`) and expand it into a full description -- document-shaped, but the input is a fragment meant to
  become a *section* of something larger, not a whole draft to be revised in place.

None of that fits the contract every pipeline step in `composables/*.yaml` assumes: whole document in, whole
document out, threaded straight into the next step. Forcing an Elements skill into that shape would need
new machinery this repo doesn't have -- something to find which terms/mechanisms/processes in a draft
actually need this treatment, and something to splice each result back into the right spot. Building that is
a real option (see the "marker-based splice" and "first-class schema support" options discussed in
`docs/example-use-case.md`), but it's real engineering, not a config change.

**Until then, the intended workflow is manual, and that's fine:**

1. Before assembling a draft, run each Elements skill standalone for anything that needs it:
   ```bash
   python tools/apply_skills.py --skill skills/04-technical-definition/skill.yaml \
       --input term.txt --output definition.txt
   python tools/apply_skills.py --skill skills/05-mechanism-description/skill.yaml \
       --input mechanism-stub.md --output mechanism-section.md
   ```
2. Paste the results into the draft by hand, wherever they belong.
3. Only then run the assembled draft through a `composables/*.yaml` pipeline (structure, style, visuals).

This matches how the book itself is organized -- Chapters 4-6 come *before* the genre chapters (7-14) as
techniques a writer already has in hand, not a stage a finished draft passes through afterward. Don't add an
Elements skill to a `composables/*.yaml` pipeline; use it standalone during drafting instead.
