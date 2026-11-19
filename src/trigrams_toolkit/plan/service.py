"""Read Plan handoffs and atomically maintain declaration snapshots and progress."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined
from trigrams_toolkit.shared.serialization import canonical, read_json
from .definitions import read_definition
from trigrams_toolkit.shared.locking import atomic_write, locked
from .model import ACTIVE_STATES, JsonObject, PlanDefinition, SCHEDULE_FIELDS, Status, TaskDefinition
from .scheduling import Schedule, blockers, build_schedule, validate_completion
from .state import change_state, compile_state, read_state, read_stored


def _task_view(task: TaskDefinition, state: JsonObject) -> JsonObject:
    result = {**state["tasks"][task.identity], "path": str(task.path), "blockers": blockers(task, state)}
    if task.workspace is not None:
        result["workspace"] = task.workspace
    return result


def _compact_progress(record: JsonObject) -> JsonObject:
    return {key: record[key] for key in ("status", "note", "reason", "workspace", "blockers")
            if record.get(key)}


def _contents(directory: Path, root: Path) -> list[str]:
    entries = []
    for path in sorted(directory.rglob("*")):
        require(path.resolve().is_relative_to(root), "invalid_task", f"Task content escapes the Plan: {path}")
        if path.is_file():
            entries.append(path.relative_to(directory).as_posix())
    return entries


class PlanService:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def _load(self, *, required: bool = False) -> tuple[PlanDefinition, Schedule, JsonObject]:
        definition = read_definition(self.root)
        schedule = build_schedule(definition)
        return definition, schedule, read_state(definition, required=required)

    def _candidate(self) -> JsonObject:
        definition = read_definition(self.root)
        schedule = build_schedule(definition)
        candidate = compile_state(definition, read_stored(self.root, allow_legacy=True))
        validate_completion(schedule, candidate)
        return candidate

    def _save(self, state: JsonObject) -> bool:
        path = self.root / "plan.json"
        changed = not path.exists() or read_json(path) != state
        if changed:
            atomic_write(path, canonical(state) + b"\n")
        return changed

    def validate(self, *, sync: bool = False) -> JsonObject:
        if not sync:
            _, schedule, state = self._load(required=True)
            validate_completion(schedule, state)
            return {"valid": True, "changed": False}
        self._candidate()
        with locked(confined(self.root, ".plan.lock"), timeout=0):
            candidate = self._candidate()
            changed = self._save(candidate)
        return {"valid": True, "changed": changed}

    def get_tasks(self) -> JsonObject:
        definition, schedule, state = self._load(required=True)
        validate_completion(schedule, state)
        ready = []
        waiting = {}
        active = state["status"] in ACTIVE_STATES
        for task in definition.tasks:
            record = state["tasks"][task.identity]
            unmet = blockers(task, state)
            if record["status"] == Status.BLOCKED:
                waiting[task.identity] = [*unmet, {"type": "manual", "reason": record["reason"]}]
            elif record["status"] in (Status.PENDING, Status.REWORK):
                if unmet:
                    waiting[task.identity] = unmet
                elif active:
                    ready.append({"id": task.identity, "path": str(task.path)})
        return {"status": state["status"], "ready": ready, "waiting": waiting}

    def inspect(self, target: str | None = None,
                locate_spec: Callable[[str], JsonObject] | None = None, *, full: bool = False) -> JsonObject:
        definition, _, state = self._load()
        if target is None:
            if full:
                return {**state, "directory": str(self.root), "summary": str(self.root / "summary.md"),
                        "tasks": {task.identity: _task_view(task, state) for task in definition.tasks}}
            result = {"directory": str(self.root), **_compact_progress(state),
                      "tasks": {task.identity: _compact_progress(_task_view(task, state))
                                for task in definition.tasks}}
            if state["stubs"]:
                result["stubs"] = state["stubs"]
            return result
        task = next((task for task in definition.tasks if task.identity == target), None)
        require(task is not None, "unknown_task", f"Task {target} does not exist in {self.root}.")
        assert task is not None
        selected = set((*task.installs, *task.fills, *task.uses))
        view = _task_view(task, state)
        result = {"id": target, **view} if full else {
            "id": target, "path": str(task.path), **_compact_progress(view)}
        if full:
            result.update(directory=str(task.path.parent), body=task.body,
                          contents=_contents(task.path.parent, self.root))
        stubs = {stub.identity: {**state["stubs"][stub.identity], **({"body": stub.body} if full else {})}
                 for stub in definition.stubs if stub.identity in selected}
        if stubs or full:
            result["stubs"] = stubs
        if task.specs or full:
            result["specs"] = [locate_spec(identity) if locate_spec is not None else {"id": identity}
                               for identity in task.specs]
        return result

    def update(self, target: str | None, record: JsonObject) -> JsonObject:
        definition, _, current = self._load(required=True)
        change_state(definition, current, target, record)
        with locked(confined(self.root, ".plan.lock"), timeout=0):
            definition, _, current = self._load(required=True)
            updated = change_state(definition, current, target, record)
            changed = self._save(updated)
        selected = updated if target is None else updated["tasks"][target]
        progress = {key: value for key, value in selected.items() if key not in (*SCHEDULE_FIELDS, "tasks", "stubs")}
        result = {"changed": changed, "directory": str(self.root), **progress}
        if target is not None:
            result["id"] = target
        changes = {identity: stub["status"] for identity, stub in updated["stubs"].items()
                   if stub["status"] != current["stubs"][identity]["status"]}
        if changes:
            result["stubChanges"] = changes
        return result
