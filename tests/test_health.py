import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class HealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_health_endpoints_exist(self):
        for path in ("/health", "/health/ready", "/health/database", "/health/ai", "/health/storage"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("status", response.json())


if __name__ == "__main__":
    unittest.main()
