from __future__ import annotations


class AppError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 500, category: str = "internal_error"):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.category = category


class RateLimitExceeded(AppError):
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__("RATE_LIMIT", message, status_code=429, category="rate_limit_error")


class AIProviderTemporaryError(AppError):
    def __init__(self, message: str = "The request is taking longer than expected. Please try again."):
        super().__init__("AI_TIMEOUT", message, status_code=504, category="ai_timeout_error")
