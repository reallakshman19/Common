from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests"
for entry in (SCRIPTS, TESTS):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from material_basis import inspect as inspect_material_basis
from plan_handover import plan_handover
from relay_tx import (
    accept_checkpoint,
    activate_lease,
    admit_task,
    close_task,
    export_local_execution,
    publish_handover,
    publish_buddy_markdown,
    release_lease,
    renew_lease,
    reconcile_roadmap,
    resolve_control,
    sync_delivery,
)
from snapshot_projection import build as build_snapshot
from test_handover_context import (
    install_parent_issue,
    install_standalone,
    parent_issue_observation,
    target_observation,
)
from test_relay_can import prepare_git
from test_v3_foundation import base_objects, dump
from transactionlib import TransactionError, execute, recover_all, yaml_bytes
from v3lib import load_events, load_yaml
from validate_foundation import validate, validate_authority


def add_open_control(root: Path) -> None:
    path = root / "relay/CONTROLS/controls.yaml"
    controls = yaml.safe_load(path.read_text(encoding="utf-8"))
    controls["controls"].append({
        "id": "CTRL-TEST-001",
        "kind": "DELIVERY",
        "state": "OPEN",
        "source": {"type": "VALIDATOR", "ref": "synthetic"},
        "condition": "Synthetic delivery obligation.",
        "blocks": ["PR_READY"],
        "permits": ["MATERIAL_WRITE"],
        "resolution": {"condition": "Evidence supplied.", "evidence": []},
    })
    dump(path, controls)


def accept_current_checkpoint_and_reconcile(root: Path, base_ref: str) -> None:
    _, _, _, _, template, *_ = base_objects()
    checkpoint = copy.deepcopy(template)
    checkpoint["id"] = "CP-TA-011"
    checkpoint["ep"] = "EP-TA-011"
    ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
    current_material = inspect_material_basis(root, ep, base_ref)["material_basis"]
    checkpoint["material_result"] = {
        "head": current_material["head"],
        "relevant_paths_digest": current_material["relevant_paths_digest"],
        "dependency_digest": current_material["dependency_digest"],
    }
    incoming = root / "close-checkpoint.yaml"
    dump(incoming, checkpoint)
    accept_checkpoint(
        root,
        tx_id="TX-CLOSE-CP",
        event_id="EVT-CLOSE-CP",
        actor="agent-x",
        checkpoint_path=incoming,
        base_ref=base_ref,
    )

    state = load_yaml(root / "relay/STATE.yaml")
    roadmap_path = root / str((state.get("roadmap") or {}).get("path"))
    roadmap = load_yaml(roadmap_path)
    reconciliation = {
        "schema_version": "relay-v3.1-roadmap-reconciliation",
        "authority": "PROPOSED_RECONCILIATION",
        "expected_revision": roadmap["revision"],
        "disposition": "NO_CHANGE",
        "basis": ["Current EP acceptance is complete; no concept change is required."],
        "roadmap_after": roadmap,
    }
    reconciliation_path = root / "close-roadmap-reconciliation.yaml"
    dump(reconciliation_path, reconciliation)
    reconcile_roadmap(
        root,
        tx_id="TX-CLOSE-ROADMAP",
        event_id="EVT-CLOSE-ROADMAP",
        actor="agent-x",
        reconciliation_path=reconciliation_path,
        base_ref=base_ref,
    )


def configure_delivery(root: Path, base_ref: str, *, lifecycle: str = "MERGED") -> Path:
    state_path = root / "relay/STATE.yaml"
    state = load_yaml(state_path)
    state["delivery"] = {
        "required": True,
        "primary_vehicle": {"provider": "GITHUB", "kind": "PULL_REQUEST", "number": 419},
    }
    dump(state_path, state)
    dump(root / "relay/GENERATED/CURRENT_SNAPSHOT.yaml", build_snapshot(root, base_ref))
    observation = {
        "schema_version": "relay-v3.1-delivery-status",
        "authority": "PROVIDER_READBACK",
        "vehicle": {"provider": "GITHUB", "kind": "PULL_REQUEST", "number": 419},
        "observed_at": "2026-09-22T03:57:35Z",
        "provider_ref": "github:reallaksh19/Common#419",
        "lifecycle": lifecycle,
        "checks": "PASS",
        "review": "APPROVED",
        "mergeability": "MERGEABLE",
    }
    path = root / "provider-observation.yaml"
    dump(path, observation)
    return path


