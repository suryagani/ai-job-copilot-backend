from __future__ import annotations


def _clean_list(values, limit: int | None = None) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or '').strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit] if limit else cleaned


def build_recommended_next_steps(optimized_resume: dict, ats_report: dict, recruiter_report: dict, linkedin_recommendations: dict, interview_preparation: dict, cover_letter: dict) -> list[str]:
    steps = []
    missing_keywords = _clean_list(ats_report.get('missing_keywords', []), 5)
    if missing_keywords:
        steps.append(f"Strengthen evidence for these missing role keywords before applying: {', '.join(missing_keywords)}.")
    concerns = _clean_list(recruiter_report.get('top_concerns', []), 3)
    if concerns:
        steps.append(f"Address recruiter concerns in the resume and interview narrative: {'; '.join(concerns)}.")
    weak_points = _clean_list(optimized_resume.get('weaknesses_found', []), 3)
    if weak_points:
        steps.append(f"Tighten the weakest resume areas next: {'; '.join(weak_points)}.")
    if int(linkedin_recommendations.get('linkedin_score', 0) or 0) < 80:
        steps.append('Update the LinkedIn headline, about section, and top skills order before sending applications.')
    if int(interview_preparation.get('readiness_score', 0) or 0) < 80:
        steps.append('Use the mock interview plan and STAR answers to improve interview readiness before high-priority applications.')
    if int(cover_letter.get('cover_letter_quality_score', 0) or 0) < 80:
        steps.append('Refine the cover letter opening and company-fit messaging for stronger first impressions.')
    if not steps:
        steps.append('Application package is strong. Personalize the submission for each employer and apply to the highest-fit roles first.')
    return steps[:6]


def classify_application_readiness(overall_application_score: int, job_match_score: int, critical_missing_keywords: int) -> str:
    if overall_application_score >= 85 and job_match_score >= 80 and critical_missing_keywords <= 2:
        return 'Excellent'
    if overall_application_score >= 75 and job_match_score >= 68:
        return 'Good'
    if overall_application_score >= 60 and job_match_score >= 55:
        return 'Needs Improvement'
    return 'Not Ready'
