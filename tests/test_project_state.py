"""Project State behavior through its standard command and Registry service."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from trigrams_toolkit.project_context.paths import path_key, physical_path
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.process_lock import acquire_process_lock
from trigrams_toolkit.state.arguments import COMMAND_NAMES, parse_arguments
from trigrams_toolkit.state.service import execute

ROOT = Path(__file__).resolve().parents[1]
from source_fixture import source_commands


class StateFixture(unittest.TestCase):
    def setUp(self):
        (ROOT / ".tmp").mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="state-兼容 ", dir=ROOT / ".tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.state = self.root / ".project-state/state.json"
        self.env = dict(os.environ)
        self.command = source_commands()["project-state"]

    def call(self, *args, code=None, cwd=None):
        result = subprocess.run([*self.command, *map(str, args)], cwd=cwd or self.root, env=self.env,
                                capture_output=True, timeout=30)
        self.assertEqual(result.stderr, b"", result.stderr.decode(errors="replace"))
        value = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0 if code is None else 1, value)
        self.assertEqual(value["ok"], code is None, value)
        if code is not None:
            self.assertEqual(value["error"]["code"], code, value)
            return value["error"]
        return value["data"]

    def modules(self):
        for name in ("one", "two", "empty"):
            self.call("register", "module", name, "--id", "module_" + name)
        for name in ("a", "b"):
            self.call("register", "feature", name, "--id", "feature_" + name, "--module", "module_one")

    def artifact(self, name, *ownership, kind="core:architecture-spec"):
        path = self.docs / (name + ".md")
        path.write_text(f"---\nartifact-id: artifact_{name}\n---\n# {name}\n", encoding="utf-8")
        return self.call("register", "artifact", path, "--kind", kind, *ownership)["entity"]



class ProjectStateCases(StateFixture):
    def test_commands_arguments_and_no_side_effect_help(self):
        snapshot = set(self.root.rglob("*"))
        for command in ("", "register", *COMMAND_NAMES):
            values = []
            for flag in ("-h", "--help"):
                result = subprocess.run([*self.command, *command.split(), flag], cwd=self.root, env=self.env, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertLessEqual(max(map(len, result.stdout.splitlines())), 100)
                self.assertLessEqual(len(result.stdout.splitlines()), 35)
                values.append(result.stdout)
            self.assertEqual(*values)
        versions = [
            subprocess.run([*self.command, flag], cwd=self.docs, env=self.env, capture_output=True, check=True,
                           text=True, encoding="utf-8").stdout.strip()
            for flag in ("-v", "--version")
        ]
        self.assertTrue(versions[0])
        self.assertEqual(*versions)
        self.assertEqual(snapshot, set(self.root.rglob("*")))
        for args in [("unknown",), ("register", "module"), ("register", "module", ""),
                     ("related", "artifact_x", "--direction", "sideways"),
                     ("project", "register", "."), ("project", "resolve"),
                     ("list", "--config", "."), ("list", "--project", "."), ("list", "--init-root", "."),
                     ("register", "artifact", "x", "--feature", "feature_x"),
                     ("register", "artifact", "x", "--module", "module_x", "--module", "module_y"),
                     ("register", "artifact", "x", "--module", "module_x", "--feature")]:
            self.call(*args, code="invalid_arguments")

    def test_public_views_one_hop_direction_and_lazy_paths(self):
        self.modules()
        self.artifact("module", "--module", "module_one")
        self.artifact("shared", "--module", "module_one", "--feature", "feature_a", "--feature", "feature_b")
        self.artifact("a", "--module", "module_one", "--feature", "feature_a")
        self.artifact("b", "--module", "module_one", "--feature", "feature_b")
        self.artifact("remote", "--module", "module_two")
        self.artifact("unbound")
        self.assertEqual(self.call("locate", "feature_a"), {"id": "feature_a", "kind": "core:feature", "name": "a", "moduleId": "module_one"})
        listed = self.call("list")["items"]
        self.assertEqual([r["id"] for r in listed], sorted(r["id"] for r in listed))
        for row in listed:
            keys = {"id", "kind", "name"} if row["kind"] == "core:module" else {"id", "kind", "name", "moduleId"} if row["kind"] == "core:feature" else {"id", "kind", "title", "featureIds"} | ({"moduleId"} if "moduleId" in row else set())
            self.assertEqual(set(row), keys)
            located = self.call("locate", row["id"])
            self.assertEqual(set(located), keys | ({"path"} if "title" in row else set()))
        both = self.call("related", "feature_a")
        self.assertEqual(set(both), {"items", "relations"})
        self.assertEqual({r["id"] for r in both["items"]}, {"module_one", "artifact_a", "artifact_shared"})
        for direction in ("incoming", "outgoing"):
            result = self.call("related", "feature_a", "--direction", direction)
            self.assertEqual(result["relations"], [e for e in both["relations"] if e["to" if direction == "incoming" else "from"] == "feature_a"])
        self.assertEqual(self.call("related", "module_empty"), {"items": [], "relations": []})
        (self.docs / "b.md").unlink()
        self.assertEqual(self.call("list")["items"], listed)
        self.assertEqual(self.call("related", "feature_a"), both)
        self.call("related", "module_one", code="invalid_reference")
        (self.docs / "a.md").unlink()
        self.call("related", "feature_a", "--direction", "outgoing", code="invalid_reference")
        self.assertEqual(self.call("related", "feature_a", "--direction", "incoming")["items"], [])
        self.call("locate", "artifact_unknown", code="invalid_reference")
        self.call("related", "artifact_unknown", code="invalid_reference")

    def test_writeback_ownership_idempotence_and_failed_validation(self):
        self.modules()
        path = self.docs / "spec.md"
        extra = "title: 'Inventory' # keep title\r\nlabels: [one, two]\r\nnotes: |\r\n  keep this\r\n"
        tail = "\r\n# Inventory\r\n\r\n```yaml\r\nmoduleId: example\r\n```\r\n"
        path.write_bytes(("\ufeff---\r\n" + extra + "moduleId: <placeholder>\r\nfeatureIds: invalid\r\n---\r\n" + tail).encode())
        args = ("register", "artifact", path, "--module", "module_one", "--feature", "feature_a", "--feature", "feature_b")
        entity = self.call(*args)["entity"]
        self.assertRegex(entity["id"], r"^artifact_[A-Za-z0-9]{10}$")
        raw = path.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf---\r\n"))
        self.assertIn(extra.encode(), raw)
        self.assertTrue(raw.endswith(("---\r\n" + tail).encode()))
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        state = self.root / ".project-state/state.json"
        before = state.read_bytes()
        self.assertFalse(self.call(*args)["changed"])
        self.assertEqual((path.read_bytes(), state.read_bytes()), (raw, before))
        for ownership in [("--module", "module_missing"), ("--module", "module_two", "--feature", "feature_a"),
                          ("--module", "module_one", "--feature", "feature_a", "--feature", "feature_a")]:
            self.call("register", "artifact", path, *ownership, code="invalid_reference")
            self.assertEqual((path.read_bytes(), state.read_bytes()), (raw, before))
        path.write_bytes(raw.replace(b"moduleId: module_one", b"moduleId: module_two"))
        self.call("validate", code="declaration_changed")
        self.assertTrue(self.call("register", "artifact", path)["changed"])
        self.assertEqual(path.read_bytes(), raw)
        replaced = self.call("register", "artifact", path, "--module", "module_two")["entity"]
        self.assertEqual(replaced["featureIds"], [])
        self.assertNotIn(b"featureIds:", path.read_bytes())
        moved = self.docs / "移动 文稿.md"
        path.rename(moved)
        self.assertEqual(self.call("locate", entity["id"])["path"], str(moved))
        self.call("validate")
        (self.docs / "duplicate.md").write_bytes(moved.read_bytes())
        self.call("validate", code="identity_conflict")
        self.call("locate", entity["id"], code="identity_conflict")

    def test_yaml_alias_merge_duplicates_and_newlines(self):
        for index, newline in enumerate(("\n", "\r\n", "\r")):
            path = self.docs / f"sample{index}.md"
            header = "# comment\ndefaults: &defaults\n  labels: [one, two]\n<<: *defaults\nquoted: 'yes'\n"
            tail = "# Body\n\nExact body.\n".replace("\n", newline)
            path.write_bytes(("\ufeff---" + newline + header.replace("\n", newline) + "---" + newline + tail).encode())
            self.call("register", "artifact", path)
            raw = path.read_bytes()
            self.assertIn(b"# comment", raw)
            self.assertIn(b"&defaults", raw)
            self.assertIn(b"*defaults", raw)
            self.assertTrue(raw.endswith(tail.encode()))
            again = self.call("register", "artifact", path)
            self.assertFalse(again["changed"])
            self.assertEqual(path.read_bytes(), raw)
        for header in ("title: One\ntitle: Two", "defaults: &d {title: One}\n<<: *d\ntitle: Two", "7: bad", "yes: bad"):
            path = self.docs / "bad.md"
            raw = ("---\n" + header + "\n---\n# Body\n").encode()
            path.write_bytes(raw)
            self.call("register", "artifact", path, code="io_error")
            self.assertEqual(path.read_bytes(), raw)

    def test_first_registration_and_binary_manifest(self):
        path = self.docs / "first.md"
        path.write_text("---\nartifact-id: artifact_unbound\nmoduleId: module_missing\nfeatureIds: [feature_missing]\n---\n# First\n", encoding="utf-8")
        entity = self.call("register", "artifact", path)["entity"]
        self.assertNotIn("moduleId", entity)
        self.assertEqual(entity["featureIds"], [])
        self.assertNotIn("moduleId", path.read_text())
        (self.docs / "image.bin").write_bytes(bytes(range(5)))
        manifest = self.docs / "image.json"
        manifest.write_text(json.dumps({"schemaVersion": 1, "members": ["docs/image.bin"], "custom": "preserved"}))
        entity = self.call("register", "artifact", manifest)["entity"]
        self.assertEqual(entity["identityMode"], "manifest")
        self.assertEqual(json.loads(manifest.read_text())["custom"], "preserved")
        self.assertFalse(self.call("register", "artifact", manifest)["changed"])
        self.call("validate")
        value = json.loads(manifest.read_text())
        value["members"] *= 2
        manifest.write_text(json.dumps(value))
        self.call("register", "artifact", manifest, code="identity_conflict")

    def test_relations_provider_types_cardinality_and_cycles(self):
        (self.docs / "resources.json").write_text(json.dumps({"schemaVersion": 1, "source": "project", "artifactTypes": ["project:spec"],
            "relationTypes": [{"kind": "project:depends", "fromKinds": ["project:spec"], "toKinds": ["project:spec"], "acyclic": True, "maxOutgoing": 1}]}))
        for name in ("one", "two", "three"):
            self.artifact(name, kind="project:spec")
        args = ("relate", "artifact_one", "project:depends", "artifact_two")
        self.assertTrue(self.call(*args)["changed"])
        self.assertFalse(self.call(*args)["changed"])
        self.call("relate", "artifact_two", "project:depends", "artifact_one", code="invalid_reference")
        self.call("relate", "artifact_one", "project:depends", "artifact_three", code="invalid_reference")
        self.assertTrue(self.call(*args, "--remove")["changed"])
        self.assertFalse(self.call(*args, "--remove")["changed"])
        self.call("validate")

    def test_reads_and_writes_local_registry_without_mapping(self):
        old_config = self.root / "absent-mapping.json"
        self.env["HARNESS_PROJECT_CONFIG"] = str(old_config)
        self.assertEqual(self.call("list")["items"], [])
        self.assertFalse(self.state.exists())
        created = self.call("register", "module", "Local", "--id", "module_local")["entity"]
        self.assertEqual(json.loads(self.state.read_bytes())["modules"], [created])
        self.assertFalse(old_config.exists())

    def test_invalid_registry_is_preserved(self):
        self.state.parent.mkdir()
        raw = b'{"schemaVersion":0}'
        self.state.write_bytes(raw)
        self.call("list", code="invalid_schema")
        self.call("register", "module", "No", code="invalid_schema")
        self.assertEqual(self.state.read_bytes(), raw)

    def test_lock_contention_and_io_failure(self):
        lock = acquire_process_lock(self.state)
        try:
            self.call("register", "module", "No", code="lock_conflict")
        finally:
            lock.release()
            lock.release()
        blocked = self.root / "blocked"
        blocked.mkdir()
        (blocked / ".project-state").write_text("file")
        error = self.call("register", "module", "No", cwd=blocked, code="io_error")
        self.assertTrue(error["details"]["cause"])

    def test_worktree_nested_and_adjacent_projects_have_local_state(self):
        repository, worktree = self.root / "repo", self.root / "工作树"
        for arguments in [("init", str(repository)), ("-C", str(repository), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-m", "init"),
                          ("-C", str(repository), "worktree", "add", "--detach", str(worktree))]:
            subprocess.run(["git", *arguments], capture_output=True, check=True)
        projects = {repository: "repo", worktree: "worktree", worktree / "nested": "nested",
                    self.root / "相邻 工程": "adjacent"}
        for root, name in projects.items():
            root.mkdir(exist_ok=True)
            self.assertEqual(self.call("list", cwd=root)["items"], [])
            self.call("register", "module", name, "--id", f"module_{name}", cwd=root)
        for root, name in projects.items():
            self.assertEqual(self.call("list", cwd=root)["items"], [
                {"id": f"module_{name}", "kind": "core:module", "name": name}
            ])
            self.assertTrue((root / ".project-state/state.json").is_file())

    def test_archive_bodies_are_excluded_from_automatic_identity_scan(self):
        archive = self.docs / "archives"
        archive.mkdir()
        active, archived = self.docs / "active.md", archive / "original.md"
        for path in (active, archived):
            path.write_text("---\nartifact-id: artifact_spec\n---\n# Spec\n")
        self.call("register", "artifact", active)
        self.assertEqual(self.call("locate", "artifact_spec")["path"], str(active))
        self.assertEqual(archived.read_bytes(), active.read_bytes())
        archived_only = archive / "explicit.md"
        archived_only.write_text("# Explicitly registered\n")
        entity = self.call("register", "artifact", archived_only)["entity"]
        self.assertEqual(self.call("locate", entity["id"])["path"], str(archived_only))
        self.call("validate")

    def test_extension_snapshot_types_and_missing_sources(self):
        from trigrams_toolkit.installation.operation_files import file_record
        from trigrams_toolkit.shared.serialization import canonical

        manifest = self.root / ".agents/extensions/example/extension.json"
        manifest.parent.mkdir(parents=True)
        value = {"schemaVersion": 1, "extension": "example", "artifactTypes": ["example:document"],
                 "version": "1.0.0", "resourceRoots": [], "install": []}
        raw = canonical(value)
        manifest.write_bytes(raw)
        record = {"schemaVersion": 2, "stateRevision": 1, "agent": "codex", "platforms": [],
                  "extensions": [{"extension": "example", "version": "1.0.0"}],
                  "managed": [file_record(".agents/extensions/example/extension.json", "example", raw)]}
        (self.root / ".agents/harness.json").write_text(json.dumps(record))
        path = self.docs / "example.md"
        path.write_text("# Example\n")
        self.call("register", "artifact", path, "--kind", "example:document")
        updated = canonical({**value, "artifactTypes": ["example:new"]})
        manifest.write_bytes(updated)
        record["managed"] = [file_record(".agents/extensions/example/extension.json", "example", updated)]
        (self.root / ".agents/harness.json").write_text(json.dumps(record))
        self.call("register", "artifact", path, "--kind", "example:new")
        bad = canonical({**value, "extension": "wrong"})
        manifest.write_bytes(bad)
        self.call("validate", code="identity_conflict")
        manifest.unlink()
        self.call("validate", code="invalid_reference")


class ProjectStateServiceTests(StateFixture):
    def test_registry_write_retry(self):
        path = self.docs / "retry.md"
        path.write_text("# Retry\n")
        invocation = parse_arguments(["register", "artifact", str(path)])
        with patch.dict(os.environ, self.env), patch("trigrams_toolkit.state.service.atomic_write", side_effect=OSError("registry denied")):
            with self.assertRaises(OSError):
                execute(invocation, cwd=self.root)
        identity = path.read_text().split("artifact-id: ")[1].splitlines()[0]
        self.assertFalse(self.state.exists())
        self.assertEqual(self.call("register", "artifact", path)["entity"]["id"], identity)


    def test_lock_timeout_exit_release_and_paths(self):
        lock = acquire_process_lock(self.state)
        started = time.monotonic()
        with self.assertRaises(ProtocolError) as raised:
            acquire_process_lock(self.state, 40)
        self.assertEqual(raised.exception.code, "FILE_LOCK_TIMEOUT")
        self.assertGreaterEqual(time.monotonic() - started, .03)
        lock.release()
        script = "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute('BEGIN IMMEDIATE'); print('locked',flush=True); sys.stdin.read()"
        child = subprocess.Popen([sys.executable, "-c", script, str(lock.lock_file)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.assertEqual(child.stdout.readline().strip(), b"locked")
        child.kill()
        child.communicate(timeout=10)
        acquire_process_lock(self.state).release()
        self.assertEqual(physical_path(self.root / "not/yet"), self.root / "not/yet")
        self.assertEqual(path_key(self.root) == path_key(str(self.root).upper()), os.name == "nt")



if __name__ == "__main__":
    unittest.main()
