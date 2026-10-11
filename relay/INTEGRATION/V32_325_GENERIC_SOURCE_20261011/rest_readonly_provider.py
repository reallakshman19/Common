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


class BoundNativeReadOnlyGitHubProvider(BoundReadOnlyGitHubProvider):
    """Optional native T02 GET methods on the *existing* normalized provider.

    The caller supplies complete, repository-scoped comment observations and
    compare results through externally authenticated, GET-only callbacks.
    This class performs no I/O, does not implement pagination or attest that
    the caller included every page, and never accepts evidence or writes.
    Unlike the T01-only base class, missing native callbacks are a hard HOLD.
    """

    _MAX_COMMENTS = 1000
    _MAX_COMMENT_CHARS = 1_000_000
    _MAX_TOTAL_COMMENT_CHARS = 5_000_000
    _REF = re.compile(r"^[A-Za-z0-9_./-]{1,200}$")

    def __init__(
        self, *, read_comments: Callable[[int], Any],
        read_compare: Callable[[str, str], Any],
        allowed_candidate_refs: tuple[str, ...] = (),
        **three_get_args: Any,
    ) -> None:
        super().__init__(**three_get_args)
        _require(callable(read_comments) and callable(read_compare),
                 "REST_NATIVE_GET_READER_REQUIRED")
        _require(isinstance(allowed_candidate_refs, tuple) and
                 all(self._valid_ref(value) for value in allowed_candidate_refs),
                 "REST_NATIVE_CANDIDATE_REF_INVALID")
        self._read_comments = read_comments
        self._read_compare = read_compare
        self._allowed_commits = frozenset((self.base_ref, *allowed_candidate_refs))

    @classmethod
    def _valid_ref(cls, value: Any) -> bool:
        return (isinstance(value, str) and cls._REF.fullmatch(value) is not None
                and ".." not in value and not value.startswith(("/", "-"))
                and not value.endswith("/"))

    def get_commit_sha(self, ref: str) -> str:
        _require(ref in self._allowed_commits,
                 "REST_NATIVE_COMMIT_REF_UNBOUND")
        if ref == self.base_ref:
            return super().get_commit_sha(ref)
        sha = self._read_commit_sha(ref)
        _require(isinstance(sha, str) and _SHA.fullmatch(sha) is not None,
                 "REST_NATIVE_CANDIDATE_SHA_INVALID")
        return sha

    def list_comments(self, number: int) -> list[dict[str, Any]]:
        _require(type(number) is int and number > 0,
                 "REST_NATIVE_COMMENT_SELECTION_INVALID")
        payload = self._read_comments(number)
        # Both the native GitHub list and the connected all-pages reader can
        # supply an array. Pagination completeness is the caller's separate
        # obligation; this class cannot certify private source currentness.
        if isinstance(payload, Mapping):
            payload = payload.get("comments")
        _require(isinstance(payload, list) and
                 len(payload) <= self._MAX_COMMENTS,
                 "REST_NATIVE_COMMENTS_INVALID_OR_UNBOUNDED")
        output: list[dict[str, Any]] = []
        previous_id = 0
        total_chars = 0
        for comment in payload:
            _require(isinstance(comment, Mapping) and
                     type(comment.get("id")) is int and
                     comment["id"] > previous_id and
                     isinstance(comment.get("body"), str) and
                     isinstance(comment.get("user"), Mapping) and
                     isinstance(comment["user"].get("login"), str) and
                     bool(comment["user"]["login"]) and
                     isinstance(comment.get("author_association"), str),
                     "REST_NATIVE_COMMENT_SOURCE_INVALID")
            _require(len(comment["body"]) <= self._MAX_COMMENT_CHARS,
                     "REST_NATIVE_COMMENT_TEXT_UNBOUNDED")
            total_chars += len(comment["body"])
            _require(total_chars <= self._MAX_TOTAL_COMMENT_CHARS,
                     "REST_NATIVE_COMMENT_TOTAL_UNBOUNDED")
            previous_id = comment["id"]
            output.append(dict(comment))
        return output

    def compare(self, base: str, head: str) -> dict[str, int]:
        _require(base == self.base_ref and self._valid_ref(head) and
                 head in self._allowed_commits and head != base,
                 "REST_NATIVE_COMPARE_REF_UNBOUND")
        result = self._read_compare(base, head)
        _require(isinstance(result, Mapping) and
                 all(type(result.get(key)) is int and
                     0 <= result[key] <= 1_000_000_000
                     for key in ("ahead_by", "behind_by")),
                 "REST_NATIVE_COMPARE_RESPONSE_INVALID")
        return {"ahead_by": result["ahead_by"],
                "behind_by": result["behind_by"]}
