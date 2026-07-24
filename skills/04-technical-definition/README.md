# 4. Technical Definition

Skill ID: `elements.technical-definition`

Drafts or repairs a technical definition using the book's formula: (Qualifier +) Term = Classification + Differentiation. Eliminates circular definitions, adds a domain qualifier when the term is ambiguous across fields, and appends one audience-appropriate extension (further definition, comparison, classification, cause-and-effect, process, exemplification, or etymology).

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 4 -- Technical Definition.

## Checklist

- [ ] Have I fully analyzed the purpose of my project and the audience's skill/knowledge level?
- [ ] Have I classified the term at a level that adds precision without being circular?
- [ ] Have I differentiated the term from other members of its class?
- [ ] Have I determined whether a qualifier is needed because the context is otherwise ambiguous?
- [ ] Have I avoided using terms in the definition that themselves need defining, or added extensions for them?
- [ ] Have I chosen extensions appropriate for my audience and purpose without sacrificing my core communicative goal?

## Usage

```bash
python tools/apply_skills.py --skill skills/04-technical-definition/skill.yaml --input draft.md --output revised.md
```
