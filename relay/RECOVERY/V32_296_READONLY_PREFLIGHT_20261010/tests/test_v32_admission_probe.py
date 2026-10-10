"""Negative/source-currentness executable tests, never real acceptance evidence."""
from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v32_admission_probe import ObservedCheck, SourceSelection, probe_v32_fact, V32_FACTS_SCHEMA

H1 = "1" * 40
H2 = "2" * 40


def selected(**kwargs):
    return replace(SourceSelection(
        repository="reallakshman19/Common", leaf_ref="Common#30", pr_number=292,
        current_head=H1, observed_pr_repository="reallakshman19/Common",
        observed_pr_number=292, original_source_state="VERIFIED",
        released_graph_state="VERIFIED", evidence_policy_state="VERIFIED",
        required_check_policy_state="VERIFIED", independent_review_state="VERIFIED",
    ), **kwargs)


def facts(sha=H1):
    return {
        "schema": V32_FACTS_SCHEMA,
        "responsibility": {"issue": "Common#30"},
        "material": {"candidate_sha": sha, "pr": "Common#292"},
        "units": [{"id": "U01", "state": "COMPLETE", "result": "VERIFIED",
                   "evidence_refs": ["https://github.com/example/real-reference"], "candidate_sha": sha}],
    }


def checks(sha=H1, conclusion="success", executed=True):
    return [ObservedCheck("unit-runtime", sha, conclusion, executed)]


class ReadOnlyAdmissionProbeTests(unittest.TestCase):
    def test_01_matching_claims_still_cannot_mint_e(self):
        result = probe_v32_fact(selected(), facts(), checks())
        self.assertEqual(result.state, "HOLD_NOT_AN_EVIDENCE_ISSUER")
        self.assertIsNone(result.accepted_evidence_count)
        self.assertFalse(result.delp_invoked)
        self.assertFalse(result.writer_authorized)

    def test_02_head_movement_invalidates_previous_claim(self):
        result = probe_v32_fact(selected(current_head=H2), facts(H1), checks(H1))
        self.assertIn("FACT_CANDIDATE_STALE", result.reasons)
        self.assertIn("SELECTED_CHECK_WRONG_HEAD:unit-runtime", result.reasons)

    def test_03_current_h2_claim_not_independently_admitted(self):
        result = probe_v32_fact(selected(current_head=H2), facts(H2), checks(H2))
        self.assertEqual(result.state, "HOLD_NOT_AN_EVIDENCE_ISSUER")

    def test_04_wrong_provider_repository_rejected(self):
        result = probe_v32_fact(selected(observed_pr_repository="reallaksh19/Common"), facts(), checks())
        self.assertIn("PR_PROVIDER_IDENTITY_MISMATCH", result.reasons)

    def test_05_unknown_required_ci_policy_holds(self):
        result = probe_v32_fact(selected(required_check_policy_state="UNKNOWN"), facts(), checks())
        self.assertIn("EFFECTIVE_REQUIRED_CHECK_POLICY_NOT_AUTHENTICATED", result.reasons)

    def test_06_missing_independent_review_holds(self):
        result = probe_v32_fact(selected(independent_review_state="UNKNOWN"), facts(), checks())
        self.assertIn("INDEPENDENT_REVIEWS_NOT_AUTHENTICATED", result.reasons)

    def test_07_no_source_graph_holds(self):
        result = probe_v32_fact(selected(released_graph_state="UNKNOWN"), facts(), checks())
        self.assertIn("RELEASED_GRAPH_NOT_AUTHENTICATED", result.reasons)

    def test_08_failed_selected_check_rejected(self):
        result = probe_v32_fact(selected(), facts(), checks(conclusion="failure"))
        self.assertIn("SELECTED_CHECK_FAILED:unit-runtime", result.reasons)

    def test_09_skipped_check_not_a_pass(self):
        result = probe_v32_fact(selected(), facts(), checks(conclusion="skipped", executed=False))
        self.assertIn("CHECK_NOT_EXECUTED:unit-runtime", result.reasons)
        self.assertEqual(result.state, "HOLD_NOT_RUN")

    def test_10_no_selected_checks_not_run(self):
        result = probe_v32_fact(selected(), facts(), ())
        self.assertIn("SELECTED_CHECKS_NOT_RUN_OR_NOT_OBSERVED", result.reasons)
        self.assertEqual(result.state, "HOLD_NOT_RUN")

    def test_11_non_native_fact_schema_rejected(self):
        bad = facts(); bad["schema"] = "relay-v3.5-facts"
        self.assertIn("FACT_SCHEMA_NOT_NATIVE_V32", probe_v32_fact(selected(), bad, checks()).reasons)

    def test_12_non_verified_claim_rejected(self):
        bad = facts(); bad["units"][0]["result"] = "NOT_RUN"
        self.assertIn("COMPLETE_UNIT_HAS_NO_CURRENT_VERIFICATION_CLAIM", probe_v32_fact(selected(), bad, checks()).reasons)

    def test_13_missing_fact_is_unknown(self):
        self.assertIn("FACTS_ABSENT", probe_v32_fact(selected(), None, checks()).reasons)

    def test_14_pr_binding_mismatch(self):
        bad = facts(); bad["material"]["pr"] = "Common#291"
        self.assertIn("FACT_PR_NOT_BOUND", probe_v32_fact(selected(), bad, checks()).reasons)

    def test_15_origin_not_authenticated_holds(self):
        result = probe_v32_fact(selected(original_source_state="UNKNOWN"), facts(), checks())
        self.assertIn("ORIGINAL_OWNER_SOURCE_NOT_AUTHENTICATED", result.reasons)

    def test_16_non_array_units_fail_closed(self):
        bad = facts(); bad["units"] = "COMPLETE"
        self.assertIn("FACT_UNITS_INVALID", probe_v32_fact(selected(), bad, checks()).reasons)

    def test_17_never_claims_acceptance_even_with_author_labelled_verified(self):
        bad = facts(); bad["units"][0]["evidence_refs"] = ["self-authored:verification"]
        result = probe_v32_fact(selected(), bad, checks())
        self.assertFalse(result.as_dict()["delp_invoked"])
        self.assertIsNone(result.as_dict()["accepted_evidence_count"])
        self.assertNotEqual(result.state, "ADMITTED")


if __name__ == "__main__":
    unittest.main()
