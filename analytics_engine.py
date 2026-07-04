from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

ANALYTICS_DIR = Path('analytics_data')
ANALYTICS_FILE = ANALYTICS_DIR / 'analytics_events.json'
AUTH_USERS_FILE = Path('auth_cloud_sync_data') / 'users.json'

GENERATION_EVENTS = {
    'resume_builder_completed',
    'resume_optimizer_completed',
    'cover_letter_generated',
    'linkedin_optimized',
    'interview_prep_generated',
    'portfolio_generated',
    'job_application_prepared',
}
DOWNLOAD_EVENTS = {'resume_downloaded_pdf', 'resume_downloaded_docx'}


def _ensure_storage() -> None:
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    if not ANALYTICS_FILE.exists():
        ANALYTICS_FILE.write_text('[]', encoding='utf-8')


def _read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []


def _write_json(path: Path, payload: list[dict]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: str) -> str:
    return str(value or '').strip()


def _clean_int(value) -> int | None:
    try:
        parsed = int(value)
    except Exception:
        return None
    return parsed


def _sample_events() -> list[dict]:
    return [
        {
            'id': str(uuid.uuid4()),
            'user_id': 'sample-user-1',
            'session_id': 'sample-session-1',
            'event_name': 'resume_builder_completed',
            'tool_name': 'resume_builder',
            'target_role': 'Business Analyst',
            'target_country': 'India',
            'resume_model': 'Business Professional Resume',
            'ats_score': 84,
            'recruiter_score': 82,
            'created_at': '2026-07-04T10:00:00+00:00',
            'metadata_json': {'source': 'sample'},
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': 'sample-user-2',
            'session_id': 'sample-session-2',
            'event_name': 'linkedin_optimized',
            'tool_name': 'linkedin_optimizer',
            'target_role': 'DevOps Engineer',
            'target_country': 'United Kingdom',
            'resume_model': '',
            'ats_score': 0,
            'recruiter_score': 79,
            'created_at': '2026-07-04T10:20:00+00:00',
            'metadata_json': {'source': 'sample'},
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': 'sample-user-1',
            'session_id': 'sample-session-1',
            'event_name': 'resume_downloaded_pdf',
            'tool_name': 'resume_builder',
            'target_role': 'Business Analyst',
            'target_country': 'India',
            'resume_model': 'Business Professional Resume',
            'ats_score': 84,
            'recruiter_score': 82,
            'created_at': '2026-07-04T10:22:00+00:00',
            'metadata_json': {'source': 'sample'},
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': None,
            'session_id': 'sample-session-3',
            'event_name': 'generation_failed',
            'tool_name': 'resume_optimizer',
            'target_role': 'Project Manager',
            'target_country': 'Canada',
            'resume_model': '',
            'ats_score': 0,
            'recruiter_score': 0,
            'created_at': '2026-07-04T11:00:00+00:00',
            'metadata_json': {'source': 'sample', 'status_code': 500},
        },
    ]


def list_analytics_events(include_sample: bool = False) -> list[dict]:
    _ensure_storage()
    events = _read_json(ANALYTICS_FILE)
    if events:
        events.sort(key=lambda item: item.get('created_at', ''), reverse=True)
        return events
    return _sample_events() if include_sample else []


def track_analytics_event(
    event_name: str,
    tool_name: str,
    session_id: str = '',
    user_id: str | None = None,
    target_role: str = '',
    target_country: str = '',
    resume_model: str = '',
    ats_score=None,
    recruiter_score=None,
    metadata_json: dict | None = None,
) -> dict:
    _ensure_storage()
    events = _read_json(ANALYTICS_FILE)
    record = {
        'id': str(uuid.uuid4()),
        'user_id': _clean_text(user_id) or None,
        'session_id': _clean_text(session_id) or f'server-{uuid.uuid4()}',
        'event_name': _clean_text(event_name),
        'tool_name': _clean_text(tool_name),
        'target_role': _clean_text(target_role),
        'target_country': _clean_text(target_country),
        'resume_model': _clean_text(resume_model),
        'ats_score': _clean_int(ats_score),
        'recruiter_score': _clean_int(recruiter_score),
        'created_at': _now_iso(),
        'metadata_json': metadata_json or {},
    }
    events.append(record)
    events.sort(key=lambda item: item.get('created_at', ''), reverse=True)
    _write_json(ANALYTICS_FILE, events)
    return record


def _count_total_users(events: list[dict]) -> int:
    auth_users = _read_json(AUTH_USERS_FILE)
    event_users = {str(item.get('user_id', '')).strip() for item in events if str(item.get('user_id', '')).strip()}
    auth_user_ids = {str(item.get('id', '')).strip() for item in auth_users if str(item.get('id', '')).strip()}
    return len(auth_user_ids | event_users)


