def get_typography(theme: dict, experience_level: str = "") -> dict:
    level = (experience_level or "").strip().lower()
    title_size = 18 if level not in {"10+ years", "10+ yrs", "10+ year"} else 20
    return {
        "title_size": title_size,
        "subtitle_size": 10,
        "heading_size": 11,
        "body_size": 10 if level in {"student", "fresher"} else 11,
    }
