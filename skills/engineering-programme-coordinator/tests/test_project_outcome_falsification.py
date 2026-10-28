import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REFERENCES = ROOT / "references"
SKILLS = ROOT.parent
LOCAL_EXAMPLE = (
    SKILLS
    / "Local_PR_Deliverty_v1.1"
    / "examples"
    / "example-complete.json"
)
sys.path.insert(0, str(SCRIPTS))

from coordlib import load_yaml
from project_outcome_falsification import (
    AUTHORITY_BOUNDARIES,
    canonical_digest,
    compile_result,
    object_digest,
    project_protocol_digest,
    validate_project_protocol,
    validate_result,
    validate_result_shape,
)
from review_basis import active_common_protocol_digest, active_common_protocol_ref
from self_review_expectation_freeze import compile_freeze, object_digest as freeze_object_digest


L0_PATH = REFERENCES / "p2-s1-l0-manifest.yaml"
L1_PATH = REFERENCES / "p2-s2-l1-manifest.yaml"
L2_PATH = REFERENCES / "p2-s3-l2-manifest.yaml"


def profile(candidate_sha, protocol, method_ids=None):
    if method_ids is None:
        method_ids = ["VM-A1-SUPER", "VM-P1-PARENT"]
    return {
        "review_profile": {
            "common_protocol": {
                "ref": active_common_protocol_ref(),
                "version": "1.0",
                "digest": active_common_protocol_digest(),
            },
            "project_protocol": {
                "ref": protocol["source_ref"],
                "digest": protocol["digest"],
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
            "project_method_ids": list(method_ids),
            "specialist_required": [],
            "final_candidate": candidate_sha,
        }
    }


def observations(candidate_sha, methods, result="PASS"):
    rows = []
    for method_id in methods:
        rows.append(
            {
                "method_id": method_id,
                "candidate_sha": candidate_sha,
                "result": result,
                "evidence_origin": "SAME_PRINCIPAL_EXECUTION",
                "evidence_refs": [f"evidence://{method_id}"] if result != "NOT_RUN" else [],
                "procedure": f"Execute pinned project method {method_id} against exact candidate.",
                "limitation": "Method could not be executed." if result == "NOT_RUN" else None,
            }
        )
    return rows


def refresh_protocol_digest(protocol):
    protocol["digest"] = project_protocol_digest(protocol)


def refresh_freeze_digest(value):
    value["freeze_digest"] = freeze_object_digest(value, "freeze_digest")


def refresh_result_digest(value):
    value["result_digest"] = object_digest(value, "result_digest")


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


class ProjectOutcomeFalsificationTests(unittest.TestCase):
    def setUp(self):
        self.l0 = load_yaml(L0_PATH)
        self.l1 = load_yaml(L1_PATH)
        self.l2 = load_yaml(L2_PATH)
        bundle = json.loads(LOCAL_EXAMPLE.read_text(encoding="utf-8"))
        self.protocol = copy.deepcopy(bundle["support"]["project_protocols"][0])
        self.assertEqual([], validate_project_protocol(self.protocol))
        self.profile = profile(self.l2["candidate"]["head_sha"], self.protocol)
        self.freeze = compile_freeze(
            "PRD-527-P3-SOLO-4",
            self.l0,
            self.l1,
            self.l2,
            self.profile,
        )
        self.methods = sorted(self.profile["review_profile"]["project_method_ids"])
        self.observations = observations(
            self.freeze["identity"]["candidate_sha"],
            self.methods,
        )
        self.result = compile_result(
            "PRD-527-P3-SOLO-4",
            self.freeze,
            self.l0,
            self.l1,
            self.l2,
            self.profile,
            self.protocol,
            self.observations,
        )

    def compile_with(self, obs=None, profile_value=None, protocol=None, freeze=None):
        return compile_result(
            "PRD-527-P3-SOLO-4",
            freeze if freeze is not None else self.freeze,
            self.l0,
            self.l1,
            self.l2,
            profile_value if profile_value is not None else self.profile,
            protocol if protocol is not None else self.protocol,
            obs if obs is not None else self.observations,
        )

    def test_pof01_all_methods_pass_means_not_falsified_not_pass(self):
        self.assertEqual("NOT_FALSIFIED", self.result["falsification_status"])
        self.assertNotEqual("PASS", self.result["falsification_status"])
        self.assertEqual([], validate_result_shape(self.result))
        self.assertEqual(
            [],
            validate_result(
                self.result,
                "PRD-527-P3-SOLO-4",
                self.freeze,
                self.l0,
                self.l1,
                self.l2,
                self.profile,
                self.protocol,
                self.observations,
            ),
        )

    def test_source_bound_fresh_replay_is_required(self):
        errors = validate_result(self.result)
        self.assertTrue(
            any("source-bound fresh replay is required" in error for error in errors),
            errors,
        )

    def test_pof02_any_fail_falsifies_project_outcome(self):
        obs = copy.deepcopy(self.observations)
        obs[0]["result"] = "FAIL"
        value = self.compile_with(obs=obs)
        self.assertEqual("FALSIFIED", value["falsification_status"])

    def test_pof03_inconclusive_precedes_not_run_when_no_fail(self):
        obs = copy.deepcopy(self.observations)
        obs[0]["result"] = "INCONCLUSIVE"
        obs[1]["result"] = "NOT_RUN"
        obs[1]["evidence_refs"] = []
        obs[1]["limitation"] = "External project oracle unavailable."
        value = self.compile_with(obs=obs)
        self.assertEqual("INCONCLUSIVE", value["falsification_status"])

    def test_pof04_not_run_remains_not_run(self):
        obs = copy.deepcopy(self.observations)
        obs[0]["result"] = "NOT_RUN"
        obs[0]["evidence_refs"] = []
        obs[0]["limitation"] = "Required protected harness unavailable."
        value = self.compile_with(obs=obs)
        self.assertEqual("NOT_RUN", value["falsification_status"])

    def test_not_run_without_limitation_is_rejected(self):
        obs = copy.deepcopy(self.observations)
        obs[0]["result"] = "NOT_RUN"
        obs[0]["evidence_refs"] = []
        obs[0]["limitation"] = None
        with self.assertRaisesRegex(ValueError, "NOT_RUN requires a concrete limitation"):
            self.compile_with(obs=obs)

    def test_pof05_wrong_candidate_observation_is_rejected(self):
        obs = copy.deepcopy(self.observations)
        obs[0]["candidate_sha"] = "e" * 40
        with self.assertRaisesRegex(
            ValueError,
            "candidate_sha must equal exact freeze candidate",
        ):
            self.compile_with(obs=obs)

    def test_pof06_project_protocol_ref_mismatch_is_rejected(self):
        value = copy.deepcopy(self.profile)
        value["review_profile"]["project_protocol"]["ref"] = "wrong://project-protocol"
        freeze = compile_freeze(
            "PRD-527-P3-SOLO-4",
            self.l0,
            self.l1,
            self.l2,
            value,
        )
        with self.assertRaisesRegex(
            ValueError,
            "project_protocol.ref must equal supplied Local project protocol source_ref",
        ):
            self.compile_with(profile_value=value, freeze=freeze)

    def test_pof06_project_protocol_digest_mismatch_is_rejected(self):
        value = copy.deepcopy(self.profile)
        value["review_profile"]["project_protocol"]["digest"] = "e" * 64
        freeze = compile_freeze(
            "PRD-527-P3-SOLO-4",
            self.l0,
            self.l1,
            self.l2,
            value,
        )
        with self.assertRaisesRegex(
            ValueError,
            "project_protocol.digest must equal supplied Local project protocol digest",
        ):
            self.compile_with(profile_value=value, freeze=freeze)

    def test_pof07_forged_project_protocol_digest_is_rejected(self):
        protocol = copy.deepcopy(self.protocol)
        protocol["version"] = protocol["version"] + "-tampered"
        errors = validate_project_protocol(protocol)
        self.assertTrue(
            any("digest does not match canonical visible content" in error for error in errors),
            errors,
        )

    def test_pof08_protected_surface_manifest_tamper_is_rejected(self):
        protocol = copy.deepcopy(self.protocol)
        protocol["protected_surface"]["manifest"][0]["ref"] += "/tampered"
        refresh_protocol_digest(protocol)
        errors = validate_project_protocol(protocol)
        self.assertTrue(
            any("protected-surface manifest_digest" in error for error in errors),
            errors,
        )

    def test_pof09_missing_selected_project_method_is_rejected(self):
        value = profile(
            self.l2["candidate"]["head_sha"],
            self.protocol,
            ["VM-A1-SUPER", "VM-NOT-THERE"],
        )
        freeze = compile_freeze(
            "PRD-527-P3-SOLO-4",
            self.l0,
            self.l1,
            self.l2,
            value,
        )
        obs = observations(
            freeze["identity"]["candidate_sha"],
            sorted(value["review_profile"]["project_method_ids"]),
        )
        with self.assertRaisesRegex(
            ValueError,
            "must resolve exactly once",
        ):
            self.compile_with(obs=obs, profile_value=value, freeze=freeze)

    def test_empty_project_method_set_is_rejected_for_falsification_pass(self):
        value = profile(
            self.l2["candidate"]["head_sha"],
            self.protocol,
            [],
        )
        freeze = compile_freeze(
            "PRD-527-P3-SOLO-4",
            self.l0,
            self.l1,
            self.l2,
            value,
        )
        with self.assertRaisesRegex(
            ValueError,
            "requires at least one project_method_id",
        ):
            self.compile_with(obs=[], profile_value=value, freeze=freeze)

    def test_pof10_missing_method_observation_is_rejected(self):
        obs = copy.deepcopy(self.observations[:-1])
        with self.assertRaisesRegex(ValueError, "missing selected method observations"):
            self.compile_with(obs=obs)

    def test_pof10_duplicate_method_observation_is_rejected(self):
        obs = copy.deepcopy(self.observations)
        obs.append(copy.deepcopy(obs[0]))
        with self.assertRaisesRegex(ValueError, "method observations must be unique"):
            self.compile_with(obs=obs)

    def test_pof10_extra_method_observation_is_rejected(self):
        obs = copy.deepcopy(self.observations)
        extra = copy.deepcopy(obs[0])
        extra["method_id"] = "VM-A1-AUTHOR"
        obs.append(extra)
        with self.assertRaisesRegex(ValueError, "unexpected method observations"):
            self.compile_with(obs=obs)

    def test_pof11_recomputed_tampered_expectation_freeze_is_rejected(self):
        freeze = copy.deepcopy(self.freeze)
        freeze["expectations"][0]["expected_observation"] += " [tampered]"
        refresh_freeze_digest(freeze)
        with self.assertRaisesRegex(ValueError, "stored freeze does not equal fresh source replay"):
            self.compile_with(freeze=freeze)

    def test_pof12_recomputed_result_tamper_is_rejected_by_fresh_replay(self):
        value = copy.deepcopy(self.result)
        value["method_plan"][0]["material_inputs"].append("TAMPERED")
        value["method_plan"][0]["material_inputs"].sort()
        refresh_result_digest(value)
        self.assertEqual([], validate_result_shape(value))
        errors = validate_result(
            value,
            "PRD-527-P3-SOLO-4",
            self.freeze,
            self.l0,
            self.l1,
            self.l2,
            self.profile,
            self.protocol,
            self.observations,
        )
        self.assertTrue(
            any("stored result does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_pof13_same_principal_truth_and_independent_label_impossible(self):
        self.assertEqual("SELF_REVIEW", self.result["review_mode"])
        self.assertEqual("NONE", self.result["principal_independence"])
        obs = copy.deepcopy(self.observations)
        obs[0]["evidence_origin"] = "SUPER_REVIEW_INDEPENDENT"
        with self.assertRaisesRegex(ValueError, "is not one of"):
            self.compile_with(obs=obs)

    def test_pof14_no_engineering_or_lifecycle_authority(self):
        self.assertEqual(AUTHORITY_BOUNDARIES, self.result["authority_boundaries"])
        self.assertTrue(
            self.result["authority_boundaries"]["consumes_expectation_challenge_freeze"]
        )
        self.assertTrue(self.result["authority_boundaries"]["consumes_project_protocol"])
        self.assertTrue(
            self.result["authority_boundaries"][
                "consumes_same_principal_method_observations"
            ]
        )
        for key, value in self.result["authority_boundaries"].items():
            if key.startswith("consumes_"):
                continue
            self.assertFalse(value, key)

        forbidden = {
            "engineering_pass",
            "project_acceptance_pass",
            "evidence_gate_decision",
            "lifecycle_advance",
            "merge_authority",
            "production_cutover",
            "ADVANCE_ELIGIBLE",
        }
        self.assertEqual(set(), forbidden & all_keys(self.result))

    def test_method_plan_retains_project_harness_and_criterion_relationships(self):
        plan = {row["method_id"]: row for row in self.result["method_plan"]}
        self.assertEqual(["A1"], plan["VM-A1-SUPER"]["criterion_ids"])
        self.assertEqual("SR-ALL", plan["VM-A1-SUPER"]["harness_id"])
        self.assertTrue(plan["VM-A1-SUPER"]["harness_manifest_refs"])
        self.assertEqual(["P1"], plan["VM-P1-PARENT"]["criterion_ids"])


if __name__ == "__main__":
    unittest.main()
