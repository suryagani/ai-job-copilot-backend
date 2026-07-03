from __future__ import annotations


def normalize_star_examples(items, limit: int = 5) -> list[str]:
    values = items if isinstance(items, list) else str(items or "").split('\n\n')
    cleaned = []
    for item in values:
        text = str(item or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit]


def fallback_star_examples(candidate_data) -> list[str]:
    examples = []
    if str(getattr(candidate_data, 'projects', '')).strip():
        examples.append(
            "Situation: Explain the project context. Task: Describe your responsibility. Action: Walk through the tools, steps, and decisions you handled. Result: Share the practical outcome or learning without inventing metrics."
        )
    if str(getattr(candidate_data, 'leadership_experience', '')).strip() or str(getattr(candidate_data, 'achievements', '')).strip():
        examples.append(
            "Situation: Describe the team or activity. Task: Explain what you needed to coordinate. Action: Show how you organized people, communication, or delivery. Result: Explain the outcome and what it demonstrates about you."
        )
    if str(getattr(candidate_data, 'work_experience', '')).strip() or str(getattr(candidate_data, 'internships', '')).strip():
        examples.append(
            "Situation: Introduce the work challenge. Task: Clarify the expectation. Action: Explain what you personally did. Result: Describe the operational, technical, or customer impact honestly."
        )
    return examples[:5]
