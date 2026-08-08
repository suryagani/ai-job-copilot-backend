import os
import sys
import time
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main
from core.exceptions import AppError


class JobFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.background_job_manager.store._jobs.clear()
        main.background_job_manager.store._idempotency_map.clear()

    def test_failed_job_returns_safe_error(self):
        original = main.run_job_application_workflow
        try:
            def fake_workflow(data, authorization=None, x_session_id=None, progress_callback=None):
                progress_callback("optimizing_resume", 25, "Optimizing.")
                raise AppError("AI_TIMEOUT", "The request is taking longer than expected. Please try again.", status_code=504, category="ai_timeout_error")
            main.run_job_application_workflow = fake_workflow
            create = self.client.post("/jobs/job-application", json={"target_role": "DevOps Engineer", "resume_text": "sample"}, headers={"X-Session-Id": "bg-e"})
            job_id = create.json()["job_id"]
            time.sleep(0.15)
            result = self.client.get(f"/jobs/{job_id}/result")
            self.assertEqual(result.status_code, 500)
            body = result.json()
            self.assertEqual(body["error_code"], "AI_TIMEOUT")
            self.assertIn("request_id", body)
        finally:
            main.run_job_application_workflow = original


if __name__ == "__main__":
    unittest.main()
