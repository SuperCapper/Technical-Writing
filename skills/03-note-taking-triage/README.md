# 3. Note-taking

Skill ID: `foundations.note-taking-triage`

Reorganizes raw, real-time notes into the Cornell format (cues, notes, summary) and flags any recorded content that carries legal, ethical, or ownership implications the book warns about -- since notes are discoverable in litigation, may belong to an employer rather than the note-taker, and never truly disappear.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 3 -- Note-taking.

## Checklist

- [ ] Should these notes even be taken, and in what format?
- [ ] What note-taking method fits this situation: outline, mapping, sketch-noting, or Cornell?
- [ ] Will these notes be the property of my employer, or are they personal?
- [ ] How will these notes be stored, maintained, and disseminated?
- [ ] Have I captured full source/citation information (site, author, date, page) as I went, not after the fact?
- [ ] Have I considered that anything I record digitally may be permanent and discoverable?

## Usage

```bash
python tools/apply_skills.py --skill skills/03-note-taking-triage/skill.yaml --input draft.md --output revised.md
```
