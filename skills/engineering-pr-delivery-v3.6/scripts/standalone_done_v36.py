#!/usr/bin/env python3
"""Read-only standalone A14 pre-DONE check; existing coordinator tools unchanged."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from decompose_v36 import load_plan
from lifecycle_v36 import load_label
from standalone_checklist_v36 import check_done, require_standalone
from standalone_activity_check_v36 import check_activity
from standalone_activity_v36 import SURFACES


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ('label', 'plan', 'task-id', 'issue-ref', 'candidate', 'criteria',
                 'criteria-sha256', 'self-check', 'repo', 'evidence-root'):
        cli.add_argument('--' + name, required=True)
    cli.add_argument("--agent-surface", choices=SURFACES, default="unknown")
    cli.add_argument("--activity-log")
    cli.add_argument("--activity-session-id")
    args = cli.parse_args(argv)
    try:
        label = require_standalone(load_label(args.label))
        plan = load_plan(args.plan, label)
        # Decode bytes explicitly: do not normalize CRLF or strip an input BOM.
        body = Path(args.self_check).read_bytes().decode("utf-8")
        result = check_done(
            label=label, plan=plan, task_id=args.task_id, issue_ref=args.issue_ref,
            candidate=args.candidate,
            criteria_text=Path(args.criteria).read_bytes().decode('utf-8'),
            criteria_sha256=args.criteria_sha256,
            body=body,
            repo=Path(args.repo), evidence_root=Path(args.evidence_root))
        activity, gaps = check_activity(
            args.agent_surface, args.activity_log, args.activity_session_id,
            body)
        result['activity'] = activity
        result['gaps'].extend(gaps)
        result['declaration_consistent'] = result['declaration_consistent'] and not gaps
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result['declaration_consistent'] else 1
    except (ValueError, OSError, RuntimeError) as exc:
        print(json.dumps({'mode': 'standalone', 'declaration_consistent': False,
                          'owner_accepted': False, 'error': str(exc)}, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
