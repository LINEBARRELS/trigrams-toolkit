"""Move explicitly selected project paths out of the active tool layout."""
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined, is_link, relative_path


def archive_project(root: Path, paths: list[str]) -> dict:
    root = root.resolve()
    require(root.is_dir(), "invalid_reference", "Archive root must be an existing project directory.")
    require(bool(paths), "invalid_arguments", "Select the project paths to archive.")
    sources: list[tuple[Path, Path]] = []
    for name in paths:
        relative_path(name)
        relative = Path(name)
        parent = root if relative.parent == Path(".") else confined(root, relative.parent.as_posix())
        source = parent / relative.name
        linked = is_link(source)
        # The selected link itself is the archived object.
        if not linked:
            source = confined(root, name)
        require(all(path.parts[0].casefold() not in (".git", ".harness-archive")
                    for path in (relative, source.relative_to(root))),
                "invalid_reference", "Archive selections cannot include Git or archive storage.")
        require(linked or source.exists(), "invalid_reference", f"Archive source missing: {name}")
        for selected, actual in sources:
            require(not (relative.is_relative_to(selected) or selected.is_relative_to(relative)
                         or source.is_relative_to(actual) or actual.is_relative_to(source)),
                    "invalid_arguments", "Archive selections overlap.")
        sources.append((relative, source))
    destination = root / ".harness-archive"
    require(not is_link(destination) and destination.resolve().is_relative_to(root),
            "path_outside_root", "Archive storage escapes the project.")
    batch = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    destination = destination / batch
    moved = []
    try:
        for relative, source in sources:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)
            moved.append((source, target))
    except OSError:
        for source, target in reversed(moved):
            source.parent.mkdir(parents=True, exist_ok=True)
            target.rename(source)
        raise
    return {"archive": str(destination), "paths": [relative.as_posix() for relative, _ in sources]}
