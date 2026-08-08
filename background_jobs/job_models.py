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
    idempotency_key: str = ""
    payload_digest: str = ""
    queue_wait_ms: float = 0.0
    processing_time_ms: float = 0.0

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

