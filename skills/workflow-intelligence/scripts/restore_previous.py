#!/usr/bin/env python3
"""Select a prior successful, same-workflow/same-branch UWI handoff artifact.

Read-only GitHub API metadata. Never download arbitrary URLs or send credentials
to a redirect. Caller downloads by validated run ID with the existing gh CLI.
A missing/corrupt prior state is a hard failure, never an implicit bootstrap.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ARTIFACT_NAME = "uwi-diagnostic-handoff-state"
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MAX_PAGES = 5
MAX_AGE_HOURS = 72


def instant(s):
    if not isinstance(s, str):
        raise ValueError("Missing GitHub timestamp")
    try:
        value = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid GitHub timestamp") from exc
    if value.tzinfo is None:
        raise ValueError("Timezone required")
    return value


def good_repo(repo):
    return (isinstance(repo, str) and REPO_PATTERN.fullmatch(repo) is not None
            and all(part.strip(".") for part in repo.split("/")))


def api_fetch(repository, endpoint, token):
    # Endpoint is generated internally only; no user URL can reach the opener.
    url = "https://api.github.com/repos/" + repository + endpoint
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "uwi-handoff-restorer/1"}
    if token:
        headers["Authorization"] = "Bearer " + token

    class ForbidRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Unexpected GitHub API redirect")

    opener = urllib.request.build_opener(ForbidRedirect())
    with opener.open(urllib.request.Request(url, headers=headers), timeout=20) as resp:
        if resp.url != url:
            raise ValueError("Unexpected response origin")
        return json.load(resp)


def pick_run(repository, current_run_id, *, branch="main", reader=None,
             max_pages=MAX_PAGES, max_age_hours=MAX_AGE_HOURS):
    if not good_repo(repository):
        raise ValueError("Invalid GitHub repository")
    if type(current_run_id) is not int or current_run_id < 1:
        raise ValueError("Invalid current run ID")
    if not isinstance(branch, str) or not branch or "/" in branch:
        raise ValueError("Invalid monitored branch")
    if type(max_pages) is not int or not 1 <= max_pages <= MAX_PAGES:
        raise ValueError("Unsupported pagination bound")
    if type(max_age_hours) not in (int, float) or not 0 < max_age_hours <= 168:
        raise ValueError("Unsupported maximum prior artifact age")
    if reader is None:
        token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("Read-only GitHub token required")
        reader = lambda endpoint: api_fetch(repository, endpoint, token)

    current = reader("/actions/runs/" + str(current_run_id))
    if (not isinstance(current, dict) or
            current.get("id") != current_run_id or
            current.get("event") not in ("schedule", "workflow_dispatch") or
            current.get("head_branch") != branch or
            not isinstance(current.get("repository"), dict) or
            current["repository"].get("full_name") != repository or
            type(current.get("workflow_id")) is not int or current["workflow_id"] < 1):
        raise ValueError("Current run does not match approved scheduled/manual workflow")
    now = instant(current.get("created_at"))
    eligible = []
    for page in range(1, max_pages + 1):
        endpoint = ("/actions/artifacts?name=" +
                    urllib.parse.quote(ARTIFACT_NAME) + "&per_page=100&page=" + str(page))
        response = reader(endpoint)
        if not isinstance(response, dict) or not isinstance(response.get("artifacts"), list):
            raise ValueError("Invalid GitHub artifact listing")
        page_artifacts = response["artifacts"]
        if len(page_artifacts) > 100:
            raise ValueError("Unbounded provider artifact page")
        for artifact in page_artifacts:
            if not isinstance(artifact, dict):
                raise ValueError("Malformed artifact record")
            if (artifact.get("name") != ARTIFACT_NAME or
                    artifact.get("expired") is not False or
                    type(artifact.get("size_in_bytes")) is not int or
                    artifact["size_in_bytes"] < 1):
                continue
            origin = artifact.get("workflow_run")
            if not isinstance(origin, dict):
                continue
            run_id = origin.get("id")
            if type(run_id) is not int or run_id <= 0 or run_id == current_run_id:
                continue
            created = instant(artifact.get("created_at"))
            if created >= now or (now - created).total_seconds() > max_age_hours * 3600:
                continue
            eligible.append((created, run_id, origin.get("head_sha")))

        if len(page_artifacts) < 100:
            break

    # Probe each distinct candidate in newest-to-oldest order. Do not trust the
    # artifact's embedded run ID/branch without checking actual run metadata.
    seen = set()
    for created, run_id, embedded_sha in sorted(eligible, key=lambda x: x[0], reverse=True):
        if run_id in seen:
            continue
        seen.add(run_id)
        prior = reader("/actions/runs/" + str(run_id))
        if (not isinstance(prior, dict) or prior.get("id") != run_id or
                prior.get("workflow_id") != current["workflow_id"] or
                prior.get("head_branch") != branch or
                prior.get("event") not in ("schedule", "workflow_dispatch") or
                prior.get("status") != "completed" or
                prior.get("conclusion") != "success" or
                not isinstance(prior.get("repository"), dict) or
                prior["repository"].get("full_name") != repository or
                (embedded_sha is not None and embedded_sha != prior.get("head_sha")) or
                instant(prior.get("created_at")) >= now):
            continue
        return run_id
    raise ValueError("No trusted recent completed handoff artifact; explicit manual bootstrap required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--current-run-id", type=int, required=True)
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    try:
        print(pick_run(args.repository, args.current_run_id, branch=args.branch))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, "RESTORE_FAILED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
