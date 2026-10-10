"""Bounded current GitHub GET-only source capture for the integrated V3.2 shadow.

No POST/PATCH/PUT/DELETE, no token serialization, no production activity.
The complete output contains private issue/comment/PR text: save 0600 and
NEVER commit. Two-pass checks detect source drift, not cryptographic witness.
"""
from __future__ import annotations

from base64 import b64decode
from hashlib import sha1
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Mapping
from urllib.parse import quote


class CaptureHold(ValueError):
    pass


def _ensure(ok: bool, reason: str) -> None:
    if not ok:
        raise CaptureHold(reason)


_SHA = re.compile(r"[0-9a-f]{40}\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_MAX_COMMENTS = 1000
_MAX_ISSUES = 25
_MAX_GRAPH = 5_000_000


def git_blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()



def _unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous graph bytes before ANY provider GET or projection."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        _ensure(key not in result, "GRAPH_DUPLICATE_JSON_KEY")
        result[key] = value
    return result



def gh_get(path: str) -> Any:
    """Entrypoint allows ONLY a single GitHub API GET, with no shell."""
    _ensure(isinstance(path, str) and path.startswith("repos/") and
            not any(c in path for c in ("\n", "\r", "\x00")),
            "GET_ENDPOINT_INVALID")
    proc = subprocess.run(
        ["gh", "api", "--method", "GET", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=False,
    )
    _ensure(proc.returncode == 0, "GITHUB_GET_UNAVAILABLE")
    try:
        return json.loads(proc.stdout)
    except ValueError as exc:
        raise CaptureHold("GITHUB_GET_INVALID_JSON") from exc


def _pr(p: Any, repo: str, repo_id: int, number: int) -> dict:
    _ensure(isinstance(p, Mapping) and type(p.get("number")) is int and
            p["number"] == number, "PR_PROVIDER_NUMBER_MISMATCH")
    head, base = p.get("head"), p.get("base")
    _ensure(isinstance(head, Mapping) and isinstance(base, Mapping),
            "PR_ENDPOINTS_UNAVAILABLE")
    for side in (head, base):
        obj = side.get("repo")
        _ensure(isinstance(obj, Mapping) and
                str(obj.get("full_name") or "").lower() == repo.lower() and
                type(obj.get("id")) is int and obj["id"] == repo_id,
                "PR_REPOSITORY_IDENTITY_MISMATCH")
        _ensure(isinstance(side.get("sha"), str) and _SHA.fullmatch(side["sha"]),
                "PR_HEAD_OR_BASE_SHA_INVALID")
    _ensure(isinstance(p.get("title"), str) and isinstance(p.get("body"), (str, type(None))),
            "PR_HUMAN_TEXT_INVALID")
    _ensure(p.get("state") in ("open", "closed") and type(p.get("merged")) is bool,
            "PR_MERGE_STATE_INVALID")
    merged_at = p.get("merged_at")
    _ensure((not p["merged"] and merged_at is None) or
            (p["merged"] and p["state"] == "closed" and isinstance(merged_at, str) and bool(merged_at)),
            "PR_MERGE_METADATA_INVALID")
    return {
        "number": number, "title": p["title"], "body": p.get("body") or "",
        "state": p["state"], "merged": p["merged"], "merged_at": merged_at,
        "head": {"sha": head["sha"], "ref": head.get("ref"),
                 "repo": {"full_name": repo, "id": repo_id}},
        "base": {"sha": base["sha"], "ref": base.get("ref"),
                 "repo": {"full_name": repo, "id": repo_id}},
    }


def _comments(get: Callable[[str], Any], repo: str, no: int) -> list:
    out: list[dict] = []
    for page in range(1, 12):
        batch = get(f"repos/{repo}/issues/{no}/comments?per_page=100&page={page}")
        _ensure(isinstance(batch, list), "COMMENTS_NOT_A_LIST")
        for c in batch:
            _ensure(isinstance(c, Mapping) and type(c.get("id")) is int and
                    c["id"] > 0 and isinstance(c.get("body"), str) and
                    isinstance((c.get("user") or {}).get("login"), str) and
                    isinstance(c.get("author_association"), str),
                    "COMMENT_SOURCE_INVALID")
            out.append({"id": c["id"], "body": c["body"],
                        "user": {"login": c["user"]["login"]},
                        "author_association": c["author_association"]})
        _ensure(len(out) <= _MAX_COMMENTS, "COMMENTS_UNBOUNDED")
        if len(batch) < 100:
            _ensure(len({c["id"] for c in out}) == len(out),
                    "COMMENT_DUPLICATE_ID")
            return out
    raise CaptureHold("COMMENTS_PAGINATION_UNBOUNDED")


def capture(
    raw_graph: bytes, repository: str, expected_graph_blob: str,
    get: Callable[[str], Any] = gh_get,
    *, graph_path: str = "governance/released-graph.json",
) -> dict:
    _ensure(isinstance(repository, str) and _REPO.fullmatch(repository) is not None,
            "TARGET_REPOSITORY_INVALID")
    _ensure(type(raw_graph) is bytes and 0 < len(raw_graph) <= _MAX_GRAPH and
            isinstance(expected_graph_blob, str) and _SHA.fullmatch(expected_graph_blob) is not None and
            git_blob(raw_graph) == expected_graph_blob,
            "PINNED_RELEASED_GRAPH_INVALID")
    _ensure(isinstance(graph_path, str) and graph_path.endswith(".json") and
            len(graph_path) <= 256 and all(t not in ("", ".", "..") for t in graph_path.split("/")),
            "GRAPH_PATH_INVALID")
    try:
        graph = json.loads(raw_graph, object_pairs_hook=_unique_json_pairs,
                           parse_constant=lambda _value: _ensure(False, "GRAPH_NONFINITE_JSON"))
    except CaptureHold:
        raise
    except (ValueError, UnicodeError, TypeError) as exc:
        raise CaptureHold("GRAPH_JSON_INVALID") from exc
    _ensure(isinstance(graph, dict) and isinstance(graph.get("programme"), dict) and
            graph["programme"].get("repository") == repository,
            "GRAPH_REPOSITORY_MISMATCH")
    nodes = graph.get("nodes")
    _ensure(isinstance(nodes, list) and 1 < len(nodes) <= _MAX_ISSUES,
            "GRAPH_NODES_UNBOUNDED")
    refs = []
    prs = []
    leaves = []
    for row in nodes:
        _ensure(isinstance(row, dict) and isinstance(row.get("ref"), str) and
                "#" in row["ref"] and
                row["ref"].rsplit("#", 1)[0].lower() in
                (repository.lower(), repository.rsplit("/", 1)[-1].lower()),
                "GRAPH_ISSUE_REFERENCE_INVALID")
        refno = row["ref"].rsplit("#", 1)[-1]
        _ensure(refno.isdecimal() and int(refno) > 0, "GRAPH_ISSUE_NUMBER_INVALID")
        refs.append(int(refno))
        if row.get("kind") == "LEAF":
            ref = row.get("primary_pr")
            _ensure(isinstance(ref, str) and "#" in ref and
                    ref.rsplit("#", 1)[0].lower() in
                    (repository.lower(), repository.rsplit("/", 1)[-1].lower()) and
                    ref.rsplit("#", 1)[-1].isdecimal() and
                    int(ref.rsplit("#", 1)[-1]) > 0,
                    "GRAPH_PRIMARY_PR_REFERENCE_INVALID")
            prs.append(int(ref.rsplit("#", 1)[-1]))
            leaves.append(int(refno))
    _ensure(len(set(refs)) == len(refs) and len(set(prs)) == len(prs) and
            graph["programme"].get("base_ref", "main") == "main",
            "GRAPH_UNRELEASED_OR_DUPLICATE_BINDING")
    repo = get(f"repos/{repository}")
    _ensure(isinstance(repo, Mapping) and
            str(repo.get("full_name") or "").lower() == repository.lower() and
            type(repo.get("id")) is int and repo["id"] > 0 and
            repo.get("default_branch") == "main",
            "PROVIDER_REPOSITORY_MISMATCH")
    repo_id = repo["id"]
    sha = get(f"repos/{repository}/commits/main").get("sha")
    _ensure(isinstance(sha, str) and _SHA.fullmatch(sha), "BASE_SHA_INVALID")
    graph_endpoint = f"repos/{repository}/contents/{quote(graph_path, safe='/')}?ref={sha}"
    git_file = get(graph_endpoint)
    _ensure(isinstance(git_file, Mapping) and git_file.get("type") == "file" and
            git_file.get("encoding") == "base64" and git_file.get("sha") == expected_graph_blob,
            "RELEASED_PROVIDER_GRAPH_PIN_MISMATCH")
    try:
        payload = b64decode(git_file["content"], validate=False)
    except (ValueError, TypeError, KeyError) as exc:
        raise CaptureHold("RELEASED_PROVIDER_GRAPH_BYTES_INVALID") from exc
    _ensure(payload == raw_graph, "RELEASED_PROVIDER_GRAPH_BYTES_DIFFER")

    def issue(no: int) -> dict:
        q = get(f"repos/{repository}/issues/{no}")
        _ensure(isinstance(q, Mapping) and type(q.get("number")) is int and
                q["number"] == no and q.get("pull_request") is None and
                isinstance(q.get("title"), str) and isinstance(q.get("body"), (str, type(None))),
                "PROVIDER_ISSUE_INVALID")
        return {"title": q["title"], "body": q.get("body") or ""}

    issues = {str(no): issue(no) for no in refs}
    pulls = {str(no): _pr(get(f"repos/{repository}/pulls/{no}"), repository, repo_id, no)
             for no in prs}
    comments = {str(no): _comments(get, repository, no) for no in leaves}
    for no in refs:
        _ensure(issue(no) == issues[str(no)], "ISSUE_CHANGED_DURING_READ")
    for no in prs:
        _ensure(_pr(get(f"repos/{repository}/pulls/{no}"), repository, repo_id, no) ==
                pulls[str(no)], "PR_CHANGED_DURING_READ")
    for no in leaves:
        _ensure(_comments(get, repository, no) == comments[str(no)],
                "COMMENTS_CHANGED_DURING_READ")
    final = get(f"repos/{repository}/commits/main").get("sha")
    _ensure(final == sha, "DEFAULT_BRANCH_MOVED_DURING_READ")
    return {
        "source_kind": "GITHUB_GET_ONLY_UNATTESTED",
        "repository": repository, "repository_id": repo_id,
        "graph_git_blob": expected_graph_blob,
        "base_ref": "main", "main_sha": sha, "final_main_sha": final,
        "issues": issues, "pulls": pulls, "comments": comments,
        "provider_authentication": "GET_ONLY_NOT_INDEPENDENTLY_WITNESSED",
        "owner_release": "NOT_VERIFIED",
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="V3.2 private GitHub GET-only capture; no writes")
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--graph-blob", required=True)
    parser.add_argument("--output", required=True, type=Path)
    a = parser.parse_args()
    if a.output.exists() or a.output.is_symlink():
        raise SystemExit("OUTPUT_ALREADY_EXISTS_REFUSING_OVERWRITE")
    result = capture(a.graph.read_bytes(), a.repository, a.graph_blob)
    fd = os.open(a.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")
    print("PRIVATE_CURRENT_PROVIDER_SNAPSHOT_SAVED_0600; NO_FACTS_ADMITTED; NO_WRITES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
