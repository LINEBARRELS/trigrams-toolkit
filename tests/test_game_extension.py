"""Game guides, linked installation and gameplay identity handoffs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import ClassVar, Final
import unittest

from source_fixture import source_commands

ROOT: Final = Path(__file__).resolve().parents[1]
GAME: Final = ROOT / "extensions/game"
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.handbook.source_catalog import source_packages
from source_fixture import copy_extension, offline_global_skills

INCLUDES: Final = {
    "game:workbook:gameplay-design": (
        "game:principle:gameplay-experience/align-player-goals-with-target-experience",
        "game:principle:gameplay-experience/let-loop-results-shape-later-decisions",
        "game:principle:gameplay-composition/make-each-spec-describe-complete-operation",
        "game:principle:gameplay-rules/define-rule-entities-and-legal-state-domains",
        "game:principle:gameplay-rules/make-state-transition-results-decidable",
        "game:principle:gameplay-rules/specify-outcomes-when-conditions-fail",
        "game:principle:gameplay-rules/derive-acceptance-from-owned-gameplay-rules",
    ),
    "game:workbook:game-programming-development": (
        "game:principle:gameplay-rules/derive-acceptance-from-owned-gameplay-rules",
        "game:principle:runtime-evidence/bind-runtime-evidence-to-version-and-environment",
        "game:principle:runtime-evidence/make-gameplay-validation-scenarios-reproducible",
        "game:principle:runtime-evidence/choose-evidence-that-can-support-the-claim",
        "game:principle:runtime-evidence/bound-conclusions-to-verified-acceptance",
    ),
    "game:principle:gameplay-experience/align-player-goals-with-target-experience": (),
    "game:principle:gameplay-experience/let-loop-results-shape-later-decisions": (),
    "game:principle:gameplay-experience/give-choices-understandable-costs-and-consequences": (),
    "game:principle:gameplay-experience/match-challenge-to-player-readiness": (),
    "game:principle:gameplay-experience/give-repeated-actions-an-experience-purpose": (),
    "game:principle:gameplay-experience/reveal-decision-information-at-the-needed-time": (),
    "game:principle:gameplay-experience/make-action-outcomes-recognizable": (),
    "game:principle:gameplay-experience/preserve-response-options-under-pressure": (),
    "game:principle:gameplay-experience/tune-rewards-and-penalties-to-experience-rhythm": (),
    "game:principle:gameplay-experience/diagnose-playtest-deviations-from-observed-behavior": (),
    "game:principle:gameplay-rules/define-rule-entities-and-legal-state-domains": (),
    "game:principle:gameplay-rules/keep-state-invariants-and-derived-values-consistent": (),
    "game:principle:gameplay-rules/make-state-transition-results-decidable": (),
    "game:principle:gameplay-rules/group-complete-effects-by-settlement": (),
    "game:principle:gameplay-rules/specify-outcomes-when-conditions-fail": (),
    "game:principle:gameplay-rules/define-boundaries-that-change-gameplay-rulings": (),
    "game:principle:gameplay-rules/align-player-input-and-feedback-with-rules": (),
    "game:principle:gameplay-rules/derive-acceptance-from-owned-gameplay-rules": (),
    "game:principle:gameplay-composition/make-each-spec-describe-complete-operation": (),
    "game:principle:gameplay-composition/keep-cross-mechanic-interactions-in-bridge-specs": (),
    "game:principle:gameplay-composition/preserve-shared-mechanic-contracts-in-composition": (),
    "game:principle:gameplay-composition/record-only-direct-acyclic-spec-dependencies": (),
    "game:principle:gameplay-composition/trace-mechanic-changes-through-actual-consumers": (),
    "game:principle:runtime-evidence/bind-runtime-evidence-to-version-and-environment": (),
    "game:principle:runtime-evidence/make-gameplay-validation-scenarios-reproducible": (),
    "game:principle:runtime-evidence/choose-evidence-that-can-support-the-claim": (),
    "game:principle:runtime-evidence/bound-conclusions-to-verified-acceptance": (),
    "game:principle:runtime-evidence/judge-performance-against-established-budgets": (),
    "game:principle:runtime-evidence/reassess-evidence-when-runtime-materials-change": (),
}


class GameContentTests(unittest.TestCase):
    def test_guides_are_classified_and_load_their_principles(self) -> None:
        catalog = GuideCatalog.discover([p for p in source_packages(ROOT, SchemaCatalog(schema_paths()))
                                         if p.manifest.get("extension") == "game"], ROOT, SchemaCatalog(schema_paths()))
        self.assertTrue(catalog.validate()["ok"])
        self.assertEqual(set(catalog.validate()["resourceIds"]), set(INCLUDES))
        self.assertEqual(catalog.scopes()["scopes"], ["game", "gameplay", "gameplay-composition", "gameplay-experience", "gameplay-rules", "runtime-evidence"])
        for scope, count in (("game", 1), ("gameplay", 1), ("gameplay-composition", 5),
                             ("gameplay-experience", 10), ("gameplay-rules", 8), ("runtime-evidence", 6)):
            resources = catalog.list(scopes=[scope])["resources"]
            self.assertEqual(len(resources), count)
            self.assertTrue(all(catalog.resolve(item["resourceId"]).scope == scope for item in resources))
        for identity, includes in INCLUDES.items():
            with self.subTest(identity=identity):
                guide = catalog.resolve(identity)
                self.assertTrue(guide.header["description"].strip())
                self.assertEqual(tuple(guide.header.get("includes", ())), includes)
                loaded = catalog.load(identity)["resources"]
                self.assertEqual({item["resourceId"] for item in loaded}, {identity, *includes})
                for item in loaded:
                    expected = catalog.resolve(item["resourceId"]).path.read_text(encoding="utf-8-sig")
                    self.assertEqual(item["content"], expected)

    def test_retained_skills_and_local_references_are_reachable(self) -> None:
        skills = {path.name for path in (GAME / "skills").iterdir() if (path / "SKILL.md").is_file()}
        self.assertEqual(skills, {"game-designer", "art-designer", "extension-setup-game"})
        for path in GAME.rglob("*.md"):
            for link in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if ":" in link or link.startswith("#"):
                    continue
                self.assertTrue((path.parent / link.split("#", 1)[0]).is_file(), f"{path}: {link}")


class GameProjectTests(unittest.TestCase):
    transcript: ClassVar[list[dict]] = []

    @classmethod
    def tearDownClass(cls) -> None:
        destination = os.environ.get("HARNESS_GAME_EVIDENCE")
        if destination:
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(cls.transcript, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def setUp(self) -> None:
        (ROOT / ".tmp").mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="game-extension-", dir=ROOT / ".tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.environment = {**os.environ, **offline_global_skills(self.root),
                            "PYTHONDONTWRITEBYTECODE": "1"}
        self.commands = source_commands()
        copy_extension(self.project, "game")
        self.install_game()

    def invoke(self, tool: str, *arguments: str, data: dict | None = None, ok: bool = True) -> dict:
        process = subprocess.run(self.commands[tool] + list(arguments), cwd=self.project, env=self.environment,
                                 input=json.dumps(data) if data is not None else None, capture_output=True,
                                 encoding="utf-8", timeout=60)
        self.assertTrue(process.stdout, process.stderr)
        response = json.loads(process.stdout)
        self.transcript.append({"case": self._testMethodName, "tool": tool, "arguments": arguments,
                                "exitCode": process.returncode, "response": response})
        self.assertEqual(process.returncode, 0 if ok else 1, process.stdout + process.stderr)
        self.assertEqual(response["ok"], ok, response)
        return response

    def install_game(self) -> None:
        parameters = {"extensions": ["game"], "platforms": ["codex", "claude"]}
        preview = self.invoke("harness-install", "install", "preview", "--input", "-", data=parameters)["data"]
        self.assertEqual(preview["conflicts"], [])
        request = {"preview": preview, "confirmedBy": {"id": "game-extension-test", "kind": "human"}}
        result = self.invoke("harness-install", "install", "apply", "--input", "-", "--request-id", "req_game",
                             "--expected-revision", "0", data=request)
        self.assertEqual(result["data"]["phase"], "committed")

    def test_installation_and_project_guide_queries(self) -> None:
        for relative in ("extension.json", "principles", "workbooks"):
            installed = self.project / ".agents/extensions/game" / relative
            self.assertFalse(installed.is_symlink())
            self.assertTrue(installed.exists())
        for name in ("game-designer", "art-designer", "extension-setup-game"):
            installed = self.project / ".agents/skills" / name
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertFalse((self.project / ".claude/skills" / name).exists())
        for retired in ("roles", "contracts", "scripts"):
            self.assertFalse((self.project / ".agents/extensions/game" / retired).exists())
        self.assertFalse((self.project / ".agents/scripts").exists())
        checked = self.invoke("handbook", "validate")
        self.assertEqual({Path(path).resolve() for path in checked["checkedSources"]}, {self.project / ".agents/extensions/game"})
        self.assertEqual(set(checked["resourceIds"]), set(INCLUDES))
        self.assertEqual(self.invoke("handbook", "scopes")["scopes"], ["game", "gameplay", "gameplay-composition", "gameplay-experience", "gameplay-rules", "runtime-evidence"])
        for scope, count in (("game", 1), ("gameplay", 1), ("gameplay-composition", 5),
                             ("gameplay-experience", 10), ("gameplay-rules", 8), ("runtime-evidence", 6)):
            self.assertEqual(len(self.invoke("handbook", "list", "--scope", scope)["resources"]), count)
        identity = "game:workbook:game-programming-development"
        loaded = self.invoke("handbook", "load", identity)
        self.assertEqual({item["resourceId"] for item in loaded["resources"]}, {identity, *INCLUDES[identity]})

    def register_spec(self, path: Path) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem}\n\nGameplay identity fixture.\n", encoding="utf-8")
        result = self.invoke("project-state", "register", "artifact", str(path), "--kind", "game:gameplay-spec")
        self.assertEqual(result["data"]["entity"]["kind"], "game:gameplay-spec")
        return result["data"]["entity"]["id"]

    def inspect_implementation_plan(self, identities: list[str]) -> list[dict]:
        plan = self.project / "docs/plans/implement-gameplay"
        task = plan / "tasks/T01/task.md"
        task.parent.mkdir(parents=True)
        (plan / "summary.md").write_text("# Implement the selected gameplay\n", encoding="utf-8")
        task.write_text("---\nspecs: " + json.dumps(identities) + "\n---\n# Implement\n"
                        "Use game:workbook:game-programming-development and deliver the runnable slice.\n",
                        encoding="utf-8")
        self.invoke("plan-toolkit", "validate", str(plan), "--sync")
        return self.invoke("plan-toolkit", "inspect", str(plan), "T01")["data"]["specs"]

    def test_spec_identity_composition_and_implementation_handoff(self) -> None:
        old = self.project / "docs/gameplay-specs/care.md"
        shared = self.register_spec(old)
        paths = {name: self.project / "docs/gameplays" / f"{name}.md" for name in ("farm", "harvest", "market-bridge")}
        identities = {name: self.register_spec(path) for name, path in paths.items()}
        renamed = self.project / "docs/gameplays/growth-care.md"
        old.rename(renamed)
        updated = self.invoke("project-state", "register", "artifact", str(renamed), "--kind", "game:gameplay-spec")
        self.assertEqual(updated["data"]["entity"]["id"], shared)
        self.assertIn(f"artifact-id: {shared}", renamed.read_text(encoding="utf-8"))
        located = self.invoke("project-state", "locate", shared)
        self.assertEqual(Path(located["data"]["path"]).resolve(), renamed)
        self.assertEqual(set(located["data"]), {"id", "kind", "title", "featureIds", "path"})
        self.assertEqual(located["data"]["featureIds"], [])
        for owner in (identities["farm"], identities["market-bridge"]):
            for child in (shared, identities["harvest"]):
                self.invoke("project-state", "relate", owner, "game:composes", child)
        incoming = self.invoke("project-state", "related", shared, "--direction", "incoming")["data"]
        consumers = {identities["farm"], identities["market-bridge"]}
        self.assertEqual({item["id"] for item in incoming["items"]}, consumers)
        self.assertEqual({edge["from"] for edge in incoming["relations"]}, consumers)
        self.assertEqual(set(incoming), {"items", "relations"})
        self.assertEqual({Path(item["path"]).resolve() for item in incoming["items"]},
                         {paths["farm"], paths["market-bridge"]})
        for item in incoming["items"]:
            self.assertEqual(set(item), {"id", "kind", "title", "featureIds", "path"})
        rejected = self.invoke("project-state", "relate", shared, "game:composes", identities["farm"], ok=False)
        self.assertEqual(rejected["error"]["code"], "invalid_reference")
        self.assertIn("cycle", rejected["error"]["message"])
        outgoing = self.invoke("project-state", "related", shared, "--direction", "outgoing")
        self.assertEqual(outgoing["data"], {"items": [], "relations": []})
        specs = self.inspect_implementation_plan([shared, identities["farm"], identities["market-bridge"]])
        self.assertEqual({entry["id"] for entry in specs}, {shared, *consumers})
        self.assertEqual({Path(entry["path"]).resolve() for entry in specs},
                         {renamed, paths["farm"], paths["market-bridge"]})


if __name__ == "__main__":
    unittest.main()
