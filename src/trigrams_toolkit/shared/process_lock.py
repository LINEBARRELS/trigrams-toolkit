"""Project State's SQLite ownership protocol; JSON remains the data store."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import time
from typing import Iterator

from .errors import ProtocolError


@dataclass
class ProcessLock:
    state_file: Path
    lock_file: Path
    _connection: sqlite3.Connection | None

    def release(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except sqlite3.Error as error:
                raise _lock_io_error(self.state_file, self.lock_file, error) from error
            self._connection = None


def _lock_io_error(state_file: Path, lock_file: Path, error: Exception) -> ProtocolError:
    return ProtocolError("FILE_WRITE_FAILED", f"Lock IO failed: {lock_file}",
                         details={"stateFile": str(state_file), "lockFile": str(lock_file), "cause": str(error)})


def acquire_process_lock(state_file: Path, timeout_ms: int = 0) -> ProcessLock:
    if type(timeout_ms) is not int or not 0 <= timeout_ms <= 9007199254740991:
        raise ProtocolError("INVALID_INPUT", "Invalid lock timeout")
    lock_file = Path(str(state_file) + ".lock.sqlite")
    connection = None
    deadline = time.monotonic() + timeout_ms / 1000
    try:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(lock_file, timeout=0, isolation_level=None)
        while True:
            try:
                assert connection is not None
                connection.execute("BEGIN IMMEDIATE")
                handle = ProcessLock(state_file, lock_file, connection)
                connection = None
                return handle
            except sqlite3.OperationalError as error:
                if (getattr(error, "sqlite_errorcode", 0) & 0xFF) not in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                    raise
            if time.monotonic() >= deadline:
                raise ProtocolError("FILE_LOCK_TIMEOUT", f"Timed out waiting for lock: {lock_file}",
                                    details={"stateFile": str(state_file), "lockFile": str(lock_file), "timeoutMs": timeout_ms})
            time.sleep(min(0.01, max(0.001, deadline - time.monotonic())))
    except (OSError, sqlite3.Error) as error:
        raise _lock_io_error(state_file, lock_file, error) from error
    finally:
        if connection is not None:
            connection.close()


@contextmanager
def state_lock(state_file: Path) -> Iterator[None]:
    try:
        handle = acquire_process_lock(state_file)
    except ProtocolError as error:
        code = "lock_conflict" if error.code == "FILE_LOCK_TIMEOUT" else "io_error"
        raise ProtocolError(code, str(error), details=error.details) from error
    try:
        yield
    finally:
        try:
            handle.release()
        except ProtocolError as error:
            raise ProtocolError("io_error", f"Cannot release lock: {state_file}", details=error.details) from error
