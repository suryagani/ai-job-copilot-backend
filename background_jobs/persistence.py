from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from services.supabase_client import SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL


JOB_DATA_DIR = Path("background_jobs_data")
LOCAL_JOBS_FILE = JOB_DATA_DIR / "jobs.json"
LOCAL_EVENTS_FILE = JOB_DATA_DIR / "job_events.json"
SUPABASE_JOBS_TABLE = "background_jobs"
SUPABASE_EVENTS_TABLE = "background_job_events"


def _ensure_storage() -> None:
    JOB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOCAL_JOBS_FILE.exists():
        LOCAL_JOBS_FILE.write_text("[]", encoding="utf-8")
    if not LOCAL_EVENTS_FILE.exists():
        LOCAL_EVENTS_FILE.write_text("[]", encoding="utf-8")


def _read_json(path: Path) -> list[dict]:
    _ensure_storage()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_json(path: Path, payload: list[dict]) -> None:
    _ensure_storage()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BackgroundJobPersistence:
    def __init__(self):
        self._supabase_enabled = bool(SUPABASE_URL and (SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY))

    def _supabase_headers(self) -> dict[str, str]:
        token = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
        return {
            "apikey": token,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _list_supabase_rows(self, table: str) -> list[dict]:
        if not self._supabase_enabled:
            return []
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(
                    f"{SUPABASE_URL}/rest/v1/{table}",
                    headers=self._supabase_headers(),
                    params={"select": "*", "order": "created_at.asc"},
                )
            if response.status_code >= 400:
                return []
            return response.json() or []
        except Exception:
            return []

    def _upsert_supabase(self, table: str, record: dict[str, Any], key: str) -> bool:
        if not self._supabase_enabled:
            return False
        try:
            headers = self._supabase_headers()
            headers["Prefer"] = f"resolution=merge-duplicates,return=representation"
            with httpx.Client(timeout=20) as client:
                response = client.post(
                    f"{SUPABASE_URL}/rest/v1/{table}",
                    headers=headers,
                    params={"on_conflict": key},
                    json=record,
                )
            return response.status_code < 400
        except Exception:
            return False

    def load_jobs(self) -> list[dict]:
        rows = self._list_supabase_rows(SUPABASE_JOBS_TABLE)
        if rows:
            return rows
        return _read_json(LOCAL_JOBS_FILE)

    def save_job(self, record: dict[str, Any]) -> None:
        saved = self._upsert_supabase(SUPABASE_JOBS_TABLE, record, "job_id")
        jobs = _read_json(LOCAL_JOBS_FILE)
        updated = False
        for idx, item in enumerate(jobs):
            if str(item.get("job_id", "")).strip() == str(record.get("job_id", "")).strip():
                jobs[idx] = record
                updated = True
                break
        if not updated:
            jobs.append(record)
        jobs.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        _write_json(LOCAL_JOBS_FILE, jobs)
        if not saved:
            return

    def load_events(self) -> list[dict]:
        rows = self._list_supabase_rows(SUPABASE_EVENTS_TABLE)
        if rows:
            return rows
        return _read_json(LOCAL_EVENTS_FILE)

    def append_event(self, event_name: str, job_record: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        event = {
            "id": str(uuid.uuid4()),
            "job_id": str(job_record.get("job_id", "")).strip(),
            "job_type": str(job_record.get("job_type", "")).strip(),
            "user_id": str(job_record.get("user_id", "")).strip() or None,
            "session_id": str(job_record.get("session_id", "")).strip() or None,
            "event_name": str(event_name or "").strip(),
            "status": str(job_record.get("status", "")).strip(),
            "retry_count": int(job_record.get("retry_count", 0) or 0),
            "processing_time_ms": float(job_record.get("processing_time_ms", 0) or 0),
            "created_at": _now_iso(),
            "metadata_json": metadata or {},
        }
        self._upsert_supabase(SUPABASE_EVENTS_TABLE, event, "id")
        events = _read_json(LOCAL_EVENTS_FILE)
        events.append(event)
        events.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        _write_json(LOCAL_EVENTS_FILE, events)
        return event
