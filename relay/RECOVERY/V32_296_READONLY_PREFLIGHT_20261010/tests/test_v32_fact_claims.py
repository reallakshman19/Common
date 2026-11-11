"""Native V3.2 comment observation, deliberately no production positive credit."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v32_fact_claims import NativeClaimAuditError, audit_native_comment_claims

SHA1 = "1" * 40
SHA2 = "2" * 40
LEAF = "v32-proto#4"


def graph(*, authors=None):
    return {"programme": {"repository": "lab/v32-proto", "fact_authors": authors or []}}


def checkpoint(*, head=SHA1, issue=LEAF, result="VERIFIED", evidence=True):
    evidence_refs = '      evidence_refs: [v32-proto#4#issuecomment-1]\n' if evidence else ''
    return (
        "Historical comments can contain unrelated prose.\n"
        "```yaml\nCHECKPOINT_FACTS_V1:\n"
        "  responsibility: {issue: " + issue + "}\n"
        "  material: {candidate_sha: '" + head + "'}\n"
        "  units:\n"
        "    - id: U01\n"
        "      state: COMPLETE\n"
        "      result: " + result + "\n"
        + evidence_refs +
        "```\n"
    )


def comment(body, login="maintainer", association="OWNER"):
    return {"id": 1, "body": body, "user": {"login": login}, "author_association": association}


def observe(comments, *, graph_value=None, head=SHA1):
    return audit_native_comment_claims(graph=graph_value or graph(), leaf_ref=LEAF,
                                       candidate_sha=head, comments=comments)


class NativeV32CommentObservationTests(unittest.TestCase):
    def test_01_no_checkpoint_blocks_stays_hold(self):
        r = observe([comment("Unrelated issue chat")])
        self.assertEqual(r["status"], "HOLD_NO_COMMENT_CLAIMS")
        self.assertEqual(r["blocks_seen"], 0)
        self.assertIsNone(r["accepted_evidence_count"])

    def test_02_native_structural_current_verified_claim_is_not_admitted(self):
        r = observe([comment(checkpoint())])
        self.assertEqual(r["blocks_seen"], 1)
        self.assertEqual(r["native_structural_claims"], 1)
        self.assertEqual(r["complete_verified_unit_claims"], 1)
        self.assertEqual(r["current_candidate_claims"], 1)
        self.assertEqual(r["status"], "HOLD_UNATTESTED_COMMENT_CLAIMS")
        self.assertEqual(r["provider_evidence_eligibility"], "UNKNOWN_NOT_ASSESSED")
        self.assertIsNone(r["accepted_evidence_count"])
        self.assertFalse(r["writer_authorized"])
        self.assertFalse(r["delp_invoked"])

    def test_03_foreign_author_visible_but_never_eligible(self):
        r = observe([comment(checkpoint(), login="stranger", association="NONE")])
        self.assertEqual(r["untrusted_author_claims"], 1)
        self.assertEqual(r["native_structural_claims"], 1)
        self.assertIsNone(r["accepted_evidence_count"])

    def test_04_explicit_allowlist_overrides_owner_association(self):
        r = observe([comment(checkpoint(), login="owner", association="OWNER")],
                    graph_value=graph(authors=["different-issuer"]))
        self.assertEqual(r["untrusted_author_claims"], 1)
        self.assertIsNone(r["accepted_evidence_count"])

    def test_05_stale_candidate_claim_is_not_current(self):
        r = observe([comment(checkpoint(head=SHA1))], head=SHA2)
        self.assertEqual(r["current_candidate_claims"], 0)
        self.assertEqual(r["stale_candidate_claims"], 1)
        self.assertEqual(r["native_structural_claims"], 1)

    def test_06_wrong_issue_claim_is_structurally_out_of_scope(self):
        r = observe([comment(checkpoint(issue="v32-proto#5"))])
        self.assertEqual(r["invalid_claims"], 1)
        self.assertEqual(r["native_structural_claims"], 0)

    def test_07_native_invalid_complete_claim_never_valid(self):
        r = observe([comment(checkpoint(evidence=False))])
        # Native validate_facts allows a COMPLETE unit without refs; this is
        # structurally valid but definitely not engineering verification.
        self.assertEqual(r["native_structural_claims"], 1)
        self.assertEqual(r["complete_verified_unit_claims"], 1)
        self.assertIsNone(r["accepted_evidence_count"])

    def test_08_malformed_yaml_is_fail_closed_not_silent_no_claims(self):
        bad = "```yaml\nCHECKPOINT_FACTS_V1:\n  material: [unfinished\n```"
        with self.assertRaisesRegex(NativeClaimAuditError, "CLAIM_AUDIT_NATIVE_BLOCK_PARSE_FAILED"):
            observe([comment(bad)])

    def test_09_duplicate_unknown_author_preserves_claim_count(self):
        r = observe([comment(checkpoint(), login="unknown", association="NONE"),
                     comment(checkpoint(head=SHA2), login="other", association="NONE")])
        self.assertEqual(r["blocks_seen"], 2)
        self.assertEqual(r["untrusted_author_claims"], 2)
        self.assertEqual(r["stale_candidate_claims"], 1)
        self.assertEqual(r["current_candidate_claims"], 1)

    def test_10_invalid_author_policy_is_not_a_default_grant(self):
        with self.assertRaisesRegex(NativeClaimAuditError, "CLAIM_AUDIT_AUTHOR_POLICY_INVALID"):
            observe([], graph_value={"programme": {"fact_authors": "everyone"}})


    def test_11_unquoted_numeric_SHA_is_type_ambiguous_not_stale(self):
        quoted = checkpoint()
        unquoted = quoted.replace("candidate_sha: '" + SHA1 + "'", "candidate_sha: " + SHA1)
        r = observe([comment(unquoted)])
        self.assertEqual(r["native_structural_claims"], 1)
        self.assertEqual(r["candidate_type_ambiguous_claims"], 1)
        self.assertEqual(r["stale_candidate_claims"], 0)
        self.assertEqual(r["current_candidate_claims"], 0)
        self.assertIsNone(r["accepted_evidence_count"])

if __name__ == "__main__":
    unittest.main()
