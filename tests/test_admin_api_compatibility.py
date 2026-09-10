import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main


class AdminApiCompatibilityTests(unittest.TestCase):
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

    def _auth(self, user):
        return patch.object(main, "get_current_user_optional", return_value=(user, "token"))

    def test_waitlist_admin_and_owner_allowed_user_denied(self):
        with patch.object(main, "list_waitlist_entries", return_value=[]):
            for role in ("admin", "owner"):
                with self.subTest(role=role), self._auth(self._user(role)):
                    response = self.client.get("/admin/waitlist", headers={"Authorization": "Bearer token"})
                self.assertEqual(response.status_code, 200)

            with self._auth(self._user()):
                response = self.client.get("/admin/waitlist", headers={"Authorization": "Bearer token"})
            self.assertEqual(response.status_code, 403)

    def test_owner_only_user_listing(self):
        with patch.object(main, "list_admin_users", return_value=[]):
            with self._auth(self._user("owner")):
                owner_response = self.client.get("/admin/users", headers={"Authorization": "Bearer token"})
            self.assertEqual(owner_response.status_code, 200)

            for role in ("admin", "user"):
                with self.subTest(role=role), self._auth(self._user(role)):
                    response = self.client.get("/admin/users", headers={"Authorization": "Bearer token"})
                self.assertEqual(response.status_code, 403)

    def test_all_frontend_analytics_routes_accept_bearer_admin(self):
        routes = {
            "/admin/analytics/summary": "analytics_summary",
            "/admin/analytics/tool-usage": "analytics_tool_usage",
            "/admin/analytics/countries": "analytics_countries",
            "/admin/analytics/roles": "analytics_roles",
            "/admin/analytics/downloads": "analytics_downloads",
            "/admin/analytics/errors": "analytics_errors",
            "/admin/analytics/recent-events": "analytics_recent_events",
        }
        patches = [patch.object(main, function_name, return_value={}) for function_name in routes.values()]
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            for role in ("admin", "owner"):
                for route in routes:
                    with self.subTest(role=role, route=route), self._auth(self._user(role)):
                        response = self.client.get(route, headers={"Authorization": "Bearer token"})
                    self.assertEqual(response.status_code, 200)

    def test_suspended_accounts_are_denied_from_admin_routes(self):
        routes = ("/admin/waitlist", "/admin/users", "/admin/analytics/summary")
        for role in ("admin", "owner"):
            for route in routes:
                with self.subTest(role=role, route=route), self._auth(self._user(role, "suspended")):
                    response = self.client.get(route, headers={"Authorization": "Bearer token"})
                self.assertEqual(response.status_code, 403)

    def test_role_and_status_updates_are_owner_only_and_validated(self):
        target = self._user("user")
        with patch.object(main, "get_admin_profile", return_value=target), patch.object(
            main, "update_profile_role", return_value={**target, "role": "admin"}
        ), patch.object(main, "update_profile_status", return_value={**target, "account_status": "suspended"}):
            with self._auth(self._user("owner")):
                role_response = self.client.patch(
                    "/admin/users/user-id/role",
                    json={"role": "admin"},
                    headers={"Authorization": "Bearer token"},
                )
                status_response = self.client.patch(
                    "/admin/users/user-id/status",
                    json={"account_status": "suspended"},
                    headers={"Authorization": "Bearer token"},
                )
            self.assertEqual(role_response.status_code, 200)
            self.assertEqual(status_response.status_code, 200)

            with self._auth(self._user("admin")):
                denied = self.client.patch(
                    "/admin/users/user-id/role",
                    json={"role": "admin"},
                    headers={"Authorization": "Bearer token"},
                )
            self.assertEqual(denied.status_code, 403)

        with self._auth(self._user("owner")):
            invalid = self.client.patch(
                "/admin/users/user-id/status",
                json={"account_status": "deleted"},
                headers={"Authorization": "Bearer token"},
            )
        self.assertEqual(invalid.status_code, 400)


if __name__ == "__main__":
    unittest.main()
