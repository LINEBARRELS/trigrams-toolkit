"""Project root discovery and working-directory resolution for public CLIs."""
from __future__ import annotations

from pathlib import Path

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import is_link

HARNESS_MARKER = Path(".agents/harness.json")


def current_project_root(cwd: Path | None = None) -> Path:
    """Resolve the physical working directory as an explicit project root."""
    try:
        root = (Path.cwd() if cwd is None else cwd).resolve(strict=True)
    except RuntimeError as error:
        raise OSError(str(error)) from error
    require(root.is_dir(), "invalid_reference", f"Project root must be a directory: {root}")
    return root


def discover_project_root(cwd: Path | None = None) -> Path:
    """Walk upward from cwd to find the nearest .agents/harness.json, falling back to cwd."""
    start = current_project_root(cwd)
    for candidate in (start, *start.parents):
        marker = candidate / HARNESS_MARKER
        if marker.is_file() and not is_link(marker):
            return candidate
        if candidate.name == ".tmp" or (candidate / ".git").exists():
            break
    return start


__all__ = ["HARNESS_MARKER", "current_project_root", "discover_project_root"]
