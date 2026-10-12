"""Control Tower WP3: bounded, source-preserving materialized read models.

Materialization is an explicit trusted process. HTTP GET uses ProjectionQueryService
in SQLite read-only mode; it never polls GitHub, runs PowerShell, or writes state.
Neither coordinator display columns nor Owner acceptance are recalculated.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from coordination.coordinator_bridge import CompositeBindingResolver, LivenessEvaluator
from coordination.indexer import CanonicalV36Adapter

VIEWS = ("portfolio", "works", "assignments", "unassigned_observations", "evidence", "recovery")
CELLS = ("tab", "status", "aim", "plan", "ac", "ci", "meter", "due", "checked", "next")
MAX_PAGE = 200


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return d if d.tzinfo else None
    except (ValueError, TypeError, AttributeError):
        return None


def age_state(then: Optional[str], as_of: str, cycle_seconds: int) -> str:
    a, b = dt(then), dt(as_of)
    if a is None or b is None:
        return "UNKNOWN"
    sec = (b - a).total_seconds()
    if sec < 0:
        return "UNKNOWN"
    return "STALE" if sec > 2 * cycle_seconds else "FRESH"


def _valid_mapping(registry, m: dict) -> bool:
    """Explicit evidence attribution is admissible only if all foreign keys agree."""
    keys = ("project_id", "task_id", "child_issue", "work_id",
            "assignment_id", "run_id", "source_ref", "source_revision")
    if not all(isinstance(m.get(k), str) and m[k] for k in keys):
        return False
    if not m["source_ref"].startswith("https://"):
        return False
    work = registry.works.get(m["work_id"])
    assign = registry.assignments.get(m["assignment_id"])
    run = registry.runs.get(m["run_id"])
    lane = registry.lanes.get(assign.lane_id) if assign else None
    return bool(work and assign and run and lane and
                work.project_id == m["project_id"] and
                lane.work_id == work.work_id and
                run.assignment_id == assign.assignment_id)


def _evidence_match(registry, mapping: list, evidence: dict) -> tuple:
    """No inferred attribution: missing or multiple eligible proofs remain unassigned."""
    candidates = []
    for m in mapping:
        if not _valid_mapping(registry, m):
            continue
        if (m["project_id"], m["task_id"], m["child_issue"]) != (
            evidence["project_id"], evidence["task_id"], evidence["owner_issue"]):
            continue
        issued = dt(evidence["created_at"])
        start, end = dt(m.get("valid_from_utc")), dt(m.get("valid_to_utc"))
        if m.get("valid_from_utc") and (not issued or not start or issued < start):
            continue
        if m.get("valid_to_utc") and (not issued or not end or issued > end):
            continue
        candidates.append(m)
    if len(candidates) == 1:
        return candidates[0], []
    return None, (["ATTRIBUTION_CONFLICT"] if len(candidates) > 1 else ["UNATTRIBUTED"])


class ProjectionEngine:
    """Explicit producer: transactions publish one immutable generation at a time."""

    def __init__(self, db_path: str):
        self.db_path = str(db_path)

    @staticmethod
    def _schema(conn):
        conn.execute("""CREATE TABLE IF NOT EXISTS projection_meta(
            generation TEXT PRIMARY KEY, content_digest TEXT NOT NULL,
            as_of_utc TEXT NOT NULL, source_watermarks TEXT NOT NULL,
            built_at_utc TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS projection_rows(
            generation TEXT NOT NULL, view TEXT NOT NULL,
            project_id TEXT NOT NULL, sort_key TEXT NOT NULL,
            body TEXT NOT NULL,
            PRIMARY KEY(generation, view, project_id, sort_key))""")
        conn.execute("""CREATE INDEX IF NOT EXISTS projection_rows_page
            ON projection_rows(generation, view, project_id, sort_key)""")

    def materialize(self, registry, evidence_index, observation_snapshots: List[dict],
                    as_of_utc: str, source_watermarks: dict,
                    task_attributions: Optional[List[dict]] = None,
                    pr_bindings: Optional[List[dict]] = None) -> dict:
        if dt(as_of_utc) is None:
            raise ValueError("as_of_utc must be an explicit timezone-aware ISO8601 instant")
        if not isinstance(source_watermarks, dict):
            raise ValueError("source_watermarks must be an explicit version vector")
        task_attributions = task_attributions or []
        pr_bindings = pr_bindings or []
        if any(not _valid_mapping(registry, m) for m in task_attributions):
            raise ValueError("Unverifiable task attribution: fail closed")
        if any(s.get("schema_version") != "v1.0.0" for s in observation_snapshots):
            raise ValueError("Unsupported WP2 observation snapshot")

        conn = sqlite3.connect(self.db_path)
        try:
            self._schema(conn)
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM projection_rows WHERE generation = '__staging__'")
            counts = {v: 0 for v in VIEWS}
            digest = hashlib.sha256()
            digest.update(canon({"as_of_utc": as_of_utc,
                                 "source_watermarks": source_watermarks}).encode("utf-8"))
            active_evidence_by_work = {}
            seen_task_by_work = {}
            def emit(view, project, key, row):
                if view not in VIEWS or not isinstance(project, str):
                    raise ValueError("Invalid projection scope")
                body = canon(row)
                # Globally ordered key prevents cross-project cursor collisions.
                key = project + "|" + key
                conn.execute("""INSERT INTO projection_rows(generation, view, project_id, sort_key, body)
                                VALUES ('__staging__', ?, ?, ?, ?)""", (view, project, key, body))
                digest.update(canon([view, project, key, row]).encode("utf-8"))
                counts[view] += 1

            # Source provenance: explicit project registry, never fabricate provider presence.
            for pid in sorted(registry.projects):
                p = registry.projects[pid]
                assignments = [a for a in registry.assignments.values()
                               if registry.works[registry.lanes[a.lane_id].work_id].project_id == pid]
                active_assignments = sum(a.status == "ACTIVE" for a in assignments)
                emit("portfolio", pid, pid, {
                    "project_id": pid, "verified_repo_id": None,
                    "name": p.name, "provider_reachability": p.provider_reachability,
                    "provider_observed_at_utc": p.as_of, "registered_assignments": len(assignments),
                    "registered_active_assignments": active_assignments,
                    "work_count": sum(w.project_id == pid for w in registry.works.values()),
                    "coordinator_source_state": "UNKNOWN", "stale_observation_count": 0,
                })
            for wid in sorted(registry.works):
                w = registry.works[wid]
                emit("works", w.project_id, wid, {
                    "work_id": wid, "project_id": w.project_id, "aim_id": w.aim_id,
                    "label_sha": w.label_sha, "issue_ref": w.issue_ref,
                    "acceptance_status": w.acceptance_status,
                    "candidate_pr_ref": w.candidate_pr_ref,
                    "candidate_head_sha": w.candidate_head_sha,
                    "ci_status": "UNKNOWN", "reported_done": None, "tasks_total": None,
                    "evidenced_tasks": None, "accepted_ac": None,
                })

            # Explicitly sorted trusted snapshots. No tab-only or chat-only joins.
            sorted_snaps = sorted(observation_snapshots,
                key=lambda s: (s.get("project_id",""), s.get("coordinator_id",""),
                               s.get("session_id",""), s.get("source_watermark","")))
            observed_assignments = set()
            for snap in sorted_snaps:
                pid = snap.get("project_id")
                if pid not in registry.projects:
                    raise ValueError("Unregistered coordinator project")
                cycle = snap.get("cycle_seconds", 900)
                if not isinstance(cycle, int) or cycle < 1:
                    raise ValueError("Invalid cycle")
                fresh = age_state(snap.get("generated_at_utc"), as_of_utc, cycle)
                for n, obs in enumerate(snap.get("observations", [])):
                    if not all(isinstance(obs.get(k), str) for k in CELLS):
                        raise ValueError("Missing authoritative ten-cell observation")
                    resolved = CompositeBindingResolver.resolve(
                        obs, pid, snap["coordinator_id"], snap["session_id"], registry)
                    # A snapshot can be fresh even when the last probe failed.
                    live = LivenessEvaluator.evaluate(
                        obs.get("probe_status","UNKNOWN"), obs.get("last_probe_at_utc"),
                        as_of_utc, cycle)
                    if fresh != "FRESH" and live == "ALIVE":
                        live = "STALE"
                    aid, wid = resolved.get("assignment_id"), resolved.get("work_id")
                    run_id = None
                    lane_id = None
                    if aid:
                        runs = [r for r in registry.runs.values()
                                if r.assignment_id == aid and
                                r.chat_id == obs.get("chat_id") and
                                r.generation == obs.get("binding_generation")]
                        if len(runs) != 1:
                            aid, wid = None, None
                        else:
                            run_id = runs[0].run_id
                            lane_id = registry.assignments[aid].lane_id
                    envelope = dict(obs)
                    envelope.update({
                        "project_id": pid, "coordinator_id": snap["coordinator_id"],
                        "session_id": snap["session_id"],
                        "snapshot_source_digest": snap["source_digest"],
                        "source_watermark": snap["source_watermark"],
                        "snapshot_freshness": fresh, "agent_probe_freshness": live,
                        "assignment_id": aid, "work_id": wid, "run_id": run_id,
                        "lane_id": lane_id,
                        "conflicts": sorted(set(resolved.get("conflicts", []))),
                    })
                    key = "|".join([snap["coordinator_id"],snap["session_id"],
                                    str(obs.get("tab_position","")),str(obs.get("chat_id","")),
                                    str(obs.get("binding_generation","")),str(n).zfill(5)])
                    if aid and run_id:
                        observed_assignments.add(aid)
                        envelope["assignment_state"] = registry.assignments[aid].status
                        emit("assignments", pid, key, envelope)
                    else:
                        envelope["conflicts"] = sorted(set(envelope["conflicts"] + ["UNATTRIBUTED_TAB"]))
                        emit("unassigned_observations", pid, key, envelope)
                    kind = obs.get("probe_status")
                    anomalies = []
                    if kind in ("LOADFAIL", "NOBOX", "UNUSUAL", "TIMEOUT", "ERROR"):
                        anomalies.append("PROBE_FAILURE")
                    if fresh == "STALE" or live == "STALE":
                        anomalies.append("STALE_OBSERVATION")
                    if resolved.get("conflicts"):
                        anomalies.append("IDENTITY_CONFLICT")
                    for k in anomalies:
                        emit("recovery", pid, key+"|"+k, {
                            "anomaly_type": k, "project_id": pid, "assignment_id": aid,
                            "run_id": run_id, "source_ref": snap["source_digest"],
                            "detected_at_utc": as_of_utc, "coordinator_next": obs["next"],
                            "probe_status": kind, "status_verbatim": obs["status"],
                            "source_watermark": snap["source_watermark"],
                        })

            # Preserve missing-run visibility without declaring agents OFFLINE.
            for aid, a in sorted(registry.assignments.items()):
                if aid not in observed_assignments and a.status == "ACTIVE":
                    lane = registry.lanes[a.lane_id]
                    work = registry.works[lane.work_id]
                    emit("recovery", work.project_id, "no-snapshot|"+aid, {
                        "anomaly_type": "NO_CURRENT_OBSERVATION", "project_id": work.project_id,
                        "assignment_id": aid, "run_id": None, "source_ref": None,
                        "detected_at_utc": as_of_utc, "coordinator_next": None,
                        "probe_status": "UNKNOWN", "status_verbatim": None,
                        "source_watermark": None,
                    })

            # Source WP1 records in cursor-sized batches; no whole-table fetchall.
            with evidence_index._lock:
                src = evidence_index._get_connection().execute(
                    """SELECT project_id, provider_comment_id, task_id, owner_issue, candidate_sha,
                              author, created_at, updated_at, content_sha, proof_url,
                              is_canonical_8line, raw_text, version, evidence_id
                       FROM task_evidence WHERE is_active_version=1
                       ORDER BY project_id, provider_comment_id, version""")
                while True:
                    chunk = src.fetchmany(200)
                    if not chunk:
                        break
                    for ev in chunk:
                        row = dict(ev)
                        pid = row["project_id"]
                        if pid not in registry.projects:
                            continue
                        match, conflicts = _evidence_match(registry, task_attributions, row)
                        parsed, status = CanonicalV36Adapter.parse(row["raw_text"])
                        if status != "PARSED" or not row["is_canonical_8line"]:
                            match = None
                            conflicts = sorted(set(conflicts + ["INVALID_CANONICAL_EVIDENCE"]))
                        out = {
                            "evidence_id": row["evidence_id"],
                            "project_id": pid, "task_id": row["task_id"],
                            "child_issue": row["owner_issue"],
                            "provider_comment_id": row["provider_comment_id"],
                            "source_ref": row["proof_url"], "content_sha": row["content_sha"],
                            "candidate_sha": row["candidate_sha"] or None,
                            "candidate_text": parsed["candidate"] if parsed else None,
                            "parsed_canonical": status == "PARSED",
                            "validator_verdict": None, "author": row["author"],
                            "created_at": row["created_at"], "updated_at": row["updated_at"],
                            "version": row["version"],
                            "work_id": match["work_id"] if match else None,
                            "assignment_id": match["assignment_id"] if match else None,
                            "run_id": match["run_id"] if match else None,
                            "attribution": "ATTRIBUTED" if match else "UNATTRIBUTED",
                            "conflicts": conflicts,
                        }
                        emit("evidence", pid, "|".join([row["provider_comment_id"].zfill(20),
                            str(row["version"]).zfill(8)]), out)
                        if match:
                            seen_task_by_work.setdefault(match["work_id"], set()).add(
                                (row["task_id"], row["owner_issue"]))

            # Store count of distinct evidenced tasks only where an explicit mapping exists.
            # Work data are replaced, keeping all unsupported plan/Owner fields null.
            for wid, tasks in sorted(seen_task_by_work.items()):
                w = registry.works[wid]
                old = conn.execute("""SELECT body FROM projection_rows WHERE generation='__staging__'
                                      AND view='works' AND project_id=? AND sort_key=?""",
                                   (w.project_id, wid)).fetchone()[0]
                new = json.loads(old)
                new["evidenced_tasks"] = len(tasks)
                conn.execute("""UPDATE projection_rows SET body=? WHERE generation='__staging__'
                                AND view='works' AND project_id=? AND sort_key=?""",
                             (canon(new), w.project_id, wid))

            # Final digest is of ordered FINAL rows and explicit source/clock vector.
            h = hashlib.sha256()
            h.update(canon({"as_of_utc":as_of_utc,"source_watermarks":source_watermarks}).encode())
            scan = conn.execute("""SELECT view, project_id, sort_key, body FROM projection_rows
                                  WHERE generation='__staging__'
                                  ORDER BY view,project_id,sort_key""")
            while True:
                batch = scan.fetchmany(200)
                if not batch:
                    break
                for v,p,k,b in batch:
                    h.update(canon([v,p,k,json.loads(b)]).encode("utf-8"))
            generation = h.hexdigest()
            conn.execute("DELETE FROM projection_rows WHERE generation != '__staging__'")
            conn.execute("DELETE FROM projection_meta")
            conn.execute("UPDATE projection_rows SET generation=? WHERE generation='__staging__'",
                         (generation,))
            conn.execute("""INSERT INTO projection_meta VALUES(?,?,?,?,?)""", (
                generation, generation, as_of_utc, canon(source_watermarks),
                datetime.now(timezone.utc).isoformat()))
            conn.commit()
            return {"generation": generation, "projection_digest": generation,
                    "as_of_utc": as_of_utc, "counts": counts}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class ProjectionQueryService:
    """Never creates a DB. Only reads a pre-materialized projection generation."""

    def __init__(self, db_path: str):
        self.db_path = str(db_path)

    @staticmethod
    def _decode(cursor: str) -> dict:
        try:
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,4096}", cursor):
                raise ValueError("Malformed cursor")
            raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
            obj = json.loads(raw)
            if not isinstance(obj, dict) or set(obj) != {"generation","view","project","after"}:
                raise ValueError("Malformed cursor")
            return obj
        except Exception as exc:
            raise ValueError("Invalid projection cursor") from exc

    def page(self, view: str, project: Optional[str] = None,
             limit: int = 50, cursor: Optional[str] = None) -> dict:
        if view not in VIEWS or not isinstance(limit,int) or not 1 <= limit <= MAX_PAGE:
            raise ValueError("Invalid view or page limit")
        if project is not None and (not isinstance(project,str) or len(project)>256 or "\x00" in project):
            raise ValueError("Invalid project")
        from urllib.parse import quote
        path = Path(self.db_path)
        if not path.is_file():
            raise FileNotFoundError("Projection generation not available")
        conn = sqlite3.connect("file:"+quote(str(path.resolve()),safe="/:")+"?mode=ro",uri=True)
        conn.row_factory = sqlite3.Row
        try:
            meta = conn.execute("SELECT * FROM projection_meta LIMIT 1").fetchone()
            if meta is None:
                raise FileNotFoundError("Projection generation not available")
            gen = meta["generation"]
            after = ""
            if cursor:
                c = self._decode(cursor)
                if c["generation"] != gen:
                    raise LookupError("Expired projection generation")
                if (c["view"],c["project"]) != (view,project) or not isinstance(c["after"],str):
                    raise ValueError("Cursor filters do not match request")
                after = c["after"]
            filters = ["generation=?","view=?","sort_key>?"]
            values = [gen,view,after]
            if project is not None:
                filters.append("project_id=?");values.append(project)
            items = conn.execute(
                "SELECT sort_key,body FROM projection_rows WHERE "+
                " AND ".join(filters)+" ORDER BY sort_key LIMIT ?", values+[limit+1]).fetchall()
            has_more = len(items)>limit
            selected = items[:limit]
            next_cursor = None
            if has_more and selected:
                payload = {"generation":gen,"view":view,"project":project,
                           "after":selected[-1]["sort_key"]}
                next_cursor = base64.urlsafe_b64encode(canon(payload).encode()).decode().rstrip("=")
            return {"schema_version":"control_tower_projections_v1","generation":gen,
                    "projection_digest":meta["content_digest"],
                    "as_of_utc":meta["as_of_utc"],"view":view,"project_id":project,
                    "items":[json.loads(x["body"]) for x in selected],
                    "next_cursor":next_cursor}
        finally:
            conn.close()
