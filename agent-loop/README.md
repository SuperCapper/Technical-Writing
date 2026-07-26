# Agent Loop: A Self-Correcting Generation Architecture

A reference architecture for a Generate -> Evaluate -> Refine -> Orchestrate loop, using six cognitive
lenses ("hats," after the Six Thinking Hats framework) to draft, critique, and repair AI-generated output
without a single evaluator's blind spots deciding everything.

This is an independent addition to the repository, not derived from *Technical Writing for Engineers and
Scientists*. It started from a source document (see `docs/source-and-changes.md` for exactly what changed
and why) and has been substantially reworked: several internal contradictions in the source are fixed, the
four originally near-duplicated stage write-ups are unified into one document, and a few real gaps
(cost-tiered evaluation, a schema, a validator, a security note) are filled in that the source never
addressed.

Like `skills/` and `tools/apply_skills.py`, this is a **reference implementation**, not a production
service: `tools/run_loop.py` actually runs the loop end to end against the real Claude API, but there is no
durable execution engine, persistent state store surviving a process restart, or horizontal concurrency --
see `schemas/loop-config.schema.json`'s `white_hat_archivist` section for the contract a production
implementation would need to satisfy beyond what a single JSON transcript file provides here. Treat
`tools/validate_loop.py` the way you'd treat `tests/validate_skills.py`: it validates the *configuration*
files (hat cards, loop configs), separately from whether a live run of `run_loop.py` behaves correctly (see
`tests/test_orchestrator.py` and `tests/test_run_loop.py` for that, both API-free).

## Running it

```bash
python agent-loop/tools/run_loop.py \
    --loop-config agent-loop/loop-config.example.yaml \
    --task agent-loop/tasks/deployment-delay-email.yaml \
    --transcript-out transcript.json \
    --dry-run --verbose   # drop --dry-run to actually call Claude (needs ANTHROPIC_API_KEY)
```

