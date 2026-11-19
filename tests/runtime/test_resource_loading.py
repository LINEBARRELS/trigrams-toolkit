"""The guide CLI uses one project catalog for discovery and loading."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from unittest.mock import patch

from support import RuntimeCase, write_json
from trigrams_toolkit.handbook.cli import main as global_main


class GuideCliTests(RuntimeCase):
    def cli(self, *arguments: str) -> tuple[int, dict | str]:
        stream = io.StringIO()
        with redirect_stdout(stream), \
                patch("trigrams_toolkit.handbook.cli.discover_project_root", return_value=self.project), \
                patch("trigrams_toolkit.handbook.cli.sources_for_project", return_value=self.catalog.packages):
            code = global_main(list(arguments))
        try:
            return code, json.loads(stream.getvalue())
        except json.JSONDecodeError:
            return code, stream.getvalue()

    def test_commands_share_the_project_catalog(self) -> None:
        code, output = self.cli("scopes", "--kind", "workbook")
        self.assertEqual((code, output), (0, {"ok": True, "scopes": ["programming", "research"]}))
        code, output = self.cli("list", "--kind", "workbook",
                                "--scope", "research", "--scope", "programming")
        self.assertEqual(code, 0, output)
        self.assertEqual(len(output["resources"]), 2)
        code, output = self.cli("load", "research")
        self.assertEqual(code, 0, output)
        self.assertEqual(output["selected"], "core:workbook:research")
        self.assertEqual(output["selectedIds"], [output["selected"]])
        code, output = self.cli("validate")
        self.assertEqual(code, 0, output)
        self.assertEqual(len(output["resourceIds"]), 3)

    def test_batch_uses_one_catalog_and_deduplicates_inputs_and_dependencies(self) -> None:
        self.guide("programming", "workbook", {"includes": ["core:workbook:research"]})
        self.refresh()
        with patch("trigrams_toolkit.handbook.cli.GuideCatalog.discover", wraps=self.catalog.discover) as discover, \
                patch("trigrams_toolkit.handbook.cli.discover_project_root", return_value=self.project) as project_root:
            stream = io.StringIO()
            with redirect_stdout(stream), \
                    patch("trigrams_toolkit.handbook.cli.sources_for_project", return_value=self.catalog.packages):
                code = global_main(["load", "programming", "core:workbook:research", "programming"])
        output = json.loads(stream.getvalue())
        self.assertEqual(code, 0, output)
        project_root.assert_called_once_with()
        discover.assert_called_once()
        self.assertEqual(output["selectedIds"], ["core:workbook:programming", "core:workbook:research"])
        self.assertNotIn("selected", output)
        self.assertEqual([item["resourceId"] for item in output["resources"]],
                         ["core:principle:scale/limits", "core:workbook:research", "core:workbook:programming"])
        code, output = self.cli("load", "research", "core:workbook:research")
        self.assertEqual(code, 0, output)
        self.assertEqual(output["selectedIds"], ["core:workbook:research"])
        self.assertNotIn("selected", output)

    def test_batch_failures_are_atomic_and_ambiguous_candidates_can_be_retried(self) -> None:
        extra = self.root / "extra"
        write_json(extra / "resources.json", {**self.manifest, "source": "aaa", "resourceRoots": ["guides"]})
        path = extra / "guides/research/WORKBOOK.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: Other\ndescription: Other provider.\n---\nBody.\n", encoding="utf-8")
        self.catalog = self.catalog.discover([self.package, extra], self.project, self.schemas)
        code, output = self.cli("load", "programming", "research")
        self.assertEqual((code, output["error"]["code"]), (1, "resource_conflict"))
        self.assertIn("research", output["error"]["message"])
        self.assertNotIn("resources", output)
        candidates = output["error"]["conflicts"]
        self.assertEqual(candidates, ["aaa:workbook:research", "core:workbook:research"])
        code, output = self.cli("load", *candidates)
        self.assertEqual(code, 0, output)
        self.assertEqual(output["selectedIds"], candidates)
        self.guide("programming", "workbook", {"includes": ["core:workbook:research"]})
        self.guide("research", "workbook", {"includes": ["core:workbook:programming"]})
        for ids in (("core:workbook:research", "missing"), ("aaa:workbook:research", "programming")):
            code, output = self.cli("load", *ids)
            self.assertEqual((code, output["error"]["code"]), (1, "invalid_reference"))
            self.assertNotIn("resources", output)
        self.guide("programming", "workbook", {"includes": ["core:principle:scale/missing"]})
        code, output = self.cli("load", "aaa:workbook:research", "programming")
        self.assertEqual((code, output["error"]["code"]), (1, "invalid_reference"))
        self.assertNotIn("resources", output)
        for includes in ([], ["core:principle:scale/limits"]):
            self.guide("scale/limits", "principle", {"includes": includes})
            code, output = self.cli("load", "aaa:workbook:research", "core:principle:scale/limits")
            self.assertEqual((code, output["error"]["code"]), (1, "invalid_schema"))
            self.assertNotIn("resources", output)

    def test_removed_commands_and_arguments_are_rejected(self) -> None:
        cases = [("providers",), ("history",), ("load",), ("load", "--id", "research"),
                 ("load", "research", "--kind", "workbook"),
                 ("load", "research", "--scope", "research"),
                 ("list", "--kind", "skill"), ("list", "--global-core"),
                 ("--config", "projects.json", "scopes"),
                 ("validate", "--project", str(self.project)),
                 ("validate", "--init-root", str(self.project))]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                code, output = self.cli(*arguments)
                self.assertEqual((code, output["error"]["code"]), (1, "invalid_arguments"))

    def test_source_selection_is_rejected(self) -> None:
        for command in (("scopes",), ("list",), ("load", "research"), ("validate",)):
            code, output = self.cli(*command, "--source", str(self.package))
            self.assertEqual((code, output["error"]["code"]), (1, "invalid_arguments"))

    def test_help_and_version_do_not_load_project_context(self) -> None:
        for arguments in (("--help",), ("scopes", "--help"), ("list", "--help"), ("load", "--help"), ("-v",), ("--version",)):
            code, output = self.cli(*arguments)
            self.assertEqual(code, 0, output)
            self.assertIsInstance(output, str)
            self.assertNotIn("--source", output)
        with redirect_stdout(io.StringIO()), patch("trigrams_toolkit.handbook.cli.discover_project_root", side_effect=AssertionError("project IO")):
            self.assertEqual(global_main(["load", "--help"]), 0)

    def test_version_uses_the_current_toolkit_regardless_of_external_home(self) -> None:
        from support import ROOT
        from trigrams_toolkit.version import version
        expected = version()
        path = self.root / "tools/deployment.json"
        write_json(path, {"schemaVersion": 1, "version": "9.9.9"})
        code, output = self.cli("--version")
        self.assertEqual((code, output.strip()), (0, expected))
        path.write_text("invalid external deployment JSON", encoding="utf-8")
        code, output = self.cli("--version")
        self.assertEqual((code, output.strip()), (0, expected))
