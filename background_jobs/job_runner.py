from __future__ import annotations

import threading
import time
from typing import Callable

from core.exceptions import AppError
from observability.logging_config import configure_logging
from observability.performance_metrics import metrics_registry

from .job_store import JobStore


logger = configure_logging()


class JobRunner:
    def __init__(self, store: JobStore):
        self.store = store

    def start(self, job_id: str, func: Callable[[Callable[[str, int, str], None]], dict]) -> None:
        def _target():
            started = time.perf_counter()
            try:
                self.store.start(job_id, queue_wait_ms=0)
                result = func(lambda stage, percent, message="": self.store.update_progress(job_id, stage, percent, message))
                result_refs = sorted({str(value) for key, value in result.items() if key.endswith("_path") and str(value).strip()})
                elapsed = round((time.perf_counter() - started) * 1000, 2)
                self.store.complete(job_id, result, result_refs, elapsed)
                metrics_registry.increment("background_jobs_completed")
                logger.info("background_job.completed", extra={"job_id": job_id, "success": True})
            except AppError as exc:
                elapsed = round((time.perf_counter() - started) * 1000, 2)
                self.store.fail(job_id, exc.error_code, exc.message, elapsed)
                metrics_registry.increment("background_jobs_failed")
                logger.error("background_job.failed", extra={"job_id": job_id, "success": False, "error_category": exc.category})
            except Exception:
                elapsed = round((time.perf_counter() - started) * 1000, 2)
                self.store.fail(job_id, "INTERNAL_ERROR", "Something went wrong. Please try again.", elapsed)
                metrics_registry.increment("background_jobs_failed")
                logger.exception("background_job.failed", extra={"job_id": job_id, "success": False, "error_category": "internal_error"})

        thread = threading.Thread(target=_target, daemon=True, name=f"bg-job-{job_id[:8]}")
        thread.start()
