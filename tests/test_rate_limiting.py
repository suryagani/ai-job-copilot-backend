import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class RateLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.RATE_LIMIT_STORE.clear()

    def test_rate_limit_blocks_after_limit(self):
        original = main.RATE_LIMIT_ANONYMOUS_PER_HOUR
        main.RATE_LIMIT_ANONYMOUS_PER_HOUR = 1
        payload = {
            "email": "sample@example.com",
            "target_role": "QA Engineer",
            "country": "India",
            "city": "Chennai",
            "experience_level": "Fresher",
            "keywords": "",
            "preferred_time": "09:00",
        }
        try:
            first = self.client.post("/save-job-alert", json=payload)
            second = self.client.post("/save-job-alert", json=payload)
            self.assertEqual(first.status_code, 200)
            self.assertEqual(second.status_code, 429)
        finally:
            main.RATE_LIMIT_ANONYMOUS_PER_HOUR = original


if __name__ == "__main__":
    unittest.main()
