import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
LOCAL_ROOT = SKILLS / "Local_PR_Deliverty_v1.1"
LOCAL_TESTS = LOCAL_ROOT / "tests"
V35_ROOT = SKILLS / "engineering-pr-delivery-v3.5"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(LOCAL_ROOT / "scripts"))
sys.path.insert(0, str(LOCAL_TESTS))

from phase1_runtime_replay import (
    canonical_digest,
    run_phase1_replay,
    validate_phase1_replay,
)
from provider_mutation import canonical_provider_key, derive_provider_action


NATIVE_SPEC = importlib.util.spec_from_file_location(
    "p1i_native_fixture",
    LOCAL_TESTS / "test_492_native_validation.py",
)
native_fixture = importlib.util.module_from_spec(NATIVE_SPEC)
assert NATIVE_SPEC.loader is not None
NATIVE_SPEC.loader.exec_module(native_fixture)

PROTOCOL_SPEC = importlib.util.spec_from_file_location(
    "p1i_local_protocol_fixture",
    LOCAL_TESTS / "test_protocol.py",
)
protocol_fixture = importlib.util.module_from_spec(PROTOCOL_SPEC)
assert PROTOCOL_SPEC.loader is not None
PROTOCOL_SPEC.loader.exec_module(protocol_fixture)

V35_SPEC = importlib.util.spec_from_file_location(
    "p1i_v35",
    V35_ROOT / "scripts" / "embedded_coder_v35.py",
)
v35 = importlib.util.module_from_spec(V35_SPEC)
assert V35_SPEC.loader is not None
V35_SPEC.loader.exec_module(v35)


NOW = "2026-10-04T00:08:00Z"


def active_native_bundle():
    """Build a real Local native responsibility with a fresh Coordinator rework attempt."""
    bundle = native_fixture.make_native_bundle(complete=False)
    coordinator = next(
        row for row in bundle["stages"]
        if row["task_id"] == native_fixture.PRD and row["stage"] == "COORDINATOR"
    )
    rework = copy.deepcopy(coordinator)
    rework["record_id"] = "S3-REWORK"
    rework["attempt"] = coordinator["attempt"] + 1
    rework["previous_record"] = coordinator["record_id"]
    rework["started_at"] = "2026-10-04T00:03:00Z"
    rework["work_periods"] = [{"start": "2026-10-04T00:03:00Z", "end": None}]
    rework["status"] = "REWORK"
    rework["input_sha"] = coordinator["validated_sha"]
    rework["output_sha"] = None
    rework["validated_sha"] = None
    rework["acceptance_checked"] = []
    rework["validation"] = []
    rework["findings"] = []
    rework["changes"] = "Fresh same-stage integration rework."
    rework["repeat_stages"] = []
    rework["writer_stopped"] = False
    rework["next_action"] = "Continue bounded repair and replay."
    rework["publications"]["start"] = {
        "comment_ref": "https://example.invalid/issues/85#start-S3-REWORK",
        "published_at": "2026-10-04T00:03:00Z",
        "summary": "Fresh Coordinator rework start.",
    }
    rework["publications"]["end"] = None
    rework["parent_context"] = {
        "read_at": "2026-10-04T00:03:00Z",
        "through_comment_ref": "https://example.invalid/issues/85#before-S3-REWORK",
        "reconciled_points": ["Reconstructed prior Local responsibility evidence."],
    }
    rework["context_start_ref"] = "CTX-START-S3-REWORK"
    start_snapshot = next(
        row for row in bundle["support"]["context_snapshots"]
        if row["snapshot_id"] == coordinator["context_start_ref"]
    )
    rework_start = copy.deepcopy(start_snapshot)
    rework_start["snapshot_id"] = rework["context_start_ref"]
    rework_start["task_id"] = rework["task_id"]
    rework_start["observed_at"] = "2026-10-04T00:03:00Z"
    rework_start["parent_comment_frontier"] = rework["parent_context"]["through_comment_ref"]
    rework_start["reconciliation_note"] = "Fresh Coordinator rework START context reconstructed from durable provider state."
    for index, event in enumerate(rework_start["context_events"], start=1):
        event["provider_id"] = f"rework-start-{index}"
        if event["source_kind"] == "PARENT_COMMENT":
            event["provider_ref"] = rework["parent_context"]["through_comment_ref"]
            event["created_at"] = "2026-10-04T00:03:00Z"
            event["updated_at"] = "2026-10-04T00:03:00Z"
    bundle["support"]["context_snapshots"].append(rework_start)
    rework["context_pre_verdict_ref"] = None
    rework["source_attestation"] = None
    rework["review_lease_ref"] = None
    rework["evidence_refs"] = []
    rework["evidence_manifest"] = []
    rework["acceptance_results"] = []
    rework["carried_findings"] = []
    rework["discovery_freeze"] = None
    rework["production_output"] = {
        "deliverables": ["Fresh Coordinator rework is active."],
        "coverage_completed": [],
        "fixes_applied": [],
        "regressions_added": [],
        "education_points": ["Active rework has no verdict yet; prior accepted evidence remains historical only."],
        "unresolved_internal_defects": [],
        "internal_fixable_defects_remaining": 0,
        "blocking_class": "NONE",
        "coverage_complete_for_stage": False,
        "early_termination": False,
        "early_termination_reason": None,
        "candidate_changed": False,
        "defects_found": [],
        "defects_fixed_here": [],
        "external_escalations": [],
        "changed_components": [],
    }
    bundle["stages"].append(rework)
    bundle["observed"]["parent_comment_frontiers"][rework["record_id"]] = {
        "comment_ref": rework["parent_context"]["through_comment_ref"],
        "observed_at": rework["started_at"],
    }
    bundle["observed"]["issue_states"] = {"85": "OPEN", "86": "OPEN"}
    bundle["observed"]["pr_states"]["101"] = "DRAFT"
    bundle["observed"]["merged"] = {}
    return bundle


