"""Synthetic M2 handoff dataset for M1 loopback contract v1.0.0.

Never use fixture identity, reported claims or timestamps as live agent
observations, independent evidence review or Owner command receipt.

Usage:
  python -m coordination.master_panel.demo_fixture --db /tmp/dash-m1-demo.sqlite
  python -m coordination.master_panel.read_api --db /tmp/dash-m1-demo.sqlite --port 8777
  curl http://127.0.0.1:8777/api/master/v1/projects
  curl 'http://127.0.0.1:8777/api/master/v1/rows?project_id=common&limit=10'
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .models import SourceIdentity, SourceKind
from .report_parser import extract_report
from .storage import SourceStore


def seed_demo(db_path: str) -> dict:
    """Seed only synthetic public metadata; no network or private commands."""
    p = Path(db_path)
    if p.exists():
        raise FileExistsError("Use a new fixture path; preserve existing local data")
    p.parent.mkdir(parents=True, exist_ok=True)
    common = "reallakshman19/Common"
    stamp = "2026-10-14T01:00:00Z"
    envelope = {
        "protocol_version": "1.0.0", "message_id": "synthetic-msg-v1",
        "request_id": "synthetic-req-v1", "kind": "RESULT",
        "sender_id": "synthetic-regular-chatgpt", "status": "REPORTED",
        "target": {
            "project_id": "common", "work_id": "common-360-dash-master",
            "lane_id": "m1", "assignment_id": "dash-master-m1",
            "run_id": "synthetic-run-v1",
        },
        "repository": {"id": "1412133785", "name": common},
        "mailbox": {
            "repository": {"id": "1412133785", "name": common},
            "issue_number": 373, "visibility": "PUBLIC",
        },
        "basis": {"candidate": "1" * 40},
        "payload": {"text": "SYNTHETIC; not proof", "refs": [], "decision": None},
    }
    body = "```casp\n" + json.dumps(envelope, sort_keys=True) + "\n```"
    source = SourceIdentity(
        project_id="common", repo_id="1412133785",
        repo_full_name=common, kind=SourceKind.ISSUE_COMMENT,
        entity_id="999999999", revision_id=stamp,
        issue_number=373, comment_id="999999999",
        body_sha256=hashlib.sha256(body.encode()).hexdigest(),
        created_at_utc=stamp, updated_at_utc=stamp,
        url=f"https://github.com/{common}/issues/373#issuecomment-999999999",
    )
    store = SourceStore(str(p))
    try:
        store.observe(source, "synthetic-scan-1", extract_report(body, source))
        store.save_scan(
            project_id="common", repo_id="1412133785", scan_id="synthetic-scan-1",
            issue_page=1, issue_index=1, comment_page=1,
            status="REACHABLE", completed=True,
        )
        store.save_scan(
            project_id="aa3", repo_id="1363905693", scan_id="synthetic-scan-2",
            issue_page=1, issue_index=0, comment_page=1,
            status="RATE_LIMITED", failure_code=429, failure_kind="RATE_LIMIT",
        )
    finally:
        store.close()
    return {
        "fixture": "SYNTHETIC_NOT_LIVE", "schema_version": "1.0.0",
        "db": str(p),
        "expected_common_objects": 1,
        "expected_aa3_health": "RATE_LIMITED",
        "expected_unregistered_binding": "UNASSIGNED",
        "expected_independent_review": "UNKNOWN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    print(json.dumps(seed_demo(args.db), sort_keys=True))


if __name__ == "__main__":
    main()
