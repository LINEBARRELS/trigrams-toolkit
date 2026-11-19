"""Read Registry JSON and reject unsupported formats before any mutation."""
from pathlib import Path
from typing import cast

from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.state_json import optional_bytes, parse_state_json
from .model import RegistryState, validate_record
from .relations import validate_identity_graph


def read_state(path: Path) -> RegistryState:
    raw = optional_bytes(path)
    if raw is None:
        return {"schemaVersion": 1, "modules": [], "features": [], "artifacts": [], "relations": []}
    try:
        value = parse_state_json(raw, bom=True)
    except ValueError as error:
        raise ProtocolError("io_error", f"Invalid Registry JSON: {path}") from error
    try:
        validate_record(value, code="invalid_schema")
        state = cast(RegistryState, value)
        for entity in [*state["modules"], *state["features"]]:
            entity["name"] = entity["name"].strip()
            require(bool(entity["name"]), "invalid_schema", "Entity names must not be blank.")
        for artifact in state["artifacts"]:
            artifact["title"] = artifact["title"].strip()
            require(bool(artifact["title"]), "invalid_schema", "Artifact titles must not be blank.")
    except ProtocolError as error:
        if error.code != "invalid_schema":
            raise
        raise ProtocolError("invalid_schema", f"Unsupported Registry format: {path}. Archive the existing state and rebuild it with project-setup.") from error
    validate_identity_graph(state)
    return state
