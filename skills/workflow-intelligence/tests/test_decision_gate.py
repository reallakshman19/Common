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
    return {"schema": mod.REQUEST_SCHEMA, "enabled": True, "scope": copy.deepcopy(SCOPE),
            "decision": copy.deepcopy(MCDA_EXAMPLE),
            "authority": {"approval_ref": "https://github.com/owner/repo/issues/10#issuecomment-1",
                          "decision_digest": "sha256:" + fingerprint(MCDA_EXAMPLE)},
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


if __name__ == "__main__":
    unittest.main()
