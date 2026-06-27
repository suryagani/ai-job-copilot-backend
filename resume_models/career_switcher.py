from ._shared import generate_resume_with_strategy


def generate_resume(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    instructions = """
Career Switcher Model
- Audience: candidates moving into a different domain or role family.
- Priority order: Summary, Transferable Skills, Relevant Experience, Projects, Education, Certifications.
- Summary style: career transition, transferable value, role relevance, business or technical fit without forcing unrelated detail.
- Bullet style: highlight transferable outcomes, coordination, problem solving, customer value, process ownership, and adjacent experience.
- Reduce unrelated legacy detail and do not oversell domain depth the candidate does not have.
"""
    return generate_resume_with_strategy(
        "Career Switcher",
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
