"""Pilot regressions: supplied reports cannot certify qualification or execution."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, request, reconstruction, source
from relay_evidence import digest
from relay_workflow import assess, invoke


def executed(activity="INVESTIGATION"):
    return {"status": "EXECUTED", "activity": activity,
            "action": "Run the original public-entry regression",
            "result": "One regression passed; no browser run",
            "evidence": ["fixture:probe/stdout"]}


def blocked():
    return {"status": "BLOCKED", "activity": "CODING", "attempted": True,
            "action": "Request the selected exact-file write claim",
            "observed_restriction": "Current claim belongs to another engineer",
            "affected_scope": ["writes to the selected adapter"],
            "next_feasible_action": "Inspect consumers read-only",
            "evidence": ["fixture:claim-response"]}


class ProgressTests(unittest.TestCase):
    def evidence(self, case):
        return assess(case, reconstruction()).get("continuation_evidence", {})

    def test_reconstruction_is_separate_from_execution(self):
        result = assess(request(), reconstruction())
        self.assertEqual(result.get("reconstruction_status"), "STRUCTURALLY_RECORDED")
        self.assertEqual(result.get("continuation_evidence", {}).get("status"), "NOT_STARTED")
        self.assertFalse(result["workflow_executed"])

    def test_publishing_reconstruction_is_not_continuation(self):
        case = request()
        case["progress"] = executed("RECONSTRUCTION")
        self.assertEqual(self.evidence(case).get("status"), "NOT_STARTED")

    def test_supplied_execution_is_reported_not_verified(self):
        case = request()
        case["progress"] = dict(executed(), workflow_executed=True, coding_authorized=True)
        result = assess(case, reconstruction())
        evidence = result.get("continuation_evidence", {})
        self.assertEqual(evidence.get("status"), "EXECUTION_REPORTED")
        self.assertEqual(evidence.get("grade"), "SUPPLIED_UNVERIFIED")
        self.assertFalse(result["workflow_executed"])
        self.assertFalse(result["coding_authorized"])

    def test_execution_without_result_or_evidence_is_unsupported(self):
        for missing in ("result", "evidence"):
            case = request()
            case["progress"] = executed()
            del case["progress"][missing]
            with self.subTest(missing=missing):
                self.assertEqual(self.evidence(case).get("status"), "EXECUTION_UNSUPPORTED")

    def test_blocker_needs_attempt_observation_scope_and_next_action(self):
        for missing in ("action", "attempted", "observed_restriction", "affected_scope",
                        "next_feasible_action", "evidence"):
            case = request()
            case["progress"] = blocked()
            del case["progress"][missing]
            with self.subTest(missing=missing):
                value = self.evidence(case)
                self.assertEqual(value.get("status"), "BLOCKER_UNSUPPORTED")
                self.assertIn(missing, value.get("missing", []))

    def test_supported_blocker_remains_scoped_and_unverified(self):
        case = request()
        case["progress"] = blocked()
        result = assess(case, reconstruction())
        value = result.get("continuation_evidence", {})
        self.assertEqual(value.get("status"), "BLOCKED_REPORTED")
        self.assertEqual(value.get("affected_scope"), ["writes to the selected adapter"])
        self.assertEqual(value.get("next_feasible_action"), "Inspect consumers read-only")
        self.assertEqual(result["next"], "ENTER_PINNED_CODING_PROTOCOL")
        self.assertFalse(result["coding_authorized"])

    def test_forbidden_action_need_not_be_attempted_to_prove_a_blocker(self):
        case = request()
        case["progress"] = dict(blocked(), attempted=False,
            not_attempted_reason="Observed Owner instruction forbids this write")
        self.assertEqual(self.evidence(case).get("status"), "BLOCKED_REPORTED")
        del case["progress"]["not_attempted_reason"]
        self.assertEqual(self.evidence(case).get("status"), "BLOCKER_UNSUPPORTED")

    def test_onboard_wait_is_normal_and_needs_no_failed_attempt(self):
        case = request("ONBOARD", "AWAIT_OWNER_TASK")
        rec = reconstruction()
        event = {"ref": case["issue"] + "#issuecomment-2",
                 "subject": digest(rec), "digest": digest("Approve reconstruction")}
        result = assess(case, rec, approval=event,
                        reader=lambda ref: source("Approve reconstruction"))
        self.assertEqual(result.get("continuation_evidence", {}).get("status"), "OWNER_WAIT")
        self.assertEqual(result["state"], "ONBOARDED_AWAITING_TASK")

    def test_onboard_coding_claim_does_not_bypass_owner_wait(self):
        case = request("ONBOARD", "AWAIT_OWNER_TASK")
        case["progress"] = executed("CODING")
        result = assess(case, reconstruction())
        self.assertEqual(result.get("continuation_evidence", {}).get("status"), "CODING_CLAIM_CONFLICT")
        calls = []
        invoke(result, {"task": "old task"}, authorize=lambda _: True,
               executor=lambda item: calls.append(item))
        self.assertEqual(calls, [])

    def test_unknown_profile_retains_investigation_without_qualifying_takeover(self):
        case = request()
        case["profile"]["assurance"] = "AGENT_CLAIM"
        case["progress"] = executed()
        result = assess(case, reconstruction())
        self.assertEqual(result["state"], "PROFILE_UNQUALIFIED")
        self.assertEqual(result.get("reconstruction_status"), "STRUCTURALLY_RECORDED")
        self.assertEqual(result.get("continuation_evidence", {}).get("status"), "EXECUTION_REPORTED")
        self.assertFalse(result["coding_authorized"])

    def test_missing_material_item_is_visible_without_globally_blocking_work(self):
        case = request()
        case["known_items"] = ["STALE-REPORT", "TARGET-CUSTODY"]
        rec = reconstruction()
        rec["dispositions"] = {"STALE-REPORT": {
            "decision": "SUPERSEDED", "reason": "Current source includes the mount",
            "refs": ["fixture:src/ui.py"]}}
        result = assess(case, rec)
        self.assertEqual(result.get("carry_forward", {}).get("unaddressed"), ["TARGET-CUSTODY"])
        self.assertEqual(result["next"], "ENTER_PINNED_CODING_PROTOCOL")

    def test_resolved_item_requires_source_and_reason(self):
        case = request()
        case["known_items"] = ["RISK"]
        rec = reconstruction()
        rec["dispositions"] = {"RISK": {"decision": "RESOLVED"}}
        with self.assertRaises(ValueError):
            assess(case, rec)

    def test_cli_progress_is_untrusted_and_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = {name: Path(tmp) / (name + ".json") for name in ("request", "record", "progress")}
            for name, value in (("request", request()), ("record", reconstruction()),
                                ("progress", executed())):
                paths[name].write_text(json.dumps(value))
            command = [sys.executable, str(ROOT / "scripts/buddy_runner_v20.py"),
                       "--input", str(paths["request"]), "--record", str(paths["record"]),
                       "--progress", str(paths["progress"]), "--status-json"]
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["continuation_evidence"]["status"], "EXECUTION_REPORTED")
            before = paths["progress"].read_bytes()
            rejected = subprocess.run(command + ["--output", str(paths["progress"])],
                                      text=True, capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(paths["progress"].read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
