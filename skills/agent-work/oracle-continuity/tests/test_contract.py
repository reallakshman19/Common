"""Failure-oriented checks for coordination invariants, not domain correctness."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("oracle_validate", ROOT / "validate.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def example(name="completed"):
    return V.load(ROOT / "examples" / (name + ".json"))


def advance(state):
    state["revision"] += 1
    n = state["revision"]
    ev = copy.deepcopy(state["history"][-1])
    ev.update(id=f"event-{n}", seq=n, previous_id=f"event-{n-1}", command_id=f"command-{n}", actor=state["control"]["oracle_session_id"])
    state["history"].append(ev)
    return state


class ContractTests(unittest.TestCase):
    def reject(self, state, code, previous=None, artifact_root=None):
        errors = V.validate(state, previous, artifact_root)
        self.assertTrue(any(e.startswith(code + " ") or e.startswith(code + ":") for e in errors), errors)

    def test_schema_itself(self):
        for name in ("oracle-state.schema.json", "oracle-command.schema.json"):
            V.Draft202012Validator.check_schema(V.load(ROOT / name))

    def test_all_examples(self):
        for name in ("initial", "worker-cutover", "oracle-cutover", "completed", "learning-pending"):
            with self.subTest(name=name):
                self.assertEqual([], V.validate(example(name)))

    def test_valid_publication_commands_and_cutovers(self):
        for old, new in (("initial", "worker-cutover"), ("worker-cutover", "oracle-cutover"), ("oracle-cutover", "completed")):
            with self.subTest(new=new):
                before, after = example(old), example(new)
                self.assertEqual([], V.validate(after, before))
                path = ROOT / "examples" / (new + ".json")
                self.assertEqual([], V.validate_command(V.load(path.with_suffix(".command.json")), before, after, path.read_bytes()))

    def test_actual_example_hash(self):
        self.assertEqual([], V.validate(example(), artifact_root=ROOT / "examples"))

    def test_unknown_core_property(self):
        s = example(); s["tasks"][0]["readyy"] = True
        self.reject(s, "SCHEMA")

    def test_wrong_schema_version(self):
        s = example(); s["schema_version"] = "2.0.0"
        self.reject(s, "SCHEMA")

    def test_date_requires_timezone(self):
        s = example(); s["updated_at"] = "2026-10-23T08:00:00"
        self.reject(s, "SCHEMA")

    def test_blank_aim(self):
        s = example(); s["project"]["aim"] = "   "
        self.reject(s, "SCHEMA")

    def test_unversioned_unobserved_source(self):
        s = example(); s["project"]["aim_source"].update(version=None, captured_at=None)
        self.reject(s, "SCHEMA")

    def test_duplicate_json_keys_and_nan_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmp:
            p = Path(tmp) / "bad.json"
            for raw in ('{"x": 1, "x": 2}', '{"x": NaN}'):
                p.write_text(raw, encoding="utf-8")
                with self.assertRaises(ValueError):
                    V.load(p)

    def test_bad_record_shapes_are_diagnostics(self):
        for value in (None, [None], {}, "wrong", 3):
            with self.subTest(value=value):
                s = example(); s["assignments"] = value
                self.reject(s, "SCHEMA")

    def test_duplicate_entity_id(self):
        s = example(); s["sessions"].append(copy.deepcopy(s["sessions"][0]))
        self.reject(s, "DUPLICATE_ID")

    def test_unknown_reference(self):
        s = example(); s["evidence"][0]["actor"] = "missing-session"
        self.reject(s, "REFERENCE")

    def test_dependency_cycle(self):
        s = example(); s["tasks"][0]["dependencies"] = ["task-1"]
        self.reject(s, "DEPENDENCY_CYCLE")

    def test_parallel_writer_conflict(self):
        s = example("initial")
        a = copy.deepcopy(s["assignments"][0]); a.update(id="runner-assignment", role="runner", session_id="reviewer-1", required_capabilities=[])
        s["assignments"].append(a)
        self.reject(s, "WRITER_CONFLICT")

    def test_unconfirmed_delivery_cannot_be_active(self):
        s = example("initial"); s["assignments"][0]["delivery"] = "uncertain"
        self.reject(s, "DELIVERY_UNCONFIRMED")

    def test_actual_capability_required_before_activation(self):
        s = example("initial"); s["assignments"][0]["required_capabilities"].append("browser")
        self.reject(s, "CAPABILITY_UNCONFIRMED")

    def test_reported_probe_does_not_establish_capability(self):
        s = example("initial"); s["sessions"][2]["probes"][0]["basis"] = "reported"
        self.reject(s, "CAPABILITY_UNCONFIRMED")

    def test_stale_assignment_revision(self):
        s = example("initial"); s["tasks"][0]["revision"] = 2
        self.reject(s, "STALE_ASSIGNMENT")

    def test_own_artifact_cannot_receive_separate_review(self):
        s = example(); s["assessments"][0]["by"] = "builder-2"
        self.reject(s, "AUTHOR_REVIEW")

    def test_inherited_author_lineage_counts(self):
        s = example()
        parent = copy.deepcopy(s["artifacts"][0]); parent.update(id="artifact-parent", assignment_id=None, produced_by=["reviewer-1"], sha256="1" * 64)
        s["artifacts"].append(parent); s["artifacts"][0]["derived_from"] = ["artifact-parent"]
        self.reject(s, "AUTHOR_REVIEW")

    def test_artifact_lineage_cycle(self):
        s = example(); s["artifacts"][0]["derived_from"] = ["artifact-1"]
        self.reject(s, "ARTIFACT_CYCLE")

    def test_changed_candidate_does_not_reuse_old_review(self):
        s = example()
        changed = copy.deepcopy(s["artifacts"][0]); changed.update(id="artifact-2", sha256="2" * 64)
        s["artifacts"].append(changed); s["tasks"][0]["candidate_artifact_id"] = "artifact-2"
        self.reject(s, "INCOMPLETE_CRITERIA")

    def test_reported_pass_is_not_observed_support(self):
        s = example(); s["evidence"][0]["basis"] = "reported"
        self.reject(s, "UNSUPPORTED_VERDICT")

    def test_not_run_cannot_support_pass(self):
        s = example(); s["evidence"][0]["result"] = "NOT_RUN"
        self.reject(s, "UNSUPPORTED_VERDICT")

    def test_positive_witness_required(self):
        s = example(); s["evidence"][0]["witness"] = None
        self.reject(s, "OBSERVATION_WITNESS")

    def test_known_failure_cannot_be_omitted_from_assessment(self):
        s = example()
        failed = copy.deepcopy(s["evidence"][0]); failed.update(id="evidence-fail", result="FAIL")
        s["evidence"].append(failed)
        self.reject(s, "UNRECONCILED_FAILURE")

    def test_corrected_measurement_preserves_failure_history(self):
        s = example()
        failed = copy.deepcopy(s["evidence"][0]); failed.update(id="evidence-fail", result="FAIL")
        correction = copy.deepcopy(s["evidence"][0]); correction.update(id="evidence-corrected", supersedes="evidence-fail")
        s["evidence"] += [failed, correction]
        s["assessments"][0]["evidence_ids"] = ["evidence-corrected"]
        self.assertEqual([], V.validate(s))

    def test_user_use_is_separate_from_technical_check(self):
        s = example(); s["evidence"][1]["kind"] = "inspection"
        self.reject(s, "USER_USE_REQUIRED")

    def test_learning_example_cannot_claim_unobserved_transfer(self):
        s = example("learning-pending"); s["tasks"][0]["state"] = "complete"
        self.reject(s, "INCOMPLETE_CRITERIA")

    def test_acceptance_must_name_current_artifact(self):
        s = example(); s["decisions"][0]["artifact_id"] = None
        self.reject(s, "ACCEPTANCE_REQUIRED")

    def test_acceptance_delegate_needs_authority_reference(self):
        s = example(); s["decisions"][0]["by"] = "oracle-2"
        self.reject(s, "ACCEPTANCE_AUTHORITY")

    def test_append_only_evidence(self):
        before = example(); after = advance(copy.deepcopy(before)); after["evidence"][0]["method"] = "rewritten"
        self.reject(after, "HISTORY_REWRITE", before)

    def test_task_meaning_change_requires_revision(self):
        before = example("initial"); after = advance(copy.deepcopy(before)); after["tasks"][0]["outcome"] = "A different task."
        self.reject(after, "TASK_REVISION", before)

    def test_task_revision_requires_scoped_decision(self):
        before = example("initial"); after = advance(copy.deepcopy(before)); after["tasks"][0]["revision"] = 2
        after["assignments"][0]["status"] = "superseded"
        self.reject(after, "TASK_CHANGE_DECISION", before)

    def test_worker_cutover_needs_activated_handover(self):
        s = example("worker-cutover"); s["handovers"][0]["status"] = "uncertain"
        self.reject(s, "HANDOVER_REQUIRED")

    def test_prepared_or_uncertain_successor_can_wait_without_ownership(self):
        for status in ("prepared", "uncertain"):
            with self.subTest(status=status):
                s = example("worker-cutover")
                s["assignments"][0]["status"] = "active"
                s["assignments"][1].update(status="queued", delivery="prepared")
                s["handovers"][0].update(status=status, cutover_at=None)
                self.assertEqual([], V.validate(s))

    def test_same_chat_can_receive_a_revised_assignment(self):
        before = example("initial"); after = advance(copy.deepcopy(before))
        after["assignments"][0]["status"] = "superseded"
        revised = copy.deepcopy(after["assignments"][0])
        revised.update(id="build-2", generation=2, replaces_assignment_id="build-1", status="active")
        after["assignments"].append(revised)
        self.assertEqual([], V.validate(after, before))

    def test_latest_capability_failure_overrides_earlier_yes(self):
        s = example("initial")
        failed = copy.deepcopy(s["sessions"][2]["probes"][0]); failed["result"] = "no"
        s["sessions"][2]["probes"].append(failed)
        self.reject(s, "CAPABILITY_UNCONFIRMED")

    def test_old_writer_must_be_reconciled(self):
        s = example("worker-cutover"); s["assignments"][0]["status"] = "active"
        self.reject(s, "HANDOVER_OLD_ACTIVE")

    def test_oracle_cutover_adopts_continuing_work(self):
        before, after = example("worker-cutover"), example("oracle-cutover")
        after["handovers"][-1]["adopted_assignment_ids"] = []
        self.reject(after, "ORACLE_ADOPTION", before)

    def test_two_active_oracles_are_rejected(self):
        s = example("oracle-cutover"); s["sessions"][1]["lifecycle"] = "active"
        self.reject(s, "ORACLE_BINDING")

    def test_oracle_epoch_cannot_jump(self):
        s = example("oracle-cutover"); s["control"]["epoch"] = 5
        self.reject(s, "ORACLE_EPOCH_CHAIN")

    def test_superseded_assignment_cannot_reclaim_candidate(self):
        s = example(); s["assignments"][1]["status"] = "superseded"
        self.reject(s, "LATE_RETURN")

    def test_state_revision_conflict(self):
        before = example("initial"); after = advance(advance(copy.deepcopy(before)))
        self.reject(after, "REVISION_CONFLICT", before)

    def test_command_replay_and_stale_epoch(self):
        before, after = example("oracle-cutover"), example()
        path = ROOT / "examples/completed.json"
        cmd = V.load(ROOT / "examples/completed.command.json")
        for field, value, code in (("command_id", "command-3", "COMMAND_REPLAY"), ("expected_oracle_epoch", 1, "COMMAND_EPOCH"), ("actor", "oracle-1", "COMMAND_ACTOR")):
            with self.subTest(field=field):
                altered = copy.deepcopy(cmd); altered[field] = value
                self.assertTrue(any(e.startswith(code + ":") for e in V.validate_command(altered, before, after, path.read_bytes())))

    def test_command_digest_binds_exact_bytes(self):
        before, after = example("oracle-cutover"), example()
        cmd = V.load(ROOT / "examples/completed.command.json")
        errors = V.validate_command(cmd, before, after, b"changed bytes")
        self.assertTrue(any(e.startswith("COMMAND_DIGEST:") for e in errors))

    def test_hash_mismatch_and_escape(self):
        s = example(); s["artifacts"][0]["sha256"] = "0" * 64
        self.reject(s, "ARTIFACT_HASH", artifact_root=ROOT / "examples")
        s["artifacts"][0]["locator"] = "../validate.py"
        self.reject(s, "ARTIFACT_PATH", artifact_root=ROOT / "examples")

    def test_schema_does_not_authenticate_a_declared_witness(self):
        s = example()
        s["evidence"][0]["witness"]["locator"] = "OWNER_PRIVATE_REF:unverified-reference"
        self.assertEqual([], V.validate(s))  # Explicit limit: the reference must be verified outside this checker.


if __name__ == "__main__":
    unittest.main()
