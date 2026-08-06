import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class DuplicateRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def setUp(self):
        main.IDEMPOTENCY_STORE.clear()
        main.EXPENSIVE_ENDPOINTS.add("/save-job-alert")

    def tearDown(self):
        main.EXPENSIVE_ENDPOINTS.discard("/save-job-alert")

    def test_idempotency_returns_same_result(self):
        payload = {
            "email": "sample@example.com",
            "target_role": "QA Engineer",
            "country": "India",
            "city": "Chennai",
            "experience_level": "Fresher",
            "keywords": "",
            "preferred_time": "09:00",
        }
        headers = {"Idempotency-Key": "same-request", "X-Session-Id": "session-a"}
        first = self.client.post("/save-job-alert", json=payload, headers=headers)
        second = self.client.post("/save-job-alert", json=payload, headers=headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), second.json())


if __name__ == "__main__":
    unittest.main()
