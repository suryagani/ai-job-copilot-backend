from __future__ import annotations


def clean_headline(headline: str, target_role: str = "", keywords: list[str] | None = None) -> str:
    value = " ".join(str(headline or "").replace("\n", " ").split()).strip(" |")
    if not value:
        pieces = [target_role.strip()]
        for keyword in (keywords or [])[:4]:
            text = str(keyword or "").strip()
            if text:
                pieces.append(text)
        value = " | ".join([piece for piece in pieces if piece])
    return value[:220].strip(" |")


def score_headline(headline: str, target_role: str = "", keywords: list[str] | None = None) -> int:
    score = 40
    text = str(headline or "").strip()
    lowered = text.lower()
    if target_role and target_role.lower() in lowered:
        score += 20
    matches = 0
    for keyword in (keywords or [])[:10]:
        token = str(keyword or "").strip().lower()
        if token and token in lowered:
            matches += 1
    score += min(matches * 4, 24)
    if "|" in text:
        score += 8
    if 35 <= len(text) <= 220:
        score += 8
    elif len(text) > 220:
        score -= 20
    return max(0, min(100, score))
