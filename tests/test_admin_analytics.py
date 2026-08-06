import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class AdminAnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_admin_requires_secret(self):
        response = self.client.get("/admin/analytics/summary")
        self.assertEqual(response.status_code, 403)

    def test_admin_performance_with_secret(self):
        response = self.client.get("/admin/analytics/performance", headers={"X-Admin-Secret": main.ADMIN_SECRET})
        self.assertEqual(response.status_code, 200)
        self.assertIn("slowest_endpoints", response.json())


if __name__ == "__main__":
    unittest.main()
