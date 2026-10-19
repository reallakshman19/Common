#!/usr/bin/env python3
"""Read-only standalone A14 pre-DONE check; existing coordinator tools unchanged."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from decompose_v36 import load_plan
from lifecycle_v36 import load_label
from standalone_checklist_v36 import check_done, require_standalone


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ('label', 'plan', 'task-id', 'issue-ref', 'candidate', 'criteria',
                 'criteria-sha256', 'self-check', 'repo', 'evidence-root'):
        cli.add_argument('--' + name, required=True)
    args = cli.parse_args(argv)
    try:
        label = require_standalone(load_label(args.label))
        plan = load_plan(args.plan, label)
        # Decode bytes explicitly: do not normalize CRLF or strip an input BOM.
        result = check_done(
            label=label, plan=plan, task_id=args.task_id, issue_ref=args.issue_ref,
            candidate=args.candidate,
            criteria_text=Path(args.criteria).read_bytes().decode('utf-8'),
            criteria_sha256=args.criteria_sha256,
            body=Path(args.self_check).read_bytes().decode('utf-8'),
            repo=Path(args.repo), evidence_root=Path(args.evidence_root))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result['declaration_consistent'] else 1
    except (ValueError, OSError, RuntimeError) as exc:
        print(json.dumps({'mode': 'standalone', 'declaration_consistent': False,
                          'owner_accepted': False, 'error': str(exc)}, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
