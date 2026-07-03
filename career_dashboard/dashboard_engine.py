from __future__ import annotations

from .career_assets import list_assets, list_history
from .career_timeline import build_career_timeline, build_recent_activity
from .dashboard_reports import build_user_summary
from .dashboard_stats import compute_career_statistics


def _library(assets: list[dict], asset_type: str) -> list[dict]:
    return [asset for asset in assets if asset.get('asset_type') == asset_type]


def get_dashboard_snapshot() -> dict:
    assets = list_assets()
    history = list_history()
    statistics = compute_career_statistics(assets)
    timeline = build_career_timeline(assets, history)
    recent_activity = build_recent_activity(timeline)
    return {
        'user_summary': build_user_summary(assets, statistics, recent_activity),
        'resume_library': _library(assets, 'resume'),
        'cover_letter_library': _library(assets, 'cover_letter'),
        'linkedin_library': _library(assets, 'linkedin'),
        'portfolio_library': _library(assets, 'portfolio'),
        'interview_library': _library(assets, 'interview'),
        'job_description_library': _library(assets, 'job_description'),
        'career_statistics': statistics,
        'career_timeline': timeline,
        'recent_activity': recent_activity,
    }


def get_dashboard_assets() -> dict:
    assets = list_assets()
    return {
        'resume_library': _library(assets, 'resume'),
        'cover_letter_library': _library(assets, 'cover_letter'),
        'linkedin_library': _library(assets, 'linkedin'),
        'portfolio_library': _library(assets, 'portfolio'),
        'interview_library': _library(assets, 'interview'),
        'job_description_library': _library(assets, 'job_description'),
    }


def get_dashboard_timeline() -> list[dict]:
    return build_career_timeline(list_assets(), list_history())


def get_dashboard_statistics() -> dict:
    return compute_career_statistics(list_assets())


def get_dashboard_history() -> list[dict]:
    return list_history()
