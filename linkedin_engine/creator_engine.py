from __future__ import annotations


def build_creator_profile_suggestions(candidate_data, career_knowledge: dict | None = None, recruiter_intelligence: dict | None = None) -> list[str]:
    role = str(getattr(candidate_data, "target_role", "") or "your target role").strip()
    suggestions = [
        f"Create a repeatable content theme around {role} insights, project learnings, and practical lessons.",
        "Turn one project, internship, or work challenge into a short carousel or text post each month.",
        "Use the Featured section to pin your strongest proof of work instead of leaving it empty.",
    ]
    if recruiter_intelligence and recruiter_intelligence.get("top_strengths"):
        suggestions.append(f"Build posts around strengths such as {', '.join(recruiter_intelligence['top_strengths'][:2])}.")
    if career_knowledge and career_knowledge.get("future_growth_roles"):
        suggestions.append(f"Create content that also signals growth toward {career_knowledge['future_growth_roles'][0]}.")
    return suggestions[:5]


def build_networking_suggestions(candidate_data, job_intelligence: dict | None = None, career_knowledge: dict | None = None) -> list[str]:
    role = str(getattr(candidate_data, "target_role", "") or "target role").strip()
    industry = str(getattr(candidate_data, "target_industry", "") or "target industry").strip()
    suggestions = [
        f"Connect with recruiters hiring for {role} roles in {getattr(candidate_data, 'target_country', 'your market')}.",
        f"Follow companies and hiring managers in {industry or role}-related spaces and engage with recent posts thoughtfully.",
        "Join 3-5 role-specific LinkedIn groups or communities and contribute useful comments regularly.",
    ]
    if job_intelligence and job_intelligence.get("company_type_guess"):
        suggestions.append(f"Prioritize networking with professionals in {job_intelligence['company_type_guess']} environments similar to your target jobs.")
    if career_knowledge and career_knowledge.get("recommended_industries"):
        suggestions.append(f"Expand your network into adjacent industries such as {career_knowledge['recommended_industries'][0]} for more opportunities.")
    return suggestions[:5]
