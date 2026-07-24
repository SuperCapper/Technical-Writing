# 6. Description of a Process

Skill ID: `elements.process-description`

Drafts or reviews a description of a process -- either a mechanism in operation or a conceptual process -- following the book's outline: define the process, list its steps in the introduction, then define, explain the function of, and precisely describe each step in order, with transitions and explicit branching for iterative processes.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 6 -- Description of a Process.

## Checklist

- [ ] Have I defined the process and extended the definition with any theory the reader needs?
- [ ] Have I described the process's overall function or purpose?
- [ ] Have I listed the main steps in the introduction, in the order they are discussed?
- [ ] Have I defined each step and described its function or purpose?
- [ ] Have I precisely described what happens in each step, with transitions between steps?
- [ ] For iterative processes, have I shown clearly where branching occurs and when the process completes?
- [ ] Have I concluded by summarizing the process's purpose and function, giving it a sense of finality?
- [ ] Do all visuals relate directly to the text?

## Usage

```bash
python tools/apply_skills.py --skill skills/06-process-description/skill.yaml --input draft.md --output revised.md
```
