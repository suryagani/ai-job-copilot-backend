# Backend Architecture

Generated: 2026-08-08T21:39:10+00:00

## Summary
- App version target: `2.2`
- Total API route-method entries: `58`
- Route groups: `{'ACTIVE': 34, 'ADMIN': 12, 'LEGACY': 7, 'BACKGROUND': 5}`
- Engine groups: `{'ACTIVE': 15, 'LEGACY': 1}`

## Core Layers
- `main.py`: FastAPI entrypoint, request models, endpoint orchestration, intelligence helpers, export helpers, rate limiting, idempotency, and backward-compatible legacy routes.
- `background_jobs/`: additive long-running workflow abstraction for portfolio and job application processing, now with persisted metadata plus in-memory result handling.
- `resume_models/`: writing-model layer for graduate, technical, career-switcher, business, and executive resume variants.
- `resume_designer/`: ATS-safe layout and rendering layer for PDF and DOCX exports.
- `cover_letter/`, `linkedin_engine/`, `interview_engine/`, and `job_application_engine/`: downstream career-asset generators built on the shared resume intelligence stack.
- `career_dashboard/`, `auth_cloud_sync.py`, and `analytics_engine.py`: persistence, dashboard storage, authentication, and admin analytics support.
- `observability/`, `services/`, and `core/`: structured logging, retry policy, AI client wrapper, and safe error handling.

## Background Job Notes
- Metadata persistence survives restart where local JSON storage or Supabase-backed REST persistence is available.
- Full private generated content is intentionally not persisted in the background-job metadata layer; restart recovery prefers artifact references and falls back to compact previews.
- Synchronous endpoints remain unchanged for website and extension compatibility.

## Compatibility Notes
- Legacy job-alert and profile endpoints remain present during backend freeze.
- Chrome extension files are not part of the V2.2 backend change set.