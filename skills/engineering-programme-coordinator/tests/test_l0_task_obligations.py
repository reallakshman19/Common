import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coordlib import load_yaml
from l0_task_obligations import (
    L0TaskObligationError,
    SOURCE_HEADING,
    canonical_digest,
    compile_l0,
    extract_precommitted_source,
    validate_manifest,
    validate_source,
)


SOURCE_PATH = ROOT / "references" / "p2-s1-l0-source.yaml"
MANIFEST_PATH = ROOT / "references" / "p2-s1-l0-manifest.yaml"


def source():
    return copy.deepcopy(load_yaml(SOURCE_PATH))


def manifest():
    return copy.deepcopy(load_yaml(MANIFEST_PATH))


def refresh_manifest_digest(value):
    body = copy.deepcopy(value)
    body.pop("manifest_digest", None)
    value["manifest_digest"] = canonical_digest(body)


class L0TaskObligationTests(unittest.TestCase):
    def test_retained_source_compiles_to_retained_manifest(self):
        self.assertEqual(compile_l0(source()), manifest())

    def test_compilation_is_deterministic(self):
        first = compile_l0(source())
        second = compile_l0(source())
        self.assertEqual(first, second)
        self.assertEqual(
            first["manifest_digest"],
            "85a05f6c308a5035ecf9308328f2bc13da42536a578de02031a92e53a91012e9",
        )

    def test_source_digest_and_freeze_ref_are_exact(self):
        value = compile_l0(source())
        self.assertEqual(
            value["source"]["digest"],
            "5be577a4b69a0d9f34e0f660fa15efcdde0eb944aad9d1c0f568311c5d1fc09e",
        )
        self.assertEqual(value["freeze"]["freeze_ref"], "sha256:" + value["source"]["digest"])

    def test_issue_markdown_source_extracts_exact_retained_source(self):
        markdown = (
            "# Child\n\n"
            + SOURCE_HEADING
            + "\n\n```yaml\n"
            + SOURCE_PATH.read_text(encoding="utf-8")
            + "```\n"
        )
        self.assertEqual(extract_precommitted_source(markdown), source())

    def test_issue_markdown_duplicate_source_heading_is_rejected(self):
        markdown = SOURCE_HEADING + "\n" + SOURCE_HEADING
        with self.assertRaisesRegex(L0TaskObligationError, "exactly one"):
            extract_precommitted_source(markdown)

    def test_issue_markdown_source_with_candidate_field_is_rejected(self):
        payload = SOURCE_PATH.read_text(encoding="utf-8") + "\ncandidate_sha: " + ("a" * 40) + "\n"
        markdown = SOURCE_HEADING + "\n\n```yaml\n" + payload + "```\n"
        with self.assertRaisesRegex(L0TaskObligationError, "Additional properties"):
            extract_precommitted_source(markdown)

    def test_candidate_field_is_not_legal_contract_input(self):
        value = source()
        value["candidate_sha"] = "a" * 40
        errors = validate_source(value)
        self.assertTrue(any("Additional properties are not allowed" in error for error in errors), errors)

    def test_implementation_evidence_is_not_legal_contract_input(self):
        for field in [
            "implementation_evidence",
            "coder_rationale",
            "reviewer_verdict",
            "diff_impact",
            "test_results",
            "pass",
            "reviewer_confidence",
        ]:
            value = source()
            value[field] = "forbidden"
            errors = validate_source(value)
            self.assertTrue(errors, field)

    def test_l2_impact_claim_type_is_rejected_from_l0_source(self):
        value = source()
        value["contract_claims"][0]["claim"]["type"] = "IMPACT"
        errors = validate_source(value)
        self.assertTrue(errors)

    def test_empty_contract_denominator_is_rejected(self):
        value = source()
        value["contract_claims"] = []
        errors = validate_source(value)
        self.assertTrue(any("non-empty" in error or "should be" in error for error in errors), errors)

    def test_duplicate_claim_id_is_rejected(self):
        value = source()
        value["contract_claims"].append(copy.deepcopy(value["contract_claims"][0]))
        errors = validate_source(value)
        self.assertTrue(any("claim ids must be globally unique" in error for error in errors), errors)

    def test_duplicate_evidence_requirement_id_is_rejected(self):
        value = source()
        value["contract_claims"][1]["evidence_required"][0]["id"] = (
            value["contract_claims"][0]["evidence_required"][0]["id"]
        )
        errors = validate_source(value)
        self.assertTrue(any("evidence requirement ids must be globally unique" in error for error in errors), errors)

    def test_non_precommitted_evidence_is_rejected(self):
        value = source()
        value["contract_claims"][0]["evidence_required"][0]["independence"] = "REVIEWER_GENERATED"
        errors = validate_source(value)
        self.assertTrue(errors)

    def test_every_source_claim_compiles_exactly_once(self):
        src = source()
        out = compile_l0(src)
        self.assertEqual(
            [row["id"] for row in out["obligations"]],
            [row["id"] for row in src["contract_claims"]],
        )

    def test_expectation_chain_is_preserved_exactly(self):
        src = source()
        out = compile_l0(src)
        by_id = {row["id"]: row for row in out["obligations"]}
        for claim in src["contract_claims"]:
            compiled = by_id[claim["id"]]
            for field in [
                "severity",
                "claim",
                "expected_observation",
                "plausible_green_but_wrong",
                "oracle_refs",
                "evidence_required",
            ]:
                self.assertEqual(compiled[field], claim[field])
            self.assertEqual(compiled["source_refs"], [src["identity"]["child_ref"]])

    def test_source_mutation_invalidates_stored_manifest(self):
        src = source()
        stored = manifest()
        src["one_primary_outcome"] += " changed"
        errors = validate_manifest(stored, src)
        self.assertTrue(any("fresh source replay" in error for error in errors), errors)

    def test_tampered_manifest_rejected_even_with_recomputed_digest(self):
        src = source()
        forged = manifest()
        forged["obligations"][0]["claim"]["statement"] = "forged"
        refresh_manifest_digest(forged)
        errors = validate_manifest(forged, src)
        self.assertTrue(any("fresh source replay" in error for error in errors), errors)

    def test_unbound_manifest_validation_fails_closed(self):
        errors = validate_manifest(manifest(), None)
        self.assertTrue(any("source-bound replay is required" in error for error in errors), errors)

    def test_authority_boundaries_are_all_false(self):
        value = compile_l0(source())
        self.assertFalse(any(value["authority_boundaries"].values()))

    def test_no_phase2_successor_surfaces_are_emitted(self):
        value = compile_l0(source())
        self.assertNotIn("l1", value)
        self.assertNotIn("l2", value)
        self.assertNotIn("ledger", value)
        self.assertNotIn("candidate_sha", value)

    def test_duplicate_dependency_producer_is_rejected(self):
        value = source()
        value["dependency_requirements"].append(
            copy.deepcopy(value["dependency_requirements"][0])
        )
        errors = validate_source(value)
        self.assertTrue(any("dependency producers must be unique" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
