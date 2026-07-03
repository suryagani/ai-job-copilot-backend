from __future__ import annotations


def build_top_keywords(skill_intelligence: dict | None, ats_intelligence: dict | None, job_intelligence: dict | None, target_role: str = "", career_knowledge: dict | None = None) -> list[str]:
    ordered = []

    def contains(value: str) -> bool:
        return value.lower() in {item.lower() for item in ordered}

    def add_many(values):
        for value in values or []:
            text = str(value or "").strip()
            if text and not contains(text):
                ordered.append(text)

    if target_role and not contains(target_role.strip()):
        ordered.append(target_role.strip())
    for group in (skill_intelligence or {}).get("skill_groups", []):
        add_many(group.get("skills", []))
    add_many((ats_intelligence or {}).get("matching_keywords", []))
    add_many((ats_intelligence or {}).get("required_keywords", []))
    add_many((job_intelligence or {}).get("ats_keywords", []))
    add_many((job_intelligence or {}).get("required_skills", []))
    add_many((job_intelligence or {}).get("preferred_skills", []))
    add_many((career_knowledge or {}).get("recommended_roles", []))
    add_many((career_knowledge or {}).get("recommended_certifications", []))
    return ordered[:50]
