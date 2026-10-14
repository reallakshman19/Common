"""MCDA advisory decision history and stable semantic replay integration."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("uwi_state", ROOT / "scripts" / "state.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BASE = {"schema": "workflow-progress-monitor/v1", "workflows": []}


def assessment(winner="Refactor", sha="a" * 40, workflow="workflow"):
    return {
        "schema": "workflow-intelligence.assessment/v1",
        "scope": {"repository": "owner/repo", "workflow_id": workflow, "issue": 17,
                  "decision_id": "architecture", "assessed_sha": sha},
        "notification_eligible": False,
        "authority": "SELF_DECLARED_INPUTS_NOT_INDEPENDENTLY_VERIFIED",
        "status": "ADVISORY_REVIEW_REQUIRED",
        "reason": "Unverified self-declared source references",
        "configuration_digest": "sha256:" + "f" * 64,
        "mcda": {"schema": "software-mcda.result/v1",
                 "original": {"winner": winner,
                              "ranking": [{"name": winner, "score": 3.8,
                                           "eligible": True, "evidence_level": "OBSERVED"}]}}
    }


class DecisionHistory(unittest.TestCase):
    def test_first_baseline_with_decision_silent(self):
        state, events = mod.advance(BASE, None, assessment())
        self.assertEqual(events, [])
        self.assertEqual(len(state["decisions"]), 1)

    def test_unchanged_reassessment_silent(self):
        first, _ = mod.advance(BASE, None, assessment())
        later, events = mod.advance(BASE, first, assessment())
        self.assertEqual(events, [])
        self.assertEqual(later["decisions"], first["decisions"])

    def test_recommendation_flip_diagnostic_not_alert(self):
        first, _ = mod.advance(BASE, None, assessment("Rewrite"))
        second, events = mod.advance(BASE, first, assessment("Refactor"))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "ADVISORY_RECOMMENDATION_CHANGED")
        self.assertEqual(events[0]["previous_recommendation"], "Rewrite")
        self.assertEqual(events[0]["current_recommendation"], "Refactor")
        self.assertFalse(events[0]["alert_eligible"])
        self.assertFalse(events[0]["mcda_eligible"])
        self.assertEqual(mod.advance(BASE, first, assessment("Refactor"))[1], events)
        self.assertEqual(mod.advance(BASE, second, assessment("Refactor"))[1], [])

    def test_changed_candidate_same_winner_is_input_change(self):
        first, _ = mod.advance(BASE, None, assessment())
        nxt, events = mod.advance(BASE, first, assessment(sha="b" * 40))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "DECISION_INPUT_CHANGED")
        self.assertNotEqual(first["decisions"], nxt["decisions"])

    def test_multiple_decisions_keep_isolated_history(self):
        first, _ = mod.advance(BASE, None, assessment(workflow="w1"))
        second, events = mod.advance(BASE, first, assessment(workflow="w2"))
        self.assertEqual(len(second["decisions"]), 2)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["namespace"][1], "w2")

    def test_untrusted_notification_claim_rejected(self):
        claimed = assessment()
        claimed["notification_eligible"] = True
        with self.assertRaises(ValueError):
            mod.advance(BASE, None, claimed)

    def test_forged_qualified_status_rejected(self):
        claimed = assessment()
        claimed["status"] = "VERIFIED"
        with self.assertRaises(ValueError):
            mod.advance(BASE, None, claimed)

    def test_wrong_assessment_schema_rejected(self):
        claimed = assessment()
        claimed["schema"] = "wrong"
        with self.assertRaises(ValueError):
            mod.advance(BASE, None, claimed)

    def test_corrupt_prior_decision_digest_rejected(self):
        first, _ = mod.advance(BASE, None, assessment())
        key = next(iter(first["decisions"]))
        first["decisions"][key]["semantic_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            mod.advance(BASE, first, assessment())

    def test_not_evaluated_state_does_not_recommend(self):
        assessed = assessment()
        assessed["status"] = "NOT_EVALUATED"
        assessed["reason"] = "No approved inputs"
        assessed.pop("configuration_digest")
        assessed.pop("mcda")
        state, events = mod.advance(BASE, None, assessed)
        self.assertFalse(events)
        summary = next(iter(state["decisions"].values()))["summary"]
        self.assertNotIn("winner", summary)


if __name__ == "__main__":
    unittest.main()
