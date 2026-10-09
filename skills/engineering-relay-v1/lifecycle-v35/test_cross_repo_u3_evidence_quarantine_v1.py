"""Native R14 U1/U2/U3 cutover tests; synthetic references, NO imported approvals."""
from __future__ import annotations

import copy
import unittest

from test_evidence_review_contract_v1 import sample as historical_sample
from cross_repo_u3_evidence_quarantine_v1 import (
    CrossRepoEvidenceError, reconcile_u3_cutover,
)

OLD = "reallaksh19/Common"
NEW = "reallakshman19/Common"
SHA = "c" * 40
D = "sha256:" + "d" * 64


def sample():
    old = historical_sample()
    current = copy.deepcopy(old)
    identity = current["owner_session"]["identity"]
    identity["programme"].update(
        id="R14-NEW-REPO-CUTOVER-SYNTHETIC", repository=NEW, root_issue=5,
    )
    identity["owner_source_grade"] = "UNKNOWN"
    for role in ("graph_source", "session_source", "candidate_source"):
        identity[role]["repository"] = NEW
    identity["candidate_source"]["pr_number"] = 101

    for event in current["owner_session"]["owner_events"]:
        event.update(source_grade="UNKNOWN", source_url=None, content_sha256=None)
    for event in current["owner_session"]["session_events"]:
        event["session_id"] = "AGENT_B_SESSION"
        event["actor_label"] = "Agent B (unverified)"
    current["producer"] = {
        "session_id": "AGENT_B_SESSION", "actor_label": "Agent B (unverified)"
    }
    current["responsibility"].update(id="R14-NEW-U3", issue_number=100)
    current["checkpoint_facts"]["responsibility"]["issue"] = NEW + "#100"
    current["checkpoint_facts"]["material"]["pr"] = NEW + "#101"
    for unit in current["checkpoint_facts"]["units"]:
        unit.update(state="NOT_STARTED", result="NOT_RUN", evidence_refs=[])
    for observation in current["test_observations"]:
        observation.update(result="NOT_RUN", tested_head_sha=None, run_url=None)

    return {
        "schema": "relay-v35-cross-repo-u3-evidence-quarantine-v1",
        "mode": "RESEARCH_ONLY",
        "migration": {
            "historical": {
                "repository_id": 1207996454,
                "repository": OLD, "root_issue": 787,
                "leaf_issue": 878, "pr_number": 891,
            },
            "current": {
                "repository_id": 1412133785,
                "repository": NEW, "root_issue": 5,
                "leaf_issue": 100, "pr_number": 101,
            },
            "relation": "RELATED_NEW_IMPLEMENTATION",
            "historical_source_continuity": "NO_NATIVE_PR_REVIEW_CI_OR_OWNER_TRANSFER",
        },
        "historical_evidence": old, "current_evidence": current,
        "policy_adoption": "NOT_ADOPTED", "writer_state": "OFF",
    }


