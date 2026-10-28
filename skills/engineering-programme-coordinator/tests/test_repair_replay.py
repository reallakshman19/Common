#!/usr/bin/env python3
from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coordlib import load_yaml
from repair_replay import (
    BOUNDARIES,
    canonical_digest,
    compile_source,
    extract_precommitted_source,
    object_digest,
    validate_result,
    validate_result_shape,
    validate_source,
)

SOURCE_PATH = ROOT / "references" / "p2-s5-repair-replay-source.yaml"


class RepairReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = load_yaml(SOURCE_PATH)
        cls.result = compile_source(cls.source, REPO_ROOT)

    def test_source_digest_is_frozen(self) -> None:
        self.assertEqual(
            "9a5ee85cfb923834641db67b6d1e56cc8825ba70308ab1f101e26e4fb86ba3d6",
            canonical_digest(self.source),
        )

    def test_retained_repair_delta_is_one_exact_path(self) -> None:
        delta = self.result["repair_delta"]
        self.assertEqual(1, delta["changed_path_count"])
        self.assertEqual(
            [
                {
                    "status": "M",
                    "path": (
                        "skills/engineering-programme-coordinator/tests/"
                        "test_exact_candidate_evidence.py"
                    ),
                }
            ],
            delta["changes"],
        )

    def test_candidate_sha_change_invalidates_all_prior_evidence(self) -> None:
        invalidation = self.result["invalidation"]
        self.assertEqual("CANDIDATE_CHANGED", invalidation["reason"])
        self.assertEqual(3, invalidation["invalidated_count"])
        self.assertEqual(0, invalidation["carried_count"])
        self.assertEqual([], invalidation["carried_prior_evidence_ids"])
        self.assertEqual(
            sorted(row["evidence_id"] for row in self.source["prior_evidence"]),
            invalidation["invalidated_evidence_ids"],
        )

    def test_same_path_set_does_not_preserve_candidate_evidence(self) -> None:
        self.assertTrue(
            self.result["assertions"]["initial_final_changed_paths_equal"]
        )
        self.assertTrue(
            self.result["assertions"]["initial_final_obligation_ids_equal"]
        )
        self.assertTrue(
            self.result["assertions"]["initial_final_manifest_digest_differs"]
        )
        self.assertEqual(3, self.result["invalidation"]["invalidated_count"])

    def test_initial_and_final_l2_are_exact_candidate_bound(self) -> None:
        lineage = self.source["candidate_lineage"]
        self.assertEqual(
            lineage["initial_sha"],
            self.result["initial_l2"]["candidate_sha"],
        )
        self.assertEqual(
            lineage["final_sha"],
            self.result["final_l2"]["candidate_sha"],
        )
        self.assertNotEqual(
            self.result["initial_l2"]["manifest_digest"],
            self.result["final_l2"]["manifest_digest"],
        )

    def test_final_l2_has_eight_obligations(self) -> None:
        final_l2 = self.result["final_l2"]
        self.assertEqual(8, final_l2["changed_path_count"])
        self.assertEqual(8, len(final_l2["obligation_ids"]))

    def test_final_closed_denominator_is_fifteen_by_fifteen(self) -> None:
        ledger = self.result["final_ledger"]
        self.assertEqual(15, ledger["obligation_count"])
        self.assertEqual(15, ledger["requirement_count"])
        self.assertEqual(0, ledger["requirements_with_evidence"])
        self.assertEqual(15, ledger["requirements_without_evidence"])
        self.assertEqual(0, ledger["evidence_item_count"])

    def test_final_replay_carries_zero_prior_evidence(self) -> None:
        self.assertTrue(self.result["assertions"]["no_prior_evidence_carried"])
        self.assertEqual(
            0,
            self.result["final_ledger"]["evidence_item_count"],
        )
        self.assertEqual(
            [],
            self.result["invalidation"]["carried_prior_evidence_ids"],
        )

    def test_final_candidate_is_exact(self) -> None:
        self.assertTrue(self.result["assertions"]["final_candidate_exact"])
        self.assertEqual(
            self.source["candidate_lineage"]["final_sha"],
            self.result["candidate_lineage"]["final_sha"],
        )

    def test_repair_is_descendant_lineage(self) -> None:
        self.assertTrue(self.result["assertions"]["repair_descendant"])
        self.assertTrue(self.result["assertions"]["candidate_changed"])

    def test_duplicate_prior_evidence_ids_are_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["prior_evidence"].append(copy.deepcopy(source["prior_evidence"][0]))
        errors = validate_source(source)
        self.assertTrue(
            any("prior evidence ids must be globally unique" in e for e in errors),
            errors,
        )

    def test_mixed_candidate_prior_evidence_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["prior_evidence"][0]["candidate_sha"] = source["candidate_lineage"]["final_sha"]
        errors = validate_source(source)
        self.assertTrue(
            any("must equal initial_sha" in e for e in errors),
            errors,
        )

    def test_same_initial_and_final_candidate_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["candidate_lineage"]["final_sha"] = source["candidate_lineage"]["initial_sha"]
        errors = validate_source(source)
        self.assertTrue(any("must differ" in e for e in errors), errors)

    def test_reversed_repair_history_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["candidate_lineage"]["final_sha"] = source["candidate_lineage"]["base_sha"]
        with self.assertRaisesRegex(ValueError, "initial_sha must be an ancestor"):
            compile_source(source, REPO_ROOT)

    def test_wrong_repair_path_expectation_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["expected_transition"]["repair_changed_paths"] = ["wrong/path.py"]
        with self.assertRaisesRegex(ValueError, "repair changed paths"):
            compile_source(source, REPO_ROOT)

    def test_wrong_final_l2_count_expectation_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["expected_transition"]["final_l2_obligation_count"] = 7
        with self.assertRaisesRegex(ValueError, "final L2 obligation count"):
            compile_source(source, REPO_ROOT)

    def test_wrong_final_closed_denominator_expectation_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["expected_transition"]["final_closed_requirement_count"] = 14
        with self.assertRaisesRegex(ValueError, "final closed requirement count"):
            compile_source(source, REPO_ROOT)

    def test_template_digest_tamper_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["templates"]["l2_source"]["digest"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "canonical digest"):
            compile_source(source, REPO_ROOT)

    def test_expected_invalidated_count_must_equal_prior_evidence(self) -> None:
        source = copy.deepcopy(self.source)
        source["expected_transition"]["prior_evidence_invalidated"] = 2
        errors = validate_source(source)
        self.assertTrue(
            any("must equal prior evidence count" in e for e in errors),
            errors,
        )

    def test_generic_validator_requires_source_and_repo_basis(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            result_path = Path(td) / "repair-replay-result.yaml"
            result_path.write_text(
                yaml.safe_dump(self.result, sort_keys=False),
                encoding="utf-8",
            )

            unbound = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate.py"),
                    "repair-replay-result",
                    str(result_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, unbound.returncode)
            self.assertIn(
                "source-bound exact-object replay is required",
                unbound.stdout,
            )

            bound = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate.py"),
                    "repair-replay-result",
                    str(result_path),
                    "--repair-source",
                    str(SOURCE_PATH),
                    "--repo-root",
                    str(REPO_ROOT),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                0,
                bound.returncode,
                bound.stdout + bound.stderr,
            )

    def test_unbound_result_validation_fails_closed(self) -> None:
        errors = validate_result(self.result)
        self.assertTrue(
            any("source-bound exact-object replay is required" in e for e in errors),
            errors,
        )

    def test_recomputed_result_tamper_digest_does_not_bypass_replay(self) -> None:
        result = copy.deepcopy(self.result)
        result["final_ledger"]["requirements_without_evidence"] = 14
        result["result_digest"] = object_digest(result, "result_digest")
        errors = validate_result(result, self.source, REPO_ROOT)
        self.assertTrue(errors)

    def test_forged_final_candidate_cannot_self_certify(self) -> None:
        result = copy.deepcopy(self.result)
        result["candidate_lineage"]["final_sha"] = "a" * 40
        result["result_digest"] = object_digest(result, "result_digest")
        errors = validate_result(result, self.source, REPO_ROOT)
        self.assertTrue(errors)

    def test_result_schema_rejects_verdict_and_authority_fields(self) -> None:
        for field, value in [
            ("state", "VERIFIED"),
            ("verdict", "PASS"),
            ("pass", True),
            ("waiver", "accepted"),
            ("not_applicable", True),
            ("criticality", "CRITICAL"),
            ("gate", "ADVANCE_ELIGIBLE"),
            ("lifecycle", "ADVANCE"),
            ("merge_authority", True),
            ("production_mode", "DEFAULT_GATE"),
        ]:
            result = copy.deepcopy(self.result)
            result[field] = value
            result["result_digest"] = object_digest(result, "result_digest")
            self.assertTrue(validate_result_shape(result), field)

    def test_source_schema_rejects_verdict_and_authority_fields(self) -> None:
        for field, value in [
            ("state", "VERIFIED"),
            ("verdict", "PASS"),
            ("pass", True),
            ("waiver", "accepted"),
            ("criticality", "CRITICAL"),
            ("gate", "ADVANCE_ELIGIBLE"),
            ("merge_authority", True),
            ("production_mode", "DEFAULT_GATE"),
        ]:
            source = copy.deepcopy(self.source)
            source[field] = value
            self.assertTrue(validate_source(source), field)

    def test_authority_boundaries_are_replay_only(self) -> None:
        self.assertEqual(BOUNDARIES, self.result["authority_boundaries"])
        self.assertTrue(BOUNDARIES["performs_repair_invalidation"])
        self.assertTrue(BOUNDARIES["replays_final_candidate"])
        self.assertFalse(BOUNDARIES["assigns_evidence_verdict"])
        self.assertFalse(BOUNDARIES["applies_criticality_policy"])
        self.assertFalse(BOUNDARIES["performs_lifecycle_advance"])
        self.assertFalse(BOUNDARIES["grants_merge_authority"])
        self.assertFalse(BOUNDARIES["grants_production_cutover"])

    def test_extracts_precommitted_issue_source(self) -> None:
        markdown = (
            "# Child\n\n"
            "## Precommitted repair-replay source\n\n"
            "```yaml\n"
            + yaml.safe_dump(self.source, sort_keys=False)
            + "```\n"
        )
        self.assertEqual(self.source, extract_precommitted_source(markdown))

    def test_duplicate_precommitted_heading_is_rejected(self) -> None:
        block = (
            "## Precommitted repair-replay source\n"
            "```yaml\n{}\n```\n"
        )
        with self.assertRaises(ValueError):
            extract_precommitted_source(block + block)


if __name__ == "__main__":
    unittest.main()
