from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from core.exceptions import AppError
from observability.error_reporting import categorize_exception, mask_sensitive_text
from observability.logging_config import configure_logging
from observability.performance_metrics import metrics_registry
from observability.request_context import get_request_id


logger = configure_logging()


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        metrics_registry.record_failure(request.url.path, exc.category, exc.message)
        logger.error(
            exc.message,
            extra={
                "endpoint": request.url.path,
                "http_method": request.method,
                "status_code": exc.status_code,
                "success": False,
                "error_category": exc.category,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "request_id": get_request_id(),
            },
        )

    @app.exception_handler(HTTPException)
    async def handle_http_error(request: Request, exc: HTTPException):
        metrics_registry.record_failure(request.url.path, "validation_error" if exc.status_code < 500 else "internal_error", str(exc.detail))
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": get_request_id()},
        )

    @app.exception_handler(Exception)
    async def handle_generic_error(request: Request, exc: Exception):
        category = categorize_exception(exc)
        metrics_registry.record_failure(request.url.path, category, str(exc))
        logger.exception(
            mask_sensitive_text(str(exc)),
            extra={
                "endpoint": request.url.path,
                "http_method": request.method,
                "status_code": 500,
                "success": False,
                "error_category": category,
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR" if category == "internal_error" else category.upper(),
                "message": "Something went wrong. Please try again.",
                "request_id": get_request_id(),
            },
        )
