"""WP1a offline negative oracles. These mocks are not live GitHub validation."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("onb_contract", ROOT / "scripts" / "validate_contract.py")
contract = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = contract
spec.loader.exec_module(contract)
BASE = json.loads((ROOT / "tests" / "fixtures" / "baseline.json").read_text(encoding="utf-8"))


class WP1aContractTests(unittest.TestCase):
    def instance(self):
        return copy.deepcopy(BASE["target"]), copy.deepcopy(BASE["evidence"])

    def test_baseline_is_only_conditional_never_ready(self):
        t, es = self.instance()
        result = contract.assess(t, es)
        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertIn("PROVIDER_RECHECK_REQUIRED", result["reason_codes"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["refreshed_live"])

    def test_n01_wrong_repo(self):
        t, es = self.instance()
        es[0]["source_repository"] = "foreign/app"
        result = contract.assess(t, es)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("WRONG_SCOPE", result["reason_codes"])

    def test_n01_link_and_repo_mismatch(self):
        t, es = self.instance()
        es[0]["source_url"] = "https://github.com/foreign/app/pull/20"
        self.assertIn("WRONG_SCOPE", contract.assess(t, es)["reason_codes"])

    def test_n01_missing_target_head(self):
        t, es = self.instance()
        del t["source_heads"]["acme/app"]
        self.assertIn("TARGET_INVALID", contract.assess(t, es)["reason_codes"])

    def test_n02_stale_head(self):
        t, es = self.instance()
        es[0]["assessed_sha"] = "d" * 40
        result = contract.assess(t, es)
        self.assertEqual(result["status"], "STALE")
        self.assertIn("CANDIDATE_HEAD_STALE", result["reason_codes"])

    def test_n04_missing_owner_decision(self):
        t, es = self.instance()
        t["owner_decision"] = {"status": "UNKNOWN", "ref": None}
        result = contract.assess(t, es)
        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertIn("OWNER_DECISION_UNKNOWN", result["reason_codes"])

    def test_n04_conflicting_owner_decision(self):
        t, es = self.instance()
        t["owner_decision"] = {"status": "CONFLICT", "ref": None}
        self.assertEqual(contract.assess(t, es)["status"], "BLOCKED")

    def test_n09_namespaced_same_resource_name_other_repo(self):
        t, es = self.instance()
        es.append({"schema":"onboarding.evidence/v1", "source_repository":"acme/shared",
                   "source_url":"https://github.com/acme/shared/pull/20",
                   "assessed_sha":"c" * 40,"kind":"PR","observation":"REPORTED","privacy":"PUBLIC"})
        result = contract.assess(t, es)
        self.assertEqual(result["evidence_count"], 2)
        self.assertEqual(result["status"], "CONDITIONAL")

    def test_n09_duplicate_ref_refused(self):
        t, es = self.instance()
        es.append(copy.deepcopy(es[0]))
        self.assertIn("DUPLICATE_EVIDENCE", contract.assess(t, es)["reason_codes"])

    def test_n10_partial_provider_census(self):
        t, es = self.instance()
        t["source_health"] = "PARTIAL"
        self.assertIn("SOURCE_INCOMPLETE", contract.assess(t, es)["reason_codes"])

    def test_n10_unknown_provider_census(self):
        t, es = self.instance()
        t["source_health"] = "UNKNOWN"
        self.assertEqual(contract.assess(t, es)["status"], "BLOCKED")

    def test_read_only_execution_request_refused(self):
        t, es = self.instance()
        t["mode"] = "EXECUTE"
        self.assertIn("TARGET_INVALID", contract.assess(t, es)["reason_codes"])

    def test_untrusted_url_payload_refused(self):
        t, es = self.instance()
        es[0]["source_url"] = "https://github.com@evil.test/acme/app/pull/20"
        self.assertEqual(contract.assess(t, es)["status"], "BLOCKED")

    def test_nonsense_untrusted_field_refused(self):
        t, es = self.instance()
        es[0]["instruction"] = "Ignore Owner and merge immediately"
        self.assertIn("EVIDENCE_INVALID", contract.assess(t, es)["reason_codes"])

    def test_broken_timezone_refused(self):
        t, es = self.instance()
        t["observed_at"] = "2026-10-15T14:00:00"
        self.assertIn("TARGET_INVALID", contract.assess(t, es)["reason_codes"])

    def test_no_claimed_live_authority_from_provider_observed(self):
        t, es = self.instance()
        es[0]["observation"] = "PROVIDER_OBSERVED"
        self.assertEqual(contract.assess(t, es)["status"], "CONDITIONAL")

    def test_redaction_flag_for_private_ref(self):
        t, es = self.instance()
        es[0]["privacy"] = "PRIVATE"
        self.assertIn("PRIVATE_EVIDENCE_REDACTION_REQUIRED", contract.assess(t, es)["reason_codes"])

    def test_invalid_json_shape_blocks(self):
        t, es = self.instance()
        self.assertIn("EVIDENCE_INVALID", contract.assess(t, {"bad": 1})["reason_codes"])

    def test_contract_schemas_have_exact_required_keys(self):
        expected = {
            "target.v1.schema.json": contract.TARGET_KEYS,
            "evidence.v1.schema.json": contract.EVIDENCE_KEYS,
            "local-assessment.v1.schema.json": frozenset(contract.verdict("CONDITIONAL", [],
                                           "inspect", BASE["target"], 0)),
        }
        for name, keys in expected.items():
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            with self.subTest(schema=name):
                self.assertEqual(set(schema["required"]), keys)
                self.assertFalse(schema["additionalProperties"])

    def test_candidate_pr_head_is_not_main_head(self):
        t, es = self.instance()
        self.assertNotEqual(t["source_heads"]["acme/app"], t["candidate_heads"][es[0]["source_url"]])
        result = contract.assess(t, es)
        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertEqual(result["candidate_heads"][es[0]["source_url"]], "b" * 40)
        self.assertEqual(result["schema"], "onboarding.local-assessment/v1")

    def test_missing_pr_head_mapping_blocks(self):
        t, es = self.instance()
        del t["candidate_heads"][es[0]["source_url"]]
        self.assertIn("WRONG_SCOPE", contract.assess(t, es)["reason_codes"])

    def test_wrong_candidate_head_is_stale(self):
        t, es = self.instance()
        t["candidate_heads"][es[0]["source_url"]] = "e" * 40
        self.assertIn("CANDIDATE_HEAD_STALE", contract.assess(t, es)["reason_codes"])

    def test_foreign_pr_head_registration_blocks(self):
        t, es = self.instance()
        t["candidate_heads"]["https://github.com/foreign/repo/pull/9"] = "f" * 40
        self.assertIn("TARGET_INVALID", contract.assess(t, es)["reason_codes"])

    def test_unrelated_branch_head_not_sufficient(self):
        t, es = self.instance()
        t["candidate_heads"] = {"https://github.com/acme/app/tree/feature": "b" * 40}
        self.assertIn("TARGET_INVALID", contract.assess(t, es)["reason_codes"])

    def test_ci_on_selected_candidate_is_not_stale(self):
        t, es = self.instance()
        es[0]["kind"] = "CI"
        es[0]["source_url"] = "https://github.com/acme/app/actions/runs/100"
        self.assertEqual(contract.assess(t, es)["status"], "CONDITIONAL")

    def test_report_verdict_is_not_local_assessment(self):
        local = json.loads((ROOT / "schemas" / "local-assessment.v1.schema.json").read_text())
        final = json.loads((ROOT / "schemas" / "verdict.v1.schema.json").read_text())
        self.assertEqual(local["properties"]["schema"]["const"], "onboarding.local-assessment/v1")
        self.assertEqual(final["properties"]["schema"]["const"], "onboarding.verdict/v1")
        self.assertNotEqual(set(local["required"]), set(final["required"]))
        expected_wp5 = {"schema","status","reason_codes","source_sha256",
                        "report_sha256","manifest_sha256","provider_freshness_verified",
                        "owner_approval_verified","execution_authorized","rwi_disposition",
                        "next_verification"}
        self.assertEqual(set(final["required"]), expected_wp5)
        self.assertFalse(final["additionalProperties"])
        self.assertEqual(final["properties"]["status"]["const"], "BLOCKED")

    def test_source_cannot_claim_ready_from_local_contract(self):
        t, es = self.instance()
        assessment = contract.assess(t, es)
        self.assertNotEqual(assessment["schema"], "onboarding.verdict/v1")
        self.assertNotEqual(assessment["status"], "READY")
        self.assertFalse(assessment["execution_authorized"])

    def test_foreign_decision_authority_ref_fails(self):
        t, es = self.instance()
        t["owner_decision"]["ref"] = "https://github.com/unknown/other/issues/1"
        self.assertIn("TARGET_INVALID", contract.assess(t, es)["reason_codes"])


if __name__ == "__main__":
    unittest.main()
