"""Read-only, local help rendering shared by the Python public CLIs."""
from __future__ import annotations

import json
import argparse
from pathlib import Path
import textwrap
from typing import Any, Sequence, Iterable

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.serialization import read_json

HELP_WIDTH = 100


def paragraph(value: str) -> str:
    return textwrap.fill(value, width=HELP_WIDTH, break_long_words=False, break_on_hyphens=False)


def help_rows(rows: Sequence[tuple[str, str]]) -> list[str]:
    lines: list[str] = []
    for label, description in rows:
        prefix = "  " + label
        if len(prefix) >= 30:
            lines.append(prefix)
            prefix = " " * 30
        else:
            prefix = prefix.ljust(30)
        lines.extend(textwrap.wrap(description, width=HELP_WIDTH, initial_indent=prefix,
                                   subsequent_indent=" " * 30, break_long_words=False,
                                   break_on_hyphens=False) or [prefix.rstrip()])
    return lines


class HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, width=HELP_WIDTH, max_help_position=30)

    def add_usage(self, usage: str | None, actions: Iterable[argparse.Action],
                  groups: Iterable[argparse._MutuallyExclusiveGroup], prefix: str | None = None) -> None:
        super().add_usage(usage, actions, groups, prefix="Usage: " if prefix is None else prefix)

    def start_section(self, heading: str | None) -> None:
        super().start_section({"options": "Options", "positional arguments": "Arguments"}.get(heading or "", heading or ""))

    def _get_help_string(self, action: argparse.Action) -> str:
        return {"show this help message and exit": "Show help.",
                "show program's version number and exit": "Show toolkit version."}.get(action.help or "", action.help or "")

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        return "\n\n".join(textwrap.fill(part, width, initial_indent=indent, subsequent_indent=indent,
                                        break_long_words=False, break_on_hyphens=False)
                           for part in text.split("\n\n"))


def help_requested(argv: Sequence[str]) -> bool:
    return any(arg in ("-h", "--help") for arg in argv)


def help_selection(argv: Sequence[str], names: Sequence[str], value_options: set[str]) -> tuple[str, bool]:
    """Select a command/group while skipping declared option values."""
    index = next(i for i, arg in enumerate(argv) if arg in ("-h", "--help"))
    tail = list(argv[index + 1:])
    require(tail in ([], ["schema"]), "invalid_arguments", "Help accepts only the optional 'schema' topic.")
    words: list[str] = []
    tokens = iter(argv[:index])
    for arg in tokens:
        if arg.startswith("-"):
            option, equal, _ = arg.partition("=")
            require(option in value_options, "invalid_arguments", f"Unknown option: {option}")
            if not equal:
                next(tokens, None)
            continue
        words.append(arg)
    selected = " ".join(words)
    if selected not in names:
        matches = [name for name in names if selected.startswith(name + " ")]
        if matches:
            selected = max(matches, key=len)
    require(not selected or selected in names or any(name.startswith(selected + " ") for name in names),
            "invalid_arguments", f"Unknown help command: {selected}")
    require(not tail or selected in names, "invalid_arguments", "Select a leaf command for schema help.")
    return selected, bool(tail)


