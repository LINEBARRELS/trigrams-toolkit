"""Atomic publication retains original bytes when Windows refuses replacement."""
from pathlib import Path
import os
import sys
from support import temporary_directory
import unittest
from unittest.mock import patch

from trigrams_toolkit.shared import files


@unittest.skipUnless(os.name == "nt", "Windows replacement conflict behavior")
class AtomicFileTests(unittest.TestCase):
    def setUp(self):
        self.temp = temporary_directory(prefix="atomic-file-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "receipt.json"
        self.target.write_bytes(b"original")

    def denied(self, code=32):
        error = PermissionError("Injected replacement conflict")
        error.winerror = code
        return error

    def test_short_sharing_conflict_retries_the_same_bytes_then_publishes(self):
        replace = files.os.replace
        count = 0
        def intermittent(source, target):
            nonlocal count
            count += 1
            if count < 3:
                self.assertEqual(self.target.read_bytes(), b"original")
                raise self.denied()
            return replace(source, target)
        with patch.object(files.os, "replace", side_effect=intermittent), patch.object(files.time, "sleep"):
            files.atomic_write(self.target, b"confirmed candidate")
        self.assertEqual(self.target.read_bytes(), b"confirmed candidate")
        self.assertEqual(list(self.root.glob(".harness-*")), [])

    def test_persistent_access_denial_is_bounded_and_retains_original(self):
        with patch.object(files.os, "replace", side_effect=self.denied(5)) as replace, patch.object(files.time, "sleep"):
            with self.assertRaises(PermissionError):
                files.atomic_write(self.target, b"candidate")
            self.assertGreater(replace.call_count, 1)
            self.assertLessEqual(replace.call_count, 6)
        self.assertEqual(self.target.read_bytes(), b"original")
        self.assertEqual(list(self.root.glob(".harness-*")), [])

    def test_other_permission_failures_are_not_retried(self):
        with patch.object(files.os, "replace", side_effect=self.denied(19)) as replace:
            with self.assertRaises(PermissionError):
                files.atomic_write(self.target, b"candidate")
            self.assertEqual(replace.call_count, 1)
        self.assertEqual(self.target.read_bytes(), b"original")
