"""Resolve package declarations and installed guide source boundaries."""
from __future__ import annotations

from pathlib import Path, PurePosixPath

from trigrams_toolkit.installation.installation_sources import read_installation
from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined, is_link
from trigrams_toolkit.shared.skill_installations import skill_agent
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import read_json
from .package import ProviderPackage, load_packages, manifest_owner, package_manifest
from .skill_sources import global_core
from .sources import ProviderSource


def project_provider_root(project: Path) -> Path | None:
    root = confined(project, "docs")
    path = confined(root, "resources.json")
    if not path.is_file():
        return None
    value = read_json(path)
    return root if isinstance(value, dict) and value.get("source") == "project" else None


def _snapshot_file(project: Path, relative: str) -> Path:
    target = project / relative
    require(target == confined(project, relative) and target.is_file(), "invalid_reference",
            f"Snapshot file must be a regular project file: {relative}")
    return target


def _installed_extension(project: Path, item: dict, managed: list[dict],
                         schemas: SchemaCatalog, *, guides: bool) -> ProviderPackage:
    extension = item["extension"]
    prefix = f".agents/extensions/{extension}"
    container = project / prefix
    require(not any(is_link(part) for part in (project / ".agents", container.parent, container)),
            "invalid_reference", f"Extension container must be a real directory: {container}")
    confined(project, prefix)
    records = {record["path"]: record for record in managed if record["source"] == extension}
    relative = prefix + "/extension.json"
    require(relative in records, "invalid_reference", f"Snapshot declaration is not registered: {relative}")
    _snapshot_file(project, relative)
    manifest = package_manifest(container, schemas, filename="extension.json", expected_provider=extension)
    require(manifest["version"] == item["version"],
            "identity_conflict", f"Installed snapshot identity or version differs: {relative}")
    if not guides:
        return ProviderPackage(container, manifest, ())
    starts = [PurePosixPath(prefix, name) for name in manifest["resourceRoots"]]
    entries = tuple(_snapshot_file(project, rel) for rel in sorted(records)
                    if PurePosixPath(rel).name in ("WORKBOOK.md", "PRINCIPLE.md")
                    and any(PurePosixPath(rel).is_relative_to(start) for start in starts))
    return ProviderPackage(container, manifest, (ProviderSource(container, "installed-resource", entries),))


def installed_extensions(project: Path, record: dict | None, schemas: SchemaCatalog,
                         *, guides: bool = True) -> list[ProviderPackage]:
    if record is None:
        return []
    return [_installed_extension(project, item, record["managed"], schemas, guides=guides)
            for item in record["extensions"]]


def sources_for_project(project: Path, schemas: SchemaCatalog,
                        agent: str | None = None) -> dict[str, ProviderPackage]:
    """Resolve current provider declarations without Plan or Registry reads."""
    project = project.resolve()
    record = read_installation(project, schemas)
    core = global_core(skill_agent(agent or (record or {}).get("agent")))
    packages: dict[str, ProviderPackage] = {}
    if core is not None:
        packages["core"] = core
    for package in installed_extensions(project, record, schemas):
        packages[manifest_owner(package.manifest)] = package
    local = project_provider_root(project)
    if local is not None:
        packages.update(load_packages([local], project, schemas))
    return dict(sorted(packages.items()))
