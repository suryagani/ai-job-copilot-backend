# ATS Root Cause Report

## Main Findings
- Low ATS scores were primarily caused by flat keyword treatment, where market-language keywords and hard requirements were mixed together.
- Several legacy synthetic resumes lacked ATS-safe headings like `Professional Summary` or `Experience`, which reduced placement and structure quality even when the technical evidence was present.
- Career-switcher and senior-manager samples were penalized for keywords that were adjacent to the role but not directly evidenced as verified skills.
- The ATS engine previously gave too much weight to broad library keywords and too little weight to verified placement inside summary, projects, and experience.

## Issue Classes
- `A` Missing role keywords: present in some cases, but often mixed with non-critical library terminology.
- `B` Existing skills not placed correctly: common in VLSI, DevOps, and senior leadership samples.
- `C` Weak JD matching: strong in optimizer cases when real missing skills such as Terraform or Kubernetes were genuine gaps.
- `D` Skills present in input but omitted from final resume: visible in some builder samples before calibration.
- `E` Skills only in skills section, not evidenced in bullets: common across technical and operations samples.
- `F` Non-standard headings: visible in older stored builder outputs.
- `G` Incorrect section order: visible in some builder models but less harmful than missing headings.
- `J` Career-switcher relevance issues: HR switcher needed transferable-evidence emphasis, not forced HR claims.
- `L` ATS scoring formula problems: the main calibration target in this sprint.

## Low-Score Persona Notes
### SYN-VLSI-001 — VLSI Engineer
- Before ATS score: `35`
- Actual problem: legacy scoring treated too many terms as equally required, and older resume text did not always place verified skills into ATS-safe headings and evidence sections.
- Primary fix: weighted ATS keyword tiers plus evidence-aware keyword placement in summary, skills, projects, and experience.
- Risk of fix: over-optimizing could lead to keyword stuffing or fake skills, so missing verified skills remain in suggestions only.
### SYN-DEVOPS-002 — DevOps Engineer
- Before ATS score: `36`
- Actual problem: legacy scoring treated too many terms as equally required, and older resume text did not always place verified skills into ATS-safe headings and evidence sections.
- Primary fix: weighted ATS keyword tiers plus evidence-aware keyword placement in summary, skills, projects, and experience.
- Risk of fix: over-optimizing could lead to keyword stuffing or fake skills, so missing verified skills remain in suggestions only.
### SYN-RESTAURANT-005 — Restaurant Manager
- Before ATS score: `54`
- Actual problem: legacy scoring treated too many terms as equally required, and older resume text did not always place verified skills into ATS-safe headings and evidence sections.
- Primary fix: weighted ATS keyword tiers plus evidence-aware keyword placement in summary, skills, projects, and experience.
- Risk of fix: over-optimizing could lead to keyword stuffing or fake skills, so missing verified skills remain in suggestions only.
### SYN-SOFTWARE-MANAGER-007 — Engineering Manager
- Before ATS score: `36`
- Actual problem: legacy scoring treated too many terms as equally required, and older resume text did not always place verified skills into ATS-safe headings and evidence sections.
- Primary fix: weighted ATS keyword tiers plus evidence-aware keyword placement in summary, skills, projects, and experience.
- Risk of fix: over-optimizing could lead to keyword stuffing or fake skills, so missing verified skills remain in suggestions only.
### SYN-OPS-006 — Engineering Manager
- Before ATS score: `36`
- Actual problem: legacy scoring treated too many terms as equally required, and older resume text did not always place verified skills into ATS-safe headings and evidence sections.
- Primary fix: weighted ATS keyword tiers plus evidence-aware keyword placement in summary, skills, projects, and experience.
- Risk of fix: over-optimizing could lead to keyword stuffing or fake skills, so missing verified skills remain in suggestions only.
### SYN-CLOUD-OPTIMIZER-008 — DevOps Engineer
- Before ATS score: `49`
- Actual problem: legacy scoring treated too many terms as equally required, and older resume text did not always place verified skills into ATS-safe headings and evidence sections.
- Primary fix: weighted ATS keyword tiers plus evidence-aware keyword placement in summary, skills, projects, and experience.
- Risk of fix: over-optimizing could lead to keyword stuffing or fake skills, so missing verified skills remain in suggestions only.

## Fixture Availability
- The repository already contained eight directly reusable synthetic ATS benchmark outputs and one JD optimizer sample.
- The requested marketing, finance, healthcare, and sales ATS fixtures were not present as stored V2.0/V2.2 benchmark samples in the repo, so they are listed as unavailable rather than recreated with changed content.