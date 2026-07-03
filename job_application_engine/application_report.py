from __future__ import annotations


def _clean_list(values, limit: int | None = None) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or '').strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit] if limit else cleaned


def build_application_report(candidate_data, result: dict) -> dict:
    optimized_resume = result.get('optimized_resume', {})
    cover_letter = result.get('cover_letter', {})
    linkedin = result.get('linkedin_recommendations', {})
    interview = result.get('interview_preparation', {})
    ats_report = result.get('ats_report', {})
    recruiter_report = result.get('recruiter_report', {})

    return {
        'candidate_name': getattr(candidate_data, 'full_name', ''),
        'target_role': getattr(candidate_data, 'target_role', ''),
        'target_company': getattr(candidate_data, 'company_name', ''),
        'target_country': getattr(candidate_data, 'target_country', ''),
        'application_readiness': result.get('application_readiness', ''),
        'overall_application_score': result.get('overall_application_score', 0),
        'job_match_score': result.get('job_match_score', 0),
        'resume_summary': {
            'recommended_style': optimized_resume.get('recommended_resume_style', ''),
            'recommendation_reason': optimized_resume.get('recommendation_reason', ''),
            'ats_score_estimate': optimized_resume.get('ats_score_estimate', 0),
            'quality_score': optimized_resume.get('quality_score', 0),
            'strengths': _clean_list(optimized_resume.get('strengths', []), 5),
            'weaknesses_found': _clean_list(optimized_resume.get('weaknesses_found', []), 5),
        },
        'ats_summary': {
            'ats_readiness_level': ats_report.get('ats_readiness_level', ''),
            'matching_keywords': _clean_list(ats_report.get('matching_keywords', []), 8),
            'missing_keywords': _clean_list(ats_report.get('missing_keywords', []), 8),
            'ats_improvement_actions': _clean_list(ats_report.get('ats_improvement_actions', []), 6),
        },
        'recruiter_summary': {
            'shortlisting_decision': recruiter_report.get('shortlisting_decision', ''),
            'resume_competitiveness': recruiter_report.get('resume_competitiveness', ''),
            'first_impression': recruiter_report.get('first_impression', ''),
            'top_strengths': _clean_list(recruiter_report.get('top_strengths', []), 5),
            'top_concerns': _clean_list(recruiter_report.get('top_concerns', []), 5),
        },
        'cover_letter_summary': {
            'quality_score': cover_letter.get('cover_letter_quality_score', 0),
            'ats_alignment_score': cover_letter.get('ats_alignment_score', 0),
            'recruiter_confidence': cover_letter.get('recruiter_confidence', 0),
        },
        'linkedin_summary': {
            'headline_score': linkedin.get('headline_score', 0),
            'linkedin_score': linkedin.get('linkedin_score', 0),
            'recruiter_visibility_score': linkedin.get('recruiter_visibility_score', 0),
            'quality_notes': _clean_list(linkedin.get('quality_notes', []), 6),
        },
        'interview_plan': {
            'confidence_score': interview.get('confidence_score', 0),
            'readiness_score': interview.get('readiness_score', 0),
            'technical_questions': _clean_list(interview.get('technical_questions', []), 5),
            'behavioral_questions': _clean_list(interview.get('behavioral_questions', []), 5),
            'interview_tips': _clean_list(interview.get('interview_tips', []), 6),
        },
        'recommended_next_steps': _clean_list(result.get('recommended_next_steps', []), 6),
    }
