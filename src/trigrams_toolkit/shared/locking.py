"""Durable atomic replacement and short-lived OS file ownership."""

from __future__ import annotations

from contextlib import contextmanager
import errno
import os
import sys
from pathlib import Path
import time
from typing import Iterator

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.files import atomic_write


def _lock(handle, unlock: bool = False) -> None:
    handle.seek(0)
    if sys.platform == "win32":
        import msvcrt
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK if unlock else msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN if unlock else fcntl.LOCK_EX | fcntl.LOCK_NB)


@contextmanager
def locked(path: Path, *, timeout: float = 5.0) -> Iterator[None]:
    """The file remains; the OS releases ownership on process death."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if path.stat().st_size == 0:
            handle.write(b"\0")
            handle.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                _lock(handle)
                break
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if time.monotonic() >= deadline:
                    raise ProtocolError("lock_busy", f"Another process holds {path}") from error
                time.sleep(0.01)
        try:
            yield
        finally:
            _lock(handle, unlock=True)
