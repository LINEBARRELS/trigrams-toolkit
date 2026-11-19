"""Keep legacy state JSON distinct from strict handbook/Plan/install JSON."""
import json
from pathlib import Path
import unittest

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.serialization import parse_json
from trigrams_toolkit.shared.state_json import json_bytes, parse_state_json
from trigrams_toolkit.state.frontmatter import metadata
from trigrams_toolkit.state.model import identity_sort_key
from trigrams_toolkit.state.identity import declaration, with_registration


class StateSerializationTests(unittest.TestCase):
    def test_null_ownership_is_repaired_instead_of_treated_as_missing(self):
        source = '---\nartifact-id: artifact_a\nmoduleId: null\n---\n# a\n'
        entity = {"id": "artifact_a", "title": "a", "kind": "core:document", "featureIds": [],
                  "locatorHint": "docs/a.md", "identityMode": "frontmatter"}
        updated = with_registration(source, entity)
        self.assertNotIn("moduleId:", updated)
        self.assertIsNone(declaration(updated, Path("a.md")).module_id)
        self.assertEqual(with_registration(updated, entity), updated)

    def test_ascii_identity_collation_keeps_legacy_order(self):
        values = ["artifact_a", "artifact_A", "artifact_a-b", "artifact_a_b", "artifact_Z", "artifact_z", "artifact_2", "artifact_10", "artifact__", "artifact_-"]
        self.assertEqual(sorted(values, key=identity_sort_key),
                         ["artifact__", "artifact_-", "artifact_10", "artifact_2", "artifact_a", "artifact_A", "artifact_a_b", "artifact_a-b", "artifact_z", "artifact_Z"])

    def test_json_parse_last_key_float_and_double_precision(self):
        source = '{"same":0,"same":1.5,"version":1.0,"large":9007199254740993}'
        self.assertEqual(parse_state_json(source), {"same": 1.5, "version": 1, "large": 9007199254740992})
        with self.assertRaises(ProtocolError):
            parse_json(source)

    def test_encoding_bom_surrogates_and_overflow(self):
        self.assertEqual(parse_state_json(b'"\xff"'), "\ufffd")
        with self.assertRaises(ValueError):
            parse_state_json('\ufeff{}')
        self.assertEqual(parse_state_json('\ufeff{}', bom=True), {})
        self.assertEqual(json.loads(json_bytes(parse_state_json('{"text":"\\ud800", "weight":1e400}'))),
                         {"text": "\ud800", "weight": None})
        for raw in ('NaN', 'Infinity', '-Infinity'):
            with self.assertRaises(ValueError):
                parse_state_json(raw)

    def test_yaml_nested_duplicate_merge_and_alias_semantics(self):
        self.assertEqual(metadata('defaults: &d {moduleId: module_docs}\n<<: *d\ntitle: "yes"'),
                         {"moduleId": "module_docs", "title": "yes"})
        for raw in ('nested: {value: 1, value: 2}', 'base: &b {value: 1}\n<<: *b\nvalue: 2',
                    'title: *absent', 'first: &a {one: 1}\nsecond: &b {two: 2}\n<<: *a\n<<: *b'):
            with self.assertRaises(ValueError):
                metadata(raw)

    def test_yaml_roundtrip_preserves_unmanaged_alias_graph_and_legacy_scalars(self):
        header = "title: 'y' # quoted title\nrecurse: &loop {self: *loop}\nratio: 01:02\nwhen: 2026-02-31\n"
        source = f"---\n{header}---\n# Body\n"
        entity = {"id": "artifact_doc", "identityMode": "frontmatter", "featureIds": []}
        updated = with_registration(source, entity)
        self.assertIn(header, updated)
        self.assertTrue(updated.endswith("---\n# Body\n"))
        self.assertEqual(with_registration(updated, entity), updated)
        self.assertEqual(declaration(updated, Path("doc.md")).title, "y")
        for scalar in ("y", "1e3", "01:02", "09", "2026-2-3"):
            with self.subTest(scalar=scalar), self.assertRaises(ValueError):
                declaration(f"---\ntitle: {scalar}\n---\n", Path("doc.md"))
