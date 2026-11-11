"""Invariant tests for the persisted local prototype, using simulated evidence."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from aim_store import InvariantError, Store

CHAT_A = "https://chatgpt.com/c/aim-store-test-agent-a"
CHAT_B = "https://chatgpt.com/c/aim-store-test-agent-b"


def aim(identifier, aim_type="task", active=False):
    return {"id": identifier, "aim_type": aim_type,
            "label": "Verify the approved local prototype",
            "criteria": [{"id": "C1", "text": "Observable acceptance condition"}],
            "excluded_scope": ["Live browser operation"],
            "authority_ref": "simulated owner decision", "active": active}


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "events.sqlite"
        self.store = Store(self.path)
        self.seed()

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def seed(self, namespace="demo"):
        self.store.register_aim(aim("M1", "main", True), namespace)
        self.store.register_aim(aim("A1", active=True), namespace)

    def task(self, identifier="T1", namespace="demo", recipient="agent-a", **extra):
        record = {"id": identifier, "aim_id": "A1", "workpack_id": "WP1",
                  "criterion_ids": ["C1"], "expected_proof": ["C1"],
                  "recipient": recipient, **extra}
        return self.store.register_task(record, namespace)

    def evidence(self, identifier="E1", task_id="T1", namespace="demo", **extra):
        record = {"id": identifier, "task_id": task_id, "aim_id": "A1",
                  "artifact": "sha256:simulated-artifact-v1", "result": "PASS",
                  "verified": True, "criterion_ids": ["C1"],
                  "summary": "Simulated acceptance receipt", "proof_source": "demo-only test",
                  "test_input": "simulated known input", "limitation": "No live artifact checked",
                  **extra}
        return self.store.record_evidence(record, namespace)

    def assessment(self, identifier="V1", task_id="T1", namespace="demo", **extra):
        record = {"id": identifier, "task_id": task_id, "aim_id": "A1",
                  "artifact": "sha256:simulated-artifact-v1", "verdict": "VALIDATED",
                  "evidence_ids": ["E1"], "reason": "Supplied coordinator judgement", **extra}
        return self.store.assess_task(record, namespace)

    def proposal(self, identifier="P1", revision="A2", namespace="demo", **extra):
        record = {"id": identifier, "baseline_main_id": "M1", "baseline_task_id": "A1",
                  "impact_task_ids": [t["id"] for t in self.store.list("task", namespace)
                                      if t["id"] not in {v["id"] for v in self.store.validated_tasks(namespace)}],
                  "suggestion": "Approve a revised acceptance contract for the local demonstration.",
                  "benefit_claim": "Agent reports a benefit; semantic truth is not inferred",
                  "displaced_work": "Previous task criteria will be replanned",
                  "new_aims": [aim(revision)], **extra}
        return self.store.propose(record, namespace)

    def approve(self, proposal="P1", **extra):
        return self.store.decide(proposal, "APPROVE", "simulated owner approval", "M1", "A1", **extra)

    def work_handover_record(self, namespace, identifier="HO", task_ids=None):
        current = self.store.current_aims(namespace)
        response = {"id": identifier+"-response2", "input_type": "response_2", "verified": True,
                    "recipient": CHAT_A, "workpack_id": "WP1", "main_aim_id": current["main"]["id"],
                    "task_aim_id": current["task"]["id"], "source_ref": "Saved outgoing reply",
                    "digest": "synthetic exact-source digest"}
        self.store.append("review_input", response, namespace)
        return {"id": identifier, "from": CHAT_A, "to": CHAT_B,
                "unfinished_task_ids": task_ids if task_ids is not None else ["T1"],
                "workpack_id": "WP1", "main_aim_id": current["main"]["id"],
                "task_aim_id": current["task"]["id"], "response_2_id": response["id"],
                "owner_authorized": True, "authority_ref": "Existing authorized mapping source"}

    def test_claim_and_alignment_are_not_task_completion(self):
        self.task(status="claimed")
        self.store.append("control", {"id": "claim", "task_id": "T1", "status": "DONE"})
        self.assessment(verdict="ALIGNED", evidence_ids=[])
        self.assertEqual(self.store.validated_tasks(), [])
        with self.assertRaises(InvariantError):
            self.assessment(identifier="V2", evidence_ids=[])
        self.evidence()
        self.assessment(identifier="V3")
        self.assertEqual([t["id"] for t in self.store.validated_tasks()], ["T1"])

    def test_duplicate_evidence_is_idempotent_and_payload_immutable(self):
        self.task()
        record = self.evidence()
        self.store.record_evidence(record)
        self.assertEqual(len(self.store.list("evidence")), 1)
        changed = {**record, "summary": "Changed after the fact"}
        with self.assertRaises(InvariantError):
            self.store.record_evidence(changed)
        self.store.append("roi", {"id": "R1", "claim": "Unproven"}, event_id="receipt-1")
        with self.assertRaises(InvariantError):
            self.store.append("roi", {"id": "R2", "claim": "Different"}, event_id="receipt-1")

    def test_partial_coverage_and_wrong_artifact_cannot_validate(self):
        second = aim("A2")
        second["criteria"].append({"id": "C2", "text": "Second required condition"})
        self.proposal(new_aims=[second])
        self.approve()
        self.task(aim_id="A2", criterion_ids=["C1", "C2"], expected_proof=["C1", "C2"])
        self.store.record_adoption(self.adoption_controls(criteria=["C1", "C2"]))
        self.evidence(aim_id="A2")
        with self.assertRaises(InvariantError):
            self.assessment(aim_id="A2")
        self.evidence(identifier="E2", aim_id="A2", criterion_ids=["C2"])
        with self.assertRaises(InvariantError):
            self.assessment(aim_id="A2", artifact="sha256:different-artifact", evidence_ids=["E1", "E2"])
        self.assessment(aim_id="A2", evidence_ids=["E1", "E2"])
        self.assertEqual(len(self.store.validated_tasks()), 1)

    def test_active_fail_blocks_and_explicit_supersession_is_required(self):
        self.task()
        self.evidence()
        self.assessment()
        self.evidence(identifier="F1", result="FAIL")
        self.assertEqual(self.store.validated_tasks(), [])
        self.evidence(identifier="E2")
        with self.assertRaises(InvariantError):
            self.assessment(identifier="V2", evidence_ids=["E2"])
        with self.assertRaisesRegex(InvariantError, "cannot supersede"):
            self.evidence(identifier="NOT-RESOLVED", result="NOT_RUN", supersedes=["F1"])
        self.evidence(identifier="E3", supersedes=["F1"])
        self.assessment(identifier="V3", evidence_ids=["E3"])
        self.assertEqual(len(self.store.validated_tasks()), 1)
        with self.assertRaises(InvariantError):
            self.evidence(identifier="E4", artifact="different-artifact", supersedes=["E3"])

    def test_unverified_or_not_run_receipt_cannot_validate(self):
        self.task()
        self.evidence(verified=False)
        with self.assertRaises(InvariantError):
            self.assessment()
        self.evidence(identifier="E2", result="NOT_RUN")
        with self.assertRaises(InvariantError):
            self.assessment(evidence_ids=["E2"])

    def test_stale_approval_preserves_history_and_has_no_partial_writes(self):
        self.proposal()
        self.proposal(identifier="P2", revision="A3")
        self.approve()
        events_before = len(self.store.events())
        with self.assertRaisesRegex(InvariantError, "stale"):
            self.approve(proposal="P2")
        self.assertEqual(len(self.store.events()), events_before)
        self.assertEqual(self.store.current_aims()["task"]["id"], "A2")
        self.assertEqual([a["id"] for a in self.store.list("aim")], ["M1", "A1", "A2"])
        self.assertIsNotNone(self.approve())  # Exact retry after activation remains idempotent.
        self.assertEqual(len(self.store.events()), events_before)

    def test_task_added_race_invalidates_pending_approval(self):
        self.task()
        self.proposal()
        second = Store(self.path)
        try:
            second.register_task({"id": "T2", "aim_id": "A1", "workpack_id": "WP1",
                                  "criterion_ids": ["C1"], "expected_proof": ["C1"]})
        finally:
            second.close()
        with self.assertRaisesRegex(InvariantError, "impact changed"):
            self.approve()
        self.assertEqual(self.store.current_aims()["task"]["id"], "A1")
        self.assertEqual(self.store.list("decision"), [])
        self.assertFalse(any(a["id"] == "A2" for a in self.store.list("aim")))

    def test_completion_race_also_changes_pending_impact(self):
        self.task()
        self.proposal()
        self.evidence()
        self.assessment()
        with self.assertRaisesRegex(InvariantError, "impact changed"):
            self.approve()

    def test_namespaces_do_not_share_evidence_decisions_or_counts(self):
        self.seed("recorded")
        self.task(namespace="recorded")
        self.evidence(namespace="recorded")
        self.assessment(namespace="recorded")
        self.assertEqual(self.store.validated_tasks(), [])
        self.assertEqual(len(self.store.validated_tasks("recorded")), 1)
        self.task()
        with self.assertRaises(InvariantError):
            self.assessment()  # E1 exists only in recorded.
        self.proposal(namespace="recorded")
        with self.assertRaisesRegex(InvariantError, "recorded"):
            self.store.decide("P1", "APPROVE", "claimed historical approval", "M1", "A1", namespace="recorded")
        self.assertEqual(self.store.current_aims("recorded")["task"]["id"], "A1")

    def test_checkpoint_count_survives_handover_restart_and_duplicate_receipt(self):
        for number in range(1, 6):
            task_id, evidence_id = f"T{number}", f"E{number}"
            self.task(task_id)
            self.evidence(evidence_id, task_id)
            self.assessment(f"V{number}", task_id, evidence_ids=[evidence_id])
        self.assertEqual(self.store.checkpoint_due(workpack_id="WP1")["due"], [5])
        self.store.append("handover", {"id": "H1", "workpack_id": "WP1", "summary": "Simulated new chat"})
        self.store.close()
        self.store = Store(self.path)
        self.assertEqual(self.store.checkpoint_due(workpack_id="WP1")["count"], 5)
        self.store.record_review({"id": "review5", "workpack_id": "WP1", "thresholds": [5], "reason": "Recorded checkpoint"})
        self.assertEqual(self.store.checkpoint_due(workpack_id="WP1")["due"], [])
        self.assertEqual(self.store.checkpoint_due(workpack_id="WP2")["count"], 0)
        self.task("T6", workpack_id="WP2")
        self.evidence("E6", "T6")
        self.assessment("V6", "T6", evidence_ids=["E6"])
        self.assertEqual(self.store.checkpoint_due(workpack_id="WP1")["count"], 5)
        self.assertEqual(self.store.checkpoint_due(workpack_id="WP2")["count"], 1)

    def test_roi_cannot_activate_aim_and_generic_decision_cannot_bypass(self):
        self.store.append("roi", {"id": "R1", "benefit_claim": "1000 percent", "verified": False})
        self.proposal()
        self.assertEqual(self.store.current_aims()["task"]["id"], "A1")
        with self.assertRaises(InvariantError):
            self.store.append("decision", {"id": "forged", "outcome": "APPROVE", "activation_committed": True})
        with self.assertRaises(InvariantError):
            self.store.register_aim(aim("A2", active=True))
        self.assertEqual(self.store.current_aims()["task"]["id"], "A1")

    def adoption_controls(self, recipient="agent-a", aim_id="A2", status="ACKNOWLEDGED", criteria=None,
                          namespace="demo", task_id="T1", prefix=""):
        self.store.append("control", {"id": prefix+"D1", "control_type": "DELIVERY", "recipient": recipient,
                                      "aim_id": aim_id, "status": "DELIVERED", "verified": True}, namespace)
        self.store.append("control", {"id": prefix+"K1", "control_type": "ACKNOWLEDGEMENT", "recipient": recipient,
                                      "aim_id": aim_id, "delivery_id": prefix+"D1", "status": status, "verified": True}, namespace)
        self.store.append("control", {"id": prefix+"PLAN1", "control_type": "TASK_PLAN", "recipient": recipient,
                                      "task_id": task_id, "aim_id": aim_id, "criterion_ids": criteria or ["C1"],
                                      "next_action": "Reverify the exact simulated artifact", "owner_authorized": True,
                                      "authority_ref": "simulated approved workpack"}, namespace)
        return {"id": prefix+"AD1", "recipient": recipient, "aim_id": aim_id, "delivery_id": prefix+"D1",
                "acknowledgement_id": prefix+"K1", "task_plan_ids": [prefix+"PLAN1"], "owner_authorized": True,
                "authority_ref": "simulated approved revision"}

    def test_adoption_requires_exact_recipient_and_implemented_plan(self):
        self.task()
        self.proposal()
        self.approve()
        self.assertTrue(any(c["control_type"] == "UPDATE_OUTBOX" and c["status"] == "PLANNED"
                            for c in self.store.list("control")))
        self.evidence(aim_id="A2")
        with self.assertRaisesRegex(InvariantError, "adopted"):
            self.assessment(aim_id="A2")
        adoption = self.adoption_controls()
        with self.assertRaises(InvariantError):
            self.store.record_adoption({**adoption, "recipient": "agent-b"})
        self.store.record_adoption(adoption)
        self.assessment(aim_id="A2")
        self.assertEqual(len(self.store.validated_tasks()), 1)

    def test_planned_acknowledgement_is_not_adoption(self):
        self.task()
        self.proposal()
        self.approve()
        adoption = self.adoption_controls(status="PLANNED")
        with self.assertRaisesRegex(InvariantError, "receipts"):
            self.store.record_adoption(adoption)
        self.assertEqual(self.store.list("adoption"), [])

    def test_adoption_cannot_substitute_keyboard_or_added_scope_for_pointer_proof(self):
        self.task()  # C1 represents the registered pointer criterion.
        changed_aim = aim("A2")
        changed_aim["criteria"] += [
            {"id": "C2.keyboard", "text": "Keyboard selection"},
            {"id": "C7.batch", "text": "Added previewed batch scope"}]
        self.proposal(new_aims=[changed_aim])
        self.approve()
        adoption = self.adoption_controls()
        for index, replacement in enumerate((["C2.keyboard"], ["C7.batch"], ["C1", "C7.batch"])):
            plan_id = f"BAD-PLAN-{index}"
            self.store.append("control", {"id": plan_id, "control_type": "TASK_PLAN",
                "recipient": "agent-a", "task_id": "T1", "aim_id": "A2",
                "criterion_ids": replacement, "next_action": "Try substituted proof",
                "owner_authorized": True, "authority_ref": "simulated approval"})
            with self.assertRaisesRegex(InvariantError, "preserve.*registered required proof"):
                self.store.record_adoption({**adoption, "id": f"BAD-ADOPTION-{index}",
                                           "task_plan_ids": [plan_id]})
        self.evidence(identifier="KEYBOARD-PASS", aim_id="A2", criterion_ids=["C2.keyboard"])
        with self.assertRaises(InvariantError):
            self.assessment(aim_id="A2", evidence_ids=["KEYBOARD-PASS"])
        self.store.record_adoption(adoption)  # Original pointer requirement is preserved.
        with self.assertRaisesRegex(InvariantError, "every expected proof"):
            self.assessment(aim_id="A2", evidence_ids=["KEYBOARD-PASS"])
        self.evidence(identifier="POINTER-PASS", aim_id="A2")
        self.assessment(aim_id="A2", evidence_ids=["POINTER-PASS"])
        self.assertEqual(len(self.store.validated_tasks()), 1)

    def test_handover_allows_new_recipient_only_with_explicit_transfer(self):
        self.task()
        adoption = self.adoption_controls(recipient="agent-b", aim_id="A1")
        with self.assertRaisesRegex(InvariantError, "assigned task"):
            self.store.record_adoption(adoption)
        self.store.append("handover", {"id": "H1", "from": "agent-a", "to": "agent-b",
                                       "unfinished_task_ids": ["T1"], "workpack_id": "WP1"})
        self.store.record_adoption(adoption)
        self.proposal()
        self.approve()
        outbox = [c for c in self.store.list("control") if c.get("control_type") == "UPDATE_OUTBOX"]
        self.assertEqual({c["recipient"] for c in outbox}, {"agent-b"})
        self.assertEqual(self.store.list("task")[0]["recipient"], "agent-a")

    def test_main_revision_change_also_requires_recipient_adoption(self):
        self.task()
        changed_main = aim("M2", "main")
        changed_main["criteria"] = [{"id": "M.output", "text": "Broader project outcome"}]
        self.proposal(new_aims=[changed_main])
        self.approve()
        self.evidence()
        with self.assertRaisesRegex(InvariantError, "adopted"):
            self.assessment()
        adoption = self.adoption_controls(aim_id="M2")
        self.store.record_adoption(adoption)
        self.assessment()
        self.assertEqual(len(self.store.validated_tasks()), 1)

    def test_new_task_cannot_bind_a_superseded_revision(self):
        self.proposal()
        self.approve()
        with self.assertRaisesRegex(InvariantError, "active task aim"):
            self.task()
        self.task(aim_id="A2")

    def test_report_snapshot_and_review_input_are_nonauthoritative(self):
        self.store.append("report", {"id": "SNAP1", "current_task_aim": "invented", "approved": True})
        self.store.append("review_input", {"id": "BASELINE2", "suggested_aim": "invented"})
        self.store.append("source", {"id": "SOURCE1", "path": "saved-evidence.md", "sha256": "simulated"})
        self.assertEqual(self.store.current_aims()["task"]["id"], "A1")
        self.assertIn("report", self.store.snapshot())

    def test_recall_is_scoped_and_reports_truncation(self):
        self.store.append("roi", {"id": "R1", "claim": "Benefit from simulated change"})
        self.store.append("roi", {"id": "R2", "claim": "Benefit from another simulated change"})
        result = self.store.recall(query="benefit", kinds=["roi"], max_items=1)
        self.assertEqual(result["total"], 2)
        self.assertTrue(result["truncated"])
        self.assertEqual(self.store.recall(ids=["R2"])["items"][0]["record"]["id"], "R2")
        self.assertEqual(self.store.recall(query="benefit", namespace="recorded")["total"], 0)

    def test_default_recall_excludes_duplicated_report_snapshots(self):
        proposal = self.proposal()
        self.store.append("report", {"id": "REPORT-P1", "name": "Saved P1 report",
            "records": [{"kind": "proposal", "record": proposal}],
            "long_snapshot_detail": "Duplicated history " * 1000})
        normal = self.store.recall(query="P1")
        self.assertEqual(normal["total"], 1)
        self.assertEqual([item["kind"] for item in normal["items"]], ["proposal"])
        self.assertFalse(any(item["kind"] == "report" for item in self.store.recall()["items"]))
        explicit_kind = self.store.recall(query="P1", kinds=["report"])
        self.assertEqual(explicit_kind["total"], 1)
        self.assertEqual(explicit_kind["items"][0]["record"]["id"], "REPORT-P1")
        explicit_id = self.store.recall(ids=["REPORT-P1"])
        self.assertEqual(explicit_id["total"], 1)
        self.assertEqual(explicit_id["items"][0]["kind"], "report")
        underlying_id = self.store.recall(query="P1", ids=["P1"])
        self.assertEqual([item["kind"] for item in underlying_id["items"]], ["proposal"])

    def test_database_enforces_append_only_history(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.store._db.execute("DELETE FROM events")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store._db.execute("UPDATE events SET payload='{}'")

    def test_work_namespaces_are_bounded_safe_and_isolated(self):
        for invalid in ("work:", "work:../unsafe", "work:a/b", "work:a b", "work:"+"a"*65):
            with self.subTest(namespace=invalid), self.assertRaises(InvariantError):
                self.store.events(invalid)
        for namespace in ("work:aa3-lfea", "work:another-stream", "work:"+"a"*64):
            self.seed(namespace)
        self.task(namespace="work:aa3-lfea", recipient=CHAT_A)
        self.evidence(namespace="work:aa3-lfea")
        self.assessment(namespace="work:aa3-lfea")
        self.task(namespace="work:another-stream", recipient=CHAT_A)
        with self.assertRaises(InvariantError):
            self.assessment(namespace="work:another-stream")
        self.assertEqual(len(self.store.validated_tasks("work:aa3-lfea")), 1)
        self.assertEqual(self.store.validated_tasks("work:another-stream"), [])
        self.assertEqual(self.store.validated_tasks("demo"), [])

    def test_work_decisions_require_explicit_authority_and_exact_proposal(self):
        ns = "work:owner-approval"
        self.seed(ns)
        self.proposal(namespace=ns)
        with self.assertRaises(InvariantError):
            self.store.decide("P1", "APPROVE", "", "M1", "A1", ns)
        with self.assertRaises(InvariantError):
            self.store.append("decision", {"id": "forged", "activation_committed": True}, ns)
        decision = self.store.decide("P1", "APPROVE", "Owner message source assertion", "M1", "A1", ns)
        self.assertTrue(decision["activation_committed"])
        self.assertEqual(self.store.current_aims(ns)["task"]["id"], "A2")
        self.assertEqual(self.store.current_aims("demo")["task"]["id"], "A1")

    def test_projection_scope_initial_assignment_and_namespace_sequence(self):
        ns = "work:scope"
        self.seed(ns)
        with self.assertRaises(InvariantError):
            self.task(namespace=ns, recipient="display name only")
        self.task(namespace=ns, recipient=CHAT_A)
        self.task("T2", namespace=ns, recipient=CHAT_B)
        self.task("T3", namespace=ns, recipient=CHAT_A, workpack_id="WP2")
        projection = self.store.projection(ns, "WP1", CHAT_A)
        self.assertEqual(projection["registered_ids"], ["T1", "T2"])
        self.assertEqual(projection["eligible_ids"], ["T1"])
        self.assertEqual(projection["alignment"], "UNASSESSED")
        sequence = projection["sequence"]
        self.store.append("roi", {"id": "outside", "claim": "Another namespace"})
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["sequence"], sequence)
        self.assertEqual(sequence, self.store.events(ns)[-1]["sequence"])
        self.assertNotIn("report", projection)

    def test_projection_holds_drift_and_stopped_tasks(self):
        ns = "work:holds"
        self.seed(ns)
        self.task(namespace=ns, recipient=CHAT_A)
        self.assessment(namespace=ns, verdict="DRIFT", evidence_ids=[])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], [])
        self.assessment("V2", namespace=ns, verdict="ALIGNED", evidence_ids=[])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1"])
        self.proposal(namespace=ns, task_actions={"T1": "STOP"})
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["pending_proposal_ids"], ["P1"])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1"])
        self.store.decide("P1", "APPROVE", "Owner source", "M1", "A1", ns)
        projection = self.store.projection(ns, "WP1", CHAT_A)
        self.assertEqual(projection["eligible_ids"], [])
        self.assertEqual(projection["pending_proposal_ids"], [])

    def test_projection_preserves_workpack_counts_and_reviews_across_handover(self):
        ns = "work:handover-count"
        self.seed(ns)
        for number in range(1, 7):
            task_id, evidence_id = f"T{number}", f"E{number}"
            self.task(task_id, ns, recipient=CHAT_A)
            if number <= 5:
                self.evidence(evidence_id, task_id, ns)
                self.assessment(f"V{number}", task_id, ns, evidence_ids=[evidence_id])
        self.store.append("handover", self.work_handover_record(ns, task_ids=["T6"]), ns)
        incoming = self.store.projection(ns, "WP1", CHAT_B)
        self.assertEqual(incoming["validated_ids"], ["T1", "T2", "T3", "T4", "T5"])
        self.assertEqual(incoming["eligible_ids"], [])
        self.store.record_adoption(self.adoption_controls(recipient=CHAT_B, aim_id="A1",
                                                        namespace=ns, task_id="T6", prefix="incoming-"), ns)
        incoming = self.store.projection(ns, "WP1", CHAT_B)
        self.assertEqual(incoming["eligible_ids"], ["T6"])
        self.assertEqual(incoming["due"], [5])
        self.store.record_review({"id": "R5", "workpack_id": "WP1", "thresholds": [5],
                                  "reason": "Checkpoint reviewed before handover"}, ns)
        self.store.close()
        self.store = Store(self.path, read_only=True)
        incoming = self.store.projection(ns, "WP1", CHAT_B)
        self.assertEqual(len(incoming["validated_ids"]), 5)
        self.assertEqual(incoming["reviewed_thresholds"], [5])
        self.assertEqual(incoming["due"], [])

    def test_work_handover_guard_requires_verified_exact_response2_and_authorized_mapping(self):
        ns = "work:handover-guard"
        self.seed(ns)
        self.task(namespace=ns, recipient=CHAT_A)
        handover = self.work_handover_record(ns)
        original_response = self.store.list("review_input", ns)[0]
        for index, changed in enumerate(({"verified": False}, {"input_type": "roi"},
                {"recipient": CHAT_B}, {"workpack_id": "WP2"}, {"main_aim_id": "other"},
                {"task_aim_id": "other"}, {"source_ref": ""}, {"digest": ""})):
            response = {**original_response, **changed, "id": f"bad-response-{index}"}
            self.store.append("review_input", response, ns)
            with self.subTest(change=changed), self.assertRaises(InvariantError):
                self.store.append("handover", {**handover, "id": f"bad-ho-{index}",
                                              "response_2_id": response["id"]}, ns)
        for changed in ({"response_2_id": "missing"}, {"owner_authorized": False},
                        {"authority_ref": ""}, {"main_aim_id": "stale"},
                        {"unfinished_task_ids": ["T1", "T1"]}, {"unfinished_task_ids": ["unknown"]}):
            with self.subTest(change=changed), self.assertRaises(InvariantError):
                self.store.append("handover", {**handover, **changed}, ns)
        self.task("DONE", namespace=ns, recipient=CHAT_A)
        self.evidence("DONE-E", "DONE", ns)
        self.assessment("DONE-A", "DONE", ns, evidence_ids=["DONE-E"])
        self.task("OTHER-WP", namespace=ns, recipient=CHAT_A, workpack_id="WP2")
        self.task("OTHER-AGENT", namespace=ns, recipient=CHAT_B)
        for task_id in ("DONE", "OTHER-WP", "OTHER-AGENT"):
            with self.subTest(task=task_id), self.assertRaises(InvariantError):
                self.store.append("handover", {**handover, "unfinished_task_ids": [task_id]}, ns)
        self.store.append("handover", handover, ns)
        before = len(self.store.events(ns))
        self.store.append("handover", handover, ns)  # Replay succeeds after assignment moved.
        self.assertEqual(len(self.store.events(ns)), before)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_B)["eligible_ids"], ["OTHER-AGENT"])

    def test_initial_revision_transfer_requires_incoming_adoption_before_validation_or_eligibility(self):
        ns = "work:initial-transfer"
        self.seed(ns)
        self.task(namespace=ns, recipient=CHAT_A)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1"])
        self.store.append("handover", self.work_handover_record(ns), ns)
        incoming = self.store.projection(ns, "WP1", CHAT_B)
        self.assertEqual(incoming["eligible_ids"], [])
        self.evidence(namespace=ns)
        with self.assertRaisesRegex(InvariantError, "adopted"):
            self.assessment(namespace=ns)
        self.store.record_adoption(self.adoption_controls(recipient=CHAT_B, aim_id="A1", namespace=ns), ns)
        adopted = self.store.projection(ns, "WP1", CHAT_B)
        self.assertEqual(adopted["eligible_ids"], ["T1"])
        self.assertEqual(adopted["validated_ids"], incoming["validated_ids"])
        self.assertEqual(adopted["reviewed_thresholds"], incoming["reviewed_thresholds"])
        self.assertEqual(adopted["due"], incoming["due"])
        self.assessment(namespace=ns)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_B)["validated_ids"], ["T1"])

    def test_non_count_reconciliation_requires_explicit_source_and_does_not_earn_checkpoint(self):
        ns = "work:non-count-review"
        self.seed(ns)
        review = {"id": "handover-review", "workpack_id": "WP1", "thresholds": [],
                  "trigger": "handover", "source_ref": "Saved handover and response-2 input",
                  "reason": "Retain aim; carry open evidence into incoming assignment"}
        before = self.store.projection(ns, "WP1", CHAT_A)
        self.store.record_review(review, ns)
        after = self.store.projection(ns, "WP1", CHAT_A)
        self.assertGreater(after["sequence"], before["sequence"])
        self.assertEqual(after["reviewed_thresholds"], before["reviewed_thresholds"])
        self.assertEqual(after["due"], before["due"])
        with self.assertRaisesRegex(InvariantError, "unearned"):
            self.store.record_review({**review, "id": "unearned-5", "thresholds": [5]}, ns)
        for change in ({"trigger": None}, {"trigger": "routine"}, {"source_ref": ""}, {"reason": ""}):
            with self.subTest(change=change), self.assertRaises(InvariantError):
                self.store.record_review({**review, "id": "bad-review", **change}, ns)
        for trigger in ("response_2", "y", "closure", "contradiction"):
            self.store.record_review({**review, "id": "review-"+trigger, "trigger": trigger}, ns)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["reviewed_thresholds"], [])

    def test_activated_revision_requires_exact_recipient_and_new_scope_task_adoption(self):
        ns = "work:adoption"
        self.seed(ns)
        self.task(namespace=ns, recipient=CHAT_A)
        self.task("T2", namespace=ns, recipient=CHAT_B)
        self.proposal(namespace=ns)
        self.store.decide("P1", "APPROVE", "Owner source", "M1", "A1", ns)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], [])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_B)["eligible_ids"], [])
        self.store.record_adoption(self.adoption_controls(recipient=CHAT_A, namespace=ns), ns)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1"])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_B)["eligible_ids"], [])
        self.task("T3", namespace=ns, recipient=CHAT_A, aim_id="A2")
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1"])
        self.evidence("E3", "T3", ns, aim_id="A2")
        with self.assertRaisesRegex(InvariantError, "adopted"):
            self.assessment("V3", "T3", ns, aim_id="A2", evidence_ids=["E3"])
        self.store.record_adoption(self.adoption_controls(recipient=CHAT_A, namespace=ns,
                                                        task_id="T3", prefix="new-"), ns)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1", "T3"])
        self.assessment("V3", "T3", ns, aim_id="A2", evidence_ids=["E3"])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["eligible_ids"], ["T1"])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["validated_ids"], ["T3"])

    def test_read_only_projection_creates_no_files_and_cannot_mutate(self):
        ns = "work:reader"
        self.seed(ns)
        self.task(namespace=ns, recipient=CHAT_A)
        self.store.close()
        before_bytes = self.path.read_bytes()
        before_files = sorted(p.name for p in self.path.parent.iterdir())
        self.store = Store(self.path, read_only=True)
        trace = []
        self.store._db.set_trace_callback(trace.append)
        projection = self.store.projection(ns, "WP1", CHAT_A)
        self.assertEqual(projection["eligible_ids"], ["T1"])
        self.assertEqual(trace[0], "BEGIN")
        self.assertEqual(trace[-1], "COMMIT")
        self.assertEqual(self.path.read_bytes(), before_bytes)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), before_files)
        with self.assertRaisesRegex(InvariantError, "read-only"):
            self.store.append("roi", {"id": "forbidden", "claim": "Must not persist"}, ns)
        missing = self.path.parent / "never-created" / "events.db"
        with self.assertRaises(FileNotFoundError):
            Store(missing, read_only=True)
        self.assertFalse(missing.parent.exists())

    def test_read_only_projection_refreshes_after_another_writer_commits(self):
        ns = "work:fresh-read"
        self.seed(ns)
        with Store(self.path, read_only=True) as reader:
            first = reader.projection(ns, "WP1", CHAT_A)
            self.task(namespace=ns, recipient=CHAT_A)
            second = reader.projection(ns, "WP1", CHAT_A)
            self.assertGreater(second["sequence"], first["sequence"])
            self.assertEqual(second["eligible_ids"], ["T1"])

    def test_read_only_legacy_wal_cannot_create_sidecars_or_ignore_pending_commits(self):
        wal_path = self.path.parent / "old-wal.sqlite"
        with Store(wal_path):
            pass
        db = sqlite3.connect(wal_path)
        db.execute("PRAGMA journal_mode=WAL")
        db.close()
        before_files = sorted(p.name for p in self.path.parent.iterdir())
        before_bytes = wal_path.read_bytes()
        with self.assertRaisesRegex(InvariantError, "legacy WAL"):
            Store(wal_path, read_only=True)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), before_files)
        self.assertEqual(wal_path.read_bytes(), before_bytes)
        with Store(wal_path):  # Explicit writable migration checkpoints the old journal.
            pass
        with Store(wal_path, read_only=True) as reader:
            self.assertEqual(reader.events(), [])

    def test_legacy_namespace_schema_migration_preserves_event_sequence_and_payload(self):
        legacy_path = self.path.parent / "legacy.sqlite"
        db = sqlite3.connect(legacy_path)
        db.execute("""CREATE TABLE events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace TEXT CHECK(namespace IN ('recorded','demo')),event_id TEXT,kind TEXT,
            record_id TEXT,payload TEXT,created_at TEXT,UNIQUE(namespace,event_id),UNIQUE(namespace,kind,record_id))""")
        payload = json.dumps({"id": "old", "claim": "Preserve verbatim"})
        db.execute("INSERT INTO events VALUES(42,'recorded','roi:old','roi','old',?,'historic-time')", (payload,))
        db.commit(); db.close()
        with Store(legacy_path) as migrated:
            event = migrated.events("recorded")[0]
            self.assertEqual(event["sequence"], 42)
            self.assertEqual(event["record"], {"id": "old", "claim": "Preserve verbatim"})
            self.assertEqual(migrated._db.execute("SELECT payload FROM events").fetchone()[0], payload)
            migrated.append("roi", {"id": "new", "claim": "Work namespace permitted"}, "work:migrated")
            self.assertEqual(migrated.events("work:migrated")[0]["sequence"], 43)
            with self.assertRaises(sqlite3.IntegrityError):
                migrated._db.execute("DELETE FROM events")

    def test_task_report_reviews_require_matching_sources_and_allow_incomplete_reports(self):
        ns = "work:task-reports"
        self.seed(ns)
        self.task(namespace=ns, recipient=CHAT_A)
        self.store.append("control", {"id": "observe", "control_type": "TASK_REPORT_OBSERVATION",
            "message_id": "message-1", "recipient": CHAT_A, "workpack_id": "WP1"}, ns)
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_A)["unreviewed_message_ids"], ["message-1"])
        self.store.append("report", {"id": "report1", "message_id": "message-1", "recipient": CHAT_A,
            "workpack_id": "WP1", "summary": "An incomplete support reply", "assessments": []}, ns)
        review = {"id": "review1", "control_type": "TASK_REPORT_REVIEW", "report_id": "report1",
            "message_id": "message-1", "recipient": CHAT_A, "workpack_id": "WP1", "assessment_ids": [],
            "reason": "Support work serves the unchanged task; proof remains open",
            "source_ref": "Saved message-1", "alignment": "ALIGNED"}
        for changed in ({"report_id": "missing"}, {"message_id": "other-message"},
                        {"recipient": CHAT_B}, {"source_ref": ""}, {"assessment_ids": ["missing"]}):
            with self.subTest(change=changed), self.assertRaises(InvariantError):
                self.store.append("control", {**review, **changed}, ns)
        self.task("T2", namespace=ns, recipient=CHAT_A, workpack_id="WP2")
        self.assessment("A-OTHER", "T2", ns, verdict="ALIGNED", evidence_ids=[])
        with self.assertRaisesRegex(InvariantError, "another workpack"):
            self.store.append("control", {**review, "assessment_ids": ["A-OTHER"]}, ns)
        self.store.append("control", review, ns)
        self.store.append("control", review, ns)  # Replays after a crash are idempotent.
        projection = self.store.projection(ns, "WP1", CHAT_A)
        self.assertEqual(projection["reviewed_message_ids"], ["message-1"])
        self.assertEqual(projection["latest_reviewed_message_id"], "message-1")
        self.assertEqual(projection["unreviewed_message_ids"], [])
        self.assertEqual(projection["alignment"], "ALIGNED")
        self.assertEqual(projection["validated_ids"], [])
        self.assertEqual(self.store.projection(ns, "WP1", CHAT_B)["reviewed_message_ids"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
