THEMES = {
    "Modern Professional": {
        "docx_font": "Aptos",
        "pdf_font": "Helvetica",
        "heading_color": "#0f172a",
        "body_color": "#1f2937",
        "accent_color": "#334155",
    },
    "Classic ATS": {
        "docx_font": "Calibri",
        "pdf_font": "Helvetica",
        "heading_color": "#111827",
        "body_color": "#111827",
        "accent_color": "#374151",
    },
    "Technical Professional": {
        "docx_font": "Aptos",
        "pdf_font": "Helvetica",
        "heading_color": "#0b3b60",
        "body_color": "#102a43",
        "accent_color": "#486581",
    },
    "Executive": {
        "docx_font": "Cambria",
        "pdf_font": "Helvetica",
        "heading_color": "#1f2937",
        "body_color": "#111827",
        "accent_color": "#4b5563",
    },
    "Minimal": {
        "docx_font": "Arial",
        "pdf_font": "Helvetica",
        "heading_color": "#111827",
        "body_color": "#374151",
        "accent_color": "#6b7280",
    },
}


def select_theme(resume_model: str = "", preferred_theme: str = "") -> str:
    if preferred_theme in THEMES:
        return preferred_theme

    normalized = (resume_model or "").strip().lower()
    if "executive" in normalized:
        return "Executive"
    if "technical" in normalized:
        return "Technical Professional"
    if "graduate" in normalized:
        return "Classic ATS"
    if "career switcher" in normalized:
        return "Minimal"
    return "Modern Professional"


def get_theme(theme_name: str) -> dict:
    return THEMES.get(theme_name, THEMES["Modern Professional"]).copy()
