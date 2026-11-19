"""Legacy Project State JSON.parse boundary (separate from strict CLI JSON)."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _invalid_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def _number(value: str) -> int | float:
    number = float(value)
    return int(number) if math.isfinite(number) and number.is_integer() else number


def parse_state_json(raw: str | bytes, *, bom: bool = False) -> Any:
    text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
    if bom:
        text = text.removeprefix("\ufeff")
    return json.loads(text, parse_int=_number, parse_float=_number, parse_constant=_invalid_constant)


def optional_bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def json_bytes(value: Any) -> bytes:
    return (json.dumps(_json_value(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8", errors="backslashreplace")


def _json_value(value: Any) -> Any:
    """JSON.stringify emits null for overflowed numbers in unmanaged fields."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value
