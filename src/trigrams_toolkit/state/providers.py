"""Artifact and relation types declared by the project and its installed extensions."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trigrams_toolkit.handbook.location import installed_extensions
from trigrams_toolkit.handbook.package import manifest_owner
from trigrams_toolkit.installation.installation_sources import read_installation
from trigrams_toolkit.resources import resource_path, schema_paths
from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import read_json
from trigrams_toolkit.shared.state_json import optional_bytes, parse_state_json
from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class Types:
    artifacts: frozenset[str]
    relations: dict[str, dict[str, Any]]
    same_artifact_kind: frozenset[str]


def _validate_project_package(value: Any) -> None:
    schema = read_json(resource_path("state/sources.schema.json"))
    error = next(Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/package"}).iter_errors(value), None)
    require(error is None, "invalid_schema", "Unsupported source format. Archive the existing state and rebuild it with project-setup.")


def _package_at(path: Path) -> dict[str, Any] | None:
    raw = optional_bytes(path)
    if raw is None:
        return None
    value = parse_state_json(raw, bom=True)
    if not isinstance(value, dict) or not any(key in value for key in ("source", "extension")):
        return None
    _validate_project_package(value)
    return _declaration(value)


def _declaration(value: dict[str, Any]) -> dict[str, Any]:
    owner = value.get("extension") or value["source"]
    relations = [{"kind": r["kind"], "fromKinds": r["fromKinds"], "toKinds": r["toKinds"],
                  "maxOutgoing": r.get("maxOutgoing"), "maxIncoming": r.get("maxIncoming"), "acyclic": r.get("acyclic", False)}
                 for r in value.get("relationTypes", [])]
    for kind in [*value.get("artifactTypes", []), *(r["kind"] for r in relations)]:
        require(kind.startswith(owner + ":"), "identity_conflict", f"Foreign provider type: {kind}")
    return {"source": owner, "artifactTypes": value.get("artifactTypes", []), "relationTypes": relations}


def provider_declarations(project_root: Path) -> list[dict[str, Any]]:
    schemas = SchemaCatalog(schema_paths())
    record = read_installation(project_root, schemas)
    declarations = {manifest_owner(package.manifest): _declaration(package.manifest)
                    for package in installed_extensions(project_root, record, schemas, guides=False)}
    for location in ("docs/resources.json", "resources.json"):
        item = _package_at(confined(project_root, location))
        if item is not None and item["source"] == "project":
            require("project" not in declarations, "resource_conflict", "Multiple project provider roots.")
            declarations["project"] = item
    return list(declarations.values())


def provider_types(project_root: Path) -> Types:
    core = read_json(resource_path("state/core-types.json"))
    artifacts = set(core["artifactTypes"])
    relations = {r["kind"]: r for r in core["relationTypes"]}
    for package in provider_declarations(project_root):
        artifacts.update(package["artifactTypes"])
        for relation in package["relationTypes"]:
            existing = relations.get(relation["kind"])
            require(existing is None or existing == relation, "resource_conflict", f"Conflicting relation: {relation['kind']}")
            relations[relation["kind"]] = relation
    return Types(frozenset(artifacts), relations, frozenset(core["sameArtifactKindRelations"]))
