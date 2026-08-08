from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .job_errors import JobExpiredError, JobNotFoundError
from .job_models import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_EXPIRED,
    JOB_STATUS_FAILED,
    JOB_STATUS_PROCESSING,
    BackgroundJob,
)
from .persistence import BackgroundJobPersistence


class JobStore:
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self._jobs: dict[str, BackgroundJob] = {}
        self._idempotency_map: dict[str, str] = {}
        self._lock = threading.Lock()
        self.persistence = BackgroundJobPersistence()
        self._load_persisted_jobs()

    def _load_persisted_jobs(self) -> None:
        for record in self.persistence.load_jobs():
            job = BackgroundJob.from_record(record)
            if not job.job_id:
                continue
            self._jobs[job.job_id] = job
            if job.idempotency_key and job.payload_digest:
                idem_key = f"{job.job_type}:{job.user_id}:{job.session_id}:{job.idempotency_key}:{job.payload_digest}"
                self._idempotency_map[idem_key] = job.job_id

    def _persist_job_locked(self, job: BackgroundJob, event_name: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        self.persistence.save_job(job.to_record())
        if event_name:
            self.persistence.append_event(event_name, job.to_record(), metadata=metadata or {})

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
                self._persist_job_locked(job)

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
            self._persist_job_locked(job, event_name="background_job_created")
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
            self._persist_job_locked(job, event_name="background_job_started")

    def update_progress(self, job_id: str, stage: str, progress_percent: int, message: str = "") -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.current_stage = str(stage or job.current_stage)
            job.progress_percent = max(job.progress_percent, min(100, int(progress_percent)))
            if message:
                job.message = message
            self._persist_job_locked(job)

    def complete(self, job_id: str, result: dict[str, Any], result_reference: list[str], result_preview: dict[str, Any], processing_time_ms: float) -> None:
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
            job.result_preview = result_preview or {}
            job.message = "Your result is ready."
            self._persist_job_locked(job, event_name="background_job_completed", metadata={"result_reference_count": len(result_reference)})

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
            self._persist_job_locked(job, event_name="background_job_failed", metadata={"error_code": error_code})

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
            self._persist_job_locked(job, event_name="background_job_cancelled")

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
            job.result = self._load_result_from_references(job.result_reference)
        if job.result is None and job.result_preview:
            return dict(job.result_preview)
        if job.result is None:
            return {}
        return job.result

    @staticmethod
    def _load_result_from_references(references: list[str]) -> dict[str, Any] | None:
        for reference in references:
            path = Path(str(reference or "").strip())
            if not path.exists() or path.suffix.lower() != ".json":
                continue
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(parsed, dict) and (
                    "portfolio_html_path" in parsed
                    or "portfolio_json_path" in parsed
                    or "overall_application_score" in parsed
                    or "optimized_resume" in parsed
                ):
                    return parsed
            except Exception:
                continue
        return None

    def background_metrics(self) -> dict[str, Any]:
        with self._lock:
            self._cleanup_locked()
            jobs = list(self._jobs.values())
        events = self.persistence.load_events()
        completed = [job for job in jobs if job.status == JOB_STATUS_COMPLETED]
        failed = [job for job in jobs if job.status == JOB_STATUS_FAILED]
        longest = max(completed, key=lambda item: item.processing_time_ms, default=None)
        historical_completed = [item for item in events if str(item.get("event_name", "")).strip() == "background_job_completed"]
        historical_failed = [item for item in events if str(item.get("event_name", "")).strip() == "background_job_failed"]
        historical_created = [item for item in events if str(item.get("event_name", "")).strip() == "background_job_created"]
        by_type: dict[str, dict[str, Any]] = {}
        for event in historical_created + historical_completed + historical_failed:
            job_type = str(event.get("job_type", "")).strip() or "unknown"
            bucket = by_type.setdefault(job_type, {"job_type": job_type, "created": 0, "completed": 0, "failed": 0, "average_processing_time_ms": 0})
            if event.get("event_name") == "background_job_created":
                bucket["created"] += 1
            elif event.get("event_name") == "background_job_completed":
                bucket["completed"] += 1
            elif event.get("event_name") == "background_job_failed":
                bucket["failed"] += 1
        for job_type, bucket in by_type.items():
            type_completed = [item for item in historical_completed if str(item.get("job_type", "")).strip() == job_type]
            times = [float(item.get("processing_time_ms", 0) or 0) for item in type_completed if float(item.get("processing_time_ms", 0) or 0) > 0]
            bucket["average_processing_time_ms"] = round(sum(times) / len(times), 2) if times else 0
        return {
            "jobs_created": len(historical_created) or len(jobs),
            "jobs_completed": len(historical_completed) or len(completed),
            "jobs_failed": len(historical_failed) or len(failed),
            "average_processing_time_ms": round(sum(float(item.get("processing_time_ms", 0) or 0) for item in historical_completed) / len(historical_completed), 2) if historical_completed else (round(sum(job.processing_time_ms for job in completed) / len(completed), 2) if completed else 0),
            "longest_running_job": {
                "job_id": longest.job_id,
                "job_type": longest.job_type,
                "processing_time_ms": longest.processing_time_ms,
            } if longest else {},
            "job_failure_rate": round(((len(historical_failed) or len(failed)) / (len(historical_created) or len(jobs))) * 100, 2) if (historical_created or jobs) else 0,
            "historical_by_type": sorted(by_type.values(), key=lambda item: item["job_type"]),
        }
