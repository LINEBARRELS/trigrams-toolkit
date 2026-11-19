"""Independent package fixtures for read-only guide tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def temporary_directory(prefix: str) -> tempfile.TemporaryDirectory:
    directory = ROOT / ".tmp"
    directory.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(prefix=prefix, dir=directory)


class RuntimeCase(unittest.TestCase):
    def setUp(self) -> None:
        temporary = temporary_directory(prefix="handbook-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.package = self.root / "core"
        self.package.mkdir()
        self.schemas = SchemaCatalog(schema_paths())
        self.manifest = {"schemaVersion": 1, "source": "core", "version": "1.0.0",
                         "resourceRoots": ["guides", "principles", "skills"], "install": []}
        self.guide("research", "workbook", {"includes": ["core:principle:scale/limits"]})
        self.guide("programming", "workbook")
        self.guide("scale/limits", "principle")
        (self.package / "skills/example").mkdir(parents=True)
        (self.package / "skills/example/SKILL.md").write_text("No resource metadata.\n", encoding="utf-8")
        self.save_manifest()
        self.refresh()

    def guide(self, name: str, kind: str, fields: dict | None = None) -> Path:
        path = self.package / ("principles" if kind == "principle" else "guides") / name / (kind.upper() + ".md")
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"description": "Use " + name + ".", **({"name": name} if kind == "workbook" else {}), **(fields or {})}
        path.write_text("---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n\n# " + name + "\n", encoding="utf-8")
        return path

    def save_manifest(self) -> None:

        write_json(self.package / "resources.json", self.manifest)

    def install_core(self) -> tuple[Path, dict[str, str]]:
        profile = self.root / "profile"
        root = profile / ".agents/skills"
        for name, directory, source in (("principles", "principles", "principles"),
                                         ("workbook", "workbooks", "guides")):
            shutil.copytree(self.package / source, root / name / directory)
            (root / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Core fixture\n---\n", encoding="utf-8")
        return root, {"USERPROFILE" if os.name == "nt" else "HOME": str(profile)}

    def refresh(self) -> None:
        self.catalog = GuideCatalog.discover([self.package], self.project, self.schemas)

    def assert_code(self, code: str, callback) -> ProtocolError:
        with self.assertRaises(ProtocolError) as failure:
            callback()
        self.assertEqual(failure.exception.code, code, str(failure.exception))
        return failure.exception
