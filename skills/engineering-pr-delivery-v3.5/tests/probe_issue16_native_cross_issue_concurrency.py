"""Issue #16 positive concurrency control for *different issue scopes*.

This is a real native transaction replay in disposable temp storage against the
current advisory-patched PR2 worktree, NOT a production policy grant, native
source mutation, or B/Owner/Local principal authentication. The only patched
function is a scheduling seam AFTER the real incomplete-transaction read;
the native validation, _prepare, execute, receipts and writes are not mocked.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import pathlib
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

PIN = "da3680459c5b48f44cda822ccf5009be4b035eef"
NATIVE_ROOT: pathlib.Path | None = None
TX = None
PUBLISH = None


class IndependentIssueAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if NATIVE_ROOT is None:
            raise RuntimeError("NATIVE_ROOT_REQUIRED")
        current = subprocess.check_output(
            ["git", "-C", str(NATIVE_ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
        if current != PIN:
            raise RuntimeError("PINNED_NATIVE_GIT_HEAD_MISMATCH")
        scripts = NATIVE_ROOT / "skills/engineering-pr-delivery-v3.2/scripts"
        sys.path.insert(0, str(scripts))
        import transactionlib
        from relay_tx import publish_buddy_markdown
        global TX, PUBLISH
        TX, PUBLISH = transactionlib, publish_buddy_markdown

    def test_parallel_distinct_issue_intake_admission_preserves_two_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            barrier = threading.Barrier(2, timeout=25)
            seen: dict[int, int] = {}
            real_preflight = TX.incomplete_transactions

            def pause_after_real_preflight(base: pathlib.Path):
                found = real_preflight(base)
                if threading.current_thread().name.startswith("issue16-other-issue"):
                    seen[threading.get_ident()] = len(found)
                    barrier.wait()
                return found

            def submit(issue: int):
                return PUBLISH(
                    root,
                    issue_number=issue,
                    tx_id=f"TX.{issue}.20",
                    stage="STAGE1_INTAKE",
                    actor=f"synthetic-controller-{issue}",
                    markdown=(
                        f"# STAGE1_INTAKE\n\nHistorical fixture for synthetic issue {issue}.\n"
                    ).encode("utf-8"),
                )

            with patch.object(TX, "incomplete_transactions", side_effect=pause_after_real_preflight):
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=2, thread_name_prefix="issue16-other-issue"
                ) as pool:
                    futures = [pool.submit(submit, issue) for issue in (6006, 6007)]
                    replies = [future.result(timeout=55) for future in futures]

            self.assertEqual(sorted(seen.values()), [0, 0])
            self.assertEqual([row["status"] for row in replies], ["COMMITTED", "COMMITTED"])
            for issue in (6006, 6007):
                txid = f"TX.{issue}.20"
                p = root / f"relay/CONTINUITY/episodes/ISSUE-{issue}/messages/{txid}-STAGE1_INTAKE.md"
                manifest = root / f"relay/TRANSACTIONS/{txid}/manifest.yaml"
                self.assertTrue(p.is_file(), f"MISSING_DIFFERENT_ISSUE_MESSAGE_{issue}")
                self.assertTrue(manifest.is_file(), f"MISSING_DIFFERENT_ISSUE_RECEIPT_{issue}")
                receipt = TX.load_manifest(manifest)
                self.assertEqual(receipt["id"], txid)
                self.assertEqual(receipt["status"], "COMMITTED")
                self.assertEqual(receipt["command"], "PUBLISH_BUDDY_MARKDOWN")
                self.assertEqual(
                    receipt["operations"][0]["after_digest"],
                    TX._digest_bytes(p.read_bytes()),
                )
            for name in ("STATE.yaml", "EVENTS.jsonl"):
                self.assertFalse((root / "relay" / name).exists())
            self.assertFalse((root / "relay/LEASES").exists())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", required=True, type=pathlib.Path)
    args = parser.parse_args()
    NATIVE_ROOT = args.native_root.resolve()
    unittest.main(argv=[sys.argv[0], "-v"])
