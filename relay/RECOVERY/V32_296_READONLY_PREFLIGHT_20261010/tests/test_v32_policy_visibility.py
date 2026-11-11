"""Negative D4/D5 source visibility tests; no reviewer/CI authority is minted."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v32_policy_visibility import observe_review_and_policy_visibility

REPO = "lab/v32-proto"
H1 = "a" * 40
H2 = "b" * 40


class Provider:
    def __init__(self):
        self.calls = []
        self.sha = H1
        self.base_name = REPO
        self.base_ref = "main"
        self.reviews = []
        self.rulesets = []
        self.active_rules = []
        self.active_error = None
        self.classic = OSError("403")
        self.review_error = None
        self.ruleset_error = None
        self.pr_reads = 0
        self.move_on_second_read = False

    def get_pull(self, repository, number):
        self.calls.append("pull")
        self.pr_reads += 1
        if self.move_on_second_read and self.pr_reads == 2:
            self.sha = H2
        return {
            "number": 7, "head": {"sha": self.sha, "repo": {"full_name": REPO}},
            "base": {"ref": self.base_ref, "repo": {"full_name": self.base_name}},
            "user": {"login": "coder"},
        }

    def get_pr_reviews(self, repository, number):
        self.calls.append("reviews")
        if self.review_error:
            raise self.review_error
        return list(self.reviews)

    def get_branch_rulesets(self, repository, branch):
        self.calls.append("rulesets")
        if self.ruleset_error:
            raise self.ruleset_error
        return list(self.rulesets)

    def get_active_branch_rules(self, repository, branch):
        self.calls.append("active_rules")
        if self.active_error:
            raise self.active_error
        return list(self.active_rules)

    def get_branch_required_checks(self, repository, branch):
        self.calls.append("classic")
        if isinstance(self.classic, Exception):
            raise self.classic
        return dict(self.classic)


def review(id, login, *, state="APPROVED", commit=H1):
    return {"id": id, "user": {"login": login}, "state": state, "commit_id": commit}


def run(provider=None, head=H1, repository=REPO):
    return observe_review_and_policy_visibility(
        provider or Provider(), repository=repository, pr_number=7, expected_head=head
    )


class NativeV32PolicyVisibilityTests(unittest.TestCase):
    def test_01_empty_rulesets_and_classic_403_never_waive_required_ci(self):
        out = run().as_dict()
        self.assertEqual(out["status"], "HOLD_D4_D5_AUTHORITY_UNKNOWN")
        self.assertEqual(out["required_policy_endpoints"]["rulesets"], "OBSERVED_EMPTY")
        self.assertEqual(out["required_policy_endpoints"]["classic_required_checks"], "UNKNOWN")
        self.assertEqual(out["required_policy_endpoints"]["active_branch_rules"], "OBSERVED_EMPTY")
        self.assertEqual(out["effective_required_check_policy"], "UNKNOWN_NOT_AUTHENTICATED")
        self.assertIsNone(out["accepted_evidence_count"])
        self.assertFalse(out["writer_authorized"])
        self.assertFalse(out["delp_invoked"])

    def test_02_same_head_approval_is_only_observation(self):
        p = Provider(); p.reviews = [review(1, "reviewer")]
        o = run(p)
        self.assertEqual(o.exact_head_latest_approvals, 1)
        self.assertEqual(o.distinct_latest_approved_reviewers, 1)
        self.assertEqual(o.independent_review_authority, "UNKNOWN_NOT_AUTHENTICATED")

    def test_03_stale_approval_not_current(self):
        p = Provider(); p.reviews = [review(1, "reviewer", commit=H2)]
        self.assertEqual(run(p).exact_head_latest_approvals, 0)

    def test_04_later_changes_requested_is_not_approved(self):
        p = Provider(); p.reviews = [review(1, "reviewer"), review(2, "reviewer", state="CHANGES_REQUESTED")]
        self.assertEqual(run(p).distinct_latest_approved_reviewers, 0)

    def test_05_pr_author_approval_not_counted(self):
        p = Provider(); p.reviews = [review(1, "coder")]
        self.assertEqual(run(p).distinct_latest_approved_reviewers, 0)

    def test_06_moved_head_between_reads_holds(self):
        p = Provider(); p.move_on_second_read = True
        o = run(p)
        self.assertEqual(o.status, "HOLD_MOVED_SOURCE")
        self.assertIsNone(o.observed_candidate)

    def test_07_stale_requested_head_refused_without_review_reads(self):
        p = Provider()
        o = run(p, head=H2)
        self.assertEqual(o.status, "HOLD_STALE_CANDIDATE")
        self.assertEqual(p.calls, ["pull"])

    def test_08_ruleset_read_unknown_is_not_no_requirements(self):
        p = Provider(); p.ruleset_error = OSError("403")
        o = run(p)
        self.assertIn("RULESET_ENDPOINT_UNKNOWN", o.reasons)
        self.assertEqual(o.required_policy_endpoints["rulesets"], "UNKNOWN")
        self.assertEqual(o.effective_required_check_policy, "UNKNOWN_NOT_AUTHENTICATED")

    def test_09_classic_and_rulesets_visible_still_not_complete_policy(self):
        p = Provider()
        p.classic = {"contexts": ["build"]}
        p.rulesets = [{"id": 20, "name": "source control rule"}]
        o = run(p)
        self.assertEqual(o.required_policy_endpoints["rulesets"], "OBSERVED_UNQUALIFIED")
        self.assertEqual(o.required_policy_endpoints["classic_required_checks"], "OBSERVED_UNQUALIFIED")
        self.assertEqual(o.status, "HOLD_D4_D5_AUTHORITY_UNKNOWN")

    def test_10_review_endpoint_failure_keeps_unknown_not_zero_verdict(self):
        p = Provider(); p.review_error = OSError("not accessible")
        o = run(p)
        self.assertEqual(o.required_policy_endpoints["reviews"], "UNKNOWN")
        self.assertIn("REVIEW_ENDPOINT_UNKNOWN", o.reasons)
        self.assertEqual(o.independent_review_authority, "UNKNOWN_NOT_AUTHENTICATED")
        self.assertIsNone(o.submitted_reviews)
        self.assertIsNone(o.distinct_latest_approved_reviewers)
        self.assertIsNone(o.exact_head_latest_approvals)

    def test_11_wrong_base_repo_fails_closed(self):
        p = Provider(); p.base_name = "historic/v32-proto"
        o = run(p)
        self.assertEqual(o.status, "HOLD_PROVIDER_READ")

    def test_12_bad_review_state_fails_closed(self):
        p = Provider(); p.reviews = [review(1, "reviewer", state="INVALID")]
        o = run(p)
        self.assertEqual(o.status, "HOLD_PROVIDER_READ")

    def test_13_bad_selector_never_reads_provider(self):
        p = Provider()
        o = run(p, repository="../escape")
        self.assertEqual(o.status, "FAILED_TARGET")
        self.assertEqual(p.calls, [])

    def test_14_output_redacts_logins_even_with_review_records(self):
        p = Provider(); p.reviews = [review(1, "sensitive-internal-login")]
        row = run(p).as_dict()
        self.assertNotIn("sensitive-internal-login", repr(row))
        self.assertNotIn("reviews", row)

    def test_15_later_comment_review_is_conservative_not_qualification(self):
        p = Provider(); p.reviews = [review(1, "rev"), review(2, "rev", state="COMMENTED")]
        self.assertEqual(run(p).exact_head_latest_approvals, 0)

    def test_16_provider_exception_never_claims_policy(self):
        p = Provider()
        def broken(*args):
            raise OSError("secret token")
        p.get_pull = broken
        result = run(p).as_dict()
        self.assertEqual(result["status"], "HOLD_PROVIDER_READ")
        self.assertNotIn("secret", repr(result))


    def test_17_repository_inventory_is_not_applied_policy(self):
        p = Provider()
        p.rulesets = [{"id": 123, "name": "unrelated tag ruleset"}]
        p.active_rules = []
        out = run(p).as_dict()
        self.assertEqual(out["required_policy_endpoints"]["rulesets"], "OBSERVED_UNQUALIFIED")
        self.assertEqual(out["required_policy_endpoints"]["active_branch_rules"], "OBSERVED_EMPTY")
        self.assertEqual(out["effective_required_check_policy"], "UNKNOWN_NOT_AUTHENTICATED")
        self.assertFalse(out["writer_authorized"])

    def test_18_applied_branch_required_rule_is_still_not_d5(self):
        p = Provider()
        p.rulesets = []
        p.active_rules = [{"type": "required_status_checks", "ruleset_id": 7}]
        out = run(p).as_dict()
        self.assertEqual(out["required_policy_endpoints"]["rulesets"], "OBSERVED_EMPTY")
        self.assertEqual(out["required_policy_endpoints"]["active_branch_rules"], "OBSERVED_UNQUALIFIED")
        self.assertEqual(out["required_policy_endpoints"]["classic_required_checks"], "UNKNOWN")
        self.assertEqual(out["status"], "HOLD_D4_D5_AUTHORITY_UNKNOWN")
        self.assertFalse(out["writer_authorized"])

    def test_19_active_branch_rules_403_does_not_waive_anything(self):
        p = Provider()
        p.active_error = OSError("403 with secret raw data")
        out = run(p).as_dict()
        self.assertIn("ACTIVE_BRANCH_RULES_ENDPOINT_UNKNOWN", out["reasons"])
        self.assertEqual(out["required_policy_endpoints"]["active_branch_rules"], "UNKNOWN")
        self.assertEqual(out["effective_required_check_policy"], "UNKNOWN_NOT_AUTHENTICATED")
        self.assertNotIn("secret", str(out))

    def test_20_malformed_active_rules_fails_closed_as_unknown(self):
        p = Provider()
        p.active_rules = [None]
        out = run(p).as_dict()
        self.assertEqual(out["required_policy_endpoints"]["active_branch_rules"], "UNKNOWN")
        self.assertFalse(out["delp_invoked"])

if __name__ == "__main__":
    unittest.main()