def v35_pair(bundle):
    parent = next(row for row in bundle["tasks"] if row["kind"] == "PARENT")
    task = next(row for row in bundle["tasks"] if row["kind"] == "RESPONSIBILITY")
    local_ref = task["protocol_ref"]
    prefix = local_ref.split(":skills/", 1)[0]
    relay_ref = prefix + ":skills/engineering-pr-delivery-v3.5"
    context = v35.build_context(
        local_parent_task_id=parent["task_id"],
        local_responsibility_task_id=task["task_id"],
        local_protocol_ref=local_ref,
        local_protocol_digest="a" * 64,
        relay_protocol_ref=relay_ref,
        relay_protocol_digest="b" * 64,
        acceptance_epoch_ref=task["acceptance_epoch_id"],
        acceptance_profile_ref=task["acceptance_profile_ref"],
        acceptance_profile_digest=task["acceptance_profile_digest"],
    )
    result = v35.build_task_result(
        context,
        engineering_responsibility_complete=False,
        coverage="Active nested Coder evidence only; Local lifecycle remains authoritative.",
        evidence_refs=["local://phase1-replay/v35"],
    )
    return context, result


def provider_transaction():
    identity = {
        "programme_or_parent_id": "COMMON-PROD-CONTROL-V1",
        "prd_id": "PRD-527-P1-I",
        "resource_kind": "ISSUE",
        "mutation_slot": "HORIZONTAL_REPLAY_NOOP",
        "canonical_key": "",
    }
    identity["canonical_key"] = canonical_provider_key(identity)
    value = {
        "schema_version": "PROVIDER_MUTATION_V1",
        "authority": "PROVIDER_MUTATION_TRANSACTION",
        "identity": identity,
        "mutation": {
            "class": "CREATE_ONCE",
            "operation": "CREATE_ISSUE",
            "payload_digest": "c" * 64,
            "attempted": True,
            "attempt_id": "provider-request://lost-response",
            "provider_id": None,
        },
        "lookup": {"performed": True, "matches": []},
        "readback": {
            "performed": False,
            "found": False,
            "provider_id": None,
            "canonical_key": None,
            "payload_digest": None,
        },
        "next_action": {},
    }
    value["next_action"] = derive_provider_action(value)
    return value


def request():
    bundle = active_native_bundle()
    context, result = v35_pair(bundle)
    return {
        "local_bundle": bundle,
        "task_id": native_fixture.PRD,
        "observed_at": NOW,
        "v35_context": context,
        "v35_result": result,
        "provider_transaction": provider_transaction(),
    }


