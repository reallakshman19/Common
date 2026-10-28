import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REFERENCES = ROOT / "references"
sys.path.insert(0, str(SCRIPTS))

from coordlib import load_yaml
from review_basis import active_common_protocol_digest, active_common_protocol_ref
from self_review_expectation_freeze import (
    AUTHORITY_BOUNDARIES,
    canonical_digest,
    compile_freeze,
    object_digest,
    review_planning_basis,
    review_planning_digest,
    validate_freeze,
    validate_freeze_shape,
)


L0_PATH = REFERENCES / "p2-s1-l0-manifest.yaml"
L1_PATH = REFERENCES / "p2-s2-l1-manifest.yaml"
L2_PATH = REFERENCES / "p2-s3-l2-manifest.yaml"


def profile(candidate_sha):
    return {
        "review_profile": {
            "common_protocol": {
                "ref": active_common_protocol_ref(),
                "version": "1.0",
                "digest": active_common_protocol_digest(),
            },
            "project_protocol": {
                "ref": "issue://578/project-acceptance",
                "digest": "a" * 64,
            },
            "role": "SELF_REVIEW",
            "author_principal": "agent://solo-1",
            "review_principal": "agent://solo-1",
            "principal_independence": "NONE",
            "context_reset": "FRESH_REVIEW_ATTEMPT",
            "common_criteria": {
                f"CR-{index:02d}": {
                    "applicability": "REQUIRED",
                    "result": "NOT_RUN",
                }
                for index in range(1, 11)
            },
            "project_method_ids": [
                "PROJECT-METHOD-1",
                "PROJECT-METHOD-NEGATIVE-CASE",
            ],
            "specialist_required": [],
            "final_candidate": candidate_sha,
        }
    }


def refresh_manifest_digest(value):
    payload = copy.deepcopy(value)
    payload.pop("manifest_digest", None)
    value["manifest_digest"] = canonical_digest(payload)


def refresh_freeze_digest(value):
    value["freeze_digest"] = object_digest(value, "freeze_digest")


