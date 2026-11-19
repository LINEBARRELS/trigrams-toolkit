"""Document parsing preserves its boundary before runtime-value validation."""
from pathlib import Path
import sys
import unittest

from trigrams_toolkit.shared.errors import ProtocolError
from trigrams_toolkit.shared.serialization import MAX_INTEGER, parse_json, parse_json_document


class SerializationTests(unittest.TestCase):
    def test_documents_keep_large_integer_and_escaped_string_values(self):
        for raw, expected in ((str(MAX_INTEGER + 1), MAX_INTEGER + 1), ('"\\ud800"', '\ud800')):
            self.assertEqual(parse_json_document(raw), expected)
            with self.assertRaises(ProtocolError) as caught:
                parse_json(raw)
            self.assertEqual(caught.exception.code, "invalid_json")

    def test_documents_and_runtime_share_syntax_and_number_failures(self):
        for parse in (parse_json_document, parse_json):
            for raw in ('{"x":1,"x":2}', '1.0', '1e2', 'NaN', 'Infinity', b'"\xff"', '{'):
                with self.subTest(parser=parse.__name__, raw=raw):
                    with self.assertRaises(ProtocolError) as caught:
                        parse(raw)
                    self.assertEqual(caught.exception.code, "invalid_json")

    def test_bad_encoding_and_syntax_retain_their_causes(self):
        for raw in (b'"\xff"', '{'):
            with self.assertRaises(ProtocolError) as caught:
                parse_json_document(raw)
            self.assertIsNotNone(caught.exception.__cause__)

    def test_runtime_unicode_and_nested_values_still_roundtrip(self):
        self.assertEqual(parse_json('{"空间":[true,null,-1,"\\ud83d\\udc09"]}'),
                         {"空间": [True, None, -1, "🐉"]})
