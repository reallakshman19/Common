"""Offline parity: Common's portable viewer and tools must equal the pinned source bytes.
Only intentional source sync may update references/UPSTREAM_PARITY.json.
"""
import hashlib
import json
import re
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=ROOT/"references"/"UPSTREAM_PARITY.json"

class UpstreamParity(unittest.TestCase):
    def test_pinned_source_and_exact_blob_bytes(self):
        m=json.loads(EXPECTED.read_text(encoding="utf-8"))
        self.assertRegex(m["commit"],r"^[a-f0-9]{40}$")
        self.assertIn(m["commit"],(ROOT/"viewer"/"VERSION").read_text(encoding="utf-8"))
        for folder in ("viewer","scripts"):
            base=ROOT/folder
            expected=m[folder]
            actual={p.name for p in base.iterdir() if p.is_file() and (
                p.suffix in (".py",".js",".css",".html") and p.name!="VERSION")}
            self.assertEqual(set(expected),actual,folder+" contains drifted or missing files")
            for name,blob in expected.items():
                with self.subTest(folder=folder,name=name):
                    raw=(base/name).read_bytes()
                    got=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
                    self.assertEqual(got,blob,"file differs from the immutable upstream source candidate")
    def test_browser_cache_versions_are_consistent(self):
        m=json.loads(EXPECTED.read_text(encoding="utf-8"))
        for path in list((ROOT/"viewer").glob("*.js"))+[ROOT/"viewer"/"index.html"]:
            versions=set(re.findall(r"\?v=([0-9]+)",path.read_text(encoding="utf-8")))
            self.assertTrue(not versions or versions=={m["viewerVersion"]},str(path)+": "+str(versions))

if __name__=="__main__":unittest.main()
