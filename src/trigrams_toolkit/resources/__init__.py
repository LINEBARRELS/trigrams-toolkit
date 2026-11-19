"""Package-owned contracts; extracted files live until process shutdown."""
from __future__ import annotations

import atexit
from contextlib import ExitStack
from functools import cache
from importlib.resources import as_file, files
from pathlib import Path

_files = ExitStack()
atexit.register(_files.close)


@cache
def resource_path(name: str) -> Path:
    """Keep as_file's context alive for consumers retaining schema paths."""
    return _files.enter_context(as_file(files(__package__).joinpath(name)))


@cache
def schema_paths() -> tuple[Path, ...]:
    return tuple(resource_path(f"{component}/{entry.name}")
                 for component in ("plan", "handbook", "state", "installation", "shared")
                 for entry in sorted(files(__package__).joinpath(component).iterdir(), key=lambda p: p.name)
                 if entry.name.endswith(".schema.json"))


def adapter_files(platform: str) -> dict[str, bytes]:
    targets = {"codex": ".codex/agents", "claude": ".claude/agents", "pi-web": ".pi/agents"}
    root = files(__package__).joinpath("adapters", platform)
    return {f"{targets[platform]}/{entry.name}": entry.read_bytes()
            for entry in root.iterdir() if entry.is_file()}


__all__ = ["resource_path", "schema_paths", "adapter_files"]
