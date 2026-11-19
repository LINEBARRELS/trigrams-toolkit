"""Real filesystem boundaries shared by resource and project references."""

from __future__ import annotations

import os
import re
import stat
import sys
from pathlib import Path, PurePath, PureWindowsPath
from typing import Callable, Iterator

from .errors import ProtocolError, require

_INVALID = re.compile(r'[\\:*?"<>|\x00-\x1f]')
_DEVICE = re.compile(r"^(?:CON|PRN|AUX|NUL|CLOCK\$|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])$", re.I)


def relative_path(value: str) -> None:
    require(isinstance(value, str) and bool(value), "path_outside_root", "Expected a relative path.")
    parts = value.split("/")
    require(not _INVALID.search(value), "path_outside_root", f"Invalid path: {value}")
    for part in parts:
        require(part not in ("", ".", "..") and not part.endswith((".", " ")),
                "path_outside_root", f"Invalid path component: {value}")
        require(not _DEVICE.match(part.split(".")[0]), "path_outside_root", f"Device alias: {value}")


def _comparison_path(path: PurePath) -> PurePath:
    """@to-plan P05/S01 Normalize known Windows prefixes only for component comparison."""
    if isinstance(path, PureWindowsPath):
        value = str(path)
        if value[:8].casefold() == "\\\\?\\unc\\":
            return PureWindowsPath("\\\\" + value[8:])
        if value.startswith("\\\\?\\") and re.match(r"^[A-Za-z]:\\", value[4:]):
            return PureWindowsPath(value[4:])
    return path


def confined(root: Path, relative: str) -> Path:
    relative_path(relative)
    try:
        boundary = root.resolve()
        path = (boundary / relative).resolve()
    except (OSError, RuntimeError) as error:
        raise ProtocolError("path_outside_root", f"Cannot resolve path: {relative}") from error
    require(_comparison_path(path).is_relative_to(_comparison_path(boundary)), "path_outside_root",
            f"Resolved path escapes root: {relative}", str(path))
    return path


def inside(root: Path, path: Path) -> Path:
    boundary, resolved = root.resolve(), path.resolve()
    boundary_key, resolved_key = _comparison_path(boundary), _comparison_path(resolved)
    require(resolved_key.is_relative_to(boundary_key), "path_outside_root",
            f"Path escapes root: {path}", str(path))
    relative_path(resolved_key.relative_to(boundary_key).as_posix())
    return resolved


def path_key(path: Path) -> str:
    return os.path.normcase(str(_comparison_path(path.resolve())))


def is_link(path: Path) -> bool:
    """Detect symlinks and Windows junctions on Python 3.11 as well."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return (stat.S_ISLNK(info.st_mode) or
            (sys.platform == "win32" and info.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT))


def files_under(root: Path, start: Path, *, exclude: Callable[[str], bool] | None = None) -> Iterator[Path]:
    """Follow internal directory links once; reject cycles and outside targets."""
    def visit(path: Path, ancestors: frozenset[str]) -> Iterator[Path]:
        if exclude is not None and exclude(path.relative_to(root).as_posix()):
            return
        resolved = inside(root, path)
        key = path_key(resolved)
        require(key not in ancestors, "invalid_reference", f"Directory link cycle: {path}")
        if resolved.is_file():
            yield path
            return
        require(resolved.is_dir(), "invalid_reference", f"Source path is unavailable: {path}")
        for child in sorted(path.iterdir()):
            yield from visit(child, ancestors | {key})

    yield from visit(start, frozenset())
