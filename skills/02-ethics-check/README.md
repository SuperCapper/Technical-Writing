# 2. Ethical Considerations

Skill ID: `foundations.ethics-check`

Screens a technical document or communication plan for the ethical hazards the book identifies: undisclosed image alteration, uncredited ideas, fabricated or cherry-picked data, hidden ambiguity, and social-media-unsafe language. Flags for human judgment rather than issuing verdicts, since ethics here turns on intent, not just rule-following.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 2 -- Ethical Considerations.

## Checklist

- [ ] Am I being accurate, honest, and free of speculation presented as fact?
- [ ] Have I given proper credit for every non-original idea, image, or dataset (see Documentation, Ch. 16)?
- [ ] Have I avoided violating copyright, fair use, or an applicable nondisclosure agreement?
- [ ] If any image has been altered, have I disclosed the alteration and its purpose in the caption?
- [ ] Is my underlying intent to do good for my audience, not to deceive them?
- [ ] Would this content, if it became public via social media, embarrass or expose me or my organization?

## Usage

```bash
python tools/apply_skills.py --skill skills/02-ethics-check/skill.yaml --input draft.md --output revised.md
```
