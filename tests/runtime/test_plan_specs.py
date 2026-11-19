"""Task Spec lookup follows registered identity after a file rename."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from support import temporary_directory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PlanSpecLookupTests(unittest.TestCase):
    def test_inspect_follows_spec_identity_and_retains_unresolved_ids(self) -> None:
        with temporary_directory(prefix="plan-spec-lookup-") as temporary:
            root = Path(temporary)
            project = root / "project"
            plan = project / "docs/plans/P01"
            task = plan / "tasks/T01/task.md"
            task.parent.mkdir(parents=True)
            task.write_text("---\nspecs: [artifact_adapter, artifact_missing]\n---\n# Build adapter\n", encoding="utf-8")
            (plan / "summary.md").write_text("# Adapter plan\n", encoding="utf-8")
            document = project / "docs/specs/adapter.md"
            document.parent.mkdir(parents=True)
            document.write_text("---\nartifact-id: artifact_adapter\n---\n# Adapter\n", encoding="utf-8")
            binary = root / "bin"
            binary.mkdir()
            environment = dict(os.environ)
            environment["PATH"] = str(binary)
            registered = subprocess.run(
                [sys.executable, "-m", "trigrams_toolkit.state.cli", "register", "artifact", "docs/specs/adapter.md"],
                cwd=project, env=environment, capture_output=True, text=True, encoding="utf-8", timeout=30)
            self.assertEqual(registered.returncode, 0, registered.stdout + registered.stderr)
            renamed = document.with_name("adapter-renamed.md")
            document.rename(renamed)
            views = []
            for options in ([], ["--full"]):
                inspected = subprocess.run(
                    [sys.executable, "-B", "-m", "trigrams_toolkit.plan.cli",
                     "inspect", "docs/plans/P01", "T01", *options],
                    cwd=project, env=environment, capture_output=True, text=True, encoding="utf-8", timeout=30)
                self.assertEqual(inspected.returncode, 0, inspected.stdout + inspected.stderr)
                result = json.loads(inspected.stdout)["data"]
                self.assertEqual(Path(result["specs"][0]["path"]).resolve(), renamed.resolve())
                self.assertEqual(result["specs"][1]["id"], "artifact_missing")
                self.assertIn("error", result["specs"][1])
                self.assertEqual("body" in result, bool(options))
                views.append(result)
            self.assertEqual(views[0]["specs"], views[1]["specs"])
            self.assertFalse((plan / "plan.json").exists())
            self.assertFalse((plan / ".plan.lock").exists())

    def test_project_boundaries_reject_outside_plans_and_writable_links(self) -> None:
        with temporary_directory(prefix="plan-paths-") as temporary:
            root = Path(temporary)
            project, outside = root / "project 空间", root / "sibling"
            project.mkdir()
            outside.mkdir()
            (outside / "summary.md").write_text("# Sibling plan\n", encoding="utf-8")

            def run(*args: str):
                result = subprocess.run([sys.executable, "-B", "-m", "trigrams_toolkit.plan.cli", *args],
                                        cwd=project, capture_output=True, encoding="utf-8", timeout=30)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["error"]["code"], "path_outside_root")

            run("inspect", str(outside))
            run("inspect", "../sibling")
            try:
                (project / "linked").symlink_to(outside, target_is_directory=True)
            except OSError as error:
                if getattr(error, "winerror", None) != 1314:
                    raise
                # Directory junctions provide the same escape regression on Windows without link privilege.
                subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(project / "linked"), str(outside)],
                               check=True, capture_output=True, timeout=20)
            run("inspect", "linked")
            plan = project / "plan"
            plan.mkdir()
            (plan / "summary.md").write_text("# In-project plan\n", encoding="utf-8")
            task = plan / "tasks/T01/task.md"
            task.parent.mkdir(parents=True)
            task.write_text("# Task\n", encoding="utf-8")
            lock = outside / "outside.lock"
            lock.touch()
            try:
                (plan / ".plan.lock").symlink_to(lock)
            except OSError as error:
                if getattr(error, "winerror", None) != 1314:
                    raise
                self.skipTest("Symbolic link privilege unavailable for file lock")
            run("validate", "plan", "--sync")
            self.assertEqual(lock.read_bytes(), b"")
            self.assertFalse((plan / "plan.json").exists())
