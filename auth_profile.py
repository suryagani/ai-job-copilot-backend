from __future__ import annotations

from typing import Any

import httpx

from services.supabase_client import (
    get_supabase_admin_client,
    get_supabase_client,
    is_supabase_admin_configured,
    is_supabase_configured,
)


def get_authenticated_profile(user_uuid: str, access_token: str = "") -> dict[str, Any] | None:
    """Read authorization fields from the profile bound to an authenticated UUID."""
    user_id = str(user_uuid or "").strip()
    if not user_id or not is_supabase_configured():
        return None
    try:
        client = get_supabase_admin_client() if is_supabase_admin_configured() else get_supabase_client()
        bearer = None if client.admin else str(access_token or "").strip() or None
        response = httpx.get(
            client.rest_url("rest/v1/profiles"),
            headers=client.headers(bearer_token=bearer),
            params={"select": "id,role,account_status,full_name,email", "id": f"eq.{user_id}", "limit": "1"},
            timeout=15,
        )
        if response.status_code >= 400:
            return None
        rows = response.json()
    except Exception:
        return None
    if not isinstance(rows, list) or not rows:
        return None
    profile = rows[0]
    return profile if str(profile.get("id") or "").strip() == user_id else None
