"""M1-U02 bounded public GitHub issues/comment intake for Common and AA3.

No GitHub write, private control transport, browser liveness inference or
acceptance evaluator. Partial scans preserve last-good source observations.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from .models import SourceIdentity, SourceKind
from .report_parser import extract_report
from .storage import SourceStore, SourceConflict


@dataclass(frozen=True)
class RegisteredSource:
    project_id: str
    repo_id: str
    repo_full_name: str


ALLOWLIST = {
    "common": RegisteredSource("common", "1412133785", "reallakshman19/Common"),
    "aa3": RegisteredSource("aa3", "1363905693", "reallakshman19/AA3"),
}


class ProviderError(Exception):
    def __init__(self, code: int, reason: str):
        self.code = code
        self.reason = reason
        super().__init__(f"GitHub source failure: HTTP {code} ({reason})")


class PageBudgetExhausted(Exception):
    pass


class PublicGitHubReader:
    """Read-only REST caller with bounded response size and timeout.

    Token is held only in memory; do not put token, request headers or body
    payloads in logs, database/status rows, issue comments or frontend.
    """

    def __init__(self, token: Optional[str] = None, timeout: float = 10):
        if not 0 < timeout <= 15:
            raise ValueError("Timeout must be within 15 seconds")
        self._token = token
        self.timeout = timeout

    def get_json(self, path: str, query: Optional[dict] = None) -> Any:
        if not path.startswith("repos/") or any(
            part in (".", "..") for part in path.split("/")
        ):
            raise ValueError("Invalid GitHub API path")
        url = "https://api.github.com/" + urllib.parse.quote(path, safe="/-_.")
        if query:
            url += "?" + urllib.parse.urlencode(query)
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dash-master-m1-read-only/1.0",
        }
        if self._token:
            headers["Authorization"] = "Bearer " + self._token
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=self.timeout
            ) as response:
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ProviderError(413, "RESPONSE_TOO_LARGE")
            return json.loads(raw)
        except urllib.error.HTTPError as error:
            raise ProviderError(error.code, "HTTP_ERROR") from error
        except (urllib.error.URLError, TimeoutError):
            raise ProviderError(0, "NETWORK_OR_TIMEOUT") from None
        except (ValueError, UnicodeError):
            raise ProviderError(502, "MALFORMED_JSON") from None


class GitHubSourceScanner:
    """Crash-replayable, bounded full scan with per-project source health.

    Cursor is (issue_page, issue_index, comment_page) and a persisted scan_id.
    Complete all issues and their paginated comments before tombstoning.
    """
    PAGE_SIZE = 100

    def __init__(self, store: SourceStore, reader: PublicGitHubReader):
        self.store = store
        self.reader = reader

    @staticmethod
    def _state(code: int) -> str:
        if code == 429:
            return "RATE_LIMITED"
        if code == 403:
            return "FORBIDDEN"
        return "UNAVAILABLE"

    @staticmethod
    def _source(reg: RegisteredSource, kind: SourceKind, item: dict,
                issue_number: int, comment: bool = False) -> SourceIdentity:
        entity = str(item["id"])
        body = item.get("body")
        if body is not None and not isinstance(body, str):
            raise SourceConflict("Invalid provider body")
        updated = item.get("updated_at")
        created = item.get("created_at")
        if not isinstance(updated, str) or not isinstance(created, str):
            raise SourceConflict("Missing provider revision timestamp")
        return SourceIdentity(
            project_id=reg.project_id, repo_id=reg.repo_id,
            repo_full_name=reg.repo_full_name, kind=kind,
            entity_id=entity, revision_id=updated,
            issue_number=issue_number,
            comment_id=entity if comment else None,
            body_sha256=hashlib.sha256((body or "").encode("utf-8")).hexdigest(),
            created_at_utc=created, updated_at_utc=updated,
            url=item.get("html_url"),
        )

    def run(self, project_id: str, max_requests: int = 20) -> dict[str, Any]:
        if project_id not in ALLOWLIST:
            raise ValueError("Unregistered GitHub project")
        if type(max_requests) is not int or not 3 <= max_requests <= 100:
            raise ValueError("Invalid bounded read budget")
        reg = ALLOWLIST[project_id]
        prior = self.store.scan(project_id)
        if prior and prior["repo_id"] != reg.repo_id:
            raise SourceConflict("Registered repo identity changed")
        restart = prior is None or prior["status"] == "REACHABLE"
        scan_id = uuid.uuid4().hex if restart else prior["scan_id"]
        page = 1 if restart else prior["issue_page"]
        index = 0 if restart else prior["issue_index"]
        comment_page = 1 if restart else prior["comment_page"]
        calls, new, replayed, tombstones = 0, 0, 0, 0

        def read(path: str, query: Optional[dict] = None) -> Any:
            nonlocal calls
            if calls >= max_requests:
                raise PageBudgetExhausted()
            calls += 1
            return self.reader.get_json(path, query)

        def status(state: str, error_code=None, error_kind=None, completed=False):
            self.store.save_scan(
                project_id=reg.project_id, repo_id=reg.repo_id,
                scan_id=scan_id, issue_page=page, issue_index=index,
                comment_page=comment_page, status=state,
                failure_code=error_code, failure_kind=error_kind,
                completed=completed,
            )
            return {
                "project_id": reg.project_id, "repo_id": reg.repo_id,
                "source_status": state, "scan_id": scan_id,
                "requests": calls, "new_versions": new, "replayed": replayed,
                "tombstones": tombstones, "complete": completed,
                "cursor": {
                    "issue_page": page, "issue_index": index,
                    "comment_page": comment_page,
                },
                "error_code": error_code, "error_kind": error_kind,
            }

        def observe(item: dict, kind: SourceKind, issue_number: int,
                    is_comment: bool = False):
            nonlocal new, replayed
            source = self._source(reg, kind, item, issue_number, is_comment)
            claim = extract_report(item.get("body"), source) if is_comment else None
            result = self.store.observe(source, scan_id, claim)
            if result == "REPLAY":
                replayed += 1
            else:
                new += 1

        # Save scan identity before any I/O, so interrupted pages replay under
        # the same scan_id. A saved PARTIAL cursor does not prove absence.
        status("PARTIAL")
        try:
            meta = read(f"repos/{reg.repo_full_name}")
            if (str(meta.get("id")) != reg.repo_id or
                str(meta.get("full_name", "")).lower() != reg.repo_full_name.lower()):
                raise SourceConflict("Repository identity mismatch")
            while True:
                issues = read(f"repos/{reg.repo_full_name}/issues", {
                    "state": "all", "sort": "created", "direction": "asc",
                    "per_page": self.PAGE_SIZE, "page": page,
                })
                if not isinstance(issues, list) or len(issues) > self.PAGE_SIZE:
                    raise SourceConflict("Invalid provider issue page")
                while index < len(issues):
                    issue = issues[index]
                    n = issue.get("number")
                    if type(n) is not int or n < 1:
                        raise SourceConflict("Invalid issue number")
                    if comment_page == 1:
                        kind = SourceKind.PR if issue.get("pull_request") else SourceKind.ISSUE
                        observe(issue, kind, n)
                    while True:
                        comments = read(
                            f"repos/{reg.repo_full_name}/issues/{n}/comments",
                            {"per_page": self.PAGE_SIZE, "page": comment_page},
                        )
                        if not isinstance(comments, list) or len(comments) > self.PAGE_SIZE:
                            raise SourceConflict("Invalid provider comment page")
                        for comment in comments:
                            observe(comment, SourceKind.ISSUE_COMMENT, n, True)
                        if len(comments) < self.PAGE_SIZE:
                            break
                        comment_page += 1
                    index += 1
                    comment_page = 1
                    # Durable progress after every full issue, not after every scan.
                    status("PARTIAL")
                if len(issues) < self.PAGE_SIZE:
                    tombstones = self.store.complete_scan(
                        reg.project_id, reg.repo_id, scan_id
                    )
                    return status("REACHABLE", completed=True)
                page += 1
                index = 0
        except PageBudgetExhausted:
            return status("PARTIAL", error_kind="READ_BUDGET")
        except ProviderError as error:
            error_kind = (
                "AUTHENTICATION" if error.code == 401 else
                "AUTHORIZATION" if error.code == 403 else
                "RATE_LIMIT" if error.code == 429 else
                error.reason if error.reason in (
                    "RESPONSE_TOO_LARGE", "MALFORMED_JSON", "NETWORK_OR_TIMEOUT"
                ) else "HTTP_ERROR"
            )
            return status(self._state(error.code),
                          error_code=error.code, error_kind=error_kind)
        except (SourceConflict, KeyError, TypeError, ValueError) as error:
            # Source shape/identity conflicts are failure, never absence.
            return status("UNAVAILABLE", error_kind="SOURCE_CONFLICT")
