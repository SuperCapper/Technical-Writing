# 17. Visuals

Skill ID: `style-support.visuals`

Reviews or drafts visual placement and captions for reproducibility, simplicity, and accuracy: every visual must be referenced in the text before it appears, carry a sequence number within its own type, serve a specific purpose, and avoid all-caps or underlined text in favor of bold for emphasis.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 17 -- Visuals.

## Checklist

- [ ] Have I identified my audience and whether a visual will help them understand the message?
- [ ] Is each visual referenced in the text before it appears?
- [ ] Does each visual carry a sequence number, numbered separately by visual type?
- [ ] Does each visual serve a specific purpose rather than decorating the page?
- [ ] For instructions, do the visuals show something happening (dynamic), not a static state?
- [ ] Have I used bold rather than all-caps or underlining for emphasis?

## Usage

```bash
python tools/apply_skills.py --skill skills/17-visuals/skill.yaml --input draft.md --output revised.md
```
