from .spacing_engine import estimate_page_count, get_spacing
from .theme_engine import get_theme, select_theme
from .typography_engine import get_typography


def build_layout_config(resume_model: str = "", preferred_theme: str = "", experience_level: str = "", word_count: int = 0) -> dict:
    selected_theme = select_theme(resume_model, preferred_theme)
    theme = get_theme(selected_theme)
    spacing = get_spacing(experience_level)
    typography = get_typography(theme, experience_level)
    page_count = estimate_page_count(word_count, experience_level)
    render_quality_score = 92
    if page_count > spacing["max_pages"]:
        render_quality_score -= 8

    return {
        "selected_theme": selected_theme,
        "theme": theme,
        "spacing": spacing,
        "typography": typography,
        "page_count": page_count,
        "render_quality_score": max(75, min(98, render_quality_score)),
    }
