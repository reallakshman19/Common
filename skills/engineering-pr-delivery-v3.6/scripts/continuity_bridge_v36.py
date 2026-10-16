#!/usr/bin/env python3
"""Read-only reconciliation facade for native v3.6 C1 and coding addendum.

The issue_chain_v36 contract is the *only* 11-category continuity authority.
The addendum's historical hop renderer and advisory evidence selector are
views, never a second source of task completion, approval or publication.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import issue_chain_v36 as spine
import continuity_addendum_v36 as addendum


class BridgeError(ValueError):
    """The two reported-only views disagree about their owning issue."""


def project(document, *, lineage=None, inspect_protocol=False,
            project_protocol=None, explicit_protocol=None,
            governed_v36=False, has_issue=False):
    """Check the source-reported spine first and optionally enrich its view.

    No fetching or external authentication is performed here. In particular,
    a rendered issue link is NOT proof that the issue exists or was deleted.
    """
    report = spine.validate(document)
    owner_repo, issue_text = document["parent"].rsplit("#", 1)

    if lineage is not None:
        nodes = addendum.check_chain(lineage)
        if lineage["repository"] != owner_repo:
            raise BridgeError("LINEAGE_REPOSITORY_MISMATCH")
        if nodes[0]["issue"] != int(issue_text):
            raise BridgeError("LINEAGE_ROOT_ISSUE_MISMATCH")
        report["reported_issue_lineage"] = addendum.render_chain(lineage)
        report["lineage_status"] = "REPORTED_NOT_PROVIDER_VERIFIED"

    if inspect_protocol:
        # Two independently specified, conflicting governance schemes
        # cannot be resolved by selecting the more permissive route.
        if governed_v36 and project_protocol and project_protocol.casefold() not in (
                "v3.6", "native v3.6", "task_evidence v3.6"):
            report["evidence_routing"] = {
                "mode": "PROTOCOL_CONFLICT_HOLD", "required": False}
        else:
            report["evidence_routing"] = addendum.evidence_choice(
                explicit_protocol=explicit_protocol,
                project_protocol=project_protocol,
                governed_v36=governed_v36, has_issue=has_issue)
        report["evidence_routing"]["does_not_create_evidence"] = True

    report["projection_only"] = True
    report["may_publish"] = False
    report["may_count_for_native_o2"] = False
    report["may_grant_owner_acceptance"] = False
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--lineage", type=Path)
    p.add_argument("--inspect-protocol", action="store_true")
    p.add_argument("--governed-v36", action="store_true")
    p.add_argument("--project-protocol")
    p.add_argument("--explicit-protocol")
    p.add_argument("--has-issue", action="store_true")
    args = p.parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        lineage = (json.loads(args.lineage.read_text(encoding="utf-8"))
                   if args.lineage else None)
        out = project(document, lineage=lineage,
                      inspect_protocol=args.inspect_protocol,
                      governed_v36=args.governed_v36,
                      project_protocol=args.project_protocol,
                      explicit_protocol=args.explicit_protocol,
                      has_issue=args.has_issue)
    except (spine.ChainError, addendum.AddendumError, BridgeError,
            ValueError, TypeError, OSError) as exc:
        print(json.dumps({"status": "CONTINUITY_BRIDGE_BLOCKED",
                          "reason": str(exc), "may_publish": False,
                          "may_count_for_native_o2": False}))
        return 2
    print(json.dumps(out, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
