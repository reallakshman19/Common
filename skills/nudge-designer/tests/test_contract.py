"""Behavioral contracts: declarations bind; they never authenticate or authorize."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from nd_contract import intent_digest, validate_intent, validate_plan
from nd_io import ContractError, load_json
from nd_profiles import load_profiles, profile_digest


def case(name="lfea"):
    folder = ROOT / "examples" / name
    return load_json(folder / "intent.json"), load_json(folder / "plan.json")


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.intent, self.plan = case()
        self.profiles = load_profiles()

    def rebound(self):
        self.plan["intent_sha256"] = intent_digest(self.intent)

    def check(self):
        return validate_plan(self.intent, self.plan, self.profiles)

    def test_four_domains_and_mixed_profiles_are_structural_only(self):
        for name in ("lfea", "logic", "grade11", "fea"):
            with self.subTest(name=name):
                intent, plan = case(name)
                report = validate_plan(intent, plan, self.profiles)
                self.assertEqual(report["status"], "STRUCTURALLY_VALID")
                self.assertEqual(report["semantic_quality"], "NOT_MACHINE_VERIFIED")
                self.assertEqual(report["coverage_basis"], "DECLARED_ITEMS_ONLY")
                self.assertFalse(report["execution_performed"])
                self.assertFalse(report["authority_verified"])
                self.assertFalse(report["sources_authenticated"])
                self.assertGreater(len(plan["profile_ids"]), 1)

    def test_stale_intent_content_rejected_without_revision_change(self):
        self.intent["items"][0]["text"] += " Changed scope."
        with self.assertRaisesRegex(ContractError, "intent content"):
            self.check()

    def test_wrong_intent_revision_rejected(self):
        self.plan["intent_revision"] += 1
        with self.assertRaisesRegex(ContractError, "intent identity"):
            self.check()

    def test_changed_profile_content_rejected(self):
        self.profiles["core"]["review_questions"].append("A new question")
        with self.assertRaisesRegex(ContractError, "profile content"):
            self.check()

    def test_duplicate_ids_rejected_across_item_and_outcome(self):
        self.intent["outcomes"][0]["id"] = self.intent["items"][0]["id"]
        with self.assertRaisesRegex(ContractError, "duplicate"):
            validate_intent(self.intent)

    def test_unknown_source_reference_rejected(self):
        self.intent["items"][0]["source_refs"] = ["invented"]
        with self.assertRaisesRegex(ContractError, "source"):
            validate_intent(self.intent)

    def test_unsourced_requirement_rejected(self):
        self.intent["items"][0]["source_refs"] = []
        with self.assertRaisesRegex(ContractError, "source"):
            validate_intent(self.intent)

    def test_genuine_unknown_may_have_no_citation(self):
        unknown = next(x for x in self.intent["items"] if x["kind"] == "UNKNOWN")
        unknown["source_refs"] = []
        self.rebound()
        self.check()

    def test_source_assessment_cannot_claim_verified(self):
        self.intent["sources"][0]["assessment"] = "VERIFIED"
        with self.assertRaises(ContractError):
            validate_intent(self.intent)

    def test_injected_authority_field_is_not_accepted(self):
        self.plan["execution_authorized"] = True
        with self.assertRaises(ContractError):
            self.check()

    def test_profile_operations_and_evidence_must_exist(self):
        for key in ("reasoning_moves", "evidence_methods"):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["nudges"][0][key] = ["magic"]
                with self.assertRaisesRegex(ContractError, "profile"):
                    validate_plan(self.intent, plan, self.profiles)

    def test_missing_declared_requirement_coverage_rejected(self):
        requirement = next(x["id"] for x in self.intent["items"] if x["kind"] == "REQUIREMENT")
        self.plan["coverage"] = [x for x in self.plan["coverage"] if x["target_id"] != requirement]
        with self.assertRaisesRegex(ContractError, "coverage"):
            self.check()

    def test_unknowns_and_outcomes_cannot_disappear(self):
        for kind in ("UNKNOWN", "OUTCOME"):
            plan = copy.deepcopy(self.plan)
            target = (self.intent["outcomes"][0]["id"] if kind == "OUTCOME" else
                      next(x["id"] for x in self.intent["items"] if x["kind"] == kind))
            plan["coverage"] = [x for x in plan["coverage"] if x["target_id"] != target]
            with self.assertRaisesRegex(ContractError, "coverage"):
                validate_plan(self.intent, plan, self.profiles)

    def test_evidence_disposition_needs_a_source_not_an_acceptance_flag(self):
        row = self.plan["coverage"][0]
        row.update(disposition="EVIDENCE_REPORTED", evidence_refs=[])
        with self.assertRaisesRegex(ContractError, "evidence"):
            self.check()

    def test_planned_disposition_needs_a_real_nudge(self):
        self.plan["coverage"][0].update(disposition="PLANNED", nudge_ids=[])
        with self.assertRaisesRegex(ContractError, "nudge"):
            self.check()

    def test_coverage_cannot_link_only_an_unrelated_nudge(self):
        intent, plan = case("logic")
        row = next(x for x in plan["coverage"] if x["target_id"] == "R-EXPORT")
        row.update(disposition="PLANNED", nudge_ids=["N-PROBE"])
        with self.assertRaisesRegex(ContractError, "coverage nudge"):
            validate_plan(intent, plan, self.profiles)

    def test_orphan_and_self_dependencies_rejected(self):
        nudge = self.plan["nudges"][0]
        for dependency in ("missing", nudge["id"]):
            nudge["depends_on"] = [dependency]
            with self.assertRaises(ContractError):
                self.check()

    def test_dependency_cycle_rejected(self):
        first, second = self.plan["nudges"][:2]
        first["depends_on"] = [second["id"]]
        second["depends_on"] = [first["id"]]
        with self.assertRaisesRegex(ContractError, "cycle"):
            self.check()

    def test_outcome_hierarchy_cycle_rejected(self):
        first, second = self.intent["outcomes"][:2]
        first["parent_id"], second["parent_id"] = second["id"], first["id"]
        with self.assertRaisesRegex(ContractError, "cycle"):
            validate_intent(self.intent)

    def test_nested_nudges_supported_but_parent_cycle_rejected(self):
        first, second = self.plan["nudges"][:2]
        second["parent_id"] = first["id"]
        second["depends_on"] = []
        self.check()
        first["parent_id"] = second["id"]
        with self.assertRaisesRegex(ContractError, "cycle"):
            self.check()

    def test_branches_must_name_existing_other_nudges(self):
        self.plan["nudges"][0]["branches"][0]["next_ids"] = ["missing"]
        with self.assertRaisesRegex(ContractError, "branch"):
            self.check()

    def test_applicable_constraint_cannot_be_omitted(self):
        self.plan["nudges"][0]["boundaries"]["preserve_refs"] = []
        with self.assertRaisesRegex(ContractError, "constraint"):
            self.check()

    def test_constraint_for_unrelated_outcome_is_not_global(self):
        intent, plan = case("logic")
        intent["items"].append({"id": "C-OTHER", "kind": "CONSTRAINT", "text": "Keep the unrelated export format.",
            "source_refs": [intent["sources"][0]["id"]], "condition": None,
            "state": "CURRENT", "outcome_refs": [intent["outcomes"][-1]["id"]]})
        for nudge in plan["nudges"]:
            if intent["outcomes"][-1]["id"] in nudge["outcome_refs"]:
                nudge["boundaries"]["preserve_refs"].append("C-OTHER")
        plan["coverage"].append({"target_id": "C-OTHER", "disposition": "DEFERRED",
            "nudge_ids": [], "evidence_refs": [], "rationale": "Separate export task remains recorded."})
        plan["intent_sha256"] = intent_digest(intent)
        validate_plan(intent, plan, self.profiles)

    def test_unsafe_source_url_and_duplicate_json_rejected(self):
        self.intent["sources"][0]["locator"] = "https://user:secret@example.com/a"
        with self.assertRaisesRegex(ContractError, "locator"):
            validate_intent(self.intent)
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for data in ('{"id":1,"id":2}', '{"a":NaN}', '{"a":1e999}'):
                path.write_text(data)
                with self.assertRaises(ContractError):
                    load_json(path)

    def test_input_objects_remain_unchanged(self):
        before = json.dumps([self.intent, self.plan, self.profiles], sort_keys=True)
        self.check()
        self.assertEqual(before, json.dumps([self.intent, self.plan, self.profiles], sort_keys=True))


if __name__ == "__main__":
    unittest.main()
