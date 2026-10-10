"""Read-only GitHub CLI transport for the V3.2 #296 preflight.

Uses gh api --method GET only. No GitHub PATCH/POST, no credential
modification, no native R3 trust claim and no author/reviewer authority.
Not an independent attestation of the effective required-check policy.
"""
from __future__ import annotations

from base64 import b64decode
from json import loads
from re import fullmatch
from subprocess import run, CompletedProcess
from typing import Any, Callable, Mapping
from urllib.parse import quote


class GitHubReadError(OSError):
    pass


def _safe_repository(repo: str) -> bool:
    return (isinstance(repo, str) and
            fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) is not None and
            all(segment not in (".", "..") for segment in repo.split("/")))


class GitHubGetOnly:
    """Small independent GET transport; not evidence admission itself."""

    def __init__(self, runner: Callable[..., CompletedProcess[str]] = run):
        self._runner = runner

    def _get(self, path: str) -> Any:
        if not path.startswith("repos/") or any(c in path for c in "\n\r\x00"):
            raise GitHubReadError("UNSAFE_GITHUB_GET_PATH")
        try:
            result = self._runner(
                ["gh", "api", "--method", "GET", path],
                capture_output=True, text=True, check=False, timeout=30,
            )
        except (OSError, TimeoutError) as exc:
            raise GitHubReadError("GITHUB_GET_TRANSPORT_UNAVAILABLE") from exc
        if result.returncode != 0:
            raise GitHubReadError("GITHUB_GET_FAILED")
        try:
            return loads(result.stdout)
        except (ValueError, TypeError) as exc:
            raise GitHubReadError("GITHUB_GET_NON_JSON") from exc

    def _repo(self, repository: str) -> str:
        if not _safe_repository(repository):
            raise GitHubReadError("INVALID_REPOSITORY_SELECTOR")
        return "repos/" + repository

    def get_repository(self, repository: str) -> Mapping[str, Any]:
        value = self._get(self._repo(repository))
        if not isinstance(value, dict):
            raise GitHubReadError("REPOSITORY_RESPONSE_INVALID")
        return value

    def get_commit(self, repository: str, ref: str) -> Mapping[str, Any]:
        if not isinstance(ref, str) or not fullmatch(r"[A-Za-z0-9_./-]{1,200}", ref):
            raise GitHubReadError("INVALID_COMMIT_REF")
        value = self._get(self._repo(repository) + "/commits/" + quote(ref, safe=""))
        if not isinstance(value, dict):
            raise GitHubReadError("COMMIT_RESPONSE_INVALID")
        return value

    def get_file_bytes(self, repository: str, path: str, ref: str) -> bytes:
        if (not isinstance(path, str) or not path.endswith(".json") or len(path) > 256 or
                any(x in ("", ".", "..") for x in path.split("/"))):
            raise GitHubReadError("INVALID_GRAPH_PATH")
        if not isinstance(ref, str) or not fullmatch(r"[0-9a-f]{40}", ref):
            raise GitHubReadError("UNPINNED_GRAPH_COMMIT")
        value = self._get(self._repo(repository) + "/contents/" + quote(path, safe="/") + "?ref=" + ref)
        if not isinstance(value, dict) or value.get("type") != "file" or value.get("encoding") != "base64":
            raise GitHubReadError("GRAPH_RESPONSE_NOT_CONTENT_FILE")
        content = value.get("content")
        if not isinstance(content, str) or len(content) > 8_000_000:
            raise GitHubReadError("GRAPH_RESPONSE_UNBOUNDED")
        try:
            raw = b64decode("".join(content.split()), validate=True)
        except ValueError as exc:
            raise GitHubReadError("GRAPH_BASE64_INVALID") from exc
        if len(raw) > 5_000_000:
            raise GitHubReadError("GRAPH_BYTES_UNBOUNDED")
        return raw

    def get_pull(self, repository: str, number: int) -> Mapping[str, Any]:
        if type(number) is not int or number < 1:
            raise GitHubReadError("INVALID_PR_NUMBER")
        value = self._get(self._repo(repository) + "/pulls/" + str(number))
        if not isinstance(value, dict):
            raise GitHubReadError("PR_RESPONSE_INVALID")
        return value

    def get_issue_comments(self, repository: str, number: int) -> list[Mapping[str, Any]]:
        if type(number) is not int or number < 1:
            raise GitHubReadError("INVALID_ISSUE_NUMBER")
        path = self._repo(repository) + "/issues/" + str(number) + "/comments"
        out: list[Mapping[str, Any]] = []
        for page in range(1, 22):
            chunk = self._get(path + "?per_page=100&page=" + str(page))
            if not isinstance(chunk, list):
                raise GitHubReadError("COMMENT_PAGE_INVALID")
            out.extend(chunk)
            if len(out) > 2000:
                raise GitHubReadError("COMMENT_COLLECTION_UNBOUNDED")
            if len(chunk) < 100:
                return out
        raise GitHubReadError("COMMENT_PAGINATION_EXCEEDED")

    def get_check_runs(self, repository: str, head: str) -> list[Mapping[str, Any]]:
        if not isinstance(head, str) or not fullmatch(r"[0-9a-f]{40}", head):
            raise GitHubReadError("INVALID_CHECK_HEAD")
        path = self._repo(repository) + "/commits/" + head + "/check-runs"
        out: list[Mapping[str, Any]] = []
        for page in range(1, 12):
            response = self._get(path + "?per_page=100&page=" + str(page))
            if not isinstance(response, dict) or not isinstance(response.get("check_runs"), list):
                raise GitHubReadError("CHECK_PAGE_INVALID")
            chunk = response["check_runs"]
            for item in chunk:
                if not isinstance(item, dict):
                    raise GitHubReadError("CHECK_ITEM_INVALID")
                out.append({
                    "name": item.get("name"), "head_sha": item.get("head_sha"),
                    "status": item.get("status"), "conclusion": item.get("conclusion"),
                })
            if len(out) > 1000:
                raise GitHubReadError("CHECK_COLLECTION_UNBOUNDED")
            if len(chunk) < 100:
                return out
        raise GitHubReadError("CHECK_PAGINATION_EXCEEDED")

    def get_pr_reviews(self, repository: str, number: int) -> list[Mapping[str, Any]]:
        """Bounded read-only submitted-review snapshots; not reviewer certification."""
        if type(number) is not int or number < 1:
            raise GitHubReadError("INVALID_PR_NUMBER")
        path = self._repo(repository) + "/pulls/" + str(number) + "/reviews"
        out: list[Mapping[str, Any]] = []
        for page in range(1, 22):
            chunk = self._get(path + "?per_page=100&page=" + str(page))
            if not isinstance(chunk, list) or not all(isinstance(row, dict) for row in chunk):
                raise GitHubReadError("REVIEW_PAGE_INVALID")
            out.extend(chunk)
            if len(out) > 2000:
                raise GitHubReadError("REVIEW_COLLECTION_UNBOUNDED")
            if len(chunk) < 100:
                return out
        raise GitHubReadError("REVIEW_PAGINATION_EXCEEDED")

    def get_branch_rulesets(self, repository: str, branch: str) -> list[Mapping[str, Any]]:
        """Observe ruleset endpoints but never interpret empty as no obligations."""
        if not isinstance(branch, str) or not fullmatch(r"[A-Za-z0-9_./-]{1,200}", branch):
            raise GitHubReadError("INVALID_TARGET_BRANCH")
        path = self._repo(repository) + "/rulesets?includes_parents=true"
        raw = self._get(path)
        if not isinstance(raw, list) or len(raw) > 1000 or not all(isinstance(x, dict) for x in raw):
            raise GitHubReadError("RULESETS_RESPONSE_INVALID")
        return raw

    def get_branch_required_checks(self, repository: str, branch: str) -> Mapping[str, Any]:
        """Classic endpoint may 403/404; the caller must report UNKNOWN."""
        if not isinstance(branch, str) or not fullmatch(r"[A-Za-z0-9_./-]{1,200}", branch):
            raise GitHubReadError("INVALID_TARGET_BRANCH")
        path = self._repo(repository) + "/branches/" + quote(branch, safe="") + "/protection/required_status_checks"
        raw = self._get(path)
        if not isinstance(raw, dict):
            raise GitHubReadError("REQUIRED_CHECKS_RESPONSE_INVALID")
        return raw
