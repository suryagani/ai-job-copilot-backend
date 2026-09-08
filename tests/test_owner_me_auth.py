import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class OwnerMeAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def _user(self, role="user", account_status="active"):
        return {
            "id": f"{role}-id",
            "email": f"{role}@example.test",
            "full_name": role.title(),
            "auth_mode": "supabase",
            "role": role,
            "account_status": account_status,
        }

    def test_me_returns_user_role_and_status(self):
        with patch.object(main, "get_current_user_optional", return_value=(self._user(), "token")):
            response = self.client.get("/me", headers={"Authorization": "Bearer token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], "user")
        self.assertEqual(response.json()["account_status"], "active")

    def test_me_returns_admin_role_and_status(self):
        with patch.object(main, "get_current_user_optional", return_value=(self._user("admin"), "token")):
            response = self.client.get("/me", headers={"Authorization": "Bearer token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], "admin")

    def test_me_returns_owner_role_and_status(self):
        with patch.object(main, "get_current_user_optional", return_value=(self._user("owner"), "token")):
            response = self.client.get("/me", headers={"Authorization": "Bearer token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], "owner")

    def test_suspended_me_is_denied(self):
        with patch.object(main, "get_current_user_optional", return_value=(self._user("owner", "suspended"), "token")):
            response = self.client.get("/me", headers={"Authorization": "Bearer token"})
        self.assertEqual(response.status_code, 403)
        self.assertIn("suspended", response.json()["detail"].lower())

    def test_active_admin_and_owner_are_allowed(self):
        for role in ("admin", "owner"):
            with self.subTest(role=role), patch.object(main, "get_current_user_optional", return_value=(self._user(role), "token")), patch.object(main, "analytics_summary", return_value={"ok": True}):
                response = self.client.get("/admin/analytics/summary", headers={"Authorization": "Bearer token"})
            self.assertEqual(response.status_code, 200)

    def test_normal_user_is_denied(self):
        with patch.object(main, "get_current_user_optional", return_value=(self._user(), "token")):
            response = self.client.get("/admin/analytics/summary", headers={"Authorization": "Bearer token"})
        self.assertEqual(response.status_code, 403)

    def test_suspended_admin_and_owner_are_denied(self):
        for role in ("admin", "owner"):
            with self.subTest(role=role), patch.object(main, "get_current_user_optional", return_value=(self._user(role, "suspended"), "token")):
                response = self.client.get("/admin/analytics/summary", headers={"Authorization": "Bearer token"})
            self.assertEqual(response.status_code, 403)
            self.assertIn("suspended", response.json()["detail"].lower())


if __name__ == "__main__":
    unittest.main()
