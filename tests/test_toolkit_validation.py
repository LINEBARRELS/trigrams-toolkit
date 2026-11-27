"""Historical Plan links do not suppress validation of current documents."""
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import tasks
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

    def test_execute_plan_bundles_agile_and_flow_constraints_without_top_level_subskills(self) -> None:
        for mode in ("agile", "flow"):
            for filename in ("guide.md", "dev-constraints.md", "review-constraints.md"):
                with self.subTest(mode=mode, filename=filename):
                    self.assertTrue((ROOT / "skills/execute-plan/references" / mode / filename).is_file())
        for retired in ("execute-task", "delivery-review"):
            self.assertFalse((ROOT / "skills" / retired).exists())
        self.assertFalse((ROOT / "src/trigrams_toolkit/resources/adapters").exists())

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

    def test_finished_agile_plan_links_are_historical_without_plan_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "toolkit.json").write_text(json.dumps({
                "core": {"manifest": str(ROOT / "skills/resources.json")}, "extensions": {}}), encoding="utf-8")
            plan = root / "docs/plans/agile-example"
            (plan / "S01/findings").mkdir(parents=True)
            (plan / "S01/result.md").write_text("[Prior artifact](missing.md)\n", encoding="utf-8")
            (plan / "S01/findings/R01.md").write_text("[Prior log](missing.log)\n", encoding="utf-8")
            prepared = {"ok": True, "resources": 0, "sources": []}
            with patch.object(verify_toolkit, "ROOT", root), patch.object(verify_toolkit, "validate_source_catalog", return_value=prepared):
                for status, expected in (("done", True), ("cancelled", True), ("doing", False),
                                         ("pending", False), ("blocked", False), (None, False)):
                    with self.subTest(status=status):
                        header = f"---\nplan-type: agile\nstatus: {status}\n---\n" if status else "---\nplan-type: agile\n---\n"
                        (plan / "summary.md").write_text(header + "[Prior source](missing.md)\n", encoding="utf-8")
                        result = verify_toolkit.validate()
                        self.assertEqual(result["ok"], expected, result)

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

    def test_release_metadata_check_validates_versions_tag_and_changelog(self) -> None:
        current = tasks.check_release_metadata(ROOT)
        self.assertTrue(current["ok"], current)
        tagged = tasks.check_release_metadata(ROOT, tag=f"v{current['version']}")
        self.assertTrue(tagged["ok"], tagged)
        wrong_tag = tasks.check_release_metadata(ROOT, tag="v9.9.9")
        self.assertFalse(wrong_tag["ok"])
        self.assertTrue(any("Git tag" in issue for issue in wrong_tag["issues"]), wrong_tag)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8")
            (root / "toolkit.json").write_text(json.dumps({
                "version": "1.2.0",
                "core": {"manifest": "skills/resources.json"},
                "extensions": {"ext": {"manifest": "extensions/ext/extension.json"}},
            }), encoding="utf-8")
            (root / "skills").mkdir()
            (root / "skills/resources.json").write_text('{"version": "1.2.3"}', encoding="utf-8")
            (root / "extensions/ext").mkdir(parents=True)
            (root / "extensions/ext/extension.json").write_text('{"version": "1.0.0"}', encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## 1.2.3\n", encoding="utf-8")
            (root / "docs").mkdir()
            cli_changelog = root / "docs/cli-changelog.md"
            cli_changelog.write_text("# CLI changelog\n\n## 1.2.3\n", encoding="utf-8")

            toolkit = tasks.check_release_metadata(root, tag="v1.2.0")
            self.assertEqual(toolkit["target"], "toolkit")
            self.assertEqual(toolkit["version"], "1.2.0")
            self.assertFalse(toolkit["ok"])
            self.assertEqual(len(toolkit["issues"]), 3, toolkit)
            self.assertNotIn("pyproject.toml", toolkit["checked"])

            cli = tasks.check_release_metadata(root, tag="vcli-1.2.3")
            self.assertTrue(cli["ok"], cli)
            self.assertEqual(cli["target"], "cli")
            self.assertEqual(cli["checked"], ["pyproject.toml", "docs/cli-changelog.md"])
            self.assertFalse(tasks.check_release_metadata(root, tag="vcli-1.2.0")["ok"])
            cli_changelog.unlink()
            self.assertFalse(tasks.check_release_metadata(root, tag="vcli-1.2.3")["ok"])

    def test_bump_version_updates_only_selected_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "demo"\nversion = "1.0.0"\n\n[tool.demo]\nversion = "keep"\n',
                encoding="utf-8",
            )
            (root / "toolkit.json").write_text(json.dumps({
                "version": "1.0.0",
                "core": {"manifest": "skills/resources.json"},
                "extensions": {"ext": {"manifest": "extensions/ext/extension.json"}},
            }), encoding="utf-8")
            (root / "skills").mkdir()
            (root / "skills/resources.json").write_text('{"version": "1.0.0"}\n', encoding="utf-8")
            (root / "extensions/ext").mkdir(parents=True)
            (root / "extensions/ext/extension.json").write_text('{"version": "0.9.0"}\n', encoding="utf-8")

            with self.assertRaises(ValueError):
                tasks.bump_version(root, "v2.0.0")

            preview = tasks.bump_version(root, "2.0.0", dry_run=True)
            self.assertTrue(preview["dryRun"])
            manifests = [root / relative for relative in preview["updated"]]
            self.assertEqual(len(manifests), 3)
            self.assertNotIn("pyproject.toml", preview["updated"])
            original = [path.read_bytes() for path in manifests]
            pyproject = root / "pyproject.toml"
            cli_before = pyproject.read_bytes()

            open_file = Path.open

            def deny_extension_write(path, mode="r", *args, **kwargs):
                if path == root / "extensions/ext/extension.json" and mode == "r+":
                    raise PermissionError(path)
                return open_file(path, mode, *args, **kwargs)

            with patch.object(Path, "open", deny_extension_write):
                with self.assertRaises(PermissionError):
                    tasks.bump_version(root, "2.0.0")
            self.assertEqual([path.read_bytes() for path in manifests], original)

            applied = tasks.bump_version(root, "2.0.0")
            self.assertFalse(applied["dryRun"])
            self.assertFalse(applied["changelogReady"])
            self.assertEqual(pyproject.read_bytes(), cli_before)
            toolkit_before = [path.read_bytes() for path in manifests]

            applied = tasks.bump_version(root, "1.1.0", target=tasks.ReleaseTarget.CLI)
            self.assertEqual(applied["updated"], ["pyproject.toml"])
            self.assertEqual([path.read_bytes() for path in manifests], toolkit_before)
            self.assertIn('version = "keep"', pyproject.read_text(encoding="utf-8"))
            for tag in ("v2.0.0", "vcli-1.1.0"):
                with self.subTest(tag=tag):
                    checked = tasks.check_release_metadata(root, tag=tag, check_changelog=False)
                    self.assertTrue(checked["ok"], checked)

    def test_github_workflows_pin_actions_and_scope_oidc_permissions(self) -> None:
        pinned_re = re.compile(r"^[^@]+@[0-9a-f]{40}$")
        workflows = {}
        for name in ("ci.yml", "release.yml"):
            data = yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"))
            workflows[name] = data
            self.assertEqual(data["permissions"], {"contents": "read"})
            for job_name, job in data["jobs"].items():
                for step in job.get("steps", []):
                    uses = step.get("uses")
                    if uses:
                        self.assertRegex(uses, pinned_re, f"{name}:{job_name} action must pin 40-char SHA: {uses}")
        ci_triggers = workflows["ci.yml"].get("on", workflows["ci.yml"].get(True))
        self.assertNotIn("push", ci_triggers)
        ci_changes = workflows["ci.yml"]["jobs"]["check-changes"]["steps"][1]["run"]
        self.assertIn("GITHUB_BASE_REF -eq 'main'", ci_changes)
        self.assertIn("refs/remotes/origin/dev", ci_changes)
        release = workflows["release.yml"]
        release_triggers = release.get("on", release.get(True))
        self.assertEqual(release_triggers["push"]["tags"], ["vcli-*"])
        build_steps = "\n".join(step.get("run", "") for step in release["jobs"]["build"]["steps"])
        self.assertIn("git merge-base --is-ancestor HEAD refs/remotes/origin/main", build_steps)
        self.assertIn('check-release --target cli --tag "$RELEASE_TAG"', build_steps)
        for job_name, job in release["jobs"].items():
            if job_name == "publish-pypi":
                self.assertEqual(job["permissions"], {"id-token": "write"})
                self.assertEqual(job["environment"]["name"], "pypi")
                self.assertEqual(job["needs"], ["build", "verify"])
            else:
                self.assertNotIn("permissions", job)
        self.assertIn('branch" = "main"', (ROOT / ".githooks/pre-commit").read_text(encoding="utf-8"))
        self.assertIn("git merge-base --is-ancestor", (ROOT / ".githooks/pre-push").read_text(encoding="utf-8"))

    def test_extension_setup_skills_disable_model_invocation(self) -> None:
        required_sections = (
            "## 1. 资源结构与依赖检查",
            "## 2. 特定目录路径",
            "## 3. 项目级文档补充与新增",
            "## 4. 存量迁移与归档建议（按需）",
        )
        setup_skills = sorted((ROOT / "extensions").glob("*/skills/extension-setup-*/SKILL.md"))
        self.assertTrue(setup_skills)
        for path in setup_skills:
            with self.subTest(skill=path.parent.name):
                data = verify_toolkit.frontmatter(path)
                self.assertIs(data.get("disable-model-invocation"), True)
                body = path.read_text(encoding="utf-8")
                for heading in required_sections:
                    self.assertIn(heading, body)

    def test_program_guard_setup_principle_references_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "skills/principles/principles/programming-code-metrics/review-code-size-and-nesting/PRINCIPLE.md"
            valid.parent.mkdir(parents=True)
            valid.write_text("---\ndescription: Fixture\n---\n", encoding="utf-8")
            ref_file = root / "skills/program-guard-setup/references/typescript/static.md"
            ref_file.parent.mkdir(parents=True)
            ref_file.write_text(
                "## `core:principle:programming-code-metrics/review-code-size-and-nesting`\n"
                "## `core:principle:programming-code-metrics/missing-rule`\n",
                encoding="utf-8",
            )
            issues = verify_toolkit._validate_guard_references(root)
            self.assertEqual(len(issues), 1, issues)
            self.assertIn("core:principle:programming-code-metrics/missing-rule", issues[0])