def all_keys(value):
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            found.add(key)
            found.update(all_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.update(all_keys(item))
    return found


class SelfReviewExpectationFreezeTests(unittest.TestCase):
    def setUp(self):
        self.l0 = load_yaml(L0_PATH)
        self.l1 = load_yaml(L1_PATH)
        self.l2 = load_yaml(L2_PATH)
        self.profile = profile(self.l2["candidate"]["head_sha"])
        self.freeze = compile_freeze(
            "PRD-527-P3-SOLO-3",
            self.l0,
            self.l1,
            self.l2,
            self.profile,
        )

    def test_ecf01_clean_retained_manifests_compile_and_validate(self):
        self.assertEqual([], validate_freeze_shape(self.freeze))
        self.assertEqual(
            [],
            validate_freeze(
                self.freeze,
                self.l0,
                self.l1,
                self.l2,
                self.profile,
            ),
        )
        expected_count = (
            len(self.l0["obligations"])
            + len(self.l1["obligations"])
            + len(self.l2["obligations"])
        )
        self.assertEqual(expected_count, len(self.freeze["expectations"]))
        self.assertEqual(expected_count, len(self.freeze["challenges"]))

    def test_source_bound_replay_is_required(self):
        errors = validate_freeze(self.freeze)
        self.assertTrue(
            any("source-bound fresh replay is required" in error for error in errors),
            errors,
        )

    def test_ecf02_recomputed_freeze_claim_tamper_is_rejected(self):
        value = copy.deepcopy(self.freeze)
        value["expectations"][0]["claim"]["statement"] += " [tampered]"
        refresh_freeze_digest(value)
        self.assertEqual([], validate_freeze_shape(value))
        errors = validate_freeze(value, self.l0, self.l1, self.l2, self.profile)
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf03_recomputed_challenge_tamper_is_rejected(self):
        value = copy.deepcopy(self.freeze)
        value["challenges"][0]["plausible_green_but_wrong"] += " [tampered]"
        refresh_freeze_digest(value)
        self.assertEqual([], validate_freeze_shape(value))
        errors = validate_freeze(value, self.l0, self.l1, self.l2, self.profile)
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf04_recomputed_oracle_tamper_is_rejected(self):
        value = copy.deepcopy(self.freeze)
        value["challenges"][0]["oracle_refs"][0] += "/tampered"
        refresh_freeze_digest(value)
        self.assertEqual([], validate_freeze_shape(value))
        errors = validate_freeze(value, self.l0, self.l1, self.l2, self.profile)
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf05_l0_expectation_movement_stales_freeze(self):
        l0 = copy.deepcopy(self.l0)
        l0["obligations"][0]["expected_observation"] += " [changed]"
        refresh_manifest_digest(l0)
        errors = validate_freeze(self.freeze, l0, self.l1, self.l2, self.profile)
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf06_l1_expectation_movement_stales_freeze(self):
        l1 = copy.deepcopy(self.l1)
        l1["obligations"][0]["expected_observation"] += " [changed]"
        refresh_manifest_digest(l1)
        errors = validate_freeze(self.freeze, self.l0, l1, self.l2, self.profile)
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf07_l2_impact_expectation_movement_stales_freeze(self):
        l2 = copy.deepcopy(self.l2)
        l2["obligations"][0]["expected_observation"] += " [changed]"
        refresh_manifest_digest(l2)
        errors = validate_freeze(self.freeze, self.l0, self.l1, l2, self.profile)
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_l2_candidate_must_equal_profile_final_candidate(self):
        value = copy.deepcopy(self.profile)
        value["review_profile"]["final_candidate"] = "e" * 40
        with self.assertRaisesRegex(
            ValueError,
            "final_candidate must equal L2 exact candidate head",
        ):
            compile_freeze(
                "PRD-527-P3-SOLO-3",
                self.l0,
                self.l1,
                self.l2,
                value,
            )

    def test_ecf08_review_applicability_movement_stales_freeze(self):
        value = copy.deepcopy(self.profile)
        value["review_profile"]["common_criteria"]["CR-06"] = {
            "applicability": "NOT_APPLICABLE",
            "applicability_basis": "project://no-interface-change",
            "result": "NOT_APPLICABLE",
        }
        errors = validate_freeze(
            self.freeze,
            self.l0,
            self.l1,
            self.l2,
            value,
        )
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf08_project_method_movement_stales_freeze(self):
        value = copy.deepcopy(self.profile)
        value["review_profile"]["project_method_ids"].append("PROJECT-METHOD-EXTRA")
        errors = validate_freeze(
            self.freeze,
            self.l0,
            self.l1,
            self.l2,
            value,
        )
        self.assertTrue(
            any("stored freeze does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_ecf09_evidence_and_result_changes_do_not_rewrite_planning_basis(self):
        before = review_planning_basis(self.profile)
        before_digest = review_planning_digest(self.profile)

        value = copy.deepcopy(self.profile)
        value["review_profile"]["common_criteria"]["CR-03"] = {
            "applicability": "REQUIRED",
            "result": "PASS",
            "evidence_refs": ["evidence://later-runtime"],
        }
        value["review_profile"]["findings"] = [
            {
                "id": "ADV-1",
                "class": "ADVISORY",
                "summary": "Later evidence-only review note.",
                "disposition": "ACCEPTED_ADVISORY",
            }
        ]
        after = review_planning_basis(value)
        after_digest = review_planning_digest(value)

        self.assertEqual(before, after)
        self.assertEqual(before_digest, after_digest)
        self.assertEqual(
            [],
            validate_freeze(
                self.freeze,
                self.l0,
                self.l1,
                self.l2,
                value,
            ),
        )

    def test_ecf10_non_self_review_profile_is_rejected(self):
        value = copy.deepcopy(self.profile)
        value["review_profile"]["role"] = "REVIEWER"
        value["review_profile"]["principal_independence"] = "DEGRADED"
        with self.assertRaisesRegex(
            ValueError,
            "requires SELF_REVIEW profile",
        ):
            compile_freeze(
                "PRD-527-P3-SOLO-3",
                self.l0,
                self.l1,
                self.l2,
                value,
            )

    def test_ecf11_duplicate_obligation_id_across_layers_is_rejected(self):
        l1 = copy.deepcopy(self.l1)
        l1["obligations"][0]["id"] = self.l0["obligations"][0]["id"]
        refresh_manifest_digest(l1)
        with self.assertRaisesRegex(
            ValueError,
            "duplicate obligation id across freeze layers",
        ):
            compile_freeze(
                "PRD-527-P3-SOLO-3",
                self.l0,
                l1,
                self.l2,
                self.profile,
            )

    def test_ecf12_freeze_has_no_acceptance_or_lifecycle_result_fields(self):
        self.assertEqual(AUTHORITY_BOUNDARIES, self.freeze["authority_boundaries"])
        self.assertTrue(self.freeze["authority_boundaries"]["consumes_candidate_diff_via_l2"])
        for key, value in self.freeze["authority_boundaries"].items():
            if key != "consumes_candidate_diff_via_l2":
                self.assertFalse(value, key)

        forbidden = {
            "result",
            "evidence_refs",
            "findings",
            "engineering_pass",
            "lifecycle_advance",
            "merge_authority",
            "production_cutover",
            "verdict",
        }
        self.assertEqual(set(), forbidden & all_keys(self.freeze))

    def test_layer_order_is_l0_then_l1_then_l2_and_l2_supplements(self):
        layers = [row["layer"] for row in self.freeze["expectations"]]
        first_l1 = layers.index("L1")
        first_l2 = layers.index("L2")
        self.assertTrue(all(layer == "L0" for layer in layers[:first_l1]))
        self.assertTrue(all(layer == "L1" for layer in layers[first_l1:first_l2]))
        self.assertTrue(all(layer == "L2" for layer in layers[first_l2:]))

    def test_source_manifest_digests_are_bound_exactly(self):
        self.assertEqual(
            self.l0["manifest_digest"],
            self.freeze["source_manifests"]["l0"]["manifest_digest"],
        )
        self.assertEqual(
            self.l1["manifest_digest"],
            self.freeze["source_manifests"]["l1"]["manifest_digest"],
        )
        self.assertEqual(
            self.l2["manifest_digest"],
            self.freeze["source_manifests"]["l2"]["manifest_digest"],
        )


if __name__ == "__main__":
    unittest.main()
