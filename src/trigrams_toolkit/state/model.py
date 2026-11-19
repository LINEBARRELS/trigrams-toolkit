"""Registry records and schema-validated entity boundaries."""
from __future__ import annotations

from functools import cache
from typing import Any, Literal, NotRequired, TypedDict, cast
from jsonschema import Draft202012Validator

from trigrams_toolkit.resources import resource_path
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.serialization import read_json


class Module(TypedDict):
    id: str
    name: str


class Feature(Module):
    moduleId: str


class Artifact(TypedDict):
    id: str
    kind: str
    title: str
    locatorHint: str
    identityMode: Literal["frontmatter", "manifest"]
    moduleId: NotRequired[str]
    featureIds: list[str]


Entity = Module | Feature | Artifact


# `from` is a Python keyword, so its wire type uses functional TypedDict syntax.
Edge = TypedDict("Edge", {"kind": str, "from": str, "to": str})


class RegistryState(TypedDict):
    schemaVersion: int
    modules: list[Module]
    features: list[Feature]
    artifacts: list[Artifact]
    relations: list[Edge]


@cache
def state_schema() -> dict[str, Any]:
    return read_json(resource_path("state/state.schema.json"))


def validate_record(value: Any, definition: str | None = None, *, code: str = "io_error") -> None:
    schema = state_schema()
    if definition:
        schema = {"$defs": schema["$defs"], "$ref": f"#/$defs/{definition}"}
    error = next(Draft202012Validator(schema).iter_errors(value), None)
    if error is not None:
        if error.validator == "uniqueItems":
            raise ProtocolError("invalid_reference", "Duplicate featureIds in Artifact.")
        raise ProtocolError(code, f"{error.json_path}: {error.message}")


def all_entities(state: RegistryState) -> list[Entity]:
    return [*state["modules"], *state["features"], *state["artifacts"]]


def entity_kind(entity: Entity) -> str:
    if "kind" in entity:
        return cast(Artifact, entity)["kind"]
    return "core:feature" if "moduleId" in entity else "core:module"


def identity_sort_key(identity: str) -> tuple[tuple[int, ...], tuple[bool, ...]]:
    """Locale collation for the Registry's ASCII ID alphabet, lowercase first."""
    alphabet = "_-0123456789abcdefghijklmnopqrstuvwxyz"
    return tuple(alphabet.index(c.lower()) for c in identity), tuple(c.isupper() for c in identity)
