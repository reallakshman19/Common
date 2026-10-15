#!/usr/bin/env python3
"""ONB #391 WP2. Read-only GitHub facts; neither a successor verdict nor approval.

No imports from v3.6 or the two unmerged WP1 PRs. Does not read predecessor chat.
An injected GET transport makes every data/identity/freshness assumption falsifiable.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9_./-]+$")
INDEX_RE = re.compile(r"<!-- v36-plan-index:(V36-[0-9]+-PLAN-[0-9]+) parent:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#[1-9][0-9]* -->")
MAX_PAGES = 25
MAX_RESPONSE_BYTES = 6_000_000


class SourceError(Exception):
    """Provider results, scope or fetch completeness cannot be trusted."""


class ProviderError(SourceError):
    def __init__(self, status, message):
        self.status = status
        super().__init__(str(message))


def positive_int(value, label):
    if type(value) is not int or value < 1:
        raise SourceError(label + " must be a positive integer")
    return value


def repository(value):
    if not isinstance(value, str) or not REPO_RE.fullmatch(value):
        raise SourceError("invalid canonical owner/repo")
    return value


def require_sha(value, label="SHA"):
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise SourceError("invalid " + label + " (requires 40 lowercase hex)")
    return value


def as_dict(value, what):
    if not isinstance(value, dict):
        raise SourceError(what + " must be a JSON object")
    return value


def number_from(obj, expected, name):
    if type(obj.get("number")) is not int or obj["number"] != expected:
        raise SourceError(name + " returned the wrong number")
    return expected


def body_digest(s):
    if s is None:
        s = ""
    if not isinstance(s, str):
        raise SourceError("issue/comment body must be UTF-8 text")
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()


def link_for(repo, kind, number):
    return "https://github.com/" + repo + "/" + kind + "/" + str(number)


class HttpReadTransport:
    """Allowlisted HTTPS GitHub REST GET only; no workflow, writes or redirects."""

    def __init__(self, token=None, timeout=15):
        self.token = token
        self.timeout = timeout

    def get(self, path):
        if not isinstance(path, str) or not path.startswith("/repos/"):
            raise SourceError("request outside approved /repos scope")
        if not re.fullmatch(r"/repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/[-A-Za-z0-9_./?&=%]+", path):
            raise SourceError("unsafe REST request path")
        url = "https://api.github.com" + path
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "onb-rwi-wp2-readonly",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        req = urllib.request.Request(url, method="GET", headers=headers)
        try:
            # Authentication and redirects are not interpreted as source authority.
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.geturl().split("?", 1)[0] != url.split("?", 1)[0]:
                    raise SourceError("provider redirected endpoint; canonical target unknown")
                raw = resp.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise SourceError("provider response exceeds bounded size")
                try:
                    return json.loads(raw), resp.headers.get("Link", "")
                except (UnicodeDecodeError, ValueError) as e:
                    raise SourceError("malformed GitHub provider JSON") from e
        except urllib.error.HTTPError as e:
            raise ProviderError(e.code, "GitHub GET failed") from e
        except (urllib.error.URLError, TimeoutError) as e:
            raise ProviderError(None, "GitHub GET unavailable") from e


def checked_page_link(link, expected_page):
    """Only use page numbers; NEVER follow a provider-supplied arbitrary URL."""
    if not isinstance(link, str):
        raise SourceError("malformed pagination Link")
    next_links = []
    for part in link.split(","):
        if 'rel="next"' not in part:
            continue
        match = re.match(r"\s*<([^>]+)>\s*;\s*rel=\"next\"", part.strip())
        if not match:
            raise SourceError("malformed provider next-page link")
        url = urllib.parse.urlsplit(match.group(1))
        if url.scheme != "https" or url.netloc != "api.github.com":
            raise SourceError("next-page URL points to foreign provider")
        query = urllib.parse.parse_qs(url.query, strict_parsing=True)
        if query.get("page") != [str(expected_page)] or query.get("per_page") != ["100"]:
            raise SourceError("next-page URL index mismatch")
        next_links.append(url)
    if len(next_links) > 1:
        raise SourceError("ambiguous next-page link")
    return bool(next_links)


def list_all(transport, route, *, key=None, max_pages=MAX_PAGES):
    """Fail closed on malformed, duplicate or over-limit paginated GET results."""
    items = []
    total_count = None
    for page in range(1, max_pages + 1):
        sep = "&" if "?" in route else "?"
        endpoint = f"{route}{sep}per_page=100&page={page}"
        data, link = transport.get(endpoint)
        if key:
            wrapped = as_dict(data, "paged result")
            if type(wrapped.get("total_count")) is not int:
                raise SourceError("paged wrapper missing total_count")
            if total_count is not None and total_count != wrapped["total_count"]:
                raise SourceError("provider total_count changed mid-pagination")
            total_count = wrapped["total_count"]
            data = wrapped.get(key)
        if not isinstance(data, list):
            raise SourceError("provider list response is not an array")
        if len(data) > 100:
            raise SourceError("provider page exceeds per_page=100")
        items.extend(data)
        more = checked_page_link(link, page + 1)
        if not more:
            if total_count is not None and total_count != len(items):
                raise SourceError("partial provider list (total_count mismatch)")
            return items
        if not data:
            raise SourceError("provider next page declared after empty page")
    raise SourceError("page budget exhausted; never claim complete source inventory")


def collect(client, target_repo, issue_number, pr_numbers=(), *, expected_main=None,
            now=None):
    """Collect an exact-cut observer snapshot. Data is historical fact, NOT Owner approval.

    A provider interruption is an exception, never partial-success. CI source errors
    become explicit UNKNOWN for just that optional PR check surface.
    """
    repo = repository(target_repo)
    positive_int(issue_number, "issue")
    if not isinstance(pr_numbers, (list, tuple)) or any(type(x) is not int or x < 1 for x in pr_numbers):
        raise SourceError("invalid PR selection")
    if len(pr_numbers) != len(set(pr_numbers)):
        raise SourceError("duplicate PR selection")
    if expected_main is not None:
        require_sha(expected_main, "expected main")
    prefix = "/repos/" + repo
    meta, _ = client.get(prefix)
    meta = as_dict(meta, "repo metadata")
    if meta.get("full_name") != repo:
        raise SourceError("repository renamed/redirected: require explicit owner decision")
    default = meta.get("default_branch")
    if not isinstance(default, str) or not BRANCH_RE.fullmatch(default):
        raise SourceError("invalid default branch")
    start, _ = client.get(prefix + "/commits/" + urllib.parse.quote(default, safe=""))
    main_sha = require_sha(as_dict(start, "default branch commit").get("sha"), "default branch")
    if expected_main is not None and main_sha != expected_main:
        raise SourceError("expected main does not match current provider head")
    item, _ = client.get(prefix + "/issues/" + str(issue_number))
    item = as_dict(item, "issue")
    number_from(item, issue_number, "issue")
    if "pull_request" in item:
        raise SourceError("selected parent is a PR, not an issue")
    if not isinstance(item.get("title"), str):
        raise SourceError("issue title missing")
    comment_data = list_all(client, prefix + "/issues/" + str(issue_number) + "/comments")
    sanitized_comments, indexes = [], []
    for c in comment_data:
        c = as_dict(c, "comment")
        cid = positive_int(c.get("id"), "comment id")
        body = c.get("body") or ""
        digest = body_digest(body)
        raw_markers = [m.group(0) for m in INDEX_RE.finditer(body)]
        if raw_markers:
            indexes.append({"comment_id": cid, "markers": raw_markers,
                            "body_digest": digest, "body": body})
        sanitized_comments.append({
            "id": cid, "url": link_for(repo, "issues", issue_number) + "#issuecomment-" + str(cid),
            "author": (c.get("user") or {}).get("login") if isinstance(c.get("user"), dict) else None,
            "created_at": c.get("created_at"), "updated_at": c.get("updated_at"),
            "body_sha256": digest,
            "mentions_v36_evidence": "TASK_EVIDENCE v3.6" in body,
            "mentions_v36_index": bool(raw_markers),
            "text_exported": False
        })
    if len({c["id"] for c in sanitized_comments}) != len(sanitized_comments):
        raise SourceError("duplicate provider comment identity")

    prs = []
    for pr_no in pr_numbers:
        pr, _ = client.get(prefix + "/pulls/" + str(pr_no))
        pr = as_dict(pr, "pull request")
        number_from(pr, pr_no, "PR")
        head = require_sha(as_dict(pr.get("head"), "PR head").get("sha"), "PR head")
        base = require_sha(as_dict(pr.get("base"), "PR base").get("sha"), "PR base")
        if pr.get("state") not in {"open", "closed"} or type(pr.get("draft")) is not bool:
            raise SourceError("PR state/draft malformed")
        changed = list_all(client, prefix + "/pulls/" + str(pr_no) + "/files")
        files = []
        for f in changed:
            f = as_dict(f, "PR changed file")
            path = f.get("filename")
            if not isinstance(path, str) or not path or path.startswith("/") or ".." in path.split("/"):
                raise SourceError("invalid changed path")
            files.append({"path": path, "status": f.get("status")})
        if len({x["path"] for x in files}) != len(files):
            raise SourceError("duplicate changed file")
        checks = {"state": "UNKNOWN", "items": [], "reason": None}
        try:
            runs = list_all(client, prefix + "/commits/" + head + "/check-runs", key="check_runs")
            check_items = []
            for run in runs:
                run = as_dict(run, "check run")
                check_items.append({"id": run.get("id"), "name": run.get("name"),
                                    "status": run.get("status"), "conclusion": run.get("conclusion"),
                                    "head_sha": run.get("head_sha")})
                if run.get("head_sha") != head:
                    raise SourceError("check run SHA differs from PR candidate")
            checks = {"state": "OBSERVED", "items": check_items, "reason": None}
        except ProviderError as exc:
            checks = {"state": "UNKNOWN", "items": [],
                      "reason": "check provider unavailable: " + str(exc.status)}
        prs.append({"number": pr_no, "url": link_for(repo, "pull", pr_no),
                    "head_sha": head, "base_sha": base, "state": pr["state"],
                    "draft": pr["draft"], "merged": pr.get("merged") is True,
                    "files": files, "checks": checks,
                    "candidate_accepted": False})

    end, _ = client.get(prefix + "/commits/" + urllib.parse.quote(default, safe=""))
    if require_sha(as_dict(end, "final default commit").get("sha")) != main_sha:
        raise SourceError("STALE: default-branch head moved during collection")
    for pr in prs:
        finish, _ = client.get(prefix + "/pulls/" + str(pr["number"]))
        if require_sha(as_dict(finish, "final PR").get("head", {}).get("sha")) != pr["head_sha"]:
            raise SourceError("STALE: selected PR head moved during collection")
    timestamp = now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {"schema": "onboarding.provider-snapshot/v1",
            "repository": repo, "issue_number": issue_number,
            "issue_url": link_for(repo, "issues", issue_number),
            "issue_title": item["title"], "issue_state": item.get("state"),
            "issue_body_sha256": body_digest(item.get("body")),
            "default_branch": default, "default_head_sha": main_sha,
            "observed_at": timestamp, "comments": sanitized_comments, "prs": prs,
            "v36_index_candidates": indexes,
            "source_health": "COMPLETE" if all(p["checks"]["state"] == "OBSERVED" for p in prs)
                            else "PARTIAL_OPTIONAL_CI",
            "predecessor_final_report_required": False,
            "engineering_code_path_verified": False,
            "original_fixture_sha256_verified": False,
            "owner_acceptance_verified": False,
            "execution_authorized": False,
            "limitations": ["Source snapshot contains no original full comment bodies in public projection",
                            "A comment/evidence marker does not prove task acceptance",
                            "PR check-run success is candidate scoped, not product approval",
                            "Source code ownership and full Golden fixture bytes are not reconstructed",
                            "A predecessor handover, outgoing final LOG and private chat are not required or inferred"]}


def public_projection(snapshot):
    """Remove raw managed-index bodies; preserve digest and markers for audit."""
    d = json.loads(json.dumps(snapshot))
    d["v36_index_candidates"] = [
        {k: v for k, v in index.items() if k != "body"}
        for index in d["v36_index_candidates"]]
    return d


def cli(argv=None):
    parser = argparse.ArgumentParser(description="ONB WP2 GitHub-only read-only collector")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--pr", type=int, action="append", default=[])
    parser.add_argument("--expected-main")
    args = parser.parse_args(argv)
    try:
        data = collect(HttpReadTransport(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
                       args.repo, args.issue, args.pr, expected_main=args.expected_main)
        print(json.dumps(public_projection(data), indent=2, sort_keys=True))
        return 0
    except SourceError as exc:
        # Do not dump source bodies, token or private error contents.
        print(json.dumps({"schema":"onboarding.provider-error/v1",
                          "status":"BLOCKED_OR_STALE", "error":str(exc),
                          "execution_authorized":False}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
