"""Register entities; document publication precedes Registry publication."""
from __future__ import annotations

from pathlib import Path
import secrets
import string
from typing import Any, TypeVar, cast

from trigrams_toolkit.project_context.paths import path_key, resolve_project_path
from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.files import atomic_write
from .arguments import Invocation
from .identity import artifact_from_document, read_declaration, with_registration
from .location import identity_candidates
from .model import Entity, Feature, Module, RegistryState, all_entities, validate_record
from .providers import provider_types
from .relations import validate_identity_graph, validate_ownership, validate_relations

_Entity = TypeVar("_Entity", bound=Entity)


def _identity(prefix: str) -> str:
    return prefix + "_" + "".join(secrets.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase) for _ in range(10))


def _save(items: list[_Entity], entity: _Entity) -> list[_Entity]:
    for index, item in enumerate(items):
        if item["id"] == entity["id"]:
            return [*items[:index], entity, *items[index + 1:]]
    return [*items, entity]


def _named(state: RegistryState, invocation: Invocation) -> dict[str, Any]:
    module = invocation.command == "register module"
    identity = invocation.option("--id") or _identity("module" if module else "feature")
    existing = next((e for e in all_entities(state) if e["id"] == identity), None)
    name = invocation.args[0].strip()
    if module:
        require(existing is None or ("kind" not in existing and "moduleId" not in existing), "identity_conflict", f"ID belongs to another entity: {identity}")
        module_entity = Module(id=identity, name=name)
        validate_record(module_entity, "module")
        state["modules"] = _save(state["modules"], module_entity)
        entity: Entity = module_entity
    else:
        owner = invocation.option("--module") or (cast(Any, existing).get("moduleId") if existing else None)
        require(bool(owner), "invalid_arguments", "New Features require --module MODULE_ID.")
        assert owner is not None
        feature_entity = Feature(id=identity, name=name, moduleId=owner)
        validate_record(feature_entity, "feature")
        state["features"] = _save(state["features"], feature_entity)
        entity = feature_entity
    validate_identity_graph(state)
    return {"entity": entity, "changed": False}


def register(state: RegistryState, project_root: Path, invocation: Invocation, *, cwd: Path | None = None) -> dict[str, Any]:
    if invocation.command != "register artifact":
        return _named(state, invocation)
    path = resolve_project_path(project_root, invocation.args[0], cwd=cwd)
    source, declaration = read_declaration(project_root, path, ignore_ownership=True)
    identity = declaration.identity or _identity("artifact")
    existing = next((a for a in state["artifacts"] if a["id"] == identity), None)
    kind = invocation.option("--kind") or (existing["kind"] if existing else "core:document")
    types = provider_types(project_root)
    require(kind in types.artifacts, "missing_capability", f"No package declares Artifact kind: {kind}")
    explicit = "--module" in invocation.options
    module = invocation.option("--module") if explicit else (existing.get("moduleId") if existing else None)
    features = invocation.options.get("--feature", []) if explicit else (existing["featureIds"] if existing else [])
    # Ownership duplicates use the existing business error, before schema uniqueItems.
    require(len(set(features)) == len(features), "invalid_reference", f"Duplicate featureIds in {identity}.")
    entity = artifact_from_document(project_root, path, declaration, identity, kind, module, list(features))
    validate_ownership(state, entity)
    matches = sorted(identity_candidates(project_root, state, (path,)).get(identity, set()))
    if any(path_key(item) != path_key(path) for item in matches):
        raise ProtocolError("identity_conflict", f"Another body declares {identity}.", details=[str(p) for p in matches])
    state["artifacts"] = _save(state["artifacts"], entity)
    validate_identity_graph(state)
    validate_relations(state, types)
    updated = with_registration(source, entity)
    if updated != source:
        atomic_write(path, updated.encode("utf-8"))
    return {"entity": entity, "changed": updated != source}
