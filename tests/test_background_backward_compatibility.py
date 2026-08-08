import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class BackgroundBackwardCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_sync_routes_still_exist(self):
        paths = {route.path for route in main.app.routes}
        self.assertIn("/generate-portfolio", paths)
        self.assertIn("/prepare-job-application", paths)
        self.assertIn("/jobs/portfolio", paths)
        self.assertIn("/jobs/job-application", paths)

    def test_sync_routes_still_work_when_patched(self):
        original_portfolio = main.run_portfolio_workflow
        original_application = main.run_job_application_workflow
        try:
            main.run_portfolio_workflow = lambda data, authorization=None, x_session_id=None, progress_callback=None: {"portfolio_score": 77, "portfolio_pdf_path": "x.pdf", "portfolio_docx_path": "x.docx", "portfolio_html_path": "x.html", "portfolio_readme_path": "x.md", "portfolio_json_path": "x.json", "professional_bio": "", "about_me": "", "personal_tagline": "", "project_showcase": [], "project_case_studies": [], "github_readme": "", "personal_website_content": "", "skills_section": [], "timeline": [], "contact_section": [], "professional_footer": "", "seo_meta_title": "", "seo_meta_description": "", "selected_theme": "", "recruiter_score": 70, "quality_notes": []}
            main.run_job_application_workflow = lambda data, authorization=None, x_session_id=None, progress_callback=None: {"optimized_resume": {}, "cover_letter": {}, "linkedin_recommendations": {}, "interview_preparation": {}, "ats_report": {}, "recruiter_report": {}, "overall_application_score": 80, "job_match_score": 75, "application_readiness": "Good", "recommended_next_steps": [], "application_report": {}, "application_report_pdf_path": "r.pdf", "application_report_docx_path": "r.docx"}
            portfolio = self.client.post("/generate-portfolio", json={"target_role": "DevOps Engineer"})
            application = self.client.post("/prepare-job-application", json={"target_role": "DevOps Engineer", "resume_text": "sample"})
            self.assertEqual(portfolio.status_code, 200)
            self.assertEqual(application.status_code, 200)
        finally:
            main.run_portfolio_workflow = original_portfolio
            main.run_job_application_workflow = original_application


if __name__ == "__main__":
    unittest.main()
