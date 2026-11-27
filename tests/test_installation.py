"""Project snapshot changes and single-backup rollback."""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
from trigrams_toolkit.installation.installation_candidate import build_candidate
from trigrams_toolkit.installation.installation_service import apply_installation
from source_fixture import profile_environment, source_commands, write_skill
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import canonical, read_json


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else canonical(value))


class InstallationTests(unittest.TestCase):
    def setUp(self) -> None:
        (ROOT / ".tmp").mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="installation-", dir=ROOT / ".tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.profile = self.root / "profile"
        for name in ("answer-me-with-html", "smell-check"):
            write_skill(self.profile / ".agents/skills" / name, name)
        setup = self.project / ".agents/skills/extension-setup-extra"
        write_skill(setup, setup.name)
        self.extra = setup / "assets"
        write(self.extra / "extension.json", {"schemaVersion": 1, "extension": "extra",
              "version": "1.0.0", "resourceRoots": ["workbooks"], "install": []})
        write(self.extra / "workbooks/guide/WORKBOOK.md", b"---\nname: guide\ndescription: Fixture guide\n---\nInitial")
        write(self.extra / "workbooks/guide/references/check.md", b"Reference bytes")
        self.snapshot = self.project / ".agents/extensions/extra"
        environment = patch.dict(os.environ, profile_environment(self.profile))
        environment.start()
        self.addCleanup(environment.stop)
        self.schemas = SchemaCatalog(schema_paths())
        self.parameters = {"extensions": ["extra"]}

    def candidate(self, **changes):
        return build_candidate(self.project, {**self.parameters, **changes}, self.schemas)

    def test_archive_state_then_rebuild_without_interpreting_it(self):
        from trigrams_toolkit.installation.archive_project import archive_project
        raw = b'{"schemaVersion":5,"unrecognized":"opaque state"}'
        state = self.project / ".agents/harness.json"
        write(state, raw)
        self.assert_code("invalid_schema", self.candidate)
        result = archive_project(self.project, [".agents/harness.json"])
        self.assertEqual((Path(result["archive"]) / ".agents/harness.json").read_bytes(), raw)
        self.apply(self.candidate())
        self.assertEqual(read_json(state)["schemaVersion"], 2)

    def request(self, candidate):
        return {"preview": candidate.preview, "confirmedBy": {"id": "developer", "kind": "human"}}

    def apply(self, candidate, checkpoint=None):
        return apply_installation(self.project, self.request(candidate), self.schemas, "req_" + candidate.preview["operationId"],
                                  candidate.preview["baseRevision"], checkpoint=checkpoint)

    def assert_code(self, code, action):
        with self.assertRaises(ProtocolError) as raised:
            action()
        self.assertEqual(raised.exception.code, code, str(raised.exception))

    def test_preview_and_same_version_replay_leave_skill_and_lock_to_vercel(self):
        lock = self.project / "skills-lock.json"
        write(lock, b'{"version":2,"skills":{}}')
        candidate = self.candidate()
        self.assertFalse((self.project / ".harness").exists())
        self.assertFalse(self.snapshot.exists())
        self.assertEqual(candidate.preview["sources"], {"extra": str(self.extra)})
        self.assertTrue(self.apply(candidate)["changed"])
        state = read_json(self.project / ".agents/harness.json")
        self.assertEqual(state["extensions"], [{"extension": "extra", "version": "1.0.0"}])
        self.assertTrue(all(item["kind"] == "file" and item["contentDigest"].startswith("sha256:")
                            for item in state["managed"]))
        reference = self.snapshot / "workbooks/guide/references/check.md"
        self.assertEqual(reference.read_bytes(), b"Reference bytes")
        repeated = self.candidate()
        self.assertEqual([item["path"] for item in repeated.preview["changes"]], [".agents/harness.json"])
        self.assertFalse(self.apply(repeated)["changed"])
        self.assertEqual(lock.read_bytes(), b'{"version":2,"skills":{}}')

    def test_selection_omission_explicit_clear_and_declared_material(self):
        manifest = read_json(self.extra / "extension.json")
        write(self.extra / "manual.txt", b"Manual")
        manifest["install"] = [{"source": "manual.txt", "target": ".agents/extensions/extra/materials/manual.txt"}]
        write(self.extra / "extension.json", manifest)
        self.apply(self.candidate())
        manual = self.snapshot / "materials/manual.txt"
        self.assertEqual(manual.read_bytes(), b"Manual")
        retained = build_candidate(self.project, {}, self.schemas)
        self.assertEqual(retained.preview["parameters"]["extensions"], ["extra"])
        self.assertFalse(self.apply(retained)["changed"])
        self.assertTrue(manual.is_file())
        write(self.snapshot / "personal.txt", b"Local notes")
        write(self.project / "docs/personal.md", b"Project document")
        self.apply(self.candidate(extensions=[]))
        self.assertFalse(manual.exists())
        self.assertEqual((self.snapshot / "personal.txt").read_bytes(), b"Local notes")
        self.assertEqual((self.project / "docs/personal.md").read_bytes(), b"Project document")
        self.assertTrue((self.extra.parent / "SKILL.md").is_file())
        self.assertFalse((self.snapshot / "extension.json").exists())

    def test_real_cli_binds_preview_to_working_directory_and_replays_apply(self):
        cli = [*source_commands()["harness-install"], "install"]
        environment = os.environ.copy()

        def run(arguments, data, cwd=None, ok=True):
            result = subprocess.run(cli + arguments + ["--input", "-"], input=canonical(data), capture_output=True,
                                    env=environment, cwd=self.project if cwd is None else cwd, timeout=30)
            self.assertTrue(result.stdout, result.stderr.decode(errors="replace"))
            response = json.loads(result.stdout)
            self.assertEqual(response["ok"], ok, response)
            self.assertEqual(result.returncode, 0 if ok else 1)
            return response["data"] if ok else response["error"]

        preview = run(["preview"], self.parameters)
        self.assertEqual(preview["projectRoot"], str(self.project))
        self.assertNotIn("projectRoot", preview["parameters"])
        self.assertFalse((self.project / ".agents/harness.json").exists())
        request = {"preview": preview, "confirmedBy": {"id": "developer", "kind": "human"}}
        arguments = ["apply", "--request-id", "req_cli", "--expected-revision", "0"]
        error = run(arguments, request, cwd=self.root, ok=False)
        self.assertEqual(error["code"], "basis_changed")
        self.assertFalse((self.root / ".harness").exists())
        result = run(arguments, request)
        self.assertEqual(run(arguments, request), result)
        self.assertEqual(result["phase"], "committed")
        self.assertFalse((self.project / ".agents/scripts").exists())
        nested = self.project / "nested"
        nested.mkdir()
        self.assertEqual(run(["preview"], {}, cwd=nested)["projectRoot"], str(nested))
        for flag in ("--config", "--project", "--init-root"):
            with self.subTest(flag=flag):
                self.assertEqual(run(["preview", flag, str(self.project)], self.parameters, ok=False)["code"],
                                 "invalid_arguments")
        for obsolete in ({**self.parameters, "projectRoot": str(self.project)},
                         {**self.parameters, "platforms": ["codex"]}):
            self.assertEqual(run(["preview"], obsolete, ok=False)["code"], "invalid_schema")

    def test_forbidden_install_targets(self):
        original = read_json(self.extra / "extension.json")
        source = "workbooks/guide/references/check.md"
        for target in ("skills-lock.json", ".claude/skills/other/data", ".agents/skills/other/data",
                       "aGeNtS.md", "docs/personal.md", ".agents/extensions/another/material",
                       ".codex/agents/task_developer.toml"):
            with self.subTest(target=target):
                write(self.extra / "extension.json", {**original, "install": [{"source": source, "target": target}]})
                self.assert_code("invalid_reference", self.candidate)

    def test_material_edits_are_visible_and_protected(self):
        self.apply(self.candidate())
        reference = self.snapshot / "workbooks/guide/references/check.md"
        guide = self.snapshot / "workbooks/guide/WORKBOOK.md"
        write(reference, b"Local reference")
        write(guide, b"Local guide")
        for candidate in (self.candidate(), self.candidate(extensions=[])):
            expected = {
                ".agents/extensions/extra/workbooks/guide/references/check.md",
                ".agents/extensions/extra/workbooks/guide/WORKBOOK.md",
            }
            self.assertEqual(set(candidate.preview["conflicts"]), expected)
            self.assert_code("local_modification", lambda: self.apply(candidate))
        self.assertEqual(reference.read_bytes(), b"Local reference")
        self.assertEqual(guide.read_bytes(), b"Local guide")

    def test_stale_sources_and_revision_and_replay_are_distinct(self):
        first = self.candidate()
        stale_revision = self.candidate()
        source = self.extra / "workbooks/guide/references/check.md"
        write(source, b"Updated")
        self.assert_code("basis_changed", lambda: self.apply(first))
        refreshed = self.candidate()
        result = self.apply(refreshed)
        source.unlink()
        self.assertEqual(self.apply(refreshed), result)
        self.assert_code("revision_conflict", lambda: self.apply(stale_revision))

    def test_failed_snapshot_write_rolls_back_and_allows_retry(self):
        self.apply(self.candidate())
        record = self.project / ".agents/harness.json"
        original = record.read_bytes()
        reference = self.snapshot / "workbooks/guide/references/check.md"
        write(self.extra / "workbooks/guide/references/check.md", b"Updated")
        write(self.extra / "workbooks/guide/new.txt", b"New")
        candidate = self.candidate()
        def stop(point):
            if point == "item:.agents/harness.json":
                raise OSError("fixture write failure")
        with self.assertRaisesRegex(OSError, "fixture write failure"):
            self.apply(candidate, stop)
        self.assertEqual(record.read_bytes(), original)
        self.assertEqual(reference.read_bytes(), b"Reference bytes")
        self.assertFalse((reference.parent.parent / "new.txt").exists())
        self.assertEqual(read_json(self.project / ".harness/previous/receipt.json")["phase"], "rolled_back")
        self.assertEqual(self.apply(candidate)["phase"], "committed")
        self.assertEqual(reference.read_bytes(), b"Updated")

    def test_concurrent_apply_serializes_revision_checks(self):
        first, concurrent = self.candidate(), self.candidate()
        locked, release, competing = Event(), Event(), Event()

        def pause(point):
            if point == "backed_up":
                locked.set()
                self.assertTrue(release.wait(10))

        def compete():
            competing.set()
            self.assert_code("revision_conflict", lambda: self.apply(concurrent))

        with ThreadPoolExecutor(max_workers=2) as workers:
            primary = workers.submit(self.apply, first, pause)
            try:
                self.assertTrue(locked.wait(10))
                secondary = workers.submit(compete)
                self.assertTrue(competing.wait(10))
            finally:
                release.set()
            self.assertEqual(primary.result(timeout=10)["stateRevision"], 1)
            secondary.result(timeout=10)

    def test_unowned_file_blocks_install(self):
        guide = self.snapshot / "workbooks/guide/WORKBOOK.md"
        write(guide, b"Personal file")
        self.assertIn(".agents/extensions/extra/workbooks/guide/WORKBOOK.md", self.candidate().preview["conflicts"])
        self.assert_code("local_modification", lambda: self.apply(self.candidate()))
        self.assertEqual(guide.read_bytes(), b"Personal file")

    def test_legacy_record_retires_managed_adapters_and_protects_local_edits(self):
        from trigrams_toolkit.installation.operation_files import file_record

        adapter_path = ".codex/agents/task_developer.toml"
        adapter = self.project / adapter_path
        raw = b'name = "task_developer"\n'
        write(adapter, raw)
        legacy = {
            "schemaVersion": 2,
            "stateRevision": 1,
            "agent": "codex",
            "extensions": [],
            "platforms": ["codex"],
            "managed": [file_record(adapter_path, "core", raw)],
        }
        write(self.project / ".agents/harness.json", legacy)
        write(adapter, b"User customized role")
        blocked = build_candidate(self.project, {}, self.schemas)
        self.assertEqual(blocked.preview["conflicts"], [adapter_path])
        self.assert_code("local_modification", lambda: self.apply(blocked))
        self.assertEqual(adapter.read_bytes(), b"User customized role")

        write(adapter, raw)
        migrated = build_candidate(self.project, {}, self.schemas)
        self.assertEqual(migrated.preview["conflicts"], [])
        self.assertEqual([item["action"] for item in migrated.preview["changes"] if item["path"] == adapter_path],
                         ["remove"])
        self.assertTrue(self.apply(migrated)["changed"])
        self.assertFalse(adapter.exists())
        record = read_json(self.project / ".agents/harness.json")
        self.assertNotIn("platforms", record)
        self.assertEqual(record["managed"], [])


if __name__ == "__main__":
    unittest.main()
