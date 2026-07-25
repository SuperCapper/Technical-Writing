# Source and Changes

**Source:** a four-part document ("a blueprint for a self-correcting, intelligent agent") describing a
Generate -> Evaluate -> Refine -> Orchestrate loop using the Six Thinking Hats framework as both a
generation-persona system and a multi-perspective evaluation ensemble. The source was read in full and is
not reproduced here; what follows is an honest account of what was kept, what was fixed, and what was added,
so nothing here is silently passed off as identical to the source.

## Kept, because it was genuinely good

- The core insight that a single LLM judging its own output is prone to sycophancy and confirmation bias,
  and that decomposing evaluation into independent, named cognitive lenses gives a traceable failure mode
  instead of a single opaque "quality" score.
- Assigning a specific persona/lens to the *Generate* stage, not just the *Evaluate* stage -- steering the
  draft toward a strategic intent up front, rather than only catching misalignment after the fact.
- The Blue Hat's diagnostic role: reading evaluation scores to find the *root cause* of a failure rather than
  issuing a generic "improve this" instruction.
- Preservation locking: explicitly telling a refinement pass which axes already passed and must not be
  touched, to prevent regression on already-good content.
- A convergence/improvement-delta heuristic and a hard iteration/cost budget, so the loop has a defined way
  to stop.

## Fixed -- real problems in the source, not stylistic preferences

1. **Black Hat's scoring direction contradicted its own calibration table.** The source's Section 4 anchor
   table defines Black Hat's scale as risk-ascending (1 = safe, 10 = catastrophic). Its own worked example in
   the Evaluation document then scores a risky output "Black Hat: 3/10" and vetoes it via `black.score (3) <
   threshold (7)` -- which only makes sense if the scale is quality-ascending (higher = safer). The source
   used both conventions in different places without reconciling them. Fixed: every hat in `hats/*.yaml`
   scores 1-10 quality-ascending, uniformly, including Black Hat (10 = safest). See `hats/black.yaml`.

2. **"Blue Hat" named three different things.** The source used "Blue Hat" for an evaluation lens (one of
   six scored axes), the Refine stage's diagnostic agent, and the entire Orchestration layer's executive
   state machine -- three distinct responsibilities sharing one name, with no signal in the text for which
   one a given sentence meant. Fixed: `hats/blue.yaml` is only the evaluation/generation/repair lens for
   organization and structure; the Diagnostic step and the Orchestrator are named and documented as separate,
   non-hat components in `README.md`'s Design Principles.

3. **`weight` and `pass_threshold`/veto were never reconciled.** The source's example YAML configuration
   attaches both a continuous `weight` (0.5-1.5) and a `pass_thresholds` map to the same hats, plus veto
   power for Black Hat, without specifying how a hat's weight interacts with its threshold, or whether a
   high-weight hat could offset a low-weight hat's failure. Fixed: `weight` feeds only the aggregate score
   used by the convergence check; `pass_threshold` and `veto` alone decide pass/fail, independent of weight.
   See `schemas/hat.schema.json`'s field descriptions.

4. **No cost tiering.** The source's evaluation stage always fires 6 separate LLM calls, and never
   considers a cheaper structured-output alternative or a pre-filter for deterministic properties. Fixed:
   `loop-config.schema.json`'s `evaluation.mode` (`single-structured-call` vs `per-hat-calls`) and
   `evaluation.pre_filter_output_constraints`, which reuses this repo's own `tools/guardrails.py` /
   `output_constraints` mechanism as a free first gate before any LLM ensemble call runs.

5. **Reward-hacking mitigation was a soft prompt, in a document whose entire thesis is that soft prompts
   aren't guardrails.** The source's fix for a model inflating its own score ("include a system instruction:
   do not apologize or admit fault") is exactly the failure mode the rest of the document argues against.
   Fixed: `reward_hacking_mitigations.cross_judge_sampling` in `loop-config.schema.json` -- periodically
   route the same output to a structurally different judge (different model family) instead of trusting an
   instruction to the same model that might be gaming its own evaluator.

6. **No security/trust boundary for re-injected content.** The source's Refinement and Orchestration stages
   both re-inject prior failed drafts and retrieved/RAG context into subsequent prompts, with no discussion
   of that content being untrusted. Fixed: called out explicitly in `README.md`'s Design Principles, with the
   same tag-boundary discipline this repo's own `skill.yaml` prompts already use for `{{ document }}`.

7. **No schema, no validator.** The source's "Implementation Blueprint" sections are YAML sketches with no
   formal schema and nothing to check a hat card or loop config for internal consistency (e.g. a
   `veto_hats` list drifting out of sync with which hat cards actually declare `veto: true`). Fixed:
   `schemas/hat.schema.json`, `schemas/loop-config.schema.json`, and `tools/validate_loop.py` -- mirroring the
   discipline `schemas/skill.schema.json` and `tests/validate_skills.py` already apply to `skills/*/skill.yaml`
   elsewhere in this repo.

8. **Hardcoded to `gpt-4o`.** Every example configuration in the source defaults to `gpt-4o` as both
   generator and judge model. Fixed: no hat card or schema hardcodes a model; `loop-config.example.yaml`
   leaves model selection as a per-loop configuration choice, consistent with how `tools/apply_skills.py`
   treats `model` as an optional per-skill override rather than a hardcoded constant.

## Restructured, not fixed

- **Four near-duplicated documents became one.** The source presents Generate, Evaluate, Refine, and
  Orchestrate as four separate deep-dives, each repeating the same "Concept Snapshot -> Deconstruction ->
  Deep-Dive Questions -> Implementation Blueprint -> Nuance & Conflict Map -> Real-World Example ->
  Cheat Sheet" scaffold, and restating the same cross-cutting ideas (Blue Hat's role, preservation locking,
  veto power) up to four times with minor variation. `README.md` states each cross-cutting idea once, in
  Design Principles, and gives each of the four stages a short, distinct description instead of a repeated
  seven-section template.
- **One worked example instead of four near-identical ones.** The source runs a "vanilla vs. technique"
  comparison in every one of its four documents, each involving the same kind of internal
  business-communication scenario. `README.md` keeps one worked example (a deployment-delay email) that
  demonstrates the full loop end to end, and references the source's own veto example only to show how the
  fixed scoring convention (change #1) applies to it.

## Not implemented (documented as out of scope, not silently dropped)

The source repeatedly gestures at production infrastructure -- a durable workflow engine (Temporal, AWS Step
Functions), a Postgres-backed state store, an FSM runtime, horizontal concurrency limits. None of that is
built here, deliberately: this repository's existing `tools/apply_skills.py` is itself a reference CLI, not
a production service, and `agent-loop/` is held to the same scope. `schemas/loop-config.schema.json`'s
`white_hat_archivist` section documents the *contract* a real state store would need to satisfy, without
implementing one.