class RelayTransactionalCommandTests(unittest.TestCase):
    def test_different_executor_is_recorded_as_recovery_without_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            result = activate_lease(
                root,
                tx_id="TX-TAKEOVER-RECORDER",
                event_id="EVT-TAKEOVER-RECORDER",
                lease_id="LEASE-TA-011-02",
                executor_id="agent-y",
                actor="agent-y",
                method="DETERMINISTIC",
                qualification=None,
                owner_basis=None,
                branch=None,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            old = load_yaml(root / "relay/LEASES/LEASE-TA-011-01.yaml")
            self.assertEqual("INVALIDATED", old["state"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            started = [row for row in events if row["type"] == "RECOVERY_STARTED"][-1]
            self.assertEqual("RECORDER_EXPLICIT_TAKEOVER", started["details"]["recovery_reason"])

    def test_explicit_recovery_takeover_invalidates_abandoned_lease_and_keeps_same_ep(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            result = activate_lease(
                root,
                tx_id="TX-TAKEOVER-RECOVERY",
                event_id="EVT-TAKEOVER-RECOVERY",
                lease_id="LEASE-TA-011-02",
                executor_id="agent-y",
                actor="agent-y",
                method="DETERMINISTIC",
                qualification=None,
                owner_basis=None,
                branch=None,
                base_ref=base_ref,
                recovery_takeover=True,
            )
            self.assertEqual("COMMITTED", result["status"])
            state = load_yaml(root / "relay/STATE.yaml")
            old_lease = load_yaml(root / "relay/LEASES/LEASE-TA-011-01.yaml")
            new_lease = load_yaml(root / "relay/LEASES/LEASE-TA-011-02.yaml")
            self.assertEqual("EP-TA-011", state["execution"]["ep"])
            self.assertEqual("LEASE-TA-011-02", state["execution"]["lease"])
            self.assertEqual("INVALIDATED", old_lease["state"])
            self.assertIn("RECOVERY_TAKEOVER_BY:LEASE-TA-011-02", old_lease["invalidation"]["reasons"])
            self.assertEqual("ACTIVE", new_lease["state"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            revoked = [item for item in events if item["event_id"] == "EVT-TAKEOVER-RECOVERY-REL"][0]
            granted = [item for item in events if item["event_id"] == "EVT-TAKEOVER-RECOVERY"][0]
            self.assertEqual("LEASE_REVOKED", revoked["type"])
            self.assertEqual("RECOVERY", revoked["details"]["continuation"])
            self.assertEqual("RECOVERY", granted["details"]["continuation"])

    def test_recovery_records_completed_parent_context_without_blocking_takeover(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            baseline = install_parent_issue(root, number=1771)
            closed = parent_issue_observation(
                baseline=baseline,
                number=1771,
                state="CLOSED",
                disposition="CLOSE",
                acceptance_state="COMPLETE",
            )

            result = activate_lease(
                root,
                tx_id="TX-RECOVERY-STALE-PARENT",
                event_id="EVT-RECOVERY-STALE-PARENT",
                lease_id="LEASE-TA-011-02",
                executor_id="agent-y",
                actor="agent-y",
                method="DETERMINISTIC",
                qualification=None,
                owner_basis=None,
                branch=None,
                base_ref=base_ref,
                recovery_takeover=True,
                programme_issue_observations=[closed],
            )
            self.assertEqual("COMMITTED", result["status"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            started = [row for row in events if row["type"] == "RECOVERY_STARTED"][-1]
            self.assertEqual("RECORDER_EXPLICIT_TAKEOVER", started["details"]["recovery_reason"])

    def test_recovery_can_resume_only_when_parent_remains_in_programme_frontier(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            baseline = install_parent_issue(root, number=1771)
            live = parent_issue_observation(
                baseline=baseline,
                number=1771,
                state="OPEN",
                disposition="NO_CHANGE",
                acceptance_state="PENDING",
            )

            result = activate_lease(
                root,
                tx_id="TX-RECOVERY-LIVE-PARENT",
                event_id="EVT-RECOVERY-LIVE-PARENT",
                lease_id="LEASE-TA-011-02",
                executor_id="agent-y",
                actor="agent-y",
                method="DETERMINISTIC",
                qualification=None,
                owner_basis=None,
                branch=None,
                base_ref=base_ref,
                recovery_takeover=True,
                programme_issue_observations=[live],
            )
            self.assertEqual("COMMITTED", result["status"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            started = [row for row in events if row["type"] == "RECOVERY_STARTED"][-1]
            self.assertEqual(
                ["example/project#1771"],
                started["details"]["programme_frontier"],
            )

    def test_handoff_release_records_missing_handover_as_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            result = release_lease(
                root,
                tx_id="TX-RELEASE-NO-HANDOVER",
                event_id="EVT-RELEASE-NO-HANDOVER",
                actor="agent-x",
                reason="HANDOFF",
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            released = [row for row in events if row["type"] == "LEASE_RELEASED"][-1]
            self.assertIn("RECORDER_ADVISORY:NO_FRESH_HANDOVER", released["basis"])

    def test_admit_task_atomically_moves_idle_repository_to_active_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            release_lease(
                root,
                tx_id="TX-RELEASE-BEFORE-ADMIT",
                event_id="EVT-RELEASE-BEFORE-ADMIT",
                actor="agent-x",
                reason="ADMINISTRATIVE",
            )

            roadmap_path = root / "relay/ROADMAP/ROADMAP.yaml"
            roadmap = load_yaml(roadmap_path)
            roadmap["work_packages"].append({
                "id": "WP-OTHER-ACTIVE",
                "title": "Separate unfinished programme obligation",
                "weight": 10,
                "state": "ACTIVE",
                "depends_on": [],
            })
            dump(roadmap_path, roadmap)

            source_ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
            new_ep = copy.deepcopy(source_ep)
            new_ep["id"] = "EP-TA-012"
            request = {
                "schema_version": "relay-v3.1-task-admission",
                "roadmap": {
                    "disposition": "MAPPED_EXISTING_WP",
                    "new_revision": "RM-0013",
                    "basis": ["Owner selected the next bounded task."],
                    "work_package": {
                        "id": "WP-TA-109",
                        "title": "Current work",
                        "weight": 50,
                        "state": "ACTIVE",
                        "depends_on": ["WP-TA-108"],
                    },
                },
                "ep": new_ep,
                "lease": {
                    "id": "LEASE-TA-012-01",
                    "executor_id": "agent-z",
                    "method": "DETERMINISTIC",
                },
                "delivery": {"required": False, "primary_vehicle": None},
            }
            request_path = root / "task-admission.yaml"
            dump(request_path, request)
            result = admit_task(
                root,
                tx_id="TX-ADMIT-001",
                event_id="EVT-ADMIT-001",
                actor="owner",
                admission_path=request_path,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            state = load_yaml(root / "relay/STATE.yaml")
            self.assertEqual("ACTIVE", state["execution"]["lifecycle"])
            self.assertEqual("EP-TA-012", state["execution"]["ep"])
            self.assertEqual("LEASE-TA-012-01", state["execution"]["lease"])
            self.assertEqual("RM-0013", state["roadmap"]["revision"])
            admitted_roadmap = load_yaml(root / "relay/ROADMAP/ROADMAP.yaml")
            self.assertEqual(
                {"WP-TA-109", "WP-OTHER-ACTIVE"},
                {
                    item["id"]
                    for item in admitted_roadmap["work_packages"]
                    if item["state"] == "ACTIVE"
                },
            )
            self.assertTrue((root / "relay/WORK/EP-TA-012.yaml").exists())
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            ids = {row["event_id"] for row in events}
            self.assertTrue({"EVT-ADMIT-001-OWNER", "EVT-ADMIT-001-EP", "EVT-ADMIT-001-LEASE"}.issubset(ids))
            self.assertEqual([], validate(root))

    def test_provider_backed_admission_can_allocate_execution_identities(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            baseline = install_parent_issue(root, number=1771)
            release_lease(
                root,
                tx_id="TX-RELEASE-BEFORE-CANONICAL-ADMIT",
                event_id="EVT-RELEASE-BEFORE-CANONICAL-ADMIT",
                actor="agent-x",
                reason="ADMINISTRATIVE",
            )

            source_ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
            new_ep = copy.deepcopy(source_ep)
            new_ep.pop("id", None)
            request = {
                "schema_version": "relay-v3.1-task-admission",
                "roadmap": {
                    "disposition": "MAPPED_EXISTING_WP",
                    "new_revision": "RM-0013",
                    "basis": ["Owner selected the provider-backed task."],
                    "work_package": {
                        "id": "WP-TA-109",
                        "title": "Current work",
                        "weight": 50,
                        "state": "ACTIVE",
                        "depends_on": ["WP-TA-108"],
                    },
                },
                "ep": new_ep,
                "lease": {
                    "executor_id": "agent-z",
                    "method": "DETERMINISTIC",
                },
                "delivery": {"required": False, "primary_vehicle": None},
            }
            request_path = root / "canonical-task-admission.yaml"
            dump(request_path, request)
            live = parent_issue_observation(
                baseline=baseline,
                number=1771,
                state="OPEN",
                disposition="NO_CHANGE",
                acceptance_state="PENDING",
            )

            result = admit_task(
                root,
                tx_id=None,
                event_id=None,
                actor="owner",
                admission_path=request_path,
                base_ref=base_ref,
                programme_issue_observations=[live],
                selected_programme_ref="example/project#1771",
            )

            self.assertEqual("COMMITTED", result["status"])
            self.assertEqual("TX.1771.1", result["id"])
            state = load_yaml(root / "relay/STATE.yaml")
            self.assertEqual("EP.1771.1", state["execution"]["ep"])
            self.assertEqual("LEASE.1771.1", state["execution"]["lease"])
            self.assertTrue((root / "relay/WORK/EP.1771.1.yaml").exists())
            self.assertTrue((root / "relay/LEASES/LEASE.1771.1.yaml").exists())
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            canonical = [
                row["event_id"]
                for row in events
                if str(row["event_id"]).startswith("EVT.1771.")
            ]
            self.assertEqual(["EVT.1771.1", "EVT.1771.2", "EVT.1771.3"], canonical)

    def test_provider_backed_admission_records_programme_uncertainty_without_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            install_parent_issue(root, number=1771)
            release_lease(
                root,
                tx_id="TX-RELEASE-BEFORE-PARENT-ADMIT",
                event_id="EVT-RELEASE-BEFORE-PARENT-ADMIT",
                actor="agent-x",
                reason="ADMINISTRATIVE",
            )

            source_ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
            new_ep = copy.deepcopy(source_ep)
            new_ep["id"] = "EP-TA-012"
            request = {
                "schema_version": "relay-v3.1-task-admission",
                "roadmap": {
                    "disposition": "MAPPED_EXISTING_WP",
                    "new_revision": "RM-0013",
                    "basis": ["Recorder-first admission preserves programme uncertainty as context."],
                    "work_package": {
                        "id": "WP-TA-109",
                        "title": "Current work",
                        "weight": 50,
                        "state": "ACTIVE",
                        "depends_on": ["WP-TA-108"],
                    },
                },
                "ep": new_ep,
                "lease": {
                    "id": "LEASE-TA-012-01",
                    "executor_id": "agent-z",
                    "method": "DETERMINISTIC",
                },
                "delivery": {"required": False, "primary_vehicle": None},
            }
            request_path = root / "parent-task-admission.yaml"
            dump(request_path, request)

            result = admit_task(
                root,
                tx_id="TX-PARENT-ADMIT-MISSING",
                event_id="EVT-PARENT-ADMIT-MISSING",
                actor="owner",
                admission_path=request_path,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            state = load_yaml(root / "relay/STATE.yaml")
            self.assertEqual("EP-TA-012", state["execution"]["ep"])

    def test_critical_transaction_command_cannot_mutate_unowned_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prepare_git(root)
            roadmap = load_yaml(root / "relay/ROADMAP/ROADMAP.yaml")
            roadmap["revision"] = "RM-ILLEGAL"
            with self.assertRaisesRegex(TransactionError, "ACTIVATE_LEASE cannot mutate"):
                execute(
                    root,
                    tx_id="TX-ILLEGAL-TARGET",
                    command="ACTIVATE_LEASE",
                    actor="agent-x",
                    replacements={"relay/ROADMAP/ROADMAP.yaml": yaml_bytes(roadmap)},
                )

    def test_explicit_recovery_takeover_transfers_exclusive_custody_and_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            result = activate_lease(
                root,
                tx_id="TX-ACTIVATE-001",
                event_id="EVT-ACTIVATE-001",
                lease_id="LEASE-TA-011-02",
                executor_id="agent-y",
                actor="owner",
                method="DETERMINISTIC",
                qualification=None,
                owner_basis=None,
                branch=None,
                base_ref=base_ref,
                recovery_takeover=True,
            )
            self.assertEqual("COMMITTED", result["status"])
            old = load_yaml(root / "relay/LEASES/LEASE-TA-011-01.yaml")
            new = load_yaml(root / "relay/LEASES/LEASE-TA-011-02.yaml")
            state = load_yaml(root / "relay/STATE.yaml")
            snapshot = load_yaml(root / "relay/GENERATED/CURRENT_SNAPSHOT.yaml")
            self.assertEqual("INVALIDATED", old["state"])
            self.assertEqual("ACTIVE", new["state"])
            self.assertEqual("agent-y", new["executor"]["id"])
            self.assertEqual("LEASE-TA-011-02", state["execution"]["lease"])
            self.assertEqual("LEASE-TA-011-02", snapshot["execution"]["lease"])
            self.assertEqual("agent-y", snapshot["execution"]["executor"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            ids = [item["event_id"] for item in events]
            self.assertIn("EVT-ACTIVATE-001-REL", ids)
            self.assertIn("EVT-ACTIVATE-001", ids)
            self.assertEqual([], validate(root))

    def test_provider_backed_custody_maintenance_can_allocate_transition_ids(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            install_parent_issue(root, number=1771)

            activated = activate_lease(
                root,
                tx_id="TX-CUSTODY-SETUP",
                event_id="EVT-CUSTODY-SETUP",
                lease_id="LEASE-CUSTODY-SETUP",
                executor_id="agent-x",
                actor="agent-x",
                method="DETERMINISTIC",
                qualification=None,
                owner_basis=None,
                branch=None,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", activated["status"])

            renewed = renew_lease(
                root,
                tx_id=None,
                event_id=None,
                actor="agent-x",
                expected_custody_epoch=1,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", renewed["status"])
            self.assertEqual("TX.1771.1", renewed["id"])

            released = release_lease(
                root,
                tx_id=None,
                event_id=None,
                actor="agent-x",
                reason="ADMINISTRATIVE",
                expected_custody_epoch=1,
            )
            self.assertEqual("COMMITTED", released["status"])
            self.assertEqual("TX.1771.2", released["id"])
            state = load_yaml(root / "relay/STATE.yaml")
            self.assertEqual("IDLE", state["execution"]["lifecycle"])

            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            canonical = [
                (row["event_id"], row["type"])
                for row in events
                if str(row["event_id"]).startswith("EVT.1771.")
            ]
            self.assertEqual(
                [("EVT.1771.1", "LEASE_RENEWED"), ("EVT.1771.2", "LEASE_RELEASED")],
                canonical,
            )

    def test_release_lease_atomically_enters_idle_state_and_refreshes_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prepare_git(root)
            result = release_lease(
                root,
                tx_id="TX-RELEASE-001",
                event_id="EVT-RELEASE-001",
                actor="agent-x",
                reason="ADMINISTRATIVE",
            )
            self.assertEqual("COMMITTED", result["status"])
            lease = load_yaml(root / "relay/LEASES/LEASE-TA-011-01.yaml")
            state = load_yaml(root / "relay/STATE.yaml")
            snapshot = load_yaml(root / "relay/GENERATED/CURRENT_SNAPSHOT.yaml")
            self.assertEqual("RELEASED", lease["state"])
            self.assertEqual(
                {"lifecycle": "IDLE", "ep": None, "lease": None, "route": None},
                state["execution"],
            )
            self.assertEqual("IDLE", snapshot["execution"]["lifecycle"])
            self.assertIsNone(snapshot["execution"]["lease"])
            self.assertEqual([], validate(root))

    def test_accept_checkpoint_publishes_immutable_checkpoint_state_and_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            _, _, _, _, template, *_ = base_objects()
            checkpoint = copy.deepcopy(template)
            checkpoint["id"] = "CP-TA-011"
            checkpoint["ep"] = "EP-TA-011"
            ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
            current_material = inspect_material_basis(root, ep, base_ref)["material_basis"]
            checkpoint["material_result"] = {
                "head": current_material["head"],
                "relevant_paths_digest": current_material["relevant_paths_digest"],
                "dependency_digest": current_material["dependency_digest"],
            }
            incoming = root / "incoming-checkpoint.yaml"
            dump(incoming, checkpoint)

            result = accept_checkpoint(
                root,
                tx_id="TX-CP-001",
                event_id="EVT-CP-001",
                actor="agent-x",
                checkpoint_path=incoming,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            self.assertTrue((root / "relay/CHECKPOINTS/CP-TA-011.yaml").exists())
            state = load_yaml(root / "relay/STATE.yaml")
            snapshot = load_yaml(root / "relay/GENERATED/CURRENT_SNAPSHOT.yaml")
            self.assertEqual("CP-TA-011", state["accepted"]["checkpoint"])
            self.assertEqual("CP-TA-011", snapshot["evidence"]["latest_checkpoint"])
            self.assertEqual([], validate(root))

            with self.assertRaisesRegex(TransactionError, "immutable"):
                accept_checkpoint(
                    root,
                    tx_id="TX-CP-002",
                    event_id="EVT-CP-002",
                    actor="agent-x",
                    checkpoint_path=incoming,
                    base_ref=base_ref,
                )

    def test_checkpoint_records_control_and_material_debt_without_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            _, _, _, _, template, *_ = base_objects()
            checkpoint = copy.deepcopy(template)
            checkpoint["id"] = "CP-TA-011"
            checkpoint["ep"] = "EP-TA-011"
            checkpoint["material_result"]["head"] = "deadbeef"
            incoming = root / "incoming-checkpoint.yaml"
            dump(incoming, checkpoint)

            controls_path = root / "relay/CONTROLS/controls.yaml"
            controls = load_yaml(controls_path)
            controls["controls"].append({
                "id": "CTRL-BLOCK-CP",
                "kind": "QUALITY",
                "state": "OPEN",
                "source": {"type": "VALIDATOR", "ref": "synthetic"},
                "condition": "Synthetic checkpoint warning.",
                "blocks": ["CHECKPOINT"],
                "permits": ["TEST"],
                "resolution": {"condition": "Synthetic blocker clears.", "evidence": []},
            })
            dump(controls_path, controls)

            result = accept_checkpoint(
                root,
                tx_id="TX-CP-RECORDER",
                event_id="EVT-CP-RECORDER",
                actor="agent-x",
                checkpoint_path=incoming,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            stored = load_yaml(root / "relay/CHECKPOINTS/CP-TA-011.yaml")
            self.assertEqual("deadbeef", stored["material_result"]["head"])

    def test_checkpoint_acceptance_id_mismatch_is_recorded_not_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            _, _, _, _, template, *_ = base_objects()
            checkpoint = copy.deepcopy(template)
            checkpoint["id"] = "CP-TA-011"
            checkpoint["ep"] = "EP-TA-011"
            checkpoint["acceptance"][0]["id"] = "AC-WRONG"
            incoming = root / "incoming-checkpoint.yaml"
            dump(incoming, checkpoint)

            result = accept_checkpoint(
                root,
                tx_id="TX-CP-AC-MISMATCH",
                event_id="EVT-CP-AC-MISMATCH",
                actor="agent-x",
                checkpoint_path=incoming,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            stored = load_yaml(root / "relay/CHECKPOINTS/CP-TA-011.yaml")
            self.assertEqual("AC-WRONG", stored["acceptance"][0]["id"])

    def test_provider_backed_checkpoint_can_allocate_acceptance_identities(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            install_parent_issue(root, number=1771)

            _, _, _, _, template, *_ = base_objects()
            checkpoint = copy.deepcopy(template)
            checkpoint.pop("id", None)
            ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
            material = inspect_material_basis(root, ep, base_ref)["material_basis"]
            checkpoint["ep"] = "EP-TA-011"
            checkpoint["material_result"] = {
                "head": material["head"],
                "relevant_paths_digest": material["relevant_paths_digest"],
                "dependency_digest": material["dependency_digest"],
            }
            incoming = root / "canonical-checkpoint.yaml"
            dump(incoming, checkpoint)

            result = accept_checkpoint(
                root,
                tx_id=None,
                event_id=None,
                actor="agent-x",
                checkpoint_path=incoming,
                base_ref=base_ref,
            )

            self.assertEqual("COMMITTED", result["status"])
            self.assertEqual("TX.1771.1", result["id"])
            state = load_yaml(root / "relay/STATE.yaml")
            self.assertEqual("CP.1771.1", state["accepted"]["checkpoint"])
            self.assertTrue((root / "relay/CHECKPOINTS/CP.1771.1.yaml").exists())
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            accepted = [row for row in events if row["type"] == "CHECKPOINT_ACCEPTED"][-1]
            self.assertEqual("EVT.1771.1", accepted["event_id"])
            self.assertEqual("CP.1771.1", accepted["subject"])

    def test_failed_checkpoint_is_recorded_without_claiming_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            _, _, _, _, template, *_ = base_objects()
            checkpoint = copy.deepcopy(template)
            checkpoint["id"] = "CP-TA-011"
            checkpoint["ep"] = "EP-TA-011"
            checkpoint["acceptance"][0]["result"] = "FAIL"
            incoming = root / "incoming-checkpoint.yaml"
            dump(incoming, checkpoint)

            result = accept_checkpoint(
                root,
                tx_id="TX-CP-FAIL",
                event_id="EVT-CP-FAIL",
                actor="agent-x",
                checkpoint_path=incoming,
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            stored = load_yaml(root / "relay/CHECKPOINTS/CP-TA-011.yaml")
            self.assertEqual("FAIL", stored["acceptance"][0]["result"])

    def test_local_execution_after_lease_release_uses_checkpoint_ep_context(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            historical_ep = load_yaml(root / "relay/WORK/EP-TA-011.yaml")
            historical_ep["id"] = "EP-TA-010"
            dump(root / "relay/WORK/EP-TA-010.yaml", historical_ep)
            release_lease(
                root,
                tx_id="TX-RELEASE-LOCAL",
                event_id="EVT-RELEASE-LOCAL",
                actor="agent-x",
                reason="ADMINISTRATIVE",
            )
            result = export_local_execution(
                root,
                tx_id="TX-LOCAL-IDLE",
                event_id="EVT-LOCAL-IDLE",
                actor="agent-x",
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            package = load_yaml(root / "relay/GENERATED/LOCAL_EXECUTION.yaml")
            self.assertEqual("EP-TA-010", package["execution"]["ep"])
            self.assertTrue(package["checkpoint"]["handoff"])
            self.assertEqual(
                "Read CURRENT_SNAPSHOT and EP.",
                package["next"]["first_action"],
            )

    def test_control_resolution_changes_control_event_and_snapshot_together(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            add_open_control(root)
            install_parent_issue(root, number=1771)
            result = resolve_control(
                root,
                tx_id=None,
                event_id=None,
                actor="agent-x",
                control_id="CTRL-TEST-001",
                evidence=["provider readback PASS"],
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", result["status"])
            controls = load_yaml(root / "relay/CONTROLS/controls.yaml")
            row = [item for item in controls["controls"] if item["id"] == "CTRL-TEST-001"][0]
            self.assertEqual("RESOLVED", row["state"])
            self.assertEqual(["provider readback PASS"], row["resolution"]["evidence"])
            events, errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], errors)
            self.assertIn("EVT.1771.1", [item["event_id"] for item in events])
            self.assertEqual("TX.1771.1", result["id"])
            self.assertEqual([], validate(root))

    def test_handover_and_local_execution_are_generated_downstream_views(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            install_standalone(root)
            accept_current_checkpoint_and_reconcile(root, base_ref)
            planned = plan_handover(
                root,
                tx_id="TX-HANDOVER-PLAN-001",
                event_id="EVT-HANDOVER-PLAN-001",
                actor="agent-x",
                target_path=target_observation(root),
                base_ref=base_ref,
                complex_mode=False,
            )
            self.assertEqual("COMMITTED", planned["status"])
            handover = publish_handover(
                root,
                tx_id="TX-HANDOVER-001",
                event_id="EVT-HANDOVER-001",
                actor="agent-x",
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", handover["status"])
            text = (root / "relay/GENERATED/HANDOVER.md").read_text(encoding="utf-8")
            self.assertIn("Engineering Relay V3.1 Handover", text)
            self.assertIn("Reconstruction sources", text)

            local = export_local_execution(
                root,
                tx_id="TX-LOCAL-001",
                event_id="EVT-LOCAL-001",
                actor="agent-x",
                base_ref=base_ref,
            )
            self.assertEqual("COMMITTED", local["status"])
            package = load_yaml(root / "relay/GENERATED/LOCAL_EXECUTION.yaml")
            self.assertEqual("DERIVED_EXECUTION_PACKAGE", package["authority"])
            self.assertEqual("EP-TA-011", package["execution"]["ep"])
            self.assertEqual("Validate schemas.", package["next"]["first_action"])
            self.assertEqual([], validate(root))

    def test_sync_delivery_requires_provider_vehicle_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            observation = configure_delivery(root, base_ref)
            install_parent_issue(root, number=1771)
            result = sync_delivery(
                root,
                tx_id=None,
                event_id=None,
                actor="provider-sync",
                observation_path=observation,
            )
            self.assertEqual("COMMITTED", result["status"])
            self.assertEqual("TX.1771.1", result["id"])
            events, event_errors = load_events(root / "relay/EVENTS.jsonl")
            self.assertEqual([], event_errors)
            self.assertIn("EVT.1771.1", [item["event_id"] for item in events])
            persisted = load_yaml(root / "relay/GENERATED/DELIVERY_STATUS.yaml")
            self.assertEqual("PROVIDER_READBACK", persisted["authority"])
            self.assertEqual("MERGED", persisted["lifecycle"])

            wrong = load_yaml(observation)
            wrong["vehicle"]["number"] = 999
            wrong_path = root / "wrong-provider-observation.yaml"
            dump(wrong_path, wrong)
            with self.assertRaisesRegex(TransactionError, "does not match"):
                sync_delivery(
                    root,
                    tx_id="TX-DELIVERY-002",
                    event_id="EVT-DELIVERY-002",
                    actor="provider-sync",
                    observation_path=wrong_path,
                )

    def test_close_records_terminal_state_without_checkpoint_or_delivery_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            observation = configure_delivery(root, base_ref, lifecycle="OPEN")
            sync_delivery(
                root,
                tx_id="TX-DELIVERY-OPEN",
                event_id="EVT-DELIVERY-OPEN",
                actor="provider-sync",
                observation_path=observation,
            )

            result = close_task(
                root,
                tx_id="TX-CLOSE-RECORDER",
                event_id="EVT-CLOSE-RECORDER",
                actor="owner",
            )
            self.assertEqual("COMMITTED", result["status"])
            state = load_yaml(root / "relay/STATE.yaml")
            lease = load_yaml(root / "relay/LEASES/LEASE-TA-011-01.yaml")
            self.assertEqual("TERMINAL", state["execution"]["lifecycle"])
            self.assertEqual("RELEASED", lease["state"])

    def test_incomplete_transaction_blocks_all_authority_until_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, base_ref = prepare_git(root)
            with self.assertRaises(TransactionError):
                activate_lease(
                    root,
                    tx_id="TX-ACTIVATE-FAIL",
                    event_id="EVT-ACTIVATE-FAIL",
                    lease_id="LEASE-TA-011-02",
                    executor_id="agent-y",
                    actor="owner",
                    method="DETERMINISTIC",
                    qualification=None,
                    owner_basis=None,
                    branch=None,
                    base_ref=base_ref,
                    recovery_takeover=True,
                    fail_after=1,
                )
            errors = validate_authority(root)
            self.assertTrue(any("requires recovery" in item for item in errors), errors)


class BuddyMarkdownRelayTests(unittest.TestCase):
    """Issue-scoped Markdown must be transactional, immutable and non-authoritative."""

    def test_commit_readback_and_root_state_is_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            content = b"# Original source observation\n\nUNKNOWN implementation. Historical refs EP.438.7 and EVT.438.1 are citations, not new identities.\n"
            result = publish_buddy_markdown(
                root,
                issue_number=889,
                tx_id="TX.889.1",
                stage="READINESS",
                actor="runner-b",
                markdown=content,
            )
            self.assertEqual("COMMITTED", result["status"])
            self.assertEqual(
                "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.1-READINESS.md",
                result["message_path"],
            )
            self.assertEqual("NOT_ATTESTED_BY_MESSAGE_TRANSPORT", result["admission"])
            self.assertEqual(content, (root / result["message_path"]).read_bytes())
            receipt = load_yaml(root / "relay/TRANSACTIONS/TX.889.1/manifest.yaml")
            self.assertEqual("PUBLISH_BUDDY_MARKDOWN", receipt["command"])
            self.assertEqual(["TX.889.1"], receipt["identity_reservations"])
            self.assertEqual(result["message_sha256"], receipt["operations"][0]["after_digest"])
            self.assertFalse((root / "relay/STATE.yaml").exists())
            self.assertFalse((root / "relay/LEASES").exists())
            self.assertFalse((root / "relay/EVENTS.jsonl").exists())

    def test_same_transaction_cannot_overwrite_frozen_stage1(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kw = dict(issue_number=889, tx_id="TX.889.1", stage="STAGE1_INTAKE",
                      actor="runner-b")
            publish_buddy_markdown(root, markdown=b"# Frozen plan\n\nFirst ideas.\n", **kw)
            with self.assertRaisesRegex(TransactionError, "IMMUTABLE"):
                publish_buddy_markdown(root, markdown=b"# Changed plan\n\nRetrofit.\n", **kw)
            self.assertIn("First ideas", (root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.1-STAGE1_INTAKE.md").read_text())

    def test_reject_wrong_issue_stage_and_non_markdown(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(TransactionError, "MATCH_ISSUE"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.438.1",
                                       stage="STAGE1_INTAKE", actor="a", markdown=b"# a\n")
            with self.assertRaisesRegex(TransactionError, "STAGE_INVALID"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                       stage="WRITER_PROMOTION", actor="a", markdown=b"# a\n")
            with self.assertRaisesRegex(TransactionError, "HEADING_REQUIRED"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                       stage="STAGE1_INTAKE", actor="a", markdown=b"not markdown")
            for prohibited_stage in ("TECHNICAL_HANDOVER", "STAGE2_RECONCILIATION",
                                     "CONTINUATION_EVIDENCE"):
                with self.assertRaisesRegex(TransactionError, "STAGE_INVALID"):
                    publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                           stage=prohibited_stage, actor="a", markdown=b"# No admission\n")
            self.assertFalse((root / "relay/TRANSACTIONS").exists())

    def test_direct_transaction_cannot_bypass_issue_or_immutability(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.2-STAGE1_INTAKE.md"
            with self.assertRaisesRegex(TransactionError, "TX_OR_STAGE_INVALID"):
                execute(root, tx_id="TX.889.1", command="PUBLISH_BUDDY_MARKDOWN",
                        actor="rogue", replacements={path: b"# forged\n"})
            with self.assertRaisesRegex(TransactionError, "ISSUE_PATH_INVALID"):
                execute(root, tx_id="TX.889.2", command="PUBLISH_BUDDY_MARKDOWN",
                        actor="rogue", replacements={
                            "relay/CONTINUITY/episodes/ISSUE-438/messages/TX.889.2-STAGE1_PLAN.md":
                                b"# forged\n"})
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                   stage="STAGE1_INTAKE", actor="runner-b", markdown=b"# original\n")
            with self.assertRaisesRegex(TransactionError, "IMMUTABLE"):
                execute(root, tx_id="TX.889.2", command="PUBLISH_BUDDY_MARKDOWN",
                        actor="rogue", replacements={path: b"# replacement\n"})
            self.assertEqual(b"# original\n", (root / path).read_bytes())

    def test_baseline_first_sequence_with_claimed_external_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(TransactionError, "MISSING_STAGE1_BASELINE"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.5",
                                       stage="STAGE1_PLAN", actor="runner-b",
                                       markdown=b"# Plan\n\nNo source baseline.\n")
            with self.assertRaisesRegex(TransactionError, "MISSING_STAGE1_INTAKE"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                       stage="DISPATCH_REQUEST", actor="operator",
                                       markdown=b"# Dispatch\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.1",
                                   stage="STAGE1_INTAKE", actor="operator",
                                   markdown=b"# Owner and original source\n\nNo A implementation.\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                   stage="DISPATCH_REQUEST", actor="operator",
                                   markdown=b"# Launch request\n\nFresh source-only context.\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.3",
                                   stage="DISPATCH_OBSERVATION", actor="operator",
                                   markdown=b"# RUNNER_EXECUTION_OBSERVED\n\nSession ref: external-run-1\nRead-scope ref: original-only-view-1\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                   stage="STAGE1_BASELINE", actor="runner-b",
                                   markdown=b"# Independent original system baseline\n\nObserved source-to-consumer path.\n")
            plan = publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.5",
                                          stage="STAGE1_PLAN", actor="runner-b",
                                          markdown=b"# Two independent designs\n\nDesign A and B; decisive falsifiers.\n")
            self.assertEqual("COMMITTED", plan["status"])
            self.assertEqual("NOT_ATTESTED_BY_MESSAGE_TRANSPORT", plan["admission"])
            self.assertFalse((root / "relay/STATE.yaml").exists())

    def test_operator_cannot_claim_runner_baseline_and_runner_identity_cannot_switch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.1",
                                   stage="STAGE1_INTAKE", actor="operator",
                                   markdown=b"# Original Owner source\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                   stage="DISPATCH_REQUEST", actor="operator",
                                   markdown=b"# Launch request\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.3",
                                   stage="DISPATCH_OBSERVATION", actor="operator",
                                   markdown=b"# RUNNER_EXECUTION_OBSERVED\n\nSession ref: runner-123\nRead-scope ref: original-only\n")
            with self.assertRaisesRegex(TransactionError, "OPERATOR_AND_RUNNER_NOT_SEPARATE"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                       stage="STAGE1_BASELINE", actor="operator",
                                       markdown=b"# Attempted self-attestation\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                   stage="STAGE1_BASELINE", actor="runner-b",
                                   markdown=b"# Original source independently reconstructed\n")
            with self.assertRaisesRegex(TransactionError, "STAGE1_AUTHOR_CHANGED"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.5",
                                       stage="STAGE1_PLAN", actor="other-agent",
                                       markdown=b"# Different author trying to inherit baseline\n")
            good = publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.5",
                                          stage="STAGE1_PLAN", actor="runner-b",
                                          markdown=b"# Independent options and falsifiers\n")
            self.assertEqual("COMMITTED", good["status"])
            self.assertEqual("NOT_ATTESTED_BY_MESSAGE_TRANSPORT", good["admission"])

    def _good_stage1(self, root):
        """All source/author claims are intentionally synthetic; this is NOT isolation proof."""
        rows = (
            (1, "STAGE1_INTAKE", "operator", b"# Historical Owner WHAT/WHY\n"),
            (2, "DISPATCH_REQUEST", "operator", b"# Restrict Runner B to original source\n"),
            (3, "DISPATCH_OBSERVATION", "operator",
             b"# RUNNER_EXECUTION_OBSERVED\n\nSession ref: claimed-b-session\nRead-scope ref: claimed-original-only\n"),
            (4, "STAGE1_BASELINE", "runner-b", b"# Source producer and consumer witness\n"),
            (5, "STAGE1_PLAN", "runner-b", b"# Two alternate HOWs and falsifiers\n"),
        )
        results = {}
        for seq, stage, actor, content in rows:
            results[stage] = publish_buddy_markdown(
                root, issue_number=889, tx_id=f"TX.889.{seq}",
                stage=stage, actor=actor, markdown=content,
            )
        return results

    def test_freeze_candidate_binds_five_actual_receipts_but_does_not_attest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            records = self._good_stage1(root)
            body = (
                "# STAGE1_FREEZE_CANDIDATE\n"
                "Isolation verdict: NOT_ATTESTED\n"
                + "".join(
                    f"{name} tx: TX.889.{seq}\n"
                    f"{name} digest: {records[stage]['message_sha256']}\n"
                    for name, seq, stage in (
                        ("Intake", 1, "STAGE1_INTAKE"),
                        ("Dispatch request", 2, "DISPATCH_REQUEST"),
                        ("Dispatch observation", 3, "DISPATCH_OBSERVATION"),
                        ("Baseline", 4, "STAGE1_BASELINE"),
                        ("Plan", 5, "STAGE1_PLAN"),
                    )
                )
            ).encode("utf-8")
            with self.assertRaisesRegex(TransactionError, "FREEZE_OPERATOR_NOT_SEPARATE"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                       stage="STAGE1_FREEZE_CANDIDATE", actor="runner-b",
                                       markdown=body)
            with self.assertRaisesRegex(TransactionError, "FREEZE_STAG" ):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                       stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                                       markdown=body.replace(records["STAGE1_PLAN"]["message_sha256"].encode("utf-8"),
                                                             b"sha256:" + b"0" * 64))
            # Forged dispatch receipt and duplicate note cannot hide in prose.
            with self.assertRaisesRegex(TransactionError, "FREEZE_DISPATCH_OBSERVATION_REF_MISMATCH"):
                publish_buddy_markdown(
                    root, issue_number=889, tx_id="TX.889.6",
                    stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                    markdown=body.replace(records["DISPATCH_OBSERVATION"]["message_sha256"].encode("utf-8"),
                                          b"sha256:" + b"f" * 64))
            with self.assertRaisesRegex(TransactionError, "FREEZE_DISPATCH_REQUEST_REF_MISMATCH"):
                publish_buddy_markdown(
                    root, issue_number=889, tx_id="TX.889.6",
                    stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                    markdown=body + b"Dispatch request tx: TX.889.99\n")
            with self.assertRaisesRegex(TransactionError, "CANNOT_SELF_CERTIFY_ISOLATION"):
                publish_buddy_markdown(
                    root, issue_number=889, tx_id="TX.889.6",
                    stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                    markdown=body + b"Isolation verdict: VERIFIED\n")
            receipt = publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                             stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                                             markdown=body)
            self.assertEqual("COMMITTED", receipt["status"])
            self.assertEqual("NOT_ATTESTED_BY_MESSAGE_TRANSPORT", receipt["admission"])
            self.assertFalse((root / "relay/STATE.yaml").exists())
            with self.assertRaisesRegex(TransactionError, "STAGE_INVALID"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.7",
                                       stage="STAGE2_RECONCILIATION", actor="runner-b",
                                       markdown=b"# Must not open Stage2\n")

    def test_freeze_candidate_rejects_changed_plan_and_later_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            records = self._good_stage1(root)
            content = (
                "# STAGE1_FREEZE_CANDIDATE\n"
                "Isolation verdict: NOT_ATTESTED\n"
                + "".join(
                    f"{label} tx: TX.889.{seq}\n{label} digest: {records[stage]['message_sha256']}\n"
                    for label, seq, stage in (
                        ("Intake", 1, "STAGE1_INTAKE"),
                        ("Dispatch request", 2, "DISPATCH_REQUEST"),
                        ("Dispatch observation", 3, "DISPATCH_OBSERVATION"),
                        ("Baseline", 4, "STAGE1_BASELINE"),
                        ("Plan", 5, "STAGE1_PLAN"),
                    )
                )
            ).encode("utf-8")
            plan = root / records["STAGE1_PLAN"]["message_path"]
            original = plan.read_bytes()
            plan.write_bytes(b"# Altered plan after commit\n")
            with self.assertRaisesRegex(TransactionError, "RECEIPT_MISMATCH"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                       stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                                       markdown=content)
            plan.write_bytes(original)
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                   stage="DISPATCH_REQUEST", actor="operator",
                                   markdown=b"# A different attempted Runner launch\n")
            with self.assertRaisesRegex(TransactionError, "STALE_STAGE_CHAIN"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.7",
                                       stage="STAGE1_FREEZE_CANDIDATE", actor="operator",
                                       markdown=content)

    def test_new_intake_supersedes_old_dispatch_and_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.1",
                                   stage="STAGE1_INTAKE", actor="operator",
                                   markdown=b"# Original intent cutoff 1\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                   stage="DISPATCH_REQUEST", actor="operator",
                                   markdown=b"# Request source-only session\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.3",
                                   stage="DISPATCH_OBSERVATION", actor="operator",
                                   markdown=b"# RUNNER_EXECUTION_OBSERVED\n\nSession ref: run-one\nRead-scope ref: scope-one\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                   stage="STAGE1_BASELINE", actor="runner-b",
                                   markdown=b"# Original cutoff 1 baseline\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.5",
                                   stage="STAGE1_INTAKE", actor="operator",
                                   markdown=b"# Revised original cutoff 2\n")
            with self.assertRaisesRegex(TransactionError, "STALE_STAGE_CHAIN"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                       stage="STAGE1_PLAN", actor="runner-b",
                                       markdown=b"# Must not inherit old baseline\n")
            with self.assertRaisesRegex(TransactionError, "STALE_STAGE_CHAIN"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.6",
                                       stage="STAGE1_BASELINE", actor="runner-b",
                                       markdown=b"# Must not inherit old dispatch\n")
            self.assertFalse((root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.6-STAGE1_PLAN.md").exists())

    def test_new_symlinked_intake_cannot_be_ignored_for_old_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.1",
                                   stage="STAGE1_INTAKE", actor="operator",
                                   markdown=b"# Old original intake\n")
            folder = root / "relay/CONTINUITY/episodes/ISSUE-889/messages"
            alias = folder / "TX.889.2-STAGE1_INTAKE.md"
            alias.symlink_to(folder / "TX.889.1-STAGE1_INTAKE.md")
            with self.assertRaisesRegex(TransactionError, "MESSAGE_SYMLINK_FORBIDDEN"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.3",
                                       stage="DISPATCH_REQUEST", actor="operator",
                                       markdown=b"# Dispatch must not reuse old intake\n")
            self.assertFalse((root / "relay/TRANSACTIONS/TX.889.3").exists())

    def test_tampered_committed_intake_blocks_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            intake = publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.1",
                                             stage="STAGE1_INTAKE", actor="operator",
                                             markdown=b"# Original Owner/WHAT/WHY\n")
            (root / intake["message_path"]).write_bytes(b"# Changed source/candidate HEAD\n")
            with self.assertRaisesRegex(TransactionError, "RECEIPT_MISMATCH"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                       stage="DISPATCH_REQUEST", actor="operator",
                                       markdown=b"# Refuse changed intake\n")
            self.assertFalse((root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.2-DISPATCH_REQUEST.md").exists())

    def test_blocked_dispatch_cannot_become_stage1_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.1",
                                   stage="STAGE1_INTAKE", actor="operator",
                                   markdown=b"# Historic source and Owner\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                   stage="DISPATCH_REQUEST", actor="operator",
                                   markdown=b"# Dispatch request\n")
            publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.3",
                                   stage="DISPATCH_OBSERVATION", actor="operator",
                                   markdown=b"# BLOCKED_NO_RUNNER_CAPABILITY\n")
            with self.assertRaisesRegex(TransactionError, "DISPATCH_NOT_EXECUTED"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                       stage="STAGE1_BASELINE", actor="runner-b",
                                       markdown=b"# Fake baseline\n")
            self.assertFalse((root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.4-STAGE1_BASELINE.md").exists())

    def test_unreceipted_intake_does_not_satisfy_stage_sequence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            loose = root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.1-STAGE1_INTAKE.md"
            loose.parent.mkdir(parents=True)
            loose.write_bytes(b"# Loose file with no native transaction\n")
            with self.assertRaisesRegex(TransactionError, "PRIOR_MESSAGE_UNRECORDED"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.2",
                                       stage="DISPATCH_REQUEST", actor="operator",
                                       markdown=b"# Should reject loose intake\n")
            self.assertFalse((root / "relay/TRANSACTIONS").exists())

    def test_dispatch_request_then_blocker_records_no_runner_claim_or_lease(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            publish_buddy_markdown(
                root, issue_number=889, tx_id="TX.889.3", stage="STAGE1_INTAKE",
                actor="operator", markdown=b"# Historical Owner and source\n",
            )
            request = publish_buddy_markdown(
                root, issue_number=889, tx_id="TX.889.5",
                stage="DISPATCH_REQUEST", actor="operator",
                markdown=b"# Dispatch requested\n\nExact source ref; independent runtime required.\n",
            )
            blocker = publish_buddy_markdown(
                root, issue_number=889, tx_id="TX.889.6",
                stage="DISPATCH_OBSERVATION", actor="operator",
                markdown=b"# BLOCKED_NO_RUNNER_CAPABILITY\n\nNo separate AI runner available.\n",
            )
            self.assertEqual("COMMITTED", request["status"])
            self.assertEqual("COMMITTED", blocker["status"])
            self.assertEqual("NOT_ATTESTED_BY_MESSAGE_TRANSPORT", blocker["admission"])
            self.assertNotEqual(request["message_sha256"], blocker["message_sha256"])
            self.assertFalse((root / "relay/STATE.yaml").exists())
            self.assertFalse((root / "relay/EVENTS.jsonl").exists())
            self.assertFalse((root / "relay/LEASES").exists())
            with self.assertRaisesRegex(TransactionError, "DISPATCH_NOT_EXECUTED"):
                publish_buddy_markdown(
                    root, issue_number=889, tx_id="TX.889.7", stage="STAGE1_BASELINE",
                    actor="runner-b", markdown=b"# No independent Runner actually ran\n",
                )
            self.assertFalse((root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.7-STAGE1_PLAN.md").exists())

    def test_interrupted_transaction_is_recoverable_without_duplicate_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(TransactionError, "injected transaction interruption"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                       stage="READINESS", actor="agent-a",
                                       markdown=b"# Prepared\n\nUNKNOWN context life.\n",
                                       fail_after=1)
            recovered = recover_all(root)
            self.assertEqual("COMMITTED", recovered[0]["status"])
            self.assertEqual(
                b"# Prepared\n\nUNKNOWN context life.\n",
                (root / "relay/CONTINUITY/episodes/ISSUE-889/messages/TX.889.4-READINESS.md").read_bytes(),
            )
            with self.assertRaisesRegex(TransactionError, "IMMUTABLE"):
                publish_buddy_markdown(root, issue_number=889, tx_id="TX.889.4",
                                       stage="READINESS", actor="agent-a",
                                       markdown=b"# Duplicate\n")


if __name__ == "__main__":
    unittest.main()
