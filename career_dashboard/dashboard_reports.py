from __future__ import annotations


def build_user_summary(assets: list[dict], statistics: dict, recent_activity: list[dict]) -> dict:
    latest = assets[0] if assets else {}
    return {
        'total_assets': len(assets),
        'latest_role': latest.get('role', ''),
        'latest_country': latest.get('country', ''),
        'last_updated': latest.get('updated_at', ''),
        'applications_prepared': statistics.get('applications_prepared', 0),
        'recent_activity_count': len(recent_activity),
    }
