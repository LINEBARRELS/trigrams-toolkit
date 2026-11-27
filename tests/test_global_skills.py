"""Offline previews and global dependency installation on confirmed apply."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from source_fixture import ROOT, profile_environment, write_skill
from trigrams_toolkit.installation.installation_candidate import build_candidate
from trigrams_toolkit.installation.installation_service import apply_installation
from trigrams_toolkit.installation.operation_files import file_record
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.shared.serialization import canonical, read_json


class GlobalDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        (ROOT / ".tmp").mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="global-skills-", dir=ROOT / ".tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.profile = self.root / "profile"
        self.project = self.root / "project"
        self.project.mkdir()
        self.record = self.project / ".agents/harness.json"
        self.receipt = self.project / ".harness/previous/receipt.json"
        self.schemas = SchemaCatalog(schema_paths())
        self.calls = []
        self.failed_skill = None
        self.no_op = False
        for settings in (
            patch.dict(os.environ, profile_environment(self.profile)),
            patch("trigrams_toolkit.installation.global_skills.shutil.which", return_value="npx"),
            patch("trigrams_toolkit.installation.global_skills.run", side_effect=self.vercel),
        ):
            settings.start()
            self.addCleanup(settings.stop)

    def preview(self, **parameters):
        return build_candidate(self.project, {**parameters}, self.schemas).preview

    def add_extension(self, name: str = "extra") -> Path:
        setup = self.project / ".agents/skills" / f"extension-setup-{name}"
        write_skill(setup, setup.name)
        assets = setup / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        (assets / "extension.json").write_bytes(canonical({
            "schemaVersion": 1, "extension": name, "version": "1.0.0", "resourceRoots": [], "install": [],
        }))
        return assets

    def apply(self, preview, *, root=None, revision=None):
        request = {"preview": preview, "confirmedBy": {"id": "fixture", "kind": "human"}}
        return apply_installation(self.project if root is None else root, request, self.schemas,
                                  "req_" + preview["operationId"],
                                  preview["baseRevision"] if revision is None else revision)

    def directory(self, name: str, agent: str = "codex") -> Path:
        return self.profile / (".claude/skills" if agent == "claude-code" else ".agents/skills") / name

    def present(self, name: str, agent: str = "codex") -> None:
        write_skill(self.directory(name, agent), name)

    def vercel(self, command, **kwargs):
        name = command[command.index("--skill") + 1]
        agent = command[command.index("--agent") + 1]
        self.calls.append((agent, name))
        package, source = {"answer-me-with-html": ("skills", "QingYunA/answer-me-with-html"),
                           "smell-check": ("skills", "Zhen-Bo/smell-check")}[name]
        self.assertEqual(command, ["npx", "-y", package, "add", source, "--skill", name,
                                   "--agent", agent, "--global", "--copy", "--yes"])
        self.assertEqual(kwargs["cwd"], self.project)
        if self.failed_skill == name:
            return subprocess.CompletedProcess(command, 1, "", "fixture install failed")
        if not self.no_op:
            self.present(name, agent)
        return subprocess.CompletedProcess(command, 0, "", "")

    def assert_failure(self, code, preview, **settings):
        with self.assertRaises(ProtocolError) as raised:
            self.apply(preview, **settings)
        self.assertEqual(raised.exception.code, code, str(raised.exception))
        return raised.exception

    def test_preview_is_offline_and_initial_apply_fills_only_missing_skills(self):
        with patch("trigrams_toolkit.installation.global_skills.skill_directory",
                   side_effect=AssertionError("preview dependency check")):
            preview = self.preview()
        self.assertFalse((self.project / ".harness").exists())
        self.assertFalse(self.record.exists())
        self.present("answer-me-with-html")
        result = self.apply(preview)
        self.assertEqual(self.calls, [("codex", "smell-check")])
        self.assertEqual(read_json(self.record)["extensions"], [])
        self.calls.clear()
        (self.directory("smell-check") / "SKILL.md").unlink()
        with patch("trigrams_toolkit.installation.global_skills.skill_directory",
                   side_effect=AssertionError("replay dependency check")):
            self.assertEqual(self.apply(preview), result)
        self.assertFalse(self.apply(self.preview())["changed"])
        self.assertEqual(self.calls, [("codex", "smell-check")])
        with patch("trigrams_toolkit.installation.global_skills.shutil.which",
                   side_effect=AssertionError("both dependencies already installed")):
            self.apply(self.preview())

    def test_dependencies_follow_the_confirmed_agent_and_global_scope(self):
        self.present("answer-me-with-html", "claude-code")
        self.present("smell-check", "codex")
        write_skill(self.project / ".claude/skills/smell-check", "smell-check")
        self.apply(self.preview(agent="claude-code"))
        self.assertEqual(self.calls, [("claude-code", "smell-check")])
        self.assertEqual(read_json(self.record)["agent"], "claude-code")

    def test_failed_install_preserves_project_and_partial_success_is_reused(self):
        self.present("answer-me-with-html")
        self.present("smell-check")
        self.add_extension("extra")
        self.apply(self.preview(extensions=[]))
        before = {path: path.read_bytes() for path in (self.record, self.receipt)}
        for name in ("answer-me-with-html", "smell-check"):
            (self.directory(name) / "SKILL.md").unlink()
        self.failed_skill = "smell-check"
        preview = self.preview(extensions=["extra"])
        error = self.assert_failure("dependency_failed", preview)
        self.assertIn("smell-check for codex: fixture install failed", str(error))
        self.assertEqual(self.calls, [("codex", "answer-me-with-html"), ("codex", "smell-check")])
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        self.assertFalse((self.project / ".agents/extensions/extra").exists())
        self.failed_skill = None
        self.calls.clear()
        self.assertEqual(self.apply(preview)["stateRevision"], 2)
        self.assertEqual(self.calls, [("codex", "smell-check")])
        self.assertEqual(read_json(self.record)["extensions"], [{"extension": "extra", "version": "1.0.0"}])

    def test_invalid_root_revision_and_local_conflict_precede_dependency_install(self):
        self.add_extension("extra")
        preview = self.preview(extensions=["extra"])
        with patch("trigrams_toolkit.installation.global_skills.skill_directory",
                   side_effect=AssertionError("invalid apply dependency check")):
            self.assert_failure("basis_changed", preview, root=self.root)
            self.assertFalse((self.root / ".harness").exists())
            self.assert_failure("revision_conflict", preview, revision=1)
            owned = self.project / ".agents/extensions/extra/extension.json"
            owned.parent.mkdir(parents=True)
            owned.write_bytes(b"User-owned file")
            self.assert_failure("basis_changed", preview)
            self.assert_failure("local_modification", self.preview(extensions=["extra"]))
            self.assertEqual(owned.read_bytes(), b"User-owned file")
        self.assertFalse(self.record.exists())

    def test_tool_unavailable_and_success_without_installation(self):
        preview = self.preview()
        with patch("trigrams_toolkit.installation.global_skills.shutil.which", return_value=None):
            error = self.assert_failure("missing_capability", preview)
            self.assertIn("answer-me-with-html for codex: npx is unavailable", str(error))
        self.no_op = True
        error = self.assert_failure("dependency_failed", preview)
        self.assertIn("answer-me-with-html for codex: Installation did not create", str(error))
        self.assertFalse(self.record.exists())
        self.assertFalse(self.receipt.exists())

    def test_pure_uninstall_and_legacy_adapter_retirement_remain_offline(self):
        self.add_extension("extra")
        self.apply(self.preview(extensions=["extra"]))
        for name in ("answer-me-with-html", "smell-check"):
            (self.directory(name) / "SKILL.md").unlink()
        self.calls.clear()
        with patch("trigrams_toolkit.installation.global_skills.skill_directory",
                   side_effect=AssertionError("uninstall dependency check")):
            self.assertTrue(self.apply(self.preview(extensions=[]))["changed"])
        self.assertEqual(read_json(self.record)["extensions"], [])
        self.assertFalse((self.project / ".agents/extensions/extra").exists())
        self.assertFalse(self.calls)

        adapter_path = ".codex/agents/task_developer.toml"
        adapter = self.project / adapter_path
        adapter.parent.mkdir(parents=True)
        raw = b'name = "task_developer"\n'
        adapter.write_bytes(raw)
        self.record.write_bytes(canonical({
            "schemaVersion": 2,
            "stateRevision": 2,
            "agent": "codex",
            "extensions": [],
            "platforms": ["codex"],
            "managed": [file_record(adapter_path, "core", raw)],
        }))
        with patch("trigrams_toolkit.installation.global_skills.skill_directory",
                   side_effect=AssertionError("legacy cleanup dependency check")):
            self.assertTrue(self.apply(self.preview())["changed"])
        self.assertFalse(adapter.exists())
        self.assertNotIn("platforms", read_json(self.record))
        self.assertFalse(self.calls)
