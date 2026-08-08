import os
import sys
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class JobExpiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.background_job_manager.store._jobs.clear()
        main.background_job_manager.store._idempotency_map.clear()

    def test_job_expiry(self):
        original = main.run_portfolio_workflow
        try:
            def fake_workflow(data, authorization=None, x_session_id=None, progress_callback=None):
                progress_callback("completed", 100, "Done.")
                return {"portfolio_score": 90, "portfolio_pdf_path": "x.pdf", "portfolio_docx_path": "x.docx", "portfolio_html_path": "x.html", "portfolio_readme_path": "x.md", "portfolio_json_path": "x.json"}
            main.run_portfolio_workflow = fake_workflow
            create = self.client.post("/jobs/portfolio", json={"target_role": "DevOps Engineer"}, headers={"X-Session-Id": "bg-f"})
            job_id = create.json()["job_id"]
            for _ in range(20):
                if main.background_job_manager.store.get(job_id).status == "completed":
                    break
                time.sleep(0.05)
            job = main.background_job_manager.store.get(job_id)
            job.completed_at = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
            main.background_job_manager.store.ttl_hours = 24
            response = self.client.get(f"/jobs/{job_id}/result")
            self.assertEqual(response.status_code, 410)
        finally:
            main.run_portfolio_workflow = original


if __name__ == "__main__":
    unittest.main()
