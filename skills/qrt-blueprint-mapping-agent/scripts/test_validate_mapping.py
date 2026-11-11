"""Regression/negative tests for structural preflight only; no math approval."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest
from validate_mapping import validate

TEMPLATE = (Path(__file__).resolve().parents[1] / "templates"
            / "mapping-record.template.json")
SAMPLE = json.loads(TEMPLATE.read_text(encoding="utf-8"))


class MappingContractTests(unittest.TestCase):
    def check_bad(self, data, marker):
        problems = validate(data)
        self.assertTrue(any(marker in p for p in problems), problems)

    def test_unsigned_template_is_structurally_valid_but_not_accepted(self):
        self.assertEqual(validate(SAMPLE), [])
        self.assertEqual(SAMPLE["academic"]["status"], "PENDING_INDEPENDENT")
        self.assertEqual(SAMPLE["owner"]["status"], "PENDING")

    def test_demand_is_not_inferred_from_stem_verb(self):
        value = deepcopy(SAMPLE)
        value["qrt"]["primary_demand"] = "REMEMBER"
        self.check_bad(value, "qrt.primary_demand")

    def test_five_difficulty_components_are_mandatory(self):
        value = deepcopy(SAMPLE)
        del value["qrt"]["difficulty_components"]["representation_translation"]
        self.check_bad(value, "qrt.difficulty_components")

    def test_no_fabricated_qualified_judgement(self):
        value = deepcopy(SAMPLE)
        value["qrt"]["asks"]["H2"]["verdict"] = "YES"
        self.check_bad(value, "qrt.asks.H2")

    def test_no_unverified_core2_authentic_page(self):
        value = deepcopy(SAMPLE)
        value["roles"].append({"role": "CORE2"})
        self.check_bad(value, "roles.CORE2")

    def test_no_cross_question_html_byte_comparison(self):
        value = deepcopy(SAMPLE)
        value["golden"]["comparison_mode"] = "SAME_QUESTION_EXACT"
        value["golden"]["same_question_as_fixture"] = False
        self.check_bad(value, "golden.comparison_mode")

    def test_no_unsigned_owner_approval(self):
        value = deepcopy(SAMPLE)
        value["owner"]["status"] = "ACCEPT"
        value["owner"]["decision_id"] = "MADE_UP"
        value["owner"]["decision_date"] = "2026-10-13"
        self.check_bad(value, "owner")

    def test_no_unsigned_golden_release(self):
        value = deepcopy(SAMPLE)
        value["owner"]["successor_golden_approved"] = True
        self.check_bad(value, "owner")

    def test_cannot_credit_unobserved_learner_prior_knowledge(self):
        value = deepcopy(SAMPLE)
        value["qrt"]["y_evidence"] = "DEMONSTRATED"
        value["qrt"]["y"] = "Pythagoras"
        self.check_bad(value, "qrt.y_evidence")

    def test_scored_difficulty_requires_reason(self):
        value = deepcopy(SAMPLE)
        value["qrt"]["difficulty_components"]["reasoning_chain_length"]["score"] = 1
        self.check_bad(value, "qrt.difficulty_components.reasoning_chain_length")

    def test_rendered_roles_need_blueprint_receipt(self):
        value = deepcopy(SAMPLE)
        value["roles"][0]["native_html_sha256"] = "a" * 64
        self.check_bad(value, "roles[0]")

    def test_signed_review_cannot_skip_asks(self):
        value = deepcopy(SAMPLE)
        value["academic"]["status"] = "ACCEPT_SIGNED"
        value["academic"]["reviewer_identity"] = "hypothetical"
        value["academic"]["qualifications"] = "hypothetical"
        value["academic"]["independent_of_author"] = True
        value["academic"]["conflict_declaration"] = "none"
        value["academic"]["reviewed_on"] = "2026-10-13"
        value["academic"]["signature_ref"] = "hypothetical"
        self.check_bad(value, "all twelve judgements")


if __name__ == "__main__":
    unittest.main()
