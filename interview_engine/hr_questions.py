from __future__ import annotations


def normalize_hr_questions(items, limit: int = 8) -> list[str]:
    values = items if isinstance(items, list) else str(items or "").splitlines()
    cleaned = []
    for item in values:
        text = str(item or "").strip().lstrip("-? ")
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit]


def fallback_hr_questions(target_role: str, company_name: str = "") -> list[str]:
    company = company_name or "our company"
    role = target_role or "this role"
    return [
        f"Why are you interested in the {role} opportunity at {company}?",
        "Tell me about yourself and how your background connects to this role.",
        "What are your strengths, and how would they help you succeed here?",
        "What is one development area you are actively working on?",
        "Why should we hire you for this opportunity?",
    ]
