"""Source acceptance retains command and cleanup failures in receipts."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

from acceptance_support import SourceAcceptance


class AcceptanceEntryTests(unittest.TestCase):
    def test_failure_receipt_preserves_commands_already_observed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = SourceAcceptance(root / "evidence.json", "receipt-test")
            session.project, session.env = root, None
            first = session.capture([sys.executable, "-c", "print('first receipt')"])
            self.assertEqual(first.returncode, 0)
            try:
                failed = session.capture([sys.executable, "-c", "raise RuntimeError('original command failure')"])
                if failed.returncode:
                    raise AssertionError(failed.stderr)
            except AssertionError as error:
                session.fail(error)
            session.close()
            saved = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(len(saved["commands"]), 2)
            self.assertEqual(saved["commands"][0]["stdout"], "first receipt\n")
            self.assertIn("original command failure", saved["commands"][1]["stderr"])
            self.assertIn("original command failure", saved["error"]["message"])

    def test_temporary_cleanup_error_does_not_hide_the_original_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = SourceAcceptance(root / "evidence.json", "receipt-test")
            session.temporary = Mock(name="temporary")
            session.temporary.name = str(root / "isolated-files")
            session.temporary.cleanup.side_effect = OSError("temporary executable is busy")
            try:
                raise ValueError("original verification error")
            except ValueError as error:
                session.fail(error)
            session.close()
            saved = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["error"]["message"], "original verification error")
            self.assertEqual(saved["temporaryCleanup"]["error"], "temporary executable is busy")
