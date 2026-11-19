"""Identity scanning skips linked descendants and resolves only selected bodies."""
from __future__ import annotations

from pathlib import Path
import re

from trigrams_toolkit.project_context.paths import confined, path_key
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.paths import is_link
from .identity import declaration
from .model import Artifact, RegistryState

_EXCLUDED = {".git", ".cas", ".requests", "node_modules", "__pycache__", ".project-state"}


def identity_candidates(project_root: Path, state: RegistryState, extra: tuple[Path, ...] = ()) -> dict[str, set[Path]]:
    found: dict[str, set[Path]] = {}
    visited: set[str] = set()
    docs = confined(project_root, "docs")
    archive = docs / "archives"

    def scan(path: Path) -> None:
        if not path.exists() or path_key(path) in visited:
            return
        visited.add(path_key(path))
        if path.is_dir():
            for entry in sorted(path.iterdir()):
                if entry != archive and entry.name not in _EXCLUDED and not is_link(entry):
                    scan(entry)
            return
        if not path.is_file():
            return
        raw = path.read_bytes()
        start = raw.decode("utf-8", errors="replace").removeprefix("\ufeff").lstrip()
        if not start.startswith(("---", "{")):
            return
        try:
            identity = declaration(raw.decode("utf-8-sig"), path, ignore_ownership=True).identity
        except (ValueError, ProtocolError):
            if start.startswith("---") and re.search(r"^artifact-id:", start, re.MULTILINE):
                raise
            return
        if identity:
            found.setdefault(identity, set()).add(path)

    scan(docs)
    hints = [artifact["locatorHint"] for artifact in state["artifacts"]]
    paths: tuple[Path | str, ...] = ("plans", *hints, *extra)
    for path in paths:
        scan(confined(project_root, path))
    return found


def artifact_location(project_root: Path, state: RegistryState, artifact: Artifact) -> Path:
    candidates = sorted(identity_candidates(project_root, state).get(artifact["id"], set()))
    if len(candidates) != 1:
        raise ProtocolError("identity_conflict" if candidates else "invalid_reference",
                            f"Expected one body declaring {artifact['id']}.", details=[str(p) for p in candidates] or None)
    return candidates[0]
