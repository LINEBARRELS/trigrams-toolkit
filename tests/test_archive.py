"""Archival preserves opaque state and rejects unsafe path selections before moving."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
from trigrams_toolkit.installation.archive_project import archive_project
from trigrams_toolkit.shared.errors import ProtocolError


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="archive-project-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        (self.root / "state").mkdir()
        (self.root / "state/opaque.bin").write_bytes(b"\x00\xffnot a known format\r\n")

    def test_opaque_bytes_move_with_original_relative_paths(self):
        result = archive_project(self.root, ["state"])
        self.assertFalse((self.root / "state").exists())
        self.assertEqual((Path(result["archive"]) / "state/opaque.bin").read_bytes(), b"\x00\xffnot a known format\r\n")
        self.assertEqual(result["paths"], ["state"])

    def test_all_sources_are_checked_before_first_move(self):
        for paths in (["state", "missing"], ["state", "state/opaque.bin"], ["../escape"], [".git"]):
            with self.subTest(paths=paths), self.assertRaises(ProtocolError):
                archive_project(self.root, paths)
            self.assertTrue((self.root / "state/opaque.bin").is_file())
            self.assertFalse((self.root / ".harness-archive").exists())

    def test_link_is_moved_without_moving_its_target(self):
        target = self.root.parent / (self.root.name + "-external")
        target.write_bytes(b"external content")
        self.addCleanup(target.unlink)
        (self.root / "pointer").symlink_to(target)
        result = archive_project(self.root, ["pointer"])
        self.assertTrue((Path(result["archive"]) / "pointer").is_symlink())
        self.assertEqual(target.read_bytes(), b"external content")

    def test_parent_link_cannot_move_external_file(self):
        (self.root / "pointer").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ProtocolError):
            archive_project(self.root, ["pointer/external.bin"])

    def test_real_parents_determine_duplicate_and_protected_paths(self):
        (self.root / "pointer").symlink_to(self.root / "state", target_is_directory=True)
        with self.assertRaisesRegex(ProtocolError, "selections overlap"):
            archive_project(self.root, ["state/opaque.bin", "pointer/opaque.bin"])
        self.assertTrue((self.root / "state/opaque.bin").is_file())

        git = self.root / ".git"
        git.mkdir()
        (git / "config").write_bytes(b"Git config fixture")
        (self.root / "metadata").symlink_to(git, target_is_directory=True)
        with self.assertRaisesRegex(ProtocolError, "cannot include Git"):
            archive_project(self.root, ["metadata/config"])
        self.assertTrue((git / "config").is_file())
        self.assertFalse((self.root / ".harness-archive").exists())

    def test_later_move_failure_rolls_back_already_moved_source(self):
        (self.root / "second").write_bytes(b"second")
        rename = Path.rename
        def fail_second(path, target):
            if path == self.root / "second":
                raise OSError("simulated move failure")
            return rename(path, target)
        with patch.object(Path, "rename", fail_second), self.assertRaises(OSError):
            archive_project(self.root, ["state", "second"])
        self.assertTrue((self.root / "state/opaque.bin").is_file())
        self.assertEqual((self.root / "second").read_bytes(), b"second")
