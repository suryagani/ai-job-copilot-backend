from ._shared import generate_resume_with_strategy


def generate_resume(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    instructions = """
Executive Leadership Model
- Audience: 10+ years professionals, managers, directors, heads, senior operational leaders.
- Priority order: Executive Summary, Leadership Competencies, Career Highlights, Professional Experience, Strategic Achievements, Education.
- Summary style: leadership, commercial impact, strategic thinking, people management, scope, operational influence.
- Bullet style: senior, decisive, outcome-aware, leadership-oriented, structured.
- Emphasize scale, leadership, ownership, cross-functional influence, standards, transformation, and business impact without fabricating metrics.
"""
    return generate_resume_with_strategy(
        "Executive Leadership",
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
