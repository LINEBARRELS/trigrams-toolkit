"""Import an approved principle draft into the authoritative project library."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from trigrams_toolkit.shared.errors import ProtocolError, require
from trigrams_toolkit.shared.files import atomic_write
from .guide_headers import guide_header
from .guides import GuideCatalog
from .location import sources_for_project
from trigrams_toolkit.shared.paths import confined, path_key
from .project_resources import prepare_project_resources
from trigrams_toolkit.shared.schema import SchemaCatalog


@dataclass(frozen=True)
class PrincipleImportResult:
    resource_id: str
    entry_path: Path
    operation: Literal["created", "updated"]

    def as_dict(self) -> dict:
        return {"ok": True, "resourceId": self.resource_id,
                "entryPath": str(self.entry_path), "operation": self.operation}


def import_principle(project: Path, source: Path, scope: str, name: str,
                     schemas: SchemaCatalog, *, replace: bool = False, agent: str | None = None) -> PrincipleImportResult:
    """Preflight, publish declaration/body, then confirm the real discovery chain.

    Source bytes survive unchanged. Write/discovery failures retain partial files
    and report their confirmed state through ProtocolError.current.
    """
    for label, token in (("scope", scope), ("name", name)):
        try:
            schemas.validate("urn:harness:common#/$defs/token", token)
        except ProtocolError as error:
            raise ProtocolError("invalid_arguments", f"Invalid principle {label}: {token}") from error
    try:
        project, source = project.resolve(), source.resolve()
        entry = confined(project, f"docs/knowledge/principles/{scope}/{name}/PRINCIPLE.md")
        require(source.is_file(), "invalid_reference", f"Draft file is unavailable: {source}", str(source))
        exists = entry.exists()
        require(not exists or not source.samefile(entry), "invalid_arguments",
                "The draft and formal entry must be different files.", str(source))
        raw = _draft_bytes(source, schemas)
        if replace:
            require(entry.is_file(), "invalid_reference", f"Replacement target is unavailable: {entry}", str(entry))
        else:
            require(not exists, "resource_conflict", f"Principle already exists; use --replace: {entry}", str(entry))
        declaration = prepare_project_resources(project, ["knowledge/principles"], schemas)
    except OSError as error:
        raise ProtocolError("io_error", f"Cannot prepare principle import: {error}") from error

    identity = f"project:principle:{scope}/{name}"
    current = {"packagePath": str(declaration.path), "packageWritten": False,
               "entryPath": str(entry), "entryWritten": False}
    try:
        current["packageWritten"] = declaration.write()
        try:
            atomic_write(entry, raw)
        except OSError:
            current["entryWritten"] = _written(entry, raw)
            raise
        current["entryWritten"] = True
        packages = sources_for_project(project, schemas, agent)
        catalog = GuideCatalog.discover(list(packages.values()), project, schemas)
        require(path_key(catalog.resolve(identity).path) == path_key(entry), "identity_conflict",
                f"Imported identity resolves to another entry: {identity}")
    except ProtocolError as error:
        raise ProtocolError(error.code, str(error), conflicts=error.conflicts,
                            current={**current, **(error.current or {})}) from error
    except OSError as error:
        raise ProtocolError("io_error", f"Cannot complete principle import: {error}", current=current) from error
    return PrincipleImportResult(identity, entry, "updated" if replace else "created")


def _draft_bytes(source: Path, schemas: SchemaCatalog) -> bytes:
    """Validate principle metadata and a nonblank UTF-8 body without rewriting."""
    guide_header(source, schemas, kind="principle")
    raw = source.read_bytes()
    try:
        lines = raw.decode("utf-8-sig").splitlines()
    except UnicodeError as error:
        raise ProtocolError("invalid_schema", f"Draft must be UTF-8: {source}", conflicts=(str(source),)) from error
    closing = next(index for index, line in enumerate(lines[1:], 1) if line == "---")
    require(bool("\n".join(lines[closing + 1:]).strip()), "invalid_schema",
            f"Principle draft body is empty: {source}", str(source))
    return raw


def _written(path: Path, raw: bytes) -> bool | None:
    """Confirm a failed publication's actual target; unreadable results stay unknown."""
    try:
        return path.read_bytes() == raw
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return None
