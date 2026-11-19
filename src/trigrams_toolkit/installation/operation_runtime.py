"""Install managed materials with one backup and synchronous failure rollback."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Any
import os
import re
import shutil

from trigrams_toolkit.shared.errors import require
from trigrams_toolkit.shared.paths import confined, is_link, path_key
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import canonical, parse_json, read_json
from trigrams_toolkit.shared.locking import atomic_write, locked
from trigrams_toolkit.shared.skill_installations import SkillAgent
from .global_skills import ensure_global_skills
from .operation_files import target_path, matches, apply_change, ordered_changes, remove_target, prune_extension_container
from .installation_sources import INSTALLATION, SNAPSHOT_SCHEMA, installation_record


@dataclass(frozen=True)
class OperationCandidate:
    preview: dict[str, Any]
    files: Mapping[str, bytes]
    commit_path: str
    changed: bool
    dependency_agent: SkillAgent | None


class OperationEngine:
    def __init__(self, project: Path, schemas: SchemaCatalog,
                 checkpoint: Callable[[str], None] | None = None) -> None:
        self.project, self.schemas, self.checkpoint = project.resolve(), schemas, checkpoint

    def _point(self, phase: str) -> None:
        if self.checkpoint is not None:
            self.checkpoint(phase)

    def apply(self, data: dict, request_id: str, expected_revision: int,
              rebuild: Callable[[dict], OperationCandidate]) -> dict:
        self.schemas.validate("urn:harness:installation-cli#/$defs/applyInput", data)
        self.schemas.validate("urn:harness:common#/$defs/revision", expected_revision)
        require(re.fullmatch(r"req_[A-Za-z0-9_-]+", request_id) is not None,
                "invalid_arguments", "Invalid request ID.")
        preview = data["preview"]
        preview_root = Path(preview["projectRoot"])
        require(preview_root.is_absolute() and path_key(preview_root) == path_key(self.project),
                "basis_changed", "Installation preview belongs to a different project. Run apply from its project root.")
        request = {"data": data, "expectedRevision": expected_revision}
        folder = target_path(self.project, ".harness/previous")
        lock = target_path(self.project, ".harness/install.lock")
        require(not is_link(folder) and not is_link(lock), "path_outside_root", "Installation storage cannot be linked.")
        with locked(lock):
            state = installation_record(target_path(self.project, INSTALLATION), self.schemas)
            saved = read_json(folder / "receipt.json") if (folder / "receipt.json").is_file() else None
            if saved is not None and saved["requestId"] == request_id and saved["phase"] == "committed":
                require(saved["request"] == request and saved["result"]["stateRevision"] == state["stateRevision"],
                        "request_conflict", "Request ID already belongs to another installation.")
                self._remove_storage("operations")
                return saved["result"]
            require(saved is None or saved["phase"] != "applying", "recovery_required",
                    "Restore .harness/previous before replacing an interrupted installation.")
            require(expected_revision == preview["baseRevision"] == state["stateRevision"],
                    "revision_conflict", "Expected revision differs from current installation.")
            candidate = rebuild(preview)
            require(preview == candidate.preview, "basis_changed",
                    "Confirmed preview differs from current sources or target state. Refresh the preview.")
            require(not preview["conflicts"], "local_modification",
                    "Installation preview contains conflicts. Review and preserve the indicated paths before retrying.",
                    *preview["conflicts"])
            self._validate(candidate)
            if candidate.dependency_agent is not None:
                ensure_global_skills(candidate.dependency_agent, self.project)
            self._remove_storage("previous")
            folder.mkdir(parents=True)
            changes = [*ordered_changes(preview["changes"], candidate.commit_path),
                       next(c for c in preview["changes"] if c["path"] == candidate.commit_path)]
            for change in changes:
                relative = change["path"]
                if change["before"] is not None:
                    path = target_path(self.project, relative)
                    atomic_write(confined(folder / "backup", relative), path.read_bytes())
            receipt = {"schemaVersion": 1, "requestId": request_id, "request": request,
                       "phase": "applying", "backups": changes, "result": None}
            self.schemas.validate("urn:harness:installation#/$defs/operation", receipt)
            atomic_write(folder / "receipt.json", canonical(receipt))
            attempted = []
            try:
                self._point("backed_up")
                for change in changes:
                    relative = change["path"]
                    path = target_path(self.project, relative)
                    require(matches(path, change["before"]), "local_modification", f"Target changed during install: {path}")
                    attempted.append(change)
                    apply_change(self.project, change, candidate.files.get(relative))
                    self._point("item:" + relative)
                    require(matches(path, change["after"]), "io_error", f"Installation failed: {path}")
                result = {"operationId": preview["operationId"], "phase": "committed",
                          "changed": candidate.changed, "stateRevision": expected_revision + 1}
                receipt.update(phase="committed", result=result)
                self.schemas.validate("urn:harness:installation#/$defs/operation", receipt)
                atomic_write(folder / "receipt.json", canonical(receipt))
            except Exception:
                for change in reversed(attempted):
                    path = target_path(self.project, change["path"])
                    before = change["before"]
                    if before is None:
                        remove_target(path)
                        prune_extension_container(self.project, path)
                    else:
                        restore = {"path": change["path"], "action": "write", "after": before}
                        raw = confined(folder / "backup", change["path"]).read_bytes()
                        apply_change(self.project, restore, raw)
                receipt.update(phase="rolled_back", result=None)
                atomic_write(folder / "receipt.json", canonical(receipt))
                raise
            self._remove_storage("operations")
            return result

    def _remove_storage(self, name: str) -> None:
        path = self.project / ".harness" / name
        require(not is_link(path)
                and path.resolve().parent == (self.project / ".harness").resolve(),
                "path_outside_root", "Installation backup must stay inside .harness.")
        if path.exists():
            shutil.rmtree(path)

    def _validate(self, candidate: OperationCandidate) -> None:
        require(candidate.commit_path == ".agents/harness.json", "invalid_reference",
                "Installation must commit its ownership record.")
        changes = candidate.preview["changes"]
        names = [c["path"] for c in changes]
        require(len(names) == len({os.path.normcase(p) for p in names}) and candidate.commit_path in names,
                "invalid_reference", "Duplicate changes or missing installation record.")
        require(set(candidate.files) == {c["path"] for c in changes if c["action"] == "write"},
                "invalid_reference", "Candidate bytes do not match write changes.")
        for change in changes:
            path = target_path(self.project, change["path"])
            require(matches(path, change["before"]), "local_modification", f"Target ownership changed: {path}")
            for record in (change["before"], change["after"]):
                require(record is None or record["path"] == change["path"],
                        "invalid_reference", "Ownership path differs from change path.")
        self.schemas.validate(SNAPSHOT_SCHEMA, parse_json(candidate.files[candidate.commit_path]))
