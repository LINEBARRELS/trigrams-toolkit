"""Current-state behavior, file handoff and unsupported Plan rejection."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
from support import temporary_directory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]

from trigrams_toolkit.plan.cli import main
from trigrams_toolkit.shared.locking import locked
from trigrams_toolkit.plan.service import PlanService
from trigrams_toolkit.shared.errors import ProtocolError


class _PlanCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = temporary_directory(prefix="plan-current-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.plan = self.root / "docs/plans/P01"
        self.plan.mkdir(parents=True)
        (self.plan / "summary.md").write_text("# Plan\nDeliver a working adapter.\n", encoding="utf-8")
        self.task("T01")
        self.task("T02", ["T01"])
        self.service = PlanService(self.plan)

    def task(self, identity: str, dependencies: list[str] | None = None) -> Path:
        path = self.plan / f"tasks/{identity}/task.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        header = "---\ndependsOn: " + json.dumps(dependencies) + "\n---\n" if dependencies is not None else ""
        path.write_text(header + f"# {identity}\nProduce the declared result.\n", encoding="utf-8")
        return path

    def change(self, identity: str | None, status: str, **explanation: str) -> dict:
        if not (self.plan / "plan.json").exists():
            self.service.validate(sync=True)
        return self.service.update(identity, {"status": status, **explanation})

    def assert_failure(self, code: str, callback) -> None:
        with self.assertRaises(ProtocolError) as failure:
            callback()
        self.assertEqual(failure.exception.code, code, str(failure.exception))


class PlanStateTests(_PlanCase):
    def test_inspect_reads_task_handoff_without_creating_state(self) -> None:
        self.task("T01").write_text(
            "---\nspecs: [artifact_adapter]\nworkspace: ../worktree\n---\n# Task\nBuild it.\n", encoding="utf-8")
        (self.plan / "tasks/T01/result.md").write_text("Actual output and verification.\n", encoding="utf-8")
        before = {path.relative_to(self.plan): path.read_bytes() for path in self.plan.rglob("*") if path.is_file()}
        seen = []
        def locate(identity: str) -> dict:
            seen.append(identity)
            return {"id": identity, "path": "/renamed/spec.md"}
        with patch("trigrams_toolkit.plan.service._contents", side_effect=AssertionError("Directory enumeration")):
            task = self.service.inspect("T01", locate)
        self.assertEqual(set(task), {"id", "path", "status", "workspace", "specs"})
        self.assertEqual(Path(task["path"]), self.plan / "tasks/T01/task.md")
        self.assertEqual(task["workspace"], "../worktree")
        self.assertEqual(task["specs"], [{"id": "artifact_adapter", "path": "/renamed/spec.md"}])
        self.assertEqual(seen, ["artifact_adapter"])
        full = self.service.inspect("T01", locate, full=True)
        self.assertIn("Build it.", full["body"])
        self.assertEqual(full["contents"], ["result.md", "task.md"])
        self.assertEqual(full["specs"], task["specs"])
        self.assertEqual(full["stubs"], {})
        self.assertNotIn("ready", self.service.inspect())
        self.assert_failure("missing_state", self.service.get_tasks)
        self.assertEqual({path.relative_to(self.plan): path.read_bytes()
                          for path in self.plan.rglob("*") if path.is_file()}, before)

    def test_first_write_dependencies_and_plan_completion(self) -> None:
        self.assert_failure("missing_state", lambda: self.service.update("T01", {"status": "doing"}))
        self.assertFalse((self.plan / "plan.json").exists())
        self.assertEqual(self.service.validate(sync=True), {"valid": True, "changed": True})
        before = (self.plan / "plan.json").read_bytes()
        self.assert_failure("not_ready", lambda: self.change("T02", "doing"))
        self.assertEqual((self.plan / "plan.json").read_bytes(), before)
        self.change(None, "doing")
        self.change("T01", "doing")
        self.change("T01", "done")
        self.assert_failure("not_ready", lambda: self.change(None, "done"))
        self.change("T02", "done")
        self.assertEqual(self.service.inspect()["status"], "doing")
        self.change(None, "done")
        state = json.loads((self.plan / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "done")
        self.assertEqual(state["stubs"], {})
        self.assertEqual({key: record["status"] for key, record in state["tasks"].items()}, {"T01": "done", "T02": "done"})

    def test_block_rework_cancel_and_idempotence_keep_only_current_notes(self) -> None:
        self.change("T01", "doing", note="Start adapter")
        self.change("T01", "blocked", reason="Waiting for interface; continue at serialization")
        self.assertEqual(self.service.inspect("T01")["reason"], "Waiting for interface; continue at serialization")
        self.change("T01", "rework", note="Revise adapter")
        state = self.service.inspect("T01")
        self.assertNotIn("reason", state)
        self.assertEqual(state["note"], "Revise adapter")
        first = self.change("T01", "cancelled", reason="Scope removed")
        raw = (self.plan / "plan.json").read_bytes()
        self.assertTrue(first["changed"])
        self.assertFalse(self.change("T01", "cancelled", reason="Scope removed")["changed"])
        self.assertEqual((self.plan / "plan.json").read_bytes(), raw)
        self.assert_failure("not_ready", lambda: self.change("T02", "done"))
        self.change("T02", "cancelled", reason="Dependent scope removed")
        self.change(None, "done")
        self.assertEqual(self.service.inspect()["status"], "done")

    def test_declaration_changes_require_explicit_sync_and_preserve_progress(self) -> None:
        self.change("T01", "done")
        self.task("T03")
        self.assert_failure("definition_out_of_sync", self.service.inspect)
        shutil.rmtree(self.plan / "tasks/T02")
        self.assert_failure("definition_out_of_sync", lambda: self.change("T01", "done"))
        self.assertTrue(self.service.validate(sync=True)["changed"])
        reconciled = json.loads((self.plan / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual({key: record["status"] for key, record in reconciled["tasks"].items()}, {"T01": "done", "T03": "pending"})
        self.change("T03", "doing")
        state = json.loads((self.plan / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T03"]["status"], "doing")
        self.assert_failure("unknown_task", lambda: self.change("T02", "pending"))

    def test_missing_dependency_and_cycle_fail_without_state_write(self) -> None:
        self.task("T02", ["T99"])
        self.assert_failure("invalid_dependency", self.service.inspect)
        self.task("T02", ["T01"])
        self.task("T01", ["T02"])
        self.assert_failure("dependency_cycle", lambda: self.change("T01", "doing"))
        self.assertFalse((self.plan / "plan.json").exists())

    def test_failed_atomic_replace_preserves_existing_state(self) -> None:
        self.change("T01", "doing")
        before = (self.plan / "plan.json").read_bytes()
        with patch("trigrams_toolkit.shared.files.os.replace", side_effect=PermissionError("Denied")):
            with self.assertRaises(PermissionError):
                self.change("T01", "done")
        self.assertEqual((self.plan / "plan.json").read_bytes(), before)
        self.assertEqual(list(self.plan.glob(".harness-*")), [])

    def test_lock_conflict_reports_without_waiting_or_replacing_state(self) -> None:
        self.change("T01", "doing")
        before = (self.plan / "plan.json").read_bytes()
        with locked(self.plan / ".plan.lock"):
            self.assert_failure("lock_busy", lambda: self.change("T01", "done"))
        self.assertEqual((self.plan / "plan.json").read_bytes(), before)

    def test_task_yaml_rejects_duplicate_keys_and_duplicate_status(self) -> None:
        path = self.task("T01")
        for header in ("dependsOn: []\ndependsOn: [T02]", "status: done"):
            with self.subTest(header=header):
                path.write_text("---\n" + header + "\n---\nTask\n", encoding="utf-8")
                self.assert_failure("invalid_task", self.service.inspect)

    def test_unsupported_plan_requires_archive_and_rebuild_without_writing(self) -> None:
        layouts = (
            ("summary.md", "# Plan\n<!-- to-plan:data -->\n"),
            ("plan.json", json.dumps({"schemaVersion": 2, "tasks": []})),
            ("tasks/T01.md", "# Task\n"),
        )
        for relative, contents in layouts:
            with self.subTest(relative=relative):
                path = self.plan / relative
                original = path.read_bytes() if path.exists() else None
                path.write_text(contents, encoding="utf-8")
                before = {item.relative_to(self.plan): item.read_bytes()
                          for item in self.plan.rglob("*") if item.is_file()}
                for operation in (self.service.inspect, lambda: self.change("T01", "done")):
                    with self.assertRaises(ProtocolError) as failure:
                        operation()
                    self.assertEqual(failure.exception.code, "unsupported_plan")
                    self.assertIn("project-setup", str(failure.exception))
                self.assertEqual({item.relative_to(self.plan): item.read_bytes()
                                  for item in self.plan.rglob("*") if item.is_file()}, before)
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)

    def test_invalid_current_records_fail_before_creating_lock(self) -> None:
        records = (
            {"status": "doing", "tasks": {}, "extra": True},
            {"status": "blocked", "tasks": {}},
            {"status": "pending", "reason": "Invalid", "tasks": {}},
            {"status": "pending", "tasks": {"T01": {"status": "unknown"}}},
        )
        for record in records:
            with self.subTest(record=record):
                path = self.plan / "plan.json"
                path.write_text(json.dumps(record), encoding="utf-8")
                before = path.read_bytes()
                self.assert_failure("invalid_state", self.service.inspect)
                self.assert_failure("invalid_state", lambda: self.change("T01", "done"))
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse((self.plan / ".plan.lock").exists())


class PlanCliTests(_PlanCase):
    def invoke(self, *arguments: str) -> tuple[int, dict]:
        output = io.StringIO()
        with patch("trigrams_toolkit.plan.cli.discover_project_root", return_value=self.root), redirect_stdout(output):
            code = main(list(arguments))
        return code, json.loads(output.getvalue())

    def test_inspect_defaults_to_compact_plan_and_task_and_full_preserves_original_fields(self) -> None:
        task_path = self.task("T01")
        task_path.write_text("---\nworkspace: ../worktree\n---\n# Task\nBuild it.\n", encoding="utf-8")
        before = {path: path.read_bytes() for path in self.plan.rglob("*") if path.is_file()}
        code, response = self.invoke("inspect", str(self.plan))
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"], {"directory": str(self.plan), "status": "pending", "tasks": {
            "T01": {"status": "pending", "workspace": "../worktree"},
            "T02": {"status": "pending", "blockers": [{"type": "task", "id": "T01", "required": "done"}]}}})
        code, response = self.invoke("inspect", str(self.plan), "T01")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"], {"id": "T01", "path": str(task_path),
                                           "status": "pending", "workspace": "../worktree"})
        code, response = self.invoke("inspect", str(self.plan), "--full")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["summary"], str(self.plan / "summary.md"))
        self.assertEqual(response["data"]["stubs"], {})
        self.assertEqual(response["data"]["tasks"]["T01"]["dependsOn"], [])
        self.assertEqual(response["data"]["tasks"]["T01"]["path"], str(task_path))
        code, response = self.invoke("inspect", str(self.plan), "T01", "--full")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"], {"id": "T01", "status": "pending", "dependsOn": [],
            "installs": [], "fills": [], "uses": [], "path": str(task_path), "blockers": [],
            "workspace": "../worktree", "directory": str(task_path.parent), "body": task_path.read_text(encoding="utf-8"),
            "contents": ["task.md"], "stubs": {}, "specs": []})
        self.assertEqual(before, {path: path.read_bytes() for path in self.plan.rglob("*") if path.is_file()})

    def test_compact_views_keep_notes_and_manual_reasons_at_both_levels(self) -> None:
        self.change(None, "doing", note="Coordinate delivery")
        self.change("T01", "doing", note="Start adapter")
        code, response = self.invoke("inspect", str(self.plan))
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["note"], "Coordinate delivery")
        self.assertEqual(response["data"]["tasks"]["T01"]["note"], "Start adapter")
        self.change("T01", "blocked", reason="Waiting for interface")
        self.change(None, "blocked", reason="Awaiting approval")
        before = (self.plan / "plan.json").read_bytes()
        code, response = self.invoke("inspect", str(self.plan))
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["reason"], "Awaiting approval")
        self.assertEqual(response["data"]["tasks"]["T01"]["reason"], "Waiting for interface")
        code, response = self.invoke("inspect", str(self.plan), "T01")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["reason"], "Waiting for interface")
        self.assertEqual((self.plan / "plan.json").read_bytes(), before)

    def test_positional_plan_and_task_states(self) -> None:
        plan = self.plan.relative_to(self.root).as_posix()
        code, response = self.invoke("validate", plan, "--sync")
        self.assertEqual(code, 0, response)
        code, response = self.invoke("mark", plan, "doing")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["status"], "doing")
        code, response = self.invoke("mark", plan, "T01", "done", "--note", "Verified")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["note"], "Verified")
        self.assertEqual(response["data"]["id"], "T01")
        self.assertNotIn("tasks", response["data"])
        code, response = self.invoke("block", str(self.plan), "T02", "--reason", "Waiting; continue at adapter")
        self.assertEqual(code, 0, response)
        self.assertEqual(response["data"]["status"], "blocked")

    def test_removed_options_and_empty_reason_fail_before_project_io(self) -> None:
        for arguments in (
            ["claim", str(self.plan), "T01"],
            ["--project", str(self.root), "inspect", str(self.plan)],
            ["inspect", str(self.plan), "--config", "projects.json"],
            ["inspect", str(self.plan), "--init-root", str(self.root)],
            ["inspect", str(self.plan), "--input", "missing.json"],
            ["get-task", str(self.plan), "--full"],
            ["mark", str(self.plan), "T01", "doing", "--full"],
            ["mark", str(self.plan), "T01", "doing", "--request-id", "req_old"],
            ["block", str(self.plan), "T01", "--reason", "  "]):
            with self.subTest(arguments=arguments):
                output = io.StringIO()
                with patch("trigrams_toolkit.plan.cli.discover_project_root", side_effect=AssertionError("Project IO")), redirect_stdout(output):
                    code = main(arguments)
                self.assertEqual(code, 1)
                self.assertEqual(json.loads(output.getvalue())["error"]["code"], "invalid_arguments")
