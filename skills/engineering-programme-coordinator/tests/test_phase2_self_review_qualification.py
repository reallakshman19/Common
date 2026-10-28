#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coordlib import load_yaml
from phase2_self_review_qualification import (
    BOUNDARIES,
    CASE_IDS,
    STAGES,
    canonical_digest,
    compile_source,
    object_digest,
    validate_result,
    validate_result_shape,
    validate_source,
)

SOURCE_PATH = ROOT / "references" / "p2-i-self-review-qualification-source.yaml"


class Phase2SelfReviewQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = load_yaml(SOURCE_PATH)
        cls.result = compile_source(cls.source, REPO_ROOT)

    def test_source_digest_is_frozen(self) -> None:
        self.assertEqual(
            "817adca790051a23acc890f9d01e7fafba1d4f3a68a6490f88e06410cb5caa60",
            canonical_digest(self.source),
        )

    def test_clean_replay_covers_all_six_stages(self) -> None:
        clean = self.result["clean_replay"]
        self.assertEqual(list(STAGES), [row["stage"] for row in clean])
        self.assertTrue(all(row["replay_clean"] for row in clean))

    def test_mutation_cases_cover_all_six_stages(self) -> None:
        cases = self.result["mutation_cases"]
        self.assertEqual(list(STAGES), [row["stage"] for row in cases])
        self.assertEqual(list(CASE_IDS[1:]), [row["id"] for row in cases])

    def test_all_seeded_cases_are_shallow_green(self) -> None:
        self.assertTrue(
            all(row["shallow_green"] for row in self.result["mutation_cases"])
        )
        self.assertEqual(
            6,
            self.result["accounting"]["shallow_green_seeded"],
        )

    def test_all_seeded_cases_are_semantically_rejected(self) -> None:
        self.assertTrue(
            all(row["semantic_rejected"] for row in self.result["mutation_cases"])
        )
        self.assertEqual(6, self.result["accounting"]["seeded_detected"])
        self.assertEqual(0, self.result["accounting"]["seeded_missed"])

    def test_no_clean_false_block(self) -> None:
        self.assertEqual(0, self.result["accounting"]["clean_false_blocks"])

    def test_result_is_qualified_only_for_p2i(self) -> None:
        self.assertEqual("QUALIFIED", self.result["qualification_status"])
        self.assertEqual(
            "PHASE2_SELF_REVIEW_QUALIFICATION_EVIDENCE",
            self.result["authority"],
        )

    def test_historical_lanes_remain_distinct(self) -> None:
        lanes = self.result["historical_lanes"]
        self.assertEqual(
            ["P2-S1", "P2-S2", "P2-S3", "P2-S4", "P2-S6"],
            lanes["pr522_stages"],
        )
        self.assertEqual(["P2-S5"], lanes["pr565_stages"])
        self.assertFalse(lanes["monolithic_synthetic_candidate"])

    def test_every_seed_retains_rejection_reason(self) -> None:
        for row in self.result["mutation_cases"]:
            self.assertTrue(row["rejection_errors"], row["id"])

    def test_l0_seed_is_caught_by_source_bound_replay(self) -> None:
        row = self.result["mutation_cases"][0]
        self.assertEqual("SOURCE_BOUND_L0_REPLAY", row["detector"])
        self.assertTrue(
            any("fresh source replay" in e or "stored manifest" in e for e in row["rejection_errors"]),
            row,
        )

    def test_l1_seed_is_caught_by_exact_base_replay(self) -> None:
        row = self.result["mutation_cases"][1]
        self.assertEqual("EXACT_BASE_L1_REPLAY", row["detector"])
        self.assertTrue(
            any("fresh exact-base replay" in e or "stored content" in e for e in row["rejection_errors"]),
            row,
        )

    def test_l2_seed_is_caught_by_exact_diff_replay(self) -> None:
        row = self.result["mutation_cases"][2]
        self.assertEqual("EXACT_DIFF_L2_REPLAY", row["detector"])
        self.assertTrue(
            any("fresh exact-diff replay" in e or "stored content" in e for e in row["rejection_errors"]),
            row,
        )

    def test_s4_seed_is_caught_by_closed_denominator_replay(self) -> None:
        row = self.result["mutation_cases"][3]
        self.assertEqual("SOURCE_BOUND_CLOSED_DENOMINATOR_REPLAY", row["detector"])
        self.assertTrue(
            any("stored ledger" in e or "denominator replay" in e for e in row["rejection_errors"]),
            row,
        )

    def test_s5_seed_is_caught_by_exact_object_replay(self) -> None:
        row = self.result["mutation_cases"][4]
        self.assertEqual("SOURCE_BOUND_REPAIR_REPLAY", row["detector"])
        self.assertTrue(
            any("stored result" in e or "repair replay" in e for e in row["rejection_errors"]),
            row,
        )

    def test_s6_seed_is_caught_by_verdict_replay(self) -> None:
        row = self.result["mutation_cases"][5]
        self.assertEqual("SOURCE_BOUND_VERDICT_REPLAY", row["detector"])
        self.assertTrue(
            any("stored projection" in e or "verdict replay" in e for e in row["rejection_errors"]),
            row,
        )

    def test_unbound_result_validation_fails_closed(self) -> None:
        errors = validate_result(self.result)
        self.assertTrue(
            any("source-bound Phase-2 qualification replay is required" in e for e in errors),
            errors,
        )

    def test_bound_result_validation_passes(self) -> None:
        self.assertEqual(
            [],
            validate_result(self.result, self.source, REPO_ROOT),
        )

    def test_recomputed_result_tamper_cannot_self_certify(self) -> None:
        result = copy.deepcopy(self.result)
        result["mutation_cases"][0]["detector"] = "FAKE_DETECTOR"
        result["result_digest"] = object_digest(result, "result_digest")
        errors = validate_result(result, self.source, REPO_ROOT)
        self.assertTrue(errors)

    def test_source_rejects_duplicate_case_identity(self) -> None:
        source = copy.deepcopy(self.source)
        source["qualification_cases"][1]["id"] = source["qualification_cases"][2]["id"]
        errors = validate_source(source)
        self.assertTrue(any("frozen P2-I case sequence" in e for e in errors), errors)

    def test_source_rejects_stage_coverage_drift(self) -> None:
        source = copy.deepcopy(self.source)
        source["qualification_cases"][1]["stage"] = "P2-S2"
        errors = validate_source(source)
        self.assertTrue(any("cover P2-S1 through P2-S6" in e for e in errors), errors)

    def test_source_rejects_unsafe_retained_path(self) -> None:
        source = copy.deepcopy(self.source)
        source["retained_artifacts"]["l0"]["source_path"] = "../escape.yaml"
        errors = validate_source(source)
        self.assertTrue(any("unsafe retained artifact path" in e for e in errors), errors)

    def test_result_schema_rejects_pass_gate_and_review_authority(self) -> None:
        for field, value in [
            ("pass", True),
            ("engineering_pass", True),
            ("gate", "ADVANCE_ELIGIBLE"),
            ("next_action", "ADVANCE"),
            ("independent_review", True),
            ("merge_authority", True),
            ("production_mode", "DEFAULT_GATE"),
        ]:
            result = copy.deepcopy(self.result)
            result[field] = value
            result["result_digest"] = object_digest(result, "result_digest")
            self.assertTrue(validate_result_shape(result), field)

    def test_authority_boundaries_are_qualification_only(self) -> None:
        self.assertEqual(BOUNDARIES, self.result["authority_boundaries"])
        self.assertTrue(BOUNDARIES["consumes_retained_real_artifacts"])
        self.assertTrue(BOUNDARIES["applies_seed_overlays_in_memory_only"])
        self.assertFalse(BOUNDARIES["mutates_retained_artifacts"])
        self.assertFalse(BOUNDARIES["emits_engineering_pass"])
        self.assertFalse(BOUNDARIES["emits_independent_review"])
        self.assertFalse(BOUNDARIES["emits_evidence_gate_decision"])
        self.assertFalse(BOUNDARIES["performs_lifecycle_advance"])
        self.assertFalse(BOUNDARIES["grants_merge_authority"])
        self.assertFalse(BOUNDARIES["grants_production_cutover"])


if __name__ == "__main__":
    unittest.main()
