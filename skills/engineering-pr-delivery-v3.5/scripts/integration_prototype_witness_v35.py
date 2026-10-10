"""V3.5 prototype STEP-01: native GitHub source/currentness *observation*.

This is a read-only, fail-closed witness for one existing programme/child/PR.
It cannot select an execution graph, certify checks or admit evidence, grant a
Local writer, produce DELP credit, publish a scoreboard or authorize merging.
The existing R2-D cold-entry reader alone validates an Owner-selected graph.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping
from typing import Any

SHA = re.compile(r"^[a-f0-9]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
GRAPH_MARKER = "<!-- V35_GRAPH_SELECTION_APPROVAL_V1_BEGIN -->"
ROOT_MARKER = "<!-- V35_PARENT_OWNER_INTENT_BEGIN -->"
SCHEMA = "V35_PROTOTYPE_SOURCE_WITNESS_V1"


class WitnessInputError(ValueError):
    """Malformed request; do not perform any provider reads."""


def _identity(value: Any, number: int, uri: str) -> bool:
    return (isinstance(value, Mapping) and value.get("number") == number
            and value.get("html_url") == uri and "pull_request" not in value)


def _pull_identity(value: Any, number: int, uri: str, repo: str) -> bool:
    if not isinstance(value, Mapping) or value.get("number") != number or value.get("html_url") != uri:
        return False
    base = value.get("base") or {}
    head = value.get("head") or {}
    return (isinstance(base, Mapping) and isinstance(head, Mapping)
            and isinstance(base.get("repo"), Mapping)
            and isinstance(head.get("repo"), Mapping)
            and str(base["repo"].get("full_name") or "").casefold() == repo.casefold()
            and str(head["repo"].get("full_name") or "").casefold() == repo.casefold()
            and isinstance(head.get("sha"), str)
            and bool(SHA.fullmatch(head["sha"])))


def observe(transport: Any, *, root_issue: int, leaf_issue: int,
            pr_number: int, expected_head: str) -> dict[str, Any]:
    """Double-read native provider objects and delegate graph trust to R2-D.

    No input claim can establish OWNER/Local authority. Provider exceptions and
    inconsistent/moving objects are always HOLD, not a fabricated zero or PASS.
    """
    repo = getattr(transport, "repository", None)
    if not isinstance(repo, str) or not REPO.fullmatch(repo):
        raise WitnessInputError("invalid provider repository identity")
    if (any(type(n) is not int or n <= 0 for n in (root_issue, leaf_issue, pr_number))
            or root_issue == leaf_issue or not isinstance(expected_head, str)
            or not SHA.fullmatch(expected_head)):
        raise WitnessInputError("invalid root/leaf/PR/exact-head binding")

    root_url = f"https://github.com/{repo}/issues/{root_issue}"
    leaf_url = f"https://github.com/{repo}/issues/{leaf_issue}"
    pr_url = f"https://github.com/{repo}/pull/{pr_number}"
    result: dict[str, Any] = {
        "schema": SCHEMA, "repository": repo,
        "root_issue": root_issue, "leaf_issue": leaf_issue,
        "pr_number": pr_number, "expected_head": expected_head,
        "observed_head": None,
        "status": "HOLD_PROVIDER_UNVERIFIED",
        "provider_material": "UNKNOWN", "graph": "UNKNOWN",
        "effective_required_checks": "UNKNOWN",
        "positive_evidence_admission": "NOT_DERIVED",
        "delp_progress": "NOT_CALCULATED",
        "local_writer": "NOT_GRANTED_BY_WITNESS",
        "merge_authority": "NOT_GRANTED_BY_WITNESS",
        "github_writes": "NONE", "prototype_qualified": False,
    }
    try:
        root = transport.get_issue(root_issue)
        leaf = transport.get_issue(leaf_issue)
        first_pr = transport.get_pull(pr_number)
        if not _identity(root, root_issue, root_url) or not _identity(leaf, leaf_issue, leaf_url):
            result["status"] = "HOLD_ISSUE_IDENTITY_UNVERIFIED"
            return result
        if ROOT_MARKER not in str(root.get("body") or ""):
            result["status"] = "HOLD_ROOT_NOT_GOVERNED"
            return result
        if not _pull_identity(first_pr, pr_number, pr_url, repo):
            result["status"] = "HOLD_PR_IDENTITY_UNVERIFIED"
            return result
        first_head = first_pr["head"]["sha"]
        result["observed_head"] = first_head
        if first_head != expected_head:
            result["status"] = "HOLD_EXPECTED_HEAD_MOVED"
            return result
        if first_pr.get("state") != "open" or root.get("state") != "open" or leaf.get("state") != "open":
            result["status"] = "HOLD_SOURCE_LIFECYCLE_CHANGED"
            return result
        if transport.get_commit_sha(first_head) != first_head:
            result["status"] = "HOLD_COMMIT_NOT_RESOLVED"
            return result
        comments = transport.list_comments(root_issue)
        if not isinstance(comments, list) or any(not isinstance(c, Mapping) for c in comments):
            result["status"] = "HOLD_PROVIDER_COMMENTS_UNVERIFIED"
            return result
        approvals = [c for c in comments if GRAPH_MARKER in str(c.get("body") or "")]
        if not approvals:
            result["graph"] = "NO_TYPED_SELECTION_OBSERVED"
            decision = "HOLD_NO_PROVIDER_APPROVED_GRAPH"
        elif len(approvals) != 1:
            result["graph"] = "AMBIGUOUS_SELECTION"
            decision = "HOLD_AMBIGUOUS_GRAPH_SELECTION"
        else:
            # Never validate the graph from caller data: use the existing
            # immutable-graph/provider Owner gate and its DELP read model.
            from integration_cold_entry_v35 import reconstruct
            try:
                selected = reconstruct(transport, root_url)
                same = (selected.get("status") == "GOVERNED_GRAPH_PROVIDER_OBSERVED_READ_ONLY"
                        and selected.get("selected_leaf") == f"{repo.split('/')[-1]}#{leaf_issue}"
                        and selected.get("approved_pr") == pr_number
                        and selected.get("exact_head") == expected_head)
                result["graph"] = "SOURCE_VALIDATED_READ_ONLY" if same else "SCOPE_OR_HEAD_MISMATCH"
                decision = ("HOLD_LOCAL_AND_ACCEPTANCE_NOT_PROVEN" if same
                            else "HOLD_SELECTED_GRAPH_SCOPE_MISMATCH")
            except Exception:
                # This includes incomplete approval, stale source and provider
                # faults; do not turn them into a positive or an absent graph.
                result["graph"] = "VALIDATION_UNVERIFIED"
                decision = "HOLD_GRAPH_VALIDATION_UNVERIFIED"
        # Independent final source readback. An approval can be edited or
        # revoked while R2-D validates its original provider source; the same
        # applies to parent/leaf prose and PR metadata. No atomic snapshot is
        # offered by GitHub, so refuse any observed inconsistency.
        last_root = transport.get_issue(root_issue)
        last_leaf = transport.get_issue(leaf_issue)
        if last_root != root or last_leaf != leaf:
            result["status"] = "HOLD_ISSUE_MOVED_DURING_OBSERVATION"
            return result
        last_comments = transport.list_comments(root_issue)
        if last_comments != comments:
            result["status"] = "HOLD_COMMENTS_MOVED_DURING_OBSERVATION"
            return result
        last_pr = transport.get_pull(pr_number)
        if not _pull_identity(last_pr, pr_number, pr_url, repo):
            result["status"] = "HOLD_PR_READBACK_UNVERIFIED"
            return result
        if last_pr != first_pr:
            result["status"] = "HOLD_PR_MOVED_DURING_OBSERVATION"
            return result
        result["provider_material"] = "SOURCE_HEAD_DOUBLE_READ_MATCH"
        result["status"] = decision
        return result
    except Exception:
        # No guessed permission, effective CI policy, or successful validation.
        result["status"] = "HOLD_PROVIDER_READ_UNKNOWN"
        result["provider_material"] = "UNKNOWN"
        result["graph"] = "UNKNOWN"
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only V3.5 prototype STEP-01 source witness")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--root", required=True, type=int)
    parser.add_argument("--leaf", required=True, type=int)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args(argv)
    try:
        # R2-D approved graph verification needs the native immutable-file
        # and approval-comment GET methods, not just DELP.GhTransport.
        # ScoreboardTransport has these GETs; this witness calls no writes.
        from integration_scoreboard_publish_v35 import ScoreboardTransport
        value = observe(ScoreboardTransport(args.repository), root_issue=args.root,
                        leaf_issue=args.leaf, pr_number=args.pr,
                        expected_head=args.expected_head)
    except WitnessInputError as exc:
        print(f"V3.5 witness invalid request: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(value, sort_keys=True, indent=2))
    return 3 if value["status"].startswith("HOLD_") else 0


if __name__ == "__main__":
    raise SystemExit(main())
