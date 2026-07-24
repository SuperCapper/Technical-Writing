# 12. Research Reports

Skill ID: `genres.research-report`

Drafts or reviews a state-of-the-art or historical research report: scoping the research question, distinguishing primary from secondary sources, evaluating source credibility, integrating source material without over-quoting, and documenting everything.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 12 -- Research Reports.

## Checklist

- [ ] Have I discussed how I limited the report's scope, and my rationale for doing so?
- [ ] Have I provided adequate background for my reader to understand the report?
- [ ] Have I provided substantive, well-documented information, distinguishing primary from secondary sources?
- [ ] Have I summarized my research in the conclusion, and supported any recommendation with the discussion?
- [ ] Have I cited sources in the text and listed them, and evaluated each source's credibility?
- [ ] Have I included in an appendix any relevant material not necessary for understanding the paper?
- [ ] Do all visuals relate to the text and carry sequence numbers?

## Usage

```bash
python tools/apply_skills.py --skill skills/12-research-report/skill.yaml --input draft.md --output revised.md
```
