from __future__ import annotations

from collections import Counter


def compute_career_statistics(assets: list[dict]) -> dict:
    resumes = [asset for asset in assets if asset.get('asset_type') == 'resume']
    ats_scores = [int(asset.get('ats_score', 0) or 0) for asset in resumes if int(asset.get('ats_score', 0) or 0) > 0]
    recruiter_scores = [int(asset.get('recruiter_score', 0) or 0) for asset in assets if int(asset.get('recruiter_score', 0) or 0) > 0]
    roles = [asset.get('role', '') for asset in assets if asset.get('role')]
    countries = [asset.get('country', '') for asset in assets if asset.get('country')]

    role_counter = Counter(roles)
    country_counter = Counter(countries)

    improvement_trend = 'Stable'
    if len(ats_scores) >= 2 and ats_scores[0] > ats_scores[-1]:
        improvement_trend = 'Improving'
    elif len(ats_scores) >= 2 and ats_scores[0] < ats_scores[-1]:
        improvement_trend = 'Declining'

    return {
        'total_resumes': len([asset for asset in assets if asset.get('asset_type') == 'resume']),
        'total_cover_letters': len([asset for asset in assets if asset.get('asset_type') == 'cover_letter']),
        'total_linkedin_reports': len([asset for asset in assets if asset.get('asset_type') == 'linkedin']),
        'total_portfolios': len([asset for asset in assets if asset.get('asset_type') == 'portfolio']),
        'total_interview_reports': len([asset for asset in assets if asset.get('asset_type') == 'interview']),
        'total_job_descriptions': len([asset for asset in assets if asset.get('asset_type') == 'job_description']),
        'average_ats_score': round(sum(ats_scores) / len(ats_scores), 1) if ats_scores else 0,
        'average_recruiter_score': round(sum(recruiter_scores) / len(recruiter_scores), 1) if recruiter_scores else 0,
        'applications_prepared': len([asset for asset in assets if asset.get('asset_type') in {'resume', 'cover_letter', 'interview'}]),
        'most_common_target_role': role_counter.most_common(1)[0][0] if role_counter else '',
        'most_common_country': country_counter.most_common(1)[0][0] if country_counter else '',
        'improvement_trend': improvement_trend,
    }
