import copy
import importlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
LOCAL_ROOT = SKILLS / "Local_PR_Deliverty_v1.1"
LOCAL_TESTS = LOCAL_ROOT / "tests"
COORDINATOR_SCRIPTS = ROOT / "scripts"
VALIDATION_NOW = "2026-10-04T00:08:00Z"
COLLIDING_LOCAL_MODULES = (
    "validate",
    "pipeline",
    "acceptance_basis",
    "responsibility",
    "role_transition",
)
_MISSING_MODULE = object()

SPEC = importlib.util.spec_from_file_location("local_v11_integrated", ROOT / "scripts" / "local_v11_integrated.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)

NATIVE_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "local_v11_native_fixture",
    LOCAL_TESTS / "test_492_native_validation.py",
)
native_fixture = importlib.util.module_from_spec(NATIVE_FIXTURE_SPEC)
assert NATIVE_FIXTURE_SPEC.loader is not None
NATIVE_FIXTURE_SPEC.loader.exec_module(native_fixture)

SHA = "a" * 40
DIGEST = "b" * 64
LOCAL_REF = f"reallaksh19/Common@{SHA}:skills/Local_PR_Deliverty_v1.1"
V35_REF = f"reallaksh19/Common@{SHA}:skills/engineering-pr-delivery-v3.5"


def native_task():
    return {
        "kind": "RESPONSIBILITY",
        "task_id": "PRD-492-A",
        "issue": 91,
        "pr": 112,
        "representation": {
            "kind": "SINGLE_ISSUE",
            "primary_issue": 91,
            "member_issues": [91],
            "predecessor_attempt_refs": [],
            "delivery_pr_history": [112],
        },
        "acceptance_epoch_id": "AE-002",
        "acceptance_profile_ref": "APR-PRD-492-A-AE002",
        "acceptance_profile_digest": DIGEST,
    }


def parent_task(release="READY"):
    return {
        "kind": "PARENT",
        "task_id": "PARENT-492",
        "control_plane": {
            "bootstrap_state": "ESTABLISHED",
            "current_acceptance_epoch_id": "AE-002",
            "acceptance_basis_registry": [],
            "responsibility_registry": [{
                "task_id": "PRD-492-A",
                "release_state": release,
                "acceptance_profile_ref": "APR-PRD-492-A-AE002",
                "acceptance_profile_digest": DIGEST,
            }],
            "authority_grant_refs": [],
        },
    }


def v35_result(local_complete=False, coder_complete=True):
    return {
        "result_scope": "CODER_ENGINEERING_EXECUTION",
        "engineering_responsibility": "ENG-PRD-492-A-CODER",
        "engineering_responsibility_complete": coder_complete,
        "local_responsibility_task_id": "PRD-492-A",
        "local_responsibility_complete": local_complete,
        "acceptance_epoch_ref": "AE-002",
        "acceptance_profile_ref": "APR-PRD-492-A-AE002",
        "acceptance_profile_digest": DIGEST,
    }


def v35_result_for(task, *, local_complete=False, coder_complete=True):
    return {
        "result_scope": "CODER_ENGINEERING_EXECUTION",
        "engineering_responsibility": f"ENG-{task['task_id']}-CODER",
        "engineering_responsibility_complete": coder_complete,
        "local_responsibility_task_id": task["task_id"],
        "local_responsibility_complete": local_complete,
        "acceptance_epoch_ref": task["acceptance_epoch_id"],
        "acceptance_profile_ref": task["acceptance_profile_ref"],
        "acceptance_profile_digest": task["acceptance_profile_digest"],
    }


def observed(release="READY", result=None):
    return module.observe_responsibility(parent_task(release), native_task(), result)


def integrated_context(release="READY", result=None):
    parent = parent_task(release)
    return module.build_integrated_context(
        parent_task=parent,
        local_protocol_ref=LOCAL_REF,
        local_protocol_digest=DIGEST,
        engineering_evidence_provider_ref=V35_REF,
        engineering_evidence_provider_digest=DIGEST,
        responsibility_inputs=[{
            "responsibility_task": native_task(),
            "v35_result": result,
        }],
    )


