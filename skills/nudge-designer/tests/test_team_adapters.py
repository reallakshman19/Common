"""Role, capability and surface boundaries are independent of domain/model names."""
import copy
import unittest

from adapter_support import team_case
from nd_contract import validate_plan
from nd_io import ContractError
from nd_team import capability_fit, task_binding
from nd_adapters import adapt


class TeamAdapterTests(unittest.TestCase):
    def setUp(self):
        self.intent, self.plan, self.profiles = team_case()
        self.ident = self.plan["nudges"][0]["id"]

    def test_legacy_and_v11_are_supported_without_relabeling_v1(self):
        validate_plan(self.intent, self.plan, self.profiles)
        self.plan["schema"] = "nudge-designer.plan/v1"
        with self.assertRaises(ContractError):
            validate_plan(self.intent, self.plan, self.profiles)

    def test_per_task_fit_records_claim_strength_without_qualification(self):
        report = capability_fit(self.plan, self.ident, "W")
        self.assertEqual(report["status"], "RECORDED_FIT")
        self.assertFalse(report["qualification_verified"])
        self.assertFalse(report["execution_authorized"])
        self.plan["participants"][0]["capabilities"][0]["basis"] = "REPORTED"
        self.assertEqual(capability_fit(self.plan, self.ident, "W")["status"], "REPORTED_FIT")

    def test_unknown_and_missing_tools_are_scoped_to_one_task(self):
        worker = self.plan["participants"][0]
        worker["tools"] = []
        report = capability_fit(self.plan, self.ident, "W")
        self.assertEqual(report["status"], "NOT_ESTABLISHED")
        self.assertEqual(report["affected_nudge"], self.ident)
        worker["tools"] = [{"id": "python", "status": "UNAVAILABLE", "basis": "REPORTED",
                            "evidence_refs": [], "note": "Host lacks Python"}]
        self.assertEqual(capability_fit(self.plan, self.ident, "W")["status"], "MISSING_REQUIREMENTS")
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "coordinator", "plain")
        self.assertIn("N-EXPORT", packet["content"])
        self.assertFalse(packet["workflow_locked"])

    def test_model_name_and_high_effort_do_not_establish_fit(self):
        worker = self.plan["participants"][0]
        worker.update(model="very-powerful-model", reasoning_effort="maximum", capabilities=[], tools=[])
        self.assertEqual(capability_fit(self.plan, self.ident, "W")["status"], "NOT_ESTABLISHED")

    def test_observed_claim_requires_evidence_and_roles_are_checked(self):
        self.plan["participants"][0]["capabilities"][0]["evidence_refs"] = []
        with self.assertRaisesRegex(ContractError, "observed"):
            validate_plan(self.intent, self.plan, self.profiles)
        self.plan["participants"][0]["capabilities"][0]["evidence_refs"] = ["S-CASE"]
        self.plan["nudges"][0]["assignment"]["role"] = "REVIEWER"
        with self.assertRaisesRegex(ContractError, "role"):
            validate_plan(self.intent, self.plan, self.profiles)

    def test_guided_work_requires_a_method_without_restricting_open_work(self):
        assignment = self.plan["nudges"][0]["assignment"]
        assignment["method"] = None
        with self.assertRaisesRegex(ContractError, "guided"):
            validate_plan(self.intent, self.plan, self.profiles)
        assignment["support"] = "OPEN"
        validate_plan(self.intent, self.plan, self.profiles)

    def test_roles_and_surfaces_compose_across_domains(self):
        for name in ("logic", "grade11", "fea", "lfea"):
            intent, plan, profiles = team_case(name)
            ident = plan["nudges"][0]["id"]
            for role in ("owner", "designer", "worker", "specialist", "reviewer", "coordinator", "successor"):
                for surface in ("plain", "github", "nextnudge-manual", "buddy-checkpoint"):
                    packet = adapt(intent, plan, ident, profiles, role, surface)
                    self.assertFalse(packet["execution_dispatched"])
                    self.assertFalse(packet["native_import_object"])
                    self.assertFalse(packet["authority_verified"])
                    self.assertEqual(packet["binding"]["nudge_id"], ident)
                    self.assertIn(intent["purpose"], packet["content"])

    def test_worker_keeps_seven_elements_and_audience_does_not_reassign(self):
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "worker", "plain")
        self.assertEqual(packet["content"].count("\n## "), 7)
        review = adapt(self.intent, self.plan, self.ident, self.profiles, "reviewer", "github", recipient_id="R")
        self.assertEqual(review["binding"]["participant_id"], "W")
        self.assertEqual(review["recipient_id"], "R")

    def test_delivery_requires_explicit_selection_and_does_not_import_defaults(self):
        with self.assertRaisesRegex(ContractError, "delivery protocol"):
            adapt(self.intent, self.plan, self.ident, self.profiles, "worker", "delivery")
        self.intent["protocols"]["delivery"] = "https://example.com/pinned-protocol"
        from nd_contract import intent_digest
        self.plan["intent_sha256"] = intent_digest(self.intent)
        packet = adapt(self.intent, self.plan, self.ident, self.profiles, "worker", "delivery")
        self.assertIn("https://example.com/pinned-protocol", packet["content"])
        self.assertIsNone(self.intent["protocols"]["thinking"])

    def test_binding_changes_with_task_or_roster_and_inputs_remain_unchanged(self):
        before = copy.deepcopy([self.intent, self.plan])
        old = task_binding(self.intent, self.plan, self.ident)
        adapt(self.intent, self.plan, self.ident, self.profiles, "owner", "plain")
        self.assertEqual(before, [self.intent, self.plan])
        self.plan["participants"][0]["configuration_basis"] += " Updated observation."
        self.assertNotEqual(old, task_binding(self.intent, self.plan, self.ident))

    def test_standard_renderer_uses_assignment_support_and_participant_basis(self):
        from nd_render import render_nudge
        self.plan["participants"][0].update(model="recorded-runtime-name", reasoning_effort="recorded-effort")
        assignment = self.plan["nudges"][0]["assignment"]
        assignment.update(method="Inspect one original result before changing source.", worked_example="A contrast method.")
        result = render_nudge(self.intent, self.plan, self.ident, self.profiles)
        self.assertIn("recorded-runtime-name", result)
        self.assertIn(assignment["method"], result)
        self.assertIn(assignment["worked_example"], result)
        self.assertEqual(result.count("\n## "), 7)

    def test_runtime_evidence_change_reaches_only_dependent_work(self):
        from nd_contract import intent_digest
        from nd_reconcile import impact_report
        source = dict(self.intent["sources"][0], id="S-RUNTIME", revision="runtime-v1")
        self.intent["sources"].append(source)
        self.plan["participants"][0]["tools"][0]["evidence_refs"] = ["S-RUNTIME"]
        self.plan["intent_sha256"] = intent_digest(self.intent)
        changed = copy.deepcopy(self.intent)
        changed["sources"][-1]["revision"] = "runtime-v2"
        result = impact_report(self.intent, self.plan, changed, self.profiles)
        self.assertIn("N-PROBE", result["affected_nudges"])
        self.assertIn("N-REPAIR", result["affected_nudges"])
        self.assertNotIn("N-EXPORT", result["affected_nudges"])

    def test_review_relationship_cannot_make_an_execution_dependency_cycle(self):
        self.plan["nudges"][0]["assignment"]["review_of"] = ["N-REPAIR"]
        with self.assertRaisesRegex(ContractError, "cycle"):
            validate_plan(self.intent, self.plan, self.profiles)


if __name__ == "__main__":
    unittest.main()
