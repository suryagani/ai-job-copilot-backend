from __future__ import annotations


def normalize_questions(items, fallback: list[str] | None = None, limit: int = 8) -> list[str]:
    values = items if isinstance(items, list) else str(items or "").splitlines()
    cleaned = []
    for item in values:
        text = str(item or "").strip().lstrip("-? ")
        if text and text not in cleaned:
            cleaned.append(text)
    if not cleaned and fallback:
        cleaned = [str(item).strip() for item in fallback if str(item).strip()]
    return cleaned[:limit]


def build_fallback_technical_questions(target_role: str, required_skills: list[str] | None = None, projects: str = "") -> list[str]:
    role = target_role or "the role"
    skills = [str(skill).strip() for skill in (required_skills or []) if str(skill).strip()][:4]
    questions = [
        f"Walk me through the technical knowledge you have built that is most relevant to a {role} role.",
        f"Which project or hands-on experience best shows your readiness for {role}, and what exactly did you contribute?",
        f"How would you explain your approach to solving a role-specific technical problem in {role}?",
    ]
    for skill in skills:
        questions.append(f"How have you applied or learned {skill} in a practical setting?")
    if projects:
        questions.append("Which project would you choose to discuss in detail, and why is it relevant to this role?")
    return questions[:8]
