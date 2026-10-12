"""
Control Tower v3 Identity Contracts & Validation Engine
========================================================
Implements the 5-tier identity model:
Project -> Work -> ExecutionLane -> AgentAssignment -> AgentRun
with ephemeral TabBinding, immutable TaskEvidence, and CoordinatorObservation.
Enforces v3.28 invariants:
- At most 1 ACTIVE tab binding per Work
- Handover continuity with per-run meter reset
- Cross-project entity isolation
- Exact-head CI validation
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import json
import re
from pathlib import Path


@dataclass
class Project:
    project_id: str
    name: str
    repo_url: str
    coordination_dir: str
    status: str  # ACTIVE, DEGRADED, UNAVAILABLE
    as_of: str
    provider_reachability: str  # REACHABLE, UNAVAILABLE, RATE_LIMITED, FORBIDDEN

    def validate(self):
        if not self.project_id or not self.project_id.strip():
            raise ValueError("project_id cannot be empty")
        if self.status not in ("ACTIVE", "DEGRADED", "UNAVAILABLE"):
            raise ValueError(f"Invalid project status: {self.status}")
        if self.provider_reachability not in ("REACHABLE", "UNAVAILABLE", "RATE_LIMITED", "FORBIDDEN"):
            raise ValueError(f"Invalid provider_reachability: {self.provider_reachability}")


@dataclass
class Work:
    work_id: str
    project_id: str
    aim_id: str
    label_sha: str
    issue_ref: str
    acceptance_status: str  # NOT_STARTED, IN_PROGRESS, ACCEPTED, REJECTED, HOLD
    candidate_pr_ref: Optional[str] = None
    candidate_head_sha: Optional[str] = None

    def validate(self):
        if not self.work_id:
            raise ValueError("work_id cannot be empty")
        if not re.match(r"^[0-9a-fA-F]{40}$", self.label_sha):
            raise ValueError(f"label_sha must be exactly 40-char hex, got {self.label_sha}")
        if self.acceptance_status not in ("NOT_STARTED", "IN_PROGRESS", "ACCEPTED", "REJECTED", "HOLD"):
            raise ValueError(f"Invalid acceptance_status: {self.acceptance_status}")


@dataclass
class ExecutionLane:
    lane_id: str
    work_id: str
    lane_type: str  # DEVELOPMENT, REVIEW, RECOVERY, ASSESSMENT
    active_binding_policy: str = "ONE_ACTIVE_TAB_DEFAULT"

    def validate(self):
        if self.lane_type not in ("DEVELOPMENT", "REVIEW", "RECOVERY", "ASSESSMENT"):
            raise ValueError(f"Invalid lane_type: {self.lane_type}")
        if self.active_binding_policy != "ONE_ACTIVE_TAB_DEFAULT":
            raise ValueError("active_binding_policy must be ONE_ACTIVE_TAB_DEFAULT")


@dataclass
class AgentAssignment:
    assignment_id: str
    lane_id: str
    responsibility_id: str
    assigned_role: str  # PRIMARY_IMPLEMENTER, REVIEWER, ORACLE
    status: str  # ACTIVE, STALE, COMPLETED, HELD

    def validate(self):
        if self.assigned_role not in ("PRIMARY_IMPLEMENTER", "REVIEWER", "ORACLE"):
            raise ValueError(f"Invalid assigned_role: {self.assigned_role}")
        if self.status not in ("ACTIVE", "STALE", "COMPLETED", "HELD"):
            raise ValueError(f"Invalid assignment status: {self.status}")


@dataclass
class AgentRun:
    run_id: str
    assignment_id: str
    generation: int
    chat_id: str
    meter_started_at: str
    evidence_cadence_count: int
    run_state: str  # IN_PROGRESS, SUCCEEDED, FAILED, STALE, TIMED_OUT, SUPERSEDED, INTERRUPTED
    predecessor_run_id: Optional[str] = None

    def validate(self):
        if self.generation < 1:
            raise ValueError("generation must be >= 1")
        if self.generation > 1 and not self.predecessor_run_id:
            raise ValueError("predecessor_run_id is required for generation > 1")
        if self.evidence_cadence_count < 0:
            raise ValueError("evidence_cadence_count cannot be negative")
        if self.run_state not in ("IN_PROGRESS", "SUCCEEDED", "FAILED", "STALE", "TIMED_OUT", "SUPERSEDED", "INTERRUPTED"):
            raise ValueError(f"Invalid run_state: {self.run_state}")


@dataclass
class TabBinding:
    binding_id: str
    run_id: str
    project_id: str
    tab_alias: str
    generation: int
    binding_state: str  # ACTIVE, HISTORICAL, IDENTITY_CONFLICT
    session_alias: Optional[str] = None

    def validate(self):
        if self.binding_state not in ("ACTIVE", "HISTORICAL", "IDENTITY_CONFLICT"):
            raise ValueError(f"Invalid binding_state: {self.binding_state}")


@dataclass
class TaskEvidence:
    evidence_id: str
    work_id: str
    task_id: str
    candidate_sha: str
    proof_digest: str
    validator_verdict: str  # PASS, FAIL, NOT_RUN, INVALID
    is_canonical: bool
    source_ref: Optional[str] = None

    def validate(self):
        if not re.match(r"^[0-9a-fA-F]{40}$", self.candidate_sha):
            raise ValueError(f"candidate_sha must be 40-char hex: {self.candidate_sha}")
        if not re.match(r"^[0-9a-fA-F]{64}$", self.proof_digest):
            raise ValueError(f"proof_digest must be 64-char hex: {self.proof_digest}")
        if self.validator_verdict not in ("PASS", "FAIL", "NOT_RUN", "INVALID"):
            raise ValueError(f"Invalid validator_verdict: {self.validator_verdict}")


@dataclass
class CoordinatorObservation:
    tab: str
    status: str
    aim: str
    plan: str
    ac: str
    ci: str
    meter: str
    due: str
    checked: str
    next: str
    observed_at: str
    coordinator_liveness: str  # ALIVE, STALE, STOPPED

    def validate(self):
        if self.coordinator_liveness not in ("ALIVE", "STALE", "STOPPED"):
            raise ValueError(f"Invalid coordinator_liveness: {self.coordinator_liveness}")


class ControlTowerRegistry:
    """Manages and validates identity invariants across multiple projects."""

    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.works: Dict[str, Work] = {}
        self.lanes: Dict[str, ExecutionLane] = {}
        self.assignments: Dict[str, AgentAssignment] = {}
        self.runs: Dict[str, AgentRun] = {}
        self.bindings: Dict[str, TabBinding] = {}
        self.evidence: Dict[str, TaskEvidence] = {}
        self.evidence_history: List[TaskEvidence] = []

    def register_project(self, p: Project):
        p.validate()
        if p.project_id in self.projects:
            raise ValueError(f"Duplicate project_id: {p.project_id}")
        self.projects[p.project_id] = p

    def register_work(self, w: Work):
        w.validate()
        if w.project_id not in self.projects:
            raise KeyError(f"Foreign key violation: project_id {w.project_id} does not exist")
        if w.work_id in self.works:
            raise ValueError(f"Duplicate work_id: {w.work_id}")
        self.works[w.work_id] = w

    def register_lane(self, l: ExecutionLane):
        l.validate()
        if l.work_id not in self.works:
            raise KeyError(f"Foreign key violation: work_id {l.work_id} does not exist")
        if l.lane_id in self.lanes:
            raise ValueError(f"Duplicate lane_id: {l.lane_id}")
        self.lanes[l.lane_id] = l

    def register_assignment(self, a: AgentAssignment):
        a.validate()
        if a.lane_id not in self.lanes:
            raise KeyError(f"Foreign key violation: lane_id {a.lane_id} does not exist")
        if a.assignment_id in self.assignments:
            raise ValueError(f"Duplicate assignment_id: {a.assignment_id}")
        self.assignments[a.assignment_id] = a

    def register_run(self, r: AgentRun):
        r.validate()
        if r.assignment_id not in self.assignments:
            raise KeyError(f"Foreign key violation: assignment_id {r.assignment_id} does not exist")
        if r.run_id in self.runs:
            raise ValueError(f"Duplicate run_id: {r.run_id}")
        if r.predecessor_run_id:
            prev = self.runs.get(r.predecessor_run_id)
            if not prev or prev.assignment_id != r.assignment_id or prev.generation + 1 != r.generation:
                raise ValueError("Invalid predecessor run or generation")
        self.runs[r.run_id] = r

    def register_binding(self, b: TabBinding):
        b.validate()
        if b.run_id not in self.runs:
            raise KeyError(f"Foreign key violation: run_id {b.run_id} does not exist")
        if b.project_id not in self.projects:
            raise KeyError(f"Foreign key violation: project_id {b.project_id} does not exist")
        run = self.runs[b.run_id]
        assignment = self.assignments[run.assignment_id]
        lane = self.lanes[assignment.lane_id]
        work = self.works[lane.work_id]
        if b.project_id != work.project_id or b.generation != run.generation:
            raise ValueError("Binding project/generation mismatch")
        if b.binding_id in self.bindings:
            raise ValueError(f"Duplicate binding_id: {b.binding_id}")
        self.bindings[b.binding_id] = b

    def register_evidence(self, e: TaskEvidence):
        e.validate()
        if e.work_id not in self.works:
            raise KeyError(f"Foreign key violation: work_id {e.work_id} does not exist")
        # Idempotent replay: record in immutable history, keep canonical version
        if self.evidence.get(e.evidence_id) == e:
            return  # identical provider revision is idempotent
        self.evidence_history.append(e)
        self.evidence[e.evidence_id] = e

    def resolve_work_for_binding(self, binding_id: str) -> Optional[Work]:
        b = self.bindings.get(binding_id)
        if not b:
            return None
        run = self.runs.get(b.run_id)
        if not run:
            return None
        assign = self.assignments.get(run.assignment_id)
        if not assign:
            return None
        lane = self.lanes.get(assign.lane_id)
        if not lane:
            return None
        return self.works.get(lane.work_id)

    def validate_single_active_tab_invariants(self) -> List[str]:
        """
        Enforces v3.28 invariant: At most one ACTIVE tab binding per Work.
        Returns list of conflict messages.
        """
        conflicts = []
        work_active_bindings: Dict[str, List[TabBinding]] = {}
        for b in self.bindings.values():
            if b.binding_state == "ACTIVE":
                work = self.resolve_work_for_binding(b.binding_id)
                if work:
                    work_active_bindings.setdefault(work.work_id, []).append(b)

        for work_id, active_list in work_active_bindings.items():
            if len(active_list) > 1:
                # Conflict detected!
                for b in active_list:
                    b.binding_state = "IDENTITY_CONFLICT"
                # Runtime conflicts cannot mutate Owner acceptance.
                msg = f"IDENTITY_CONFLICT: Work {work_id} has {len(active_list)} simultaneous active tab bindings."
                conflicts.append(msg)

        return conflicts

    def perform_handover_carry(self, assignment_id: str, new_chat_id: str, new_tab_alias: str, project_id: str, handover_kind: str = "NORMAL") -> AgentRun:
        """
        Models watch.ps1 -Action carry:
        - Assignment preserved
        - New run with generation incremented
        - Meter reset (meter_started_at fresh)
        - Evidence cadence count carried forward
        - Predecessor run marked historical
        """
        if handover_kind not in ("NORMAL", "RECOVERY"):
            raise ValueError("Invalid handover kind")
        assign = self.assignments[assignment_id]
        work = self.works[self.lanes[assign.lane_id].work_id]
        if work.project_id != project_id:
            raise ValueError("Handover cannot cross project boundary")
        if not new_chat_id.strip():
            raise ValueError("Missing successor chat")
        # Find latest run
        runs = [r for r in self.runs.values() if r.assignment_id == assignment_id]
        runs.sort(key=lambda x: x.generation, reverse=True)
        latest_run = runs[0] if runs else None

        gen = (latest_run.generation + 1) if latest_run else 1
        carried_count = latest_run.evidence_cadence_count if latest_run else 0
        if latest_run:
            if new_chat_id == latest_run.chat_id:
                raise ValueError("Successor chat must differ from predecessor")
            if latest_run.run_state == "IN_PROGRESS":
                latest_run.run_state = "INTERRUPTED" if handover_kind == "RECOVERY" else "SUPERSEDED"

        new_run = AgentRun(
            run_id=f"{assignment_id}/run/{gen}",
            assignment_id=assignment_id,
            generation=gen,
            chat_id=new_chat_id,
            meter_started_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            evidence_cadence_count=carried_count,
            run_state="IN_PROGRESS",
            predecessor_run_id=latest_run.run_id if latest_run else None,
        )
        self.register_run(new_run)

        # Deactivate old bindings for this assignment
        for b in self.bindings.values():
            if latest_run and b.run_id == latest_run.run_id and b.binding_state == "ACTIVE":
                b.binding_state = "HISTORICAL"

        # Bind new tab
        new_binding = TabBinding(
            binding_id=f"bind-{new_run.run_id.replace('/', '-')}",
            run_id=new_run.run_id,
            project_id=project_id,
            tab_alias=new_tab_alias,
            generation=gen,
            binding_state="ACTIVE",
        )
        self.register_binding(new_binding)
        return new_run
