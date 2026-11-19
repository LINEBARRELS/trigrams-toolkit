"""Installed setup discovery and snapshot synchronization."""
from __future__ import annotations

import shutil
import unittest

import test_installation as fixture
from source_fixture import write_skill
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.handbook.location import sources_for_project
from trigrams_toolkit.shared.serialization import read_json


class ExtensionSourceTests(unittest.TestCase):
    setUp = fixture.InstallationTests.setUp
    candidate = fixture.InstallationTests.candidate
    request = fixture.InstallationTests.request
    apply = fixture.InstallationTests.apply
    assert_code = fixture.InstallationTests.assert_code

    def catalog(self):
        return GuideCatalog(sources_for_project(self.project, self.schemas), self.schemas)

    def test_source_upgrade_is_visible_only_after_sync(self):
        self.apply(self.candidate())
        guide = self.extra / "workbooks/guide/WORKBOOK.md"
        fixture.write(guide, guide.read_bytes().replace(b"Initial", b"Updated"))
        manifest = read_json(self.extra / "extension.json")
        fixture.write(self.extra / "extension.json", {**manifest, "version": "2.0.0"})
        self.assertIn("Initial", self.catalog().load("guide")["resources"][0]["content"])
        self.assertEqual(self.catalog().packages["extra"].manifest["version"], "1.0.0")
        self.apply(self.candidate())
        self.assertIn("Updated", self.catalog().load("guide")["resources"][0]["content"])
        self.assertEqual(self.catalog().packages["extra"].manifest["version"], "2.0.0")
        self.extra.rename(self.root / "unavailable")
        self.assertIn("Updated", self.catalog().load("guide")["resources"][0]["content"])
        self.apply(self.candidate(extensions=[]))
        self.assertFalse(self.snapshot.exists())

    def test_providers_are_added_and_removed_independently(self):
        first = self.apply(self.candidate())
        other = self.project / ".agents/skills/extension-setup-other"
        write_skill(other, other.name)
        fixture.write(other / "assets/extension.json", {"schemaVersion": 1, "extension": "other",
                      "version": "1.0.0", "resourceRoots": [], "install": []})
        added = self.candidate(extensions=["extra", "other"])
        self.assertEqual(added.preview["baseRevision"], first["stateRevision"])
        self.assertFalse(any("/extra/" in change["path"] for change in added.preview["changes"]))
        self.apply(added)
        self.apply(self.candidate(extensions=["other"]))
        self.assertFalse(self.snapshot.exists())
        self.assertTrue(other.exists())
        self.assertEqual(set(self.catalog().packages), {"other"})

    def test_missing_scope_wrong_identity_ambiguous_copy_and_supported_link(self):
        self.assert_code("missing_capability", lambda: self.candidate(agent="claude-code"))
        host = self.project / ".claude/skills/extension-setup-extra"
        host.parent.mkdir(parents=True)
        shutil.copytree(self.extra.parent, host)
        self.assertEqual(self.candidate(agent="claude-code").preview["conflicts"], [])
        fixture.write(host / "assets/workbooks/guide/references/check.md", b"Other source")
        self.assert_code("resource_conflict", lambda: self.candidate(agent="claude-code"))
        shutil.rmtree(host)
        manifest = read_json(self.extra / "extension.json")
        fixture.write(self.extra / "extension.json", {**manifest, "extension": "other"})
        self.assert_code("identity_conflict", self.candidate)
        fixture.write(self.extra / "extension.json", {**manifest, "resourceRoots": ["skills"]})
        self.assert_code("invalid_reference", self.candidate)
        fixture.write(self.extra / "extension.json", manifest)
        try:
            host.symlink_to(self.extra.parent, target_is_directory=True)
            self.assertEqual(self.candidate(agent="claude-code").preview["conflicts"], [])
            (self.extra / "workbooks/escape").symlink_to(self.root, target_is_directory=True)
            self.assert_code("path_outside_root", self.candidate)
        except OSError as error:
            if getattr(error, "winerror", None) != 1314:
                raise
            self.skipTest("Symbolic link privilege unavailable")


if __name__ == "__main__":
    unittest.main()