def analytics_summary(include_sample: bool = False) -> dict:
    events = list_analytics_events(include_sample=include_sample)
    generation_events = [item for item in events if item.get('event_name') in GENERATION_EVENTS]
    downloads = [item for item in events if item.get('event_name') in DOWNLOAD_EVENTS]
    ats_scores = [int(item['ats_score']) for item in generation_events if isinstance(item.get('ats_score'), int) and item.get('ats_score') is not None and int(item.get('ats_score') or 0) > 0]
    recruiter_scores = [int(item['recruiter_score']) for item in generation_events if isinstance(item.get('recruiter_score'), int) and item.get('recruiter_score') is not None and int(item.get('recruiter_score') or 0) > 0]
    tool_counter = Counter(item.get('tool_name', '') for item in generation_events if item.get('tool_name'))
    return {
        'total_users': _count_total_users(events),
        'total_generations': len(generation_events),
        'resume_downloads': len(downloads),
        'average_ats_score': round(sum(ats_scores) / len(ats_scores), 1) if ats_scores else 0,
        'average_recruiter_score': round(sum(recruiter_scores) / len(recruiter_scores), 1) if recruiter_scores else 0,
        'most_used_tool': tool_counter.most_common(1)[0][0] if tool_counter else '',
        'top_countries': analytics_countries(include_sample=include_sample)[:5],
        'top_roles': analytics_roles(include_sample=include_sample)[:5],
    }


def analytics_tool_usage(include_sample: bool = False) -> list[dict]:
    events = list_analytics_events(include_sample=include_sample)
    grouped = {}
    for item in events:
        tool_name = _clean_text(item.get('tool_name', ''))
        if not tool_name:
            continue
        grouped.setdefault(tool_name, {'tool_name': tool_name, 'count': 0, 'last_used_at': ''})
        grouped[tool_name]['count'] += 1
        grouped[tool_name]['last_used_at'] = max(grouped[tool_name]['last_used_at'], item.get('created_at', ''))
    return sorted(grouped.values(), key=lambda item: (-item['count'], item['tool_name']))


def analytics_countries(include_sample: bool = False) -> list[dict]:
    events = list_analytics_events(include_sample=include_sample)
    counter = Counter(_clean_text(item.get('target_country', '')) for item in events if _clean_text(item.get('target_country', '')))
    return [{'target_country': country, 'count': count} for country, count in counter.most_common()]


def analytics_roles(include_sample: bool = False) -> list[dict]:
    events = list_analytics_events(include_sample=include_sample)
    counter = Counter(_clean_text(item.get('target_role', '')) for item in events if _clean_text(item.get('target_role', '')))
    return [{'target_role': role, 'count': count} for role, count in counter.most_common()]


def analytics_downloads(include_sample: bool = False) -> dict:
    events = list_analytics_events(include_sample=include_sample)
    pdf_count = len([item for item in events if item.get('event_name') == 'resume_downloaded_pdf'])
    docx_count = len([item for item in events if item.get('event_name') == 'resume_downloaded_docx'])
    return {
        'pdf_downloads': pdf_count,
        'docx_downloads': docx_count,
        'total_downloads': pdf_count + docx_count,
    }


def analytics_errors(include_sample: bool = False) -> list[dict]:
    events = list_analytics_events(include_sample=include_sample)
    return [
        {
            'id': item.get('id', ''),
            'tool_name': item.get('tool_name', ''),
            'target_role': item.get('target_role', ''),
            'target_country': item.get('target_country', ''),
            'created_at': item.get('created_at', ''),
            'metadata_json': item.get('metadata_json', {}),
        }
        for item in events
        if item.get('event_name') == 'generation_failed'
    ]


def analytics_recent_events(include_sample: bool = False, limit: int = 30) -> list[dict]:
    events = list_analytics_events(include_sample=include_sample)
    recent = []
    for item in events[:limit]:
        recent.append(
            {
                'id': item.get('id', ''),
                'user_id': item.get('user_id', ''),
                'session_id': item.get('session_id', ''),
                'event_name': item.get('event_name', ''),
                'tool_name': item.get('tool_name', ''),
                'target_role': item.get('target_role', ''),
                'target_country': item.get('target_country', ''),
                'resume_model': item.get('resume_model', ''),
                'ats_score': item.get('ats_score', 0),
                'recruiter_score': item.get('recruiter_score', 0),
                'created_at': item.get('created_at', ''),
                'metadata_json': item.get('metadata_json', {}),
            }
        )
    return recent
