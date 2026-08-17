
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _supabase_url() -> str:
    return _env("SUPABASE_URL").rstrip("/")


def _supabase_anon_key() -> str:
    return _env("SUPABASE_ANON_KEY")


def _supabase_service_role_key() -> str:
    return _env("SUPABASE_SERVICE_ROLE_KEY")


def _supabase_redirect_url() -> str:
    return _env("SUPABASE_REDIRECT_URL")


def __getattr__(name: str):
    if name == "SUPABASE_URL":
        return _supabase_url()
    if name == "SUPABASE_ANON_KEY":
        return _supabase_anon_key()
    if name == "SUPABASE_SERVICE_ROLE_KEY":
        return _supabase_service_role_key()
    if name == "SUPABASE_REDIRECT_URL":
        return _supabase_redirect_url()
    raise AttributeError(name)


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
    return bool(_supabase_url() and _supabase_anon_key())


def is_supabase_admin_configured() -> bool:
    return bool(_supabase_url() and _supabase_service_role_key())


def get_supabase_client() -> SupabaseRestClient:
    if not is_supabase_configured():
        raise SupabaseConfigurationError("Supabase public configuration is missing.")
    return SupabaseRestClient(url=_supabase_url(), key=_supabase_anon_key(), admin=False)


def get_supabase_admin_client() -> SupabaseRestClient:
    if not is_supabase_admin_configured():
        raise SupabaseConfigurationError("Supabase admin configuration is missing.")
    return SupabaseRestClient(url=_supabase_url(), key=_supabase_service_role_key(), admin=True)


def get_supabase_public_config() -> dict[str, str]:
    if not is_supabase_configured():
        return {
            "supabase_url": "",
            "supabase_anon_key": "",
            "supabase_redirect_url": _supabase_redirect_url(),
        }
    return {
        "supabase_url": _supabase_url(),
        "supabase_anon_key": _supabase_anon_key(),
        "supabase_redirect_url": _supabase_redirect_url(),
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
