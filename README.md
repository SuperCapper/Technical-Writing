# Technical-Writing

A repository of reusable Claude skills distilled from *Technical Writing for Engineers and Scientists*
(ISE). Each skill packages one chapter's teaching -- its structure, its checklist, its worked examples --
into a self-contained instruction set that can draft, review, or revise a real document with Claude.

The book's content is primary. The `skill.yaml` format (see `schemas/skill.schema.json`) is only the
structure used to make that content composable and testable; nothing in a skill file should say anything
the book doesn't actually teach.

## How this works

Every skill is a YAML file conforming to `schemas/skill.schema.json`:

| Field | Purpose |
|---|---|
| `id` | `category.skill-name`, e.g. `genres.proposal` |
| `system_prompt` / `user_prompt_template` | The instructions sent to Claude, grounded in the chapter's method |
| `checklist` | The book's own end-of-chapter checklist -- usable as prompt content or as a review rubric |
| `examples` | At least one worked input/output pair, adapted from or in the spirit of the book's own examples |
| `source` | Which book and chapter this skill comes from |

Run a skill against a draft:

```bash
python -m venv .venv && .venv/Scripts/activate  # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
python tools/apply_skills.py --skill skills/07-instructions/skill.yaml \
    --input draft.md --output revised.md --dry-run   # drop --dry-run to actually call Claude
```

Validate the whole catalog (schema + renderability of every example):

```bash
python tests/validate_skills.py
```

Prefer chat over the terminal? [docs/running-via-claude-code.md](docs/running-via-claude-code.md) has
copy-pasteable prompts for running Genres skills, Workplace skills, and the Agent Loop from Claude Code's
chat panel in VS Code, including how to toggle between all three without retyping the setup each time.

## Skill catalog

### Foundations -- what technical writing is and how it's governed

| # | Skill | ID | What it does |
|---|---|---|---|
| 1 | [Reduce Abstraction](skills/01-reduce-abstraction) | `foundations.reduce-abstraction` | Rewrites abstract prose at the lowest level of abstraction the stated audience can use, per the book's "funnel of abstraction." |
| 2 | [Ethics Check](skills/02-ethics-check) | `foundations.ethics-check` | Flags undisclosed image alteration, uncredited ideas, fabricated/misleading data, and social-media-unsafe content -- for human judgment, since ethics is about intent, not just rule-following. |
| 3 | [Note-taking Triage](skills/03-note-taking-triage) | `foundations.note-taking-triage` | Reorganizes raw notes into Cornell format and flags legal/ethical/ownership issues (discoverability, employer ownership, permanence). |

### Elements -- the building blocks of technical explanation

| # | Skill | ID | What it does |
|---|---|---|---|
| 4 | [Technical Definition](skills/04-technical-definition) | `elements.technical-definition` | Builds definitions as `(Qualifier +) Term = Classification + Differentiation`, eliminating circularity. |
| 5 | [Mechanism Description](skills/05-mechanism-description) | `elements.mechanism-description` | Describes a mechanism's static parts and each part's function, per Outline 5.1. |
| 6 | [Process Description](skills/06-process-description) | `elements.process-description` | Describes a time-ordered process step by step, with transitions and explicit branching. |

### Genres -- the document types engineers and scientists actually write

| # | Skill | ID | What it does |
|---|---|---|---|
| 7 | [Instructions](skills/07-instructions) | `genres.instructions` | Step-by-step instructions calibrated to a stated audience skill level, per Outline 7.1. |
| 8 | [Proposal](skills/08-proposal) | `genres.proposal` | Problem-first formal/informal proposals with scope, benefits, and credibility. |
| 9 | [Progress Report](skills/09-progress-report) | `genres.progress-report` | Status against an already-accepted proposal, with honest appraisal and forecast. |
| 10 | [Feasibility & Recommendation Report](skills/10-feasibility-recommendation-report) | `genres.feasibility-recommendation-report` | Weighted, criteria-based comparison of options, optionally ending in a recommendation. |
| 11 | [Lab & Project Report](skills/11-lab-project-report) | `genres.lab-project-report` | Apparatus, procedure, results (kept separate from interpretation), conclusion, recommendation. |
| 12 | [Research Report](skills/12-research-report) | `genres.research-report` | Synthesizes and documents sources rather than stringing quotations. |
| 13 | [A3 Report](skills/13-a3-report) | `genres.a3-report` | One-page Lean problem-solving report; forces root-cause analysis before an action plan. |
| 14 | [Abstract & Summary](skills/14-abstract-summary) | `genres.abstract-summary` | Descriptive/informative abstracts and academic/executive summaries, each to spec. |

