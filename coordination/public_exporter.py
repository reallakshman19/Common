"""Control Tower WP4: Sanitized Public Snapshot Exporter.

Produces leak-free, allowlist-only CONTROL_TOWER_PUBLIC_SNAPSHOT_V1 artifacts
for static hosting on GitHub Pages from pre-materialized WP3 projection read tables.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from coordination.projections import ProjectionQueryService, canon


class PrivacyViolationError(SecurityError if "SecurityError" in dir(__builtins__) else Exception):
    """Raised when sensitive data (tokens, private paths, forbidden keys) leaks into export."""
    pass


class GenerationShiftError(RuntimeError):
    """Raised when underlying projection generation changes repeatedly during export."""
    pass


class PolicyViolationError(ValueError):
    """Raised when publication policy is violated (e.g., unauthorized project)."""
    pass


SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{36,}"),
    re.compile(r"gho_[A-Za-z0-9_]{36,}"),
    re.compile(r"ghu_[A-Za-z0-9_]{36,}"),
    re.compile(r"ghs_[A-Za-z0-9_]{36,}"),
    re.compile(r"ghr_[A-Za-z0-9_]{36,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]+=*", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
]

LOCAL_PATH_PATTERNS = [
    re.compile(r"[a-zA-Z]:\\(?:Users|Documents|antigravity)[^\s\"',;>]*", re.IGNORECASE),
    re.compile(r"/(?:Users|home)/[^\s\"',;>]*", re.IGNORECASE),
]

FORBIDDEN_KEY_NAMES: Set[str] = {
    "token", "password", "secret", "private_key", "chat_id", "coordination_dir"
}

ALLOWED_PUBLIC_DOMAINS = {
    "github.com",
    "raw.githubusercontent.com",
}

PORTFOLIO_ALLOWLIST = (
    "project_id", "name", "verified_repo_id", "provider_reachability",
    "provider_observed_at_utc", "work_count", "registered_assignments",
    "registered_active_assignments", "coordinator_source_state",
    "stale_observation_count", "evidence_count", "latest_evidence_at_utc"
)

WORKS_ALLOWLIST = (
    "work_id", "project_id", "aim_id", "label_sha", "issue_ref",
    "acceptance_status", "candidate_pr_ref", "candidate_head_sha",
    "ci_status", "reported_done", "tasks_total", "evidenced_tasks",
    "accepted_ac", "pr_check_observations"
)

ASSIGNMENTS_ALLOWLIST = (
    "tab", "status", "aim", "plan", "ac", "ci", "meter", "due",
    "checked", "next", "probe_status", "project_id", "snapshot_freshness",
    "agent_probe_freshness", "assignment_id", "work_id", "run_id",
    "lane_id", "latest_task_id", "latest_candidate_sha",
    "latest_evidence_verdict", "latest_evidence_source_ref",
    "conflicts", "assignment_state"
)

EVIDENCE_ALLOWLIST = (
    "evidence_id", "project_id", "task_id", "child_issue",
    "provider_comment_id", "source_ref", "content_sha", "candidate_sha",
    "candidate_text", "parsed_canonical", "validator_verdict", "author",
    "created_at", "updated_at", "version", "work_id", "assignment_id",
    "run_id", "attribution", "conflicts"
)

RECOVERY_ALLOWLIST = (
    "anomaly_type", "project_id", "assignment_id", "run_id",
    "detected_at_utc", "coordinator_next", "probe_status", "status_verbatim"
)

SCHEMA_PATH = Path(__file__).parent / "schemas" / "control_tower_public_snapshot_v1.schema.json"


class URLSanitizer:
    """Validates and sanitizes links exposed in public snapshots."""

    @staticmethod
    def sanitize(url: Optional[str]) -> Optional[str]:
        if not url or not isinstance(url, str):
            return None
        stripped = url.strip()
        if not stripped.startswith("https://"):
            return None
        try:
            parsed = urlparse(stripped)
            if parsed.scheme != "https" or not parsed.netloc:
                return None
            host = parsed.netloc.lower()
            if host in ALLOWED_PUBLIC_DOMAINS or host.endswith(".github.com"):
                return stripped
        except Exception:
            return None
        return None


class PrivacyValidator:
    """Strict, recursive fail-closed leak detector for public exports."""

    @classmethod
    def assert_no_leaks(cls, data: Any, path: str = "$") -> None:
        if isinstance(data, dict):
            for k, v in data.items():
                if k in FORBIDDEN_KEY_NAMES:
                    raise PrivacyViolationError(
                        f"Forbidden private key '{k}' present in export at {path}.{k}"
                    )
                cls.assert_no_leaks(v, f"{path}.{k}")
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                cls.assert_no_leaks(item, f"{path}[{idx}]")
        elif isinstance(data, str):
            for pat in SECRET_PATTERNS:
                if pat.search(data):
                    raise PrivacyViolationError(
                        f"Secret token pattern detected at {path}: [REDACTED_SECRET]"
                    )
            for pat in LOCAL_PATH_PATTERNS:
                if pat.search(data):
                    raise PrivacyViolationError(
                        f"Local filesystem path pattern detected at {path}: [REDACTED_LOCAL_PATH]"
                    )


def _validate_schema(instance: dict) -> None:
    """Validates public snapshot against control_tower_public_snapshot_v1 schema."""
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    # Lightweight stdlib-only validation of required root keys and types
    required = schema.get("required", [])
    for req in required:
        if req not in instance:
            raise ValueError(f"Public snapshot missing required property: {req}")

    allowed_properties = set(schema.get("properties", {}).keys())
    for key in instance.keys():
        if key not in allowed_properties:
            raise ValueError(f"Public snapshot contains forbidden property: {key}")


def _project_entity(entity: dict, allowlist: tuple) -> dict:
    """Projects entity strictly against allowlist, omitting non-matching keys."""
    return {k: entity[k] for k in allowlist if k in entity}


def export_public_snapshot(
    projection_db_path: str | Path,
    output_path: str | Path,
    approved_projects: List[str] | Set[str],
    policy_version: str = "v1.0.0",
    fixed_clock: Optional[str] = None,
    max_evidence: int = 500
) -> dict:
    """
    Exports a sanitized, deterministic CONTROL_TOWER_PUBLIC_SNAPSHOT_V1 JSON file
    from a precomputed WP3 materialized projection database.
    
    Guarantees:
    - Bounded keyset cursor pagination with 1-retry generation shift (410) recovery.
    - Strict allowlist filtering per view.
    - Withholding of private coordinator Next instructions.
    - Deep leak validation failing closed on any token or local path.
    - Atomic write via temporary file replacement.
    """
    approved = set(approved_projects)
    if not approved:
        raise PolicyViolationError("No approved projects specified for public export")

    db_path = Path(projection_db_path)
    if not db_path.is_file():
        raise FileNotFoundError(f"Projection database not found at {db_path}")

    target_out = Path(output_path).resolve()
    target_out.parent.mkdir(parents=True, exist_ok=True)
    temp_out = target_out.with_name(f"{target_out.name}.tmp.{os.getpid()}")

    for attempt in range(2):
        query_service = ProjectionQueryService(str(db_path))
        try:
            # Stage 1 & 2: Read generation and project each view
            # Page portfolio to inspect generation and watermarks
            init_page = query_service.page("portfolio", limit=1)
            generation = init_page["generation"]
            as_of_utc = init_page["as_of_utc"]

            # 1. Portfolio View
            portfolio_items = []
            cur = None
            while True:
                p_resp = query_service.page("portfolio", limit=200, cursor=cur)
                if p_resp["generation"] != generation:
                    raise LookupError("Generation shifted during portfolio paging")
                for item in p_resp["items"]:
                    if item.get("project_id") in approved:
                        portfolio_items.append(_project_entity(item, PORTFOLIO_ALLOWLIST))
                cur = p_resp.get("next_cursor")
                if not cur:
                    break

            # 2. Works View
            works_items = []
            for pid in sorted(approved):
                cur = None
                while True:
                    w_resp = query_service.page("works", project=pid, limit=200, cursor=cur)
                    if w_resp["generation"] != generation:
                        raise LookupError("Generation shifted during works paging")
                    for item in w_resp["items"]:
                        proj = _project_entity(item, WORKS_ALLOWLIST)
                        proj["issue_ref"] = URLSanitizer.sanitize(proj.get("issue_ref"))
                        proj["candidate_pr_ref"] = URLSanitizer.sanitize(proj.get("candidate_pr_ref"))
                        works_items.append(proj)
                    cur = w_resp.get("next_cursor")
                    if not cur:
                        break

            # 3. Assignments View
            assignments_items = []
            for pid in sorted(approved):
                cur = None
                while True:
                    a_resp = query_service.page("assignments", project=pid, limit=200, cursor=cur)
                    if a_resp["generation"] != generation:
                        raise LookupError("Generation shifted during assignments paging")
                    for item in a_resp["items"]:
                        proj = _project_entity(item, ASSIGNMENTS_ALLOWLIST)
                        # Explicitly withhold private coordinator Next in public export
                        proj["next"] = "[WITHHELD_PRIVATE_COORDINATOR_NEXT]"
                        proj["latest_evidence_source_ref"] = URLSanitizer.sanitize(
                            proj.get("latest_evidence_source_ref")
                        )
                        assignments_items.append(proj)
                    cur = a_resp.get("next_cursor")
                    if not cur:
                        break

            # 4. Unassigned Observations Count Summary
            unassigned_count = 0
            for pid in sorted(approved):
                cur = None
                while True:
                    u_resp = query_service.page("unassigned_observations", project=pid, limit=200, cursor=cur)
                    if u_resp["generation"] != generation:
                        raise LookupError("Generation shifted during unassigned_observations paging")
                    unassigned_count += len(u_resp["items"])
                    cur = u_resp.get("next_cursor")
                    if not cur:
                        break

            # 5. Evidence View (Bounded)
            evidence_items = []
            for pid in sorted(approved):
                cur = None
                while True:
                    e_resp = query_service.page("evidence", project=pid, limit=200, cursor=cur)
                    if e_resp["generation"] != generation:
                        raise LookupError("Generation shifted during evidence paging")
                    for item in e_resp["items"]:
                        if len(evidence_items) >= max_evidence:
                            break
                        proj = _project_entity(item, EVIDENCE_ALLOWLIST)
                        proj["source_ref"] = URLSanitizer.sanitize(proj.get("source_ref"))
                        evidence_items.append(proj)
                    if len(evidence_items) >= max_evidence:
                        break
                    cur = e_resp.get("next_cursor")
                    if not cur:
                        break
                if len(evidence_items) >= max_evidence:
                    break

            # 6. Recovery View
            recovery_items = []
            for pid in sorted(approved):
                cur = None
                while True:
                    r_resp = query_service.page("recovery", project=pid, limit=200, cursor=cur)
                    if r_resp["generation"] != generation:
                        raise LookupError("Generation shifted during recovery paging")
                    for item in r_resp["items"]:
                        proj = _project_entity(item, RECOVERY_ALLOWLIST)
                        # Withhold coordinator_next in public export
                        proj["coordinator_next"] = (
                            "[WITHHELD_PRIVATE_COORDINATOR_NEXT]" if proj.get("coordinator_next") else None
                        )
                        recovery_items.append(proj)
                    cur = r_resp.get("next_cursor")
                    if not cur:
                        break

            # Sort items deterministically
            portfolio_items.sort(key=lambda x: x["project_id"])
            works_items.sort(key=lambda x: (x["project_id"], x["work_id"]))
            assignments_items.sort(key=lambda x: (x["project_id"], x["assignment_id"]))
            evidence_items.sort(key=lambda x: (x["project_id"], x["evidence_id"]))
            recovery_items.sort(key=lambda x: (x["project_id"], x.get("assignment_id") or "", x["anomaly_type"]))

            # Compute deterministic content digest excluding publication wall clock
            digest_content = {
                "source_generation": generation,
                "as_of_utc": as_of_utc,
                "policy_version": policy_version,
                "approved_projects": sorted(approved),
                "portfolio": portfolio_items,
                "works": works_items,
                "assignments": assignments_items,
                "unassigned_observations_summary": {"count": unassigned_count},
                "evidence": evidence_items,
                "recovery": recovery_items,
            }
            content_digest = hashlib.sha256(canon(digest_content).encode("utf-8")).hexdigest()

            now_iso = fixed_clock or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            snapshot_id = f"snap-{generation[:16]}"

            public_snapshot = {
                "schema_version": "control_tower_public_snapshot_v1",
                "snapshot_id": snapshot_id,
                "published_at_utc": now_iso,
                "as_of_utc": as_of_utc,
                "source_generation": generation,
                "content_digest": content_digest,
                "visibility": "PUBLIC",
                "policy_version": policy_version,
                "source_watermarks": {pid: as_of_utc for pid in sorted(approved)},
                "portfolio": portfolio_items,
                "works": works_items,
                "assignments": assignments_items,
                "unassigned_observations_summary": {"count": unassigned_count},
                "evidence": evidence_items,
                "recovery": recovery_items,
            }

            # Stage 3: Schema validation & Deep leak scan
            _validate_schema(public_snapshot)
            PrivacyValidator.assert_no_leaks(public_snapshot)

            # Stage 4: Atomic write
            with open(temp_out, "w", encoding="utf-8") as f:
                f.write(json.dumps(public_snapshot, indent=2, sort_keys=True, ensure_ascii=False))
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_out, target_out)
            return public_snapshot

        except LookupError:
            if temp_out.is_file():
                try:
                    temp_out.unlink()
                except OSError:
                    pass
            if attempt == 0:
                continue
            raise GenerationShiftError("Projection generation changed repeatedly during export")
        except Exception:
            if temp_out.is_file():
                try:
                    temp_out.unlink()
                except OSError:
                    pass
            raise


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Export sanitized public Control Tower snapshot")
    parser.add_argument("--projection-db", required=True, help="Path to pre-materialized projection_index.db")
    parser.add_argument("--output-json", required=True, help="Path to output public_snapshot.json")
    parser.add_argument("--approved-project", action="append", dest="approved_projects", required=True,
                        help="Approved project ID for public export (repeatable)")
    parser.add_argument("--policy-version", default="v1.0.0", help="Publication policy version")
    parser.add_argument("--max-evidence", type=int, default=500, help="Maximum evidence rows to include")
    args = parser.parse_args(argv)

    try:
        snap = export_public_snapshot(
            projection_db_path=args.projection_db,
            output_path=args.output_json,
            approved_projects=args.approved_projects,
            policy_version=args.policy_version,
            max_evidence=args.max_evidence
        )
        print(f"[SUCCESS] Exported public snapshot to {args.output_json} (digest: {snap['content_digest'][:12]}...)")
        return 0
    except Exception as exc:
        print(f"[ERROR] Failed to export public snapshot: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
