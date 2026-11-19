"""The physical working directory is the project root for all public CLIs."""
from pathlib import Path

from trigrams_toolkit.shared.errors import require


def current_project_root(cwd: Path | None = None) -> Path:
    try:
        root = (Path.cwd() if cwd is None else cwd).resolve(strict=True)
    except RuntimeError as error:
        raise OSError(str(error)) from error
    require(root.is_dir(), "invalid_reference", f"Project root must be a directory: {root}")
    return root


__all__ = ["current_project_root"]
