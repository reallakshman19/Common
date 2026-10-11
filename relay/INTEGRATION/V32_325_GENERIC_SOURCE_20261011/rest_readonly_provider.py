"""Bounded GitHub GET-envelope compatibility adapter for T01/T02.

This module performs no network I/O or writes. The caller injects three GET
callables, establishes the endpoint repository and its authorization separately,
and retains all original provider provenance. This adapter never authenticates
an Owner graph or admits facts; it only normalizes public response *shape*.

Supports nested GitHub REST pull fields and the flattened metadata returned by
the connected GitHub read interface. In flattened mode the base repository is
bound to the explicitly requested /repos/{owner}/{repo}/pulls/{number}
endpoint, not inferred from a foreign head repository or issue text.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Callable

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA = re.compile(r"^[0-9a-f]{40}$")


class RestContractHold(ValueError):
    """Fail closed with a non-secret code; do not echo issue/PR bodies."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise RestContractHold(code)


def _payload(value: Any, wrapper: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), "REST_SOURCE_NOT_MAPPING")
    raw = value.get(wrapper, value)
    _require(isinstance(raw, Mapping), "REST_SOURCE_NOT_MAPPING")
    return raw


class BoundReadOnlyGitHubProvider:
    """Normalize three explicitly injected repository-scoped GET functions.

    Inputs are real observations only when the caller actually uses an
    authenticated/repository-scoped transport; a test-replayed envelope is
    *not* an independent source or evidence proof.
    """

    def __init__(
        self,
        *, repository: str, base_ref: str,
        read_issue: Callable[[int], Any],
        read_pull: Callable[[int], Any],
        read_commit_sha: Callable[[str], str],
    ) -> None:
        _require(isinstance(repository, str) and _REPO.fullmatch(repository) is not None,
                 "REST_REPOSITORY_INVALID")
        _require(isinstance(base_ref, str) and bool(base_ref.strip()),
                 "REST_BASE_REF_INVALID")
        _require(all(callable(fn) for fn in (read_issue, read_pull, read_commit_sha)),
                 "REST_GET_READER_REQUIRED")
        self.repository = repository
        self.base_ref = base_ref
        self._read_issue = read_issue
        self._read_pull = read_pull
        self._read_commit_sha = read_commit_sha

    def get_commit_sha(self, ref: str) -> str:
        _require(ref == self.base_ref, "REST_BASE_REF_UNBOUND")
        sha = self._read_commit_sha(ref)
        _require(isinstance(sha, str) and _SHA.fullmatch(sha) is not None,
                 "REST_BASE_SHA_INVALID")
        return sha

    def get_issue(self, number: int) -> dict[str, Any]:
        _require(type(number) is int and number > 0, "REST_ISSUE_SELECTION_INVALID")
        raw = _payload(self._read_issue(number), "issue")
        # GitHub REST uses 'number'; the connected fetch_issue reader returns
        # 'issue_number'. Accept either explicit source field, never guessing.
        issue_no = raw.get("number", raw.get("issue_number"))
        _require(type(issue_no) is int and issue_no == number and
                 (raw.get("number") is None or raw["number"] == issue_no) and
                 (raw.get("issue_number") is None or raw["issue_number"] == issue_no),
                 "REST_ISSUE_IDENTITY_MISMATCH")
        _require(raw.get("state") in ("open", "closed")
                 and isinstance(raw.get("title"), str) and bool(raw["title"].strip())
                 and isinstance(raw.get("body"), (str, type(None))),
                 "REST_ISSUE_SURFACE_INVALID")
        return {"number": issue_no, "state": raw["state"],
                "title": raw["title"], "body": raw.get("body")}

    def get_pull(self, number: int) -> dict[str, Any]:
        _require(type(number) is int and number > 0, "REST_PR_SELECTION_INVALID")
        raw = _payload(self._read_pull(number), "pull_request")
        _require(type(raw.get("number")) is int and raw["number"] == number,
                 "REST_PR_IDENTITY_MISMATCH")
        _require(raw.get("state") in ("open", "closed")
                 and type(raw.get("draft")) is bool and type(raw.get("merged")) is bool
                 and isinstance(raw.get("title"), str) and bool(raw["title"].strip())
                 and isinstance(raw.get("body"), (str, type(None))),
                 "REST_PR_SURFACE_INVALID")

        head, base = raw.get("head"), raw.get("base")
        if isinstance(head, Mapping) and isinstance(base, Mapping):
            head_repo = (head.get("repo") or {}).get("full_name") if isinstance(head.get("repo"), Mapping) else None
            base_repo = (base.get("repo") or {}).get("full_name") if isinstance(base.get("repo"), Mapping) else None
            head_sha, base_ref = head.get("sha"), base.get("ref")
            base_sha = base.get("sha")
        else:
            # Connected GitHub reader's compact PR result: API endpoint was
            # selected by repository; missing head_repo_full_name is a HOLD.
            head_repo = raw.get("head_repo_full_name")
            base_repo = self.repository
            head_sha, base_ref = raw.get("head_sha"), raw.get("base")
            base_sha = raw.get("base_sha")

        _require(isinstance(head_repo, str)
                 and head_repo.casefold() == self.repository.casefold(),
                 "REST_HEAD_REPOSITORY_MISMATCH")
        _require(isinstance(base_repo, str)
                 and base_repo.casefold() == self.repository.casefold(),
                 "REST_BASE_REPOSITORY_MISMATCH")
        _require(isinstance(base_ref, str) and base_ref == self.base_ref,
                 "REST_BASE_REF_MISMATCH")
        _require(isinstance(head_sha, str) and _SHA.fullmatch(head_sha) is not None,
                 "REST_HEAD_SHA_INVALID")
        _require(isinstance(base_sha, str) and _SHA.fullmatch(base_sha) is not None,
                 "REST_PR_BASE_SHA_INVALID")
        return {
            "number": number, "state": raw["state"], "merged": raw["merged"],
            "draft": raw["draft"], "title": raw["title"], "body": raw.get("body"),
            "head": {"sha": head_sha, "repo": {"full_name": head_repo}},
            "base": {"ref": base_ref, "repo": {"full_name": base_repo}},
        }
