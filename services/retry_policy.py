from __future__ import annotations

import random
import time


def should_retry_exception(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(token in text for token in ("timeout", "tempor", "connection reset", "429", "500", "502", "503", "504"))


def retry_sleep(attempt: int) -> None:
    base = min(1.5, 0.35 * (2 ** max(0, attempt - 1)))
    time.sleep(base + random.uniform(0.05, 0.15))
