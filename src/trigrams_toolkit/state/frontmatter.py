"""Validate legacy YAML metadata and edit only managed nodes in the header."""
from __future__ import annotations

from io import StringIO
import re
from typing import Iterator

from ruamel.yaml import YAML
from ruamel.yaml.anchor import Anchor
from ruamel.yaml.error import YAMLError
from ruamel.yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode
from ruamel.yaml.resolver import VersionedResolver
from ruamel.yaml.tag import Tag

_YAML_TAG = "tag:yaml.org,2002:"
_STR = _YAML_TAG + "str"
_NULL = _YAML_TAG + "null"
_MERGE = _YAML_TAG + "merge"
_MAP = _YAML_TAG + "map"
_SEQ = _YAML_TAG + "seq"
_MANAGED = ("artifact-id", "title", "moduleId", "featureIds")

# YAML 1.1's legacy JS resolver also accepts leading zeroes in sexagesimal
# and decimal numbers and single digits in timestamps.
_NUMBER = re.compile(
    r"[-+]?(?:[0-9][0-9_]*(?::[0-5]?[0-9])*|0b[01_]+|0x[0-9a-fA-F_]+)"
)
_FLOAT = re.compile(
    r"[-+]?(?:[0-9][0-9_]*)?(?:\.[0-9_]*)?[eE][-+]?[0-9]+"
    r"|[-+]?(?:[0-9][0-9_]*(?::[0-5]?[0-9])*)?\.[0-9_]*"
    r"|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN)"
)
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:(?:[tT]|[ \t]+)"
    r"[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}(?:\.[0-9]+)?"
    r"(?:[ \t]*(?:Z|[-+][012]?[0-9](?::[0-9]{2})?))?)?"
)
_RECLASSIFIED = {_YAML_TAG + name for name in ("int", "float", "timestamp", "value", "yaml")}
_SCALAR_TAGS = {_YAML_TAG + name for name in ("str", "null", "merge", "bool", "int", "float", "binary", "timestamp")}


class _LegacyResolver(VersionedResolver):
    def resolve(self, kind: type[Node], value: str, implicit: tuple[bool, ...]) -> Tag:
        tag = super().resolve(kind, value, implicit)
        if kind is ScalarNode and implicit[0] and self.processing_version == (1, 1):
            for pattern, name in ((_NUMBER, "int"), (_FLOAT, "float"), (_TIMESTAMP, "timestamp")):
                if pattern.fullmatch(value):
                    return Tag(suffix=_YAML_TAG + name)
            if str(tag) in _RECLASSIFIED:
                return self.DEFAULT_SCALAR_TAG
        return tag


def _nodes(root: Node) -> Iterator[Node]:
    pending = [root]
    seen: set[Node] = set()
    while pending:
        node = pending.pop()
        if node in seen:
            continue
        seen.add(node)
        yield node
        if isinstance(node, MappingNode):
            pending.extend(child for pair in node.value for child in pair)
        elif isinstance(node, SequenceNode):
            pending.extend(node.value)


def _mapping_fields(node: MappingNode, active: frozenset[Node] = frozenset()) -> dict[str, Node]:
    if node in active:
        raise ValueError("Recursive YAML merge")
    fields: dict[str, Node] = {}
    merged = False
    for key, value in node.value:
        entries: list[tuple[str, Node]]
        if key.tag == _MERGE:
            if merged:
                raise ValueError("Expected one YAML merge key per mapping")
            merged = True
            sources = value.value if isinstance(value, SequenceNode) else [value]
            entries = []
            for source in sources:
                if not isinstance(source, MappingNode):
                    raise ValueError("Expected YAML maps in merge")
                entries.extend(_mapping_fields(source, active | {node}).items())
        else:
            if not isinstance(key, ScalarNode) or key.tag != _STR:
                raise ValueError("Expected string YAML key")
            entries = [(key.value, value)]
        for name, child in entries:
            if name in fields:
                raise ValueError(f"Expected unique string YAML key: {name}")
            fields[name] = child
    return fields


def _document(source: str) -> tuple[YAML, MappingNode | None, dict[str, Node]]:
    parser = YAML(typ="rt")
    parser.Resolver = _LegacyResolver
    parser.version = (1, 1)
    try:
        node = parser.compose(source)
    except YAMLError as error:
        raise ValueError(str(error)) from error
    if node is None:
        return parser, None, {}
    if not isinstance(node, MappingNode) or node.tag != _MAP:
        raise ValueError("Expected mapping frontmatter")
    fields = _mapping_fields(node)
    for child in _nodes(node):
        if isinstance(child, MappingNode) and child.tag in (_MAP, _YAML_TAG + "set"):
            if child is not node:
                _mapping_fields(child)
        elif isinstance(child, SequenceNode) and child.tag in (_SEQ, _YAML_TAG + "pairs", _YAML_TAG + "omap"):
            continue
        elif not isinstance(child, ScalarNode) or child.tag not in _SCALAR_TAGS:
            raise ValueError(f"Unsupported YAML tag: {child.tag}")
    return parser, node, fields


def _managed_value(node: Node) -> str | list[str] | Node | None:
    if node.tag == _NULL:
        return None
    if isinstance(node, ScalarNode) and node.tag == _STR:
        return node.value
    if isinstance(node, SequenceNode) and node.tag == _SEQ and all(
        isinstance(child, ScalarNode) and child.tag == _STR for child in node.value
    ):
        return [child.value for child in node.value]
    return node


def metadata(source: str) -> dict[str, str | list[str] | Node | None]:
    """Read the managed values without constructing unmatched YAML scalars or aliases."""
    _, _, fields = _document(source)
    return {key: _managed_value(fields[key]) for key in _MANAGED if key in fields}


def update_metadata(source: str, identity: str, module: str | None, features: list[str]) -> str:
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    parser, node, _ = _document(source)
    parser.width = 1000000
    preamble = source if node is None else ""
    if node is None:
        node = MappingNode(_MAP, [])
    updates: dict[str, Node | None] = {
        "artifact-id": ScalarNode(_STR, identity),
        "moduleId": ScalarNode(_STR, module) if module is not None else None,
        "featureIds": SequenceNode(_SEQ, [ScalarNode(_STR, item) for item in features]) if features else None,
    }
    updated: list[tuple[Node, Node]] = []
    for key, value in node.value:
        if not isinstance(key, ScalarNode) or key.tag != _STR or key.value not in updates:
            updated.append((key, value))
            continue
        replacement = updates.pop(key.value)
        if replacement is not None:
            replacement.comment = value.comment
            if isinstance(value, ScalarNode) and isinstance(replacement, ScalarNode):
                replacement.style = value.style
            updated.append((key, replacement))
    updated.extend((ScalarNode(_STR, key), value) for key, value in updates.items() if value is not None)
    node.value = updated
    for child in _nodes(node):
        if isinstance(child.anchor, str):
            name = child.anchor
            child.anchor = Anchor()
            child.anchor.value = name
            child.anchor.always_dump = True
    output = StringIO()
    try:
        parser.serialize(node, output)
    except YAMLError as error:
        raise ValueError(str(error)) from error
    rendered = output.getvalue().removeprefix("%YAML 1.1\n---")
    return preamble + rendered.removeprefix("\n").removeprefix(" ")
