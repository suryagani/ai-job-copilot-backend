from __future__ import annotations

from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="")
_user_id: ContextVar[str] = ContextVar("user_id", default="")
_session_id: ContextVar[str] = ContextVar("session_id", default="")


def set_request_context(request_id: str, user_id: str = "", session_id: str = "") -> None:
    _request_id.set(str(request_id or "").strip())
    _user_id.set(str(user_id or "").strip())
    _session_id.set(str(session_id or "").strip())


def clear_request_context() -> None:
    set_request_context("", "", "")


def get_request_id() -> str:
    return _request_id.get()


def get_user_id() -> str:
    return _user_id.get()


def get_session_id() -> str:
    return _session_id.get()