### Style & Support -- the cross-cutting craft

| # | Skill | ID | What it does |
|---|---|---|---|
| 15 | [Style & Mechanics](skills/15-style-mechanics) | `style-support.style-mechanics` | Enforces economy and precision; fixes mechanics; keeps passive voice only where it's actually appropriate. |
| 16 | [Source Documentation](skills/16-source-documentation) | `style-support.source-documentation` | Flags uncited material and formats citations to a specified style guide. |
| 17 | [Visuals](skills/17-visuals) | `style-support.visuals` | Checks every visual is referenced before it appears, numbered by type, and purposeful. |
| 18 | [Presentations](skills/18-presentations) | `style-support.presentations` | Structures slides into title/overview/discussion/summary, matched to speaking purpose. |

### Workplace -- communicating with people, not just documents

| # | Skill | ID | What it does |
|---|---|---|---|
| 19 | [Business Communication](skills/19-business-communication) | `workplace.business-communication` | Formats email/memo/letter correctly -- and knows when NOT to write at all. |
| 20 | [Job Application Materials](skills/20-job-application-materials) | `workplace.job-application-materials` | Resumes led by relevance; cover letters backed by specific examples, never a resume restated. |
| 21 | [Team Writing](skills/21-team-writing) | `workplace.team-writing` | Runs the requirements / preliminary-actions / document-production phases, professional or student. |

## Repository structure

```
Technical-Writing/
├── README.md
├── requirements.txt
├── schemas/
│   └── skill.schema.json       # JSON Schema every skill.yaml must satisfy
├── skills/
│   └── NN-slug/
│       ├── skill.yaml          # the skill itself
│       └── README.md           # chapter checklist + usage snippet
├── tests/
│   └── validate_skills.py      # schema validation + example-rendering check
├── tools/
│   └── apply_skills.py         # reference CLI: skill(s) + document -> Claude -> revised document
├── composables/
│   └── proposal-polish.yaml    # a working example pipeline chaining several skills
├── docs/
│   ├── contributing.md
│   ├── example-use-case.md
│   └── running-via-claude-code.md
├── agent-loop/                 # independent addition -- not derived from the book, see its own README
│   ├── README.md
│   ├── loop-config.example.yaml
│   ├── schemas/
│   ├── hats/
│   ├── tasks/                  # runnable example task briefs
│   ├── tools/                  # run_loop.py (reference CLI) + orchestrator.py + validate_loop.py
│   ├── tests/
│   └── docs/
└── .github/workflows/
    └── validate-skills.yml     # CI: runs tests/validate_skills.py on push/PR
```

## Contributing

See [docs/contributing.md](docs/contributing.md). In short: every skill must trace back to something its
source chapter actually teaches, must validate against the schema, and must include a worked example.

## Example use case

[docs/example-use-case.md](docs/example-use-case.md) walks through a real, runnable pipeline
(`composables/proposal-polish.yaml`) end to end, framed against the "Skeleton Architecture" pattern
(rigid, human-owned skeleton vs. flexible, AI-authored tissue) -- see that doc for how the schema, CLI, and
CI in this repo already play the "skeleton" role, with each `skill.yaml` as a "tissue" vertical slice.

## Agent Loop (independent addition)

[agent-loop/](agent-loop/README.md) is a self-contained, **runnable** reference implementation of a Generate
-> Evaluate -> Refine -> Orchestrate self-correcting loop, using six cognitive lenses ("hats") to draft,
critique, and repair output -- `agent-loop/tools/run_loop.py` actually executes it against the real Claude
API. It is **not** derived from the book -- see `agent-loop/docs/source-and-changes.md` for its own source
and the concrete fixes made to it. The plan is to eventually merge Foundations, Elements, and Style-support
content into it as concrete instructions behind specific hats (see that doc's "Future integration" section)
-- not done yet, and the two parts of this repo remain independent until then.
