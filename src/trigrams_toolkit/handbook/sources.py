"""Physical ownership boundaries for complete packages and installed guides."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class ProviderSource:
    """Discover entry paths without reading bodies or computing source hashes."""

    root: Path
    kind: Literal["package", "installed-resource", "installed-skill"]
    resource_paths: tuple[Path, ...]
    install: tuple[dict[str, Any], ...] = ()
