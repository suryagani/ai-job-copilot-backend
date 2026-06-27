from typing import Any, Callable


_runtime_client = None
_runtime_parser: Callable[[str], dict[str, Any]] | None = None


def configure_runtime(client, parser: Callable[[str], dict[str, Any]]) -> None:
    global _runtime_client, _runtime_parser
    _runtime_client = client
    _runtime_parser = parser


def get_runtime():
    if _runtime_client is None or _runtime_parser is None:
        raise RuntimeError("Resume model runtime is not configured.")
    return _runtime_client, _runtime_parser
