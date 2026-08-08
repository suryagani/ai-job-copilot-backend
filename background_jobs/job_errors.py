from __future__ import annotations

from core.exceptions import AppError


class JobNotFoundError(AppError):
    def __init__(self):
        super().__init__("JOB_NOT_FOUND", "Background job not found.", status_code=404, category="validation_error")


class JobExpiredError(AppError):
    def __init__(self):
        super().__init__("JOB_EXPIRED", "This background job has expired.", status_code=410, category="validation_error")
