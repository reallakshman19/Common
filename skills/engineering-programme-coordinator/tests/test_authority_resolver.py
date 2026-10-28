import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT.parent / "Local_PR_Deliverty_v1.1"
LOCAL_TESTS = LOCAL / "tests"
LOCAL_SCRIPTS = LOCAL / "scripts"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(LOCAL_SCRIPTS))
sys.path.insert(0, str(LOCAL_TESTS))

from authority_resolver import (
    ALL_ACTIONS,
    _derive_ready,
    resolve_authority,
    semantic_errors,
    validate_authority_resolution,
)


SPEC = importlib.util.spec_from_file_location(
    "local_native_fixture",
    LOCAL_TESTS / "test_492_native_validation.py",
)
fixture = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(fixture)

NOW = "2026-10-04T00:08:00Z"
PRD = fixture.PRD


def local_validator():
    return fixture.native


def responsibility_stages(bundle):
    return [row for row in bundle["stages"] if row["task_id"] == PRD]


def derive_without_full_revalidation(bundle):
    parent = next(task for task in bundle["tasks"] if task["kind"] == "PARENT")
    task = next(task for task in bundle["tasks"] if task.get("task_id") == PRD)
    observation = {
        "task_id": PRD,
        "release_state": "READY",
        "acceptance_epoch_id": task["acceptance_epoch_id"],
        "acceptance_profile_ref": task["acceptance_profile_ref"],
        "acceptance_profile_digest": task["acceptance_profile_digest"],
        "local_responsibility_complete": False,
    }
    return _derive_ready(
        bundle=bundle,
        parent=parent,
        task=task,
        observation=observation,
        observed_at=NOW,
        validator=local_validator(),
    )


