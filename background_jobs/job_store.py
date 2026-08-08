from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from .job_errors import JobExpiredError, JobNotFoundError
from .job_models import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_EXPIRED,
    JOB_STATUS_FAILED,
    JOB_STATUS_PROCESSING,
    BackgroundJob,
)


class JobStore:
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self._jobs: dict[str, BackgroundJob] = {}
        self._idempotency_map: dict[str, str] = {}
        self._lock = threading.Lock()

    def _cleanup_locked(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.ttl_hours)
        for job in self._jobs.values():
            timestamp = job.completed_at or job.created_at
            if not timestamp:
                continue
            try:
                created = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except Exception:
                continue
            if created < cutoff and job.status in {JOB_STATUS_COMPLETED, JOB_STATUS_FAILED}:
                job.status = JOB_STATUS_EXPIRED
                job.result = None
                job.result_reference = []
                job.message = "This background job has expired."

    @staticmethod
    def payload_digest(payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def create_or_reuse(self, job_type: str, request_id: str, user_id: str, session_id: str, idempotency_key: str, payload: dict[str, Any]) -> tuple[BackgroundJob, bool]:
        digest = self.payload_digest(payload)
        with self._lock:
            self._cleanup_locked()
            idem_key = f"{job_type}:{user_id}:{session_id}:{idempotency_key}:{digest}" if idempotency_key else ""
            if idem_key and idem_key in self._idempotency_map:
                existing = self._jobs.get(self._idempotency_map[idem_key])
                if existing and existing.status != JOB_STATUS_EXPIRED:
                    return existing, True
            job = BackgroundJob(
                job_id=str(uuid.uuid4()),
                job_type=job_type,
                request_id=request_id,
                user_id=user_id,
                session_id=session_id,
                idempotency_key=idempotency_key,
                payload_digest=digest,
            )
            self._jobs[job.job_id] = job
            if idem_key:
                self._idempotency_map[idem_key] = job.job_id
            return job, False

    def start(self, job_id: str, queue_wait_ms: float) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JOB_STATUS_PROCESSING
            job.started_at = datetime.now(timezone.utc).isoformat()
            job.queue_wait_ms = queue_wait_ms
            job.message = "Your request is being processed."

    def update_progress(self, job_id: str, stage: str, progress_percent: int, message: str = "") -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.current_stage = str(stage or job.current_stage)
            job.progress_percent = max(job.progress_percent, min(100, int(progress_percent)))
            if message:
                job.message = message

    def complete(self, job_id: str, result: dict[str, Any], result_reference: list[str], processing_time_ms: float) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JOB_STATUS_COMPLETED
            job.progress_percent = 100
            job.current_stage = JOB_STATUS_COMPLETED
            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.processing_time_ms = processing_time_ms
            job.result = result
            job.result_reference = result_reference
            job.message = "Your result is ready."

    def fail(self, job_id: str, error_code: str, message: str, processing_time_ms: float) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JOB_STATUS_FAILED
            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.processing_time_ms = processing_time_ms
            job.safe_error_code = error_code
            job.safe_error_message = message
            job.message = message

    def cancel(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise JobNotFoundError()
            if job.status in {JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_EXPIRED}:
                return
            job.status = "cancelled"
            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.current_stage = "cancelled"
            job.message = "The background job was cancelled."

    def get(self, job_id: str) -> BackgroundJob:
        with self._lock:
            self._cleanup_locked()
            job = self._jobs.get(job_id)
            if not job:
                raise JobNotFoundError()
            return job

    def get_result(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        if job.status == JOB_STATUS_EXPIRED:
            raise JobExpiredError()
        if job.result is None:
            return {}
        return job.result

    def background_metrics(self) -> dict[str, Any]:
        with self._lock:
            self._cleanup_locked()
            jobs = list(self._jobs.values())
        completed = [job for job in jobs if job.status == JOB_STATUS_COMPLETED]
        failed = [job for job in jobs if job.status == JOB_STATUS_FAILED]
        longest = max(completed, key=lambda item: item.processing_time_ms, default=None)
        return {
            "jobs_created": len(jobs),
            "jobs_completed": len(completed),
            "jobs_failed": len(failed),
            "average_processing_time_ms": round(sum(job.processing_time_ms for job in completed) / len(completed), 2) if completed else 0,
            "longest_running_job": {
                "job_id": longest.job_id,
                "job_type": longest.job_type,
                "processing_time_ms": longest.processing_time_ms,
            } if longest else {},
            "job_failure_rate": round((len(failed) / len(jobs)) * 100, 2) if jobs else 0,
        }
