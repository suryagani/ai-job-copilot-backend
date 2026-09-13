from __future__ import annotations

from datetime import datetime, timezone


LAUNCH_AT = datetime(2026, 9, 14, 12, 14, tzinfo=timezone.utc)
LAUNCH_AT_ISO = LAUNCH_AT.isoformat().replace("+00:00", "Z")


def is_launched(now: datetime | None = None) -> bool:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc) >= LAUNCH_AT


def get_launch_status(now: datetime | None = None) -> dict:
    return {"launch_at": LAUNCH_AT_ISO, "is_launched": is_launched(now)}


def ensure_signup_open() -> None:
    if not is_launched():
        raise ValueError("Account creation opens at the official launch time.")
