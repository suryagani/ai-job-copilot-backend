from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

from auth_profile import get_authenticated_profile
from launch_control import ensure_signup_open, get_launch_status

from services.supabase_client import (
    SUPABASE_ANON_KEY,
    SUPABASE_REDIRECT_URL,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
    get_supabase_admin_client,
    get_supabase_public_config,
    is_supabase_admin_configured,
    is_supabase_configured,
)
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-me-auth-secret").encode("utf-8")
AUTH_DATA_DIR = Path("auth_cloud_sync_data")
LOCAL_USERS_FILE = AUTH_DATA_DIR / "users.json"
LOCAL_ASSETS_FILE = AUTH_DATA_DIR / "career_assets.json"
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7
SUPABASE_ADMIN_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)
SUPABASE_ADMIN_LIMITS = httpx.Limits(max_connections=8, max_keepalive_connections=4)


def _ensure_storage() -> None:
    AUTH_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOCAL_USERS_FILE.exists():
        LOCAL_USERS_FILE.write_text("[]", encoding="utf-8")
    if not LOCAL_ASSETS_FILE.exists():
        LOCAL_ASSETS_FILE.write_text("[]", encoding="utf-8")


def _read_json(path: Path) -> list[dict]:
    _ensure_storage()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_json(path: Path, payload: list[dict]) -> None:
    _ensure_storage()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return digest.hex()


def _issue_local_token(user: dict) -> str:
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "mode": "local",
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_token = _b64_encode(payload_bytes)
    signature = hmac.new(AUTH_SECRET_KEY, payload_token.encode("utf-8"), hashlib.sha256).digest()
    return f"local.{payload_token}.{_b64_encode(signature)}"


def _verify_local_token(token: str) -> dict | None:
    try:
        prefix, payload_token, signature_token = token.split(".", 2)
        if prefix != "local":
            return None
        expected = _b64_encode(hmac.new(AUTH_SECRET_KEY, payload_token.encode("utf-8"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature_token, expected):
            return None
        payload = json.loads(_b64_decode(payload_token).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        users = _read_json(LOCAL_USERS_FILE)
        for user in users:
            if user.get("id") == payload.get("sub"):
                return {
                    "id": user.get("id", ""),
                    "email": user.get("email", ""),
                    "full_name": user.get("full_name", ""),
                    "auth_mode": "local",
                }
    except Exception:
        return None
    return None


def get_auth_mode() -> str:
    if is_supabase_configured():
        return "supabase"
    return "local"


def get_auth_config() -> dict:
    return {
        "auth_mode": get_auth_mode(),
        "email_login_enabled": True,
        "google_login_enabled": bool(is_supabase_configured()),
        **get_supabase_public_config(),
        **get_launch_status(),
    }


def _extract_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
        return str(payload.get("msg") or payload.get("error_description") or payload.get("error") or payload.get("message") or "Authentication failed.")
    except Exception:
        return "Authentication failed."


def signup_user(email: str, password: str, full_name: str = "") -> dict:
    ensure_signup_open()
    email = str(email or "").strip().lower()
    password = str(password or "")
    full_name = str(full_name or "").strip()
    if not email or not password:
        raise ValueError("Email and password are required.")

    if get_auth_mode() == "supabase":
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{SUPABASE_URL}/auth/v1/signup",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Content-Type": "application/json",
                },
                json={"email": email, "password": password, "data": {"full_name": full_name}},
            )
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        payload = response.json()
        user = payload.get("user") or {}
        session = payload.get("session") or {}
        return {
            "access_token": session.get("access_token", ""),
            "refresh_token": session.get("refresh_token", ""),
            "user": {
                "id": user.get("id", ""),
                "email": user.get("email", email),
                "full_name": ((user.get("user_metadata") or {}).get("full_name") or full_name),
                "auth_mode": "supabase",
            },
            "auth_mode": "supabase",
            "message": "Account created successfully." if session.get("access_token") else "Account created. Please verify your email before logging in.",
        }

    users = _read_json(LOCAL_USERS_FILE)
    if any((user.get("email") or "").lower() == email for user in users):
        raise ValueError("An account with this email already exists.")
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "full_name": full_name,
        "salt": uuid.uuid4().hex,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    user["password_hash"] = _hash_password(password, user["salt"])
    users.append(user)
    _write_json(LOCAL_USERS_FILE, users)
    access_token = _issue_local_token(user)
    return {
        "access_token": access_token,
        "refresh_token": "",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "auth_mode": "local",
        },
        "auth_mode": "local",
        "message": "Account created successfully.",
    }


