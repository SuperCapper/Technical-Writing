# Foundations, Elements, and Style-support Merge

This documents the merge `agent-loop/README.md`'s "Future integration" section deferred: pulling
Foundations (`skills/01-03`), Elements (`skills/04-06`), and Style-support (`skills/15-18`) content into the
six hat cards' `source_skills` and their `evaluate_rubric`/`refine_strategy` instructions. Genres
(`skills/07-14`) and Workplace (`skills/19-21`) are still out of scope, per the original plan.

## The mapping

| Hat | Lens | Merged skill(s) | Why |
|---|---|---|---|
| White | facts | `elements.technical-definition`, `style-support.source-documentation`, `style-support.style-mechanics` | A circular/imprecise definition, an uncited claim, and an available-but-unquantified figure are all grounding failures of the same kind as a fabricated fact -- White Hat already asks "is this actually true and traceable," and these three failure modes are just specific instances of that question. |
| Black | risk | `foundations.ethics-check`, `foundations.note-taking-triage` | Ethics-check's hazard list (undisclosed alteration, plagiarism, misleading data, suppressed contrary facts) and note-taking's safety/ownership flags are risk categories in the literal sense Black Hat already exists to veto on. |
| Red | feelings | `foundations.reduce-abstraction` | A stretch, and named as one: audience-familiarity calibration isn't itself an emotion, but "is this pitched at a level this specific reader can use" is close enough to "how will this land for this reader" that it fits Red's lens better than any other, and nowhere else in the six hats has a natural home for it. |
| Blue | process | `elements.mechanism-description`, `elements.process-description`, `style-support.visuals`, `style-support.presentations` | All four are organizational/structural teaching -- exactly Blue's lens. Four skills feeding one hat is not a stretch; Blue Hat's job was always "does the structure make sense," and these are four instances of "what does correct structure look like" for four different content shapes. |
| Yellow | value | *(none)* | No genuine match. Persuasion and benefit-communication live in the book's Genres/Workplace chapters (proposals, business communication), which are out of scope here. Forcing a match would mean inventing content this merge didn't actually derive from the book. |
| Green | creativity | *(none)* | No genuine match, and for a stronger reason than Yellow's: the book's own Chapter 1 explicitly defines technical writing *against* creative writing ("Technical writing is not what one does out in the meadow under an elm tree; that is creative writing... Technical writing is the opposite of artistic"). A book whose own thesis excludes creative writing has nothing to teach Green Hat. This is a real finding of the merge, not a gap in it. |

Leaving Yellow and Green unmerged, explicitly and with a stated reason (see their `hats/yellow.yaml` and
`hats/green.yaml` `description` fields and changelogs), was a deliberate choice over quietly stretching a
weak connection to make all six hats look equally complete.

## The granularity mismatch, and how it was actually resolved

`agent-loop/README.md` flagged this before the merge happened: Elements skills aren't uniformly
document-shaped. `elements.mechanism-description` and `elements.process-description` are (`target_input:
markdown`, stub -> full section) -- they merge cleanly into all three of a hat's roles.
`elements.technical-definition` is not (`target_input: text`, term -> definition snippet) -- it doesn't fit
a hat's `generate_persona`, because there's no sensible way to draft an entire document "as a definition."

The resolution, visible in `hats/white.yaml`'s changelog: **span-shaped Elements content merges only into
`evaluate_rubric` and `refine_strategy`, never into `generate_persona`.** An evaluator scanning a whole draft
can absolutely apply a term-level check ("does any term defined inline in this draft use Classification +
Differentiation without circularity") without the draft itself needing to be shaped like a definition. A
refine strategy can target a single flawed sentence for a Classification + Differentiation rewrite without
touching the rest of the document, exactly the way `preservation_lock` already works for every other
targeted repair. Generation is where the shape mismatch actually bites, so generation is where nothing was
forced. This solves the granularity problem the same way once, for the one span-shaped skill in this merge,
rather than needing a different `composables/`-style special case for each future span-shaped skill that
gets merged in.

## What changed, concretely

- `hats/white.yaml`: 1.0.0 -> 1.1.0. `evaluate_rubric` and `refine_strategy` gained the three checks above;
  `generate_persona` untouched.
- `hats/black.yaml`: 1.0.0 -> 1.1.0. `evaluate_rubric` and `refine_strategy` gained the ethics/note-taking
  hazard list; `generate_persona` untouched.
- `hats/red.yaml`: 1.0.0 -> 1.1.0. `evaluate_rubric` and `refine_strategy` gained audience-calibration
  scoring/repair alongside pure tone; `generate_persona` untouched.
- `hats/blue.yaml`: 1.0.0 -> 1.1.0. All three roles (`generate_persona`, `evaluate_rubric`,
  `refine_strategy`) now branch on which of four structural patterns (mechanism, process, visuals,
  presentation) the content actually calls for, instead of one generic "is this organized" check.
- `hats/yellow.yaml`, `hats/green.yaml`: 1.0.0 -> 1.0.1. No prompt content changed; the decision to leave
  them unmerged is now documented in-file rather than left implicit.
- `tools/validate_loop.py`: now cross-checks every hat's `source_skills` against the real skill ids under
  `skills/*/skill.yaml`, so a typo'd cross-reference fails in CI instead of sitting as unchecked
  documentation forever.

## What's still not done

Genres (`skills/07-14`: proposals, reports, abstracts) and Workplace (`skills/19-21`: business
communication, job applications, team writing) remain unmerged -- always out of scope for this pass, not a
follow-on TODO implied by it. If a future task wants Yellow Hat to have real content, that's where it would
come from, and it would be a new, separately-scoped merge, not an extension of this one.