class HelpSchemas:
    def __init__(self, paths: Sequence[Path]) -> None:
        self.documents = {value["$id"]: value for value in map(read_json, paths)}

    def resolve(self, reference: str) -> Any:
        base, _, fragment = reference.partition("#")
        value = self.documents[base]
        for token in fragment.lstrip("/").split("/") if fragment else []:
            value = value[token.replace("~1", "/").replace("~0", "~")]
        return value

    def bundle(self, reference: str) -> dict:
        """Export only reachable definitions, with local refs and cycles preserved."""
        identities: dict[str, str] = {}
        definitions: dict[str, Any] = {}

        def include(target: str) -> str:
            if target not in identities:
                name = f"D{len(identities)}"
                identities[target] = name
                definitions[name] = transform(self.resolve(target), target.split("#")[0])
            return "#/$defs/" + identities[target]

        def transform(value: Any, base: str) -> Any:
            if isinstance(value, list):
                return [transform(item, base) for item in value]
            if not isinstance(value, dict):
                return value
            return {key: include(base + item if item.startswith("#") else item) if key == "$ref"
                    else transform(item, base) for key, item in value.items() if key not in ("$id", "$schema")}

        root = include(reference)
        return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$ref": root, "$defs": definitions}

    def type_label(self, value: dict, base: str) -> str:
        if "$ref" in value:
            ref = base + value["$ref"] if value["$ref"].startswith("#") else value["$ref"]
            return self.type_label(self.resolve(ref), ref.split("#")[0])
        if "const" in value:
            return json.dumps(value["const"], ensure_ascii=False)
        if "enum" in value:
            return "|".join(str(item) if item is not None else "null" for item in value["enum"])
        alternatives = value.get("oneOf", value.get("anyOf"))
        if alternatives is not None:
            return "|".join(dict.fromkeys(self.type_label(item, base) for item in alternatives))
        if "allOf" in value:
            typed = [item for item in value["allOf"] if set(item) & {"$ref", "type", "enum", "const", "oneOf", "anyOf"}]
            return "|".join(dict.fromkeys(self.type_label(item, base) for item in typed)) if typed else "object"
        kind = value.get("type", "object")
        if isinstance(kind, list):
            return "|".join(kind)
        if kind == "array":
            element = self.type_label(value.get("items", {}), base)
            return (f"({element})" if "|" in element else element) + "[]"
        return kind

    def summary(self, reference: str, descriptions: dict[str, str] | None = None) -> str:
        schema = self.resolve(reference)
        base = reference.split("#")[0]
        if "$ref" in schema:
            ref = schema["$ref"]
            return self.summary(base + ref if ref.startswith("#") else ref, descriptions)
        rows = []
        for key, value in schema.get("properties", {}).items():
            label = key + ("*" if key in schema.get("required", []) else "")
            description = (descriptions or {}).get(key, value.get("description", ""))
            rows.append((label + " " + self.type_label(value, base), description))
        return "Input JSON (* required):\n" + "\n".join(help_rows(rows) if rows else ["  {}  No input fields."])


def render_help(tool: str, argv: Sequence[str], commands: Sequence[dict], schemas: HelpSchemas) -> str:
    value_options = {label.split()[0] for item in commands for label, _ in item["options"]
                     if len(label.split()) > 1}
    selected, schema_topic = help_selection(argv, [item["name"] for item in commands], value_options)
    leaf = next((item for item in commands if item["name"] == selected), None)
    if leaf is None:
        prefix = selected + " " if selected else ""
        children = sorted({item["name"][len(prefix):].split()[0] for item in commands
                           if item["name"].startswith(prefix)})
        rows = []
        for name in children:
            path = prefix + name
            child = next((item for item in commands if item["name"] == path), None)
            summary = child["summary"] if child else next(
                item["group_summary"] for item in commands if item["name"].startswith(path + " "))
            rows.append((name, summary))
        options = [("-h, --help", "Show help.")]
        if not selected:
            options.append(("-v, --version", "Show toolkit version."))
        return (f"Usage: {tool}{' ' + selected if selected else ''} COMMAND [options]\n\nCommands:\n"
                + "\n".join(help_rows(rows)) + "\n\nOptions:\n" + "\n".join(help_rows(options))
                + ("\n\nRun commands from the target project root." if not selected else "")
                + f"\n\nUse {tool}{' ' + selected if selected else ''} COMMAND -h for command details.\n")
    if schema_topic:
        require(bool(leaf.get("input")), "invalid_arguments", "This command uses positional arguments, not input JSON.")
        return json.dumps(schemas.bundle(leaf["input"]), ensure_ascii=False, indent=2) + "\n"
    usage = f"Usage: {tool} {selected} {leaf['usage']}"
    lines = [textwrap.fill(usage, width=HELP_WIDTH, subsequent_indent="       ",
                          break_long_words=False, break_on_hyphens=False), "", paragraph(leaf["summary"])]
    if leaf.get("arguments"):
        lines.extend(["", "Arguments:", *help_rows(leaf["arguments"])])
    lines.extend(["", "Options:", *help_rows(leaf["options"]), *help_rows([("-h, --help", "Show help.")])])
    if leaf.get("input"):
        lines.extend(["", leaf.get("input_summary") or schemas.summary(leaf["input"], leaf.get("fields"))])
    lines.extend(["", paragraph("Output: " + leaf["result"] + " Exit 0 on success, 1 on error.")])
    if leaf.get("notes"):
        lines.extend(["", paragraph("Notes: " + leaf["notes"])])
    if leaf.get("input"):
        lines.extend(["", f"Schema: {tool} {selected} --help schema"])
    return "\n".join(lines).rstrip() + "\n"
