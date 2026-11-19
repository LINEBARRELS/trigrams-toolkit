"""Guide discovery, includes and package declarations."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from support import RuntimeCase, write_json
from trigrams_toolkit.handbook.guides import GuideCatalog
from trigrams_toolkit.handbook.package import load_package, resource_paths


class GuideTests(RuntimeCase):
    def test_linked_package_root_has_the_same_resources(self) -> None:
        alias = self.root / "package-alias"
        try:
            alias.symlink_to(self.package, target_is_directory=True)
        except OSError as error:
            if getattr(error, "winerror", None) != 1314:
                raise
            self.skipTest("Symbolic link privilege unavailable")
        self.assertEqual(resource_paths(alias, self.manifest["resourceRoots"]),
                         resource_paths(self.package, self.manifest["resourceRoots"]))

    def test_directory_filters_union_scopes_and_does_not_read_body_or_hash_sources(self) -> None:
        original = Path.read_bytes
        def declaration_only(path: Path) -> bytes:
            self.assertEqual(path.name, "resources.json", "payload read")
            return original(path)
        with patch.object(Path, "read_bytes", declaration_only):
            self.refresh()
            values = self.catalog.list("workbook", ["programming", "research"])["resources"]
            self.assertEqual([item["resourceId"] for item in values],
                             ["core:workbook:programming", "core:workbook:research"])
            self.assertEqual(len(self.catalog.list(scopes=["research"])["resources"]), 1)
            self.catalog.validate()

    def test_principle_scopes_are_exact_and_workbooks_include_across_scopes(self) -> None:
        self.guide("programming-design/contract-boundaries", "principle")
        self.guide("programming/implementation", "principle")
        self.guide("programming-other", "workbook", {
            "includes": ["core:workbook:research", "core:principle:programming-design/contract-boundaries"]})
        self.refresh()
        self.assertEqual(self.catalog.scopes("principle")["scopes"],
                         ["programming", "programming-design", "scale"])
        self.assertEqual([item["resourceId"] for item in self.catalog.list("principle", ["programming"])["resources"]],
                         ["core:principle:programming/implementation"])
        both = self.catalog.list("principle", ["programming", "programming-design"])["resources"]
        self.assertEqual(len(both), 2)
        self.assertEqual([item["resourceId"] for item in self.catalog.list("workbook", ["programming"])["resources"]],
                         ["core:workbook:programming", "core:workbook:programming-other"])
        loaded = self.catalog.load("programming-other")["resources"]
        self.assertEqual([item["resourceId"] for item in loaded],
                         ["core:principle:scale/limits", "core:workbook:research",
                          "core:principle:programming-design/contract-boundaries", "core:workbook:programming-other"])
        self.assertEqual(loaded[-2]["name"], "contract-boundaries")
        self.assertTrue({"content", "source", "entryPath"} <= loaded[-2].keys())
        self.assertNotIn("includes", loaded[-2])
        for item in self.catalog.list()["resources"]:
            self.assertEqual(set(item), {"resourceId", "description"})

    def test_load_reads_only_entry_and_includes_leaving_long_references_on_demand(self) -> None:
        path = self.package / "guides/research/references/long.md"
        path.parent.mkdir()
        path.write_bytes(b"\xffnot a UTF-8 document")
        result = self.catalog.load("research")
        self.assertEqual(result["selected"], "core:workbook:research")
        self.assertEqual(result["selectedIds"], [result["selected"]])
        self.assertEqual([item["resourceId"] for item in result["resources"]],
                         ["core:principle:scale/limits", "core:workbook:research"])
        self.assertTrue(all("content" in item and "binding" not in item for item in result["resources"]))

    def test_batch_load_deduplicates_roots_and_shared_dependencies_before_reading(self) -> None:
        self.guide("programming", "workbook", {"includes": ["core:workbook:research"]})
        self.refresh()
        original = Path.read_text
        reads = []
        def read_once(path: Path, *args, **kwargs) -> str:
            reads.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", read_once):
            result = self.catalog.load(["programming", "research", "core:workbook:programming",
                                        "core:principle:scale/limits"])
        self.assertEqual(result["selectedIds"], ["core:workbook:programming", "core:workbook:research",
                                                "core:principle:scale/limits"])
        self.assertNotIn("selected", result)
        self.assertEqual([item["resourceId"] for item in result["resources"]],
                         ["core:principle:scale/limits", "core:workbook:research", "core:workbook:programming"])
        self.assertEqual(reads, [Path(item["entryPath"]) for item in result["resources"]])
        with patch.object(Path, "read_text", side_effect=AssertionError("Partial body read")):
            self.assert_code("invalid_reference", lambda: self.catalog.load(["research", "missing"]))

    def test_workbook_identity_survives_move_and_duplicates_fail(self) -> None:
        self.guide("research", "workbook", {"resourceId": "core:workbook:stable"})
        (self.package / "guides/research").rename(self.package / "guides/moved")
        self.refresh()
        self.assertIn("moved", self.catalog.load("core:workbook:stable")["resources"][0]["entryPath"])
        self.guide("another", "workbook", {"resourceId": "core:workbook:stable"})
        self.assert_code("resource_conflict", self.refresh)

    def test_validate_rejects_bad_headers_identity_and_includes(self) -> None:
        cases = [({"status": "active"}, "invalid_schema"),
                 ({"appliesTo": ["research"]}, "invalid_schema"),
                 ({"resourceId": "other:workbook:research"}, "identity_conflict"),
                 ({"includes": ["core:principle:scale/missing"]}, "invalid_reference"),
                 ({"includes": ["core:workbook:research"]}, "invalid_reference")]
        for fields, expected in cases:
            with self.subTest(fields=fields):
                self.guide("research", "workbook", fields)
                self.assert_code(expected, lambda: GuideCatalog.discover([self.package], self.project, self.schemas).validate())


    def test_principle_layout_and_headers_reject_legacy_and_extra_levels(self) -> None:
        for name in ("legacy", "scope/deeper/leaf", "scope/Not-English-Slug"):
            with self.subTest(name=name):
                path = self.guide(name, "principle")
                self.assert_code("invalid_schema", self.refresh)
                path.unlink()
        for fields in ({"name": "Redundant"}, {"resourceId": "core:principle:scope/rule"},
                       {"includes": []}, {"includes": ["core:principle:scale/limits"]}):
            path = self.guide("scope/rule", "principle", fields)
            self.assert_code("invalid_schema", lambda: self.schemas.validate(
                "urn:harness:guides#/$defs/principleHeader", {"description": "Rule.", **fields}))
            self.assert_code("invalid_schema", self.refresh)
            path.unlink()

    def test_principle_rename_changes_identity_and_short_names_require_unique_provider(self) -> None:
        path = self.guide("programming/rule", "principle")
        self.guide("programming-design/rule", "principle")
        self.refresh()
        self.assertEqual(self.catalog.resolve("programming/rule").resource_id, "core:principle:programming/rule")
        path.parent.rename(path.parent.with_name("renamed"))
        self.refresh()
        self.assert_code("invalid_reference", lambda: self.catalog.load("core:principle:programming/rule"))
        self.assertEqual(self.catalog.resolve("programming/renamed").path.parent.name, "renamed")
        extra = self.root / "extra"
        write_json(extra / "resources.json", {**self.manifest, "source": "extra", "resourceRoots": ["principles"]})
        second = extra / "principles/programming/renamed/PRINCIPLE.md"
        second.parent.mkdir(parents=True)
        second.write_text("---\ndescription: Other provider.\n---\nBody.\n", encoding="utf-8")
        catalog = GuideCatalog.discover([self.package, extra], self.project, self.schemas)
        self.assert_code("resource_conflict", lambda: catalog.load("programming/renamed"))
        self.assertEqual(catalog.load("extra:principle:programming/renamed")["selected"],
                         "extra:principle:programming/renamed")

    def test_long_principles_load_only_their_own_body(self) -> None:
        path = self.guide("scope/long-rule", "principle")
        with path.open("a", encoding="utf-8") as stream:
            stream.write("Long unchanged judgment.\n" * 40)
        self.refresh()
        self.assertTrue(self.catalog.validate()["ok"])
        loaded = self.catalog.load("scope/long-rule")["resources"]
        self.assertEqual([item["resourceId"] for item in loaded], ["core:principle:scope/long-rule"])
        self.assertIn("Long unchanged judgment.\n" * 40, loaded[0]["content"])

    def test_shared_resource_references_accept_the_same_new_identity(self) -> None:
        definition = "urn:harness:common#/$defs/ref"
        for identity in ("core:principle:programming-design/contract-boundaries", "core:workbook:research"):
            self.schemas.validate(definition, {"kind": "resource", "id": identity})
        for identity in ("core:principle:legacy", "core:principle:scope/extra/leaf", "core:workbook:scope/leaf"):
            self.assert_code("invalid_schema", lambda: self.schemas.validate(definition, {"kind": "resource", "id": identity}))

    def test_package_requires_the_complete_current_declaration(self) -> None:
        original = dict(self.manifest)
        for field, replacement in (("schemaVersion", 0), ("install", None), ("version", "development")):
            with self.subTest(field=field):
                invalid = {**original, field: replacement}
                write_json(self.package / "resources.json", invalid)
                error = self.assert_code("invalid_schema", lambda: load_package(self.package, self.project, self.schemas))
                self.assertIn("Archive previous state and rebuild", str(error))

    def test_duplicate_providers_and_foreign_types_are_rejected(self) -> None:
        extra = self.root / "extra"
        write_json(extra / "resources.json", {**self.manifest, "resourceRoots": []})
        self.assert_code("resource_conflict", lambda: GuideCatalog.discover([self.package, extra], self.project, self.schemas))
        self.manifest["artifactTypes"] = ["foreign:asset"]
        write_json(self.package / "resources.json", self.manifest)
        self.assert_code("invalid_reference", lambda: self.refresh())
