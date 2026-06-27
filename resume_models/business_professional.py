from ._shared import generate_resume_with_strategy


def generate_resume(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    instructions = """
Business Professional Model
- Audience: business analyst, HR, marketing, finance, operations, sales, and business-facing professionals.
- Priority order: Professional Summary, Core Competencies, Professional Experience, Achievements, Education.
- Summary style: business value, stakeholder communication, delivery, coordination, reporting, execution quality.
- Bullet style: polished, commercially clear, role-relevant, recruiter-friendly, readable.
- Emphasize collaboration, business outcomes, documentation, communication, analysis, and operational reliability.
"""
    return generate_resume_with_strategy(
        "Business Professional",
        instructions,
        candidate_data,
        intelligence,
        skill_intelligence,
        achievement_intelligence,
        ats_intelligence,
        recruiter_intelligence,
        job_intelligence,
        personalization,
    )
