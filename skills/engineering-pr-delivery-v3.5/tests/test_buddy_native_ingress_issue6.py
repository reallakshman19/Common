"""Issue #6 R1: executable native Buddy producer/consumer seam negatives.

This is a deliberately RED diagnostic against the current native V3.2 branch,
NOT a proposed modification of the four frozen V3.2 source paths and NOT a
Runner isolation, provider issue-ID, Owner or writer-attestation test.

Synthetic actors/session strings are local test data only. Expected behavior is
the V3.5 Stage1 exact-heading and monotonic predecessor-chain contract.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NATIVE_SCRIPTS = ROOT / "skills/engineering-pr-delivery-v3.2/scripts"
sys.path.insert(0, str(NATIVE_SCRIPTS))

from relay_tx import publish_buddy_markdown
from transactionlib import TransactionError

ISSUE = 6006  # synthetic; NOT an authenticated provider issue or admission


class NativeBuddyIngressSeamTests(unittest.TestCase):
    def publish(self, root: Path, seq: int, stage: str, actor: str, body: bytes):
        return publish_buddy_markdown(
            root,
            issue_number=ISSUE,
            tx_id=f"TX.{ISSUE}.{seq}",
            stage=stage,
            actor=actor,
            markdown=body,
        )

    def preflight(self, root: Path):
        self.publish(root, 1, "STAGE1_INTAKE", "operator",
                     b"# STAGE1_INTAKE\n\nHistorical source only.\n")
        self.publish(root, 2, "DISPATCH_REQUEST", "operator",
                     b"# DISPATCH_REQUEST\n\nSynthetic launch request.\n")
        self.publish(root, 3, "DISPATCH_OBSERVATION", "operator",
                     b"# RUNNER_EXECUTION_OBSERVED\n\nSession ref: synthetic-b\nRead-scope ref: synthetic-only\n")

    def test_positive_control_two_original_stage_headings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.preflight(root)
            baseline = self.publish(root, 4, "STAGE1_BASELINE", "runner-b",
                                    b"# STAGE1_BASELINE\n\nOriginal producer to consumer.\n")
            plan = self.publish(root, 5, "STAGE1_PLAN", "runner-b",
                                b"# STAGE1_PLAN\n\nAlternatives and falsifiers.\n")
            self.assertEqual("COMMITTED", baseline["status"])
            self.assertEqual("COMMITTED", plan["status"])
            self.assertEqual("NOT_ATTESTED_BY_MESSAGE_TRANSPORT", plan["admission"])
            self.assertFalse((root / "relay/STATE.yaml").exists())
            self.assertFalse((root / "relay/LEASES").exists())

    def test_negative_reject_baseline_with_wrong_stage_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.preflight(root)
            with self.assertRaisesRegex(TransactionError, "BUDDY_.*HEADING"):
                self.publish(root, 4, "STAGE1_BASELINE", "runner-b",
                             b"# Generic document\n\nNot an original baseline.\n")
            self.assertFalse((root / f"relay/TRANSACTIONS/TX.{ISSUE}.4").exists())

    def test_negative_reject_plan_with_wrong_stage_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.preflight(root)
            self.publish(root, 4, "STAGE1_BASELINE", "runner-b",
                         b"# STAGE1_BASELINE\n\nOriginal observation.\n")
            with self.assertRaisesRegex(TransactionError, "BUDDY_.*HEADING"):
                self.publish(root, 5, "STAGE1_PLAN", "runner-b",
                             b"# Arbitrary notes\n\nCannot substitute for B plan.\n")
            self.assertFalse((root / f"relay/TRANSACTIONS/TX.{ISSUE}.5").exists())

    def test_negative_new_intake_blocks_later_committed_old_serial_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.preflight(root)
            # Git commit/transaction chronology: newer intake is already COMMITTED,
            # but a producer later tries to backfill an unused smaller serial.
            self.publish(root, 10, "STAGE1_INTAKE", "operator",
                         b"# STAGE1_INTAKE\n\nSuperseding intake, version two.\n")
            with self.assertRaisesRegex(TransactionError, "BUDDY_.*(STALE|SEQUENCE|ORDER)"):
                self.publish(root, 4, "STAGE1_BASELINE", "runner-b",
                             b"# STAGE1_BASELINE\n\nBackfilled against version one.\n")
            self.assertFalse((root / f"relay/TRANSACTIONS/TX.{ISSUE}.4").exists())

    def test_negative_new_intake_blocks_later_committed_old_serial_plan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.preflight(root)
            self.publish(root, 4, "STAGE1_BASELINE", "runner-b",
                         b"# STAGE1_BASELINE\n\nEarlier original witness.\n")
            self.publish(root, 10, "STAGE1_INTAKE", "operator",
                         b"# STAGE1_INTAKE\n\nSuperseding intake, version two.\n")
            with self.assertRaisesRegex(TransactionError, "BUDDY_.*(STALE|SEQUENCE|ORDER)"):
                self.publish(root, 5, "STAGE1_PLAN", "runner-b",
                             b"# STAGE1_PLAN\n\nLate plan for superseded witness.\n")
            self.assertFalse((root / f"relay/TRANSACTIONS/TX.{ISSUE}.5").exists())


if __name__ == "__main__":
    unittest.main()
