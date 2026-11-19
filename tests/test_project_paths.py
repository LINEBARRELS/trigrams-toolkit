"""Physical paths and standard Python entry points on supported platforms."""
from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import unittest

from test_project_state import StateFixture


class ProjectPathTests(StateFixture):
    def _directory_link(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            from _winapi import CreateJunction

            try:
                CreateJunction(str(target), str(link))
            except PermissionError as error:
                self.skipTest(f"Windows junction creation denied: {error}")
            self.addCleanup(link.rmdir)
        else:
            link.symlink_to(target, target_is_directory=True)

    def test_aliases_share_identity_and_confine_document_paths(self):
        alias = self.root / "alias"
        project = self.root / "real"
        (project / "docs").mkdir(parents=True)
        self._directory_link(alias, project)
        spec = project / "docs/spec.md"
        spec.write_text("# Spec\n")
        entity = self.call("register", "artifact", "docs/spec.md", cwd=alias)["entity"]
        self.assertEqual(self.call("locate", entity["id"], cwd=alias)["path"], str(spec))
        self.assertFalse(self.call("register", "artifact", alias / "docs/spec.md", cwd=project)["changed"])
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "escape.md").write_text("# Outside\n")
        self._directory_link(project / "docs/link", outside)
        self.call("register", "artifact", "docs/link/escape.md", cwd=alias, code="path_outside_root")
        self.assertEqual((outside / "escape.md").read_text(), "# Outside\n")

    def test_adjacent_project_document_cannot_be_registered(self):
        project = self.root / "project"
        project.mkdir()
        outside = self.docs / "escape.md"
        outside.write_text("# Outside\n")
        self.call("register", "artifact", outside, cwd=project, code="path_outside_root")
        self.call("register", "artifact", "../docs/escape.md", cwd=project, code="path_outside_root")
        self.assertEqual(outside.read_text(), "# Outside\n")
        self.assertFalse((project / ".project-state/state.json").exists())

    def test_registry_directory_link_cannot_redirect_project_state(self):
        project, outside = self.root / "project", self.root / "outside"
        for path in (project, outside):
            path.mkdir()
        self._directory_link(project / ".project-state", outside)
        self.call("list", cwd=project, code="path_outside_root")
        self.call("register", "module", "No", cwd=project, code="path_outside_root")
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows junctions")
    def test_identity_scan_skips_junctions_inside_document_roots(self):
        outside = self.root / "outside"
        outside.mkdir()
        local = self.docs / "spec.md"
        for path in (local, outside / "duplicate.md"):
            path.write_text("---\nartifact-id: artifact_spec\n---\n# Spec\n", encoding="utf-8")
        self._directory_link(self.docs / "junction", outside)
        self.call("register", "artifact", local)
        self.assertEqual(self.call("locate", "artifact_spec")["path"], str(local))

    @unittest.skipIf(os.name == "nt", "Linux path case semantics")
    def test_case_distinct_documents_and_manifest_members(self):
        for name in ("One", "one"):
            (self.docs / (name + ".md")).write_text("---\nartifact-id: artifact_same\n---\n# Spec\n")
        self.call("register", "artifact", self.docs / "One.md", code="identity_conflict")
        (self.docs / "one.md").write_text("---\nartifact-id: artifact_other\n---\n# Spec\n")
        for name in ("One", "one"):
            self.call("register", "artifact", self.docs / (name + ".md"))
        manifest = self.docs / "bundle.json"
        manifest.write_text(json.dumps({"schemaVersion": 1, "members": ["docs/One.md", "docs/one.md"]}))
        self.call("register", "artifact", manifest)
        self.call("validate")

    @unittest.skipUnless(os.name == "nt", "Windows 8.3 paths")
    def test_short_paths_preserve_the_physical_project(self):
        buffer = ctypes.create_unicode_buffer(32768)
        if not ctypes.windll.kernel32.GetShortPathNameW(str(self.root), buffer, len(buffer)):
            raise ctypes.WinError()
        short = Path(buffer.value)
        if str(short).casefold() == str(self.root).casefold():
            self.skipTest("8.3 names are disabled on the temporary volume")
        path = self.docs / "spec.md"
        path.write_text("# Spec\n")
        entity = self.call("register", "artifact", "docs/spec.md", cwd=short)["entity"]
        self.assertEqual(self.call("locate", entity["id"], cwd=short)["path"], str(path))

    def test_unicode_relative_path_and_standard_entry(self):
        path = self.docs / "中文 路径.md"
        path.write_text("# Spec\n", encoding="utf-8")
        relative = "DOCS/中文 路径.MD" if os.name == "nt" else "docs/中文 路径.md"
        entity = self.call("register", "artifact", relative)["entity"]
        self.assertEqual(self.call("locate", entity["id"])["path"], str(path))


if __name__ == "__main__":
    unittest.main()
