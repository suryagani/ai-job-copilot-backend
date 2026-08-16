
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_REDIRECT_URL = os.getenv("SUPABASE_REDIRECT_URL", "").strip()


@dataclass(frozen=True)
class SupabaseRestClient:
    url: str
    key: str
    admin: bool = False

    @property
    def configured(self) -> bool:
        return bool(self.url and self.key)

    def headers(self, bearer_token: str | None = None, prefer_return: bool = False) -> dict[str, str]:
        token = bearer_token or self.key
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {token}",
        }
        if prefer_return:
            headers["Prefer"] = "return=representation"
            headers["Content-Type"] = "application/json"
        return headers

    def rest_url(self, path: str) -> str:
        clean = str(path or "").lstrip("/")
        return f"{self.url}/{clean}"


class SupabaseConfigurationError(RuntimeError):
    pass


def is_supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)


def is_supabase_admin_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


def get_supabase_client() -> SupabaseRestClient:
    if not is_supabase_configured():
        raise SupabaseConfigurationError("Supabase public configuration is missing.")
    return SupabaseRestClient(url=SUPABASE_URL, key=SUPABASE_ANON_KEY, admin=False)


def get_supabase_admin_client() -> SupabaseRestClient:
    if not is_supabase_admin_configured():
        raise SupabaseConfigurationError("Supabase admin configuration is missing.")
    return SupabaseRestClient(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY, admin=True)


def get_supabase_public_config() -> dict[str, str]:
    if not is_supabase_configured():
        return {
            "supabase_url": "",
            "supabase_anon_key": "",
            "supabase_redirect_url": SUPABASE_REDIRECT_URL,
        }
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_anon_key": SUPABASE_ANON_KEY,
        "supabase_redirect_url": SUPABASE_REDIRECT_URL,
    }


def check_supabase_database() -> dict[str, Any]:
    if not is_supabase_configured():
        return {"connected": False, "database_reachable": False, "reason": "not_configured"}
    try:
        client = get_supabase_admin_client() if is_supabase_admin_configured() else get_supabase_client()
        with httpx.Client(timeout=15) as http_client:
            response = http_client.get(
                client.rest_url("rest/v1/"),
                headers=client.headers(),
                params={"select": "*"},
            )
        return {
            "connected": response.status_code < 500,
            "database_reachable": response.status_code < 500,
            "reason": "ok" if response.status_code < 400 else f"http_{response.status_code}",
        }
    except Exception:
        return {"connected": False, "database_reachable": False, "reason": "request_failed"}


def check_supabase_auth() -> dict[str, Any]:
    if not is_supabase_configured():
        return {"connected": False, "auth_reachable": False, "reason": "not_configured"}
    try:
        client = get_supabase_client()
        with httpx.Client(timeout=15) as http_client:
            response = http_client.get(
                client.rest_url("auth/v1/settings"),
                headers={"apikey": client.key},
            )
        return {
            "connected": response.status_code < 500,
            "auth_reachable": response.status_code < 500,
            "reason": "ok" if response.status_code < 400 else f"http_{response.status_code}",
        }
    except Exception:
        return {"connected": False, "auth_reachable": False, "reason": "request_failed"}


def check_supabase_storage() -> dict[str, Any]:
    if not is_supabase_configured():
        return {"connected": False, "storage_reachable": False, "reason": "not_configured"}
    try:
        client = get_supabase_admin_client() if is_supabase_admin_configured() else get_supabase_client()
        with httpx.Client(timeout=15) as http_client:
            response = http_client.get(
                client.rest_url("storage/v1/bucket"),
                headers=client.headers(),
            )
        return {
            "connected": response.status_code < 500,
            "storage_reachable": response.status_code < 500,
            "reason": "ok" if response.status_code < 400 else f"http_{response.status_code}",
        }
    except Exception:
        return {"connected": False, "storage_reachable": False, "reason": "request_failed"}
