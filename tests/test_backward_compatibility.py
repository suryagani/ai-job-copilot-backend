import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


class BackwardCompatibilityTests(unittest.TestCase):
    def test_critical_routes_still_exist(self):
        paths = {route.path for route in main.app.routes}
        expected = {
            "/build-resume",
            "/optimize-resume",
            "/analyze-resume-intelligence",
            "/analyze-job-description",
            "/generate-achievements",
            "/analyze-ats",
            "/generate-cover-letter",
            "/optimize-linkedin",
            "/generate-interview-prep",
            "/generate-portfolio",
            "/prepare-job-application",
            "/export-resume-docx",
            "/export-resume-pdf",
            "/dashboard",
            "/career-assets",
            "/auth/login",
            "/admin/analytics/summary",
        }
        self.assertTrue(expected.issubset(paths))


if __name__ == "__main__":
    unittest.main()
