"""Prepare and publish the project package declaration for resource imports."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Any

from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.files import atomic_write
from .package import manifest_owner, package_manifest, resource_root
from trigrams_toolkit.shared.paths import confined
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import canonical


@dataclass(frozen=True)
class ProjectResourceDeclaration:
    """A validated preparation; callers use path, changed and write()."""

    path: Path
    changed: bool
    _content: bytes

    def write(self) -> bool:
        """Publish changed bytes; report the actual file result after I/O failure."""
        if not self.changed:
            return False
        try:
            atomic_write(self.path, self._content)
        except OSError as error:
            try:
                written = self.path.read_bytes() == self._content
            except (FileNotFoundError, NotADirectoryError):
                written = False
            except OSError:
                written = None
            raise ProtocolError("io_error", f"Cannot publish project declaration {self.path}: {error}",
                                current={"packagePath": str(self.path), "packageWritten": written}) from error
        return True


def prepare_project_resources(project: Path, resource_roots: Sequence[str],
                              schemas: SchemaCatalog) -> ProjectResourceDeclaration:
    """Validate and merge roots without creating directories or files.

    Existing fields and root spellings survive. An existing parent covers its
    descendants; a requested parent conflicting with an existing child fails.
    """
    docs = confined(project, "docs")
    path = confined(project, "docs/resources.json")
    try:
        exists = path.exists()
        manifest: dict[str, Any] = package_manifest(docs, schemas, filename="resources.json") if exists else {
            "schemaVersion": 1, "source": "project", "version": "1.0.0",
            "resourceRoots": [], "install": []}
        require(manifest_owner(manifest) == "project", "identity_conflict",
                f"Project declaration source must be project: {path}", str(path))
        roots = list(manifest["resourceRoots"])
        locations: list[Path] = []
        for relative in roots:
            location = resource_root(docs, relative)
            require(not any(location.is_relative_to(existing) or existing.is_relative_to(location)
                            for existing in locations), "resource_conflict",
                    f"Project resource roots overlap: {relative}", str(path))
            locations.append(location)
        changed = not exists
        for relative in resource_roots:
            requested = resource_root(docs, relative)
            if any(requested.is_relative_to(existing) for existing in locations):
                continue
            require(not any(existing.is_relative_to(requested) for existing in locations),
                    "resource_conflict", f"Requested resource root overlaps an existing child: {relative}", str(path))
            roots.append(relative)
            locations.append(requested)
            changed = True
        manifest = {**manifest, "resourceRoots": roots}
        schemas.validate("urn:harness:guides#/$defs/resourceManifest", manifest)
        return ProjectResourceDeclaration(path, changed, canonical(manifest) + b"\n")
    except OSError as error:
        raise ProtocolError("io_error", f"Cannot prepare project declaration {path}: {error}") from error
