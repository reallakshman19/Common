"""Scoring input provenance boundary: advisory, never notification-ready."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("decision_gate", ROOT / "scripts" / "decision_gate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from observe import fingerprint

MCDA_EXAMPLE = json.loads((ROOT.parent / "software-mcda" / "assets" / "example-decision.json").read_text())
SCOPE = {"repository": "owner/repo", "workflow_id": "buddyrunner", "issue": 10,
         "decision_id": "implementation", "assessed_sha": "a" * 40}


def example():
    evidence = {}
    for option in MCDA_EXAMPLE["options"]:
        evidence[option["name"]] = {}
        for criterion in MCDA_EXAMPLE["criteria"]:
            evidence[option["name"]][criterion["id"]] = {
                "ref": "https://github.com/owner/repo/commit/" + "a" * 40,
                "assessed_sha": "a" * 40, "status": "OBSERVED"}
    observed = copy.deepcopy(MCDA_EXAMPLE)
    for option in observed["options"]:
        option["evidence_level"] = "OBSERVED"  # still self-declared, not independently verified
    return {"schema": mod.REQUEST_SCHEMA, "enabled": True, "scope": copy.deepcopy(SCOPE),
            "decision": observed,
            "authority": {"approval_ref": "https://github.com/owner/repo/issues/10#issuecomment-1",
                          "decision_digest": "sha256:" + fingerprint(observed)},
            "rating_evidence": evidence}


class EvidenceDecisionTests(unittest.TestCase):
    def test_disabled_by_default_not_evaluated(self):
        request = example()
        request["enabled"] = False
        r = mod.assessment(request)
        self.assertEqual(r["status"], "NOT_EVALUATED")
        self.assertFalse(r["notification_eligible"])

    def test_declared_evidence_only_advisory(self):
        result = mod.assessment(example())
        self.assertEqual(result["status"], "ADVISORY_REVIEW_REQUIRED")
        self.assertFalse(result["notification_eligible"])
        self.assertEqual(result["mcda"]["original"]["winner"], "Rewrite From Scratch")

    def test_missing_approval_not_evaluated(self):
        request = example()
        request.pop("authority")
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_modified_weights_break_digest(self):
        request = example()
        request["decision"]["criteria"][0]["weight"] = 0.35
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_stale_assessed_sha_fails(self):
        request = example()
        name = next(iter(request["rating_evidence"]))
        request["rating_evidence"][name]["cost"]["assessed_sha"] = "b" * 40
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_missing_evidence_fails(self):
        request = example()
        name = next(iter(request["rating_evidence"]))
        del request["rating_evidence"][name]["cost"]
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_claimed_verified_status_not_accepted(self):
        request = example()
        name = next(iter(request["rating_evidence"]))
        request["rating_evidence"][name]["cost"]["status"] = "VERIFIED"
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_cross_repo_evidence_fails(self):
        request = example()
        name = next(iter(request["rating_evidence"]))
        request["rating_evidence"][name]["cost"]["ref"] = "https://github.com/other/repo/commit/abc"
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_cross_repo_approval_fails(self):
        request = example()
        request["authority"]["approval_ref"] = "https://github.com/other/repo/issues/10"
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_invalid_schema_fails(self):
        request = example()
        request["schema"] = "workflow-intelligence.decision-request/v2"
        with self.assertRaises(ValueError):
            mod.assessment(request)

    def test_unscored_option_not_auto_filled(self):
        request = example()
        del request["decision"]["options"][0]["scores"]["risk"]
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_boolean_enabled_required(self):
        request = example()
        request["enabled"] = 1
        with self.assertRaises(ValueError):
            mod.assessment(request)


    def test_assumed_ratings_never_automatically_evaluated(self):
        request = example()
        request["decision"]["options"][0]["evidence_level"] = "ASSUMED"
        request["authority"]["decision_digest"] = "sha256:" + fingerprint(request["decision"])
        self.assertEqual(mod.assessment(request)["status"], "NOT_EVALUATED")

    def test_bound_exact_commit_ci_check_does_not_certify_scores(self):
        request = example()
        check_request = {"schema": "workflow-intelligence.github-check-request/v1",
                         "enabled": True,
                         "scope": {"repository": "owner/repo", "assessed_sha": "a" * 40},
                         "checks": [{"alias": "unit-tests", "check_run_id": 42,
                                     "expected_name": "tests", "trusted_app_id": 15368}]}
        source = {"id": 42, "head_sha": "a" * 40, "name": "tests",
                  "status": "completed", "conclusion": "success",
                  "app": {"id": 15368}}
        result = mod.assessment(request, check_request, lambda *_: source)
        self.assertEqual(result["status"], "ADVISORY_REVIEW_REQUIRED")
        self.assertEqual(result["ci_check_facts"]["status"], "CHECKS_VERIFIED")
        self.assertFalse(result["notification_eligible"])
        self.assertFalse(result["ci_check_facts"]["eligible_for_mcda_rating"])

    def test_failed_required_check_prevents_assessment(self):
        request = example()
        check_request = {"schema": "workflow-intelligence.github-check-request/v1",
                         "enabled": True,
                         "scope": {"repository": "owner/repo", "assessed_sha": "a" * 40},
                         "checks": [{"alias": "unit-tests", "check_run_id": 42,
                                     "expected_name": "tests", "trusted_app_id": 15368}]}
        source = {"id": 42, "head_sha": "a" * 40, "name": "tests",
                  "status": "completed", "conclusion": "skipped",
                  "app": {"id": 15368}}
        result = mod.assessment(request, check_request, lambda *_: source)
        self.assertEqual(result["status"], "NOT_EVALUATED")
        self.assertFalse(result["notification_eligible"])

    def test_mismatched_check_scope_rejected(self):
        request = example()
        check_request = {"schema": "workflow-intelligence.github-check-request/v1",
                         "enabled": False,
                         "scope": {"repository": "other/repo", "assessed_sha": "a" * 40}}
        def do_not_fetch(*_):
            raise AssertionError("Cross-repository validation must happen before GET")
        result = mod.assessment(request, check_request, do_not_fetch)
        self.assertEqual(result["status"], "NOT_EVALUATED")



if __name__ == "__main__":
    unittest.main()
