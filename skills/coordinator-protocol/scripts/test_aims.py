"""Report integration tests; isolated temporary registers, no external actions."""
import copy
from pathlib import Path
import tempfile
import unittest
from aim_store import Store
from aims import execute, html_report, report_data

URL = "https://chatgpt.com/c/test-owner-mapped"
NS = "work:report-tests"


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "aims.sqlite")
        for kind, aid in [("main", "MA1"), ("task", "TA1")]:
            self.store.register_aim({"id": aid, "aim_type": kind, "label": "Make the required correction usable", "criteria": [{"id": "C1", "text": "Pointer opens inspector"}], "excluded_scope": [], "authority_ref": "Fixture Owner instruction", "active": True}, NS)
        self.store.register_task({"id": "T1", "aim_id": "TA1", "workpack_id": "WP1", "recipient": URL, "criterion_ids": ["C1"], "expected_proof": ["C1"]}, NS)
        self.payload = {"id": "R1", "recipient": URL, "workpack_id": "WP1", "message_id": "message-1", "summary": "Pointer work reported; proof pending", "alignment": "VERIFY_FIRST", "source_ref": "Observed message-1", "gaps": ["Authentic pointer receipt"], "next_action": "Obtain applicable proof", "assessments": [{"id": "A1", "task_id": "T1", "aim_id": "TA1", "verdict": "VERIFY_FIRST", "evidence_ids": [], "reason": "Claim alone is insufficient"}]}

    def tearDown(self):
        self.store.close(); self.temp.cleanup()

    def test_task_report_reviews_exact_message_without_validating_claim(self):
        result = execute(self.store, NS, "task-report", self.payload, output_dir=self.temp.name)
        p = result["projection"]
        self.assertEqual(p["validated_ids"], [])
        self.assertIn("message-1", p["reviewed_message_ids"])
        self.assertIn("MA1", result["markdown"])
        self.assertIn("TA1", result["markdown"])
        self.assertIn("Authentic pointer receipt", result["markdown"])
        self.assertTrue((Path(self.temp.name) / "status.html").exists())

    def test_replay_does_not_duplicate_report_assessment_or_review(self):
        execute(self.store, NS, "task-report", self.payload)
        before = len(self.store.events(NS))
        execute(self.store, NS, "task-report", self.payload)
        self.assertEqual(len(self.store.events(NS)), before)

    def test_failed_assessment_does_not_close_message_review_gate(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0].update(verdict="VALIDATED", artifact="head-with-no-proof")
        with self.assertRaises(ValueError):
            execute(self.store, NS, "task-report", payload)
        self.assertNotIn("message-1", self.store.projection(NS, "WP1", URL)["reviewed_message_ids"])

    def test_unplanned_report_can_be_reviewed_without_invented_task(self):
        payload = copy.deepcopy(self.payload)
        payload.update(assessments=[], alignment="DRIFT", summary="Unplanned rewrite lacks an outcome link")
        execute(self.store, NS, "task-report", payload)
        self.assertEqual(len(self.store.list("task", NS)), 1)
        self.assertEqual(len(self.store.validated_tasks(NS)), 0)
        self.assertIn("message-1", self.store.projection(NS, "WP1", URL)["reviewed_message_ids"])

    def test_report_escapes_untrusted_text(self):
        payload = copy.deepcopy(self.payload)
        payload["summary"] = '<img src=x onerror="alert(1)">'
        execute(self.store, NS, "task-report", payload)
        page = html_report(report_data(self.store, NS, "WP1", URL))
        self.assertNotIn(payload["summary"], page)
        self.assertIn("&lt;img", page)

    def test_handover_requires_mapping_and_carries_ids(self):
        h = {"id": "HO1", "from": URL, "to": "https://chatgpt.com/c/new-mapped", "workpack_id": "WP1", "main_aim_id": "MA1", "task_aim_id": "TA1", "response_2_id": "IN2", "authority_ref": "Owner named successor", "source_ref": "verified response 2", "summary": "Keep aim; finish T1", "unfinished_task_ids": ["T1"], "drift_ids": ["DR1"], "roi_ids": ["ROI1"]}
        with self.assertRaises(ValueError): execute(self.store, NS, "handover-report", {"handover": h})
        h["owner_authorized"] = True
        self.store.append("drift", {"id": "DR1", "comparison": "Pointer requirement was deferred", "verdict": "CONCERN", "correction": "Retain pointer proof"}, NS)
        self.store.append("roi", {"id": "ROI1", "agent": "Incoming fixture agent", "claim": "Inspector reuse saves effort", "effort": "Unknown", "confidence": "Unverified", "displaced_work": "None proposed"}, NS)
        with self.assertRaises(ValueError): execute(self.store, NS, "handover-report", {"handover": h})
        self.assertEqual(self.store.list("handover", NS), [])
        self.store.append("review_input", {"id": "IN2", "input_type": "response_2", "verified": True, "recipient": URL, "workpack_id": "WP1", "main_aim_id": "MA1", "task_aim_id": "TA1", "source_ref": "Fixture checked response 2", "digest": "fixture-content-digest"}, NS)
        result = execute(self.store, NS, "handover-report", {"handover": h})
        self.assertIn("HO1", result["markdown"])
        self.assertIn("Pointer opens inspector", result["markdown"])
        self.assertIn("Pointer requirement was deferred", result["markdown"])
        self.assertIn("Incoming fixture agent claims: Inspector reuse saves effort", result["markdown"])
        self.assertIn("0/1 validated", result["markdown"])
        page = html_report(report_data(self.store, NS, "WP1", h["to"]))
        self.assertIn("C1: Pointer opens inspector", page)
        self.assertEqual(self.store.list("handover", NS)[0]["unfinished_task_ids"], ["T1"])
        execute(self.store, NS, "handover-report", {"handover": h})
        self.assertEqual(len(self.store.list("handover", NS)), 1)

    def test_generic_record_cannot_bypass_decision_or_handover(self):
        for kind in ["decision", "report", "handover"]:
            with self.assertRaises(ValueError): execute(self.store, NS, "record", {"kind": kind, "record": {"id": "bad"}})


if __name__ == "__main__": unittest.main()
