"""Read guide front matter without opening accompanying documents."""
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Literal

import yaml
from yaml.tokens import AliasToken, AnchorToken, TagToken

from trigrams_toolkit.shared.errors import ProtocolError, require
from .package import yaml_mapping
from trigrams_toolkit.shared.schema import SchemaCatalog


def _read_header(stream: BinaryIO) -> dict:
    first = stream.readline().removeprefix(b"\xef\xbb\xbf").rstrip(b"\r\n")
    require(first == b"---", "invalid_schema", "Add a YAML header starting with ---.")
    lines = []
    for line in stream:
        if line.rstrip(b"\r\n") == b"---":
            break
        lines.append(line)
    else:
        raise ProtocolError("invalid_schema", "Close the YAML header with ---.")
    text = b"".join(lines).decode("utf-8")
    require(not any(isinstance(token, (AliasToken, AnchorToken, TagToken)) for token in yaml.scan(text)),
            "invalid_schema", "Guide headers cannot use YAML anchors, aliases or custom tags.")
    value = yaml_mapping(text)
    return {key: item.strip() if isinstance(item, str) else item for key, item in value.items()}


def guide_header(path: Path, schemas: SchemaCatalog, *,
                 kind: Literal["workbook", "principle"] | None = None) -> dict:
    """Validate the explicit draft kind or derive the kind from an entry filename."""
    try:
        with path.open("rb") as stream:
            value = _read_header(stream)
        principle = kind == "principle" if kind is not None else path.name == "PRINCIPLE.md"
        definition = "principleHeader" if principle else "header"
        schemas.validate(f"urn:harness:guides#/$defs/{definition}", value)
        return value
    except (ProtocolError, yaml.YAMLError, UnicodeError) as error:
        raise ProtocolError("invalid_schema", f"{path}: {error}", conflicts=(str(path),)) from error
