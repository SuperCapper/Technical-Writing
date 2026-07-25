# Example Use Case: Skeleton Architecture Applied to This Repo

This walks through one real, runnable use of this repo, framed using the "Skeleton Architecture" pattern
(InfoQ, "Skeleton Architecture" -- separating a rigid, human-owned **skeleton** from flexible, AI-authored
**tissue**, held together by hard guardrails rather than soft prompt instructions). The mapping isn't a
retrofit: this repo already had a skeleton/tissue split before the pattern had a name, which is exactly why
it plugs into the pattern cleanly.

## 1. The mapping

| Skeleton Architecture concept | This repo's equivalent |
|---|---|
| Rigid skeleton (interfaces, validators) | `schemas/skill.schema.json`, the fixed control flow inside `tools/apply_skills.py` |
| Flexible tissue (AI-authored business logic) | `skills/*/skill.yaml` -- each chapter's `system_prompt` / `user_prompt_template` |
| Template Method's `final run()` | `apply_skill()` in `tools/apply_skills.py`: every skill is rendered, (optionally) dry-run-printed, sent to Claude, and returned through the exact same sequence -- no skill can special-case its way around this |
| `protected _execute()` | The prompt content itself -- the only thing a skill author actually writes |
| Director role | The human running `apply_skills.py`, choosing which skill/pipeline to run, and reviewing output against the chapter's own checklist |
| Hard guardrails | `tests/validate_skills.py` (schema validation, example-rendering check) enforced in CI on every push; `--dry-run` as a pre-flight check before spending a token |
| Walking skeleton | How this repo was actually built: schema + one working skill + CLI proven end-to-end *first*, then 20 more tissue slices filled in against that same fixed skeleton |
| Vertical slices | One `skill.yaml` per book chapter/genre -- each isolated, each concerned only with its own transformation |
| Architecture drift | Would look like special-casing one skill inside `apply_skills.py` (e.g. `if skill["id"] == "genres.proposal": ...`) instead of changing the skill's YAML -- something this repo's structure makes awkward to do by accident |

The important discipline the article names: **prompts are soft, architecture is hard.** In this repo, that
means: if a skill's output is wrong, the fix is almost always to edit that skill's `user_prompt_template`
(tissue) -- not to add a special case to `apply_skills.py` (skeleton). The skeleton stays boring on purpose.

## 2. Worked example: the "Proposal Polish" pipeline

**Scenario:** Dana has a one-paragraph rough draft for new lab equipment and wants it turned into a proper
proposal -- structurally sound, mechanically clean, and with well-formed visuals -- by chaining three
chapters of the book together.

### Step 1 -- Compose the pipeline (tissue composition, not new skeleton code)

`composables/proposal-polish.yaml`:

```yaml
id: proposal-polish
name: "Proposal Polish"
version: "1.0.0"
description: >
  Takes a rough proposal draft through three chapters of the book in sequence: shape it as a proposal
  (Ch. 8), tighten its style and mechanics (Ch. 15), then check its visuals (Ch. 17). Order matters --
  structural fixes happen first so mechanical edits land on the final prose, not a draft that is about to
  be restructured.
steps:
  - skill_id: genres.proposal
    parameters:
      formality: informal
  - skill_id: style-support.style-mechanics
    parameters:
      strictness: moderate
  - skill_id: style-support.visuals
    parameters: {}
```

Notice this is pure data -- three `skill_id`s and their parameter overrides. Nothing in
`tools/apply_skills.py` changes to support a new pipeline. That's the skeleton/tissue boundary working as
intended: composing a new workflow is a tissue-level change, not a skeleton-level one.

### Step 2 -- Dry-run before spending a token

```bash
python tools/apply_skills.py --pipeline composables/proposal-polish.yaml \
    --input draft.md --output out.md --dry-run --verbose
```

Input (`draft.md`):

```
Problem: our lab's centrifuge is old.
Solution: buy a new one.
It costs a lot of money but it is very important.
```

This actually renders three fully-formed prompts (verified against the live repo):

- `genres.proposal` -- injects `formality=informal`, includes Outline 8.1's required elements (problem,
  scope, solution+benefits, credibility) and the instruction not to let the solution appear before the
  problem is established.
- `style-support.style-mechanics` -- injects `strictness=moderate`, instructs economy/precision edits and
  explicitly *not* to blanket-convert passive voice.
- `style-support.visuals` -- checks visual referencing, sequence numbering, and purpose.

`--dry-run` is the guardrail that lets Dana inspect exactly what will be sent to Claude, at zero API cost,
before committing real tokens -- the CLI-level analogue of a fail-fast validator.

### Step 3 -- The skeleton's real guardrail already ran, before Dana ever saw this repo

`tests/validate_skills.py` (run in CI on every push, via `.github/workflows/validate-skills.yml`) already
validated all 21 `skill.yaml` files against `schemas/skill.schema.json` and confirmed every example renders
without a template error. Dana never has to wonder whether `genres.proposal`'s YAML is well-formed --
that guarantee was enforced upstream, once, for every skill, not re-checked per use.

### Step 4 -- Run it for real

```bash
export ANTHROPIC_API_KEY=...
python tools/apply_skills.py --pipeline composables/proposal-polish.yaml \
    --input draft.md --output out.md
```

`run_pipeline()` threads the document through all three steps in order -- each skill's output becomes the
next skill's input -- and writes the final result to `out.md`.

### Step 5 -- Review against the tissue's own rubric, not the skeleton's

Dana checks the result against each chapter's own checklist (not something invented for this walkthrough --
it's copied straight from the book's end-of-chapter checklists into each skill's `README.md`):

- `skills/08-proposal/README.md`: problem defined in enough detail, scope stated, benefits tied back to the
  problem, credibility established.
- `skills/15-style-mechanics/README.md`: economy, precision, passive voice kept only where appropriate.
- `skills/17-visuals/README.md`: every visual referenced before it appears, numbered by type, purposeful.

If a checklist item is missed, that's a **tissue** problem: the fix is to sharpen that skill's
`user_prompt_template`, bump its `version` per `docs/contributing.md` (PATCH for prompt wording), and rerun
`tests/validate_skills.py`. The fix is never "patch `apply_skills.py` to handle proposals specially" --
that's the architecture-drift failure mode the article warns about, and this repo's structure makes it
awkward to do by accident.

### Step 6 -- A guardrail worth adding later (not implemented here)

The article's strongest claim is "hard guardrails, not soft prompts." One concrete candidate for this repo:
`skills/14-abstract-summary/skill.yaml` has a `word_limit` parameter, but nothing currently enforces it
except the prompt asking nicely. A real hard guardrail would check the *output's* word count in
`apply_skill()` (skeleton, one place) and fail fast if it's violated -- rather than trusting every skill
author to remember to ask nicely in every relevant prompt (tissue, 21 places). That single change would
apply uniformly to every skill with a `word_limit` parameter, present or future -- which is exactly the
leverage a skeleton is supposed to provide.

## 3. Why this holds together

This repo separates "what a chapter teaches" (tissue -- one YAML file, safely editable by anyone, validated
in isolation) from "how a document actually flows through the system" (skeleton -- one Python control flow,
one JSON Schema, one CI check, changed rarely and on purpose). Composing a new pipeline, like
`proposal-polish.yaml` above, only ever touches the tissue layer. That's the whole point: the skeleton stays
boring, so the tissue is free to grow.
