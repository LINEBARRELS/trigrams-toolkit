"""Read current project installation ownership."""
from pathlib import Path

from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.paths import is_link
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import read_json
from .operation_files import target_path, validate_owned_paths

INSTALLATION = ".agents/harness.json"
INSTALLATION_SCHEMA = "urn:harness:installation#/$defs/installation"
SNAPSHOT_SCHEMA = "urn:harness:installation#/$defs/snapshotInstallation"


def read_installation(project: Path, schemas: SchemaCatalog) -> dict | None:
    path = target_path(project, INSTALLATION)
    require(not is_link(path), "invalid_reference", f"Installation record must be a regular file: {path}")
    if not path.exists():
        return None
    value = read_json(path)
    try:
        schemas.validate(INSTALLATION_SCHEMA, value)
    except ProtocolError as error:
        raise ProtocolError(error.code, f"{path}: {error}. Archive unsupported records before rebuilding.",
                            conflicts=(str(path),)) from error
    extensions = [item["extension"] for item in value["extensions"]]
    require(len(set(extensions)) == len(extensions), "resource_conflict", "Duplicate installed extension.")
    validate_owned_paths([item["path"] for item in value["managed"]], INSTALLATION)
    return value


def installation_record(path: Path, schemas: SchemaCatalog) -> dict:
    return read_installation(path.parent.parent, schemas) or {
        "schemaVersion": 2, "stateRevision": 0, "extensions": [], "platforms": [], "managed": []}