class U3CrossRepoMigrationTests(unittest.TestCase):
    def reject(self, doc, needle):
        with self.assertRaises(CrossRepoEvidenceError) as exc:
            reconcile_u3_cutover(doc)
        self.assertIn(needle, str(exc.exception))

    def test_positive_two_real_u3_contracts_remain_not_admitted(self):
        out = reconcile_u3_cutover(sample())
        self.assertEqual("QUARANTINED_NOT_TRANSFERRED", out["historical_evidence"])
        self.assertEqual("NEW_REPOSITORY_REVERIFICATION_REQUIRED", out["current_evidence"])
        self.assertEqual("CALLER_REFERENCED_UNATTESTED", out["source_grade"])
        self.assertEqual("NOT_EXECUTED", out["provider_acquisition"])
        self.assertEqual("NOT_AUTHENTICATED", out["original_owner"])
        self.assertEqual("NOT_QUALIFIED", out["independent_reviewer"])
        self.assertEqual("NOT_ADMITTED", out["delp_evidence_admission"])
        self.assertEqual("NOT_CALCULATED", out["canonical_delp_projection"])
        self.assertIsNone(out["programme_progress"])
        self.assertEqual("NOT_GRANTED", out["writer_authorization"])
        self.assertEqual("NOT_PROVEN", out["successor_lease"])

    def test_old_verified_and_pass_with_real_refs_do_not_transfer(self):
        doc = sample()
        self.assertEqual("VERIFIED", doc["historical_evidence"]["checkpoint_facts"]["units"][0]["result"])
        self.assertEqual("PASS", doc["historical_evidence"]["test_observations"][0]["result"])
        out = reconcile_u3_cutover(doc)
        self.assertEqual("NOT_ADMITTED", out["delp_evidence_admission"])

    def test_historical_verified_currently_claimed_without_own_tests_rejected(self):
        doc = sample()
        doc["current_evidence"]["checkpoint_facts"]["units"][0].update(
            state="COMPLETE", result="VERIFIED",
            evidence_refs=[OLD + "#878#issuecomment-6083423582"],
        )
        self.reject(doc, "HISTORICAL_UNIT_EVIDENCE_PROMOTED")

    def test_copied_test_pass_satisfying_head_shape_still_rejected(self):
        doc = sample()
        doc["current_evidence"]["test_observations"][0].update(
            result="PASS", tested_head_sha=SHA,
            run_url=f"https://github.com/{NEW}/actions/runs/123",
        )
        self.reject(doc, "HISTORICAL_CI_PROMOTED")

    def test_copied_reviewer_claim_even_different_label_is_not_admitted(self):
        doc = sample()
        review = doc["current_evidence"]["reviewer_claim"]
        review.update(state="CLAIMED_ACCEPTED", actor_label="Third reviewer",
                      session_id="REVIEWER_SESSION", candidate_sha=SHA,
                      source_url=f"https://github.com/{NEW}/pull/101#pullrequestreview-12",
                      source_digest=D)
        self.reject(doc, "HISTORICAL_REVIEW_PROMOTED")

    def test_reusing_old_session_label_is_not_custody(self):
        doc = sample()
        doc["current_evidence"]["producer"]["session_id"] = (
            doc["historical_evidence"]["producer"]["session_id"]
        )
        # A malformed producer history fails even before migration custody check.
        self.reject(doc, "CURRENT_U3_INVALID")

    def test_forged_current_owner_mirror_grade_rejected(self):
        doc = sample()
        doc["current_evidence"]["owner_session"]["identity"]["owner_source_grade"] = (
            "GITHUB_VERBATIM_MIRROR"
        )
        self.reject(doc, "HISTORICAL_OWNER_MIRROR_PROMOTED")

    def test_owner_url_copied_into_unknown_current_rejected_by_u2(self):
        doc = sample()
        doc["current_evidence"]["owner_session"]["owner_events"][0]["source_url"] = (
            f"https://github.com/{OLD}/issues/787#issuecomment-1"
        )
        self.reject(doc, "CURRENT_U3_INVALID")

    def test_wrong_new_repo_source_identity_fails_u1(self):
        doc = sample()
        doc["current_evidence"]["owner_session"]["identity"]["graph_source"]["repository"] = OLD
        self.reject(doc, "CURRENT_U3_INVALID")

    def test_wrong_current_root_binding_fails(self):
        doc = sample()
        doc["migration"]["current"]["root_issue"] = 6
        self.reject(doc, "CURRENT_SOURCE_ROLE_BINDING_MISMATCH")

    def test_wrong_current_leaf_issue_ref_fails(self):
        doc = sample()
        doc["migration"]["current"]["leaf_issue"] = 99
        self.reject(doc, "CURRENT_SOURCE_ROLE_BINDING_MISMATCH")

    def test_wrong_new_pr_ref_fails(self):
        doc = sample()
        doc["migration"]["current"]["pr_number"] = 102
        self.reject(doc, "CURRENT_SOURCE_ROLE_BINDING_MISMATCH")

    def test_foreign_old_root_claim_fails(self):
        doc = sample()
        doc["migration"]["historical"]["root_issue"] = 788
        self.reject(doc, "HISTORICAL_SOURCE_ROLE_BINDING_MISMATCH")

    def test_same_repo_id_or_namespace_cannot_be_cutover(self):
        doc = sample()
        doc["migration"]["current"]["repository_id"] = 1207996454
        self.reject(doc, "REPOSITORY_IDENTITY_NOT_DISTINCT")
        doc = sample()
        doc["migration"]["current"]["repository"] = OLD
        self.reject(doc, "REPOSITORY_IDENTITY_NOT_DISTINCT")

    def test_self_parent_leaf_invalid_before_progress(self):
        doc = sample()
        doc["migration"]["current"]["leaf_issue"] = 5
        self.reject(doc, "CURRENT_LEAF_IS_ROOT")

    def test_forged_writer_evidence_percent_and_adopted_policy_rejected_by_schema(self):
        for section, name, value in (
            (None, "evidence_percent", 100),
            (None, "writer_authorized", True),
            (None, "policy_adoption", "ADOPTED"),
            (None, "writer_state", "ON"),
        ):
            with self.subTest(name=name):
                doc = sample()
                doc[name] = value
                self.reject(doc, "SCHEMA_INVALID")

    def test_mutations_change_digest_not_admission(self):
        doc = sample()
        first = reconcile_u3_cutover(doc)
        doc["historical_evidence"]["checkpoint_facts"]["units"][0]["result"] = "FAILED"
        later = reconcile_u3_cutover(doc)
        self.assertNotEqual(first["binding_sha256"], later["binding_sha256"])
        self.assertEqual("NOT_ADMITTED", later["delp_evidence_admission"])

    def test_claimed_stopped_producer_blocks_new_reconciliation(self):
        doc = sample()
        events = doc["current_evidence"]["owner_session"]["session_events"]
        events.append({
            "id": "S003", "session_id": "AGENT_B_SESSION",
            "actor_label": "Agent B (unverified)",
            "kind": "STOP_CLAIMED", "owner_event_id": "O002",
            "source_commit": "b" * 40, "predecessor_id": "S002",
        })
        # Native U3 already rejects a stopped producer; this pre-admission
        # wrapper must never weaken or reinterpret that denial as a fence.
        self.reject(doc, "PRODUCER_SESSION_CLAIMED_STOPPED")

    def test_current_complete_failed_facts_not_copied_as_complete(self):
        doc = sample()
        doc["current_evidence"]["checkpoint_facts"]["units"][0].update(
            state="COMPLETE", result="FAILED"
        )
        self.reject(doc, "HISTORICAL_UNIT_EVIDENCE_PROMOTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
