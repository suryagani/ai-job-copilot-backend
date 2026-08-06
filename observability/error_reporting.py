from __future__ import annotations

import re


SENSITIVE_PATTERNS = [
    re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"),
    re.compile(r"\b\+?\d[\d\-\s]{6,}\d\b"),
]


def mask_sensitive_text(value: str) -> str:
    text = str(value or "")
    for pattern in SENSITIVE_PATTERNS:
        text = pattern.sub("[masked]", text)
    return text


def categorize_exception(exc: Exception) -> str:
    name = exc.__class__.__name__.lower()
    text = str(exc).lower()
    if "timeout" in text or "timeout" in name:
        return "ai_timeout_error"
    if "auth" in name or "token" in text:
        return "authentication_error"
    if "permission" in text or "forbidden" in text:
        return "authorization_error"
    if "rate" in text and "limit" in text:
        return "rate_limit_error"
    if "openai" in name or "api" in text:
        return "ai_provider_error"
    return "internal_error"
