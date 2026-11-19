"""Offline schema closure catches broken contracts without replaying retired workflows."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_protocols", ROOT / "scripts/check_protocols.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
from trigrams_toolkit.shared.errors import ProtocolError


class ProtocolContractTests(unittest.TestCase):
    def test_document_parser_preserves_large_integers_and_escaped_surrogates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "document.json"
            path.write_text('{"integer":9007199254740992,"escaped":"\\ud800"}', encoding="utf-8")
            self.assertEqual(CHECK.read_json(path), {"integer": 9007199254740992, "escaped": "\ud800"})

    def test_invalid_document_errors_keep_the_source_path_and_cause(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "document.json"
            for raw in (b'{"x":1,"x":2}', b'{"x":1.5}', b'{"x":1e2}', b'{"x":NaN}',
                        b'{"x":Infinity}', b'{broken', b'"\xff"'):
                with self.subTest(raw=raw):
                    path.write_bytes(raw)
                    with self.assertRaises(ValueError) as caught:
                        CHECK.read_json(path)
                    self.assertIn(str(path), str(caught.exception))
                    self.assertIsInstance(caught.exception.__cause__, ProtocolError)

    def test_project_path_contract_accepts_windows_and_posix_absolute_paths(self) -> None:
        registry, _ = CHECK._load_schemas(ROOT)
        validator = CHECK.Draft202012Validator(
            {"$ref": "urn:harness:state-cli#/$defs/absolutePath"}, registry=registry)
        for value in ("/", "/srv/projects/空间", "C:/projects", r"\\server\share\project"):
            self.assertEqual(list(validator.iter_errors(value)), [], value)
        for value in ("relative/path", "C:relative", "", "/srv/\0project"):
            self.assertTrue(list(validator.iter_errors(value)), value)

    def test_source_contracts_resolve_offline(self) -> None:
        self.assertEqual(CHECK.check_contracts(ROOT), [])

    def test_project_state_contract_uses_local_context_for_all_eight_commands(self) -> None:
        registry, schemas = CHECK._load_schemas(ROOT)
        commands = CHECK.read_json(ROOT / CHECK.CONTRACT_ROOTS[1] / "commands.json")["commands"]
        self.assertNotIn("urn:harness:project", schemas)
        self.assertEqual({command["name"] for command in commands},
                         {"register module", "register feature", "register artifact", "locate", "list",
                          "related", "relate", "validate"})
        for command in commands:
            with self.subTest(command=command["name"]):
                schema = registry.resolver().lookup(command["input"]).contents
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue({"config", "project", "initRoot"}.isdisjoint(schema.get("properties", {})))

    def test_artifact_ownership_contract_requires_module_and_unique_features(self) -> None:
        registry, schemas = CHECK._load_schemas(ROOT)
        schema = schemas["urn:harness:state-cli"]
        validator = CHECK.Draft202012Validator(
            {"$ref": "urn:harness:state-cli#/$defs/artifactInput"}, registry=registry)
        for value in ({"path": "docs/spec.md"}, {"path": "docs/spec.md", "module": "module_inventory"},
                      {"path": "docs/spec.md", "module": "module_inventory", "feature": ["feature_slots", "feature_sorting"]}):
            with self.subTest(value=value):
                self.assertEqual(list(validator.iter_errors(value)), [])
        for value in ({"path": "docs/spec.md", "feature": ["feature_slots"]},
                      {"path": "docs/spec.md", "module": "module_inventory", "feature": ["feature_slots", "feature_slots"]},
                      {"path": "docs/spec.md", "module": "feature_slots"}):
            with self.subTest(value=value):
                self.assertTrue(list(validator.iter_errors(value)))
        self.assertEqual(schema["$defs"]["relateInput"]["required"], ["from", "kind", "to"])

    def test_unknown_schema_reference_is_located(self) -> None:
        with tempfile.TemporaryDirectory(prefix="contracts-") as folder:
            root = Path(folder)
            for name in CHECK.CONTRACT_ROOTS:
                shutil.copytree(ROOT / name, root / name)
            path = root / CHECK.CONTRACT_ROOTS[0] / "broken.schema.json"
            path.write_text(json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema",
                                        "$id": "urn:harness:broken:1", "$ref": "urn:harness:missing:1"}))
            issues = CHECK.check_contracts(root)
            self.assertTrue(any("urn:harness:missing:1" in issue for issue in issues), issues)

    def test_duplicate_commands_and_malformed_documents_fail_through_cli(self) -> None:
        with tempfile.TemporaryDirectory(prefix="contracts-") as folder:
            root = Path(folder)
            for name in CHECK.CONTRACT_ROOTS:
                shutil.copytree(ROOT / name, root / name)
            path = root / CHECK.CONTRACT_ROOTS[0] / "commands.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["commands"].append(value["commands"][0])
            path.write_text(json.dumps(value), encoding="utf-8")
            self.assertTrue(any("Duplicate or invalid command" in issue for issue in CHECK.check_contracts(root)))
            path.write_text('{"tool": "plan-toolkit", "tool": "other"}', encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/check_protocols.py"), "--root", str(root)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1, result)
            output = json.loads(result.stdout)
            self.assertFalse(output["ok"])
            self.assertTrue(any("Duplicate JSON key" in issue for issue in output["issues"]), output)
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
