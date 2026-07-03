from __future__ import annotations


def normalize_behavioral_questions(items, limit: int = 8) -> list[str]:
    values = items if isinstance(items, list) else str(items or "").splitlines()
    cleaned = []
    for item in values:
        text = str(item or "").strip().lstrip("-? ")
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit]


def fallback_behavioral_questions(target_role: str) -> list[str]:
    role = target_role or "this role"
    return [
        f"Tell me about a time you had to learn something quickly to become effective for {role}.",
        "Describe a situation where you handled pressure or a tight deadline.",
        "Tell me about a time you worked with others to solve a problem.",
        "Describe a time you received feedback and how you responded to it.",
        "Tell me about a situation where you had to stay organized across multiple tasks.",
    ]
