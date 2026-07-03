from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import uuid

from .version_manager import enrich_versions, next_version

DASHBOARD_DIR = Path('career_dashboard_data')
ASSETS_FILE = DASHBOARD_DIR / 'assets.json'
HISTORY_FILE = DASHBOARD_DIR / 'history.json'


def _ensure_storage() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    if not ASSETS_FILE.exists():
        ASSETS_FILE.write_text('[]', encoding='utf-8')
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text('[]', encoding='utf-8')


def _read_json(path: Path) -> list[dict]:
    _ensure_storage()
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []


def _write_json(path: Path, payload: list[dict]) -> None:
    _ensure_storage()
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_list(values, limit: int | None = None) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or '').strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit] if limit else cleaned


def _available_actions(files: dict) -> list[str]:
    actions = ['duplicate', 'delete']
    if files.get('pdf_path'):
        actions.append('download_pdf')
    if files.get('docx_path'):
        actions.append('download_docx')
    if files.get('html_path'):
        actions.append('open_html')
    if files.get('json_path'):
        actions.append('download_json')
    if files.get('readme_path'):
        actions.append('download_readme')
    return actions


def _asset_title(asset_type: str, role: str = '', company_name: str = '') -> str:
    label = {
        'resume': 'Resume',
        'cover_letter': 'Cover Letter',
        'linkedin': 'LinkedIn Optimization',
        'portfolio': 'Portfolio',
        'interview': 'Interview Prep',
        'job_description': 'Job Description',
    }.get(asset_type, 'Career Asset')
    if company_name and asset_type in {'cover_letter', 'interview', 'job_description'}:
        return f"{role or label} - {company_name}".strip(' -')
    if role:
        return f"{role} {label}".strip()
    return label


def _extract_scores(payload: dict | None) -> tuple[int, int]:
    payload = payload or {}
    def clamp(value):
        try:
            return max(0, min(100, int(value)))
        except Exception:
            return 0
    ats_score = clamp(payload.get('ats_score_estimate', payload.get('ats_score', 0)))
    recruiter_score = clamp(payload.get('recruiter_score', payload.get('recruiter_confidence', 0)))
    return ats_score, recruiter_score


def append_history(event_type: str, asset_id: str = '', title: str = '', asset_type: str = '', role: str = '', country: str = '', metadata: dict | None = None) -> None:
    history = _read_json(HISTORY_FILE)
    history.append({
        'id': str(uuid.uuid4()),
        'timestamp': _now_iso(),
        'event_type': event_type,
        'asset_id': asset_id,
        'title': title,
        'asset_type': asset_type,
        'role': role,
        'country': country,
        'metadata': metadata or {},
    })
    history.sort(key=lambda item: item.get('timestamp', ''), reverse=True)
    _write_json(HISTORY_FILE, history)


def register_asset(asset_type: str, candidate_data, payload: dict, files: dict | None = None, text_key: str = '', metadata: dict | None = None, origin: str = 'api') -> dict:
    assets = _read_json(ASSETS_FILE)
    full_name = str(getattr(candidate_data, 'full_name', '') or '').strip()
    role = str(getattr(candidate_data, 'target_role', '') or '').strip()
    country = str(getattr(candidate_data, 'target_country', '') or '').strip()
    company_name = str(getattr(candidate_data, 'company_name', '') or '').strip()
    version, version_key = next_version(assets, asset_type, full_name, role, country)
    ats_score, recruiter_score = _extract_scores(payload)
    summary = str(payload.get(text_key, '') if text_key else '').strip()[:500]
    record = {
        'id': str(uuid.uuid4()),
        'asset_type': asset_type,
        'title': _asset_title(asset_type, role, company_name),
        'created_at': _now_iso(),
        'updated_at': _now_iso(),
        'version': version,
        'version_label': f'V{version}',
        'version_key': version_key,
        'full_name': full_name,
        'role': role,
        'country': country,
        'company_name': company_name,
        'ats_score': ats_score,
        'recruiter_score': recruiter_score,
        'origin': origin,
        'files': files or {},
        'summary': summary,
        'metadata': metadata or {},
        'available_actions': _available_actions(files or {}),
    }
    assets.append(record)
    _write_json(ASSETS_FILE, assets)
    append_history('asset_created', asset_id=record['id'], title=record['title'], asset_type=asset_type, role=role, country=country, metadata={'version': version})
    return record


