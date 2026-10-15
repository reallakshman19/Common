#!/usr/bin/env python3
"""WP2 v3.6 semantic adapter: index/child LINK evidence only, not owner acceptance.

Inputs are the read-only provider collector's internally retained index bodies.
This does NOT import existing v3.6 code, recompute O1-O5 progress or execute prompts.
"""
from __future__ import annotations

import re

MARKER = re.compile(r"<!-- v36-plan-index:(V36-[0-9]+-PLAN-[0-9]+) parent:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*) -->")
CHILD_LINK = re.compile(
    r"\[[^]\n]*\]\(https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)\)"
)


def interpret_index(provider_snapshot, expected_plan=None):
    if not isinstance(provider_snapshot, dict):
        raise ValueError("provider snapshot required")
    repo = provider_snapshot.get("repository")
    number = provider_snapshot.get("issue_number")
    if not isinstance(repo, str) or type(number) is not int or number < 1:
        raise ValueError("target scope missing")
    candidates = provider_snapshot.get("v36_index_candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("managed index candidates unavailable")
    entries = []
    for item in candidates:
        if not isinstance(item, dict) or not isinstance(item.get("body"), str):
            raise ValueError("a raw index body is needed for local correlation")
        matches = MARKER.findall(item["body"])
        for plan, parent_repo, parent_number in matches:
            if expected_plan is not None and plan != expected_plan:
                continue
            if parent_repo != repo or int(parent_number) != number:
                raise ValueError("managed index claims wrong parent")
            numbers = []
            for child_repo, child in CHILD_LINK.findall(item["body"]):
                if child_repo != repo:
                    raise ValueError("managed index contains cross-repository child")
                if int(child) == number:
                    raise ValueError("managed index points at own parent")
                numbers.append(int(child))
            if len(numbers) != len(set(numbers)):
                raise ValueError("duplicated index child link")
            entries.append({
                "plan": plan,
                "parent": repo + "#" + str(number),
                "index_comment_id": item.get("comment_id"),
                "index_body_sha256": item.get("body_digest"),
                "children": sorted(numbers),
                "index_authorship_verified": False,
                "plan_label_verified": False,
                "child_issue_verified": False,
                "task_evidence_verified": False,
                "owner_accepted": False,
            })
    if len(entries) > 1:
        raise ValueError("ambiguous managed parent indices")
    if not entries:
        return {"schema": "onboarding.v36-index-projection/v1",
                "status": "INDEX_NOT_VERIFIED",
                "parent": repo + "#" + str(number),
                "entry": None,
                "execution_authorized": False}
    return {"schema": "onboarding.v36-index-projection/v1",
            "status": "INDEX_LINKS_OBSERVED_NOT_VERIFIED",
            "parent": repo + "#" + str(number),
            "entry": entries[0],
            "execution_authorized": False}
