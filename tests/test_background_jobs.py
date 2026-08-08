import os
import sys
import time
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class BackgroundJobTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.background_job_manager.store._jobs.clear()
        main.background_job_manager.store._idempotency_map.clear()

    def test_create_portfolio_job(self):
        original = main.run_portfolio_workflow
        try:
            def fake_workflow(data, authorization=None, x_session_id=None, progress_callback=None):
                if progress_callback:
                    progress_callback("analyzing_profile", 15, "Analyzing.")
                time.sleep(0.2)
                if progress_callback:
                    progress_callback("completed", 100, "Done.")
                return {"portfolio_score": 90, "portfolio_pdf_path": "x.pdf", "portfolio_docx_path": "x.docx", "portfolio_html_path": "x.html", "portfolio_readme_path": "x.md", "portfolio_json_path": "x.json"}
            main.run_portfolio_workflow = fake_workflow
            payload = {"target_role": "DevOps Engineer"}
            response = self.client.post("/jobs/portfolio", json=payload, headers={"X-Session-Id": "bg-a", "Idempotency-Key": "portfolio-1"})
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertIn("job_id", body)
            self.assertEqual(body["status"], "queued")
        finally:
            main.run_portfolio_workflow = original


if __name__ == "__main__":
    unittest.main()
