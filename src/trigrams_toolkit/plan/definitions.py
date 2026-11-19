"""Read Task declarations and the Stub handoff blocks in summary.md."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

from trigrams_toolkit.shared.errors import ProtocolError, require
from .model import PlanDefinition, REBUILD_INSTRUCTION, STUB_FIELDS, StubDefinition, TaskDefinition


class _HeaderLoader(yaml.SafeLoader):
    pass


def _mapping(loader: _HeaderLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        require(isinstance(key, str), "invalid_task", "Task header keys must be strings.")
        require(key not in result, "invalid_task", f"Duplicate Task header: {key}")
        result[key] = loader.construct_object(value_node)
    return result


_HeaderLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise ProtocolError("plan_unreadable", f"Cannot read {path}: {error}") from error


def _header(body: str, path: Path) -> dict[str, Any]:
    lines = body.splitlines()
    if not lines or lines[0] != "---":
        return {}
    require("---" in lines[1:], "invalid_task", f"Close the YAML header in {path}.")
    try:
        value = yaml.load("\n".join(lines[1:lines.index("---", 1)]), Loader=_HeaderLoader)
    except yaml.YAMLError as error:
        raise ProtocolError("invalid_task", f"Invalid YAML in {path}: {error}") from error
    require(value is None or isinstance(value, dict), "invalid_task", f"Task header must be a mapping: {path}")
    value = value or {}
    allowed = {"dependsOn", "specs", "workspace", *STUB_FIELDS}
    require(not set(value) - allowed, "invalid_task", f"Unknown Task header fields in {path}: {sorted(set(value) - allowed)}")
    return value


def _identities(value: Any, label: str) -> tuple[str, ...]:
    require(isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value),
            "invalid_task", f"{label} must be an array of nonempty IDs.")
    require(len(value) == len(set(value)), "invalid_task", f"{label} contains duplicate IDs.")
    return tuple(value)


def _stub_refs(value: Any, label: str, stubs: dict[str, StubDefinition]) -> tuple[str, ...]:
    require(isinstance(value, list), "invalid_task", f"{label} must be an array of Stub IDs and names.")
    identities = []
    for item in value:
        require(isinstance(item, dict) and set(item) == {"id", "name"},
                "invalid_task", f"{label} entries accept only id and name.")
        identity = item["id"]
        require(isinstance(identity, str) and identity in stubs,
                "invalid_stub", f"{label} references unknown Stub: {identity}")
        require(item["name"] == stubs[identity].name, "invalid_stub", f"{label}.{identity} has a different name from summary.md.")
        identities.append(identity)
    return _identities(identities, label)


def _task(path: Path, root: Path, stubs: dict[str, StubDefinition]) -> TaskDefinition:
    require(path.resolve().is_relative_to(root), "invalid_task", f"Task file escapes the Plan: {path}")
    identity = path.parent.name
    require(re.fullmatch(r"T[0-9]+", identity) is not None,
            "invalid_task", f"Use a Task directory ID such as T01: {path.parent}")
    body = read_text(path)
    header = _header(body, path)
    require(not stubs or all(field in header for field in STUB_FIELDS),
            "invalid_task", f"Declare installs, fills and uses (empty arrays when unused) in {path}.")
    dependencies = _identities(header.get("dependsOn", []), f"{identity}.dependsOn")
    specs = _identities(header.get("specs", []), f"{identity}.specs")
    workspace = header.get("workspace")
    require(workspace is None or isinstance(workspace, str) and bool(workspace.strip()),
            "invalid_task", f"{identity}.workspace must be a nonempty path.")
    refs = {field: _stub_refs(header.get(field, []), f"{identity}.{field}", stubs) for field in STUB_FIELDS}
    return TaskDefinition(identity, path, body, dependencies, specs, workspace, **refs)


def _stubs(summary: str) -> dict[str, StubDefinition]:
    result: dict[str, StubDefinition] = {}
    opened: tuple[str, int] | None = None
    markers = list(re.finditer(r"<!--\s*(/?)harness:stub\b(.*?)-->", summary, re.DOTALL))
    require(len(markers) == len(re.findall(r"<!--\s*/?harness:stub\b", summary)),
            "invalid_stub", "Unclosed Stub marker comment in summary.md.")
    for marker in markers:
        closing, identity = marker[1], marker[2].strip()
        require(re.fullmatch(r"S[0-9]+", identity) is not None, "invalid_stub", f"Invalid Stub ID in summary.md: {identity}")
        if not closing:
            require(opened is None and identity not in result, "invalid_stub", f"Duplicate or nested Stub block in summary.md: {identity}")
            opened = identity, marker.end()
            continue
        require(opened is not None and opened[0] == identity, "invalid_stub", f"Unmatched Stub closing marker in summary.md: {identity}")
        assert opened is not None
        body = summary[opened[1]:marker.start()].strip()
        title, _, content = body.partition("\n")
        heading = re.fullmatch(rf"### {identity} (\S[^\r\n]*)", title.strip())
        require(heading is not None and bool(content.strip()), "invalid_stub", f"Stub {identity} needs a '### {identity} NAME' heading and requirements in summary.md.")
        assert heading is not None
        result[identity] = StubDefinition(identity, heading[1].strip(), body)
        opened = None
    require(opened is None, "invalid_stub", f"Unclosed Stub block in summary.md: {opened}")
    return result


def read_definition(root: Path) -> PlanDefinition:
    root = root.resolve()
    require(root.is_dir(), "plan_unreadable", f"Plan directory does not exist: {root}")
    summary_path = root / "summary.md"
    require(summary_path.resolve().is_relative_to(root), "plan_unreadable", "summary.md escapes the Plan.")
    summary = read_text(summary_path)
    require("<!-- to-plan:data -->" not in summary and not any((root / "tasks").glob("T[0-9]*.md")),
            "unsupported_plan", f"Unsupported Plan layout. {REBUILD_INSTRUCTION}")
    stubs = _stubs(summary)
    tasks = tuple(_task(path, root, stubs) for path in sorted((root / "tasks").glob("*/task.md")))
    require(bool(tasks), "invalid_plan", f"Create at least one tasks/T01/task.md under {root}.")
    return PlanDefinition(root, tasks, tuple(stubs.values()))
