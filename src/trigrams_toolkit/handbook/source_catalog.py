"""Read repository provider declarations without generating runtime payloads."""
from __future__ import annotations

from pathlib import Path

from trigrams_toolkit.shared.errors import require
from .guides import GuideCatalog
from .package import ProviderPackage, resource_paths
from trigrams_toolkit.shared.paths import confined
from trigrams_toolkit.resources import resource_path, schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import read_json
from .sources import ProviderSource


def source_packages(toolkit: Path, schemas: SchemaCatalog) -> list[ProviderPackage]:
    """Compose source-only declarations; core types have one contract authority."""
    toolkit = toolkit.resolve()
    manifest = read_json(toolkit / "toolkit.json")
    components = [("core", manifest["core"]), *manifest.get("extensions", {}).items()]
    packages = []
    for provider, component in components:
        relative = component.get("manifest") or component["package"]
        path = confined(toolkit, relative)
        require(not (toolkit / relative).is_symlink(), "path_outside_root",
                f"Linked resource declaration: {path}")
        declaration = read_json(path)
        require(isinstance(declaration, dict), "invalid_schema", f"Resource declaration must be an object: {path}")
        owner = declaration.get("source") if provider == "core" else declaration.get("extension")
        require(owner == provider, "identity_conflict",
                f"Resource declaration differs from toolkit index: {path}")
        if provider == "core":
            require(not {"artifactTypes", "relationTypes"} & declaration.keys(), "invalid_schema",
                    "Core types belong only in resources/state/core-types.json.")
            types = read_json(resource_path("state/core-types.json"))
            declaration = {**declaration, "artifactTypes": types["artifactTypes"],
                           "relationTypes": types["relationTypes"]}
        schema_id = ("urn:harness:guides#/$defs/resourceManifest" if provider == "core"
                     else "urn:harness:guides#/$defs/extensionManifest")
        schemas.validate(schema_id, declaration)
        for kind in declaration.get("artifactTypes", []) + [item["kind"] for item in declaration.get("relationTypes", [])]:
            require(kind.split(":")[0] == provider, "invalid_reference", f"Foreign provider type: {kind}")
        root = path.parent
        source = ProviderSource(root, "package", resource_paths(root, declaration["resourceRoots"]),
                                tuple(declaration.get("install", [])))
        packages.append(ProviderPackage(root, declaration, (source,)))
    return packages


def validate_source_catalog(toolkit: Path) -> dict:
    """Validate provider identities, guide metadata and cross-resource references."""
    schemas = SchemaCatalog(schema_paths())
    catalog = GuideCatalog.discover(source_packages(toolkit, schemas), toolkit, schemas)
    catalog.validate()
    return {"resources": len(catalog.list()["resources"]), "sources": sorted(catalog.packages)}
