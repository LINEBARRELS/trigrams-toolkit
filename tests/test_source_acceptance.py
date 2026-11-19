"""Multi-tool business behavior through source commands on Windows and Linux."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import unittest

import yaml

from acceptance_support import SourceAcceptance, ROOT
from source_fixture import copy_extension, write_skill
from trigrams_toolkit.version import version as package_version


class SourceAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        destination = os.environ.get("TRIGRAMS_ACCEPTANCE_EVIDENCE")
        cls.session = SourceAcceptance(Path(destination) if destination else None, "source-business")
        cls.addClassCleanup(cls.session.close)
        try:
            cls.session.setup()
            cls.base, cls.source = cls.session.base, cls.session.source
            cls.transcript = cls.session.report["commands"]
            cls.session.report["ok"] = True
        except Exception as error:
            cls.session.fail(error)
            raise

    def setUp(self) -> None:
        self.addCleanup(self._record_test)
        self.session.case = self._testMethodName
        self.session.report["phase"] = "business"
        # Windows process creation limits cwd length; the receipt carries the case name.
        self.project = self.base / f"project-{len(self.session.report['tests']) + 1:02d}"
        self.session.configure_project(self.project)

    def _record_test(self) -> None:
        result = self._outcome.result
        failures = [message for test, message in [*result.failures, *result.errors] if test is self]
        self.session.report["tests"].append({"case": self._testMethodName, "ok": not failures, "failures": failures})
        if failures:
            self.session.report["ok"] = False

    def command(self, tool: str, arguments=()) -> list[str]:
        return self.session.command(tool, arguments)

    def test_source_help_without_project_inputs(self) -> None:
        for tool, component in (("plan-toolkit", "plan-toolkit"), ("project-state", "project-state"),
                                ("handbook", "handbook"), ("harness-install", "installation")):
            declarations = json.loads((ROOT / "src/trigrams_toolkit/resources" / {"plan-toolkit": "plan", "project-state": "state"}.get(component, component) / "commands.json").read_text())["commands"]
            paths = {""}
            for item in declarations:
                words = item["name"].split()
                paths.update(" ".join(words[:index]) for index in range(1, len(words) + 1))
            for path in sorted(paths):
                outputs = []
                for flag in ("-h", "--help"):
                    result = self.session.capture(self.command(tool, [*path.split(), flag]), timeout=20,
                                                  cwd=self.session.help_cwd)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertIn(tool, result.stdout)
                    self.assertLessEqual(max(map(len, result.stdout.splitlines())), 100)
                    outputs.append(result.stdout)
                self.assertEqual(*outputs)
            for flag in ("-v", "--version"):
                version = self.session.capture(self.command(tool, [flag]), timeout=20, cwd=self.session.help_cwd)
                self.assertEqual(version.returncode, 0, version.stdout + version.stderr)
                self.assertEqual(version.stdout.strip(), package_version())
        self.assertEqual(list(self.session.help_cwd.iterdir()), [])

    def invoke(self, command: str, arguments=(), data=None, *, ok=True) -> dict:
        self.session.report["phase"] = "business"
        process = self.session.capture(self.command(command, arguments),
                                       json.dumps(data, ensure_ascii=False) if data is not None else None)
        self.assertEqual(process.returncode, 0 if ok else 1, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["ok"], ok, result)
        return result

    def install(self, extensions: list[str], revision: int) -> None:
        for provider in extensions:
            if provider == "validation":
                setup = self.project / ".agents/skills/extension-setup-validation"
                if not setup.exists():
                    write_skill(setup, setup.name)
                    assets = setup / "assets"
                    for folder in ("workbooks", "materials"):
                        shutil.copytree(self.session.extension / folder, assets / folder)
                    raw = json.loads((self.session.extension / "extension.json").read_text(encoding="utf-8"))
                    (assets / "extension.json").write_text(json.dumps(raw), encoding="utf-8")
                    shutil.copytree(self.session.extension / "skills/validation-helper", setup.parent / "validation-helper")
            elif not (self.project / ".agents/skills" / f"extension-setup-{provider}").exists():
                copy_extension(self.project, provider)
        parameters = {"extensions": extensions, "platforms": ["codex", "claude", "pi-web"]}
        result = self.invoke("harness-install", ["install", "preview", "--input", "-"], parameters)
        candidate = result["data"]
        self.assertEqual(Path(candidate["projectRoot"]), self.project)
        self.assertEqual(candidate["conflicts"], [])
        request = {"preview": candidate, "confirmedBy": {"id": "acceptance", "kind": "human"}}
        arguments = ["install", "apply", "--input", "-", "--request-id", f"req_install{revision}",
                     "--expected-revision", str(revision)]
        first = self.invoke("harness-install", arguments, request)
        self.assertEqual(self.invoke("harness-install", arguments, request), first)

    def test_source_commands_share_project_and_minimal_task_state(self) -> None:
        guides = self.invoke("handbook", ["list", "--kind", "workbook"])
        self.assertTrue(guides["resources"])
        self.assertTrue(self.invoke("handbook", ["load", guides["resources"][0]["resourceId"]])["resources"])
        plan = self.project / "docs/plans/example"
        task = plan / "tasks/T01"
        task.mkdir(parents=True)
        (plan / "summary.md").write_text("# Goal\nA minimal delivery.\n", encoding="utf-8")
        (task / "task.md").write_text("# Task\nDeliver the result and verification.\n", encoding="utf-8")
        overview = self.invoke("plan-toolkit", ["inspect", str(plan)])["data"]
        self.assertEqual(overview, {"directory": str(plan), "status": "pending", "tasks": {"T01": {"status": "pending"}}})
        compact = self.invoke("plan-toolkit", ["inspect", str(plan), "T01"])["data"]
        self.assertEqual(compact, {"id": "T01", "path": str(task / "task.md"), "status": "pending"})
        self.assertIn("Deliver the result", Path(compact["path"]).read_text(encoding="utf-8"))
        full = self.invoke("plan-toolkit", ["inspect", str(plan), "--full"])["data"]
        self.assertEqual(full["summary"], str(plan / "summary.md"))
        self.assertEqual(full["tasks"]["T01"]["dependsOn"], [])
        full_task = self.invoke("plan-toolkit", ["inspect", str(plan), "T01", "--full"])["data"]
        self.assertIn("Deliver the result", full_task["body"])
        self.assertEqual(full_task["contents"], ["task.md"])
        self.assertFalse((plan / "plan.json").exists())
        self.assertFalse((plan / ".plan.lock").exists())
        self.invoke("plan-toolkit", ["validate", str(plan), "--sync"])
        self.assertEqual(self.invoke("plan-toolkit", ["get-task", str(plan)])["data"]["ready"][0]["id"], "T01")
        self.invoke("plan-toolkit", ["mark", str(plan), "T01", "doing"])
        self.invoke("plan-toolkit", ["block", str(plan), "T01", "--reason", "Missing input; continue at the adapter"])
        before = (plan / "plan.json").read_bytes()
        blocked = self.invoke("plan-toolkit", ["inspect", str(plan), "T01"])["data"]
        self.assertEqual(blocked["reason"], "Missing input; continue at the adapter")
        self.assertEqual((plan / "plan.json").read_bytes(), before)
        self.invoke("plan-toolkit", ["mark", str(plan), "T01", "done"])
        self.assertEqual(json.loads((plan / "plan.json").read_text())["tasks"]["T01"]["status"], "done")
        self.assertFalse((plan / ".cas").exists())
        self.assertFalse((plan / "submissions").exists())
        self.assertEqual(self.invoke("project-state", ["list"])["data"]["items"], [])
        self.invoke("plan-toolkit", ["cancel", str(plan), "--reason", "Scope closed 空间"])
        self.assertEqual(self.invoke("plan-toolkit", ["inspect", str(plan)])["data"]["status"], "cancelled")

    def test_principle_layout_index_and_sources_through_source_cli(self) -> None:
        self.install(["toolkit-maintenance", "game"], 0)
        documents = self.project / "docs"
        documents.mkdir(exist_ok=True)
        (documents / "resources.json").write_text(json.dumps({
            "schemaVersion": 1, "source": "project", "version": "1.0.0",
            "resourceRoots": ["principles"], "install": []}), encoding="utf-8")
        entry = documents / "principles/programming-design/local-boundary/PRINCIPLE.md"
        entry.parent.mkdir(parents=True)
        entry.write_text("---\ndescription: Local contract boundary.\n---\n# Local judgment\n", encoding="utf-8")
        scopes = self.invoke("handbook", ["scopes", "--kind", "principle"])["scopes"]
        self.assertTrue({"programming", "programming-design", "gameplay-rules", "maintenance"} <= set(scopes))
        for kind in ("principle", "workbook"):
            values = self.invoke("handbook", ["list", "--kind", kind])["resources"]
            self.assertTrue(values)
            self.assertTrue(all(set(item) == {"resourceId", "description"} for item in values))
        programming = self.invoke("handbook", ["list", "--kind", "principle", "--scope", "programming"])["resources"]
        self.assertEqual([item["resourceId"] for item in programming], ["core:principle:programming/define-framework-before-implementation", "core:principle:programming/mark-stubs-and-handoff-notes-in-source"])
        union = self.invoke("handbook", ["list", "--kind", "principle", "--scope", "programming",
                                        "--scope", "programming-design"])["resources"]
        self.assertEqual(len(union), 3)
        loaded = self.invoke("handbook", ["load", "core:workbook:programming-development"])["resources"]
        self.assertTrue(all({"content", "source", "entryPath", "name"} <= item.keys() for item in loaded))
        self.assertGreater(len(loaded), 1)
        self.assertEqual(self.invoke("handbook", ["load", "programming-design/local-boundary"])["resources"][0]["source"], str(documents))
        sources = self.invoke("handbook", ["validate"])["checkedSources"]
        self.assertEqual({Path(path).resolve() for path in sources},
                         {self.session.core, self.project / ".agents/extensions/game",
                          self.project / ".agents/extensions/toolkit-maintenance", documents})
        for name in ("gameplay-design", "game-programming-development"):
            identity = f"game:workbook:{name}"
            workbook = self.project / ".agents/extensions/game/workbooks" / name / "WORKBOOK.md"
            header = yaml.safe_load(workbook.read_text(encoding="utf-8").split("---", 2)[1])
            loaded = self.invoke("handbook", ["load", identity])["resources"]
            self.assertEqual({item["resourceId"] for item in loaded}, {identity, *header["includes"]})
            self.assertTrue(all(Path(item["entryPath"]).is_relative_to(self.project / ".agents/extensions/game")
                                for item in loaded))
        principle = header["includes"][0]
        loaded = self.invoke("handbook", ["load", principle])["resources"]
        self.assertEqual([item["resourceId"] for item in loaded], [principle])

    def test_batch_loading_and_leaf_principles_through_source_cli(self) -> None:
        documents = self.project / "docs"
        documents.mkdir()
        (documents / "resources.json").write_text(json.dumps({
            "schemaVersion": 1, "source": "project", "version": "1.0.0",
            "resourceRoots": ["principles", "workbooks"], "install": []}), encoding="utf-8")
        leaf = "project:principle:scope/leaf"
        framework = "core:principle:programming/define-framework-before-implementation"
        entries = {
            "principles/scope/leaf/PRINCIPLE.md": {"description": "An independent judgment."},
            "workbooks/local-inner/WORKBOOK.md": {"name": "Inner", "description": "Shared method.",
                                                  "includes": [leaf, framework]},
            "workbooks/local-outer/WORKBOOK.md": {"name": "Outer", "description": "Nested method.",
                                                  "includes": ["project:workbook:local-inner", leaf]},
        }
        for relative, header in entries.items():
            path = documents / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("---\n" + json.dumps(header) + "\n---\n# Source body\n", encoding="utf-8")
        loaded = self.invoke("handbook", ["load", "local-outer", "project:workbook:local-inner",
                                         "project:workbook:local-outer", framework])
        self.assertEqual(loaded["selectedIds"], ["project:workbook:local-outer", "project:workbook:local-inner", framework])
        self.assertNotIn("selected", loaded)
        self.assertEqual([item["resourceId"] for item in loaded["resources"]],
                         [leaf, framework, "project:workbook:local-inner", "project:workbook:local-outer"])
        single = self.invoke("handbook", ["load", "scope/leaf"])
        self.assertEqual((single["selected"], single["selectedIds"]), (leaf, [leaf]))
        self.assertEqual(len(single["resources"]), 1)
        missing = self.invoke("handbook", ["load", "local-outer", "missing"], ok=False)
        self.assertEqual(missing["error"]["code"], "invalid_reference")
        self.assertNotIn("resources", missing)
        alias = documents / "principles/programming/define-framework-before-implementation/PRINCIPLE.md"
        alias.parent.mkdir(parents=True)
        alias.write_text("---\ndescription: Another provider.\n---\n# Another judgment\n", encoding="utf-8")
        ambiguous = self.invoke("handbook", ["load", "local-outer", "programming/define-framework-before-implementation"], ok=False)
        self.assertEqual(ambiguous["error"]["code"], "resource_conflict")
        candidates = ambiguous["error"]["conflicts"]
        self.assertEqual(candidates, [framework, framework.replace("core:", "project:")])
        self.assertNotIn("resources", ambiguous)
        self.assertEqual(self.invoke("handbook", ["load", *candidates])["selectedIds"], candidates)
        for includes in ([], [framework]):
            path = documents / "principles/scope/leaf/PRINCIPLE.md"
            path.write_text("---\n" + json.dumps({"description": "Invalid leaf.", "includes": includes}) +
                            "\n---\n# Body\n", encoding="utf-8")
            invalid = self.invoke("handbook", ["load", framework, leaf], ok=False)
            self.assertEqual(invalid["error"]["code"], "invalid_schema")
            self.assertNotIn("resources", invalid)

    def test_registry_ownership_and_relations_through_source_cli(self) -> None:
        self.invoke("project-state", ["register", "module", "Inventory 空间", "--id", "module_inventory"])
        self.invoke("project-state", ["register", "feature", "Slots", "--id", "feature_slots", "--module", "module_inventory"])
        self.invoke("project-state", ["register", "feature", "Sorting", "--id", "feature_sorting", "--module", "module_inventory"])
        documents = self.project / "docs"
        documents.mkdir()
        identities = []
        for name in ("old spec 空间.md", "new spec 空间.md"):
            path = documents / name
            path.write_text("# Inventory Spec\n", encoding="utf-8")
            response = self.invoke("project-state", ["register", "artifact", str(path), "--kind", "core:architecture-spec",
                                  "--module", "module_inventory", "--feature", "feature_slots"])
            identities.append(response["data"]["entity"]["id"])
        extra = []
        for name, features in (("module.md", []), ("sorting.md", ["--feature", "feature_sorting"])):
            path = documents / name
            path.write_text(f"# {name}\n", encoding="utf-8")
            extra.append(self.invoke("project-state", ["register", "artifact", str(path), "--kind", "core:architecture-spec",
                                     "--module", "module_inventory", *features])["data"]["entity"]["id"])
        located = self.invoke("project-state", ["locate", "feature_slots"])["data"]
        self.assertEqual(located, {"id": "feature_slots", "kind": "core:feature", "name": "Slots", "moduleId": "module_inventory"})
        related = self.invoke("project-state", ["related", "feature_slots"])["data"]
        self.assertEqual(set(related), {"items", "relations"})
        self.assertEqual({item["id"] for item in related["items"]}, {"module_inventory", *identities})
        self.assertEqual({Path(item["path"]) for item in related["items"] if "title" in item},
                         {documents / "old spec 空间.md", documents / "new spec 空间.md"})
        module = self.invoke("project-state", ["related", located["moduleId"]])["data"]
        self.assertEqual({item["id"] for item in module["items"]}, {"feature_slots", "feature_sorting", *identities, *extra})
        for item in module["items"]:
            self.assertNotIn("locatorHint", item)
            self.assertNotIn("identityMode", item)
            if "title" in item:
                self.assertTrue(Path(item["path"]).is_file())
        for item in self.invoke("project-state", ["list"])["data"]["items"]:
            self.assertNotIn("path", item)
            self.assertNotIn("locatorHint", item)
            self.assertNotIn("identityMode", item)
        relation = ["relate", identities[1], "core:supersedes", identities[0]]
        self.invoke("project-state", relation)
        self.invoke("project-state", [*relation, "--remove"])
        self.assertTrue(self.invoke("project-state", ["validate"])["data"]["valid"])
        moved = documents / "moved spec 空间.md"
        (documents / "old spec 空间.md").rename(moved)
        self.assertEqual(Path(self.invoke("project-state", ["locate", identities[0]])["data"]["path"]), moved)
        plan = documents / "plans/query-specs"
        task = plan / "tasks/T01/task.md"
        task.parent.mkdir(parents=True)
        (plan / "summary.md").write_text("# Query Spec handoff\n", encoding="utf-8")
        task.write_text("---\nspecs: " + json.dumps([identities[0], "artifact_missing"]) + "\n---\n# Implement\n", encoding="utf-8")
        for options in ([], ["--full"]):
            specs = self.invoke("plan-toolkit", ["inspect", str(plan), "T01", *options])["data"]["specs"]
            self.assertEqual(Path(specs[0]["path"]), moved)
            self.assertEqual(specs[1]["id"], "artifact_missing")
            self.assertEqual(specs[1]["error"]["code"], "invalid_reference")
        moved.unlink()
        self.assertEqual(self.invoke("project-state", ["locate", "feature_slots"])["data"], located)
        failed = self.invoke("project-state", ["related", "feature_slots"], ok=False)
        self.assertEqual(failed["error"]["code"], "invalid_reference")
        specs = self.invoke("plan-toolkit", ["inspect", str(plan), "T01"])["data"]["specs"]
        self.assertEqual([entry["error"]["code"] for entry in specs], ["invalid_reference", "invalid_reference"])
        listed = self.invoke("project-state", ["list", "--kind", "artifact"])["data"]["items"]
        self.assertEqual({item["id"] for item in listed}, {*identities, *extra})

    def test_source_plan_commands_enforce_stub_handoffs(self) -> None:
        plan = self.project / "docs/plans/stubs"
        plan.mkdir(parents=True)
        (plan / "summary.md").write_text(
            "# Goal\n<!-- harness:stub S01 -->\n### S01 Adapter\n"
            "Install the public contract; fill and verify its behavior.\n<!-- /harness:stub S01 -->\n",
            encoding="utf-8")
        declarations = {
            "T01": {"installs": [{"id": "S01", "name": "Adapter"}]},
            "T02": {"fills": [{"id": "S01", "name": "Adapter"}]},
            "T03": {"uses": [{"id": "S01", "name": "Adapter"}]},
            "T04": {"dependsOn": ["T02", "T03"]},
        }
        for identity, fields in declarations.items():
            directory = plan / "tasks" / identity
            directory.mkdir(parents=True)
            header = {"installs": [], "fills": [], "uses": [], **fields}
            (directory / "task.md").write_text(
                "---\n" + json.dumps(header) + "\n---\n# Work\nDeliver verified output.\n", encoding="utf-8")
        self.invoke("plan-toolkit", ["validate", str(plan), "--sync"])
        compact = self.invoke("plan-toolkit", ["inspect", str(plan), "T02"])["data"]
        self.assertEqual(compact["stubs"], {"S01": {"name": "Adapter", "status": "uninstalled"}})
        self.assertTrue(compact["blockers"])
        self.assertNotIn("fills", compact)
        definition = yaml.safe_load(Path(compact["path"]).read_text(encoding="utf-8").split("---", 2)[1])
        self.assertEqual(definition["fills"], [{"id": "S01", "name": "Adapter"}])
        full = self.invoke("plan-toolkit", ["inspect", str(plan), "T02", "--full"])["data"]
        self.assertIn("Install the public contract", full["stubs"]["S01"]["body"])
        self.invoke("plan-toolkit", ["block", str(plan), "--reason", "Pause new work"])
        self.assertEqual(self.invoke("plan-toolkit", ["get-task", str(plan)])["data"]["ready"], [])
        self.invoke("plan-toolkit", ["mark", str(plan), "T01", "doing"], ok=False)
        self.invoke("plan-toolkit", ["mark", str(plan), "doing"])
        before = (plan / "plan.json").read_bytes()
        rejected = self.invoke("plan-toolkit", ["mark", str(plan), "T02", "done"], ok=False)
        self.assertEqual(rejected["error"]["code"], "not_ready")
        self.assertEqual(before, (plan / "plan.json").read_bytes())
        installed = self.invoke("plan-toolkit", ["mark", str(plan), "T01", "done"])
        self.assertEqual(installed["data"]["stubChanges"], {"S01": "installed"})
        ready = self.invoke("plan-toolkit", ["get-task", str(plan)])["data"]["ready"]
        self.assertEqual([task["id"] for task in ready], ["T02", "T03"])
        self.invoke("plan-toolkit", ["mark", str(plan), "T03", "done"])
        filled = self.invoke("plan-toolkit", ["mark", str(plan), "T02", "done"])
        self.assertEqual(filled["data"]["stubChanges"], {"S01": "filled"})
        self.invoke("plan-toolkit", ["mark", str(plan), "T04", "done"])
        self.invoke("plan-toolkit", ["mark", str(plan), "done"])
        self.assertTrue(self.invoke("plan-toolkit", ["validate", str(plan)])["data"]["valid"])

    def test_project_snapshots_and_registry_use_the_same_provider(self) -> None:
        self.install([], 0)
        self.assertFalse((self.project / ".project-state").exists())
        self.assertFalse((self.project / ".agents/skills").exists())
        self.assertFalse((self.project / ".agents/roles").exists())
        for directory, suffix in ((".codex", ".toml"), (".claude", ".md"), (".pi", ".md")):
            for name, skill in (("task_developer", "execute-task"), ("evaluator", "delivery-review")):
                entry = self.project / directory / "agents" / (name + suffix)
                self.assertIn(f"使用 {skill} Skill", entry.read_text(encoding="utf-8"))
                if directory == ".pi":
                    data = yaml.safe_load(entry.read_text(encoding="utf-8").split("---", 2)[1])
                    self.assertIs(data["load_skills"], True)
                    self.assertNotIn("model", data)
        self.install(["toolkit-maintenance", "validation"], 1)
        skill = self.project / ".agents/skills/validation-helper"
        self.assertTrue((skill / "references/check.md").is_file())
        self.assertFalse((self.project / ".agents/extensions/validation").is_symlink())
        self.assertTrue((self.project / ".agents/extensions/validation/extension.json").is_file())
        self.assertFalse((self.project / ".agents/extensions/validation/workbooks").is_symlink())
        self.assertTrue((self.project / ".agents/extensions/validation/materials/manual.md").is_file())
        self.assertFalse((self.project / ".agents/extensions/validation/skills").exists())
        self.assertFalse((self.project / ".agents/extensions/validation/tools").exists())
        self.assertFalse((self.project / ".agents/scripts").exists())
        self.assertTrue((self.project / ".codex/agents/task_developer.toml").is_file())
        self.invoke("handbook", ["validate"])
        document = self.project / "docs/validation.md"
        document.parent.mkdir(exist_ok=True)
        document.write_text("# Validation document\n", encoding="utf-8")
        registered = self.invoke("project-state", ["register", "artifact", str(document), "--kind", "validation:document"])
        self.assertEqual(registered["data"]["entity"]["kind"], "validation:document")
        self.assertEqual(Path(self.invoke("harness-validation")["cwd"]), self.project)
        self.install([], 2)
        self.assertTrue((skill / "SKILL.md").exists())
        self.assertFalse((self.project / ".agents/extensions/validation").exists())
        obsolete = self.project / "obsolete file 空间.txt"
        obsolete.write_text("Archive this exact file", encoding="utf-8")
        archived = self.invoke("harness-install", ["archive", obsolete.name])["data"]
        self.assertFalse(obsolete.exists())
        self.assertEqual((Path(archived["archive"]) / obsolete.name).read_text(), "Archive this exact file")


if __name__ == "__main__":
    unittest.main()
