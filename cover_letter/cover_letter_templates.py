from __future__ import annotations

TONE_CONFIG = {
    "Professional": {
        "voice": "polished, confident, and recruiter-friendly",
        "opening": "Start with direct role alignment and a credible reason for interest.",
        "closing": "Close with a calm, professional invitation for next steps.",
    },
    "Executive": {
        "voice": "strategic, leadership-focused, and commercially aware",
        "opening": "Lead with leadership scope, business outcomes, and market relevance.",
        "closing": "Close with senior-level confidence and business value.",
    },
    "Friendly": {
        "voice": "warm, human, and still professional",
        "opening": "Start with authentic interest and a clear fit for the role.",
        "closing": "Close with warmth while staying concise and credible.",
    },
    "Technical": {
        "voice": "precise, technically credible, and problem-solving oriented",
        "opening": "Open with technical alignment, domain exposure, and delivery mindset.",
        "closing": "Close with confidence around execution and contribution.",
    },
    "Business": {
        "voice": "stakeholder-aware, outcome-driven, and commercially grounded",
        "opening": "Lead with role relevance, communication strengths, and business impact.",
        "closing": "Close with concise business confidence and collaboration readiness.",
    },
    "Graduate": {
        "voice": "high-potential, credible, and learning-oriented without sounding junior",
        "opening": "Open with target role fit, academic or project relevance, and motivation.",
        "closing": "Close with professional enthusiasm and readiness to contribute.",
    },
    "Career Switcher": {
        "voice": "confident, transferable, and transition-aware",
        "opening": "Open by bridging previous experience to the new target role clearly.",
        "closing": "Close by reinforcing transferable value and readiness to transition.",
    },
}


def normalize_tone(tone: str, experience_level: str = "") -> str:
    value = (tone or "").strip()
    if value in TONE_CONFIG:
        return value
    lowered = value.lower()
    if "execut" in lowered:
        return "Executive"
    if "friend" in lowered:
        return "Friendly"
    if "technic" in lowered:
        return "Technical"
    if "business" in lowered:
        return "Business"
    if "switch" in lowered:
        return "Career Switcher"
    if any(token in (experience_level or "").lower() for token in ["student", "fresher", "graduate"]):
        return "Graduate"
    return "Professional"


def get_template_config(tone: str, experience_level: str = "") -> dict:
    selected = normalize_tone(tone, experience_level)
    config = dict(TONE_CONFIG[selected])
    config["tone"] = selected
    return config


def build_greeting(hiring_manager: str = "") -> str:
    manager = (hiring_manager or "").strip()
    if manager:
        return f"Dear {manager},"
    return "Dear Hiring Manager,"


def build_signature(full_name: str = "") -> str:
    return (full_name or "").strip() or "Candidate"
