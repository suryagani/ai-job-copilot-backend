from __future__ import annotations

import threading
import time
from typing import Callable

from core.exceptions import AppError
from observability.logging_config import configure_logging
from observability.performance_metrics import metrics_registry

from .job_store import JobStore


logger = configure_logging()


def _result_preview(result: dict) -> dict:
    if "portfolio_score" in result:
        return {
            "professional_bio": "",
            "about_me": "",
            "personal_tagline": "",
            "project_showcase": [],
            "project_case_studies": [],
            "github_readme": "",
            "personal_website_content": "",
            "skills_section": [],
            "timeline": [],
            "contact_section": [],
            "professional_footer": "",
            "seo_meta_title": result.get("seo_meta_title", ""),
            "seo_meta_description": result.get("seo_meta_description", ""),
            "selected_theme": result.get("selected_theme", ""),
            "portfolio_score": result.get("portfolio_score", 0),
            "recruiter_score": result.get("recruiter_score", 0),
            "quality_notes": [],
            "portfolio_html_path": result.get("portfolio_html_path", ""),
            "portfolio_readme_path": result.get("portfolio_readme_path", ""),
            "portfolio_docx_path": result.get("portfolio_docx_path", ""),
            "portfolio_pdf_path": result.get("portfolio_pdf_path", ""),
            "portfolio_json_path": result.get("portfolio_json_path", ""),
        }
    if "overall_application_score" in result:
        return {
            "optimized_resume": {},
            "cover_letter": {},
            "linkedin_recommendations": {},
            "interview_preparation": {},
            "ats_report": {},
            "recruiter_report": {},
            "overall_application_score": result.get("overall_application_score", 0),
            "job_match_score": result.get("job_match_score", 0),
            "application_readiness": result.get("application_readiness", ""),
            "recommended_next_steps": result.get("recommended_next_steps", []),
            "application_report": {},
            "application_report_pdf_path": result.get("application_report_pdf_path", ""),
            "application_report_docx_path": result.get("application_report_docx_path", ""),
        }
    return {}


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
                result_preview = _result_preview(result)
                elapsed = round((time.perf_counter() - started) * 1000, 2)
                self.store.complete(job_id, result, result_refs, result_preview, elapsed)
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
