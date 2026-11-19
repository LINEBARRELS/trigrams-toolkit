"""Local contract registration; schema retrieval never uses the network."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

from .errors import ProtocolError, require
from .serialization import read_json, scalar_json


class SchemaCatalog:
    """@to-plan P04/S01

    Register source schemas by their own $id and reject unresolved local URNs.
    T02 uses jsonschema Draft202012Validator plus referencing.Registry; callers
    supply the contract files and no validator may fetch a missing remote schema.
    """

    def __init__(self, paths: Sequence[Path]) -> None:
        self.paths = tuple(paths)
        schemas: dict[str, Any] = {}
        try:
            for path in self.paths:
                schema = read_json(path)
                Draft202012Validator.check_schema(schema)
                identity = schema["$id"]
                require(identity not in schemas, "invalid_schema", f"Duplicate schema: {identity}")
                schemas[identity] = schema
            self._registry = Registry().with_resources(
                (identity, Resource.from_contents(value)) for identity, value in schemas.items())
            for identity, schema in schemas.items():
                for ref in _references(schema):
                    self._registry.resolver(identity).lookup(ref)
        except (SchemaError, Unresolvable, KeyError) as error:
            raise ProtocolError("invalid_schema", f"Invalid local contract closure: {error}") from error

    def validate(self, reference: str, value: Any) -> None:
        scalar_json(value)
        try:
            validator = Draft202012Validator({"$ref": reference}, registry=self._registry,
                                             format_checker=FormatChecker())
            error = next(validator.iter_errors(value), None)
            if error is not None:
                raise ProtocolError("invalid_schema", f"{error.json_path}: {error.message}")
        except Unresolvable as error:
            raise ProtocolError("invalid_schema", f"Missing local schema: {reference}") from error


def _references(value: Any) -> list[str]:
    if isinstance(value, dict):
        own = [value["$ref"]] if "$ref" in value else []
        return own + [ref for item in value.values() for ref in _references(item)]
    if isinstance(value, list):
        return [ref for item in value for ref in _references(item)]
    return []
