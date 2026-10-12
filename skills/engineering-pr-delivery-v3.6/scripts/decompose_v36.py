#!/usr/bin/env python3
"""V3.6 O1: real GitHub child issue materialization; dry-run by default."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml
from lifecycle_v36 import ContractError, OUTCOME_IDS, REPO_REF, TASK_REF, UniqueKeyLoader, load_label

PLAN_KEYS = {"plan_version", "parent", "label", "tasks"}
TASK_KEYS = {"task_id", "size", "outcome", "title", "acceptance", "for_user"}
LABEL_KEYS = {"work", "version", "label_sha"}
PARENT_REF = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)$")
PLAN_VERSION = re.compile(r"^V36-[0-9]+-PLAN-[0-9]+$")
SIZES = frozenset(("XS", "S", "M", "L"))


def require_keys(value: object, keys: set[str], context: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise ContractError(f"{context} must contain exactly {sorted(keys)}")
    return value


def required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise ContractError(f"{name} must be nonempty trimmed text")
    return value


def validate_plan(plan: object, label: dict) -> dict:
    plan = require_keys(plan, PLAN_KEYS, "plan")
    revision = required_text(plan["plan_version"], "plan_version")
    if not PLAN_VERSION.fullmatch(revision):
        raise ContractError("plan_version must be a stable V36-N-PLAN-N ID")
    parent = required_text(plan["parent"], "parent")
    match = PARENT_REF.fullmatch(parent)
    if not match:
        raise ContractError("parent must be owner/repo#N")
    if match[1] != label["repository"]:
        raise ContractError("parent repository does not match approved label")
    expected = {key: label[key] for key in LABEL_KEYS}
    if require_keys(plan["label"], LABEL_KEYS, "label binding") != expected:
        raise ContractError("plan must bind exact approved work/version/label_sha")
    tasks = plan["tasks"]
    if not isinstance(tasks, list) or len(tasks) < 1:
        raise ContractError("tasks must be a nonempty list")
    names = set()
    for idx, task in enumerate(tasks):
        task = require_keys(task, TASK_KEYS, f"tasks[{idx}]")
        task_id = required_text(task["task_id"], "task_id")
        if not TASK_REF.fullmatch(task_id) or task_id in names:
            raise ContractError("invalid or duplicate task ID")
        if not task_id.startswith(f"V36-{match[2]}-"):
            raise ContractError("task ID must bind parent issue number")
        names.add(task_id)
        if task["size"] not in SIZES:
            raise ContractError("size must be XS/S/M/L")
        if task["outcome"] not in OUTCOME_IDS:
            raise ContractError("task outcome must be O1..O5")
        for field in ("title", "acceptance", "for_user"):
            required_text(task[field], field)
    return plan


def load_plan(path: str | Path, label: dict) -> dict:
    try:
        plan = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError(f"plan unavailable or invalid: {exc}") from exc
    return validate_plan(plan, label)


def marker(task_id: str, parent: str) -> str:
    return f"<!-- v36-task:{task_id} parent:{parent} -->"


def child_title(task: dict) -> str:
    return f"[V3.6][{task['outcome']}][PLANNED] {task['task_id']} — {task['title']}"


def child_body(task: dict, plan: dict) -> str:
    return (
        f"{marker(task['task_id'], plan['parent'])}\n"
        f"Parent: {plan['parent']}\n"
        f"Plan: {plan['plan_version']}\n"
        f"Label: {plan['label']['work']}@{plan['label']['version']}"
        f" ({plan['label']['label_sha']})\n"
        f"Task ID: {task['task_id']}\n"
        f"Outcome: {task['outcome']}\n"
        f"Size: {task['size']}\n"
        f"For the user: {task['for_user']}\n"
        f"Acceptance: {task['acceptance']}\n"
        "\nTASK_EVIDENCE belongs on THIS issue after actual verified task completion;"
        " closing a child issue without evidence never proves completion.\n"
    )


def is_task_issue(issue: dict, task: dict, parent: str) -> bool:
    body = issue.get("body") or ""
    title = issue.get("title") or ""
    task_id = task["task_id"]
    if marker(task_id, parent) in body:
        return True
    # One manual WP1 child predates the machine-created marker. Adopt it
    # only if both exact task identity and parent are unambiguously present.
    match = PARENT_REF.fullmatch(parent)
    if not match:
        return False
    legacy_task = f"**Task:** {task_id}" in body
    legacy_parent = f"**Parent:** #{match[2]}" in body
    return task_id in title and legacy_task and legacy_parent


def index_marker(plan: dict) -> str:
    return f"<!-- v36-plan-index:{plan['plan_version']} parent:{plan['parent']} -->"


def render_index(plan: dict, child_links: dict[str, str]) -> str:
    lines = [
        index_marker(plan), f"PLAN_INDEX — {plan['plan_version']}",
        f"Owner label: {plan['label']['work']}@{plan['label']['version']} ({plan['label']['label_sha']})",
        f"Parent: {plan['parent']}",
        "Real child issues (link updated after creation; completion requires evidence):",
        "| Task | Outcome | Size | Child issue |",
        "|---|---|---|---|",
    ]
    for task in plan["tasks"]:
        url = child_links.get(task["task_id"])
        lines.append(
            f"| {task['task_id']} | {task['outcome']} | {task['size']} | "
            f"{f'[issue]({url})' if url else 'NOT_CREATED'} |"
        )
    return "\n".join(lines) + "\n"


class GithubClient:
    """Only selected API routes; no implicit authorization or title writes."""

    def __init__(self, repo: str, token: str | None = None):
        if not REPO_REF.fullmatch(repo):
            raise ContractError("invalid repository")
        self.repo, self.token = repo, token

    def request(self, method: str, endpoint: str, body: dict | None = None):
        url = f"https://api.github.com/repos/{self.repo}{endpoint}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "v36-lifecycle"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = Request(url, headers=headers, data=data, method=method)
        try:
            with urlopen(req, timeout=25) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ContractError(f"GitHub API failure for {method} {endpoint}: {exc}") from exc

    def paginate(self, path: str) -> list[dict]:
        values = []
        for page in range(1, 101):
            separator = "&" if "?" in path else "?"
            batch = self.request("GET", f"{path}{separator}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise ContractError("GitHub list response must be an array")
            values.extend(batch)
            if len(batch) < 100:
                return values
        raise ContractError("too many pages: refusing incomplete GitHub list")

    def list_issues(self):
        return [issue for issue in self.paginate("/issues?state=all")
                if "pull_request" not in issue]

    def list_comments(self, number: int):
        return self.paginate(f"/issues/{number}/comments")

    def create_issue(self, title: str, body: str):
        return self.request("POST", "/issues", {"title": title, "body": body})

    def create_comment(self, number: int, body: str):
        return self.request("POST", f"/issues/{number}/comments", {"body": body})

    def update_comment(self, comment_id: int, body: str):
        return self.request("PATCH", f"/issues/comments/{comment_id}", {"body": body})


def execute(plan: dict, client, *, apply: bool = False) -> dict:
    """Snapshot current GitHub, reject duplicate IDs, then create only missing children."""
    parent = plan["parent"]
    match = PARENT_REF.fullmatch(parent)
    if not match or client.repo != match[1]:
        raise ContractError("GitHub client must match parent repository")
    issues = client.list_issues()
    mapping = {}
    missing = []
    for task in plan["tasks"]:
        matches = [issue for issue in issues if is_task_issue(issue, task, parent)]
        if len(matches) > 1:
            raise ContractError(f"duplicate provider issues for {task['task_id']}")
        if matches:
            if not isinstance(matches[0].get("html_url"), str):
                raise ContractError("existing issue missing URL")
            mapping[task["task_id"]] = matches[0]["html_url"]
        else:
            missing.append(task)
    planned = [task["task_id"] for task in missing]
    # Preflight managed-index uniqueness BEFORE creating any issues.
    existing_index = []
    if apply:
        existing_index = [c for c in client.list_comments(int(match[2]))
                          if index_marker(plan) in (c.get("body") or "")]
        if len(existing_index) > 1:
            raise ContractError("duplicate managed parent indexes; manual reconciliation required")
        for task in missing:
            created = client.create_issue(child_title(task), child_body(task, plan))
            if not isinstance(created.get("html_url"), str) or not isinstance(created.get("number"), int):
                raise ContractError("created issue missing verified identity")
            mapping[task["task_id"]] = created["html_url"]
    proposed_index = render_index(plan, mapping)
    index_action = "pending"
    if apply:
        if not existing_index:
            client.create_comment(int(match[2]), proposed_index)
            index_action = "created"
        elif existing_index[0]["body"] != proposed_index:
            client.update_comment(existing_index[0]["id"], proposed_index)
            index_action = "updated"
        else:
            index_action = "unchanged"
    return {
        "plan": plan["plan_version"], "parent": parent, "dry_run": not apply,
        "already_present": len(plan["tasks"]) - len(missing),
        "would_create": planned, "created": planned if apply else [],
        "index": index_action, "children": mapping
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="v3.6 O1 parent child decomposition")
    parser.add_argument("--label", required=True, help="actual master relay/AIM/<WORK>.yaml")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--apply", action="store_true", help="opt-in GitHub writes")
    parser.add_argument("--confirm-scope", default="", help="exact owner/repo#parent required for --apply")
    args = parser.parse_args(argv)
    try:
        label = load_label(args.label)
        plan = load_plan(args.plan, label)
        token = os.environ.get("GITHUB_TOKEN")
        if args.apply and (args.confirm_scope != plan["parent"] or not token):
            raise ContractError("write refused: --confirm-scope exact parent and GITHUB_TOKEN are required")
        result = execute(plan, GithubClient(label["repository"], token), apply=args.apply)
        print(json.dumps(result, indent=2, sort_keys=True))
    except ContractError as exc:
        print(f"v3.6 decomposition error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
