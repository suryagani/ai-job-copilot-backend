import os
import sys
import time
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class JobPollingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.background_job_manager.store._jobs.clear()
        main.background_job_manager.store._idempotency_map.clear()

    def test_polling_progress_and_invalid_job(self):
        original = main.run_portfolio_workflow
        try:
            def fake_workflow(data, authorization=None, x_session_id=None, progress_callback=None):
                progress_callback("analyzing_profile", 20, "Analyzing.")
                time.sleep(0.15)
                progress_callback("generating_content", 70, "Generating.")
                time.sleep(0.15)
                progress_callback("completed", 100, "Done.")
                return {"portfolio_score": 80, "portfolio_pdf_path": "x.pdf", "portfolio_docx_path": "x.docx", "portfolio_html_path": "x.html", "portfolio_readme_path": "x.md", "portfolio_json_path": "x.json"}
            main.run_portfolio_workflow = fake_workflow
            create = self.client.post("/jobs/portfolio", json={"target_role": "DevOps Engineer"}, headers={"X-Session-Id": "bg-d"})
            job_id = create.json()["job_id"]
            status = self.client.get(f"/jobs/{job_id}")
            self.assertEqual(status.status_code, 200)
            time.sleep(0.05)
            interim = self.client.get(f"/jobs/{job_id}/result")
            self.assertIn(interim.status_code, {200, 202})
            missing = self.client.get("/jobs/does-not-exist")
            self.assertEqual(missing.status_code, 404)
        finally:
            main.run_portfolio_workflow = original


if __name__ == "__main__":
    unittest.main()