def login_user(email: str, password: str) -> dict:
    email = str(email or "").strip().lower()
    password = str(password or "")
    if not email or not password:
        raise ValueError("Email and password are required.")

    if get_auth_mode() == "supabase":
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Content-Type": "application/json",
                },
                json={"email": email, "password": password},
            )
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        payload = response.json()
        user = payload.get("user") or {}
        return {
            "access_token": payload.get("access_token", ""),
            "refresh_token": payload.get("refresh_token", ""),
            "user": {
                "id": user.get("id", ""),
                "email": user.get("email", email),
                "full_name": ((user.get("user_metadata") or {}).get("full_name") or ""),
                "auth_mode": "supabase",
            },
            "auth_mode": "supabase",
            "message": "Login successful.",
        }

    users = _read_json(LOCAL_USERS_FILE)
    for user in users:
        if (user.get("email") or "").lower() != email:
            continue
        if user.get("password_hash") != _hash_password(password, user.get("salt", "")):
            break
        token = _issue_local_token(user)
        return {
            "access_token": token,
            "refresh_token": "",
            "user": {
                "id": user.get("id", ""),
                "email": user.get("email", ""),
                "full_name": user.get("full_name", ""),
                "auth_mode": "local",
            },
            "auth_mode": "local",
            "message": "Login successful.",
        }
    raise ValueError("Invalid email or password.")


def verify_access_token(token: str) -> dict | None:
    token = str(token or "").strip()
    if not token:
        return None
    if token.startswith("local."):
        return _verify_local_token(token)
    if get_auth_mode() != "supabase":
        return None
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {token}",
    }
    with httpx.Client(timeout=SUPABASE_ADMIN_TIMEOUT, limits=SUPABASE_ADMIN_LIMITS) as client:
        response = client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)
    if response.status_code >= 400:
        return None
    payload = response.json()
    user = {
        "id": payload.get("id", ""),
        "email": payload.get("email", ""),
        "full_name": ((payload.get("user_metadata") or {}).get("full_name") or ""),
        "auth_mode": "supabase",
    }
    profile = get_authenticated_profile(user["id"], access_token=token)
    if not profile:
        return None
    user.update({key: profile.get(key, "") for key in ("role", "account_status", "full_name", "email")})
    return user


def user_is_admin(user: dict) -> bool:
    return str((user or {}).get("role") or "").strip().lower() in {"admin", "owner"}


def _admin_rest_request(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json_body: dict | None = None,
    http_client: httpx.Client | None = None,
) -> httpx.Response:
    if not is_supabase_admin_configured():
        raise RuntimeError("Supabase admin configuration is missing.")
    supabase_client = get_supabase_admin_client()
    headers = supabase_client.headers(prefer_return=json_body is not None)
    if http_client is not None:
        return http_client.request(
            method,
            supabase_client.rest_url(path),
            headers=headers,
            params=params,
            json=json_body,
        )
    with httpx.Client(timeout=SUPABASE_ADMIN_TIMEOUT, limits=SUPABASE_ADMIN_LIMITS) as request_client:
        return request_client.request(
            method,
            supabase_client.rest_url(path),
            headers=headers,
            params=params,
            json=json_body,
        )


def _admin_profile_output(profile: dict, asset_count: int = 0) -> dict:
    return {
        "id": str(profile.get("id") or "").strip(),
        "email": str(profile.get("email") or "").strip(),
        "full_name": str(profile.get("full_name") or "").strip(),
        "role": str(profile.get("role") or "user").strip().lower(),
        "account_status": str(profile.get("account_status") or "active").strip().lower(),
        "created_at": str(profile.get("created_at") or "").strip(),
        "last_login_at": str(profile.get("last_login_at") or "").strip(),
        "asset_count": asset_count,
    }


