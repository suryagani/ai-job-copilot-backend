# ATS Scoring Change Log

## Before
- One flat `required_keywords` list mixed hard requirements, market language, and nice-to-have skills.
- ATS score was dominated by raw keyword match ratio with strong penalties for any missing terms.
- Placement quality in summary, skills, projects, and experience had little influence.

## After
- ATS keywords are separated into `required`, `preferred`, and `supporting` tiers.
- Matching now uses verified evidence mapping from skills, projects, experience, internships, education, and certifications.
- ATS score now weights required coverage most heavily, but still considers preferred/supporting evidence and real placement inside ATS-safe sections.
- Missing verified skills are still kept out of the resume and remain only in improvement guidance.

## Guardrails
- No ATS score floors or artificial bonuses were added.
- No unsupported skills are inserted into resume content.
- Keyword stuffing penalties remain active.