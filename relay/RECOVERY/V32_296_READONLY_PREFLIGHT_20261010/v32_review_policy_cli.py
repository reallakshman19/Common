#!/usr/bin/env python3
"""V3.2 D4/D5 GET-only visibility. Exit 0 is intentionally impossible."""
from __future__ import annotations

import argparse
from json import dumps

from v32_github_get import GitHubGetOnly
from v32_policy_visibility import observe_review_and_policy_visibility


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review/required-check policy visibility; never issue E")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args(argv)
    report = observe_review_and_policy_visibility(
        GitHubGetOnly(), repository=args.repository,
        pr_number=args.pr_number, expected_head=args.expected_head,
    )
    print(dumps(report.as_dict(), sort_keys=True, indent=2))
    return 1 if report.status == "FAILED_TARGET" else 2


if __name__ == "__main__":
    raise SystemExit(main())
