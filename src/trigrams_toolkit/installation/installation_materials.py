"""Build the files owned by a provider snapshot."""
from __future__ import annotations

import os
from pathlib import Path

from trigrams_toolkit.handbook.package import ProviderPackage, manifest_owner, runtime_cache
from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined, files_under, relative_path
from trigrams_toolkit.shared.serialization import canonical
from .operation_files import file_record


class ProjectMaterials:
    def __init__(self) -> None:
        self.records: dict[str, dict] = {}
        self.files: dict[str, bytes] = {}
        self.path_keys: set[str] = set()

    def add(self, name: str, provider: str, raw: bytes) -> None:
        relative_path(name)
        key = os.path.normcase(name)
        require(key not in self.path_keys, "resource_conflict", f"Installation sources share a target: {name}")
        self.path_keys.add(key)
        self.records[name] = file_record(name, provider, raw)
        self.files[name] = raw

    def _copy(self, root: Path, source: Path, target: str, provider: str) -> None:
        require(source != root, "invalid_reference", "An install mapping must select material within the provider.")
        for path in files_under(root, source, exclude=runtime_cache):
            suffix = path.relative_to(source).as_posix() if source.is_dir() else ""
            name = f"{target}/{suffix}" if suffix else target
            require(path.name.casefold() != "skill.md", "invalid_reference",
                    f"Install mappings cannot copy a Skill: {path}")
            self.add(name, provider, path.read_bytes())

    def extension(self, package: ProviderPackage) -> None:
        root, manifest = package.root, package.manifest
        owner = manifest_owner(manifest)
        prefix = f".agents/extensions/{owner}"
        self.add(f"{prefix}/extension.json", owner, canonical(manifest))
        for folder in ("principles", "workbooks"):
            source = root / folder
            if source.exists():
                self._copy(root, source, f"{prefix}/{folder}", owner)

    def declared(self, package: ProviderPackage) -> None:
        manifest, root = package.manifest, package.root
        owner = manifest_owner(manifest)
        for mapping in manifest["install"]:
            name = mapping["target"]
            relative_path(name)
            normalized = name.casefold()
            prefix = f".agents/extensions/{owner}/"
            owns_target = normalized.startswith(prefix) and normalized[len(prefix):].split("/")[0] not in (
                "principles", "workbooks", "extension.json", "resources.json")
            reserved = (".agents/skills", ".claude/skills", ".codex/skills",
                        ".pi/skills", ".pi/agent/skills", "skills-lock.json", ".git", ".harness",
                        ".harness-archive", ".project-state", ".agents/scripts", ".agents/tools",
                        ".agents/runtime", ".agents/harness.json", "docs", "agents.md", "claude.md",
                        "product.md", "design.md", "devtech.md", "readme.md", ".codex/agents",
                        ".claude/agents", ".pi/agents") + (() if owns_target else (".agents/extensions",))
            require(not any(normalized == path or normalized.startswith(path + "/")
                            or path.startswith(normalized + "/") for path in reserved)
                    and not normalized.endswith("/project-tools.zip"),
                    "invalid_reference", f"Material target belongs to another project owner: {name}")
            source = confined(root, mapping["source"])
            require(not source.is_relative_to(root / "tools"),
                    "invalid_reference", f"Public tools cannot be installed as project material: {source}")
            self._copy(root, source, name, owner)