def validated_native_inputs(*, complete=True):
    bundle = native_fixture.make_native_bundle(complete=complete)
    parent = next(task for task in bundle["tasks"] if task["kind"] == "PARENT")
    responsibility = next(task for task in bundle["tasks"] if task["kind"] == "RESPONSIBILITY")
    return bundle, parent, responsibility


def delivery_result(bundle, task_id):
    return next(
        result
        for result in bundle["results"]
        if result.get("record") == "DELIVERY_RESULT" and result.get("task_id") == task_id
    )


def ed01_synthetic_pseudo_local_task():
    """Retained ED-01 anti-golden: the former coordinator-owned pseudo Local TASK."""
    return {
        "kind": "RESPONSIBILITY",
        "task_id": "PRD-492-A",
        "acceptance_epoch_ref": "AE-002",
        "acceptance_profile_ref": "APR-PRD-492-A-AE002",
        "acceptance_profile_digest": DIGEST,
        "release_state": "READY",
        "responsibility_complete": False,
        "representation": {
            "kind": "SINGLE_ISSUE",
            "primary_issue": 91,
            "member_issues": [91],
            "predecessor_attempt_refs": [],
            "delivery_pr_history": [112],
        },
    }


def ed01_canonical_native_fixture():
    """Retained ED-01 golden: real Local native Parent + RESPONSIBILITY records."""
    return validated_native_inputs(complete=False)


def save_collision_state():
    return (
        list(sys.path),
        {name: sys.modules.get(name, _MISSING_MODULE) for name in COLLIDING_LOCAL_MODULES},
    )


def restore_collision_state(path_state, module_state):
    sys.path[:] = path_state
    for name, previous in module_state.items():
        sys.modules.pop(name, None)
        if previous is not _MISSING_MODULE:
            sys.modules[name] = previous


def clear_colliding_modules():
    for name in COLLIDING_LOCAL_MODULES:
        sys.modules.pop(name, None)


def remove_local_import_paths():
    local_paths = {str(LOCAL_ROOT / "scripts"), str(LOCAL_TESTS)}
    sys.path[:] = [entry for entry in sys.path if entry not in local_paths]


def import_coordinator_validate():
    original_path = list(sys.path)
    try:
        scripts = str(COORDINATOR_SCRIPTS)
        sys.path[:] = [scripts, *[entry for entry in original_path if entry != scripts]]
        return importlib.import_module("validate")
    finally:
        sys.path[:] = original_path