`--dry-run` prints the Generate and Evaluate prompts for the first iteration and stops -- it can't preview
Refine, since there are no real scores yet to diagnose against. A real run writes a full transcript (every
draft, every hat's score and justification, every diagnosis, the final status) to `--transcript-out`.

`tools/orchestrator.py` holds every decision that must be deterministic, not LLM-judged: which hats failed,
whether a veto fired, the convergence aggregate, and -- going one step further than the source material --
*which axis gets repaired next*. That last one matters: the Diagnostic step in `run_loop.py` still makes an
LLM call, but only to explain *why* the orchestrator's already-chosen axis failed, never to choose which
axis. `tests/test_orchestrator.py` exercises all of this with synthetic scores, no API key required.

## The four stages, briefly

1. **Generate** -- produce a draft by explicitly assigning it a cognitive lens (a hat's `generate_persona`),
   rather than letting the model default to a generic, statistically-average voice. A risk audit should be
   drafted by something wearing the Black Hat; a customer email, the Red Hat.
2. **Evaluate** -- score the draft across all six lenses at once (a hat's `evaluate_rubric`), so a
   confident-sounding but wrong or risky draft can't talk its way past a single judge that's easily
   persuaded by fluent prose.
3. **Refine** -- the Diagnostic step (see below) reads all six scores, identifies the one axis that
   actually failed, and deploys *only* that hat's `refine_strategy` -- locking every already-passing axis so
   the repair can't quietly break something that was fine.
4. **Orchestrate** -- the fixed control logic (budget, veto enforcement, convergence check, escalation)
   that runs the other three stages in a loop and knows when to stop.

## Design Principles

These apply across all four stages; the source document restated variations of most of them four times, once
per stage. Stated once, here:

**"Blue Hat" is three different things in the source material; here it's one.** The source used "Blue Hat"
to mean an evaluation lens, the Refine stage's diagnostician, *and* the entire Orchestration layer's
executive -- three jobs, one name, real ambiguity about which one a given sentence meant. Here:
- `hats/blue.yaml` is a hat like the other five -- it scores/generates/repairs *organization and structure*,
  nothing more.
- **The Diagnostic step** is a fixed prompt owned by the Orchestrator, not a hat card, because it doesn't
  generate or repair content itself -- it reads all six scores and the failed draft and returns which axis
  failed and why. It is not swappable per use case the way a hat is.
- **The Orchestrator** is the control-flow component (budget, veto, convergence, escalation) that calls the
  other three stages. It is code, not a persona, and should never be prompted as if it were one.

**Veto is a hard guardrail, not a Blue Hat's judgment call.** The source's escalation logic (`if:
black.score < 7 -> Hard Reject`) is exactly the "hard guardrails, not soft prompts" principle this repo's
`tools/guardrails.py` already applies to skill output: whether a veto fires must be a deterministic
`if score < threshold` in the Orchestrator's code, never a instruction asking an LLM to "remember to veto
if things look risky." An LLM that forgets to enforce its own veto instruction has produced exactly the
failure mode this whole architecture exists to prevent.

**Every hat scores quality-ascending.** The source's own worked example scores the Black Hat backwards from
its own calibration table: the anchor table defines 1 = safe, 10 = catastrophic, but the worked example
then vetoes on `black.score (3) < threshold (7)` -- treating 3 as a *failing* score, which only makes sense
if higher is better. Every hat card here (`hats/*.yaml`) scores 1-10 with 10 always meaning "this hat is
fully satisfied," including Black Hat (10 = safe). `pass_threshold` and veto logic are uniform across every
hat as a result -- no per-hat exception to remember.

**Weight and threshold do different jobs; the source conflated them.** A hat's `weight` (in `hats/*.yaml`)
feeds only the aggregate score the convergence check tracks across iterations -- it never decides pass/fail.
`pass_threshold` and `veto` decide pass/fail, independent of weight. This means a low-weight hat (Green,
weight 0.5) can never accidentally get vetoed just because its raw score is low but unimportant, and a
high-weight hat can't buy its way past a threshold it failed by being "important."

**Preservation locking is what makes refinement monotonic.** Every `refine_strategy` instructs the model to
touch *only* the flagged axis and leave everything the Diagnostic step marked as already-passing untouched.
Without this, refinement is just regeneration with extra steps -- fixing tone by rewriting the whole draft
risks reintroducing the fact error that was already fixed.

**Check cheap and deterministic things before spending an LLM ensemble call.** `loop-config`'s
`evaluation.pre_filter_output_constraints` runs a skill's `output_constraints` (word counts, required
sections -- see `skills/schemas/skill.schema.json` and `tools/guardrails.py`) *before* the six-hat ensemble
runs at all. The source's design always ran all six hats regardless; that's paying for six LLM calls to
discover a word-count violation `len(text.split())` would have caught for free.

**Tier the ensemble call itself.** The source calls for 6 separate LLM calls per evaluation pass with no
cheaper option. `evaluation.mode: single-structured-call` (the default in `loop-config.example.yaml`) asks
for all six scores in one structured-output call; reserve `per-hat-calls` for when a specific hat's rubric
is complex enough to need its own full context window.

**Reward-hacking mitigation must be structural, not a polite request.** The source's mitigation for a model
"apologizing" to inflate its own tone score was a system instruction asking it not to. That's a soft prompt
defending against exactly the failure mode this architecture exists to catch with hard checks instead. Use
`reward_hacking_mitigations.cross_judge_sampling` -- periodically route the same output to a judge from a
*different model family* than the generator, so evaluator and generator can't share the same blind spot.

**Treat prior failed drafts and retrieved context as untrusted input, not instructions.** The source never
raises this: a refinement prompt that re-injects the previous (failed) draft and any retrieved/RAG context
is feeding untrusted content back into the model's context window on every iteration. That content should be
handled the way this repo's `skill.yaml` prompts already wrap `{{ document }}` in an explicit tag boundary
-- never concatenated in a way that lets it read as system instructions.

## Worked example

**Task:** an internal email announcing a Q3 deployment delay, for an engineering audience.

1. **Generate:** the Orchestrator selects Red (empathy) + Black (transparency about risk) as the generation
   lenses, per the task's intent ("manage morale while being honest about risk"). The draft acknowledges the
   team's effort, names the specific blocker (an Auth0 migration dependency), and proposes a concrete next
   step.
2. **Evaluate (single-structured-call):** White 8 (the blocker is accurately described), Yellow 7, Black 9
   (no unsupported claims, no omitted risk), Red 9, Green 5, Blue 8. `pre_filter_output_constraints` already
   passed (no word-limit skill attached to this task).
3. **Orchestrator decision:** every hat clears its `pass_threshold`; Black (veto hat) clears comfortably.
   Aggregate score is within `convergence.improvement_delta_threshold` of "done." **Accept, no refinement
   needed.**

Contrast with the source's own worked example for the *evaluation-only* case (a marketing email claiming
"perfectly manage your calendar" when the product only supports Google Calendar): White 8, Yellow 9, **Black
3** (deceptive claim, real reputational risk), Red 8, Green 5. Black's raw score of 3 is below its
`pass_threshold` of 7 -- the Orchestrator's veto check fires (a deterministic `if`, not a hope that the Blue
Hat remembers), execution moves to Refine, and the Diagnostic step routes to White+Black's `refine_strategy`
to correct the claim before the email ever ships.

