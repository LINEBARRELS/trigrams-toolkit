"""Source declarations stay read-only and retain guide identities after relocation."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.handbook.source_catalog import source_packages, validate_source_catalog


class SourceCatalogTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".tmp").mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="source-catalog-", dir=ROOT / ".tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for name in ("skills", "extensions", "src/trigrams_toolkit/resources/state"):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "toolkit.json", self.root / "toolkit.json")
        self.manifest = self.root / "skills/resources.json"

    def packages(self):
        return source_packages(self.root, SchemaCatalog(schema_paths()))

    def test_document_changes_need_no_generated_declarations(self):
        declaration = self.manifest.read_bytes()
        before = validate_source_catalog(self.root)
        path = self.root / "skills/how/SKILL.md"
        path.write_bytes(path.read_bytes() + b"\nFixture source update.\n")
        result = validate_source_catalog(self.root)
        self.assertEqual(result, before)
        self.assertEqual(result["sources"], ["core", "game", "toolkit-maintenance"])
        self.assertEqual(self.manifest.read_bytes(), declaration)

    def test_types_are_read_from_one_authority_without_sync(self):
        path = self.root / "src/trigrams_toolkit/resources/state/core-types.json"
        value = json.loads(path.read_text())
        value["artifactTypes"].append("core:fixture")
        path.write_text(json.dumps(value))
        with patch("trigrams_toolkit.handbook.source_catalog.resource_path", return_value=path):
            self.assertIn("core:fixture", self.packages()[0].manifest["artifactTypes"])
        self.assertNotIn("artifactTypes", json.loads(self.manifest.read_text()))

    def test_duplicate_type_authority_is_rejected_without_rewriting(self):
        value = json.loads(self.manifest.read_text())
        value["artifactTypes"] = []
        self.manifest.write_text(json.dumps(value))
        before = self.manifest.read_bytes()
        with self.assertRaisesRegex(ProtocolError, "Core types belong only"):
            self.packages()
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_foreign_type_and_mismatched_provider_are_rejected(self):
        path = self.root / "extensions/game/skills/extension-setup-game/assets/extension.json"
        value = json.loads(path.read_text())
        for field, replacement, message in (("artifactTypes", ["foreign:fixture"], "Foreign provider type"),
                                             ("extension", "foreign", "differs from toolkit")):
            path.write_text(json.dumps({**value, field: replacement}))
            with self.assertRaisesRegex(ProtocolError, message):
                self.packages()

    def test_missing_resource_and_unknown_include_are_rejected(self):
        workbook = self.root / "extensions/game/skills/extension-setup-game/assets/workbooks/gameplay-design/WORKBOOK.md"
        workbook.write_text(workbook.read_text(encoding="utf-8").replace(
            "game:principle:gameplay-rules/define-rule-entities-and-legal-state-domains", "game:principle:missing/entry"), encoding="utf-8")
        with self.assertRaises(ProtocolError):
            validate_source_catalog(self.root)

    def test_manifest_cannot_escape_repository(self):
        path = self.root / "toolkit.json"
        value = json.loads(path.read_text())
        value["core"]["manifest"] = "../outside/resources.json"
        path.write_text(json.dumps(value))
        with self.assertRaises(ProtocolError):
            self.packages()

    def test_linked_manifest_is_rejected_without_changing_its_target(self):
        target = self.manifest.with_name("original.json")
        self.manifest.rename(target)
        try:
            self.manifest.symlink_to(target)
        except OSError as error:
            if getattr(error, "winerror", None) != 1314:
                raise
            self.skipTest("Symbolic link privilege unavailable")
        before = target.read_bytes()
        with self.assertRaisesRegex(ProtocolError, "Linked resource declaration"):
            self.packages()
        self.assertEqual(target.read_bytes(), before)
