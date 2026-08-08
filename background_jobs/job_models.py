from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


JOB_STATUS_QUEUED = "queued"
JOB_STATUS_PROCESSING = "processing"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_CANCELLED = "cancelled"
JOB_STATUS_EXPIRED = "expired"

TERMINAL_JOB_STATUSES = {
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_CANCELLED,
    JOB_STATUS_EXPIRED,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BackgroundJob:
    job_id: str
    job_type: str
    request_id: str
    user_id: str = ""
    session_id: str = ""
    status: str = JOB_STATUS_QUEUED
    progress_percent: int = 0
    current_stage: str = JOB_STATUS_QUEUED
    created_at: str = field(default_factory=now_iso)
    started_at: str = ""
    completed_at: str = ""
    retry_count: int = 0
    safe_error_code: str = ""
    safe_error_message: str = ""
    message: str = "Your request has been queued."
    result: dict[str, Any] | None = None
    result_reference: list[str] = field(default_factory=list)
    result_preview: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str = ""
    payload_digest: str = ""
    queue_wait_ms: float = 0.0
    processing_time_ms: float = 0.0

    def to_record(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "current_stage": self.current_stage,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "retry_count": self.retry_count,
            "safe_error_code": self.safe_error_code,
            "safe_error_message": self.safe_error_message,
            "message": self.message,
            "result_reference": list(self.result_reference or []),
            "result_preview": dict(self.result_preview or {}),
            "idempotency_key": self.idempotency_key,
            "payload_digest": self.payload_digest,
            "queue_wait_ms": self.queue_wait_ms,
            "processing_time_ms": self.processing_time_ms,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "BackgroundJob":
        return cls(
            job_id=str(record.get("job_id", "")).strip(),
            job_type=str(record.get("job_type", "")).strip(),
            request_id=str(record.get("request_id", "")).strip(),
            user_id=str(record.get("user_id", "")).strip(),
            session_id=str(record.get("session_id", "")).strip(),
            status=str(record.get("status", JOB_STATUS_QUEUED)).strip() or JOB_STATUS_QUEUED,
            progress_percent=int(record.get("progress_percent", 0) or 0),
            current_stage=str(record.get("current_stage", JOB_STATUS_QUEUED)).strip() or JOB_STATUS_QUEUED,
            created_at=str(record.get("created_at", "")).strip() or now_iso(),
            started_at=str(record.get("started_at", "")).strip(),
            completed_at=str(record.get("completed_at", "")).strip(),
            retry_count=int(record.get("retry_count", 0) or 0),
            safe_error_code=str(record.get("safe_error_code", "")).strip(),
            safe_error_message=str(record.get("safe_error_message", "")).strip(),
            message=str(record.get("message", "Your request has been queued.")).strip() or "Your request has been queued.",
            result=None,
            result_reference=[str(item) for item in (record.get("result_reference") or []) if str(item).strip()],
            result_preview=dict(record.get("result_preview") or {}),
            idempotency_key=str(record.get("idempotency_key", "")).strip(),
            payload_digest=str(record.get("payload_digest", "")).strip(),
            queue_wait_ms=float(record.get("queue_wait_ms", 0) or 0),
            processing_time_ms=float(record.get("processing_time_ms", 0) or 0),
        )

    def status_payload(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "current_stage": self.current_stage,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "retry_count": self.retry_count,
            "message": self.message,
        }
