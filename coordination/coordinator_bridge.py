"""
Coordinator Status-to-JSON Bridge & Private Observation Snapshot Engine (WP2)
=============================================================================
Provides side-effect-free, authoritative export from coordinator runtime state
to typed JSON without altering original coordinator status/probe algorithms.

Key Components:
- AtomicSnapshotWriter: Writes observation snapshots via atomic replace (.tmp -> dst)
- AtomicSnapshotReader: Safely loads and parses snapshots with corrupt-state tolerance
- CompositeBindingResolver: Resolves (project_id, coordinator_id, session_id, tab_position,
  chat_id, binding_generation) to assignment/run while preserving coordinator status strings
- LivenessEvaluator: Evaluates probe freshness against 2x Cycle threshold without guessing STOPPED
- CoordinatorBridge: Orchestrates script export, validation, and snapshot publication
"""

import json
import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from coordination.contracts import CoordinatorObservation, ControlTowerRegistry

SNAPSHOT_SCHEMA_VERSION = "v1.0.0"
DEFAULT_CYCLE_SECONDS = 15


class AtomicSnapshotWriter:
    """Atomic file writer using temporary file and atomic replace."""

    @staticmethod
    def write_snapshot(target_path: Union[Path, str], snapshot_data: dict) -> Path:
        p = Path(target_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp_p = p.with_name(f"{p.name}.tmp.{os.getpid()}")
        try:
            with open(tmp_p, "w", encoding="utf-8") as f:
                json.dump(snapshot_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_p, p)
            return p
        except Exception:
            if tmp_p.exists():
                try:
                    tmp_p.unlink()
                except OSError:
                    pass
            raise


class AtomicSnapshotReader:
    """Safely reads private snapshot files with schema validation."""

    @staticmethod
    def read_snapshot(target_path: Union[Path, str]) -> Optional[dict]:
        if "\x00" in str(target_path):
            return None
        try:
            p = Path(target_path).resolve()
            if not p.is_file():
                return None
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            if data.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
                return None
            if "observations" not in data or not isinstance(data["observations"], list):
                return None
            return data
        except (json.JSONDecodeError, OSError, ValueError):
            return None


class LivenessEvaluator:
    """Multi-clock liveness evaluator comparing probe age to 2x Cycle threshold."""

    @staticmethod
    def evaluate(
        probe_status: str,
        last_probe_at_utc: Optional[str],
        as_of_utc: Optional[Union[datetime, str]] = None,
        cycle_seconds: int = DEFAULT_CYCLE_SECONDS
    ) -> str:
        if probe_status == "NEVER_PROBED":
            return "UNKNOWN"
        if probe_status in ("TIMEOUT", "LOADFAIL", "NOBOX", "UNUSUAL", "ERROR"):
            return "STALE"
        if not last_probe_at_utc:
            return "UNKNOWN"

        try:
            probe_dt = datetime.fromisoformat(last_probe_at_utc.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return "STALE"

        if as_of_utc is None:
            now_dt = datetime.now(timezone.utc)
        elif isinstance(as_of_utc, str):
            try:
                now_dt = datetime.fromisoformat(as_of_utc.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                now_dt = datetime.now(timezone.utc)
        else:
            now_dt = as_of_utc

        threshold = 2 * max(1, cycle_seconds)
        elapsed = (now_dt - probe_dt).total_seconds()
        if elapsed < 0:
            return "ALIVE"
        if elapsed > threshold:
            return "STALE"
        if probe_status == "SUCCESS":
            return "ALIVE"
        return "UNKNOWN"


class CompositeBindingResolver:
    """
    Resolves composite binding keys to Control Tower assignments and works.
    Invariant: Verbatim coordinator status/due/next/meter strings are NEVER overwritten.
    """

    @staticmethod
    def resolve(
        observation: dict,
        project_id: str,
        coordinator_id: str,
        session_id: str,
        registry_or_map: Optional[Union[ControlTowerRegistry, Dict[str, Any]]] = None,
        active_work_tabs: Optional[Dict[str, str]] = None
    ) -> dict:
        obs = dict(observation)
        tab_pos = str(obs.get("tab_position", ""))
        chat_id = str(obs.get("chat_id", ""))
        gen = int(obs.get("binding_generation", 1))

        composite_key = f"{project_id}|{coordinator_id}|{session_id}|{tab_pos}|{chat_id}|{gen}"
        conflicts = list(obs.get("conflicts", []))

        assignment_id = None
        work_id = None

        if isinstance(registry_or_map, ControlTowerRegistry):
            # Resolve from ControlTowerRegistry
            matched_run = None
            for run in registry_or_map.runs.values():
                if run.chat_id == chat_id and run.generation == gen:
                    matched_run = run
                    break

            if matched_run:
                assignment_id = matched_run.assignment_id
                assign = registry_or_map.assignments.get(assignment_id)
                if assign:
                    lane = registry_or_map.lanes.get(assign.lane_id)
                    if lane:
                        work_id = lane.work_id
            else:
                conflicts.append("UNASSIGNED_OR_UNKNOWN_TAB")
        elif isinstance(registry_or_map, dict):
            # Resolve from dictionary map (either composite_key or (chat_id, gen))
            match = registry_or_map.get(composite_key) or registry_or_map.get(f"{chat_id}|{gen}") or registry_or_map.get(chat_id)
            if isinstance(match, dict):
                assignment_id = match.get("assignment_id")
                work_id = match.get("work_id")
            elif isinstance(match, tuple) and len(match) == 2:
                assignment_id, work_id = match
            else:
                conflicts.append("UNASSIGNED_OR_UNKNOWN_TAB")
        else:
            conflicts.append("UNASSIGNED_OR_UNKNOWN_TAB")

        # Invariant check: At most one active tab per work
        if work_id and active_work_tabs is not None:
            existing_tab = active_work_tabs.get(work_id)
            if existing_tab and existing_tab != tab_pos:
                conflicts.append(f"MULTIPLE_ACTIVE_TABS_FOR_WORK:{work_id}")
            else:
                active_work_tabs[work_id] = tab_pos

        obs["assignment_id"] = assignment_id
        obs["work_id"] = work_id
        obs["conflicts"] = conflicts
        return obs


class CoordinatorBridge:
    """Bridge orchestrating rowsjson extraction, verification, and snapshot generation."""

    def __init__(
        self,
        coordinator_id: str = "claude-desktop-coordinator-01",
        project_id: str = "reallakshman19/Common",
        session_id: str = "Session_Default",
        cycle_seconds: int = DEFAULT_CYCLE_SECONDS,
        snapshot_dir: Optional[Union[Path, str]] = None
    ):
        self.coordinator_id = coordinator_id
        self.project_id = project_id
        self.session_id = session_id
        self.cycle_seconds = cycle_seconds
        self.snapshot_dir = Path(snapshot_dir) if snapshot_dir else Path(__file__).parent / "snapshots"

    def parse_rowsjson(self, raw_json_str: str) -> List[dict]:
        """Parses and normalizes JSON rows from watch.ps1 -Action rowsjson."""
        trimmed = raw_json_str.strip()
        if not trimmed:
            return []
        data = json.loads(trimmed)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
        raise ValueError(f"Unexpected JSON structure from coordinator: {type(data)}")

    def build_snapshot(
        self,
        raw_json_str: str,
        source_watermark: str = "",
        registry_or_map: Optional[Union[ControlTowerRegistry, Dict[str, Any]]] = None,
        as_of_utc: Optional[str] = None
    ) -> dict:
        """Constructs an atomic observation snapshot conforming to coordinator_observation_snapshot."""
        now_utc = as_of_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = self.parse_rowsjson(raw_json_str)
        source_digest = hashlib.sha256(raw_json_str.encode("utf-8")).hexdigest()

        active_work_tabs: Dict[str, str] = {}
        processed_obs = []

        for row in rows:
            obs = dict(row)
            # Ensure UTC timestamps
            if not obs.get("observed_at_utc"):
                obs["observed_at_utc"] = now_utc
            obs["observed_at"] = obs.get("observed_at") or obs["observed_at_utc"]

            # Liveness evaluation
            liveness = LivenessEvaluator.evaluate(
                probe_status=obs.get("probe_status", "UNKNOWN"),
                last_probe_at_utc=obs.get("last_probe_at_utc"),
                as_of_utc=now_utc,
                cycle_seconds=self.cycle_seconds
            )
            obs["liveness"] = liveness
            obs["coordinator_liveness"] = liveness

            # Composite binding resolution
            resolved = CompositeBindingResolver.resolve(
                observation=obs,
                project_id=self.project_id,
                coordinator_id=self.coordinator_id,
                session_id=self.session_id,
                registry_or_map=registry_or_map,
                active_work_tabs=active_work_tabs
            )
            processed_obs.append(resolved)

        snapshot = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "coordinator_id": self.coordinator_id,
            "session_id": self.session_id,
            "project_id": self.project_id,
            "generated_at_utc": now_utc,
            "source_digest": source_digest,
            "source_watermark": source_watermark or f"cycle-{now_utc}",
            "cycle_seconds": self.cycle_seconds,
            "observations": processed_obs
        }
        return snapshot

    def publish_snapshot(self, snapshot_data: dict, file_name: Optional[str] = None) -> Path:
        """Atomically saves the snapshot to the snapshot directory."""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        safe_proj = self.project_id.replace("/", "_").replace("\\", "_")
        safe_sess = self.session_id.replace("/", "_").replace("\\", "_")
        fn = file_name or f"observations_{safe_proj}_{safe_sess}.json"
        target_path = self.snapshot_dir / fn
        return AtomicSnapshotWriter.write_snapshot(target_path, snapshot_data)

    def execute_and_export(
        self,
        watch_script_path: Union[Path, str],
        tabs: str,
        state_file: Optional[Union[Path, str]] = None,
        registry_or_map: Optional[Union[ControlTowerRegistry, Dict[str, Any]]] = None
    ) -> dict:
        """Executes watch.ps1 -Action rowsjson via PowerShell and builds the snapshot."""
        cmd = [
            "powershell",
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(watch_script_path),
            "-Action", "rowsjson",
            "-Tabs", tabs,
            "-Session", self.session_id,
            "-Cycle", str(self.cycle_seconds)
        ]
        if state_file:
            cmd.extend(["-StateFile", str(state_file)])

        res = subprocess.run(cmd, capture_output=True, text=True, encoding="latin1")
        if res.returncode != 0:
            raise RuntimeError(f"watch.ps1 failed (exit {res.returncode}): {res.stderr}")

        return self.build_snapshot(res.stdout, registry_or_map=registry_or_map)


def get_observations_for_api(
    project_id: str,
    session_id: Optional[str] = None,
    snapshot_dir: Optional[Union[Path, str]] = None
) -> dict:
    """Internal-only API helper to read observations snapshot from disk without running scripts."""
    if "\x00" in str(project_id) or (session_id and "\x00" in str(session_id)):
        return {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "coordinator_id": "UNKNOWN",
            "session_id": session_id or "UNKNOWN",
            "project_id": project_id,
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_digest": "0" * 40,
            "source_watermark": "INVALID_QUERY_PARAMETERS",
            "cycle_seconds": DEFAULT_CYCLE_SECONDS,
            "observations": []
        }
    s_dir = Path(snapshot_dir) if snapshot_dir else Path(__file__).parent / "snapshots"
    safe_proj = project_id.replace("/", "_").replace("\\", "_")

    if session_id:
        safe_sess = session_id.replace("/", "_").replace("\\", "_")
        target = s_dir / f"observations_{safe_proj}_{safe_sess}.json"
        snap = AtomicSnapshotReader.read_snapshot(target)
        if snap:
            return snap

    # Fallback to general project snapshot or search matching files
    candidates = list(s_dir.glob(f"observations_{safe_proj}*.json"))
    if candidates:
        # Sort by mtime descending to get freshest snapshot
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        snap = AtomicSnapshotReader.read_snapshot(candidates[0])
        if snap:
            return snap

    # No snapshot found: return uninitialized structure
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "coordinator_id": "UNKNOWN",
        "session_id": session_id or "UNKNOWN",
        "project_id": project_id,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_digest": "0" * 40,
        "source_watermark": "NO_OBSERVATIONS_FOUND",
        "cycle_seconds": DEFAULT_CYCLE_SECONDS,
        "observations": []
    }
