#!/usr/bin/env python3
"""Offline-authority-neutral read-only V3.2 source preflight.

Exit 0 is intentionally unreachable: it cannot certify production positive E.
Exit 2 = fail-closed HOLD; exit 1 = observed invalid source / target.
"""
from __future__ import annotations

import argparse
from json import dumps, loads
from pathlib import Path

from v32_github_get import GitHubGetOnly
from v32_provider_preflight import PreflightTarget, inspect_v32_read_only


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="V3.2 GET-only consistency preflight; never admits evidence or writes")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repository-id", required=True, type=int)
    parser.add_argument("--graph-path", required=True)
    parser.add_argument("--leaf-ref", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--expected-graph-digest")
    parser.add_argument("--facts-file", type=Path, help="Local author claim for classification only; never authoritative")
    args = parser.parse_args(argv)
    facts = None
    if args.facts_file is not None:
        try:
            facts = loads(args.facts_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            print(dumps({"status": "FAILED_INPUT", "reasons": ["FACTS_FILE_UNREADABLE"],
                         "accepted_evidence_count": None, "writer_authorized": False, "delp_invoked": False}))
            return 1
    report = inspect_v32_read_only(
        PreflightTarget(repository=args.repository, repository_id=args.repository_id,
                        graph_path=args.graph_path, leaf_ref=args.leaf_ref,
                        pr_number=args.pr_number,
                        expected_graph_sha256=args.expected_graph_digest),
        GitHubGetOnly(), facts,
    )
    print(dumps(report.as_dict(), sort_keys=True, indent=2))
    return 1 if report.status.startswith("FAILED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
