from __future__ import annotations


def clamp_score(value, default: int = 0) -> int:
    try:
        return max(0, min(100, int(value)))
    except Exception:
        return default


def average_score(*values) -> int:
    cleaned = [clamp_score(value) for value in values if value is not None]
    if not cleaned:
        return 0
    return round(sum(cleaned) / len(cleaned))


def calculate_job_match_score(optimized_resume: dict, ats_report: dict, recruiter_report: dict) -> int:
    skill_match = clamp_score(optimized_resume.get('skill_match_percentage', 0))
    ats_score = clamp_score(ats_report.get('ats_score_estimate', 0))
    role_alignment = clamp_score(recruiter_report.get('interview_probability', 0))
    missing_penalty = min(len(ats_report.get('missing_keywords', [])) * 3, 18)
    return max(0, min(100, round((skill_match * 0.4) + (ats_score * 0.35) + (role_alignment * 0.25) - missing_penalty)))


def calculate_overall_application_score(optimized_resume: dict, cover_letter: dict, linkedin_recommendations: dict, interview_preparation: dict, ats_report: dict, recruiter_report: dict) -> int:
    resume_score = average_score(
        optimized_resume.get('quality_score', 0),
        optimized_resume.get('ats_score_estimate', 0),
        optimized_resume.get('interview_probability', 0),
        optimized_resume.get('recruiter_confidence', 0),
    )
    cover_letter_score = average_score(
        cover_letter.get('cover_letter_quality_score', 0),
        cover_letter.get('ats_alignment_score', 0),
        cover_letter.get('recruiter_confidence', 0),
    )
    linkedin_score = average_score(
        linkedin_recommendations.get('headline_score', 0),
        linkedin_recommendations.get('linkedin_score', 0),
        linkedin_recommendations.get('recruiter_visibility_score', 0),
    )
    interview_score = average_score(
        interview_preparation.get('confidence_score', 0),
        interview_preparation.get('readiness_score', 0),
    )
    ats_score = average_score(
        ats_report.get('ats_score_estimate', 0),
        100 - min(len(ats_report.get('missing_keywords', [])) * 6, 40),
    )
    recruiter_score = average_score(
        recruiter_report.get('interview_probability', 0),
        recruiter_report.get('recruiter_confidence', 0),
    )
    weighted = (
        resume_score * 0.3
        + cover_letter_score * 0.1
        + linkedin_score * 0.15
        + interview_score * 0.15
        + ats_score * 0.15
        + recruiter_score * 0.15
    )
    return max(0, min(100, round(weighted)))


def normalize_application_payload(result: dict) -> dict:
    result['overall_application_score'] = clamp_score(result.get('overall_application_score', 0))
    result['job_match_score'] = clamp_score(result.get('job_match_score', 0))
    for key in ('recommended_next_steps',):
        values = []
        for item in result.get(key, []):
            text = str(item or '').strip()
            if text and text not in values:
                values.append(text)
        result[key] = values
    return result
