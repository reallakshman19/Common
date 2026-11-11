"""Issue #16: execute REAL native Buddy publisher and direct transaction paths.

Target repository is a separate immutable checkout of protected PR #2.
Unlike the earlier payload-only test, this replays the genuine committed
intake -> dispatch request -> dispatch observation -> Stage1 baseline/plan
chain. No native functions are mocked. All writes are to disposable tmpdirs,
never to the checked-out native source, real Relay state or a live issue.

The operator/session/read-scope strings are SYNTHETIC. This proves receipt
and payload acceptance behavior only. It cannot establish actual B tool
isolation, provider identity, Owner permission or a completed freeze.
"""
from __future__ import annotations

import argparse
import importlib
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ISSUE = 889
PINNED_SHA = None
NATIVE_ROOT = None


def native_module(name):
    return importlib.import_module(name)


class NativeBuddyFullIngressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not re.fullmatch(r"[0-9a-f]{40}", PINNED_SHA or ""):
            raise RuntimeError("EXACT_NATIVE_SHA_REQUIRED")
        observed = subprocess.check_output(
            ["git", "-C", str(NATIVE_ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        if observed != PINNED_SHA:
            raise RuntimeError(
                f"NATIVE_HEAD_MOVED: expected {PINNED_SHA}, observed {observed}"
            )
        scripts = (
            pathlib.Path(NATIVE_ROOT)
            / "skills/engineering-pr-delivery-v3.2/scripts"
        )
        if not (scripts / "relay_tx.py").is_file() or not (
            scripts / "transactionlib.py"
        ).is_file():
            raise RuntimeError(f"PROTECTED_CANDIDATE_FILES_MISSING: {scripts}")
        sys.path.insert(0, str(scripts))
        cls.cli = native_module("relay_tx")
        cls.tx = native_module("transactionlib")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)

    def _publish(self, seq, stage, actor, body):
        return self.cli.publish_buddy_markdown(
            self.root,
            issue_number=ISSUE,
            tx_id=f"TX.{ISSUE}.{seq}",
            stage=stage,
            actor=actor,
            markdown=body,
        )

    def _build_real_prior_receipts(self, stage):
        stages = (
            (1, "STAGE1_INTAKE", "operator",
             b"# Historical Owner and original source\n\nSynthesized intake for transport test.\n"),
            (2, "DISPATCH_REQUEST", "operator",
             b"# Dispatch original-only request\n\nSynthetic.\n"),
            (3, "DISPATCH_OBSERVATION", "operator",
             b"# RUNNER_EXECUTION_OBSERVED\n\nSession ref: synthetic-runner-b\nRead-scope ref: synthetic-original-only\n"),
        )
        for seq, phase, actor, raw in stages:
            receipt = self._publish(seq, phase, actor, raw)
            self.assertEqual(receipt["status"], "COMMITTED")
            self.assertEqual(
                receipt["admission"],
                "NOT_ATTESTED_BY_MESSAGE_TRANSPORT",
            )
        if stage == "STAGE1_PLAN":
            receipt = self._publish(
                4, "STAGE1_BASELINE", "runner-b",
                b"# STAGE1_BASELINE\n\nOriginal producer -> consumer synthetic witness.\n",
            )
            self.assertEqual(receipt["status"], "COMMITTED")

    def _submit(self, stage, raw, route):
        seq = 4 if stage == "STAGE1_BASELINE" else 5
        txid = f"TX.{ISSUE}.{seq}"
        target = (
            f"relay/CONTINUITY/episodes/ISSUE-{ISSUE}/messages/"
            f"{txid}-{stage}.md"
        )
        if route == "wrapper":
            return self._publish(seq, stage, "runner-b", raw)
        if route == "direct_execute":
            return self.tx.execute(
                self.root,
                tx_id=txid,
                command="PUBLISH_BUDDY_MARKDOWN",
                actor="runner-b",
                replacements={target: raw},
            )
        raise AssertionError("UNSUPPORTED_ROUTE")

    def _exercise(self, stage, raw, route, expect_reject):
        self._build_real_prior_receipts(stage)
        seq = 4 if stage == "STAGE1_BASELINE" else 5
        txid = f"TX.{ISSUE}.{seq}"
        target = self.root / (
            f"relay/CONTINUITY/episodes/ISSUE-{ISSUE}/messages/"
            f"{txid}-{stage}.md"
        )
        manifest = self.root / f"relay/TRANSACTIONS/{txid}/manifest.yaml"
        self.assertFalse(target.exists())
        self.assertFalse(manifest.exists())

        if expect_reject:
            try:
                self._submit(stage, raw, route)
            except self.tx.TransactionError as error:
                # A failing earlier sequence/permission step cannot masquerade
                # as correctly enforced content admission.
                self.assertRegex(
                    str(error),
                    r"BUDDY_.*(?:STAGE1|HEADING|COMBINED)",
                    f"WRONG_REJECTION_REASON: {error}",
                )
                self.assertFalse(target.exists(), "BAD_STAGE1_FILE_COMMITTED")
                self.assertFalse(manifest.exists(), "BAD_STAGE1_MANIFEST_STAGED")
            else:
                self.fail(
                    f"NATIVE_FULL_INGRESS_GAP: route={route}, stage={stage}: "
                    "committed malformed B-authored original document"
                )
        else:
            result = self._submit(stage, raw, route)
            self.assertEqual(result["status"], "COMMITTED")
            self.assertEqual(target.read_bytes(), raw)
            self.assertTrue(manifest.is_file())
            self.assertFalse((self.root / "relay/STATE.yaml").exists())
            self.assertFalse((self.root / "relay/LEASES").exists())
            self.assertFalse((self.root / "relay/EVENTS.jsonl").exists())

    def test_valid_canonical_baseline_via_wrapper(self):
        self._exercise(
            "STAGE1_BASELINE",
            b"# STAGE1_BASELINE\n\nObserved original source and consumer.\n",
            "wrapper", False,
        )

    def test_valid_no_change_plan_via_direct_execute(self):
        self._exercise(
            "STAGE1_PLAN",
            b"# STAGE1_PLAN\n\nNO_CHANGE: original condition satisfies WHAT.\n",
            "direct_execute", False,
        )


MALFORMED = {
    "generic_baseline": (
        "STAGE1_BASELINE",
        b"# Source producer and consumer witness\n\nIncorrect heading.\n",
    ),
    "generic_plan": (
        "STAGE1_PLAN",
        b"# Two alternate HOWs and falsifiers\n\nIncorrect heading.\n",
    ),
    "baseline_relabelled_plan": (
        "STAGE1_PLAN",
        b"# STAGE1_BASELINE\n\nMislabelled original document.\n",
    ),
    "combined_baseline_and_plan": (
        "STAGE1_BASELINE",
        b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN\n\nPlan.\n",
    ),
    "combined_crlf_second_heading": (
        "STAGE1_BASELINE",
        b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN\r\nPlan.\n",
    ),
    "combined_padded_second_heading": (
        "STAGE1_BASELINE",
        b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN  \nPlan.\n",
    ),
    "combined_second_heading_eof": (
        "STAGE1_BASELINE",
        b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN",
    ),
}


def make_negative_case(stage, raw, route):
    def exercise(self):
        self._exercise(stage, raw, route, True)
    return exercise


for label, (stage, raw) in MALFORMED.items():
    for route in ("wrapper", "direct_execute"):
        setattr(
            NativeBuddyFullIngressTests,
            f"test_reject_{label}_via_{route}",
            make_negative_case(stage, raw, route),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", required=True)
    parser.add_argument("--expected-native-sha", required=True)
    args = parser.parse_args()
    NATIVE_ROOT = pathlib.Path(args.native_root).resolve()
    PINNED_SHA = args.expected_native_sha
    unittest.main(argv=[sys.argv[0], "-v"], exit=True)
