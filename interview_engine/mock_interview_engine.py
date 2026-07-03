from __future__ import annotations


def normalize_mock_plan(items, limit: int = 7) -> list[str]:
    values = items if isinstance(items, list) else str(items or "").splitlines()
    cleaned = []
    for item in values:
        text = str(item or "").strip().lstrip("-? ")
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit]


def fallback_mock_plan(target_role: str) -> list[str]:
    role = target_role or "your target role"
    return [
        f"Round 1: Practice a 90-second introduction tailored to {role}.",
        "Round 2: Rehearse 5 technical or role-specific questions out loud.",
        "Round 3: Practice 3 STAR stories covering teamwork, challenge, and achievement.",
        "Round 4: Prepare company-specific answers and 3 thoughtful questions to ask the interviewer.",
        "Round 5: Run a timed mock interview and refine weak answers.",
    ]
