"""Issue #6 R1C: deterministic native transaction admission race oracle.

SOURCE: currently protected V3.2 transactionlib._prepare calls the real
incomplete_transactions(root) and then creates a *different* TX directory
with exist_ok=False. Those separate steps are not a repository/issue lock.

This test stages TWO same-issue Stage1 attempts at the SAME unprotected
read/check gap. It patches ONLY that observation boundary to synchronize
two real threads. It does NOT mock _validate_buddy_markdown_transaction,
_prepare, execute, any receipt content or the commit path.

The proposed negative oracle is fail-closed same-issue admission: two
concurrent independent STAGE1_INTAKE publications must not BOTH complete
unless a clearly authorized ordered controller owns their issue sequence.
Whether parallel research messages may share one issue is a separate
Owner/Local policy decision. Therefore a RED test establishes an observed
race capability, not authenticated dual production writers or a granted
policy amendment. Actor strings are synthetic, never B identity proof.
"""
from __future__ import annotations

import concurrent.futures
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
NATIVE = ROOT / "skills/engineering-pr-delivery-v3.2/scripts"
sys.path.insert(0, str(NATIVE))

import transactionlib
from relay_tx import publish_buddy_markdown

ISSUE = 6006


def intake(root: Path, serial: int, actor: str):
    return publish_buddy_markdown(
        root, issue_number=ISSUE,
        tx_id=f"TX.{ISSUE}.{serial}",
        stage="STAGE1_INTAKE", actor=actor,
        markdown=(
            f"# STAGE1_INTAKE\n\n"
            f"Independent synthetic attempt {serial}; no actor authorization.\n"
        ).encode("utf-8"),
    )


class NativeBuddyConcurrencyTests(unittest.TestCase):
    def test_positive_sequential_new_intake_receipts_remain_immutable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = intake(root, 10, "controller-one")
            b = intake(root, 11, "controller-two")
            self.assertEqual((a["status"], b["status"]), ("COMMITTED", "COMMITTED"))
            for seq in (10, 11):
                receipt = root / f"relay/TRANSACTIONS/TX.{ISSUE}.{seq}/manifest.yaml"
                self.assertTrue(receipt.is_file())
            self.assertFalse((root / "relay/LEASES").exists())
            self.assertFalse((root / "relay/STATE.yaml").exists())

    def test_negative_same_issue_simultaneous_admission_requires_arbitration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            barrier = threading.Barrier(2)
            observed = {}
            real_incomplete = transactionlib.incomplete_transactions

            def real_read_then_pause(path: Path):
                # Both real callers get the true preflight observation before
                # either creates its own transaction dir. The patch merely
                # forces the unsafe check-to-reservation interleaving.
                current = real_incomplete(path)
                if threading.current_thread().name.startswith("issue6-race"):
                    observed[threading.current_thread().name] = len(current)
                    barrier.wait(timeout=25)
                return current

            def run(serial: int):
                try:
                    result = intake(root, serial, f"synthetic-controller-{serial}")
                    return ("COMMITTED", result["status"])
                except transactionlib.TransactionError as err:
                    return ("REJECTED", str(err))

            with patch.object(transactionlib, "incomplete_transactions", side_effect=real_read_then_pause):
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=2, thread_name_prefix="issue6-race"
                ) as pool:
                    tasks = [pool.submit(run, 20), pool.submit(run, 21)]
                    outcomes = [f.result(timeout=50) for f in tasks]

            # If this fails with two COMMITTED receipts, existing native
            # transaction checks offer no atomic, issue-scoped arbitration.
            # A stronger fix needs controller/custody semantics and an actual
            # single-writer lock/transaction serialization, not a new README.
            self.assertEqual(sorted(observed.values()), [0, 0])
            committed = [result for result in outcomes if result[0] == "COMMITTED"]
            self.assertLessEqual(
                len(committed), 1,
                "BUDDY_UNSERIALIZED_SAME_ISSUE_ADMISSION: both synthetic "
                "controller attempts committed after each observed no "
                "incomplete transaction; owner policy and native lock needed",
            )
            self.assertFalse((root / "relay/STATE.yaml").exists())
            self.assertFalse((root / "relay/LEASES").exists())


if __name__ == "__main__":
    unittest.main()
