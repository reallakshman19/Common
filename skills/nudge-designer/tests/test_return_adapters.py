"""Native reports remain claims; intake does not accept outcomes or change plans."""
import copy
import unittest

from adapter_support import team_case, native_return
from nd_io import ContractError
from nd_team import task_binding
from nd_returns import receive
from nd_adapters import adapt


class ReturnAdapterTests(unittest.TestCase):
    def setUp(self):
        self.intent, self.plan, self.profiles = team_case()
        self.ident = self.plan["nudges"][0]["id"]
        self.report = native_return(task_binding(self.intent, self.plan, self.ident))

    def check(self):
        return receive(self.intent, self.plan, self.report, self.profiles)

    def test_roundtrip_preserves_native_report_and_does_not_promote_pass(self):
        before = copy.deepcopy([self.intent, self.plan, self.report])
        result = self.check()
        self.assertEqual(result["status"], "RETURN_RECORDED")
        self.assertEqual(result["native_report"], self.report["native_report"])
        self.assertEqual(result["accepted_outcomes"], [])
        self.assertFalse(result["execution_verified"])
        self.assertFalse(result["authority_verified"])
        self.assertEqual(result["freshness"], "NOT_ASSESSED")
        self.assertEqual(before, [self.intent, self.plan, self.report])

    def test_cross_task_stale_and_wrong_actor_returns_fail(self):
        for mutate in (lambda r: r["binding"].update(nudge_id="N-EXPORT"),
                       lambda r: r["binding"].update(plan_revision=99),
                       lambda r: r.update(actor_id="R")):
            report = copy.deepcopy(self.report)
            mutate(report)
            with self.assertRaisesRegex(ContractError, "binding|actor"):
                receive(self.intent, self.plan, report, self.profiles)

    def test_changed_plan_needs_issued_snapshot_without_destroying_history(self):
        self.plan["strategy"] += " Revised direction."
        with self.assertRaisesRegex(ContractError, "issued|binding"):
            self.check()

    def test_binding_metadata_types_are_exact_not_python_numeric_equality(self):
        for revision in (True, 1.0):
            report = copy.deepcopy(self.report)
            report["binding"]["plan_revision"] = revision
            with self.assertRaisesRegex(ContractError, "binding"):
                receive(self.intent, self.plan, report, self.profiles)

    def test_source_mismatch_is_recorded_as_stale_evidence_not_discarded(self):
        self.intent["sources"][0]["revision"] = "source-v1"
        from nd_contract import intent_digest
        self.plan["intent_sha256"] = intent_digest(self.intent)
        self.report["binding"] = task_binding(self.intent, self.plan, self.ident)
        self.report["source_observations"] = [{"source_id": "S-CASE", "revision": "source-v2"}]
        result = self.check()
        self.assertEqual(result["freshness"], "DISCREPANCY_RECORDED")
        self.assertIn("S-CASE", result["source_discrepancies"])
        self.assertEqual(result["accepted_outcomes"], [])

    def test_declared_findings_do_not_expand_scope_or_automatically_classify(self):
        for kind in ("DRIFT", "IMPROVEMENT", "NEW_ISSUE", "ASSUMPTION_CONFLICT"):
            self.report["findings"] = [{"kind": kind, "text": "Reported finding, not verified here.",
                                       "item_refs": ["R-EXPORT"], "attempt_refs": ["A1"]}]
            result = self.check()
            self.assertEqual(result["findings"][0]["declared_kind"], kind)
            self.assertIn("R-EXPORT", result["outside_nudge_refs"])
            self.assertFalse(result["scope_expanded"])
            self.assertFalse(result["semantic_classification_verified"])

    def test_blocked_return_preserves_attempt_restriction_and_independent_work(self):
        self.report.update(claimed_status="BLOCKED", next_proposal="Continue independent CSV preparation.")
        self.report["attempts"][0].update(state="BLOCKED", observed="Python is unavailable in this host.")
        result = self.check()
        self.assertEqual(result["claimed_status"], "BLOCKED")
        self.assertIn("N-EXPORT", result["independent_candidates"])
        self.assertFalse(result["workflow_locked"])

    def test_no_execution_cannot_be_presented_as_complete(self):
        self.report["attempts"][0]["state"] = "NOT_RUN"
        with self.assertRaisesRegex(ContractError, "COMPLETE"):
            self.check()

    def test_indirect_dependents_are_not_listed_as_independent(self):
        descendant = copy.deepcopy(self.plan["nudges"][1])
        descendant.update(id="N-DESCENDANT", depends_on=["N-REPAIR"])
        self.plan["nudges"].append(descendant)
        self.report["binding"] = task_binding(self.intent, self.plan, self.ident)
        result = self.check()
        self.assertNotIn("N-DESCENDANT", result["independent_candidates"])

    def test_reviewer_gets_actual_native_content_and_attempts(self):
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "reviewer", "plain",
                       recipient_id="R", report=self.report)
        self.assertIn("Native result: PASS", packet["content"])
        self.assertIn(self.report["attempts"][0]["action"], packet["content"])

    def test_review_relationship_participates_in_reconciliation(self):
        from nd_reconcile import impact_report
        review = copy.deepcopy(self.plan["nudges"][0])
        review.update(id="N-REVIEW", depends_on=[])
        review["assignment"].update(role="REVIEWER", participant_id="R", review_of=["N-PROBE"])
        self.plan["nudges"].append(review)
        self.report["binding"] = task_binding(self.intent, self.plan, self.ident)
        result = self.check()
        self.assertNotIn("N-REVIEW", result["independent_candidates"])
        changed = copy.deepcopy(self.intent)
        next(row for row in changed["items"] if row["id"] == "F-RACE")["text"] += " Changed observation."
        impact = impact_report(self.intent, self.plan, changed, self.profiles)
        self.assertIn("N-REVIEW", impact["affected_nudges"])

    def test_self_review_conflict_and_missing_independence_are_explicit(self):
        result = self.check()
        self.assertEqual(result["independence"], "NOT_ESTABLISHED")
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "reviewer", "plain",
                       recipient_id="W", report=self.report)
        self.assertEqual(packet["review_conflict"], "SAME_RECORDED_PARTICIPANT")
        self.assertFalse(packet["independence_verified"])

    def test_unknown_fields_refs_duplicate_attempts_and_unsafe_urls_fail(self):
        mutations = [lambda r: r.update(approved=True),
                     lambda r: r["findings"][0].update(item_refs=["invented"]),
                     lambda r: r["attempts"].append(copy.deepcopy(r["attempts"][0])),
                     lambda r: r["native_report"].update(locator="https://user:secret@example.com/")]
        for mutate in mutations:
            report = copy.deepcopy(self.report)
            mutate(report)
            with self.assertRaises(ContractError):
                receive(self.intent, self.plan, report, self.profiles)

    def test_unicode_crlf_native_text_is_preserved_as_supplied(self):
        import hashlib
        content = "# முடிவு\r\nSigned displacement: +0.25 mm\r\n"
        self.report["native_report"]["content"] = content
        result = self.check()
        self.assertEqual(result["native_report"]["content"], content)
        self.assertEqual(result["native_content_sha256"], hashlib.sha256(content.encode("utf-8")).hexdigest())

    def test_binary_native_artifact_can_be_referenced_without_inventing_content(self):
        self.report["native_report"].update(format="application/pdf", locator="study.pdf", content=None)
        result = self.check()
        self.assertEqual(result["native_representation"], "REFERENCE_ONLY")
        self.assertIsNone(result["native_content_sha256"])
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "reviewer", "plain", report=self.report)
        self.assertIn("authorized reader", packet["content"])
        self.report["native_report"]["locator"] = None
        with self.assertRaisesRegex(ContractError, "locator"):
            self.check()

    def test_owner_return_view_distinguishes_issued_work_from_new_continuation(self):
        import hashlib
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "owner", "plain", report=self.report)
        self.assertIn("Issued task:", packet["content"])
        self.assertNotIn("Next proposed work:", packet["content"])
        self.assertIn(self.report["next_proposal"], packet["content"])
        self.assertEqual(packet["content_sha256"], hashlib.sha256(packet["content"].encode("utf-8")).hexdigest())


if __name__ == "__main__":
    unittest.main()
