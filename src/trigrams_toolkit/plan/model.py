"""Plan definitions and the six current states."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from trigrams_toolkit.shared.errors import ProtocolError

JsonObject = dict[str, Any]


class Status(StrEnum):
    PENDING = "pending"
    DOING = "doing"
    REWORK = "rework"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


MARK_STATES: Final = (Status.PENDING, Status.DOING, Status.REWORK, Status.DONE)
ACTIVE_STATES: Final = (Status.PENDING, Status.DOING, Status.REWORK)
REBUILD_INSTRUCTION: Final = "Archive the old state and rebuild the Plan with project-setup."
STUB_FIELDS: Final = ("installs", "fills", "uses")
SCHEDULE_FIELDS: Final = ("dependsOn", *STUB_FIELDS)


class PlanError(ProtocolError):
    def __init__(self, code: str, message: str, issues: list[JsonObject]) -> None:
        super().__init__(code, message)
        self.issues = issues


@dataclass(frozen=True)
class StubDefinition:
    identity: str
    name: str
    body: str


@dataclass(frozen=True)
class TaskDefinition:
    identity: str
    path: Path
    body: str
    dependencies: tuple[str, ...] = ()
    specs: tuple[str, ...] = ()
    workspace: str | None = None
    installs: tuple[str, ...] = ()
    fills: tuple[str, ...] = ()
    uses: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanDefinition:
    root: Path
    tasks: tuple[TaskDefinition, ...]
    stubs: tuple[StubDefinition, ...] = ()