class AuthorityResolverTests(unittest.TestCase):
    def test_real_native_bundle_validates_before_complete_resolution(self):
        bundle = fixture.make_native_bundle()
        result = resolve_authority(bundle, PRD, NOW)
        self.assertEqual(result["local_validation"], "PASS")
        self.assertEqual(result["lifecycle"]["state"], "COMPLETE")
        self.assertEqual(result["active_role"], "NONE")
        self.assertEqual(result["allowed_actions"], [])

    def test_ready_bundle_cannot_self_authorize_when_native_validation_fails(self):
        bundle = fixture.make_native_bundle()
        bundle["native_support"]["acceptance_profiles"][0]["digest"] = "f" * 64
        with self.assertRaisesRegex(Exception, "READY responsibility failed Local native validation"):
            resolve_authority(bundle, PRD, NOW)

    def test_non_ready_release_only_reduces_authority(self):
        bundle = fixture.make_native_bundle()
        bundle["tasks"][0]["control_plane"]["responsibility_registry"][0]["release_state"] = "BLOCKED_DEPENDENCY"
        result = resolve_authority(bundle, PRD, NOW)
        self.assertEqual(result["local_validation"], "NOT_REQUIRED_NO_CAPABILITY")
        self.assertEqual(result["lifecycle"]["state"], "BLOCKED")
        self.assertEqual(result["active_role"], "NONE")
        self.assertEqual(result["allowed_actions"], [])
        self.assertEqual(set(result["forbidden_actions"]), set(ALL_ACTIONS))

    def test_caller_role_assertion_is_not_an_input_surface(self):
        bundle = fixture.make_native_bundle()
        bundle["active_role"] = "CODER"
        with self.assertRaisesRegex(Exception, "unexpected/missing top-level fields"):
            resolve_authority(bundle, PRD, NOW)

    def test_completed_coder_stage_does_not_activate_reviewer(self):
        bundle = fixture.make_native_bundle(complete=False)
        stages = responsibility_stages(bundle)
        coder = next(row for row in stages if row["stage"] == "CODER")
        bundle["stages"] = [
            row for row in bundle["stages"]
            if row["task_id"] != PRD or row["record_id"] == coder["record_id"]
        ]
        result = derive_without_full_revalidation(bundle)
        self.assertEqual(result["lifecycle"]["state"], "STAGE_COMPLETE")
        self.assertEqual(result["active_role"], "NONE")
        self.assertEqual(result["next_eligible_role"], "REVIEWER")
        self.assertEqual(result["allowed_actions"], [])

    def test_running_coder_derives_material_capability_from_stage(self):
        bundle = fixture.make_native_bundle(complete=False)
        coder = next(row for row in responsibility_stages(bundle) if row["stage"] == "CODER")
        coder["status"] = "RUNNING"
        coder["writer_stopped"] = False
        coder["publications"]["end"] = None
        coder["work_periods"][-1]["end"] = None
        bundle["stages"] = [
            row for row in bundle["stages"]
            if row["task_id"] != PRD or row["record_id"] == coder["record_id"]
        ]
        result = derive_without_full_revalidation(bundle)
        self.assertEqual(result["lifecycle"]["state"], "ACTIVE")
        self.assertEqual(result["active_role"], "CODER")
        self.assertEqual(result["active_principal"], coder["executor"])
        self.assertEqual(result["principal_independence"], "NONE")
        self.assertIn("WRITE_CANDIDATE", result["allowed_actions"])
        self.assertIn("REQUEST_STAGE_ADVANCE", result["allowed_actions"])

    def test_owner_hold_blocks_material_actions(self):
        bundle = fixture.make_native_bundle(complete=False)
        coder = next(row for row in responsibility_stages(bundle) if row["stage"] == "CODER")
        coder["status"] = "RUNNING"
        coder["writer_stopped"] = False
        coder["publications"]["end"] = None
        coder["work_periods"][-1]["end"] = None
        bundle["stages"] = [
            row for row in bundle["stages"]
            if row["task_id"] != PRD or row["record_id"] == coder["record_id"]
        ]
        parent = next(task for task in bundle["tasks"] if task["kind"] == "PARENT")
        parent["owner_commands"].append({
            "id": "CMD-HOLD-R4",
            "command": "HOLD",
            "target": "CODER",
            "child_issue": None,
            "responsibility_task_id": PRD,
            "issued_at": "2026-10-04T00:07:00Z",
            "instruction_ref": "owner://hold/r4",
            "reason": "test hold",
            "minutes": None,
            "owner_principal": parent["owner_principals"][0],
            "source_kind": "DIRECT_OWNER_SESSION",
            "source_digest": "e" * 64,
            "authentication_status": "AUTHENTICATED",
        })
        result = derive_without_full_revalidation(bundle)
        self.assertEqual(result["lifecycle"]["state"], "HELD")
        self.assertEqual(result["active_role"], "CODER")
        self.assertNotIn("WRITE_CANDIDATE", result["allowed_actions"])
        self.assertNotIn("REPAIR_CANDIDATE", result["allowed_actions"])
        self.assertEqual(
            set(result["allowed_actions"]),
            {"PUBLISH_EVIDENCE", "ESCALATE"},
        )

    def test_owner_stop_removes_active_role_and_capability(self):
        bundle = fixture.make_native_bundle(complete=False)
        coder = next(row for row in responsibility_stages(bundle) if row["stage"] == "CODER")
        coder["status"] = "RUNNING"
        coder["writer_stopped"] = False
        coder["publications"]["end"] = None
        coder["work_periods"][-1]["end"] = None
        bundle["stages"] = [
            row for row in bundle["stages"]
            if row["task_id"] != PRD or row["record_id"] == coder["record_id"]
        ]
        parent = next(task for task in bundle["tasks"] if task["kind"] == "PARENT")
        parent["owner_commands"].append({
            "id": "CMD-STOP-R4",
            "command": "STOP",
            "target": "CODER",
            "child_issue": None,
            "responsibility_task_id": PRD,
            "issued_at": "2026-10-04T00:07:00Z",
            "instruction_ref": "owner://stop/r4",
            "reason": "test stop",
            "minutes": None,
            "owner_principal": parent["owner_principals"][0],
            "source_kind": "DIRECT_OWNER_SESSION",
            "source_digest": "f" * 64,
            "authentication_status": "AUTHENTICATED",
        })
        result = derive_without_full_revalidation(bundle)
        self.assertEqual(result["lifecycle"]["state"], "STOPPED")
        self.assertEqual(result["active_role"], "NONE")
        self.assertEqual(result["allowed_actions"], [])

    def test_same_principal_review_succession_is_degraded_with_transition(self):
        bundle = fixture.make_native_bundle(collapse=True, complete=False)
        stages = responsibility_stages(bundle)
        coordinator = next(row for row in stages if row["stage"] == "COORDINATOR")
        coordinator["status"] = "RUNNING"
        coordinator["writer_stopped"] = False
        coordinator["publications"]["end"] = None
        coordinator["work_periods"][-1]["end"] = None
        result = derive_without_full_revalidation(bundle)
        self.assertEqual(result["active_role"], "COORDINATOR")
        self.assertEqual(result["principal_independence"], "DEGRADED")
        self.assertEqual(
            result["role_transition_ref"],
            "RT-REVIEWER-COORDINATOR-1",
        )

    def test_same_principal_review_without_transition_fails_closed(self):
        bundle = fixture.make_native_bundle(collapse=True, complete=False)
        coordinator = next(
            row for row in responsibility_stages(bundle)
            if row["stage"] == "COORDINATOR"
        )
        coordinator["status"] = "RUNNING"
        coordinator["writer_stopped"] = False
        coordinator["publications"]["end"] = None
        coordinator["work_periods"][-1]["end"] = None
        bundle["native_support"]["role_transitions"] = []
        with self.assertRaisesRegex(Exception, "lacks validated ROLE_TRANSITION"):
            derive_without_full_revalidation(bundle)

    def test_real_ready_incomplete_bundle_validates_without_self_activating_successor(self):
        bundle = fixture.make_native_bundle(complete=False)
        result = resolve_authority(bundle, PRD, NOW)
        self.assertEqual(result["local_validation"], "PASS")
        self.assertEqual(result["lifecycle"]["state"], "STAGE_COMPLETE")
        self.assertEqual(result["active_role"], "NONE")
        self.assertEqual(result["allowed_actions"], [])

    def test_schema_valid_forged_projection_requires_raw_bundle_replay(self):
        bundle = fixture.make_native_bundle()
        result = resolve_authority(bundle, PRD, NOW)
        forged = copy.deepcopy(result)
        forged["lifecycle"]["state"] = "ACTIVE"
        forged["active_role"] = "CODER"
        forged["active_principal"] = "attacker"
        forged["principal_independence"] = "NONE"
        forged["allowed_actions"] = ["WRITE_CANDIDATE"]
        forged["forbidden_actions"] = sorted(set(ALL_ACTIONS) - {"WRITE_CANDIDATE"})
        errors = validate_authority_resolution(forged, bundle, NOW)
        self.assertTrue(any("must exactly equal raw Local-bundle derivation" in e for e in errors), errors)

    def test_unbound_projection_validation_is_rejected(self):
        bundle = fixture.make_native_bundle()
        result = resolve_authority(bundle, PRD, NOW)
        errors = validate_authority_resolution(result, None, NOW)
        self.assertTrue(any("requires raw Local native bundle" in e for e in errors), errors)

    def test_same_role_rework_retains_original_transition_basis(self):
        bundle = fixture.make_native_bundle(collapse=True, complete=False)
        stages = responsibility_stages(bundle)
        coordinator = next(row for row in stages if row["stage"] == "COORDINATOR")
        coordinator["status"] = "STAGE_COMPLETE"
        rework = copy.deepcopy(coordinator)
        rework["record_id"] = "S3-REWORK"
        rework["attempt"] = coordinator["attempt"] + 1
        rework["status"] = "REWORK"
        rework["started_at"] = "2026-10-04T00:02:30Z"
        rework["work_periods"] = [{"start": "2026-10-04T00:02:30Z", "end": None}]
        rework["publications"]["start"]["comment_ref"] = "https://example.invalid/issues/85#s3-rework-start"
        rework["publications"]["start"]["published_at"] = "2026-10-04T00:02:29Z"
        rework["publications"]["end"] = None
        rework["writer_stopped"] = False
        bundle["stages"].append(rework)
        result = derive_without_full_revalidation(bundle)
        self.assertEqual(result["active_role"], "COORDINATOR")
        self.assertEqual(result["principal_independence"], "DEGRADED")
        self.assertEqual(result["role_transition_ref"], "RT-REVIEWER-COORDINATOR-1")

    def test_allowed_and_forbidden_are_exact_complement(self):
        bundle = fixture.make_native_bundle()
        result = resolve_authority(bundle, PRD, NOW)
        self.assertEqual(
            set(result["allowed_actions"]) | set(result["forbidden_actions"]),
            set(ALL_ACTIONS),
        )
        self.assertFalse(
            set(result["allowed_actions"]) & set(result["forbidden_actions"])
        )
        self.assertEqual(semantic_errors(result), [])

    def test_output_boundaries_are_explicitly_non_authoritative(self):
        bundle = fixture.make_native_bundle()
        result = resolve_authority(bundle, PRD, NOW)
        self.assertEqual(result["authority"], "LOCAL_AUTHORITY_RESOLUTION")
        self.assertFalse(result["authority_boundaries"]["performs_local_stage_transition"])
        self.assertFalse(result["authority_boundaries"]["grants_merge_authority"])
        self.assertFalse(result["authority_boundaries"]["grants_production_cutover"])
        self.assertFalse(result["authority_boundaries"]["accepts_caller_role_assertion"])
        self.assertFalse(result["authority_boundaries"]["accepts_caller_capability_assertion"])


if __name__ == "__main__":
    unittest.main()
