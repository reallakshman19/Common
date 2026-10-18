import unittest
from support import request, reconstruction, source
from relay_evidence import digest
from relay_workflow import assess, invoke


class WorkflowTests(unittest.TestCase):
    def event(self, body, subject):
        return {"ref": "https://github.com/example/project/issues/1#issuecomment-2",
                "digest": digest(body), "subject": digest(subject)}

    def test_recovery_does_not_require_predecessor(self):
        case = request()
        del case["outgoing"]
        result = assess(case, reconstruction())
        self.assertEqual(result["state"], "DIRECTION_RECORDED")
        self.assertEqual(result["next"], "ENTER_PINNED_CODING_PROTOCOL")
        self.assertFalse(result["agent_invoked"])

    def test_onboard_waits_for_reconstruction_approval(self):
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), reconstruction())
        self.assertEqual(result["state"], "AWAITING_RECONSTRUCTION_APPROVAL")

    def test_unread_approval_is_not_trusted(self):
        rec = reconstruction()
        event = self.event("Approved", rec)
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec, approval=event)
        self.assertEqual(result["state"], "OWNER_APPROVAL_UNVERIFIED")

    def test_approved_onboard_without_task_is_normal_waiting(self):
        rec = reconstruction()
        event = self.event("Approved reconstruction", rec)
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=event, reader=lambda ref: source("Approved reconstruction"))
        self.assertEqual(result["state"], "ONBOARDED_AWAITING_TASK")
        self.assertEqual(result["next"], "AWAIT_OWNER_TASK")
        self.assertFalse(result["agent_invoked"])

    def test_task_does_not_imply_reconstruction_approval(self):
        rec = reconstruction()
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        task=self.event("Do task B", rec),
                        reader=lambda ref: source("Do task B"))
        self.assertEqual(result["state"], "AWAITING_RECONSTRUCTION_APPROVAL")

    def test_explicit_approval_and_task_can_share_source(self):
        rec = reconstruction()
        body = "Approved reconstruction; now do task B."
        event = self.event(body, rec)
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=event, task=event, reader=lambda ref: source(body))
        self.assertEqual(result["next"], "ENTER_PINNED_CODING_PROTOCOL")
        self.assertEqual(result["task_prompt"], body)

    def test_task_can_differ_from_recommendation(self):
        rec = reconstruction()
        bodies = {"approval": "Approve reconstruction", "task": "Investigate a different module."}
        approval = self.event(bodies["approval"], rec)
        task = self.event(bodies["task"], rec)
        task["ref"] = task["ref"].replace("-2", "-3")
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=approval, task=task,
                        reader=lambda ref: source(bodies["task"] if ref.endswith("-3") else bodies["approval"]))
        self.assertEqual(result["task_prompt"], bodies["task"])

    def test_changed_reconstruction_invalidates_its_approval(self):
        rec = reconstruction()
        event = self.event("Approve", rec)
        rec["rationale"] += " New information."
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=event, reader=lambda ref: source("Approve"))
        self.assertEqual(result["state"], "OWNER_APPROVAL_UNVERIFIED")

    def test_shared_owner_account_does_not_prove_owner_instruction(self):
        rec = reconstruction()
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=self.event("Approve", rec),
                        reader=lambda ref: source("Approve", owner_instruction=False))
        self.assertEqual(result["state"], "OWNER_APPROVAL_UNVERIFIED")

    def test_unrelated_ci_failure_is_not_global_blocker(self):
        rec = reconstruction()
        rec["findings"] = [{"id": "F1", "kind": "DEFECT", "impact": "Unrelated CI",
                           "action": "Retain separate repair", "refs": ["run:42"], "introduced": False}]
        self.assertEqual(assess(request(), rec)["next"], "ENTER_PINNED_CODING_PROTOCOL")

    def test_owner_decision_route_does_not_start_coding(self):
        rec = reconstruction()
        rec["choices"][0]["decision"] = "OWNER_DECISION_REQUIRED"
        result = assess(request(), rec)
        self.assertEqual(result["state"], "OWNER_DIRECTION_DECISION_REQUIRED")
        calls = []
        invoke(result, {"task": "unapproved route"}, authorize=lambda _: True,
               executor=lambda item: calls.append(item))
        self.assertEqual(calls, [])

    def test_new_onboard_task_can_supersede_decision_recommendation(self):
        rec = reconstruction()
        rec["choices"][0]["decision"] = "OWNER_DECISION_REQUIRED"
        body = "Approve the reconstruction; investigate different task B."
        event = self.event(body, rec)
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=event, task=event, reader=lambda ref: source(body))
        self.assertEqual(result["next"], "ENTER_PINNED_CODING_PROTOCOL")
        self.assertEqual(result["task_prompt"], body)

    def test_profile_failure_preserves_source_investigation(self):
        case = request()
        case["profile"]["effort"] = "low"
        result = assess(case, reconstruction())
        self.assertEqual(result["state"], "PROFILE_UNQUALIFIED")
        self.assertEqual(result["next"], "RETAIN_INVESTIGATION_CONFIGURE_PROFILE")

    def test_preparation_cannot_claim_semantic_verification(self):
        result = assess(request(), reconstruction())
        self.assertEqual(result["semantic_assessment"], "NOT_MACHINE_VERIFIED")
        self.assertFalse(result["coding_authorized"])

    def test_assisted_needs_real_predecessor_reconciliation(self):
        case = request("ASSISTED")
        case["phase"] = "1b"
        rec = reconstruction()
        rec["phase"] = "1b"
        self.assertEqual(assess(case, rec)["next"], "G1_RECONCILE_ONCE")

    def test_wrong_actor_cannot_submit_predecessor_direction(self):
        case = request("ASSISTED")
        case["phase"] = "2"
        rec = reconstruction()
        rec["phase"] = "2"
        with self.assertRaises(ValueError):
            assess(case, rec)

    def test_no_executor_means_prepared_not_invoked(self):
        report = assess(request(), reconstruction())
        result = invoke(report, {"task": "T1"})
        self.assertFalse(result["agent_invoked"])
        self.assertEqual(result["state"], "CODING_ASSIGNMENT_PREPARED")

    def test_waiting_onboard_cannot_invoke_even_with_old_authority(self):
        report = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), reconstruction())
        calls = []
        result = invoke(report, {"task": "old"}, executor=lambda item: calls.append(item))
        self.assertFalse(calls)
        self.assertFalse(result["agent_invoked"])

    def test_executor_needs_actual_scope_and_returns_real_receipt(self):
        report = assess(request(), reconstruction())
        calls = []
        result = invoke(report, {"task": "T1"},
                        authorize=lambda item: True,
                        executor=lambda item: calls.append(item) or {"ref": "session://actual"})
        self.assertEqual(len(calls), 1)
        self.assertTrue(result["agent_invoked"])
        self.assertEqual(result["response_ref"], "session://actual")
        self.assertFalse(result["workflow_executed"])

    def test_approval_only_source_cannot_be_reused_as_task(self):
        rec = reconstruction()
        event = self.event("Approve reconstruction", rec)
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=event, task=event,
                        reader=lambda ref: source("Approve reconstruction",
                            kinds=["RECONSTRUCTION_APPROVAL"]))
        self.assertEqual(result["state"], "OWNER_TASK_UNVERIFIED")

    def test_verified_body_is_reused_without_second_fetch(self):
        rec = reconstruction()
        body = "Approve reconstruction and do task B"
        event = self.event(body, rec)
        calls = []
        def read(ref):
            calls.append(ref)
            return source(body if len(calls) == 1 else "Unverified replacement")
        result = assess(request("ONBOARD", "AWAIT_OWNER_TASK"), rec,
                        approval=event, task=event, reader=read)
        self.assertEqual(calls, [event["ref"]])
        self.assertEqual(result["task_prompt"], body)

    def test_exact_supplied_1b_does_not_require_publication(self):
        import json
        prior = reconstruction()
        prior["phase"] = "1b"
        case = request("ASSISTED")
        case.update(phase="2", actor="previous")
        record = reconstruction()
        record.update(phase="2", actor="previous")
        body = json.dumps(prior)
        record["prior_1b"] = {"body_text": body, "supplied_ref": "conversation:incoming",
                              "digest": digest(body)}
        result = assess(case, record)
        self.assertEqual(result["next"], "ENTER_PINNED_CODING_PROTOCOL")
        self.assertEqual(result["prior_1b_grade"], "SUPPLIED_UNVERIFIED")

    def test_duplicate_receipt_requires_host_reconciliation_without_resend(self):
        report = assess(request(), reconstruction())
        prepared = invoke(report, {"task": "T1"})
        calls = []
        result = invoke(report, {"task": "T1"}, authorize=lambda payload: True,
                        executor=lambda payload: calls.append(payload),
                        receipts=[{"target": prepared["target"], "response_ref": "session://prior"}])
        self.assertEqual(result["state"], "VERIFY_EXISTING_INVOCATION")
        self.assertEqual(calls, [])


    def test_ambiguous_delivery_never_becomes_fake_success(self):
        report = assess(request(), reconstruction())
        result = invoke(report, {"task": "T1"}, authorize=lambda item: True,
                        executor=lambda item: None)
        self.assertEqual(result["state"], "INVOCATION_UNCONFIRMED")
        self.assertFalse(result["agent_invoked"])


if __name__ == "__main__":
    unittest.main()
