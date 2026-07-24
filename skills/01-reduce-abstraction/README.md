# 1. Introduction

Skill ID: `foundations.reduce-abstraction`

Rewrites overly abstract technical prose at the lowest level of abstraction the target audience can still understand, following the book's 'funnel of abstraction' model. Flags terms whose meaning is not pinned down for the stated audience, purpose, and context.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 1 -- Introduction.

## Checklist

- [ ] Have I identified how much my audience already knows about the topic?
- [ ] Have I calibrated the level of abstraction to the lowest level the audience can understand?
- [ ] Have I stated (or flagged as missing) the purpose: inform, persuade, or build goodwill?
- [ ] Have I considered situational context (history, culture, politics, company norms) outside my control?
- [ ] Have I chosen the technical-writing genre appropriate to this audience, purpose, and context?
- [ ] Does the writing stay non-abstract, precise, and free of rich metaphor or figurative language?

## Usage

```bash
python tools/apply_skills.py --skill skills/01-reduce-abstraction/skill.yaml --input draft.md --output revised.md
```
