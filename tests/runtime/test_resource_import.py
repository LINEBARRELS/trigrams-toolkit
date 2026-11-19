"""Approved drafts enter the real project discovery chain without losing inputs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from unittest.mock import patch

from support import ROOT, RuntimeCase, write_json
from trigrams_toolkit.shared.files import atomic_write
from trigrams_toolkit.handbook.principle_import import import_principle

CLI = ROOT / "tests/runtime/resource_cli.py"
DRAFT = b"---\ndescription: Use evidence when choosing a design.\n---\n\n# Evidence\nChoose from observed behavior.\n"


class PrincipleImportCliTests(RuntimeCase):
    def setUp(self) -> None:
        super().setUp()
        binary = self.root / "bin"
        binary.mkdir()
        self.core, environment = self.install_core()
        self.environment = {**os.environ, **environment, "PATH": str(binary) + os.pathsep + os.environ.get("PATH", ""),
                            "PYTHONDONTWRITEBYTECODE": "1"}
        self.declaration = self.project / "docs/resources.json"
        self.entry = self.project / "docs/knowledge/principles/design/use-evidence/PRINCIPLE.md"

    def cli(self, *arguments: str, cwd: Path | None = None, ok: bool = True) -> dict:
        process = subprocess.run([sys.executable, "-B", str(CLI), *arguments], cwd=cwd or self.project,
                                 capture_output=True, encoding="utf-8", env=self.environment, timeout=30)
        self.assertEqual(process.returncode, 0 if ok else 1, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["ok"], ok, result)
        return result

    def draft(self, relative: str = "approved.notes", raw: bytes = DRAFT) -> Path:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def import_draft(self, path: Path, *options: str, ok: bool = True) -> dict:
        return self.cli("import-principle", str(path), "--scope", "design", "--name", "use-evidence", *options, ok=ok)

    def test_first_import_retains_bytes_and_closes_all_four_read_commands(self) -> None:
        raw = b"\xef\xbb\xbf" + DRAFT.replace(b"\n", b"\r\n")
        draft = self.draft("docs/research/principle-drafts/arbitrary-name.txt", raw)
        self.assertNotIn("project:principle:design/use-evidence", self.cli("validate")["resourceIds"])
        result = self.import_draft(draft)
        self.assertEqual(result, {"ok": True, "resourceId": "project:principle:design/use-evidence",
                                  "entryPath": str(self.entry), "operation": "created"})
        self.assertEqual(draft.read_bytes(), raw)
        self.assertEqual(self.entry.read_bytes(), raw)
        self.assertEqual(json.loads(self.declaration.read_bytes()), {
            "schemaVersion": 1, "source": "project", "version": "1.0.0",
            "resourceRoots": ["knowledge/principles"], "install": []})
        self.assertIn("design", self.cli("scopes", "--kind", "principle")["scopes"])
        self.assertEqual(self.cli("list", "--kind", "principle", "--scope", "design")["resources"], [
            {"resourceId": result["resourceId"], "description": "Use evidence when choosing a design."}])
        loaded = self.cli("load", result["resourceId"])
        self.assertEqual(loaded["resources"][0]["content"], DRAFT.decode())
        self.assertIn(result["resourceId"], self.cli("validate")["resourceIds"])
        self.assertEqual(set(self.cli("validate")["checkedSources"]), {str(self.core), str(self.project / "docs")})

    def test_existing_custom_resources_and_declaration_fields_survive_another_import(self) -> None:
        self.import_draft(self.draft())
        workbook = self.project / "docs/manuals/research/WORKBOOK.md"
        workbook.parent.mkdir(parents=True)
        workbook.write_text("---\nname: Research\ndescription: Follow sources.\n---\n# Research\n", encoding="utf-8")
        manifest = {"schemaVersion": 1, "source": "project", "version": "2.4.6",
                    "resourceRoots": ["manuals", "knowledge/principles"],
                    "install": [{"source": "skills/local", "target": ".agents/skills/local"}]}
        write_json(self.declaration, manifest)
        before = self.declaration.read_bytes(), self.declaration.stat().st_mtime_ns
        second = self.draft("second.md", DRAFT.replace(b"Evidence", b"Second"))
        result = self.cli("import-principle", str(second), "--scope", "design", "--name", "second")
        self.assertEqual((self.declaration.read_bytes(), self.declaration.stat().st_mtime_ns), before)
        self.assertEqual(json.loads(self.declaration.read_bytes()), manifest)
        self.assertEqual(self.cli("load", "project:workbook:research")["selected"], "project:workbook:research")
        self.assertEqual(len(self.cli("list", "--kind", "principle", "--scope", "design")["resources"]), 2)
        self.assertIn(result["resourceId"], self.cli("validate")["resourceIds"])

    def test_create_conflict_explicit_replace_missing_replace_and_same_file(self) -> None:
        draft = self.draft()
        self.import_draft(draft)
        before = self.declaration.read_bytes(), self.entry.read_bytes()
        revised = self.draft("revised.md", DRAFT.replace(b"observed behavior", b"verified results"))
        conflict = self.import_draft(revised, ok=False)
        self.assertEqual(conflict["error"]["code"], "resource_conflict")
        self.assertEqual((self.declaration.read_bytes(), self.entry.read_bytes()), before)
        updated = self.import_draft(revised, "--replace")
        self.assertEqual(updated["operation"], "updated")
        self.assertEqual(self.entry.read_bytes(), revised.read_bytes())
        self.assertEqual(draft.read_bytes(), DRAFT)
        missing = self.cli("import-principle", str(revised), "--scope", "design", "--name", "absent", "--replace", ok=False)
        self.assertEqual(missing["error"]["code"], "invalid_reference")
        self.assertFalse(self.entry.parent.parent.joinpath("absent").exists())
        same = self.import_draft(self.entry, "--replace", ok=False)
        self.assertEqual(same["error"]["code"], "invalid_arguments")
        self.assertEqual(self.declaration.read_bytes(), before[0])

    def test_invalid_tokens_and_missing_or_directory_sources_fail_before_writes(self) -> None:
        draft = self.draft()
        for scope, name in (("Design", "rule"), ("design", "bad--name"), ("../design", "rule")):
            with self.subTest(scope=scope, name=name):
                result = self.cli("import-principle", str(draft), "--scope", scope, "--name", name, ok=False)
                self.assertEqual(result["error"]["code"], "invalid_arguments")
        for source in (self.project / "missing.md", self.project):
            with self.subTest(source=source):
                self.assertEqual(self.import_draft(source, ok=False)["error"]["code"], "invalid_reference")
        self.assertFalse(self.declaration.exists())
        self.assertFalse(self.entry.parent.exists())

    def test_invalid_drafts_fail_before_declaration_or_entry_writes(self) -> None:
        cases = [b"No metadata", b"---\ndescription: Rule.\nincludes: []\n---\nBody\n",
                 b"---\ndescription: Rule.\nname: Extra\n---\nBody\n",
                 b"---\ndescription: Rule.\n---\n \t\n", DRAFT + b"\xff",
                 b"---\ndescription: First\ndescription: Duplicate\n---\nBody\n"]
        for raw in cases:
            with self.subTest(raw=raw):
                source = self.draft(raw=raw)
                self.assertEqual(self.import_draft(source, ok=False)["error"]["code"], "invalid_schema")
                self.assertEqual(source.read_bytes(), raw)
                self.assertFalse(self.declaration.exists())
                self.assertFalse(self.entry.parent.exists())

    def test_damaged_or_conflicting_packages_are_preserved_before_writes(self) -> None:
        draft = self.draft()
        valid = {"schemaVersion": 1, "source": "project", "version": "1.0.0", "resourceRoots": [], "install": []}
        cases = [(b"broken JSON", "invalid_json"),
                 (json.dumps({**valid, "version": "bad"}).encode(), "invalid_schema"),
                 (json.dumps({**valid, "source": "other"}).encode(), "identity_conflict"),
                 (json.dumps({**valid, "resourceRoots": ["knowledge/principles/design"]}).encode(), "resource_conflict")]
        self.declaration.parent.mkdir()
        for raw, code in cases:
            with self.subTest(code=code):
                self.declaration.write_bytes(raw)
                self.assertEqual(self.import_draft(draft, ok=False)["error"]["code"], code)
                self.assertEqual(self.declaration.read_bytes(), raw)
                self.assertFalse(self.entry.parent.exists())

    def test_draft_paths_and_output_use_the_current_project_root(self) -> None:
        source = self.draft("src/local.txt")
        result = self.cli("import-principle", "src/local.txt", "--scope", "design", "--name", "use-evidence")
        self.assertEqual(result["entryPath"], str(self.entry))
        self.assertFalse((source.parent / "docs").exists())
        other = self.root / "other-project"
        other.mkdir()
        result = self.cli("import-principle", str(source), "--scope", "design", "--name", "use-evidence", cwd=other)
        self.assertEqual(result["entryPath"], str(other / "docs/knowledge/principles/design/use-evidence/PRINCIPLE.md"))
        self.assertEqual(source.read_bytes(), DRAFT)

    def test_external_docs_link_is_rejected_before_any_write(self) -> None:
        source = self.draft()
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.project / "docs").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if getattr(error, "winerror", None) != 1314:
                raise
            self.skipTest("Symbolic link privilege unavailable")
        error = self.import_draft(source, ok=False)["error"]
        self.assertEqual(error["code"], "path_outside_root")
        self.assertEqual(self.cli("scopes", ok=False)["error"]["code"], "path_outside_root")
        self.assertEqual(list(outside.iterdir()), [])

    def test_real_body_directory_failure_reports_the_published_declaration(self) -> None:
        source = self.draft()
        obstruction = self.entry.parent
        obstruction.parent.mkdir(parents=True)
        obstruction.write_text("Obstructing file", encoding="utf-8")
        error = self.import_draft(source, ok=False)["error"]
        self.assertEqual(error["code"], "io_error")
        self.assertEqual(error["current"], {"packagePath": str(self.declaration), "packageWritten": True,
                                            "entryPath": str(self.entry), "entryWritten": False})
        self.assertTrue(self.declaration.is_file())
        self.assertEqual(obstruction.read_text(), "Obstructing file")
        self.assertEqual(source.read_bytes(), DRAFT)

    def test_postwrite_discovery_failure_reports_both_files_without_success(self) -> None:
        source = self.draft()
        write_json(self.declaration, {"schemaVersion": 1, "source": "project", "version": "1.0.0",
                                      "resourceRoots": ["workbooks"], "install": []})
        broken = self.project / "docs/workbooks/broken/WORKBOOK.md"
        broken.parent.mkdir(parents=True)
        broken.write_text("Invalid existing guide", encoding="utf-8")
        error = self.import_draft(source, ok=False)["error"]
        self.assertEqual(error["code"], "invalid_schema")
        self.assertEqual(error["current"]["packageWritten"], True)
        self.assertEqual(error["current"]["entryWritten"], True)
        self.assertEqual(self.entry.read_bytes(), DRAFT)
        self.assertEqual(source.read_bytes(), DRAFT)


class PrincipleImportFailureTests(RuntimeCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = self.project / "draft.md"
        self.source.write_bytes(DRAFT)
        self.entry = self.project / "docs/knowledge/principles/design/evidence/PRINCIPLE.md"

    def run_import(self):
        return import_principle(self.project, self.source, "design", "evidence", self.schemas)

    def test_declaration_failure_current_is_merged_with_unwritten_entry(self) -> None:
        with patch("trigrams_toolkit.handbook.project_resources.atomic_write", side_effect=OSError("Injected declaration failure")):
            error = self.assert_code("io_error", self.run_import)
        self.assertFalse(error.current["packageWritten"])
        self.assertFalse(error.current["entryWritten"])
        self.assertEqual(error.current["entryPath"], str(self.entry))
        self.assertFalse(self.entry.exists())

    def test_failure_after_body_publication_reports_the_confirmed_content(self) -> None:
        def publish_then_fail(path: Path, raw: bytes) -> None:
            atomic_write(path, raw)
            raise OSError("Injected post-publication failure")

        with patch("trigrams_toolkit.handbook.principle_import.atomic_write", side_effect=publish_then_fail):
            error = self.assert_code("io_error", self.run_import)
        self.assertTrue(error.current["packageWritten"])
        self.assertTrue(error.current["entryWritten"])
        self.assertEqual(self.entry.read_bytes(), DRAFT)
        self.assertEqual(self.source.read_bytes(), DRAFT)
