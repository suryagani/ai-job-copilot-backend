from ._shared import generate_resume_with_strategy


def generate_resume(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    instructions = """
Graduate ATS Model
- Audience: students, freshers, early career starters, internship applicants.
- Priority order: Education, Projects, Skills, Certifications, Internships, Additional Experience.
- Summary style: potential, learning ability, academic strength, technical exposure, readiness.
- Bullet style: academic, project-based, learning-oriented, truthful, concise.
- Avoid executive or senior leadership language.
- Keep the resume compact and one-page friendly unless the strategy clearly allows more.
"""
    return generate_resume_with_strategy(
        "Graduate ATS",
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