class LocalV11IntegratedTests(unittest.TestCase):
    def test_canonical_parent_responsibility_fixture_is_consumed(self):
        row = observed(result=v35_result())
        self.assertEqual(row["task_id"], "PRD-492-A")
        self.assertEqual(row["acceptance_epoch_id"], "AE-002")
        self.assertNotIn("acceptance_epoch_ref", row)
        self.assertFalse(row["local_responsibility_complete"])
        self.assertNotIn("local_completion_status", row)

    def test_all_canonical_release_states_are_preserved(self):
        for release in sorted(module.CANONICAL_RELEASE_STATES):
            with self.subTest(release=release):
                row = observed(release)
                self.assertEqual(row["release_state"], release)
                self.assertFalse(row["local_responsibility_complete"])
                self.assertFalse(row["coder_engineering_complete"])

    def test_ED_01_anti_golden_synthetic_pseudo_local_task_is_rejected(self):
        pseudo = ed01_synthetic_pseudo_local_task()
        self.assertEqual(pseudo["acceptance_epoch_ref"], "AE-002")
        self.assertEqual(pseudo["release_state"], "READY")
        self.assertFalse(pseudo["responsibility_complete"])
        self.assertNotIn("acceptance_epoch_id", pseudo)
        with self.assertRaisesRegex(module.IntegratedModeError, "acceptance_epoch_id|synthetic observation field"):
            module.observe_responsibility(parent_task(), pseudo)

    def test_ED_01_golden_real_native_parent_responsibility_is_accepted(self):
        bundle, parent, task = ed01_canonical_native_fixture()
        self.assertEqual(task["kind"], "RESPONSIBILITY")
        self.assertIn("acceptance_epoch_id", task)
        self.assertNotIn("acceptance_epoch_ref", task)
        self.assertNotIn("release_state", task)
        self.assertNotIn("responsibility_complete", task)
        row = module.observe_responsibility(
            parent,
            task,
            local_bundle=bundle,
            local_validation_now=VALIDATION_NOW,
        )
        self.assertEqual(row["task_id"], task["task_id"])
        self.assertEqual(row["release_state"], "READY")
        self.assertEqual(row["acceptance_epoch_id"], task["acceptance_epoch_id"])
        self.assertFalse(row["local_responsibility_complete"])
        self.assertFalse(row["coder_engineering_complete"])

    def test_projected_dict_cannot_assert_local_provenance(self):
        fake_projection = {
            "task_id": "PRD-FAKE",
            "release_state": "READY",
            "acceptance_epoch_id": "AE-FAKE",
            "acceptance_profile_ref": "APR-FAKE",
            "acceptance_profile_digest": DIGEST,
            "local_responsibility_complete": False,
        }
        with self.assertRaisesRegex(module.IntegratedModeError, "Parent TASK control_plane"):
            module.observe_responsibility(fake_projection, native_task())

    def test_complete_is_not_a_canonical_release_state(self):
        with self.assertRaisesRegex(module.IntegratedModeError, "non-canonical"):
            module.observe_responsibility(parent_task("COMPLETE"), native_task())

    def test_no_validated_local_bundle_means_local_incomplete_even_when_coder_complete(self):
        row = observed(result=v35_result(False, True))
        self.assertTrue(row["coder_engineering_complete"])
        self.assertFalse(row["local_responsibility_complete"])

    def test_v35_cannot_claim_local_completion(self):
        with self.assertRaisesRegex(module.IntegratedModeError, "illegally claims"):
            observed(result=v35_result(True, True))

    def test_non_coder_scoped_v35_result_is_rejected(self):
        result = v35_result()
        result["result_scope"] = "LOCAL_COMPLETION"
        with self.assertRaisesRegex(module.IntegratedModeError, "Coder-scoped"):
            observed(result=result)

    def test_non_boolean_v35_coder_completion_is_rejected(self):
        result = v35_result()
        result["engineering_responsibility_complete"] = "true"
        with self.assertRaisesRegex(module.IntegratedModeError, "must be boolean"):
            observed(result=result)

    def test_stale_acceptance_epoch_is_rejected_CH_R1_08(self):
        result = v35_result()
        result["acceptance_epoch_ref"] = "AE-STALE"
        with self.assertRaisesRegex(module.IntegratedModeError, "acceptance epoch is stale"):
            observed(result=result)

    def test_empty_acceptance_epoch_id_is_rejected(self):
        task = native_task()
        task["acceptance_epoch_id"] = ""
        with self.assertRaisesRegex(module.IntegratedModeError, "lacks acceptance_epoch_id"):
            module.observe_responsibility(parent_task(), task)

    def test_stale_acceptance_profile_ref_is_rejected(self):
        result = v35_result()
        result["acceptance_profile_ref"] = "APR-STALE"
        with self.assertRaisesRegex(module.IntegratedModeError, "acceptance profile is stale"):
            observed(result=result)

    def test_stale_acceptance_profile_is_rejected(self):
        result = v35_result()
        result["acceptance_profile_digest"] = "c" * 64
        with self.assertRaisesRegex(module.IntegratedModeError, "profile digest is stale"):
            observed(result=result)

    def test_mismatched_v35_nested_identity_is_rejected(self):
        result = v35_result()
        result["engineering_responsibility"] = "ENG-PRD-OTHER-CODER"
        with self.assertRaisesRegex(module.IntegratedModeError, "nested responsibility"):
            observed(result=result)

    def test_mismatched_v35_local_task_id_is_rejected(self):
        result = v35_result()
        result["local_responsibility_task_id"] = "PRD-OTHER"
        with self.assertRaisesRegex(module.IntegratedModeError, "another Local responsibility"):
            observed(result=result)

    def test_G_R1_LOCAL_COMPLETE_uses_real_schema_valid_delivery_result(self):
        bundle, parent, task = validated_native_inputs()
        result = delivery_result(bundle, task["task_id"])
        schema = json.loads((LOCAL_ROOT / "schemas" / "delivery-result.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(len(schema["required"]), 21)
        self.assertTrue(set(schema["required"]) <= set(result))
        row = module.observe_responsibility(
            parent,
            task,
            v35_result_for(task, coder_complete=True),
            local_bundle=bundle,
            local_validation_now=VALIDATION_NOW,
        )
        self.assertTrue(row["local_responsibility_complete"])
        self.assertTrue(row["coder_engineering_complete"])

    def test_valid_v35_completion_changes_only_coder_completion(self):
        bundle, parent, task = validated_native_inputs()
        row_without_coder = module.observe_responsibility(
            parent,
            task,
            v35_result_for(task, coder_complete=False),
            local_bundle=bundle,
            local_validation_now=VALIDATION_NOW,
        )
        row_with_coder = module.observe_responsibility(
            parent,
            task,
            v35_result_for(task, coder_complete=True),
            local_bundle=bundle,
            local_validation_now=VALIDATION_NOW,
        )
        self.assertTrue(row_without_coder["local_responsibility_complete"])
        self.assertTrue(row_with_coder["local_responsibility_complete"])
        self.assertFalse(row_without_coder["coder_engineering_complete"])
        self.assertTrue(row_with_coder["coder_engineering_complete"])

    def test_schema_shaped_but_forged_delivery_result_is_rejected_by_Local_validation(self):
        bundle, parent, task = validated_native_inputs()
        forged = delivery_result(bundle, task["task_id"])
        forged["head_sha"] = "f" * 40
        with self.assertRaisesRegex(module.IntegratedModeError, "Local native validation rejected bundle"):
            module.observe_responsibility(
                parent,
                task,
                local_bundle=bundle,
                local_validation_now=VALIDATION_NOW,
            )

    def test_schema_invalid_delivery_result_is_rejected_by_Local_validation(self):
        bundle, parent, task = validated_native_inputs()
        delivery_result(bundle, task["task_id"]).pop("canonical_observation")
        with self.assertRaisesRegex(module.IntegratedModeError, "Local native validation rejected bundle"):
            module.observe_responsibility(
                parent,
                task,
                local_bundle=bundle,
                local_validation_now=VALIDATION_NOW,
            )

    def test_wrong_delivery_result_task_id_is_rejected_by_Local_validation(self):
        bundle, parent, task = validated_native_inputs()
        delivery_result(bundle, task["task_id"])["task_id"] = "PRD-WRONG"
        with self.assertRaisesRegex(module.IntegratedModeError, "Local native validation rejected bundle"):
            module.observe_responsibility(
                parent,
                task,
                local_bundle=bundle,
                local_validation_now=VALIDATION_NOW,
            )

    def test_reduced_delivery_result_cannot_bypass_Local_validation(self):
        bundle, parent, task = validated_native_inputs()
        bundle["results"] = [{
            "record": "DELIVERY_RESULT",
            "task_id": task["task_id"],
            "responsibility_complete": True,
        }]
        with self.assertRaisesRegex(module.IntegratedModeError, "Local native validation rejected bundle"):
            module.observe_responsibility(
                parent,
                task,
                local_bundle=bundle,
                local_validation_now=VALIDATION_NOW,
            )

    def test_caller_validation_flag_does_not_exist(self):
        with self.assertRaises(TypeError):
            module.observe_responsibility(
                parent_task(),
                native_task(),
                validated_delivery_result={"responsibility_complete": True},
            )

    def test_local_bundle_requires_explicit_validation_time(self):
        bundle, parent, task = validated_native_inputs()
        with self.assertRaisesRegex(module.IntegratedModeError, "explicit validation time"):
            module.observe_responsibility(parent, task, local_bundle=bundle)

    def test_validation_time_without_bundle_is_rejected(self):
        with self.assertRaisesRegex(module.IntegratedModeError, "requires a Local validation bundle"):
            module.observe_responsibility(
                parent_task(),
                native_task(),
                local_validation_now=VALIDATION_NOW,
            )

    def test_validated_bundle_parent_must_equal_observed_parent(self):
        bundle, parent, task = validated_native_inputs()
        observed_parent = copy.deepcopy(parent)
        observed_parent["owner_principals"] = list(observed_parent["owner_principals"]) + ["DIFFERENT-OWNER"]
        with self.assertRaisesRegex(module.IntegratedModeError, "Parent differs from observed Parent"):
            module.observe_responsibility(
                observed_parent,
                task,
                local_bundle=bundle,
                local_validation_now=VALIDATION_NOW,
            )

    def test_validated_bundle_responsibility_must_equal_observed_responsibility(self):
        bundle, parent, task = validated_native_inputs()
        observed_task = copy.deepcopy(task)
        observed_task["issue"] = observed_task["issue"] + 1000
        with self.assertRaisesRegex(module.IntegratedModeError, "RESPONSIBILITY differs from observed RESPONSIBILITY"):
            module.observe_responsibility(
                parent,
                observed_task,
                local_bundle=bundle,
                local_validation_now=VALIDATION_NOW,
            )

    def test_valid_in_progress_bundle_without_delivery_result_stays_incomplete(self):
        bundle, parent, task = validated_native_inputs(complete=False)
        self.assertFalse(any(result.get("record") == "DELIVERY_RESULT" for result in bundle["results"]))
        row = module.observe_responsibility(
            parent,
            task,
            v35_result_for(task, coder_complete=True),
            local_bundle=bundle,
            local_validation_now=VALIDATION_NOW,
        )
        self.assertTrue(row["coder_engineering_complete"])
        self.assertFalse(row["local_responsibility_complete"])

    def test_F1_coordinator_validate_imported_first_does_not_poison_Local_validator(self):
        path_state, module_state = save_collision_state()
        module._load_local_native_validator_module.cache_clear()
        try:
            remove_local_import_paths()
            clear_colliding_modules()
            coordinator_validate = import_coordinator_validate()
            before_load_path = list(sys.path)
            validator = module._load_local_native_validator_module()

            self.assertEqual(sys.path, before_load_path)
            self.assertIs(sys.modules.get("validate"), coordinator_validate)
            self.assertEqual(
                Path(validator.legacy.__file__).resolve(),
                (LOCAL_ROOT / "scripts" / "validate.py").resolve(),
            )
            bundle = native_fixture.make_native_bundle()
            validator.validate_native_bundle(copy.deepcopy(bundle), VALIDATION_NOW)
        finally:
            module._load_local_native_validator_module.cache_clear()
            restore_collision_state(path_state, module_state)

    def test_F1_Local_validator_loaded_first_does_not_shadow_coordinator_validate(self):
        path_state, module_state = save_collision_state()
        module._load_local_native_validator_module.cache_clear()
        try:
            remove_local_import_paths()
            clear_colliding_modules()
            before_load_path = list(sys.path)
            validator = module._load_local_native_validator_module()

            self.assertEqual(sys.path, before_load_path)
            for name in COLLIDING_LOCAL_MODULES:
                self.assertNotIn(name, sys.modules)

            coordinator_validate = import_coordinator_validate()
            self.assertEqual(
                Path(coordinator_validate.__file__).resolve(),
                (COORDINATOR_SCRIPTS / "validate.py").resolve(),
            )
            bundle = native_fixture.make_native_bundle()
            validator.validate_native_bundle(copy.deepcopy(bundle), VALIDATION_NOW)
        finally:
            module._load_local_native_validator_module.cache_clear()
            restore_collision_state(path_state, module_state)

    def test_build_context_rejects_noncanonical_release_state(self):
        with self.assertRaisesRegex(module.IntegratedModeError, "non-canonical"):
            integrated_context("COMPLETE")

    def test_build_context_rejects_raw_observation_bypass_with_fabricated_completion(self):
        fake = observed()
        fake["local_responsibility_complete"] = True
        with self.assertRaisesRegex(module.IntegratedModeError, "Raw responsibility observations are not accepted"):
            module.build_integrated_context(
                parent_task=parent_task(),
                local_protocol_ref=LOCAL_REF,
                local_protocol_digest=DIGEST,
                engineering_evidence_provider_ref=V35_REF,
                engineering_evidence_provider_digest=DIGEST,
                responsibility_inputs=[],
                responsibility_observations=[fake],
            )

    def test_CH_R1_09_schema_runtime_observation_contract_matches(self):
        schema = yaml.safe_load(
            (ROOT / "schemas" / "local-v1.1-integrated.schema.yaml").read_text(encoding="utf-8")
        )
        item_schema = schema["properties"]["responsibilities"]["items"]
        self.assertFalse(item_schema["additionalProperties"])
        self.assertEqual(set(item_schema["required"]), module.RESPONSIBILITY_OBSERVATION_FIELDS)
        self.assertEqual(set(item_schema["properties"]), module.RESPONSIBILITY_OBSERVATION_FIELDS)
        self.assertEqual(
            set(item_schema["properties"]["release_state"]["enum"]),
            module.CANONICAL_RELEASE_STATES,
        )
        self.assertEqual(set(observed()), module.RESPONSIBILITY_OBSERVATION_FIELDS)

    def test_v31_provider_cannot_select_integrated_mode(self):
        with self.assertRaisesRegex(module.IntegratedModeError, "V3.5"):
            module.build_integrated_context(
                parent_task=parent_task(),
                local_protocol_ref=LOCAL_REF,
                local_protocol_digest=DIGEST,
                engineering_evidence_provider_ref=V35_REF.replace("v3.5", "v3.1"),
                engineering_evidence_provider_digest=DIGEST,
                responsibility_inputs=[],
            )

    def test_integrated_mode_has_complete_non_authority_boundary(self):
        context = integrated_context(result=v35_result())
        self.assertEqual(set(context["non_authorities"]), module.NON_AUTHORITIES)
        self.assertEqual(context["authority"], "OBSERVATION_ONLY")
        self.assertEqual(context["legacy_v31_interpretation"], "READABLE_COMPATIBILITY_ONLY")

    def test_every_forbidden_authority_action_is_rejected(self):
        for action in module.NON_AUTHORITIES:
            with self.subTest(action=action):
                with self.assertRaisesRegex(module.IntegratedModeError, "cannot exercise authority"):
                    module.assert_observation_only_action(action)

    def test_status_projects_validated_local_completion_without_acceptance_authority(self):
        bundle, parent, task = validated_native_inputs()
        row = module.observe_responsibility(
            parent,
            task,
            v35_result_for(task),
            local_bundle=bundle,
            local_validation_now=VALIDATION_NOW,
        )
        context = module.build_integrated_context(
            parent_task=parent,
            local_protocol_ref=LOCAL_REF,
            local_protocol_digest=DIGEST,
            engineering_evidence_provider_ref=V35_REF,
            engineering_evidence_provider_digest=DIGEST,
            responsibility_inputs=[{
                "responsibility_task": task,
                "v35_result": v35_result_for(task),
                "local_bundle": bundle,
                "local_validation_now": VALIDATION_NOW,
            }],
        )
        status = module.derive_programme_status(context)
        self.assertEqual(status["engineering_acceptance_verdict"], "NOT_AUTHORIZED")
        self.assertEqual(status["merge_authority"], "NOT_AUTHORIZED")
        self.assertEqual(status["coder_engineering_complete"], 1)
        self.assertEqual(status["local_responsibilities_complete"], 1)

    def test_stopped_status_is_reported_without_completion_claim(self):
        status = module.derive_programme_status(integrated_context("STOPPED"))
        self.assertEqual(status["stopped"], ["PRD-492-A"])
        self.assertEqual(status["local_responsibilities_complete"], 0)
        self.assertEqual(status["engineering_acceptance_verdict"], "NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()