# 13. A3 Reports

Skill ID: `genres.a3-report`

Drafts or reviews a Lean A3 problem-solving report: a single-page document telling the whole story from problem through root cause to action plan, avoiding the common failure modes the book warns against (no visuals, no assignments/due dates, over-polishing, or skipping root-cause analysis).

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 13 -- A3 Reports.

## Checklist

- [ ] Who is the audience and how will they use this A3?
- [ ] What is the situational context of the problem?
- [ ] Have I stated the current condition with data rather than impressions?
- [ ] Have I identified the root cause, not just the first symptom noticed?
- [ ] Does the action plan include named owners and due dates, plus a follow-up/check step?
- [ ] Does the whole document fit on one page and use visuals to tell the story?
- [ ] Have I avoided over-polishing at the expense of shipping a useful working document?

## Usage

```bash
python tools/apply_skills.py --skill skills/13-a3-report/skill.yaml --input draft.md --output revised.md
```
