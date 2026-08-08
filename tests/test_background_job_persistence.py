import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from background_jobs.job_store import JobStore


class BackgroundJobPersistenceTests(unittest.TestCase):
    def test_completed_job_metadata_survives_store_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                store = JobStore(ttl_hours=24)
                payload = {"target_role": "DevOps Engineer"}
                job, _ = store.create_or_reuse("portfolio", "req-1", "", "session-a", "idem-1", payload)
                store.start(job.job_id, queue_wait_ms=5)
                store.complete(
                    job.job_id,
                    result={"portfolio_pdf_path": "resume.pdf", "portfolio_json_path": "portfolio.json"},
                    result_reference=["portfolio.json", "resume.pdf"],
                    result_preview={"portfolio_pdf_path": "resume.pdf", "portfolio_docx_path": "", "portfolio_html_path": "", "portfolio_readme_path": "", "portfolio_json_path": "portfolio.json", "portfolio_score": 84, "recruiter_score": 80, "selected_theme": "Developer", "professional_bio": "", "about_me": "", "personal_tagline": "", "project_showcase": [], "project_case_studies": [], "github_readme": "", "personal_website_content": "", "skills_section": [], "timeline": [], "contact_section": [], "professional_footer": "", "seo_meta_title": "", "seo_meta_description": "", "quality_notes": []},
                    processing_time_ms=120,
                )

                persisted = json.loads(Path("background_jobs_data/jobs.json").read_text(encoding="utf-8"))
                self.assertEqual(len(persisted), 1)
                self.assertEqual(persisted[0]["status"], "completed")

                restarted_store = JobStore(ttl_hours=24)
                loaded = restarted_store.get(job.job_id)
                self.assertEqual(loaded.status, "completed")
                self.assertEqual(loaded.result_reference[0], "portfolio.json")
                self.assertEqual(restarted_store.get_result(job.job_id)["portfolio_score"], 84)
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
