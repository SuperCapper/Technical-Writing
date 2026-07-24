# 7. Instructions and Manuals

Skill ID: `genres.instructions`

Drafts or reviews step-by-step instructions calibrated to a stated audience skill level, following Outline 7.1: disclaimer, process overview and theory, and a numbered sequence of steps, each preceded by an overview of what the step accomplishes and followed by needed cautions.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 7 -- Instructions and Manuals.

## Checklist

- [ ] Do I understand the process and the skill level of the intended audience?
- [ ] Have I defined the overall process and described its purpose?
- [ ] Have I explained any needed theories or principles for this audience?
- [ ] Have I listed and defined each step?
- [ ] Before each action, have I given an overview of what will happen?
- [ ] Have I provided needed cautions, dangers, and required equipment?
- [ ] Have I transitioned to the next step, if there is one?
- [ ] Do the visuals show something happening (dynamic, not static), get referenced before use, and carry sequence numbers?
- [ ] Does each visual serve a specific purpose rather than decorating the page?

## Usage

```bash
python tools/apply_skills.py --skill skills/07-instructions/skill.yaml --input draft.md --output revised.md
```
