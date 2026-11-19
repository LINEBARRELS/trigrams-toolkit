"""The maintenance extension exposes atomic principles and selectable workbooks with local references."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.resources import schema_paths
from trigrams_toolkit.shared.schema import SchemaCatalog
from trigrams_toolkit.handbook.source_catalog import source_packages


class MaintenanceContentTests(unittest.TestCase):
    def test_workbooks_load_baseline_principles_and_atomic_pilot_budget(self) -> None:
        catalog = GuideCatalog.discover([p for p in source_packages(ROOT, SchemaCatalog(schema_paths()))
                                         if p.manifest.get("extension") == "toolkit-maintenance"], ROOT,
                                        SchemaCatalog(schema_paths()))
        expected_includes = {
            "extension": [
                "toolkit-maintenance:principle:maintenance/keep-one-authoritative-source-per-rule",
                "toolkit-maintenance:principle:maintenance/keep-reference-chains-reachable-and-complete",
            ],
            "knowledge": [
                "toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence",
                "toolkit-maintenance:principle:maintenance-knowledge/separate-normative-rules-from-guidance-and-history",
            ],
            "workbook": [
                "toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence",
                "toolkit-maintenance:principle:maintenance-workbook/structure-workbooks-for-plan-translation",
            ],
            "tooling": [
                "toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence",
                "toolkit-maintenance:principle:maintenance-tooling/separate-public-cli-from-private-scripts",
            ],
            "skill": [
                "toolkit-maintenance:principle:maintenance/ground-review-in-verifiable-evidence",
                "toolkit-maintenance:principle:maintenance-skill/align-skill-type-with-trigger-and-delivery",
            ],
        }
        for topic, includes in expected_includes.items():
            identity = f"toolkit-maintenance:workbook:maintenance-{topic}"
            guide = catalog.resolve(identity)
            self.assertEqual(guide.header["includes"], includes)
            self.assertTrue(guide.header["description"])

        principles = catalog.list(kind="principle")["resources"]
        self.assertEqual(len(principles), 19)
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
