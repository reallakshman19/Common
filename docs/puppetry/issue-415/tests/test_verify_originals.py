#!/usr/bin/env python3
"""Focused tests for #415 original-asset custody; synthetic bytes only."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_originals import verify


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "originals"
        self.root.mkdir()
        self.manifest = Path(self.tmp.name) / "manifest.json"
        self.rel = "king_puppet_final/make.py"
        self.data = b"synthetic fixture, not a recovered original"
        self.expected = hashlib.sha256(self.data).hexdigest()
        self.records = [{"path": self.rel, "sha256": self.expected, "kind": "generator"}]

    def write_manifest(self, records=None):
        self.manifest.write_text(json.dumps({
            "schema": "puppet-originals-sha256/v1",
            "files": self.records if records is None else records,
        }), encoding="utf-8")

    def test_matching_bytes_pass(self):
        self.write_manifest()
        dest = self.root / self.rel
        dest.parent.mkdir(parents=True)
        dest.write_bytes(self.data)
        outcome = verify(self.manifest, self.root)
        self.assertTrue(outcome["all_match"])
        self.assertEqual(outcome["counts"], {"MATCH": 1, "MISSING": 0, "MISMATCH": 0})
        self.assertIn("NOT_MANUFACTURING_APPROVAL", outcome["scope"])

    def test_missing_original_fails_closed(self):
        self.write_manifest()
        outcome = verify(self.manifest, self.root)
        self.assertFalse(outcome["all_match"])
        self.assertEqual(outcome["findings"][0]["status"], "MISSING")

    def test_altered_original_fails_closed(self):
        self.write_manifest()
        dest = self.root / self.rel
        dest.parent.mkdir(parents=True)
        dest.write_bytes(self.data + b" changed")
        outcome = verify(self.manifest, self.root)
        self.assertFalse(outcome["all_match"])
        self.assertEqual(outcome["findings"][0]["status"], "MISMATCH")

    def test_path_traversal_rejected(self):
        self.write_manifest([{"path": "../outside.pdf", "sha256": self.expected}])
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            verify(self.manifest, self.root)

    def test_duplicate_identity_rejected(self):
        self.write_manifest(self.records + self.records)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            verify(self.manifest, self.root)

    def test_malformed_digest_rejected(self):
        self.write_manifest([{"path": self.rel, "sha256": "0"}])
        with self.assertRaisesRegex(ValueError, "Invalid SHA-256"):
            verify(self.manifest, self.root)


if __name__ == "__main__":
    unittest.main()
