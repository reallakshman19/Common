#!/usr/bin/env python3
"""GET-only native V3.2 C6 source bridge; intentionally no success exit."""
from __future__ import annotations

import argparse
from json import dumps, loads
from pathlib import Path

from v32_c6_preview import inspect_v32_c6_read_only
from v32_github_get import GitHubGetOnly
from v32_provider_preflight import PreflightTarget


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="V3.2 native C6 preflight: HOLD only; never approve successor")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repository-id", type=int, required=True)
    parser.add_argument("--graph-path", required=True)
    parser.add_argument("--leaf-ref", required=True)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--expected-graph-digest")
    parser.add_argument("--frozen-basis-file", type=Path)
    args = parser.parse_args(argv)
    basis = None
    if args.frozen_basis_file is not None:
        try:
            basis = loads(args.frozen_basis_file.read_text(encoding="utf-8"))
            if not isinstance(basis, dict) or not all(isinstance(k, str) and isinstance(v, str) for k,v in basis.items()):
                raise ValueError("FROZEN_BASIS_FORMAT_INVALID")
        except (ValueError, OSError, UnicodeError):
            print(dumps({
                "status": "FAILED_INPUT", "reasons": ["FROZEN_BASIS_INVALID"],
                "native_c6_invoked": False, "accepted_evidence_count": None,
                "writer_authorized": False, "delp_admitted": False,
            }, sort_keys=True))
            return 1
    target = PreflightTarget(
        repository=args.repository, repository_id=args.repository_id,
        graph_path=args.graph_path, leaf_ref=args.leaf_ref,
        pr_number=args.pr_number, expected_graph_sha256=args.expected_graph_digest,
    )
    row = inspect_v32_c6_read_only(target, GitHubGetOnly(), frozen_basis=basis)
    print(dumps(row, indent=2, sort_keys=True))
    return 1 if row["status"].startswith("FAILED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
