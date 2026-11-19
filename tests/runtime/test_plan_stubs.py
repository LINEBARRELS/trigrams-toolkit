"""Observable Stub scheduling, snapshot preservation and failure boundaries."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from support import temporary_directory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.plan.cli import main
from trigrams_toolkit.shared.locking import locked
from trigrams_toolkit.plan.service import PlanService


class StubSchedulingTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = temporary_directory(prefix="plan-stubs-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.plan = self.root / "P01"
        self.plan.mkdir()
        self.summary("S01")
        self.task("T01", installs=["S01"])
        self.task("T02", fills=["S01"])
        self.task("T03", uses=["S01"])
        self.task("T04", dependsOn=["T02", "T03"])
        self.service = PlanService(self.plan)

    def summary(self, *identities: str) -> None:
        blocks = [f"<!-- harness:stub {identity} -->\n### {identity} Service {identity}\n"
                  f"Install the public framework, then fill its behavior.\n<!-- /harness:stub {identity} -->"
                  for identity in identities]
        (self.plan / "summary.md").write_text("# Delivery\n" + "\n".join(blocks), encoding="utf-8")

    def task(self, identity: str, **fields) -> None:
        header = {field: [{"id": stub, "name": f"Service {stub}"} for stub in fields.pop(field, [])]
                  for field in ("installs", "fills", "uses")}
        header.update(fields)
        path = self.plan / f"tasks/{identity}/task.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + json.dumps(header) + "\n---\n# Work\nDeliver and verify.\n", encoding="utf-8")

    def mark(self, identity: str | None, status: str, **fields) -> dict:
        return self.service.update(identity, {"status": status, **fields})

    def ready(self) -> list[str]:
        return [task["id"] for task in self.service.get_tasks()["ready"]]

    def failure(self, code: str, callback) -> ProtocolError:
        with self.assertRaises(ProtocolError) as error:
            callback()
        self.assertEqual(error.exception.code, code, str(error.exception))
        return error.exception

    def test_installation_unlocks_fill_and_framework_consumers(self) -> None:
        self.service.validate(sync=True)
        self.assertEqual(self.ready(), ["T01"])
        self.failure("not_ready", lambda: self.mark("T02", "doing"))
        result = self.mark("T01", "done")
        self.assertEqual(result["stubChanges"], {"S01": "installed"})
        self.assertEqual(self.ready(), ["T02", "T03"])
        self.mark("T02", "doing")
        self.mark("T03", "done")
        self.assertEqual(self.ready(), [])
        result = self.mark("T02", "done")
        self.assertEqual(result["stubChanges"], {"S01": "filled"})
        self.assertEqual(self.service.inspect("T03")["stubs"], {
            "S01": {"name": "Service S01", "status": "filled"}})
        self.assertEqual(self.ready(), ["T04"])
        self.assertFalse(self.mark("T02", "done")["changed"])
        self.failure("not_ready", lambda: self.mark(None, "done"))
        self.mark("T04", "done")
        self.mark(None, "done")
        self.assertEqual(self.ready(), [])
        self.assertTrue(self.service.validate()["valid"])

    def test_readonly_validation_selection_and_inspection_do_not_write(self) -> None:
        self.failure("missing_state", self.service.validate)
        self.failure("missing_state", self.service.get_tasks)
        self.assertFalse((self.plan / ".plan.lock").exists())
        self.service.validate(sync=True)
        before = {path: path.read_bytes() for path in self.plan.rglob("*") if path.is_file()}
        self.service.validate()
        self.service.get_tasks()
        view = self.service.inspect("T03")
        self.assertEqual(view["stubs"], {"S01": {"name": "Service S01", "status": "uninstalled"}})
        self.assertEqual(view["blockers"], [{"type": "stub", "id": "S01", "required": "installed"}])
        full = self.service.inspect("T03", full=True)
        self.assertIn("public framework", full["stubs"]["S01"]["body"])
        self.assertEqual(full["uses"], ["S01"])
        self.assertNotIn("ready", self.service.inspect())
        self.assertEqual(before, {path: path.read_bytes() for path in self.plan.rglob("*") if path.is_file()})

    def test_sync_preserves_status_notes_reasons_and_is_idempotent(self) -> None:
        self.service.validate(sync=True)
        self.mark(None, "doing", note="Coordinate")
        self.mark("T01", "done", note="Framework verified")
        self.mark("T02", "blocked", reason="Awaiting implementation input")
        self.task("T05")
        self.failure("definition_out_of_sync", self.service.get_tasks)
        self.service.validate(sync=True)
        view = self.service.inspect()
        self.assertEqual(view["note"], "Coordinate")
        self.assertEqual(view["tasks"]["T01"]["note"], "Framework verified")
        self.assertEqual(view["tasks"]["T02"]["reason"], "Awaiting implementation input")
        self.assertEqual(view["stubs"]["S01"]["status"], "installed")
        self.assertEqual(self.service.inspect("T03")["stubs"], {
            "S01": {"name": "Service S01", "status": "installed"}})
        self.assertFalse(self.service.validate(sync=True)["changed"])

    def test_mixed_cycle_reports_actual_chain_and_does_not_create_state(self) -> None:
        self.task("T01", installs=["S01"], dependsOn=["T03"])
        error = self.failure("dependency_cycle", lambda: self.service.validate(sync=True))
        chain = error.issues[0]["chain"]
        self.assertEqual(chain[0], chain[-1])
        self.assertEqual(set(chain), {"T01", "T03"})
        self.assertFalse((self.plan / "plan.json").exists())
        self.assertFalse((self.plan / ".plan.lock").exists())

    def test_pure_stub_cycle_and_same_task_stages_are_rejected(self) -> None:
        self.summary("S01", "S02")
        self.task("T01", installs=["S01"], uses=["S02"])
        self.task("T03", installs=["S02"], uses=["S01"])
        self.task("T04", fills=["S02"])
        self.failure("dependency_cycle", lambda: self.service.validate(sync=True))
        self.summary("S01")
        self.task("T01", installs=["S01"], fills=["S01"])
        self.task("T02")
        self.task("T03")
        self.task("T04")
        self.failure("invalid_stub", lambda: self.service.validate(sync=True))

    def test_unknown_named_duplicate_or_missing_producers_fail(self) -> None:
        changes = (
            ("T02", {"fills": ["S99"]}),
            ("T02", {}),
            ("T03", {"installs": ["S01"]}),
            ("T03", {"fills": ["S01"]}),
            ("T03", {"uses": ["S01", "S01"]}),
        )
        for identity, fields in changes:
            with self.subTest(identity=identity, fields=fields):
                self.task(identity, **fields)
                with self.assertRaises(ProtocolError):
                    self.service.validate(sync=True)
                self.task("T02", fills=["S01"])
                self.task("T03", uses=["S01"])
        path = self.plan / "tasks/T03/task.md"
        path.write_text(path.read_text().replace("Service S01", "Wrong name"), encoding="utf-8")
        self.failure("invalid_stub", lambda: self.service.validate(sync=True))

    def test_summary_blocks_and_explicit_task_declarations_are_validated(self) -> None:
        path = self.plan / "summary.md"
        valid = path.read_text(encoding="utf-8")
        invalid = (
            valid + valid,
            valid.replace("<!-- /harness:stub S01 -->", ""),
            valid.replace("<!-- /harness:stub S01 -->", "<!-- /harness:stub S02 -->"),
            valid.replace("### S01 Service S01", "### S02 Wrong"),
            valid.replace("<!-- harness:stub S01 -->", "<!-- harness:stub -->"),
            valid + "\n<!-- harness:stub S02",
        )
        for body in invalid:
            with self.subTest(body=body):
                path.write_text(body, encoding="utf-8")
                self.failure("invalid_stub", lambda: self.service.validate(sync=True))
                self.assertFalse((self.plan / "plan.json").exists())
        path.write_text(valid, encoding="utf-8")
        (self.plan / "tasks/T03/task.md").write_text("# No declarations\n", encoding="utf-8")
        self.failure("invalid_task", lambda: self.service.validate(sync=True))

    def test_cancelled_producer_prevents_completion_until_scope_is_revised(self) -> None:
        self.service.validate(sync=True)
        self.mark("T02", "cancelled", reason="Implementation withdrawn")
        self.failure("unreachable_plan", self.service.validate)
        self.failure("unreachable_plan", self.service.get_tasks)
        self.failure("not_ready", lambda: self.mark(None, "done"))
        self.task("T02")
        self.task("T05", fills=["S01"])
        self.task("T04", dependsOn=["T05", "T03"])
        self.service.validate(sync=True)
        self.assertEqual(self.ready(), ["T01"])

    def test_manual_block_and_plan_gate_are_not_structural_deadlocks(self) -> None:
        self.service.validate(sync=True)
        self.mark("T01", "blocked", reason="Waiting for confirmed contract")
        self.assertTrue(self.service.validate()["valid"])
        self.assertEqual(self.ready(), [])
        self.assertEqual(self.service.get_tasks()["waiting"]["T01"][0]["type"], "manual")
        self.mark("T01", "rework")
        self.assertEqual(self.ready(), ["T01"])
        self.mark(None, "blocked", reason="Overall pause")
        self.assertEqual(self.ready(), [])
        self.failure("not_ready", lambda: self.mark("T01", "doing"))
        self.mark(None, "doing")
        self.assertEqual(self.ready(), ["T01"])
        self.mark(None, "cancelled", reason="Overall withdrawal")
        self.assertEqual(self.ready(), [])

    def test_producer_rollback_cannot_invalidate_active_or_accepted_consumers(self) -> None:
        self.service.validate(sync=True)
        self.mark("T01", "done")
        self.mark("T02", "doing")
        before = (self.plan / "plan.json").read_bytes()
        error = self.failure("invalid_progress", lambda: self.mark("T01", "rework"))
        self.assertEqual(error.issues[0]["task"], "T02")
        self.assertEqual(before, (self.plan / "plan.json").read_bytes())
        self.mark("T02", "pending")
        self.assertEqual(self.mark("T01", "rework")["stubChanges"], {"S01": "uninstalled"})

    def test_finished_task_cannot_acquire_new_handoff_or_be_silently_removed(self) -> None:
        self.service.validate(sync=True)
        self.mark("T03", "cancelled", reason="Remove consumer")
        self.mark("T01", "done")
        before = (self.plan / "plan.json").read_bytes()
        self.task("T05")
        self.task("T01", installs=["S01"], dependsOn=["T05"])
        self.failure("progress_conflict", lambda: self.service.validate(sync=True))
        self.assertEqual(before, (self.plan / "plan.json").read_bytes())
        self.task("T01", installs=["S01"])
        (self.plan / "tasks/T03/task.md").unlink()
        self.task("T04", dependsOn=["T02"])
        self.failure("progress_conflict", lambda: self.service.validate(sync=True))

    def test_schema_corruption_or_tampered_stage_is_not_repaired_by_sync(self) -> None:
        self.service.validate(sync=True)
        original = (self.plan / "plan.json").read_bytes()
        for change in (lambda value: value["stubs"]["S01"].update(status="filled"),
                       lambda value: value["tasks"]["T01"].update(extra=True)):
            value = json.loads(original)
            change(value)
            raw = json.dumps(value).encode()
            (self.plan / "plan.json").write_bytes(raw)
            self.failure("invalid_state", lambda: self.service.validate(sync=True))
            self.assertEqual(raw, (self.plan / "plan.json").read_bytes())
        (self.plan / "plan.json").write_text('{"status":"pending","status":"done"}', encoding="utf-8")
        self.failure("invalid_json", lambda: self.service.validate(sync=True))

    def test_legacy_no_stub_state_sync_preserves_accepted_progress(self) -> None:
        self.summary()
        for identity in ("T01", "T02", "T03", "T04"):
            self.task(identity)
        (self.plan / "plan.json").write_text(json.dumps({"status": "doing", "tasks": {
            "T01": {"status": "done", "note": "Already accepted"}}}), encoding="utf-8")
        self.failure("definition_out_of_sync", self.service.validate)
        self.service.validate(sync=True)
        state = self.service.inspect()
        self.assertEqual(state["tasks"]["T01"]["status"], "done")
        self.assertEqual(state["tasks"]["T01"]["note"], "Already accepted")
        self.assertEqual(state["tasks"]["T02"]["status"], "pending")
        self.assertNotIn("stubs", state)
        self.assertEqual(self.service.inspect(full=True)["stubs"], {})

    def test_legacy_done_record_cannot_fabricate_a_new_stub_installation(self) -> None:
        path = self.plan / "plan.json"
        raw = json.dumps({"status": "doing", "tasks": {"T01": {"status": "done"}}})
        path.write_text(raw, encoding="utf-8")
        self.failure("progress_conflict", lambda: self.service.validate(sync=True))
        self.assertEqual(path.read_text(), raw)

    def test_atomic_failure_and_lock_conflict_preserve_both_task_and_stub(self) -> None:
        self.service.validate(sync=True)
        before = (self.plan / "plan.json").read_bytes()
        with patch("trigrams_toolkit.shared.files.os.replace", side_effect=PermissionError("Denied")):
            with self.assertRaises(PermissionError):
                self.mark("T01", "done")
        self.assertEqual(before, (self.plan / "plan.json").read_bytes())
        self.assertEqual(list(self.plan.glob(".harness-*")), [])
        with locked(self.plan / ".plan.lock"):
            self.failure("lock_busy", lambda: self.mark("T01", "done"))
        self.assertEqual(before, (self.plan / "plan.json").read_bytes())

    def test_cli_sync_selection_and_structured_cycle_errors(self) -> None:
        def invoke(*arguments):
            output = io.StringIO()
            with patch("trigrams_toolkit.plan.cli.current_project_root", return_value=self.root), redirect_stdout(output):
                code = main(list(arguments))
            return code, json.loads(output.getvalue())
        code, result = invoke("validate", str(self.plan), "--sync")
        self.assertEqual((code, result["data"]["valid"]), (0, True))
        code, result = invoke("get-task", str(self.plan))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["data"]["ready"][0]["id"], "T01")
        self.task("T01", installs=["S01"], dependsOn=["T03"])
        code, result = invoke("validate", str(self.plan), "--sync")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"]["code"], "dependency_cycle")
        self.assertTrue(result["error"]["issues"][0]["chain"])
