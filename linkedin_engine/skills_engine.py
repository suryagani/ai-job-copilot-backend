from __future__ import annotations


def _split_skills(raw: str) -> list[str]:
    tokens = []
    for part in str(raw or "").replace("\n", ",").split(","):
        text = part.strip()
        if text and text not in tokens:
            tokens.append(text)
    return tokens


def reorder_skills(skill_intelligence: dict | None, top_keywords: list[str] | None, technical_skills: str = "", transferable_skills: str = "", tools_software: str = "") -> list[str]:
    ordered = []
    for group in (skill_intelligence or {}).get("skill_groups", []):
        for skill in group.get("skills", []):
            text = str(skill or "").strip()
            if text and text not in ordered:
                ordered.append(text)
    for skill in top_keywords or []:
        text = str(skill or "").strip()
        if text and text not in ordered:
            ordered.append(text)
    for raw in [technical_skills, transferable_skills, tools_software]:
        for skill in _split_skills(raw):
            if skill not in ordered:
                ordered.append(skill)
    return ordered[:50]
