# 16. Documentation

Skill ID: `style-support.source-documentation`

Checks that every non-original idea, quotation, image, or dataset in a document is documented, in the style guide specified, and formats individual source citations (websites, journals, source-code repositories, technical reports, interviews, etc.) according to that guide.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 16 -- Documentation.

## Checklist

- [ ] Have I identified the style guide required by my employer, teacher, or field, and used it consistently?
- [ ] Is every non-original idea, quotation, image, or dataset cited?
- [ ] Does my use of copyrighted material qualify as Fair Use, and is it documented as such?
- [ ] Have I formatted each source type (book, journal, website, source-code repo, interview, etc.) per the style guide's rules?
- [ ] Have I included author, title, date, and access/publication details required for each citation?

## Usage

```bash
python tools/apply_skills.py --skill skills/16-source-documentation/skill.yaml --input draft.md --output revised.md
```
