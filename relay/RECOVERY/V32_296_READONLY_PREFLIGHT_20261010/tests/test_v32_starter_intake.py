"""No original ZIP in this checkout: fake archives test pin and safe HOLD only."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZipInfo, ZIP_STORED

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v32_starter_intake import (
    EXPECTED_MEMBER_COUNT, REQUIRED_BASENAMES, STARTER_SHA256,
    inspect_starter_archive,
)


def fixture(path, *, rewrite=None):
    entries = {
        "relay-v32-e2e-lab-starter/tests/test_r01_input.py": "def test_pending(): pass",
        "relay-v32-e2e-lab-starter/LOCAL_AGENT_TASKS.md": "# lab",
        "relay-v32-e2e-lab-starter/evidence/TASK_EVIDENCE_TEMPLATE.md": "# evidence",
    }
    for i in range(EXPECTED_MEMBER_COUNT - len(entries)):
        entries[f"relay-v32-e2e-lab-starter/fixtures/f{i:02}.txt"] = f"fixture={i}"
    if rewrite:
        rewrite(entries)
    with ZipFile(path, "w", compression=ZIP_STORED) as z:
        for name, text in entries.items():
            z.writestr(name, text)
    return sha256(path.read_bytes()).hexdigest()


class StarterIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "starter.zip"

    def check(self, **opts):
        return inspect_starter_archive(self.path, **opts)

    def test_reported_archive_digest_is_exact(self):
        self.assertEqual(STARTER_SHA256,
                         "9f1c317494168bda0ea83baf31c5a6db4d6035085c102743b22c707c3f4a5030")
        self.assertEqual(EXPECTED_MEMBER_COUNT, 35)
        self.assertEqual(len(REQUIRED_BASENAMES), 3)

    def test_missing_archive_is_hold_not_success(self):
        row = self.check().as_dict()
        self.assertEqual(row["status"], "HOLD_ARCHIVE_MISSING")
        self.assertFalse(row["original_fixture_tests_run"])
        self.assertFalse(row["writer_authorized"])

    def test_coherent_test_zip_cannot_authenticate_owner_or_evidence(self):
        expected = fixture(self.path)
        row = self.check(expected_sha256=expected).as_dict()
        self.assertEqual(row["status"], "HOLD_PARENT_PIN_ONLY")
        self.assertEqual(row["members_observed"], 35)
        self.assertFalse(row["original_owner_authenticated"])
        self.assertFalse(row["product_pr_verified"])
        self.assertIsNone(row["accepted_evidence_count"] if "accepted_evidence_count" in row else None)
        self.assertFalse(row["positive_fact_issuer"])
        self.assertFalse(row["delp_invoked"])

    def test_wrong_digest_fails_before_any_zip_content_trust(self):
        expected = fixture(self.path)
        row = self.check()
        self.assertEqual(row.status, "HOLD_ARCHIVE_SHA_MISMATCH")
        self.assertEqual(row.archive_sha256, expected)
        self.assertIsNone(row.file_count)

    def test_bad_digest_selector_never_reads_zip(self):
        fixture(self.path)
        self.assertEqual(self.check(expected_sha256="../bad").status, "FAILED_TARGET")

    def test_wrong_member_count_holds(self):
        def truncate(entries):
            entries.pop(next(k for k in entries if "f00" in k))
        expected = fixture(self.path, rewrite=truncate)
        self.assertIn("MEMBER_COUNT_MISMATCH", self.check(expected_sha256=expected).reasons)

    def test_missing_original_r01_test_holds(self):
        def remove(entries):
            name = next(k for k in entries if k.endswith("test_r01_input.py"))
            entries.pop(name)
            entries["relay-v32-e2e-lab-starter/tests/renamed.py"] = "fake"
        expected = fixture(self.path, rewrite=remove)
        self.assertIn("ORIGINAL_TEST_OR_TASK_MISSING", self.check(expected_sha256=expected).reasons)

    def test_zip_slip_member_holds_even_when_hash_matches(self):
        def traversal(entries):
            key = next(k for k in entries if "f00" in k)
            entries["../" + key] = entries.pop(key)
        expected = fixture(self.path, rewrite=traversal)
        self.assertIn("DUPLICATE_OR_UNSAFE_MEMBER", self.check(expected_sha256=expected).reasons)

    def test_symlink_member_holds(self):
        fixture(self.path)
        entries = []
        with ZipFile(self.path) as z:
            for member in z.infolist():
                entries.append((member.filename, z.read(member.filename)))
        with ZipFile(self.path, "w") as z:
            for i, (name, body) in enumerate(entries):
                zi = ZipInfo(name)
                if i == 10:
                    zi.create_system = 3
                    zi.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(zi, body)
        expected = sha256(self.path.read_bytes()).hexdigest()
        self.assertIn("DIRECTORY_LINK_OR_ENCRYPTION", self.check(expected_sha256=expected).reasons)

    def test_nonzip_bytes_holds(self):
        self.path.write_bytes(b"not a zip")
        pin = sha256(self.path.read_bytes()).hexdigest()
        self.assertEqual(self.check(expected_sha256=pin).status, "HOLD_ARCHIVE_UNREADABLE")

    def test_source_bounded_archive_size_holds(self):
        from unittest.mock import patch
        fixture(self.path)
        with patch("v32_starter_intake.MAX_ARCHIVE_BYTES", 1):
            self.assertEqual(self.check().status, "HOLD_ARCHIVE_UNSAFE")

    def test_directory_member_holds(self):
        fixture(self.path)
        entries=[]
        with ZipFile(self.path) as z:
            entries=[(i.filename,z.read(i)) for i in z.infolist()]
        with ZipFile(self.path,"w") as z:
            for i,(name,body) in enumerate(entries):
                z.writestr(name + ("/" if i==11 else ""),body if i!=11 else b"")
        pin=sha256(self.path.read_bytes()).hexdigest()
        self.assertIn("DUPLICATE_OR_UNSAFE_MEMBER",self.check(expected_sha256=pin).reasons)

    def test_cli_is_hold_when_original_archive_absent(self):
        script=Path(__file__).resolve().parents[1]/"v32_starter_intake.py"
        run=subprocess.run([sys.executable,str(script),"--archive",str(self.path)],
                           capture_output=True,text=True,check=False,timeout=10)
        self.assertEqual(run.returncode,2)
        self.assertIn("HOLD_ARCHIVE_MISSING",run.stdout)
        self.assertNotIn("APPROVED",run.stdout)

if __name__ == "__main__":
    unittest.main()
