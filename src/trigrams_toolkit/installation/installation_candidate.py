"""Preview snapshot writes and ownership changes without modifying the project."""
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.handbook.package import ProviderPackage, manifest_owner, package_manifest, resource_paths
from trigrams_toolkit.handbook.skill_sources import global_core, setup_package, snapshot_resource_paths
from trigrams_toolkit.handbook.sources import ProviderSource
from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import is_link
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import canonical
from trigrams_toolkit.shared.skill_installations import SkillAgent, skill_agent
from .installation_materials import ProjectMaterials
from .installation_sources import INSTALLATION, SNAPSHOT_SCHEMA, installation_record
from .operation_files import blocked_parent, file_record, matches, target_path, validate_owned_paths
from .operation_runtime import OperationCandidate


def _explicit_packages(project: Path, supplied: list[str], schemas: SchemaCatalog) -> list[ProviderPackage]:
    roots: list[Path | ProviderPackage] = []
    for value in supplied:
        path = Path(value)
        require(path.is_absolute(), "path_outside_root", f"Package source must be absolute: {value}")
        root = path.resolve()
        filename = "extension.json" if (root / "extension.json").is_file() else "resources.json"
        manifest = package_manifest(root, schemas, filename=filename)
        owner = manifest_owner(manifest)
        resources = (resource_paths(root, manifest["resourceRoots"]) if owner == "core"
                     else snapshot_resource_paths(root, manifest))
        roots.append(ProviderPackage(root, manifest, (ProviderSource(root, "package", resources),)))
    return list(GuideCatalog.discover(roots, project, schemas).packages.values())


def _sources(project: Path, parameters: dict, agent: SkillAgent, schemas: SchemaCatalog) -> list[ProviderPackage]:
    selected = set(parameters["extensions"])
    if "packages" in parameters:
        packages = _explicit_packages(project, parameters["packages"], schemas)
    else:
        core = global_core(agent)
        packages = [core] if core is not None else []
        packages.extend(setup_package(project, provider, agent, schemas) for provider in sorted(selected))
    require({manifest_owner(p.manifest) for p in packages} - {"core"} == selected, "missing_capability",
            "Supply exactly the selected extensions. A core source is optional in packages.")
    GuideCatalog.discover(packages, project, schemas).validate()
    return packages


def _changes(project: Path, previous: dict, desired: dict[str, dict]) -> tuple[list[dict], list[str]]:
    old = {item["path"]: item for item in previous["managed"]}
    conflicts: set[str] = set()
    changes = []
    for path in sorted(set(old) | set(desired)):
        before, after = old.get(path), desired.get(path)
        target = target_path(project, path)
        present = os.path.lexists(target)
        owned = matches(target, before) if present else True
        if after is not None and blocked_parent(project, target):
            conflicts.add(path)
        if present and not owned:
            conflicts.add(path)
        if (before == after and owned and present) or (after is None and not present):
            continue
        changes.append({"path": path, "action": "write" if after else "remove",
                        "before": before if present else None, "after": after})
    return changes, sorted(conflicts)


def _is_uninstall(previous: dict, desired: dict, changes: list[dict]) -> bool:
    before = {(entry["extension"], entry["version"]) for entry in previous["extensions"]}
    after = {(entry["extension"], entry["version"]) for entry in desired["extensions"]}
    retiring_core = any(item["source"] == "core" for item in previous["managed"])
    return (previous.get("agent") == desired["agent"] and after <= before
            and (after < before or (retiring_core and bool(changes)))
            and all(change["action"] == "remove" for change in changes))


def build_candidate(project: Path, data: dict, schemas: SchemaCatalog, operation_id: str | None = None) -> OperationCandidate:
    schemas.validate("urn:harness:installation-cli#/$defs/installPreviewInput", data)
    state_file = target_path(project, INSTALLATION)
    require(not any((project / name).exists() for name in (".agents/harness.yaml", ".agents/harness-lock.json")),
            "archive_required", "Archive retired state before installing project materials.")
    previous = installation_record(state_file, schemas)
    agent = skill_agent(data.get("agent") or previous.get("agent"))
    selected = data.get("extensions", [item["extension"] for item in previous["extensions"]])
    parameters = {**data, "agent": agent.name, "extensions": sorted(selected)}
    packages = _sources(project, parameters, agent, schemas)
    material = ProjectMaterials()
    extensions = []
    for package in packages:
        owner = manifest_owner(package.manifest)
        if owner != "core":
            container = project / ".agents/extensions" / owner
            require(not any(is_link(p) for p in (container.parent, container))
                    and (not container.exists() or container.is_dir()),
                    "invalid_reference", f"Extension container must be a real directory: {container}")
            material.extension(package)
            extensions.append({"extension": owner, "version": package.manifest["version"]})
        material.declared(package)
    validate_owned_paths(list(material.records), INSTALLATION)
    changes, conflicts = _changes(project, previous, material.records)
    source_roots = {manifest_owner(p.manifest): str(p.root) for p in packages if manifest_owner(p.manifest) != "core"}
    for change in changes:
        target = project / change["path"]
        for root in source_roots.values():
            source = Path(root)
            require(not target.is_relative_to(source) and not source.is_relative_to(target),
                    "path_outside_root", f"Installation target overlaps its source: {change['path']}")
    state = {"schemaVersion": 2, "stateRevision": previous["stateRevision"] + 1, "agent": agent.name,
             "extensions": sorted(extensions, key=lambda item: item["extension"]),
             "managed": [material.records[path] for path in sorted(material.records)]}
    schemas.validate(SNAPSHOT_SCHEMA, state)
    dependency_agent = None if _is_uninstall(previous, state, changes) else agent
    raw = canonical(state)
    before = file_record(INSTALLATION, "core", state_file.read_bytes()) if state_file.is_file() else None
    changes.append({"path": INSTALLATION, "action": "write", "before": before,
                    "after": file_record(INSTALLATION, "core", raw)})
    preview = {"schemaVersion": 2, "operationId": operation_id or "operation_" + uuid4().hex,
               "kind": "install", "projectRoot": str(project), "parameters": parameters,
               "baseRevision": previous["stateRevision"], "sources": source_roots,
               "changes": changes, "conflicts": conflicts}
    schemas.validate("urn:harness:installation#/$defs/preview", preview)
    files = {item["path"]: material.files[item["path"]] for item in changes
             if item["action"] == "write" and item["path"] != INSTALLATION}
    files[INSTALLATION] = raw
    changed = len(changes) > 1 or state != {**previous, "stateRevision": state["stateRevision"]}
    return OperationCandidate(preview, files, INSTALLATION, changed, dependency_agent)
