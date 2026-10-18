import copy
import unittest
from support import request, reconstruction
from relay_contract import validate_request, validate_reconstruction, profile_status


class ContractTests(unittest.TestCase):
    def test_onboard_is_recovery_with_owner_continuation(self):
        case = request("ONBOARD", "AWAIT_OWNER_TASK")
        self.assertEqual(validate_request(case)["mode"], "RECOVERY")
        self.assertEqual(case["mode"], "ONBOARD")

    def test_onboard_cannot_silently_continue_old_task(self):
        case = request("ONBOARD")
        with self.assertRaises(ValueError):
            validate_request(case)

    def test_seven_assignment_parts_required(self):
        for field in request()["assignment"]:
            case = request()
            del case["assignment"][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_request(case)

    def test_unknown_mode_and_policy_rejected(self):
        for field in ("mode", "continuation"):
            case = request()
            case[field] = "TYPO"
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_request(case)

    def test_low_and_unspecified_effort_do_not_qualify(self):
        for effort in ("low", "medium", "", None):
            case = request()
            case["profile"]["effort"] = effort
            self.assertNotEqual(profile_status(case["profile"]), "CONFIGURATION_OBSERVED")

    def test_agent_self_report_is_unverified(self):
        case = request()
        case["profile"]["assurance"] = "AGENT_CLAIM"
        self.assertEqual(profile_status(case["profile"]), "UNVERIFIED")

    def test_runtime_mismatch_is_visible(self):
        case = request()
        case["profile"]["observed_effort"] = "low"
        self.assertEqual(profile_status(case["profile"]), "MISMATCH")

    def test_high_setting_is_separate_from_semantic_judgment(self):
        self.assertEqual(profile_status(request()["profile"]), "CONFIGURATION_OBSERVED")

    def test_twelve_sections_required_and_ordered(self):
        for mutation in ("missing", "reordered", "duplicate"):
            rec = reconstruction()
            if mutation == "missing":
                rec["sections"].pop()
            elif mutation == "reordered":
                rec["sections"].reverse()
            else:
                rec["sections"][-1]["id"] = 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_reconstruction(request(), rec)

    def test_unknown_needs_reason_not_fabricated_reference(self):
        rec = reconstruction()
        rec["sections"][5] = {"id": 6, "state": "UNKNOWN", "text": "Missing golden",
                              "refs": [], "reason": "Original input was never published."}
        validate_reconstruction(request(), rec)
        del rec["sections"][5]["reason"]
        with self.assertRaises(ValueError):
            validate_reconstruction(request(), rec)

    def test_missing_route_challenge_is_not_understanding(self):
        rec = reconstruction()
        rec["route_challenge"] = ""
        with self.assertRaises(ValueError):
            validate_reconstruction(request(), rec)

    def test_roi_choice_requires_evidence_risk_and_falsifier(self):
        for field in ("evidence", "risk", "falsifier", "benefit", "route"):
            rec = reconstruction()
            rec["choices"][0][field] = [] if field == "evidence" else ""
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_reconstruction(request(), rec)

    def test_justified_keep_is_valid(self):
        rec = reconstruction()
        rec["chosen"] = "keep"
        validate_reconstruction(request(), rec)

    def test_stale_record_rejected(self):
        rec = reconstruction()
        rec["assessed_commit"] = "b" * 40
        with self.assertRaises(ValueError):
            validate_reconstruction(request(), rec)

    def test_another_takeover_cannot_reuse_the_record(self):
        case = request()
        case["id"] = "different-relay"
        with self.assertRaises(ValueError):
            validate_reconstruction(case, reconstruction())

    def test_nonobject_extra_section_is_rejected_cleanly(self):
        rec = reconstruction()
        rec["sections"].append("untrusted extra data")
        with self.assertRaises(ValueError):
            validate_reconstruction(request(), rec)

    def test_newly_introduced_needs_before_and_after(self):
        rec = reconstruction()
        rec["findings"] = [{"id": "F1", "kind": "DEFECT", "impact": "Missing rows",
                           "action": "Verify export", "refs": ["src/export.py"],
                           "introduced": True}]
        with self.assertRaises(ValueError):
            validate_reconstruction(request(), rec)

    def test_newly_discovered_issue_does_not_require_invented_history(self):
        rec = reconstruction()
        rec["findings"] = [{"id": "F1", "kind": "DEFECT", "impact": "Missing rows",
                           "action": "Verify export", "refs": ["src/export.py"],
                           "introduced": False}]
        validate_reconstruction(request(), rec)


if __name__ == "__main__":
    unittest.main()
