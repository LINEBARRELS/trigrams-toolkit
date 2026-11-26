"""Project resource declarations preserve sources and report publication failures."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from support import RuntimeCase, write_json
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.handbook.package import package_manifest
from trigrams_toolkit.handbook.project_resources import prepare_project_resources


class ProjectResourceTests(RuntimeCase):
    def setUp(self) -> None:
        super().setUp()
        self.docs = self.project / "docs"
        self.path = self.docs / "resources.json"

    def prepare(self, *roots: str):
        return prepare_project_resources(self.project, roots, self.schemas)

    def test_missing_declaration_is_prepared_without_writes_then_created(self) -> None:
        prepared = self.prepare("knowledge/principles", "workbooks", "workbooks")
        self.assertFalse(self.docs.exists())
        self.assertEqual(prepared.path, self.path)
        self.assertTrue(prepared.changed)
        self.assertTrue(prepared.write())
        self.assertEqual(package_manifest(self.docs, self.schemas), {
            "schemaVersion": 1, "source": "project", "version": "1.0.0",
            "resourceRoots": ["knowledge/principles", "workbooks"], "install": []})

    def test_existing_fields_survive_and_repeat_requests_do_not_rewrite(self) -> None:
        manifest = {"schemaVersion": 1, "source": "project", "version": "2.3.4-beta",
                    "resourceRoots": ["workbooks"],
                    "install": [{"source": "skills/local", "target": ".agents/skills/local"}],
                    "artifactTypes": ["project:feature"]}
        write_json(self.path, manifest)
        prepared = self.prepare("knowledge/principles", "knowledge/principles")
        self.assertEqual(json.loads(self.path.read_bytes()), manifest)
        self.assertTrue(prepared.write())
        expected = {**manifest, "resourceRoots": ["workbooks", "knowledge/principles"]}
        self.assertEqual(package_manifest(self.docs, self.schemas), expected)
        before = self.path.read_bytes(), self.path.stat().st_mtime_ns
        repeated = self.prepare("workbooks", "knowledge/principles")
        self.assertFalse(repeated.changed)
        self.assertFalse(repeated.write())
        self.assertEqual((self.path.read_bytes(), self.path.stat().st_mtime_ns), before)

    def test_parent_coverage_preserves_original_bytes_and_discovery(self) -> None:
        write_json(self.path, {"schemaVersion": 1, "source": "project", "version": "1.2.3",
                               "resourceRoots": ["knowledge"], "install": []})
        entry = self.docs / "knowledge/principles/design/evidence/PRINCIPLE.md"
        entry.parent.mkdir(parents=True)
        entry.write_text("---\ndescription: Use evidence.\n---\n\n# Evidence\n", encoding="utf-8")
        before = self.path.read_bytes(), self.path.stat().st_mtime_ns
        prepared = self.prepare("knowledge/principles")
        self.assertFalse(prepared.changed)
        self.assertFalse(prepared.write())
        self.assertEqual((self.path.read_bytes(), self.path.stat().st_mtime_ns), before)
        catalog = GuideCatalog.discover([self.docs], self.project, self.schemas)
        self.assertEqual(catalog.validate()["resourceIds"], ["project:principle:design/evidence"])

    def test_requested_parent_preserves_existing_child_declaration_on_conflict(self) -> None:
        write_json(self.path, {"schemaVersion": 1, "source": "project", "version": "1.0.0",
                               "resourceRoots": ["knowledge/principles/design"], "install": []})
        before = self.path.read_bytes()
        self.assert_code("resource_conflict", lambda: self.prepare("knowledge/principles"))
        self.assertEqual(self.path.read_bytes(), before)

    def test_other_resource_root_uses_the_same_module(self) -> None:
        self.assertTrue(self.prepare("workbooks").write())
        entry = self.docs / "workbooks/research/WORKBOOK.md"
        entry.parent.mkdir(parents=True)
        entry.write_text("---\nname: Research\ndescription: Follow evidence.\n---\n\n# Research\n", encoding="utf-8")
        catalog = GuideCatalog.discover([self.docs], self.project, self.schemas)
        self.assertEqual(catalog.load(["project:workbook:research"])["selected"], "project:workbook:research")

    def test_existing_overlapping_roots_fail_before_publication(self) -> None:
        write_json(self.path, {"schemaVersion": 1, "source": "project", "version": "1.0.0",
                               "resourceRoots": ["knowledge", "knowledge/principles"], "install": []})
        before = self.path.read_bytes()
        self.assert_code("resource_conflict", lambda: self.prepare("workbooks"))
        self.assertEqual(self.path.read_bytes(), before)

    def test_bad_declarations_are_preserved_before_any_write(self) -> None:
        valid = {"schemaVersion": 1, "source": "project", "version": "1.0.0",
                 "resourceRoots": [], "install": []}
        cases = [(b"broken json", "invalid_json"),
                 (b'{"source":"project","source":"project"}', "invalid_json"),
                 (json.dumps({**valid, "version": "broken"}).encode(), "invalid_schema"),
                 (json.dumps({**valid, "source": "other"}).encode(), "identity_conflict")]
        self.docs.mkdir()
        for raw, code in cases:
            with self.subTest(code=code, raw=raw):
                self.path.write_bytes(raw)
                self.assert_code(code, lambda: self.prepare("knowledge/principles"))
                self.assertEqual(self.path.read_bytes(), raw)
                self.assertFalse((self.docs / "knowledge").exists())

    def test_invalid_requested_paths_do_not_create_the_package(self) -> None:
        for root in ("../outside", "/absolute", "C:/absolute", "knowledge/../outside", "CON"):
            with self.subTest(root=root):
                self.assert_code("path_outside_root", lambda: self.prepare(root))
                self.assertFalse(self.docs.exists())
        self.assert_code("invalid_reference", lambda: self.prepare(".git"))
        self.assertFalse(self.docs.exists())

    def test_prepublication_failure_keeps_existing_declaration(self) -> None:
        write_json(self.path, {"schemaVersion": 1, "source": "project", "version": "1.0.0",
                               "resourceRoots": ["workbooks"], "install": []})
        before = self.path.read_bytes()
        prepared = self.prepare("knowledge/principles")
        denied = PermissionError("Injected destination denial")
        denied.winerror = 19
        with patch("trigrams_toolkit.shared.files.os.replace", side_effect=denied):
            error = self.assert_code("io_error", prepared.write)
        self.assertEqual(error.current, {"packagePath": str(self.path), "packageWritten": False})
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.docs.glob(".harness-*.tmp")), [])

    def test_directory_failure_reports_unwritten_package(self) -> None:
        prepared = self.prepare("workbooks")
        self.docs.write_text("Obstructing file", encoding="utf-8")
        error = self.assert_code("io_error", prepared.write)
        self.assertEqual(error.current, {"packagePath": str(self.path), "packageWritten": False})
        self.assertEqual(self.docs.read_text(encoding="utf-8"), "Obstructing file")

    def test_failed_publication_distinguishes_missing_from_unreadable_destination(self) -> None:
        prepared = self.prepare("workbooks")
        for failure, written in ((FileNotFoundError, False), (NotADirectoryError, False),
                                 (PermissionError, None)):
            with self.subTest(failure=failure.__name__), \
                    patch("trigrams_toolkit.handbook.project_resources.atomic_write", side_effect=OSError("Publication failed")), \
                    patch.object(Path, "read_bytes", side_effect=failure("Cannot read destination")):
                error = self.assert_code("io_error", prepared.write)
                self.assertEqual(error.current, {"packagePath": str(self.path), "packageWritten": written})

    def test_failure_after_publication_reports_confirmed_bytes(self) -> None:
        prepared = self.prepare("workbooks")
        from trigrams_toolkit.shared.files import atomic_write

        def publish_then_fail(path: Path, raw: bytes) -> None:
            atomic_write(path, raw)
            raise OSError("Injected post-publication failure")

        with patch("trigrams_toolkit.handbook.project_resources.atomic_write", side_effect=publish_then_fail):
            error = self.assert_code("io_error", prepared.write)
        self.assertEqual(error.current, {"packagePath": str(self.path), "packageWritten": True})
        self.assertEqual(package_manifest(self.docs, self.schemas)["resourceRoots"], ["workbooks"])
