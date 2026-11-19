"""Compile declaration snapshots and preserve validated current progress."""

from __future__ import annotations

import copy
from pathlib import Path

from jsonschema import Draft202012Validator

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.serialization import read_json
from .model import (ACTIVE_STATES, JsonObject, PlanDefinition, PlanError, REBUILD_INSTRUCTION,
                    SCHEDULE_FIELDS, STUB_FIELDS, Status, StubDefinition, TaskDefinition)
from .scheduling import blockers, build_schedule, stub_states, validate_current

from trigrams_toolkit.resources import resource_path

SCHEMA_PATH = resource_path("plan/plan.schema.json")


def _validate_schema(value: JsonObject, *, legacy: bool = False, record: bool = False) -> None:
    schema = read_json(SCHEMA_PATH)
    if legacy:
        schema["required"].remove("stubs")
        del schema["properties"]["stubs"]
        schema["properties"]["tasks"]["additionalProperties"] = {"$ref": "#/$defs/record"}
        schema["properties"]["tasks"].pop("minProperties", None)
    if record:
        schema = {"$defs": schema["$defs"], "$ref": "#/$defs/record"}
    issues = [{"path": "/" + "/".join(map(str, error.absolute_path)), "message": error.message}
              for error in Draft202012Validator(schema).iter_errors(value)]
    if issues:
        raise PlanError("invalid_state", "Invalid Plan state; see issues for field locations.", issues)


def task_snapshot(task: TaskDefinition) -> JsonObject:
    return {"dependsOn": sorted(task.dependencies), **{field: sorted(getattr(task, field)) for field in STUB_FIELDS}}


def _stored_definition(root: Path, state: JsonObject) -> PlanDefinition:
    tasks = tuple(TaskDefinition(identity, root / f"tasks/{identity}/task.md", "",
                                 tuple(record["dependsOn"]), installs=tuple(record["installs"]), fills=tuple(record["fills"]), uses=tuple(record["uses"]))
                  for identity, record in state["tasks"].items())
    stubs = tuple(StubDefinition(identity, record["name"], "") for identity, record in state["stubs"].items())
    return PlanDefinition(root, tasks, stubs)


def _validate_progress(root: Path, state: JsonObject) -> None:
    definition = _stored_definition(root, state)
    expected = stub_states(build_schedule(definition), state["tasks"])
    for identity, status in expected.items():
        require(state["stubs"][identity]["status"] == status, "invalid_state",
                f"Stub {identity} status does not match its completed producer Tasks.")
    validate_current(definition, state)


def read_stored(root: Path, *, allow_legacy: bool = False) -> JsonObject | None:
    path = root / "plan.json"
    if not path.exists():
        return None
    require(path.resolve().is_relative_to(root), "invalid_state", "plan.json escapes the Plan.")
    value = read_json(path)
    require(not isinstance(value, dict) or "schemaVersion" not in value and "schema_version" not in value,
            "unsupported_plan", f"Unsupported Plan state. {REBUILD_INSTRUCTION}")
    legacy = isinstance(value, dict) and "stubs" not in value
    _validate_schema(value, legacy=legacy)
    require(not legacy or allow_legacy, "definition_out_of_sync", "Run validate PLAN --sync to compile the declaration snapshot.")
    if not legacy:
        _validate_progress(root, value)
    return value


def _guard_revision(definition: PlanDefinition, current: JsonObject) -> None:
    existing = current["tasks"]
    declared = {task.identity: task for task in definition.tasks}
    for identity, record in existing.items():
        if identity not in declared:
            require(record["status"] == Status.PENDING, "progress_conflict", f"Do not remove started Task {identity}; preserve its progress.")
            continue
        if record["status"] not in (Status.DOING, Status.DONE):
            continue
        expected = task_snapshot(declared[identity])
        fields = SCHEDULE_FIELDS if "stubs" in current else STUB_FIELDS
        require(all(record.get(field, []) == expected[field] for field in fields), "progress_conflict",
                f"Do not change handoff declarations of active or completed Task {identity}.")
    retained = {stub.identity for stub in definition.stubs}
    for identity, record in current.get("stubs", {}).items():
        require(identity in retained or record["status"] == "uninstalled", "progress_conflict",
                f"Do not discard accepted Stub {identity}.")


def compile_state(definition: PlanDefinition, current: JsonObject | None) -> JsonObject:
    if current is not None:
        _guard_revision(definition, current)
    result = {key: value for key, value in (current or {"status": Status.PENDING}).items() if key not in ("tasks", "stubs")}
    previous = current["tasks"] if current is not None else {}
    result["tasks"] = {}
    for task in definition.tasks:
        progress = {key: value for key, value in previous.get(task.identity, {"status": Status.PENDING}).items()
                    if key not in SCHEDULE_FIELDS}
        result["tasks"][task.identity] = {**progress, **task_snapshot(task)}
    stages = stub_states(build_schedule(definition), result["tasks"])
    result["stubs"] = {stub.identity: {"name": stub.name, "status": stages[stub.identity]} for stub in definition.stubs}
    _validate_schema(result)
    validate_current(definition, result)
    return result


def read_state(definition: PlanDefinition, *, required: bool = False) -> JsonObject:
    current = read_stored(definition.root)
    if current is None:
        require(not required, "missing_state", "Run validate PLAN --sync before scheduling this Plan.")
        return compile_state(definition, None)
    expected_tasks = {task.identity: task_snapshot(task) for task in definition.tasks}
    stored_tasks = {identity: {field: record[field] for field in SCHEDULE_FIELDS}
                    for identity, record in current["tasks"].items()}
    names = {stub.identity: stub.name for stub in definition.stubs}
    require(expected_tasks == stored_tasks and names == {identity: record["name"] for identity, record in current["stubs"].items()},
            "definition_out_of_sync", "Plan declarations changed; run validate PLAN --sync before scheduling.")
    return current


def change_state(definition: PlanDefinition, state: JsonObject, target: str | None,
                 record: JsonObject) -> JsonObject:
    _validate_schema(record, record=True)
    status = record["status"]
    if target is not None:
        task = next((task for task in definition.tasks if task.identity == target), None)
        require(task is not None, "unknown_task", f"Task {target} does not exist in {definition.root}.")
        assert task is not None
        if status == Status.DOING and state["tasks"][target]["status"] != Status.DOING:
            require(state["status"] in ACTIVE_STATES, "not_ready", "Resume the Plan before starting a Task.")
        if status in (Status.DOING, Status.REWORK, Status.DONE):
            unmet = blockers(task, state)
            if unmet:
                raise PlanError("not_ready", f"Task {target} has unmet prerequisites.", [{"task": target, "blockers": unmet}])
    updated = copy.deepcopy(state)
    if target is None:
        updated = {**record, "tasks": updated["tasks"], "stubs": updated["stubs"]}
    else:
        assert task is not None
        updated["tasks"][target] = {**record, **task_snapshot(task)}
    for identity, status in stub_states(build_schedule(definition), updated["tasks"]).items():
        updated["stubs"][identity]["status"] = status
    validate_current(definition, updated)
    return updated