This exact scenario is `tasks/deployment-delay-email.yaml` -- run it for real (see "Running it" above) to
get an actual transcript instead of the hypothetical scores above. `tasks/short-status-update.yaml` is a
second, shorter task that exercises the `pre_filter_output_constraints` path with a 40-word limit.

## Repository structure

```
agent-loop/
├── README.md                          # this file
├── loop-config.example.yaml           # one worked orchestrator config, all six hats
├── schemas/
│   ├── hat.schema.json                # format every hats/*.yaml must satisfy
│   └── loop-config.schema.json        # format every *loop-config*.yaml must satisfy
├── hats/
│   ├── white.yaml   (facts)
│   ├── yellow.yaml  (value)
│   ├── black.yaml   (risk -- veto hat)
│   ├── red.yaml     (feelings)
│   ├── green.yaml   (creativity)
│   └── blue.yaml    (process)
├── tasks/
│   ├── deployment-delay-email.yaml     # the worked example above, runnable
│   └── short-status-update.yaml        # exercises pre_filter_output_constraints (a 40-word limit)
├── tools/
│   ├── run_loop.py                     # the reference CLI: actually runs Generate->Evaluate->Refine->stop
│   ├── orchestrator.py                 # deterministic decisions only -- no LLM calls, unit-testable
│   └── validate_loop.py                # schema + cross-reference validator, mirrors tests/validate_skills.py
├── tests/
│   ├── test_orchestrator.py            # unit tests for orchestrator.py, no API key needed
│   └── test_run_loop.py                # prompt-rendering + pre-filter wiring checks, no API key needed
└── docs/
    └── source-and-changes.md          # exactly what was fixed/added vs. the original source document
```

## Foundations, Elements, and Style-support merge (done)

Foundations (`skills/01-03`), Elements (`skills/04-06`), and Style-support (`skills/15-18`) content is now
merged into four of the six hat cards' `source_skills`, `evaluate_rubric`, and `refine_strategy`:

- **White Hat** (facts) ← `elements.technical-definition`, `style-support.source-documentation`,
  `style-support.style-mechanics` (precision half).
- **Black Hat** (risk) ← `foundations.ethics-check`, `foundations.note-taking-triage`.
- **Red Hat** (feelings) ← `foundations.reduce-abstraction` (audience calibration).
- **Blue Hat** (process) ← `elements.mechanism-description`, `elements.process-description`,
  `style-support.visuals`, `style-support.presentations`.
- **Yellow and Green Hats** were left explicitly unmerged -- neither has a genuine match among these 10
  chapters, and forcing one would mean inventing content this merge didn't actually derive from the book.

See `docs/foundations-elements-style-merge.md` for the full rationale per hat, and for how the granularity
mismatch flagged above (span-shaped `elements.technical-definition` vs. document-shaped everything else) was
actually resolved: span-shaped content merges only into `evaluate_rubric`/`refine_strategy`, never into
`generate_persona`, since there's no sensible way to draft a whole document "as a definition."

Genres (`skills/07-14`) and Workplace (`skills/19-21`) remain unmerged, per the original scope -- not a
follow-on TODO this merge implies, a separate decision for later.
