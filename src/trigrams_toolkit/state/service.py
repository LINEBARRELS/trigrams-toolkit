"""Public Registry services, shared by CLI and Plan inspection."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from trigrams_toolkit.project_context import current_project_root
from trigrams_toolkit.project_context.paths import confined
from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.files import atomic_write
from trigrams_toolkit.shared.process_lock import state_lock
from trigrams_toolkit.shared.state_json import json_bytes
from .arguments import Invocation
from .identity import read_declaration
from .location import identity_candidates
from .model import Edge, RegistryState, all_entities, entity_kind, identity_sort_key, validate_record
from .providers import provider_types
from .registration import register
from .relations import change_relation, effective_relations, validate_relations
from .store import read_state
from .views import LocateResult, entity_view, located_entity_view


def locate(project_root: Path, state: RegistryState, identity: str) -> LocateResult:
    entity = next((e for e in all_entities(state) if e["id"] == identity), None)
    require(entity is not None, "invalid_reference", f"Unregistered identity: {identity}. Use list to find the current identity.")
    assert entity is not None
    return located_entity_view(project_root, state, entity)


def _registry_path(project_root: Path) -> Path:
    return confined(project_root, ".project-state/state.json")


def locate_identity(project_root: Path, identity: str) -> LocateResult:
    return locate(project_root, read_state(_registry_path(project_root)), identity)


def _validate(project_root: Path, state: RegistryState) -> dict[str, bool]:
    types = provider_types(project_root)
    validate_relations(state, types)
    identities = identity_candidates(project_root, state)
    for artifact in state["artifacts"]:
        require(artifact["kind"] in types.artifacts, "missing_capability", f"No package declares {artifact['kind']}.")
        matches = sorted(identities.get(artifact["id"], set()))
        if len(matches) != 1:
            raise ProtocolError("identity_conflict" if matches else "invalid_reference", f"Expected one body for {artifact['id']}.", details=[str(p) for p in matches])
        _, declaration = read_declaration(project_root, matches[0])
        require(declaration.module_id == artifact.get("moduleId") and declaration.feature_ids == artifact["featureIds"],
                "declaration_changed", f"Ownership changed in {matches[0]}. Use register artifact to restore registered ownership, or pass --module and --feature to replace it.")
    return {"valid": True}


def _query(project_root: Path, state: RegistryState, invocation: Invocation) -> dict[str, Any]:
    if invocation.command == "list":
        kind = invocation.option("--kind")
        items = [e for e in all_entities(state) if kind is None or kind == entity_kind(e)
                 or kind == entity_kind(e).removeprefix("core:") and "kind" not in e or kind == "artifact" and "kind" in e]
        return {"items": [entity_view(e) for e in sorted(items, key=lambda e: identity_sort_key(e["id"]))]}
    if invocation.command == "locate":
        return dict(locate(project_root, state, invocation.args[0]))
    if invocation.command == "related":
        identity, direction = invocation.args[0], invocation.option("--direction") or "both"
        require(any(e["id"] == identity for e in all_entities(state)), "invalid_reference", f"Unregistered identity: {identity}. Use list to find current entities.")
        edges = [e for e in effective_relations(state) if (direction != "incoming" and e["from"] == identity)
                 or (direction != "outgoing" and e["to"] == identity)]
        ids = {e[key] for e in edges for key in ("from", "to")} - {identity}
        return {"items": [located_entity_view(project_root, state, e) for e in all_entities(state) if e["id"] in ids], "relations": edges}
    return _validate(project_root, state)


def execute(invocation: Invocation, *, cwd: Path | None = None) -> dict[str, Any]:
    project_root = current_project_root(cwd)
    state_file = _registry_path(project_root)
    if not invocation.command.startswith("register ") and invocation.command != "relate":
        return _query(project_root, read_state(state_file), invocation)
    confined(project_root, state_file.with_name(state_file.name + ".lock.sqlite"))
    with state_lock(state_file):
        state = read_state(state_file)
        before = json_bytes(state)
        if invocation.command == "relate":
            edge: Edge = {"from": invocation.args[0], "kind": invocation.args[1], "to": invocation.args[2]}
            data: dict[str, Any] = {"changed": change_relation(state, edge, "--remove" in invocation.options, provider_types(project_root))}
        else:
            data = register(state, project_root, invocation)
        validate_record(state)
        after = json_bytes(state)
        if after != before:
            atomic_write(state_file, after)
        return {**data, "changed": after != before or data["changed"]}
