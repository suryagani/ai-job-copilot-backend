from __future__ import annotations


def normalize_experience_rewrite(value) -> list[str]:
    if isinstance(value, list):
        items = value
    else:
        items = str(value or "").splitlines()
    cleaned = []
    for item in items:
        text = str(item or "").strip().lstrip("-? ")
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:10]