def register_job_description(candidate_data, job_description: str, job_intelligence: dict | None = None) -> dict | None:
    text = str(job_description or '').strip()
    if not text:
        return None
    assets = _read_json(ASSETS_FILE)
    role = str(getattr(candidate_data, 'target_role', '') or '').strip()
    country = str(getattr(candidate_data, 'target_country', '') or '').strip()
    company_name = str(getattr(candidate_data, 'company_name', '') or '').strip()
    fingerprint = hashlib.sha256(text.encode('utf-8')).hexdigest()
    for asset in assets:
        if asset.get('asset_type') == 'job_description' and asset.get('metadata', {}).get('fingerprint') == fingerprint:
            return asset
    version, version_key = next_version(assets, 'job_description', '', role, country)
    record = {
        'id': str(uuid.uuid4()),
        'asset_type': 'job_description',
        'title': _asset_title('job_description', role, company_name),
        'created_at': _now_iso(),
        'updated_at': _now_iso(),
        'version': version,
        'version_label': f'V{version}',
        'version_key': version_key,
        'full_name': '',
        'role': role,
        'country': country,
        'company_name': company_name,
        'ats_score': 0,
        'recruiter_score': 0,
        'origin': 'api',
        'files': {},
        'summary': text[:500],
        'metadata': {
            'fingerprint': fingerprint,
            'job_level': str((job_intelligence or {}).get('job_level', '')).strip(),
            'industry': str((job_intelligence or {}).get('industry', '')).strip(),
        },
        'available_actions': ['duplicate', 'delete'],
    }
    assets.append(record)
    _write_json(ASSETS_FILE, assets)
    append_history('job_description_saved', asset_id=record['id'], title=record['title'], asset_type='job_description', role=role, country=country, metadata={'version': version})
    return record


def _build_inferred_asset(asset_type: str, stem: str, files: dict, created_at: str) -> dict:
    title = stem.replace('-', ' ').title()
    return {
        'id': f'inferred-{asset_type}-{stem}',
        'asset_type': asset_type,
        'title': title,
        'created_at': created_at,
        'updated_at': created_at,
        'version': 1,
        'version_label': 'V1',
        'version_key': f'inferred|{asset_type}|{stem}',
        'full_name': '',
        'role': '',
        'country': '',
        'company_name': '',
        'ats_score': 0,
        'recruiter_score': 0,
        'origin': 'inferred',
        'files': files,
        'summary': '',
        'metadata': {},
        'available_actions': _available_actions(files),
    }


def _group_paths(directory: Path, asset_type: str) -> list[dict]:
    if not directory.exists():
        return []
    groups = {}
    for path in directory.iterdir():
        if path.is_dir():
            continue
        suffix = path.suffix.lower()
        stem = path.stem
        key = stem
        if asset_type == 'portfolio' and stem.endswith('-README'):
            key = stem[:-7]
        group = groups.setdefault(key, {'created_at': datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(), 'files': {}})
        if suffix == '.pdf':
            group['files']['pdf_path'] = str(path.resolve())
        elif suffix == '.docx':
            group['files']['docx_path'] = str(path.resolve())
        elif suffix == '.html':
            group['files']['html_path'] = str(path.resolve())
        elif suffix == '.json':
            group['files']['json_path'] = str(path.resolve())
        elif suffix in {'.md', '.markdown'}:
            group['files']['readme_path'] = str(path.resolve())
    return [_build_inferred_asset(asset_type, key, value['files'], value['created_at']) for key, value in groups.items()]


def infer_assets_from_rendered(existing_assets: list[dict]) -> list[dict]:
    known_paths = set()
    for asset in existing_assets:
        for path_value in (asset.get('files') or {}).values():
            known_paths.add(str(path_value).lower())
    inferred = []
    rendered = Path('rendered')
    mapping = {
        'resume': rendered,
        'cover_letter': rendered / 'cover_letters',
        'linkedin': rendered / 'linkedin',
        'interview': rendered / 'interview',
        'portfolio': rendered / 'portfolio',
    }
    for asset_type, directory in mapping.items():
        for asset in _group_paths(directory, asset_type):
            paths = {str(value).lower() for value in asset.get('files', {}).values()}
            if not paths or paths & known_paths:
                continue
            inferred.append(asset)
    return inferred


def list_assets(asset_type: str | None = None) -> list[dict]:
    assets = _read_json(ASSETS_FILE)
    assets.extend(infer_assets_from_rendered(assets))
    assets = enrich_versions(assets)
    assets.sort(key=lambda item: item.get('created_at', ''), reverse=True)
    if asset_type:
        return [asset for asset in assets if asset.get('asset_type') == asset_type]
    return assets


def list_history() -> list[dict]:
    history = _read_json(HISTORY_FILE)
    history.sort(key=lambda item: item.get('timestamp', ''), reverse=True)
    return history
