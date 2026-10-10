"""Real unchanged native V3.2 C6 is called; all inputs synthetic and HOLD-only.

The fake provider models GET endpoints, never production Owner release.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v32_c6_preview import inspect_v32_c6_read_only
from v32_provider_preflight import PreflightTarget
from test_v32_provider_preflight import FakeProvider, H1, H2

# Existing official test fixture: never a released new-repo Owner source.
# The historical source has a genuinely released-form Proposal-V2 *shape*,
# which the native C6 code requires. No real old-repo provider is contacted.
FIXTURE = (Path(__file__).resolve().parents[4] /
           ".github/v32-evidence-spine/fixtures/718-c0-source-graph.json")
HISTORICAL_REPO = "reallaksh19/Common"


class C6PreviewProvider(FakeProvider):
    def __init__(self):
        super().__init__()
        self.graph = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.pr_base_repository = HISTORICAL_REPO

    def get_repository(self, repository):
        self._before("repo")
        return {"full_name": HISTORICAL_REPO, "id": self.repo_id, "default_branch": "main"}

    def get_issue(self, repository, number):
        self._before("issue")
        return {
            "number": number, "state": "open",
            "title": "Synthetic issue", "body": "Synthetic baseline",
        }

    def get_pull(self, repository, number):
        row = super().get_pull(repository, number)
        row["number"] = 722
        row["state"] = "open"
        row["merged"] = False
        return row


def target():
    return PreflightTarget(
        repository=HISTORICAL_REPO, repository_id=112233,
        graph_path=".github/v32-evidence-spine/fixtures/718-c0-source-graph.json",
        leaf_ref="Common#720", pr_number=722,
    )


def run(p, frozen=None):
    return inspect_v32_c6_read_only(
        target(), p, frozen_basis=frozen,
    )


class RealNativeC6BridgeTests(unittest.TestCase):
    def test_01_real_native_c6_uses_same_source_and_held_authority(self):
        row = run(C6PreviewProvider())
        self.assertEqual(row["status"], "HOLD_C6_SOURCE_UNADMITTED", row)
        self.assertTrue(row["native_c6_invoked"], row)
        self.assertEqual(row["c6_reconstruction"]["native_source_currentness"], "CURRENT_READ_ONLY")
        self.assertEqual(row["c6_reconstruction"]["owner_source_status"], "UNRESOLVED_CHAT_MESSAGE_LINK")
        self.assertEqual(row["c6_reconstruction"]["moved_axes"], [])
        self.assertEqual(row["execution_admission"], "NEVER_FROM_RECONSTRUCTION")
        self.assertIsNone(row["accepted_evidence_count"])
        self.assertFalse(row["writer_authorized"])
        self.assertFalse(row["delp_admitted"])

    def test_02_same_frozen_source_digest_is_stable_but_unadmitted(self):
        p = C6PreviewProvider()
        first = run(p)
        self.assertTrue(first["native_c6_invoked"], first)
        second = run(p, first["current_source_basis"])
        self.assertEqual(second["status"], "HOLD_C6_SOURCE_UNADMITTED", second)
        self.assertEqual(second["current_source_basis"], first["current_source_basis"])
        self.assertEqual(second["c6_reconstruction"]["moved_axes"], [])

    def test_03_moved_candidate_forces_native_c6_reconciliation(self):
        p = C6PreviewProvider()
        first = run(p)
        self.assertTrue(first["native_c6_invoked"], first)
        p.sha = H2
        p.checks[0]["head_sha"] = H2
        second = run(p, first["current_source_basis"])
        self.assertEqual(second["status"], "HOLD_C6_RECONCILE_REQUIRED", second)
        self.assertTrue(second["native_c6_invoked"])
        self.assertIn("input", second["c6_reconstruction"]["moved_axes"])
        self.assertFalse(second["writer_authorized"])

    def test_04_historical_foreign_repo_graph_stops_before_native_c6(self):
        p = C6PreviewProvider()
        p.graph["programme"]["repository"] = "historic/v32-proto"
        row = run(p)
        self.assertEqual(row["status"], "HOLD_PREFLIGHT_SOURCE")
        self.assertEqual(row["source_status"], "HOLD_PROVIDER_READ")
        self.assertFalse(row["native_c6_invoked"])
        self.assertIsNone(row["current_source_basis"])

    def test_05_graph_without_native_units_stops_before_c6(self):
        p = C6PreviewProvider()
        p.graph["nodes"][1].pop("units")
        row = run(p)
        self.assertEqual(row["status"], "HOLD_PREFLIGHT_SOURCE")
        self.assertFalse(row["native_c6_invoked"])

    def test_06_unknown_or_failed_issue_provider_does_not_authorize_c6(self):
        p = C6PreviewProvider()
        def broken_issue(*args):
            raise OSError("sensitive issue response")
        p.get_issue = broken_issue
        row = run(p)
        self.assertEqual(row["status"], "HOLD_C6_SOURCE_READ")
        self.assertEqual(row["reasons"], ["NATIVE_C6_SOURCE_UNAVAILABLE_OR_INVALID"])
        self.assertNotIn("sensitive", str(row))
        self.assertFalse(row["writer_authorized"])

    def test_07_changed_parent_title_against_frozen_basis_reconciles(self):
        p = C6PreviewProvider()
        first = run(p)
        self.assertTrue(first["native_c6_invoked"], first)
        p.issue_title = "changed"
        parent = p.get_issue
        def changed_issue(repo, number):
            row = parent(repo, number)
            row["title"] = p.issue_title
            return row
        p.get_issue = changed_issue
        moved = run(p, first["current_source_basis"])
        self.assertEqual(moved["status"], "HOLD_C6_RECONCILE_REQUIRED")
        self.assertIn("provider", moved["c6_reconstruction"]["moved_axes"])

    def test_08_bad_frozen_basis_is_closed_without_auth(self):
        row = run(C6PreviewProvider(), {"input": "sha256:" + "0" * 64})
        self.assertEqual(row["status"], "HOLD_C6_SOURCE_READ")
        self.assertFalse(row["native_c6_invoked"])
        self.assertFalse(row["writer_authorized"])


if __name__ == "__main__":
    unittest.main()
