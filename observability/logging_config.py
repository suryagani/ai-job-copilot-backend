from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from .request_context import get_request_id, get_session_id, get_user_id


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "") or get_request_id(),
            "authenticated_user_id": getattr(record, "authenticated_user_id", "") or get_user_id(),
            "anonymous_session_id": getattr(record, "anonymous_session_id", "") or get_session_id(),
        }
        for key in (
            "endpoint",
            "http_method",
            "status_code",
            "duration_ms",
            "tool_name",
            "ai_model_used",
            "ai_call_count",
            "retry_count",
            "document_export_type",
            "success",
            "error_category",
        ):
            value = getattr(record, key, None)
            if value is not None and value != "":
                payload[key] = value
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("ai_job_copilot")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
