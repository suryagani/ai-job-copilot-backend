from __future__ import annotations

from .bio_generator import clean_list, clean_text


def normalize_case_studies(value, fallback_projects: str = '', limit: int = 4) -> list[str]:
    if isinstance(value, list):
        items = value
    else:
        items = str(value or '').split('\n\n')
    cleaned = []
    for item in items:
        text = clean_text(item)
        if text and text not in cleaned:
            cleaned.append(text)
    if not cleaned and str(fallback_projects or '').strip():
        cleaned.append(clean_text(f'''Problem: Summarize the project context from the candidate input.
Solution: Explain the candidate's approach and contribution honestly.
Technology: Use only the tools or skills mentioned by the candidate.
Contribution: Clarify what the candidate personally handled.
Outcome: Describe the practical result without inventing metrics.
Lessons Learned: Explain what the project demonstrates for the target role.'''))
    return cleaned[:limit]


def build_project_showcase(projects: str, achievements: str = '', limit: int = 5) -> list[str]:
    values = []
    raw = '\n'.join(part for part in [projects, achievements] if str(part or '').strip())
    for line in raw.replace('\r', '').splitlines():
        text = line.strip().lstrip('-? ')
        if text and text not in values:
            values.append(text)
    return values[:limit]