class Phase1RuntimeReplayTests(unittest.TestCase):
    def test_actual_local_native_bundle_is_accepted(self):
        req = request()
        result = run_phase1_replay(req)
        self.assertEqual(result["assertions"]["local_native_validation"], "PASS")
        self.assertEqual(result["authority_resolution"]["active_role"], "COORDINATOR")
        self.assertEqual(result["authority_resolution"]["lifecycle"]["state"], "REWORK")

    def test_actual_v35_result_cannot_complete_local_responsibility(self):
        result = run_phase1_replay(request())
        self.assertFalse(result["v35"]["local_responsibility_complete"])
        self.assertFalse(result["local_observation"]["local_responsibility_complete"])

    def test_freshness_bindings_are_derived_from_local_evidence_and_lease(self):
        result = run_phase1_replay(request())
        freshness = result["freshness"]
        self.assertTrue(freshness["source_ledger"]["ledger_ref"].startswith("local://review-lease/"))
        self.assertGreater(freshness["source_ledger"]["evidence_count"], 0)
        self.assertNotIn("evidence_bindings", result)

    def test_required_method_denominator_comes_from_acceptance_profile(self):
        req = request()
        result = run_phase1_replay(req)
        bundle = req["local_bundle"]
        task = next(row for row in bundle["tasks"] if row["kind"] == "RESPONSIBILITY")
        profile = next(
            row for row in bundle["native_support"]["acceptance_profiles"]
            if row["profile_id"] == task["acceptance_profile_ref"]
        )
        lease_id = result["freshness"]["source_ledger"]["ledger_ref"].split(
            "local://review-lease/", 1
        )[1]
        lease = next(
            row for row in bundle["support"]["review_leases"]
            if row["lease_id"] == lease_id
        )
        role = "COORDINATOR" if lease["certifier_role"] == "PARENT_CHECK" else lease["certifier_role"]
        expected = sorted({
            row["verification_method_id"]
            for row in profile["role_bindings"][role]
        })
        self.assertEqual(result["freshness"]["required_method_ids"], expected)

    def test_nominal_replay_composes_execution_and_current_state(self):
        result = run_phase1_replay(request())
        execution = result["execution_state"]
        current = result["current_state"]
        self.assertEqual(
            current["next_action"]["type"],
            execution["next_action"]["type"],
        )
        self.assertEqual(
            current["next_action"]["execution_state_digest"],
            canonical_digest(execution),
        )
        self.assertEqual(current["production"]["mode"], "OFF")
        self.assertEqual(current["merge_authority"]["state"], "NOT_GRANTED")

    def test_candidate_movement_invalidates_prior_evidence_and_forces_verification(self):
        req = request()
        task = next(row for row in req["local_bundle"]["tasks"] if row["kind"] == "RESPONSIBILITY")
        req["local_bundle"]["observed"]["pr_heads"][str(task["pr"])] = "f" * 40
        result = run_phase1_replay(req)
        self.assertEqual(result["freshness"]["overall"]["evidence_state"], "STALE")
        self.assertEqual(result["execution_state"]["next_action"]["type"], "VERIFY_CANDIDATE")
        self.assertEqual(result["execution_state"]["next_action"]["reason_code"], "VERIFICATION_REQUIRED")
        self.assertNotEqual(result["execution_state"]["next_action"]["type"], "REQUEST_STAGE_ADVANCE")

    def test_active_stage_environment_movement_invalidates_historical_evidence(self):
        req = request()
        bundle = req["local_bundle"]
        task = next(row for row in bundle["tasks"] if row["kind"] == "RESPONSIBILITY")
        active = [
            row for row in bundle["stages"]
            if row["task_id"] == task["task_id"]
        ][-1]
        alternatives = [
            row for row in bundle["support"]["environments"]
            if row["environment_id"] != active["environment_ref"]
        ]
        self.assertTrue(alternatives)
        active["environment_ref"] = alternatives[0]["environment_id"]
        result = run_phase1_replay(req)
        self.assertEqual(result["freshness"]["overall"]["evidence_state"], "STALE")
        self.assertIn(
            "ENVIRONMENT_CHANGED",
            {
                reason
                for row in result["freshness"]["evidence_results"]
                for reason in row["reasons"]
            },
        )
        self.assertEqual(result["execution_state"]["next_action"]["type"], "VERIFY_CANDIDATE")

    def test_dependency_movement_invalidates_prior_evidence_and_forces_verification(self):
        req = request()
        task = next(row for row in req["local_bundle"]["tasks"] if row["kind"] == "RESPONSIBILITY")
        lease = max(
            (
                row for row in req["local_bundle"]["support"]["review_leases"]
                if row["task_id"] == task["task_id"]
            ),
            key=lambda row: row["sealed_at"],
        )
        if lease["dependency_heads"]:
            dep = lease["dependency_heads"][0]["task_id"]
            req["local_bundle"]["observed"]["dependency_heads"][task["task_id"]] = {
                dep: "e" * 40,
            }
        else:
            req["local_bundle"]["observed"]["dependency_heads"][task["task_id"]] = {
                "PRD-UPSTREAM": "e" * 40,
            }
        result = run_phase1_replay(req)
        self.assertEqual(result["freshness"]["overall"]["evidence_state"], "STALE")
        self.assertEqual(result["execution_state"]["next_action"]["type"], "VERIFY_CANDIDATE")

    def test_provider_lost_response_never_emits_second_mutation(self):
        result = run_phase1_replay(request())
        self.assertEqual(
            result["provider_transaction"]["next_action"],
            "READBACK_AFTER_MUTATION",
        )
        self.assertFalse(result["provider_transaction"]["mutation_performed_by_replay"])

    def test_readiness_marks_horizontal_integration_but_stays_off(self):
        result = run_phase1_replay(request())
        readiness = result["production_readiness"]
        self.assertEqual(readiness["production_mode"], "OFF")
        self.assertEqual(
            readiness["components"]["real_artifact_horizontal_integration"]["state"],
            "CONDITIONALLY_QUALIFIED",
        )
        self.assertEqual(result["assertions"]["artifact_class"], "CANONICAL_SYNTHETIC")
        self.assertIn(
            "P1I-REAL-ARTIFACT-MISSING",
            {row["id"] for row in readiness["cutover_blockers"]},
        )
        self.assertEqual(
            readiness["components"]["proof_obligation_runtime"]["state"],
            "NOT_IMPLEMENTED",
        )
        self.assertEqual(
            readiness["components"]["evidence_gate"]["state"],
            "NOT_IMPLEMENTED",
        )

    def test_synthetic_replay_cannot_self_certify_real_artifact(self):
        result = run_phase1_replay(request())
        forged = copy.deepcopy(result)
        forged["production_readiness"]["components"]["real_artifact_horizontal_integration"]["state"] = "VERIFIED"
        from phase1_runtime_replay import semantic_errors
        self.assertTrue(
            any("cannot mark real-artifact" in error for error in semantic_errors(forged))
        )

    def test_source_artifacts_are_immutable(self):
        req = request()
        before = json.dumps(req, sort_keys=True)
        result = run_phase1_replay(req)
        self.assertEqual(json.dumps(req, sort_keys=True), before)
        self.assertTrue(result["assertions"]["local_source_unchanged"])
        self.assertTrue(result["assertions"]["v35_source_unchanged"])
        self.assertTrue(result["assertions"]["provider_source_unchanged"])

    def test_caller_cannot_inject_role_or_capability(self):
        req = request()
        req["active_role"] = "CODER"
        with self.assertRaisesRegex(Exception, "unexpected/missing"):
            run_phase1_replay(req)

    def test_v35_forged_local_completion_is_rejected(self):
        req = request()
        req["v35_result"]["local_responsibility_complete"] = True
        req["v35_result"]["digest"] = v35.canonical_digest({
            k: v for k, v in req["v35_result"].items() if k != "digest"
        })
        with self.assertRaisesRegex(Exception, "never declare"):
            run_phase1_replay(req)

    def test_unbound_stored_replay_is_rejected(self):
        req = request()
        result = run_phase1_replay(req)
        errors = validate_phase1_replay(result, None)
        self.assertTrue(any("requires source request" in error for error in errors), errors)

    def test_forged_stored_replay_is_rejected(self):
        req = request()
        result = run_phase1_replay(req)
        forged = copy.deepcopy(result)
        forged["assertions"]["production_mode"] = "SHADOW_ONLY"
        errors = validate_phase1_replay(forged, req)
        self.assertTrue(errors)

    def test_no_output_grants_forbidden_authority(self):
        result = run_phase1_replay(request())
        self.assertFalse(any(result["authority_boundaries"].values()))
        self.assertFalse(result["authority_resolution"]["authority_boundaries"]["performs_local_stage_transition"])
        self.assertFalse(result["authority_resolution"]["authority_boundaries"]["grants_merge_authority"])
        self.assertFalse(result["authority_resolution"]["authority_boundaries"]["grants_production_cutover"])


if __name__ == "__main__":
    unittest.main()
