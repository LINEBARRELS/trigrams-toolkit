"""Strict protocol JSON and canonical serialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ProtocolError, require

MAX_INTEGER = 9007199254740991


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "invalid_json", f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_number(value: str) -> None:
    raise ProtocolError("invalid_json", f"Only finite integer numbers are permitted: {value}")


def scalar_json(value: Any) -> None:
    if value is None or type(value) is bool:
        return
    if isinstance(value, str):
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value),
                "invalid_json", "Strings must contain Unicode scalar values.")
        return
    if type(value) is int:
        require(abs(value) <= MAX_INTEGER, "invalid_json", "Integer exceeds the shared safe range.")
        return
    if isinstance(value, list):
        for item in value:
            scalar_json(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            require(isinstance(key, str), "invalid_json", "JSON object keys must be strings.")
            scalar_json(key)
            scalar_json(item)
        return
    raise ProtocolError("invalid_json", f"Unsupported protocol JSON value: {type(value).__name__}")


def parse_json_document(raw: str | bytes) -> Any:
    """Parse UTF-8 JSON with unique keys and integer numbers.

    Share duplicate-key/number rules and JSON/Unicode error conversion.
    Keep check_protocols' document boundary: arbitrary-size integers and escaped
    surrogate strings are accepted here; runtime values pass scalar_json too.
    Invalid encoding, syntax, duplicate keys or non-integers raise ProtocolError
    with invalid_json. File IO errors belong to the caller.
    """
    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(text, object_pairs_hook=_unique,
                          parse_float=_reject_number, parse_constant=_reject_number)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ProtocolError("invalid_json", str(error)) from error


def parse_json(raw: str | bytes) -> Any:
    """Parse document JSON and enforce runtime-safe integers/scalar strings."""
    result = parse_json_document(raw)
    scalar_json(result)
    return result


def read_json(path: Path) -> Any:
    return parse_json(path.read_bytes())


def canonical(value: Any) -> bytes:
    scalar_json(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sorted_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [parse_json(raw) for raw in sorted({canonical(ref) for ref in refs})]
