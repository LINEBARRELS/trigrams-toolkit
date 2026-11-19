"""Shared atomic file publication, independent of Plan state and locking."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import time

from .errors import require


def atomic_write(path: Path, raw: bytes, *, immutable: bool = False) -> None:
    """Publish one file using a same-directory temporary and finite retries.

    Preserve atomic publication invariants: fsync the file, replace (or
    publish immutable), fsync the parent on POSIX, and remove the temporary.
    OSError survives; immutable conflicts use ProtocolError(basis_changed).
    Multi-file installation transactions own their rollback policy.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if immutable and path.exists():
        require(path.read_bytes() == raw, "basis_changed", f"Immutable record differs: {path}")
        return
    descriptor, name = tempfile.mkstemp(prefix=".harness-", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if immutable:
            _publish_new(temporary, path, raw)
        else:
            _replace(temporary, path)
        if os.name != "nt":
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def _replace(temporary: Path, path: Path) -> None:
    """A Windows reader may briefly deny replacement; persistent errors survive."""
    for attempt in range(6):
        try:
            os.replace(temporary, path)
            return
        except PermissionError as error:
            if os.name != "nt" or getattr(error, "winerror", None) not in (5, 32) or attempt == 5:
                raise
            time.sleep(0.02 * 2 ** attempt)


def _publish_new(temporary: Path, path: Path, raw: bytes) -> None:
    try:
        if os.name == "nt":
            os.rename(temporary, path)
        else:
            os.link(temporary, path)
    except FileExistsError:
        require(path.read_bytes() == raw, "basis_changed", f"Immutable record differs: {path}")


