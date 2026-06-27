from . import business_professional, career_switcher, executive_leadership, graduate_ats, technical_professional


def select_resume_model(intelligence: dict):
    model_name = str(intelligence.get("recommended_resume_model", "")).strip().lower()
    target_role = str(intelligence.get("target_role", "")).strip().lower()
    experience_level = str(intelligence.get("experience_level", "")).strip().lower()
    career_direction = str(intelligence.get("career_direction_detected", "")).strip().lower()
    career_change = bool(intelligence.get("career_change_detected", False))

    if career_change:
        return "Career Switcher Resume", career_switcher
    if experience_level in {"student", "fresher"} or str(intelligence.get("candidate_profile_type", "")).strip().lower() in {"student", "fresher"}:
        return "Graduate ATS Resume", graduate_ats
    if experience_level in {"10+ years", "10+ yrs", "10+ year"} or "executive" in model_name:
        return "Executive Leadership Resume", executive_leadership
    if any(keyword in target_role for keyword in ["analyst", "hr", "marketing", "finance", "sales", "operations", "manager", "recruit", "talent"]):
        return "Business Professional Resume", business_professional
    if career_direction == "technical" or "technical" in model_name:
        return "Technical Professional Resume", technical_professional

    return "Business Professional Resume", business_professional
