import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


def _boom():
    raise RuntimeError("unexpected failure")


if not any(route.path == "/_test/boom" for route in main.app.routes):
    main.app.add_api_route("/_test/boom", _boom, methods=["GET"])


class ErrorHandlingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app, raise_server_exceptions=False)

    def test_generic_error_is_safe(self):
        response = self.client.get("/_test/boom")
        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertIn("request_id", body)
        self.assertEqual(body["message"], "Something went wrong. Please try again.")


if __name__ == "__main__":
    unittest.main()
