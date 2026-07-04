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

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_REDIRECT_URL = os.getenv("SUPABASE_REDIRECT_URL", "").strip()
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-me-auth-secret").encode("utf-8")
AUTH_DATA_DIR = Path("auth_cloud_sync_data")
LOCAL_USERS_FILE = AUTH_DATA_DIR / "users.json"
LOCAL_ASSETS_FILE = AUTH_DATA_DIR / "career_assets.json"
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7


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
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        return "supabase"
    return "local"


def get_auth_config() -> dict:
    return {
        "auth_mode": get_auth_mode(),
        "email_login_enabled": True,
        "google_login_enabled": bool(SUPABASE_URL and SUPABASE_ANON_KEY),
        "supabase_url": SUPABASE_URL if SUPABASE_URL and SUPABASE_ANON_KEY else "",
        "supabase_anon_key": SUPABASE_ANON_KEY if SUPABASE_URL and SUPABASE_ANON_KEY else "",
        "supabase_redirect_url": SUPABASE_REDIRECT_URL,
    }


def _extract_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
        return str(payload.get("msg") or payload.get("error_description") or payload.get("error") or payload.get("message") or "Authentication failed.")
    except Exception:
        return "Authentication failed."


def signup_user(email: str, password: str, full_name: str = "") -> dict:
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
    with httpx.Client(timeout=30) as client:
        response = client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)
    if response.status_code >= 400:
        return None
    payload = response.json()
    return {
        "id": payload.get("id", ""),
        "email": payload.get("email", ""),
        "full_name": ((payload.get("user_metadata") or {}).get("full_name") or ""),
        "auth_mode": "supabase",
    }


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
