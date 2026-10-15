#!/usr/bin/env python3
"""Pre-flight setup and verification for reallakshman19/relay-v36-stress-lab.

Verifies repository accessibility, label validity, and staging readiness.
Does NOT create the repository or perform live test writes until the Owner
explicitly approves Change Card CP-V36-STRESS-01 and provisions the lab.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from decompose_v36 import GithubClient
from lifecycle_v36 import ContractError, load_label, require_explicit_lab

STRESS_LAB_REPO = "reallakshman19/relay-v36-stress-lab"
DEFAULT_LABEL = "relay/AIM/V36-STRESS.yaml"


def check_lab_status(repo: str = STRESS_LAB_REPO, token: str | None = None) -> dict:
    """Safely check if the target stress lab repository exists and is accessible."""
    client = GithubClient(repo, token=token)
    try:
        data = client.request("GET", "")
        return {
            "repository": repo,
            "status": "ACCESSIBLE",
            "default_branch": data.get("default_branch", "main"),
            "is_empty": data.get("size", 0) == 0,
            "html_url": data.get("html_url")
        }
    except ContractError as exc:
        err_msg = str(exc)
        if "404" in err_msg or "Not Found" in err_msg:
            return {
                "repository": repo,
                "status": "NOT_PROVISIONED_404",
                "message": "Repository not found; execution remains on HOLD pending Owner repository creation."
            }
        return {
            "repository": repo,
            "status": "ERROR",
            "message": err_msg
        }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="v3.6 disposable stress lab pre-flight setup")
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--repo", default=STRESS_LAB_REPO)
    parser.add_argument("--check-only", action="store_true", default=True)
    args = parser.parse_args(argv)

    try:
        label = load_label(args.label)
        token = os.environ.get("GITHUB_TOKEN")
        status = check_lab_status(args.repo, token=token)

        scaffold_dir = Path(__file__).resolve().parents[1] / "fixtures" / "stress-lab-scaffold"
        scaffold_ready = scaffold_dir.exists() and (scaffold_dir / "README.md").exists()

        report = {
            "label": label["work"],
            "version": label["version"],
            "label_sha": label["label_sha"],
            "target_lab": args.repo,
            "lab_status": status["status"],
            "scaffold_staged": scaffold_ready,
            "details": status
        }
        print(json.dumps(report, indent=2))
        return 0
    except ContractError as exc:
        print(f"setup pre-flight error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
