# 14. Abstracts and Summaries

Skill ID: `genres.abstract-summary`

Writes a descriptive or informative abstract, or an academic or executive summary, following the book's distinctions: abstracts are compressed stand-ins for a paper aimed at the same audience, while summaries -- especially executive summaries -- are first-person, stand-alone documents in their own right.

Source: *Technical Writing for Engineers and Scientists (ISE)*, Chapter 14 -- Abstracts and Summaries.

## Checklist

- [ ] Do I understand who my audience is, and the purpose and context of this abstract or summary?
- [ ] Have I been given (or inferred) specific formulation requirements, such as word count?
- [ ] Have I met the word-count requirement and structured it to meet descriptive vs. informative expectations?
- [ ] Have I included all main ideas and limitations from the source, in original phrasing (no quotations)?
- [ ] For an academic summary, have I preserved the source's idea order and explained how the argument is supported?
- [ ] For an executive summary, have I written a first-person, stand-alone document and told the whole story?
- [ ] Have I included keywords that will inform both human evaluators and search/indexing algorithms?

## Usage

```bash
python tools/apply_skills.py --skill skills/14-abstract-summary/skill.yaml --input draft.md --output revised.md
```
