"""Historical Plan links do not suppress validation of current documents."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_toolkit
from trigrams_toolkit.handbook.guides import GuideCatalog


class SourceValidationTests(unittest.TestCase):
    def test_setup_assets_are_allowed_but_runtime_payloads_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills/example"
            (skill / "assets").mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: Fixture\n---\n", encoding="utf-8")
            (skill / "assets/extension.json").write_text("{}", encoding="utf-8")
            self.assertEqual(verify_toolkit._validate_skills(root, [{"skills": "skills"}]), ([], ["example"]))
            for name in ("tool.exe", "extension.json"):
                path = skill / name
                path.write_text("fixture", encoding="utf-8")
                issues, _ = verify_toolkit._validate_skills(root, [{"skills": "skills"}])
                self.assertEqual(len(issues), 1)
                self.assertTrue(path.is_file())
                path.unlink()

    def test_adapters_call_existing_skills_directly(self) -> None:
        self.assertEqual(verify_toolkit._validate_adapters(ROOT), [])
        for platform, suffix in (("codex", ".toml"), ("claude", ".md"), ("pi-web", ".md")):
            for name, skill in (("task_developer", "execute-task"), ("evaluator", "delivery-review")):
                with self.subTest(platform=platform, name=name):
                    source = (ROOT / "src/trigrams_toolkit/resources/adapters" / platform / (name + suffix)).read_text(encoding="utf-8")
                    self.assertIn(f"使用 {skill} Skill", source)
        with patch.object(Path, "is_file", return_value=False):
            self.assertEqual(len(verify_toolkit._validate_adapters(ROOT)), 6)

    def test_pi_web_roles_load_skills_and_inherit_the_model(self) -> None:
        for name in ("task_developer", "evaluator"):
            path = ROOT / "src/trigrams_toolkit/resources/adapters/pi-web" / (name + ".md")
            data = verify_toolkit.frontmatter(path)
            self.assertIs(data["load_skills"], True)
            self.assertNotIn("model", data)
        frontmatter = verify_toolkit.frontmatter
        def without_skills(path):
            data = frontmatter(path)
            return {**data, "load_skills": False} if path.parent.name == "pi-web" else data
        with patch.object(verify_toolkit, "frontmatter", side_effect=without_skills):
            self.assertCountEqual(verify_toolkit._validate_adapters(ROOT), [
                "Pi Web role must load Skills: evaluator.md",
                "Pi Web role must load Skills: task_developer.md",
            ])

    def test_finished_plan_links_are_historical_but_active_links_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "toolkit.json").write_text(json.dumps({
                "core": {"manifest": str(ROOT / "skills/resources.json")}, "extensions": {}}), encoding="utf-8")
            plan = root / "docs/plans/example"
            plan.mkdir(parents=True)
            (plan / "summary.md").write_text("[Prior source](missing.md)\n", encoding="utf-8")
            prepared = {"ok": True, "resources": 0, "sources": []}
            with patch.object(verify_toolkit, "ROOT", root), patch.object(verify_toolkit, "validate_source_catalog", return_value=prepared):
                for status in ("done", "cancelled", "doing", "pending", "blocked"):
                    with self.subTest(status=status):
                        (plan / "plan.json").write_text(json.dumps({"status": status}), encoding="utf-8")
                        result = verify_toolkit.validate()
                        self.assertEqual(result["ok"], status in ("done", "cancelled"), result)
                (plan / "plan.json").write_text('{"status": "done"}', encoding="utf-8")
                (root / "README.md").write_text("[Current source](missing.md)\n", encoding="utf-8")
                result = verify_toolkit.validate()
                self.assertFalse(result["ok"])
                self.assertIn("README.md", result["issues"][0])

    def test_validation_discovers_one_catalog_and_keeps_its_counts(self) -> None:
        with patch.object(GuideCatalog, "discover", wraps=GuideCatalog.discover) as discover:
            result = verify_toolkit.validate()
        self.assertTrue(result["ok"], result)
        self.assertEqual(discover.call_count, 1)
        self.assertGreater(result["resources"], 0)
        self.assertEqual(result["sources"], ["core", "game", "toolkit-maintenance"])

    def test_source_walk_prunes_local_roots_and_nested_caches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            maintained = {"README.md", "skills/new/SKILL.md", "src/trigrams_toolkit/new.py", "docs/new.md", ".github/new.yml"}
            excluded = {"core/new.py", "scratch/report.md", ".smell-check/report.md", ".tmp-local/new.py",
                        "docs/.cache/report.md", "docs/.tmp-local/new.py",
                        "src/node_modules/example/new.py", "tests/__pycache__/report.md",
                        "docs/.pi/agents/personal.md"}
            for name in maintained | excluded:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")
            visited = []
            walk = verify_toolkit.os.walk

            def track(path):
                for current, children, files in walk(path):
                    visited.append(Path(current).relative_to(root).as_posix())
                    yield current, children, files

            with patch.object(verify_toolkit.os, "walk", side_effect=track):
                found = {path.relative_to(root).as_posix() for path in verify_toolkit.source_files(root)}
            self.assertEqual(found, maintained)
            self.assertFalse(any(part in verify_toolkit.IGNORED or part.startswith(".tmp")
                                 for name in visited for part in Path(name).parts), visited)
            self.assertNotIn("scratch", visited)
            self.assertNotIn(".smell-check", visited)

    def test_new_maintenance_files_fail_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "toolkit.json").write_text('{"core": {}, "extensions": {}}', encoding="utf-8")
            for name, text in (("docs/new.md", "[Missing](absent.md)"),
                               ("scripts/new.py", "def broken(:"),
                               ("scratch/report.md", "[Ignored](absent.md)")):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            prepared = {"ok": True, "resources": 17, "sources": ["fixture"]}
            with patch.object(verify_toolkit, "ROOT", root), patch.object(verify_toolkit, "validate_source_catalog", return_value=prepared):
                result = verify_toolkit.validate()
            self.assertFalse((root / ".git").exists())
            self.assertFalse(result["ok"])
            self.assertEqual(len(result["issues"]), 2, result)
            self.assertTrue(any(str(Path("docs/new.md")) in issue for issue in result["issues"]), result)
            self.assertTrue(any("new.py" in issue for issue in result["issues"]), result)
            self.assertEqual(result["resources"], 17)
            self.assertEqual(result["sources"], ["fixture"])
