from __future__ import annotations

THEMES = {
    'Developer': {
        'accent': '#4fd1c5',
        'background': '#0b1120',
        'surface': '#111827',
        'text': '#e5f6ff',
        'muted': '#9fb7c9',
    },
    'Business': {
        'accent': '#0ea5e9',
        'background': '#071018',
        'surface': '#0f172a',
        'text': '#f5fbff',
        'muted': '#a9b8cb',
    },
    'Executive': {
        'accent': '#d4a017',
        'background': '#0a0d14',
        'surface': '#161b24',
        'text': '#f8fafc',
        'muted': '#b7c0cc',
    },
    'Creative': {
        'accent': '#f97316',
        'background': '#111827',
        'surface': '#1f2937',
        'text': '#f9fafb',
        'muted': '#c5ced8',
    },
    'Minimal': {
        'accent': '#38bdf8',
        'background': '#0f172a',
        'surface': '#111827',
        'text': '#f8fafc',
        'muted': '#b3c0ce',
    },
}


def select_theme(candidate_data, intelligence: dict | None = None) -> str:
    role = str(getattr(candidate_data, 'target_role', '')).lower()
    direction = str(getattr(candidate_data, 'career_direction', '')).lower()
    experience = str(getattr(candidate_data, 'experience_level', '')).lower()
    model = str((intelligence or {}).get('recommended_resume_model', '')).lower()
    if 'executive' in model or '10+' in experience or 'senior' in experience:
        return 'Executive'
    if any(token in direction for token in ['technical']) or any(token in role for token in ['engineer', 'developer', 'devops', 'data', 'vlsi']):
        return 'Developer'
    if any(token in direction for token in ['business', 'operations', 'finance', 'sales', 'marketing']) or any(token in role for token in ['analyst', 'manager', 'executive', 'coordinator']):
        return 'Business'
    if any(token in role for token in ['designer', 'creative']):
        return 'Creative'
    return 'Minimal'


def get_theme(theme_name: str) -> dict:
    return THEMES.get(theme_name, THEMES['Minimal'])
