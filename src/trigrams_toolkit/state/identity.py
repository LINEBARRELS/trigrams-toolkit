"""Artifact declarations, binary member manifests and byte-preserving edits."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Literal

from trigrams_toolkit.project_context.paths import confined, path_key
from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.state_json import json_bytes, parse_state_json
from .frontmatter import metadata, update_metadata
from .model import Artifact, validate_record


@dataclass(frozen=True)
class Declaration:
    identity: str | None
    title: str
    module_id: str | None
    feature_ids: list[str]
    mode: Literal["frontmatter", "manifest"]


def _id(value: Any, prefix: str) -> str:
    if not isinstance(value, str) or re.fullmatch(prefix + r"_[A-Za-z0-9_-]+", value) is None:
        raise ValueError(f"Invalid {prefix} identity: {value}")
    return value


def declaration(source: str, path: Path, *, ignore_ownership: bool = False) -> Declaration:
    mode: Literal["frontmatter", "manifest"]
    title: Any
    text = source.removeprefix("\ufeff")
    if text.lstrip().startswith("{"):
        fields = parse_state_json(text)
        if not (isinstance(fields, dict) and type(fields.get("schemaVersion")) is int and fields["schemaVersion"] == 1
                and isinstance(fields.get("members"), list) and fields["members"]
                and all(isinstance(p, str) for p in fields["members"])):
            raise ValueError("Expected identity manifest with schemaVersion 1 and nonempty members.")
        identity, title, mode = _id(fields["id"], "artifact") if "id" in fields else None, path.name, "manifest"
    else:
        lines = re.split(r"\r\n|\n|\r", text)
        end = 0
        if lines[0] == "---":
            require("---" in lines[1:], "invalid_reference", f"Unclosed frontmatter: {path}")
            end = lines.index("---", 1)
        fields = metadata("\n".join(lines[1:end])) if end else {}
        heading = next((re.sub(r"^#\s+", "", line) for line in lines[end + 1 if end else 0:] if re.match(r"^#\s+", line)), path.name)
        title = fields.get("title") if fields.get("title") is not None else heading
        identity, mode = _id(fields["artifact-id"], "artifact") if "artifact-id" in fields else None, "frontmatter"
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Expected nonempty document title")
    module, features = None, []
    if not ignore_ownership:
        if "moduleId" in fields:
            module = _id(fields["moduleId"], "module")
        features = fields.get("featureIds", [])
        if not isinstance(features, list):
            raise ValueError("Expected featureIds array")
        features = [_id(value, "feature") for value in features]
    return Declaration(identity, title.strip(), module, features, mode)


def read_declaration(root: Path, path: Path, *, ignore_ownership: bool = False) -> tuple[str, Declaration]:
    source = path.read_bytes().decode("utf-8")
    value = declaration(source, path, ignore_ownership=ignore_ownership)
    if value.mode == "manifest":
        fields = parse_state_json(source, bom=True)
        members = [confined(root, name) for name in fields["members"]]
        require(len({path_key(p) for p in members}) == len(members), "identity_conflict", "Manifest has duplicate members.")
        for member in members:
            member.read_bytes()
    return source, value


def _registered(fields: dict[str, Any], entity: Artifact, key: str) -> bool:
    return (fields.get(key) == entity["id"] and ("moduleId" in fields) == ("moduleId" in entity)
            and fields.get("moduleId") == entity.get("moduleId")
            and fields.get("featureIds", []) == entity["featureIds"])


def with_registration(source: str, entity: Artifact) -> str:
    bom = "\ufeff" if source.startswith("\ufeff") else ""
    body = source[len(bom):]
    if entity["identityMode"] == "manifest":
        value = parse_state_json(body)
        if _registered(value, entity, "id"):
            return source
        value["id"] = entity["id"]
        for key in ("moduleId", "featureIds"):
            if entity.get(key):
                value[key] = entity[key]
            else:
                value.pop(key, None)
        return bom + json_bytes(value).decode("utf-8")
    match = re.search(r"\r\n|\n|\r", body)
    newline = match[0] if match else "\n"
    opening = re.match(r"^---(?:\r\n|\n|\r)", body)
    if opening:
        rest = body[opening.end():]
        closing = re.search(r"(?:^|(?<=[\r\n]))---(?=\r\n|\n|\r|$)", rest)
        require(closing is not None, "invalid_reference", "Unclosed frontmatter.")
        assert closing is not None
        header, tail = rest[:closing.start()], rest[closing.end():]
    else:
        header, tail = "", newline + body
    if _registered(metadata(header), entity, "artifact-id"):
        return source
    updated = update_metadata(header, entity["id"], entity.get("moduleId"), entity["featureIds"])
    require(_registered(metadata(updated), entity, "artifact-id"), "invalid_reference", "Managed identity or ownership conflicts with YAML merges.")
    updated = updated.replace("\n", newline)
    return f"{bom}---{newline}{updated}---{tail}"


def artifact_from_document(root: Path, path: Path, value: Declaration, identity: str, kind: str,
                           module: str | None, features: list[str]) -> Artifact:
    entity: Artifact = {"id": identity, "kind": kind, "title": value.title, "locatorHint": path.relative_to(root).as_posix(),
                        "identityMode": value.mode, "featureIds": features}
    if module is not None:
        entity["moduleId"] = module
    validate_record(entity, "artifact")
    return entity
