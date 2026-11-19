"""Native physical paths, including nonexistent final components."""
from __future__ import annotations

import errno
import os
from pathlib import Path

from trigrams_toolkit.shared.errors import require


def physical_path(value: Path) -> Path:
    try:
        return value.resolve()
    except RuntimeError as error:
        raise OSError(errno.ELOOP, str(error), str(value)) from error


def path_key(value: Path | str) -> str:
    path = str(value)
    if os.name == "nt":
        if path.startswith("\\\\?\\UNC\\"):
            path = "\\\\" + path[8:]
        elif path.startswith("\\\\?\\"):
            path = path[4:]
    return os.path.normcase(os.path.normpath(path))


def within(root: Path, target: Path) -> bool:
    return Path(path_key(target)).is_relative_to(Path(path_key(root)))


def confined(root: Path, value: Path | str) -> Path:
    require(bool(str(value)) and "\0" not in str(value), "invalid_reference", "Expected a project path.")
    target = physical_path(root / value)
    require(within(root.resolve(strict=True), target), "path_outside_root", f"Real path escapes project: {value}")
    return target


def resolve_project_path(root: Path, value: Path | str, *, cwd: Path | None = None, confine: bool = True) -> Path:
    """Resolve a CLI path argument against root, falling back to cwd for existing relative paths."""
    require(bool(str(value)) and "\0" not in str(value), "invalid_reference", "Expected a project path.")
    candidate = Path(value)
    if candidate.is_absolute():
        return confined(root, candidate) if confine else candidate
    target = root / candidate
    if cwd is not None:
        cwd_resolved = physical_path(cwd)
        if path_key(cwd_resolved) != path_key(physical_path(root)):
            cwd_target = cwd_resolved / candidate
            if not target.exists() and cwd_target.exists():
                target = cwd_target
    return confined(root, target) if confine else target
