"""Check versioned local schemas and command declarations without mutations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.serialization import parse_json_document

CONTRACT_ROOTS = (
    "src/trigrams_toolkit/resources/plan",
    "src/trigrams_toolkit/resources/state",
    "src/trigrams_toolkit/resources/handbook",
    "src/trigrams_toolkit/resources/installation",
    "src/trigrams_toolkit/resources/shared",
)


def read_json(path: Path) -> Any:
    """Read document JSON without adding runtime-value restrictions."""
    try:
        return parse_json_document(path.read_bytes())
    except ProtocolError as error:
        raise ValueError(f"{path}: {error}") from error


def _references(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        if "$ref" in value:
            result.append(value["$ref"])
        for child in value.values():
            result.extend(_references(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(_references(child))
    return result


def _load_schemas(repository: Path) -> tuple[Registry, dict[str, dict[str, Any]]]:
    schemas: dict[str, dict[str, Any]] = {}
    for root in CONTRACT_ROOTS:
        paths = sorted((repository / root).glob("*.schema.json"))
        if not paths:
            raise ValueError(f"{root}: no schemas found")
        for path in paths:
            schema = read_json(path)
            Draft202012Validator.check_schema(schema)
            identity = schema["$id"]
            if identity in schemas:
                raise ValueError(f"{path}: duplicate schema ID {identity}")
            schemas[identity] = schema
    registry = Registry().with_resources(
        (identity, Resource.from_contents(schema)) for identity, schema in schemas.items()
    )
    for identity, schema in schemas.items():
        for ref in _references(schema):
            try:
                registry.resolver(identity).lookup(ref)
            except Unresolvable as error:
                raise ValueError(f"{identity}: unresolved local schema reference {ref}") from error
    return registry, schemas


def check_contracts(repository: Path) -> list[str]:
    """Validate local schema closure and declared command references without IO mutations."""
    try:
        registry, _ = _load_schemas(repository)
        seen = set()
        paths = sorted(path for root in CONTRACT_ROOTS
                       for path in (repository / root).glob("*commands*.json"))
        for path in paths:
            catalog = read_json(path)
            if catalog.get("schemaVersion") != 1 or not catalog.get("commands"):
                raise ValueError(f"Invalid command catalog: {path}")
            for command in catalog["commands"]:
                identity = (catalog["tool"], command["name"])
                if identity in seen or type(command["mutation"]) is not bool:
                    raise ValueError(f"Duplicate or invalid command: {path}: {identity}")
                seen.add(identity)
                for field in ("input", "output"):
                    if field in command:
                        registry.resolver().lookup(command[field])
        return []
    except (OSError, ValueError, KeyError, TypeError, Unresolvable, SchemaError) as error:
        return [f"protocol check: {error}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Toolkit source root; all references resolve offline.")
    issues = check_contracts(parser.parse_args().root)
    print(json.dumps({"ok": not issues, "scope": "static-contracts", "issues": issues},
                     ensure_ascii=False))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
