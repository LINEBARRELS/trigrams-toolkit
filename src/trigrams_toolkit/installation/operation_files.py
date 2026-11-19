"""File ownership and updates for project installation."""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import is_link, relative_path
from trigrams_toolkit.shared.locking import atomic_write


def validate_owned_paths(paths: list[str], commit_path: str) -> None:
    normalized = [os.path.normcase(path).replace("\\", "/") for path in paths]
    marker = os.path.normcase(commit_path).replace("\\", "/")
    require(len(normalized) == len(set(normalized)), "identity_conflict", "Duplicate managed paths.")
    for index, path in enumerate(normalized):
        relative_path(paths[index])
        protected = (".git", ".harness", ".harness-archive", ".project-state", "docs", "skills-lock.json",
                     "agents.md", "claude.md", "product.md", "design.md", "devtech.md", "readme.md")
        require(not any(path.casefold() == root or path.casefold().startswith(root + "/") for root in protected),
                "invalid_reference", f"Managed target overlaps protected project content: {paths[index]}")
        require(path != marker and not marker.startswith(path + "/") and not path.startswith(marker + "/"),
                "invalid_reference", "Package target overlaps the installation record.")
        require(not any(other.startswith(path + "/") or path.startswith(other + "/")
                        for other in normalized[:index]),
                "identity_conflict", f"Managed targets overlap: {paths[index]}")


def target_path(project: Path, relative: str) -> Path:
    relative_path(relative)
    path = project / relative
    require(path.parent.resolve() == path.parent,
            "path_outside_root", f"Target parent is linked: {relative}")
    return path


def blocked_parent(project: Path, path: Path) -> bool:
    return any(parent.exists() and not parent.is_dir()
               for parent in path.parents if parent != project and parent.is_relative_to(project))


def content_digest(raw: bytes) -> str:
    return "sha256:" + sha256(raw).hexdigest()


def file_record(path: str, source: str, raw: bytes) -> dict:
    return {"path": path, "source": source, "kind": "file", "contentDigest": content_digest(raw)}


def matches(path: Path, record: dict | None) -> bool:
    if record is None:
        return not os.path.lexists(path)
    if is_link(path) or not path.is_file():
        return False
    return record.get("contentDigest") == content_digest(path.read_bytes())


def prune_extension_container(project: Path, path: Path) -> None:
    parts = path.relative_to(project).parts
    if len(parts) < 4 or parts[:2] != (".agents", "extensions"):
        return
    boundary, parent = project.joinpath(*parts[:3]), path.parent
    while parent.is_relative_to(boundary):
        if is_link(parent):
            return
        try:
            parent.rmdir()
        except OSError:
            return
        parent = parent.parent


def ordered_changes(changes: list, commit_path: str) -> list:
    return sorted((c for c in changes if c["path"] != commit_path),
                  key=lambda c: (c["action"] != "remove", c["path"]))


def apply_change(project: Path, change: dict, raw: bytes | None) -> None:
    path = target_path(project, change["path"])
    if change["action"] == "remove":
        remove_target(path)
        prune_extension_container(project, path)
        return
    require(raw is not None, "invalid_reference", f"Missing installation bytes: {path}")
    assert raw is not None
    atomic_write(path, raw)


def remove_target(path: Path) -> None:
    if is_link(path) and not path.is_symlink():
        path.rmdir()
    else:
        path.unlink(missing_ok=True)
