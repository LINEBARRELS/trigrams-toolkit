"""Package metadata and declared resource source boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import yaml

from trigrams_toolkit.shared.errors import ProtocolError, require
from .model import JsonObject
from trigrams_toolkit.shared.paths import confined, files_under, path_key
from .sources import ProviderSource
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import read_json

_GENERATED = frozenset({".agents", ".git", "node_modules", "__pycache__",
                        ".pytest_cache", ".cache"})
_RUNTIME_CACHE = frozenset({"__pycache__", ".pytest_cache", ".cache"})


class _UniqueYaml(yaml.SafeLoader):
    pass


def _yaml_object(loader: _UniqueYaml, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        require(isinstance(key, str) and key not in result, "invalid_json", "Duplicate/non-string YAML key.")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


_UniqueYaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_object)


def yaml_mapping(source: str) -> JsonObject:
    try:
        value = yaml.load(source, Loader=_UniqueYaml)
    except yaml.YAMLError as error:
        raise ProtocolError("invalid_json", "Invalid YAML metadata.") from error
    require(isinstance(value, dict), "invalid_schema", "Metadata must be a mapping.")
    return value


def _generated(relative: str) -> bool:
    return any(os.path.normcase(part) in _GENERATED for part in relative.split("/"))


def runtime_cache(relative: str) -> bool:
    """Interpreter/test caches are excluded from managed sources."""
    return relative.endswith(".pyc") or any(part in _RUNTIME_CACHE for part in relative.split("/"))


@dataclass(frozen=True)
class ProviderPackage:
    root: Path
    manifest: JsonObject
    sources: tuple[ProviderSource, ...]


def manifest_owner(manifest: JsonObject) -> str:
    owner = manifest.get("extension") or manifest.get("source")
    require(isinstance(owner, str) and bool(owner), "invalid_schema", "Manifest owner is missing.")
    assert isinstance(owner, str)
    return owner


def package_manifest(root: Path, schemas: SchemaCatalog, *, filename: str = "resources.json",
                     expected_provider: str | None = None) -> JsonObject:
    """Read the complete package declaration without reading source payloads."""
    path = confined(root, filename)
    require(path.is_file(), "invalid_schema",
            f"Resource declaration is missing: {path}.", str(root))
    return _validate_manifest(read_json(path), path, schemas, expected_provider)


def _validate_manifest(manifest: JsonObject, path: Path, schemas: SchemaCatalog,
                       expected_provider: str | None = None) -> JsonObject:
    if isinstance(manifest, dict):
        manifest = {key: value for key, value in manifest.items() if key != "contentDigest"}
    schema_id = (
        "urn:harness:guides#/$defs/extensionManifest" if path.name == "extension.json"
        else "urn:harness:guides#/$defs/resourceManifest" if path.name == "resources.json"
        else "urn:harness:guides#/$defs/package"
    )
    try:
        schemas.validate(schema_id, manifest)
    except ProtocolError as error:
        recovery = " Archive previous state and rebuild." if path.name == "resources.json" else ""
        raise ProtocolError(error.code, f"{path}: {error}.{recovery}",
                            conflicts=(str(path),)) from error
    owner = manifest_owner(manifest)
    require(expected_provider is None or expected_provider == owner, "identity_conflict",
            f"Expected {expected_provider}, found {owner}: {path}")
    for kind in manifest.get("artifactTypes", []) + [item["kind"] for item in manifest.get("relationTypes", [])]:
        require(kind.split(":")[0] == owner, "invalid_reference", f"Foreign type: {kind}")
    return manifest


def resource_root(root: Path, relative: str) -> Path:
    """Validate the shared guide source boundary without scanning its content."""
    start = confined(root, relative)
    require(not _generated(relative), "invalid_reference", f"Generated resource root: {relative}")
    return start


def resource_paths(root: Path, roots: list[str] | None, *, split: bool = False) -> tuple[Path, ...]:
    """Find guide entries within each declared physical source boundary."""
    root = root.resolve()
    if roots is None:
        roots = [child.name for child in sorted(root.iterdir()) if not _generated(child.name)]
    paths: dict[str, Path] = {}
    for relative in roots:
        start = resource_root(root, relative)
        if split and not start.exists():
            continue
        for path in files_under(root, start, exclude=_generated):
            name = path.relative_to(root).as_posix()
            if runtime_cache(name):
                continue
            require(not (_generated(name) or _generated(path.resolve().relative_to(root).as_posix())),
                    "invalid_reference", "Generated content cannot be a guide source.", str(path))
            require(path.name not in ("resource.json", "resource.yaml", "resource.yml", "provider.json", "package.json", "extension.json", "resources.json"),
                    "invalid_schema", f"Unsupported guide declaration: {path}. Archive previous state and rebuild.")
            if path.name in ("WORKBOOK.md", "PRINCIPLE.md"):
                key = path_key(path)
                require(key not in paths, "resource_conflict", "Guide entry has multiple physical paths.", str(path))
                paths[key] = path
    return tuple(paths.values())


def load_packages(roots: list[Path | ProviderPackage], project: Path, schemas: SchemaCatalog) -> dict[str, ProviderPackage]:
    """Load complete provider packages and preserve their physical owners."""
    packages: dict[str, ProviderPackage] = {}
    seen_roots: set[str] = set()
    for supplied in roots:
        if isinstance(supplied, ProviderPackage):
            name = "extension.json" if "extension" in supplied.manifest else "resources.json"
            _validate_manifest(supplied.manifest, supplied.root / name, schemas)
            package = supplied
        else:
            require(supplied.is_absolute(), "path_outside_root", "Source roots must be absolute.", str(supplied))
            root = supplied.resolve()
            key = path_key(root)
            if key in seen_roots:
                continue
            seen_roots.add(key)
            filename = "extension.json" if (root / "extension.json").is_file() else "resources.json"
            manifest = package_manifest(root, schemas, filename=filename)
            source = ProviderSource(root, "package", resource_paths(root, manifest["resourceRoots"]), tuple(manifest["install"]))
            package = ProviderPackage(root, manifest, (source,))
        owner = manifest_owner(package.manifest)
        require(owner != "project" or package.root.is_relative_to(project.resolve()), "path_outside_root",
                "The project resource source must belong to the current project.", str(package.root))
        require(owner not in packages, "resource_conflict", f"Multiple package sources for source: {owner}")
        packages[owner] = package
    return packages


def load_package(root: Path, project: Path, schemas: SchemaCatalog) -> ProviderPackage:
    packages = load_packages([root], project, schemas)
    return next(iter(packages.values()))
