"""Read-only workbook and principle discovery and includes loading."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from trigrams_toolkit.shared.errors import require
from .guide_headers import guide_header
from .package import ProviderPackage, load_packages, manifest_owner
from trigrams_toolkit.shared.paths import path_key
from trigrams_toolkit.shared.schema import SchemaCatalog

ENTRY_KINDS = {"WORKBOOK.md": "workbook", "PRINCIPLE.md": "principle"}


@dataclass(frozen=True)
class Guide:
    resource_id: str
    kind: str
    path: Path
    source: Path
    header: dict

    @property
    def scope(self) -> str:
        if self.kind == "principle":
            return self.path.parent.parent.name
        return self.path.parent.name.split("-", 1)[0]

    def description(self) -> dict:
        name = self.path.parent.name if self.kind == "principle" else self.header["name"]
        result = {"resourceId": self.resource_id, "kind": self.kind, "name": name,
                  "description": self.header["description"], "entryPath": str(self.path), "source": str(self.source)}
        if self.header.get("includes"):
            result["includes"] = self.header["includes"]
        return result


def _guide(path: Path, package: ProviderPackage, schemas: SchemaCatalog, source: Path) -> Guide:
    kind = ENTRY_KINDS[path.name]
    header = guide_header(path, schemas)
    provider = manifest_owner(package.manifest)
    if kind == "principle":
        require(path.parent.parent.parent.name == "principles", "invalid_schema",
                "Principles require principles/<scope>/<principle>/PRINCIPLE.md.", str(path))
        for name in (path.parent.parent.name, path.parent.name):
            schemas.validate("urn:harness:common#/$defs/token", name)
        identity = f"{provider}:principle:{path.parent.parent.name}/{path.parent.name}"
    else:
        identity = header.get("resourceId", f"{provider}:{kind}:{path.parent.name}")
    schemas.validate("urn:harness:guides#/$defs/guideId", identity)
    require(identity.split(":")[:2] == [provider, kind], "identity_conflict",
            f"Guide ID must match its package and entry kind: {identity}", str(path))
    return Guide(identity, kind, path, source, header)


class GuideCatalog:
    def __init__(self, packages: dict[str, ProviderPackage], schemas: SchemaCatalog) -> None:
        self.packages = packages
        self._guides: dict[str, Guide] = {}
        physical: set[str] = set()
        for package in packages.values():
            self._index_package(package, schemas, physical)

    def _index_package(self, package: ProviderPackage, schemas: SchemaCatalog, physical: set[str]) -> None:
        for source in package.sources:
            for path in source.resource_paths:
                guide = _guide(path, package, schemas, source.root)
                require(guide.resource_id not in self._guides, "resource_conflict",
                        f"Duplicate guide ID: {guide.resource_id}", str(guide.path))
                require(path_key(guide.path) not in physical, "resource_conflict",
                        f"Guide entry has multiple source paths: {guide.path}")
                physical.add(path_key(guide.path))
                self._guides[guide.resource_id] = guide

    @classmethod
    def discover(cls, roots: Sequence[Path | ProviderPackage], project: Path,
                 schemas: SchemaCatalog) -> GuideCatalog:
        return cls(load_packages(list(roots), project, schemas), schemas)

    def resolve(self, identity: str) -> Guide:
        exact = self._guides.get(identity)
        if exact is not None:
            return exact
        candidates = [self._guides[key] for key in sorted(self._guides)
                      if key.rsplit(":", 1)[-1] == identity]
        require(bool(candidates), "invalid_reference", f"Guide unavailable: {identity}. Use handbook list.")
        require(len(candidates) == 1, "resource_conflict",
                f"Guide name is ambiguous: {identity}. Use a full ID.",
                *(guide.resource_id for guide in candidates))
        return candidates[0]

    def scopes(self, kind: str | None = None) -> dict:
        return {"ok": True, "scopes": sorted({guide.scope for guide in self._guides.values()
                                             if kind is None or guide.kind == kind})}

    def list(self, kind: str | None = None, scopes: Sequence[str] = ()) -> dict:
        requested = set(scopes)
        values = []
        for identity in sorted(self._guides):
            guide = self._guides[identity]
            if kind is not None and kind != guide.kind:
                continue
            if requested and guide.scope not in requested:
                continue
            values.append({"resourceId": guide.resource_id, "description": guide.header["description"]})
        return {"ok": True, "resources": values}

    def _closure(self, identity: str, ancestors: tuple[str, ...], selected: dict[str, Guide]) -> None:
        require(identity not in ancestors, "invalid_reference",
                f"Guide includes cycle: {' -> '.join((*ancestors, identity))}")
        if identity in selected:
            return
        guide = self._guides.get(identity)
        require(guide is not None, "invalid_reference", f"Included guide unavailable: {identity}.")
        assert guide is not None
        if guide.kind == "workbook":
            for child in guide.header.get("includes", []):
                self._closure(child, (*ancestors, identity), selected)
        selected[identity] = guide

    def load(self, identities: str | Sequence[str]) -> dict:
        inputs = [identities] if isinstance(identities, str) else identities
        require(bool(inputs), "invalid_arguments", "Provide at least one guide ID.")
        selected_ids = list(dict.fromkeys(self.resolve(identity).resource_id for identity in inputs))
        selected: dict[str, Guide] = {}
        for identity in selected_ids:
            self._closure(identity, (), selected)
        values = [{**item.description(), "content": item.path.read_text(encoding="utf-8-sig")}
                  for item in selected.values()]
        result = {"ok": True, "selectedIds": selected_ids, "resources": values}
        if len(inputs) == 1:
            result["selected"] = selected_ids[0]
        return result

    def validate(self) -> dict:
        for identity in self._guides:
            self._closure(identity, (), {})
        return {"ok": True, "checkedSources": sorted({str(package.root) for package in self.packages.values()}),
                "resourceIds": sorted(self._guides)}
