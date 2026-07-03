from __future__ import annotations


def _clean_list(values) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or '').strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def normalize_feedback(parsed: dict, candidate_data, recruiter_intelligence: dict | None = None, ats_intelligence: dict | None = None) -> dict:
    strengths = _clean_list(parsed.get('candidate_strengths', []))
    weaknesses = _clean_list(parsed.get('candidate_weaknesses', []))
    tips = _clean_list(parsed.get('interview_tips', []))
    follow_ups = _clean_list(parsed.get('likely_follow_up_questions', []))

    if not strengths:
        strengths = _clean_list((recruiter_intelligence or {}).get('top_strengths', []))
    if not weaknesses:
        weaknesses = _clean_list((recruiter_intelligence or {}).get('top_concerns', []))
    if not tips:
        tips = _clean_list((ats_intelligence or {}).get('ats_improvement_actions', []))

    def clamp(value, fallback):
        try:
            return max(0, min(100, int(value)))
        except Exception:
            return fallback

    confidence = clamp(parsed.get('confidence_score', 0), 70 if strengths else 55)
    readiness = clamp(parsed.get('readiness_score', 0), 68 if strengths else 52)

    return {
        'candidate_strengths': strengths[:6],
        'candidate_weaknesses': weaknesses[:6],
        'interview_tips': tips[:8],
        'likely_follow_up_questions': follow_ups[:8],
        'confidence_score': confidence,
        'readiness_score': readiness,
    }
