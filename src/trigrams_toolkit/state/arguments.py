"""The eight-command argument contract, independent of project state."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence
from trigrams_toolkit.shared.errors import require

SPECIFIC = {
    "register module": ("--id",),
    "register feature": ("--id", "--module"), "register artifact": ("--kind", "--module", "--feature"),
    "locate": (), "list": ("--kind",), "related": ("--direction",), "relate": ("--remove",), "validate": (),
}
ARITY = dict(zip(SPECIFIC, (1, 1, 1, 1, 0, 1, 3, 0)))
COMMAND_NAMES = tuple(SPECIFIC)


@dataclass(frozen=True)
class Invocation:
    command: str = ""
    args: tuple[str, ...] = ()
    options: dict[str, list[str]] = field(default_factory=dict)
    kind: Literal["command", "help", "version"] = "command"

    def option(self, flag: str) -> str | None:
        values = self.options.get(flag)
        return values[0] if values else None


def parse_arguments(argv: Sequence[str]) -> Invocation:
    words: list[str] = []
    options: dict[str, list[str]] = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        index += 1
        require(bool(token) and "\0" not in token, "invalid_arguments", "Empty or invalid argument.")
        if not token.startswith("-"):
            words.append(token)
            continue
        flag, equal, value = token.partition("=")
        require(flag == "--feature" or flag not in options, "invalid_arguments", f"Duplicate option: {flag}")
        toggle = flag in ("--help", "-h", "--version", "-v", "--remove")
        if toggle:
            value = "true"
        elif not equal:
            value = argv[index] if index < len(argv) else ""
            index += 1
        require(bool(value) and not value.startswith("--") and not (toggle and equal), "invalid_arguments", f"Expected a value for {flag}.")
        options.setdefault(flag, []).append(value)
    if "--version" in options or "-v" in options:
        require(not words and len(options) == 1, "invalid_arguments", "--version is a root option.")
        return Invocation(kind="version")
    grouped = bool(words) and words[0] == "register"
    count = 2 if grouped else 1
    name = " ".join(words[:count])
    allowed = {"-h", "--help", *SPECIFIC.get(name, ())}
    for flag in options:
        require(flag in allowed, "invalid_arguments", f"Unknown option: {flag}")
    if "--help" in options or "-h" in options or not argv or (grouped and len(words) == 1):
        require(name in SPECIFIC or name in ("", "register"), "invalid_arguments", f"Unknown command: {name}")
        return Invocation(command=name, kind="help")
    require(name in SPECIFIC, "invalid_arguments", f"Unknown command: {name}. Use project-state --help.")
    args = tuple(words[count:])
    require(len(args) == ARITY[name], "invalid_arguments", f"Expected {ARITY[name]} argument(s) for {name}. Use --help.")
    require("--direction" not in options or options["--direction"][0] in ("both", "incoming", "outgoing"),
            "invalid_arguments", "direction must be both, incoming or outgoing.")
    require("--feature" not in options or "--module" in options, "invalid_arguments", "--feature requires --module MODULE_ID in the same command.")
    return Invocation(name, args, options)