def list_waitlist_entries(limit: int = 100) -> list[dict]:
    limit = max(1, min(int(limit), 100))
    response = _admin_rest_request(
        "GET",
        "rest/v1/waitlist",
        params={
            "select": "id,email,first_name,target_role,source,created_at,status",
            "order": "created_at.desc",
            "limit": str(limit),
        },
    )
    if response.status_code >= 300:
        raise RuntimeError("Waitlist lookup failed.")
    payload = response.json()
    return payload if isinstance(payload, list) else []


def get_admin_profile(user_id: str) -> dict | None:
    user_id = str(user_id or "").strip()
    if not user_id:
        return None
    response = _admin_rest_request(
        "GET",
        "rest/v1/profiles",
        params={
            "select": "id,email,full_name,role,account_status,created_at,last_login_at",
            "id": f"eq.{user_id}",
            "limit": "1",
        },
    )
    if response.status_code >= 300:
        raise RuntimeError("Profile lookup failed.")
    payload = response.json()
    return payload[0] if isinstance(payload, list) and payload else None


def list_admin_users(limit: int = 100) -> list[dict]:
    limit = max(1, min(int(limit), 100))
    with httpx.Client(timeout=SUPABASE_ADMIN_TIMEOUT, limits=SUPABASE_ADMIN_LIMITS) as http_client:
        response = _admin_rest_request(
            "GET",
            "rest/v1/profiles",
            params={
                "select": "id,email,full_name,role,account_status,created_at,last_login_at",
                "order": "created_at.desc",
                "limit": str(limit),
            },
            http_client=http_client,
        )
        if response.status_code >= 300:
            raise RuntimeError("Profile listing failed.")
        profiles = response.json()
        if not isinstance(profiles, list):
            return []

        asset_counts: dict[str, int] = {}
        try:
            user_ids = [str(profile.get("id") or "").strip() for profile in profiles if str(profile.get("id") or "").strip()]
            if not user_ids:
                return [_admin_profile_output(profile, 0) for profile in profiles]
            assets = _admin_rest_request(
                "GET",
                "rest/v1/career_assets",
                params={
                    "select": "user_id",
                    "user_id": f"in.({','.join(user_ids)})",
                    "limit": "5000",
                },
                http_client=http_client,
            )
            if assets.status_code < 300 and isinstance(assets.json(), list):
                for asset in assets.json():
                    user_id = str(asset.get("user_id") or "").strip()
                    if user_id:
                        asset_counts[user_id] = asset_counts.get(user_id, 0) + 1
        except Exception:
            asset_counts = {}

        return [
            _admin_profile_output(profile, asset_counts.get(str(profile.get("id") or "").strip(), 0))
            for profile in profiles
        ]


def update_profile_role(user_id: str, role: str) -> dict:
    role = str(role or "").strip().lower()
    if role not in {"user", "admin", "owner"}:
        raise ValueError("Role must be user, admin, or owner.")
    response = _admin_rest_request(
        "PATCH",
        "rest/v1/profiles",
        params={"id": f"eq.{str(user_id or '').strip()}"},
        json_body={"role": role},
    )
    if response.status_code >= 300:
        raise ValueError("Profile role update failed.")
    updated = response.json()
    if isinstance(updated, list) and updated:
        return updated[0]
    profile = get_admin_profile(user_id)
    if not profile:
        raise ValueError("User profile not found.")
    return profile


def update_profile_status(user_id: str, account_status: str) -> dict:
    account_status = str(account_status or "").strip().lower()
    if account_status not in {"active", "suspended"}:
        raise ValueError("Account status must be active or suspended.")
    response = _admin_rest_request(
        "PATCH",
        "rest/v1/profiles",
        params={"id": f"eq.{str(user_id or '').strip()}"},
        json_body={"account_status": account_status},
    )
    if response.status_code >= 300:
        raise ValueError("Profile status update failed.")
    updated = response.json()
    if isinstance(updated, list) and updated:
        return updated[0]
    profile = get_admin_profile(user_id)
    if not profile:
        raise ValueError("User profile not found.")
    return profile


def _normalize_asset_record(record: dict) -> dict:
    return {
        "id": str(record.get("id", "")).strip(),
        "user_id": str(record.get("user_id", "")).strip(),
        "asset_type": str(record.get("asset_type", "")).strip(),
        "title": str(record.get("title", "")).strip(),
        "target_role": str(record.get("target_role", "")).strip(),
        "target_country": str(record.get("target_country", "")).strip(),
        "created_at": str(record.get("created_at", "")).strip(),
        "updated_at": str(record.get("updated_at", "")).strip(),
        "content_json": record.get("content_json") or {},
        "pdf_url": str(record.get("pdf_url", "")).strip(),
        "docx_url": str(record.get("docx_url", "")).strip(),
    }


