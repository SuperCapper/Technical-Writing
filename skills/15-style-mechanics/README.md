# 15. Style and Mechanics

Skill ID: `style-support.style-mechanics`

Edits prose for the two pillars of technical style the book teaches -- economy (say it in the fewest words) and precision (no vague quantifiers) -- and corrects mechanical errors: misplaced modifiers, comma splices, sentence fragments, and unjustified passive voice, while allowing passive voice where the book says it is actually appropriate.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 15 -- Style and Mechanics.

## Checklist

- [ ] Have I said what I want to say with the fewest necessary words (economy)?
- [ ] Have I replaced vague quantifiers with precise figures or comparisons (precision)?
- [ ] Have I kept passive voice only where the actor is unimportant, unknown, or not the intended focus?
- [ ] Have I fixed any misplaced modifiers, comma splices, and sentence fragments?
- [ ] Are verb and pronoun agreement, capitalization, and number formatting correct throughout?
- [ ] Is parallel construction used consistently in lists and series?

## Usage

```bash
python tools/apply_skills.py --skill skills/15-style-mechanics/skill.yaml --input draft.md --output revised.md
```
