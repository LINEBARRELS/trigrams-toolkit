"""The maintenance extension exposes maintenance-extension workbook and atomic principles."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.handbook.source_catalog import source_packages


class MaintenanceContentTests(unittest.TestCase):
    def test_extension_workbook_and_atomic_principles_budget(self) -> None:
        catalog = GuideCatalog.discover([p for p in source_packages(ROOT, SchemaCatalog(schema_paths()))
                                         if p.manifest.get("extension") == "toolkit-maintenance"], ROOT,
                                        SchemaCatalog(schema_paths()))
        workbooks = catalog.list(kind="workbook")["resources"]
        self.assertEqual(
            [item["resourceId"] for item in workbooks],
            ["toolkit-maintenance:workbook:maintenance-extension"],
        )
        guide = catalog.resolve("toolkit-maintenance:workbook:maintenance-extension")
        self.assertEqual(
            guide.header["includes"],
            [
                "toolkit-maintenance:principle:maintenance/keep-one-authoritative-source-per-rule",
                "toolkit-maintenance:principle:maintenance/keep-reference-chains-reachable-and-complete",
                "toolkit-maintenance:principle:maintenance-extension/keep-extension-self-contained-in-setup-assets",
            ],
        )
        self.assertTrue(guide.header["description"])
        loaded_workbook = catalog.load(guide.resource_id)["resources"]
        workbook_text = next(item["content"] for item in loaded_workbook if item["resourceId"] == guide.resource_id)
        for tag in ("<schedule-rule>", "</schedule-rule>", "<exec-rule>", "</exec-rule>", "<review-rule>", "</review-rule>"):
            self.assertIn(tag, workbook_text)

        scopes = set(catalog.scopes(kind="principle")["scopes"])
        self.assertEqual(
            scopes,
            {
                "maintenance",
                "maintenance-extension",
                "maintenance-knowledge",
                "maintenance-workbook",
                "maintenance-skill",
                "maintenance-tooling",
            },
        )

        principles = catalog.list(kind="principle")["resources"]
        self.assertEqual(len(principles), 26)
        for item in principles:
            loaded = catalog.load(item["resourceId"])
            self.assertEqual(len(loaded["resources"]), 1, item["resourceId"])
            entry = loaded["resources"][0]
            self.assertNotIn("includes", entry)
            body = entry["content"].replace("\r\n", "\n").split("---\n", 2)[2]
            non_empty_lines = sum(1 for line in body.splitlines() if line.strip())
            self.assertLessEqual(non_empty_lines, 15, item["resourceId"])
            self.assertLessEqual(len(body), 800, item["resourceId"])

        self.assertTrue(catalog.validate()["ok"])

    def test_references_resolve_inside_current_source(self) -> None:
        extension = ROOT / "extensions/toolkit-maintenance"
        for path in extension.rglob("*.md"):
            for link in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if ":" in link or link.startswith("#"):
                    continue
                self.assertTrue((path.parent / link.split("#", 1)[0]).is_file(), f"{path}: {link}")
        self.assertFalse(list(extension.rglob("resource.json")))


if __name__ == "__main__":
    unittest.main()