def save_career_asset(user: dict, asset_type: str, title: str, target_role: str, target_country: str, content_json: dict | list | str, pdf_url: str = "", docx_url: str = "", access_token: str = "") -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "user_id": str(user.get("id", "")).strip(),
        "asset_type": str(asset_type or "").strip(),
        "title": str(title or "").strip(),
        "target_role": str(target_role or "").strip(),
        "target_country": str(target_country or "").strip(),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "content_json": content_json or {},
        "pdf_url": str(pdf_url or "").strip(),
        "docx_url": str(docx_url or "").strip(),
    }
    if get_auth_mode() == "supabase":
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY or access_token or SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{SUPABASE_URL}/rest/v1/career_assets", headers=headers, json=record)
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        payload = response.json()
        return _normalize_asset_record((payload or [record])[0])

    assets = _read_json(LOCAL_ASSETS_FILE)
    assets.append(record)
    assets.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    _write_json(LOCAL_ASSETS_FILE, assets)
    return _normalize_asset_record(record)


def list_career_assets(user: dict, access_token: str = "") -> list[dict]:
    if get_auth_mode() == "supabase":
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY or access_token or SUPABASE_ANON_KEY}",
        }
        params = {
            "select": "id,user_id,asset_type,title,target_role,target_country,created_at,updated_at,content_json,pdf_url,docx_url",
            "user_id": f"eq.{user.get('id', '')}",
            "order": "created_at.desc",
        }
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{SUPABASE_URL}/rest/v1/career_assets", headers=headers, params=params)
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        return [_normalize_asset_record(item) for item in response.json() or []]

    assets = _read_json(LOCAL_ASSETS_FILE)
    user_assets = [
        _normalize_asset_record(asset)
        for asset in assets
        if str(asset.get("user_id", "")).strip() == str(user.get("id", "")).strip()
    ]
    user_assets.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return user_assets


def get_career_asset_by_id(user: dict, asset_id: str, access_token: str = "") -> dict | None:
    asset_id = str(asset_id or "").strip()
    if not asset_id:
        return None
    if get_auth_mode() == "supabase":
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY or access_token or SUPABASE_ANON_KEY}",
        }
        params = {
            "select": "id,user_id,asset_type,title,target_role,target_country,created_at,updated_at,content_json,pdf_url,docx_url",
            "id": f"eq.{asset_id}",
            "user_id": f"eq.{user.get('id', '')}",
        }
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{SUPABASE_URL}/rest/v1/career_assets", headers=headers, params=params)
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        rows = response.json() or []
        return _normalize_asset_record(rows[0]) if rows else None

    assets = _read_json(LOCAL_ASSETS_FILE)
    for asset in assets:
        if str(asset.get("id", "")).strip() == asset_id and str(asset.get("user_id", "")).strip() == str(user.get("id", "")).strip():
            return _normalize_asset_record(asset)
    return None


def delete_career_asset(user: dict, asset_id: str, access_token: str = "") -> bool:
    asset_id = str(asset_id or "").strip()
    if not asset_id:
        return False
    if get_auth_mode() == "supabase":
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY or access_token or SUPABASE_ANON_KEY}",
        }
        params = {
            "id": f"eq.{asset_id}",
            "user_id": f"eq.{user.get('id', '')}",
        }
        with httpx.Client(timeout=30) as client:
            response = client.delete(f"{SUPABASE_URL}/rest/v1/career_assets", headers=headers, params=params)
        if response.status_code >= 400:
            raise ValueError(_extract_error(response))
        return True

    assets = _read_json(LOCAL_ASSETS_FILE)
    filtered = [
        asset for asset in assets
        if not (
            str(asset.get("id", "")).strip() == asset_id
            and str(asset.get("user_id", "")).strip() == str(user.get("id", "")).strip()
        )
    ]
    if len(filtered) == len(assets):
        return False
    _write_json(LOCAL_ASSETS_FILE, filtered)
    return True
