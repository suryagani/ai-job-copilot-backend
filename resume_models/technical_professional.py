from ._shared import generate_resume_with_strategy


def generate_resume(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    instructions = """
Technical Professional Model
- Audience: software, cloud, devops, data, AI, cyber, VLSI, mechanical, civil, engineering professionals.
- Priority order: Professional Summary, Core Technical Skills, Experience, Projects, Certifications, Education.
- Summary style: technical credibility, engineering mindset, problem solving, tools, implementation depth.
- Bullet style: action-led, technically specific, impact-aware, delivery-focused.
- Emphasize systems, tools, methods, implementation, analysis, and technical decision quality.
"""
    return generate_resume_with_strategy(
        "Technical Professional",
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
