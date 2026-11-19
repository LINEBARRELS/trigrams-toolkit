"""Guide sources carried by installed core and extension setup Skills."""
from __future__ import annotations

from pathlib import Path

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.skill_installations import SkillAgent, installed_skill, skill_directory
from .package import ProviderPackage, package_manifest, resource_paths, yaml_mapping
from .sources import ProviderSource


def _check_name(root: Path, expected: str) -> None:
    path = confined(root, "SKILL.md")
    with path.open(encoding="utf-8-sig") as stream:
        opener = stream.readline().rstrip("\r\n")
        lines = []
        for line in stream:
            if line.rstrip("\r\n") == "---":
                break
            lines.append(line)
        else:
            lines.clear()
    require(opener == "---" and bool(lines) and yaml_mapping("".join(lines)).get("name") == expected,
            "identity_conflict", f"Expected Skill name {expected}: {path}.")


def global_core(agent: SkillAgent) -> ProviderPackage | None:
    sources = []
    for skill, directory in (("principles", "principles"), ("workbook", "workbooks")):
        root = installed_skill(skill, agent, required=False)
        if root is not None:
            _check_name(root, skill)
            sources.append(ProviderSource(root, "installed-skill", resource_paths(root, [directory])))
    if not sources:
        return None
    manifest = {"schemaVersion": 1, "source": "core", "version": "1.0.0",
                "resourceRoots": [], "install": []}
    return ProviderPackage(skill_directory(agent), manifest, tuple(sources))


def setup_package(project: Path, provider: str, agent: SkillAgent, schemas: SchemaCatalog) -> ProviderPackage:
    name = f"extension-setup-{provider}"
    skill = installed_skill(name, agent, project)
    assert skill is not None
    _check_name(skill, name)
    root = confined(skill, "assets")
    manifest = package_manifest(root, schemas, filename="extension.json", expected_provider=provider)
    paths = snapshot_resource_paths(root, manifest)
    return ProviderPackage(root, manifest, (ProviderSource(root, "installed-skill", paths),))


def snapshot_resource_paths(root: Path, manifest: dict) -> tuple[Path, ...]:
    for name in manifest["resourceRoots"]:
        require(name.split("/")[0] in ("principles", "workbooks"), "invalid_reference",
                f"Snapshot resources must be in principles/ or workbooks/: {name}")
        require(confined(root, name).is_dir(), "invalid_reference", f"Resource directory is missing: {root / name}")
    return resource_paths(root, manifest["resourceRoots"])
