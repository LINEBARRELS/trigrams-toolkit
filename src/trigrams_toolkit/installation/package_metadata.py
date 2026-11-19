"""Read YAML metadata used by toolkit packaging and installation."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys in package metadata."""


def unique_mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict:
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"Expected unique string YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueLoader)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return value


def frontmatter(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"Unclosed YAML frontmatter: {path}") from error
    value = yaml.load("\n".join(lines[1:end]), Loader=UniqueLoader)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping frontmatter: {path}")
    return value
