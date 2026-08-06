from __future__ import annotations

import time

from core.exceptions import AIProviderTemporaryError
from observability.logging_config import configure_logging
from observability.performance_metrics import metrics_registry
from services.retry_policy import retry_sleep, should_retry_exception


logger = configure_logging()


class _CompletionsProxy:
    def __init__(self, inner):
        self.inner = inner

    def create(self, **kwargs):
        max_retries = 2
        model = kwargs.get("model", "")
        started = time.perf_counter()
        for attempt in range(max_retries + 1):
            try:
                response = self.inner.create(**kwargs)
                metrics_registry.increment("ai_calls_total")
                return response
            except Exception as exc:
                retryable = attempt < max_retries and should_retry_exception(exc)
                logger.warning(
                    f"AI call failed on attempt {attempt + 1}",
                    extra={
                        "ai_model_used": model,
                        "retry_count": attempt,
                        "success": False,
                        "error_category": "ai_provider_error",
                    },
                )
                metrics_registry.increment("ai_retries_total")
                if not retryable:
                    duration_ms = round((time.perf_counter() - started) * 1000, 2)
                    metrics_registry.record_failure("openai", "ai_provider_error", str(exc))
                    logger.error(
                        "AI call exhausted retries",
                        extra={"ai_model_used": model, "duration_ms": duration_ms, "retry_count": attempt},
                    )
                    raise AIProviderTemporaryError()
                retry_sleep(attempt + 1)


class _ChatProxy:
    def __init__(self, inner):
        self.completions = _CompletionsProxy(inner.completions)


class RetryingOpenAIProxy:
    def __init__(self, inner):
        self._inner = inner
        self.chat = _ChatProxy(inner.chat)


def build_openai_client(inner_client):
    return RetryingOpenAIProxy(inner_client)
