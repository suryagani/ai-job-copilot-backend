from __future__ import annotations

from .job_store import JobStore


def cleanup_expired_jobs(store: JobStore) -> None:
    try:
        store.background_metrics()
    except Exception:
        return
