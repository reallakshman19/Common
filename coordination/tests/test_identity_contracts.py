"""
Unit Tests for Control Tower v3 Identity Contracts & Invariants
"""

import unittest
from coordination.contracts import (
    Project, Work, ExecutionLane, AgentAssignment, AgentRun,
    TabBinding, TaskEvidence, CoordinatorObservation, ControlTowerRegistry
)


class TestIdentityContracts(unittest.TestCase):

    def setUp(self):
        self.reg = ControlTowerRegistry()
        self.proj = Project(
            project_id="reallakshman19/Common",
            name="Common",
            repo_url="https://github.com/reallakshman19/Common",
            coordination_dir="coordination",
            status="ACTIVE",
            as_of="2026-10-12T16:00:00Z",
            provider_reachability="REACHABLE"
        )
        self.reg.register_project(self.proj)

        self.work = Work(
            work_id="work-common-182",
            project_id="reallakshman19/Common",
            aim_id="AIM-COMMON-CORE-V1",
            label_sha="a1b2c3d4e5f60718293a4b5c6d7e8f901a2b3c4d",
            issue_ref="https://github.com/reallakshman19/Common/issues/182",
            acceptance_status="IN_PROGRESS"
        )
        self.reg.register_work(self.work)

        self.lane = ExecutionLane(
            lane_id="work-common-182/lane/dev",
            work_id="work-common-182",
            lane_type="DEVELOPMENT",
            active_binding_policy="ONE_ACTIVE_TAB_DEFAULT"
        )
        self.reg.register_lane(self.lane)

        self.assign = AgentAssignment(
            assignment_id="work-common-182/lane/dev/assign/g1",
            lane_id="work-common-182/lane/dev",
            responsibility_id="RESP-DEV-01",
            assigned_role="PRIMARY_IMPLEMENTER",
            status="ACTIVE"
        )
        self.reg.register_assignment(self.assign)

    def test_project_validation_rejects_empty_id(self):
        with self.assertRaises(ValueError):
            p = Project(
                project_id="",
                name="Empty",
                repo_url="https://github.com/test/test",
                coordination_dir=".",
                status="ACTIVE",
                as_of="2026-10-12T00:00:00Z",
                provider_reachability="REACHABLE"
            )
            p.validate()

    def test_work_validation_rejects_invalid_label_sha(self):
        with self.assertRaises(ValueError):
            w = Work(
                work_id="work-bad",
                project_id="reallakshman19/Common",
                aim_id="AIM-1",
                label_sha="short_sha",  # not 40-char hex
                issue_ref="https://github.com/reallakshman19/Common/issues/182",
                acceptance_status="IN_PROGRESS"
            )
            w.validate()

    def test_real_aim_label_sha_is_accepted(self):
        # relay/AIM/3DC-XML-CII.yaml currently says label_sha: 5f9065d.
        w = Work(work_id="work-real-aim", project_id=self.proj.project_id,
                 aim_id="3DC-XML-CII", label_sha="5f9065d",
                 issue_ref="https://github.com/reallakshman19/3D_Converters/issues/212",
                 acceptance_status="IN_PROGRESS")
        w.validate()

    def test_foreign_key_integrity(self):
        orphan_work = Work(
            work_id="work-orphan",
            project_id="nonexistent-project",
            aim_id="AIM-1",
            label_sha="a1b2c3d4e5f60718293a4b5c6d7e8f901a2b3c4d",
            issue_ref="https://github.com/reallakshman19/Common/issues/1",
            acceptance_status="IN_PROGRESS"
        )
        with self.assertRaises(KeyError):
            self.reg.register_work(orphan_work)

    def test_handover_carry_preserves_assignment_and_resets_meter(self):
        # Initial run (generation 1)
        run1 = AgentRun(
            run_id="work-common-182/lane/dev/assign/g1/run/1",
            assignment_id="work-common-182/lane/dev/assign/g1",
            generation=1,
            chat_id="chat-initial-guid",
            meter_started_at="2026-10-12T10:00:00Z",
            evidence_cadence_count=3,
            run_state="IN_PROGRESS"
        )
        self.reg.register_run(run1)

        b1 = TabBinding(
            binding_id="bind-run1",
            run_id=run1.run_id,
            project_id="reallakshman19/Common",
            tab_alias="Tab1",
            generation=1,
            binding_state="ACTIVE"
        )
        self.reg.register_binding(b1)

        # Execute carry transition
        run2 = self.reg.perform_handover_carry(
            assignment_id="work-common-182/lane/dev/assign/g1",
            new_chat_id="chat-successor-guid",
            new_tab_alias="Tab2",
            project_id="reallakshman19/Common"
        )

        # Assertions
        self.assertEqual(run2.generation, 2)
        self.assertEqual(run2.assignment_id, "work-common-182/lane/dev/assign/g1")  # preserved
        self.assertEqual(run2.predecessor_run_id, run1.run_id)
        self.assertEqual(run2.evidence_cadence_count, 3)  # carried forward
        self.assertNotEqual(run2.meter_started_at, run1.meter_started_at)  # fresh meter
        self.assertEqual(run1.run_state, "SUPERSEDED")  # custody transfer does not prove task completion

        # Check binding states: run1 binding is HISTORICAL, run2 binding is ACTIVE
        self.assertEqual(b1.binding_state, "HISTORICAL")
        active_bindings = [b for b in self.reg.bindings.values() if b.binding_state == "ACTIVE"]
        self.assertEqual(len(active_bindings), 1)
        self.assertEqual(active_bindings[0].tab_alias, "Tab2")

    def test_single_active_tab_invariant_detects_conflict(self):
        # Create run 1
        r1 = AgentRun(
            run_id="work-common-182/lane/dev/assign/g1/run/1",
            assignment_id="work-common-182/lane/dev/assign/g1",
            generation=1,
            chat_id="chat-1",
            meter_started_at="2026-10-12T10:00:00Z",
            evidence_cadence_count=0,
            run_state="IN_PROGRESS"
        )
        self.reg.register_run(r1)

        # Register TWO ACTIVE bindings for the same Work
        b1 = TabBinding(
            binding_id="bind-tab1",
            run_id=r1.run_id,
            project_id="reallakshman19/Common",
            tab_alias="Tab1",
            generation=1,
            binding_state="ACTIVE"
        )
        b2 = TabBinding(
            binding_id="bind-tab2",
            run_id=r1.run_id,
            project_id="reallakshman19/Common",
            tab_alias="Tab2",
            generation=1,
            binding_state="ACTIVE"
        )
        self.reg.register_binding(b1)
        self.reg.register_binding(b2)

        # Check invariant
        conflicts = self.reg.validate_single_active_tab_invariants()
        self.assertEqual(len(conflicts), 1)
        self.assertIn("IDENTITY_CONFLICT", conflicts[0])

        # Assert states updated
        self.assertEqual(b1.binding_state, "IDENTITY_CONFLICT")
        self.assertEqual(b2.binding_state, "IDENTITY_CONFLICT")
        self.assertEqual(self.work.acceptance_status, "IN_PROGRESS")  # runtime conflict cannot decide Owner acceptance


    def test_cross_project_binding_must_match_assignment(self):
        other = Project(project_id="other", name="Other", repo_url="https://github.com/example/other",
                        coordination_dir="other", status="ACTIVE", as_of="2026-10-12T00:00:00Z",
                        provider_reachability="REACHABLE")
        self.reg.register_project(other)
        run = AgentRun(run_id="run-1", assignment_id=self.assign.assignment_id,
                       generation=1, chat_id="chat1", meter_started_at="2026-10-12T00:00:00Z",
                       evidence_cadence_count=0, run_state="IN_PROGRESS")
        self.reg.register_run(run)
        with self.assertRaises(ValueError):
            self.reg.register_binding(TabBinding(binding_id="wrong", run_id="run-1", project_id="other",
                                                tab_alias="Tab3", generation=1, binding_state="ACTIVE"))

    def test_duplicate_evidence_replay_is_idempotent(self):
        evidence = TaskEvidence(evidence_id="source-comment-1", work_id=self.work.work_id,
                                task_id="task-1", candidate_sha="a"*40, proof_digest="f"*64,
                                validator_verdict="PASS", is_canonical=True)
        self.reg.register_evidence(evidence)
        self.reg.register_evidence(evidence)
        self.assertEqual(len(self.reg.evidence_history), 1)
        updated = TaskEvidence(evidence_id=evidence.evidence_id, work_id=self.work.work_id,
                               task_id="task-1", candidate_sha="a"*40, proof_digest="e"*64,
                               validator_verdict="PASS", is_canonical=True)
        self.reg.register_evidence(updated)
        self.assertEqual(len(self.reg.evidence_history), 2)
        self.assertEqual(self.reg.evidence[evidence.evidence_id].proof_digest, "e"*64)

    def test_recovery_carry_does_not_claim_success(self):
        run = AgentRun(run_id="run-1", assignment_id=self.assign.assignment_id,
                       generation=1, chat_id="old-chat", meter_started_at="2026-10-12T00:00:00Z",
                       evidence_cadence_count=2, run_state="IN_PROGRESS")
        self.reg.register_run(run)
        successor = self.reg.perform_handover_carry(
            self.assign.assignment_id, "new-chat", "Tab5", self.proj.project_id, "RECOVERY")
        self.assertEqual(run.run_state, "INTERRUPTED")
        self.assertEqual(successor.predecessor_run_id, run.run_id)
        self.assertEqual(successor.evidence_cadence_count, 2)

    def test_duplicate_work_id_across_projects_is_rejected(self):
        other = Project(project_id="other", name="Other", repo_url="https://github.com/example/other",
                        coordination_dir="other", status="ACTIVE", as_of="2026-10-12T00:00:00Z",
                        provider_reachability="REACHABLE")
        self.reg.register_project(other)
        duplicate = Work(work_id=self.work.work_id, project_id="other", aim_id="OTHER",
                         label_sha="a"*40, issue_ref="https://github.com/example/other/issues/1",
                         acceptance_status="IN_PROGRESS")
        with self.assertRaises(ValueError):
            self.reg.register_work(duplicate)

    def test_invalid_predecessor_cannot_be_registered(self):
        bad = AgentRun(run_id="run-2", assignment_id=self.assign.assignment_id,
                       generation=2, chat_id="new", meter_started_at="2026-10-12T00:00:00Z",
                       evidence_cadence_count=0, run_state="IN_PROGRESS",
                       predecessor_run_id="missing-run")
        with self.assertRaises(ValueError):
            self.reg.register_run(bad)


if __name__ == "__main__":
    unittest.main()
