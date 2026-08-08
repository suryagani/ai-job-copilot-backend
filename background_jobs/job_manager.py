from __future__ import annotations

from typing import Callable

from observability.performance_metrics import metrics_registry

from .job_runner import JobRunner
from .job_store import JobStore


class BackgroundJobManager:
    def __init__(self, ttl_hours: int = 24):
        self.store = JobStore(ttl_hours=ttl_hours)
        self.runner = JobRunner(self.store)

    def create_job(self, job_type: str, request_id: str, user_id: str, session_id: str, idempotency_key: str, payload: dict, worker: Callable[[Callable[[str, int, str], None]], dict]) -> tuple[dict, bool]:
        job, reused = self.store.create_or_reuse(job_type, request_id, user_id, session_id, idempotency_key, payload)
        initial_payload = {
            "job_id": job.job_id,
            "status": "queued",
            "progress_percent": 0,
            "message": "Your request has been queued.",
        }
        if not reused:
            metrics_registry.increment("background_jobs_created")
            self.runner.start(job.job_id, worker)
            return initial_payload, False
        payload = job.status_payload()
        payload["message"] = job.message
        return payload, True

    def get_status(self, job_id: str) -> dict:
        return self.store.get(job_id).status_payload()

    def get_result(self, job_id: str) -> dict:
        return self.store.get_result(job_id)

    def cancel(self, job_id: str) -> dict:
        self.store.cancel(job_id)
        return self.store.get(job_id).status_payload()

    def background_metrics(self) -> dict:
        return self.store.background_metrics()
