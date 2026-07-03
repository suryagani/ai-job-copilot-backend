from __future__ import annotations

from .application_export import export_application_report
from .application_planner import build_recommended_next_steps, classify_application_readiness
from .application_report import build_application_report
from .application_validator import calculate_job_match_score, calculate_overall_application_score, normalize_application_payload


def generate_job_application_package(candidate_data, optimized_resume: dict, cover_letter: dict, linkedin_recommendations: dict, interview_preparation: dict, ats_report: dict, recruiter_report: dict) -> dict:
    result = {
        'optimized_resume': optimized_resume,
        'cover_letter': cover_letter,
        'linkedin_recommendations': linkedin_recommendations,
        'interview_preparation': interview_preparation,
        'ats_report': ats_report,
        'recruiter_report': recruiter_report,
    }
    result['job_match_score'] = calculate_job_match_score(optimized_resume, ats_report, recruiter_report)
    result['overall_application_score'] = calculate_overall_application_score(optimized_resume, cover_letter, linkedin_recommendations, interview_preparation, ats_report, recruiter_report)
    result['recommended_next_steps'] = build_recommended_next_steps(optimized_resume, ats_report, recruiter_report, linkedin_recommendations, interview_preparation, cover_letter)
    result['application_readiness'] = classify_application_readiness(result['overall_application_score'], result['job_match_score'], len(ats_report.get('missing_keywords', [])))
    report = build_application_report(candidate_data, result)
    result.update(export_application_report(getattr(candidate_data, 'full_name', ''), getattr(candidate_data, 'target_role', ''), getattr(candidate_data, 'target_country', 'Global'), report))
    result['application_report'] = report
    return normalize_application_payload(result)
