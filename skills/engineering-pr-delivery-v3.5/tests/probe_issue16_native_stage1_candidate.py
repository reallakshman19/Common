"""Issue #16 read-only conformance probe for a separately pinned native PR #2 checkout.

Unlike the issue16 reviewer text validator, this calls the REAL V3.2
transactionlib._validate_buddy_markdown_transaction() implementation.
It does NOT write Relay source/state, execute() or assert true B isolation.

One external prerequisite is explicitly mocked: _require_buddy_sequence() is
replaced for this narrow payload-admission test so missing historical receipts
do not mask a stage/heading acceptance defect. This MUST NOT be interpreted
as a real native end-to-end transaction or an independently attested freeze.
"""
from __future__ import annotations

import argparse
import importlib
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


class NativeBuddyHeadingContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native_root = pathlib.Path(_ARGUMENTS.native_root).resolve()
        cls.expected_sha = _ARGUMENTS.expected_native_sha.lower()
        observed = subprocess.check_output(
            ["git", "-C", str(cls.native_root), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        if observed != cls.expected_sha:
            raise RuntimeError(
                f"NATIVE_SOURCE_HEAD_MISMATCH: expected {cls.expected_sha}; found {observed}"
            )
        source = (
            cls.native_root
            / "skills/engineering-pr-delivery-v3.2/scripts"
        )
        if not (source / "transactionlib.py").is_file():
            raise RuntimeError(f"NATIVE_SOURCE_MISSING: {source}")
        sys.path.insert(0, str(source))
        cls.transactionlib = importlib.import_module("transactionlib")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)

    def _submit(self, stage: str, payload: bytes) -> None:
        seq = 4 if stage == "STAGE1_BASELINE" else 5
        target = (
            f"relay/CONTINUITY/episodes/ISSUE-889/messages/"
            f"TX.889.{seq}-{stage}.md"
        )
        lib = self.transactionlib
        with mock.patch.object(lib, "_require_buddy_sequence", return_value=None):
            lib._validate_buddy_markdown_transaction(
                self.root,
                f"TX.889.{seq}",
                "runner-b",
                {target: payload},
            )

    def _must_reject_stage_heading(self, stage, payload):
        lib = self.transactionlib
        try:
            self._submit(stage, payload)
        except lib.TransactionError as error:
            self.assertRegex(
                str(error),
                r"(?:HEADING|COMBINED|STAGE1_)",
                f"wrong rejection reason: {error}",
            )
        else:
            self.fail(
                "NATIVE_STAGE1_HEADING_GAP: published stage accepts noncanonical "
                f"B-authored {stage} bytes at native ingress"
            )

    def test_canonical_baseline_is_admitted_by_content_gate(self):
        self._submit(
            "STAGE1_BASELINE",
            b"# STAGE1_BASELINE\n\nOriginal source -> consumer observation.\n",
        )

    def test_canonical_plan_no_change_is_admitted_by_content_gate(self):
        self._submit(
            "STAGE1_PLAN",
            b"# STAGE1_PLAN\n\nNO_CHANGE: observed original behavior meets the Owner requirement.\n",
        )

    def test_generic_baseline_heading_is_rejected(self):
        self._must_reject_stage_heading(
            "STAGE1_BASELINE",
            b"# Source producer and consumer witness\n\nOriginal evidence.\n",
        )

    def test_generic_plan_heading_is_rejected(self):
        self._must_reject_stage_heading(
            "STAGE1_PLAN",
            b"# Two alternate HOWs and falsifiers\n\nPlan.\n",
        )

    def test_baseline_content_cannot_be_submitted_as_plan(self):
        self._must_reject_stage_heading(
            "STAGE1_PLAN",
            b"# STAGE1_BASELINE\n\nFacts mistakenly labelled a plan.\n",
        )

    def test_combined_stage1_document_is_rejected(self):
        self._must_reject_stage_heading(
            "STAGE1_BASELINE",
            b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN\n\nPlan.\n",
        )

    def test_embedded_plan_heading_with_crlf_is_rejected(self):
        self._must_reject_stage_heading(
            "STAGE1_BASELINE",
            b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN\r\nPlan.\n",
        )

    def test_embedded_plan_heading_with_trailing_spaces_is_rejected(self):
        self._must_reject_stage_heading(
            "STAGE1_BASELINE",
            b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN  \nPlan.\n",
        )

    def test_embedded_plan_heading_at_eof_is_rejected(self):
        self._must_reject_stage_heading(
            "STAGE1_BASELINE",
            b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", required=True)
    parser.add_argument("--expected-native-sha", required=True)
    _ARGUMENTS = parser.parse_args()
    if not __import__("re").fullmatch(r"[0-9a-f]{40}", _ARGUMENTS.expected_native_sha):
        parser.error("--expected-native-sha must be a full 40-character lowercase SHA")
    unittest.main(argv=[sys.argv[0], "-v"], exit=True)
