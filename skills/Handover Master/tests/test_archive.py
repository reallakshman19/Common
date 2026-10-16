"""Archive migration guards: exact historical blobs preserved, active native sources remain."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HISTORIC="coordination/Session_Oct07/Tab6_Dashboard_V2"
ARCHIVE="superseded/coordination/Session_Oct07/Tab6_Dashboard_V2"
ORIGINAL={
    "LINEAGE.md":"f7acbb145c79877a380912a3cfb6def6fa9d9b2f",
    "LOG.md":"defbb06f615d6a290d15fc7e4d69d83b11232329",
}

def oid(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()

class ArchiveTests(unittest.TestCase):
    def test_original_archived_bytes_are_identical(self):
        for name,sha in ORIGINAL.items():
            with self.subTest(file=name):
                data=(ROOT/ARCHIVE/name).read_bytes()
                self.assertEqual(oid(data),sha)

    def test_old_location_is_pointer_not_live_dash_v2(self):
        self.assertFalse((ROOT/HISTORIC/"LINEAGE.md").exists())
        self.assertFalse((ROOT/HISTORIC/"LOG.md").exists())
        pointer=(ROOT/HISTORIC/"README.md").read_text(encoding="utf-8")
        self.assertIn("SUPERSEDED",pointer)
        self.assertIn("CoordinatorLandingpage",pointer)
        self.assertIn("superseded",pointer)

    def test_real_native_modules_still_exist(self):
        index=json.loads((ROOT/"skills/Handover Master/sources.json").read_text(encoding="utf-8"))
        for key,item in index["sources"].items():
            for field in ("path","schema","validator","script","compiler",
                          "two_script","three_script","cold_script"):
                if field in item:
                    path=ROOT/item[field]
                    with self.subTest(key=key,field=field):
                        self.assertTrue(path.is_file(),str(path))
                        self.assertFalse(str(path).startswith(str(ROOT/"superseded")))

    def test_archive_index_declares_no_unverified_active_moves(self):
        text=(ROOT/"superseded/HANDOVER_FOLDER_AUDIT.md").read_text(encoding="utf-8")
        self.assertIn("RETAIN",text)
        self.assertIn("CoordinatorLandingpage",text)
        self.assertIn("engineering-pr-delivery-v3.6",text)
        self.assertIn("relay-onboarding-rwi",text)

    def test_archive_is_not_a_runtime_protocol_root(self):
        self.assertFalse((ROOT/"superseded/SKILL.md").exists())
        self.assertTrue((ROOT/"skills/Handover Master/SKILL.md").is_file())

if __name__=="__main__":
    unittest.main()
