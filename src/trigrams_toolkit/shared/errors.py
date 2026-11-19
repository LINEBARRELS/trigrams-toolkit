"""Shared protocol failures."""

from __future__ import annotations

from typing import Any


class ProtocolError(Exception):
    def __init__(self, code: str, message: str, *, conflicts: tuple[str, ...] = (),
                 current: dict[str, Any] | None = None, details: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.conflicts = conflicts
        self.current = current
        self.details = details

    def state_error(self) -> dict[str, Any]:
        return {"code": self.code, "message": str(self),
                **({"details": self.details} if self.details is not None else {})}

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": str(self), "current": self.current,
                "conflicts": list(self.conflicts),
                "recovery": "Inspect the indicated inputs and current state before retrying."}


def require(condition: bool, code: str, message: str, *objects: str) -> None:
    if not condition:
        raise ProtocolError(code, message, conflicts=tuple(objects))
