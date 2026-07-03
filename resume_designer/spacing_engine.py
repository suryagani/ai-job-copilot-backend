def get_spacing(experience_level: str = "") -> dict:
    level = (experience_level or "").strip().lower()
    if level in {"student", "fresher", "1-3 years", "1â€“3 years"}:
        return {
            "margins": 42,
            "title_after": 8,
            "section_before": 8,
            "section_after": 4,
            "line_leading": 13,
            "bullet_gap": 2,
            "max_pages": 1,
        }
    if level in {"10+ years", "10+ yrs", "10+ year"}:
        return {
            "margins": 46,
            "title_after": 10,
            "section_before": 10,
            "section_after": 5,
            "line_leading": 14,
            "bullet_gap": 3,
            "max_pages": 2,
        }
    return {
        "margins": 44,
        "title_after": 9,
        "section_before": 9,
        "section_after": 4,
        "line_leading": 13,
        "bullet_gap": 2,
        "max_pages": 2,
    }


def estimate_page_count(word_count: int, experience_level: str = "") -> int:
    level = (experience_level or "").strip().lower()
    if level in {"student", "fresher", "1-3 years", "1â€“3 years"}:
        return 1
    if level in {"10+ years", "10+ yrs", "10+ year"}:
        return 2 if word_count > 450 else 1
    return 2 if word_count > 650 else 1
