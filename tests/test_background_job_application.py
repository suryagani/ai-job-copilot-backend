import os
import sys
import time
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class BackgroundJobApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.background_job_manager.store._jobs.clear()
        main.background_job_manager.store._idempotency_map.clear()

    def test_background_job_application_result(self):
        original = main.run_job_application_workflow
        try:
            def fake_workflow(data, authorization=None, x_session_id=None, progress_callback=None):
                progress_callback("optimizing_resume", 25, "Optimizing.")
                time.sleep(0.1)
                progress_callback("completed", 100, "Done.")
                return {"overall_application_score": 88, "application_readiness": "Excellent", "application_report_pdf_path": "r.pdf", "application_report_docx_path": "r.docx", "optimized_resume": {}, "cover_letter": {}, "linkedin_recommendations": {}, "interview_preparation": {}, "ats_report": {}, "recruiter_report": {}, "job_match_score": 80, "recommended_next_steps": [], "application_report": {}}
            main.run_job_application_workflow = fake_workflow
            create = self.client.post("/jobs/job-application", json={"target_role": "Operations Manager", "resume_text": "sample"}, headers={"X-Session-Id": "bg-c", "Idempotency-Key": "job-app-1"})
            job_id = create.json()["job_id"]
            time.sleep(0.25)
            result = self.client.get(f"/jobs/{job_id}/result")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()["overall_application_score"], 88)
        finally:
            main.run_job_application_workflow = original


if __name__ == "__main__":
    unittest.main()
