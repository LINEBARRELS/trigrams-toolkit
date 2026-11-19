"""Apply installation ownership changes and retain only the latest backup."""
from pathlib import Path
from typing import Callable

from trigrams_toolkit.shared.schema import SchemaCatalog
from .installation_candidate import build_candidate
from .operation_runtime import OperationEngine


def apply_installation(project: Path, data: dict, schemas: SchemaCatalog, request_id: str, expected_revision: int,
                       *, checkpoint: Callable[[str], None] | None = None) -> dict:
    engine = OperationEngine(project, schemas, checkpoint)
    return engine.apply(data, request_id, expected_revision,
                        lambda preview: build_candidate(project, preview["parameters"], schemas, preview["operationId"]))
