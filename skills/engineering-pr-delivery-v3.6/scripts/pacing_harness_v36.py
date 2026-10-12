#!/usr/bin/env python3
"""V3.6 Hardened Bounded Decomposition Pacing Harness & Shared Rate Limiter.

Executes progressive decomposition in rate-controlled batches enforcing strict GitHub
secondary content-creation limits (<= 15 issue/comment/PR creates per minute aggregate).
Coordinates aggregate pacing across concurrent workers via SharedRateLimiter and
RateLimitedGithubClient.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from pathlib import Path

from decompose_v36 import (
    GithubClient, PARENT_REF, child_body, child_title,
    index_marker, is_task_issue, load_plan, render_index
)
from lifecycle_v36 import ContractError, load_label, require_explicit_lab

MAX_BATCH_SIZE = 15
MIN_ITEM_DELAY_SECONDS = 4.0
MIN_BATCH_DELAY_SECONDS = 60.0
MAX_WRITES_PER_MINUTE = 15
WINDOW_SECONDS = 60.0
DEFAULT_RATE_LIMITER_FILE = ".v36_rate_limiter.json"


def validate_pacing_parameters(
    batch_size: int,
    item_delay_seconds: float,
    batch_delay_seconds: float,
    *,
    enforce_minimums: bool = True
) -> None:
    """Fail-closed parameter validation for rate-controlled execution."""
    if not isinstance(batch_size, int) or batch_size < 1 or batch_size > MAX_BATCH_SIZE:
        raise ContractError(
            f"batch-size must be an integer between 1 and {MAX_BATCH_SIZE}; got {batch_size}"
        )
    if enforce_minimums:
        if item_delay_seconds < MIN_ITEM_DELAY_SECONDS:
            raise ContractError(
                f"item-delay must be >= {MIN_ITEM_DELAY_SECONDS}s; got {item_delay_seconds}"
            )
        if batch_delay_seconds < MIN_BATCH_DELAY_SECONDS:
            raise ContractError(
                f"batch-delay must be >= {MIN_BATCH_DELAY_SECONDS}s; got {batch_delay_seconds}"
            )


class FileLock:
    """Cross-platform atomic file lock using O_CREAT | O_EXCL with stale recovery."""

    def __init__(self, lock_path: Path, timeout: float = 30.0, stale_age: float = 60.0):
        self.lock_path = lock_path
        self.timeout = timeout
        self.stale_age = stale_age
        self.fd: int | None = None

    def acquire(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        while True:
            try:
                self.fd = os.open(
                    str(self.lock_path),
                    os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                return
            except FileExistsError:
                # Stale lock recovery
                try:
                    mtime = self.lock_path.stat().st_mtime
                    if time.time() - mtime > self.stale_age:
                        try:
                            self.lock_path.unlink()
                        except OSError:
                            pass
                except OSError:
                    pass

                if time.time() - start > self.timeout:
                    raise ContractError(f"timed out waiting for file lock: {self.lock_path}")
                time.sleep(0.01)

    def release(self) -> None:
        if self.fd is not None:
            try:
                os.close(self.fd)
            finally:
                self.fd = None
                try:
                    self.lock_path.unlink()
                except OSError:
                    pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class SharedRateLimiter:
    """Shared rate limiter coordinating writes across multiple threads and processes.

    Enforces that aggregate writes across all workers do not exceed max_requests
    within window_seconds (default: <= 15 requests per 60.0s).
    """

    def __init__(
        self,
        state_path: Path | str = DEFAULT_RATE_LIMITER_FILE,
        max_requests: int = MAX_WRITES_PER_MINUTE,
        window_seconds: float = WINDOW_SECONDS,
        *,
        clock=time.time,
        sleeper=time.sleep
    ):
        self.state_path = Path(state_path)
        self.lock_path = Path(str(self.state_path) + ".lock")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clock = clock
        self.sleeper = sleeper
        self._thread_lock = threading.Lock()

    def _read_timestamps(self) -> list[float]:
        if not self.state_path.exists():
            return []
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("timestamps"), list):
                return [float(x) for x in data["timestamps"]]
        except (OSError, json.JSONDecodeError, ValueError):
            pass
        return []

    def _write_timestamps(self, timestamps: list[float]) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"timestamps": timestamps}), encoding="utf-8")
        tmp.replace(self.state_path)

    def acquire(self) -> float:
        """Acquire 1 write token. Blocks until token is available under aggregate budget."""
        while True:
            wait_seconds = 0.0
            with self._thread_lock:
                with FileLock(self.lock_path):
                    now = self.clock()
                    cutoff = now - self.window_seconds
                    timestamps = [t for t in self._read_timestamps() if t > cutoff]
                    if len(timestamps) < self.max_requests:
                        timestamps.append(now)
                        self._write_timestamps(timestamps)
                        return now
                    # Window is full; calculate wait time until oldest timestamp in window expires
                    oldest = timestamps[0]
                    wait_seconds = (oldest + self.window_seconds) - now

            if wait_seconds > 0:
                self.sleeper(wait_seconds)
            else:
                self.sleeper(0.01)

    def get_history(self) -> list[float]:
        """Return current active window timestamps."""
        with self._thread_lock:
            with FileLock(self.lock_path):
                now = self.clock()
                cutoff = now - self.window_seconds
                return [t for t in self._read_timestamps() if t > cutoff]

    def reset(self) -> None:
        """Clear rate limiter state file and locks."""
        with self._thread_lock:
            with FileLock(self.lock_path):
                if self.state_path.exists():
                    self.state_path.unlink()


class RateLimitedGithubClient:
    """Decorator for GithubClient ensuring all write operations (issues, comments, PRs)
    acquire tokens from the SharedRateLimiter to guarantee global aggregate compliance.
    """

    def __init__(self, client: GithubClient, limiter: SharedRateLimiter):
        self._client = client
        self.limiter = limiter
        self.repo = client.repo

    @property
    def token(self):
        return getattr(self._client, "token", None)

    def request(self, method: str, endpoint: str, body: dict | None = None):
        if method.upper() in ("POST", "PATCH", "PUT", "DELETE"):
            self.limiter.acquire()
        return self._client.request(method, endpoint, body)

    def paginate(self, path: str):
        return self._client.paginate(path)

    def list_issues(self):
        return self._client.list_issues()

    def list_comments(self, number: int):
        return self._client.list_comments(number)

    def get_pr(self, number: int):
        if hasattr(self._client, "get_pr"):
            return self._client.get_pr(number)
        return self.request("GET", f"/pulls/{number}")

    def create_issue(self, title: str, body: str):
        self.limiter.acquire()
        return self._client.create_issue(title, body)

    def create_comment(self, number: int, body: str):
        self.limiter.acquire()
        return self._client.create_comment(number, body)

    def update_comment(self, comment_id: int, body: str):
        self.limiter.acquire()
        return self._client.update_comment(comment_id, body)

    def create_pr(self, title: str, head: str, base: str = "main", body: str = ""):
        return self.request("POST", "/pulls", {"title": title, "head": head, "base": base, "body": body})


def update_index(plan: dict, client: GithubClient | RateLimitedGithubClient, parent_no: int, child_links: dict[str, str]) -> str:
    """Durably synchronize the managed index comment on the parent issue."""
    existing_index = [c for c in client.list_comments(parent_no)
                      if index_marker(plan) in (c.get("body") or "")]
    if len(existing_index) > 1:
        raise ContractError("duplicate managed parent indexes; manual reconciliation required")
    proposed_index = render_index(plan, child_links)
    if not existing_index:
        client.create_comment(parent_no, proposed_index)
        return "created"
    elif existing_index[0].get("body") != proposed_index:
        client.update_comment(existing_index[0]["id"], proposed_index)
        return "updated"
    return "unchanged"


def run_bounded_decomposition(
    plan: dict,
    client: GithubClient | RateLimitedGithubClient,
    *,
    apply: bool = False,
    batch_size: int = 15,
    item_delay_seconds: float = 4.0,
    batch_delay_seconds: float = 60.0,
    limiter: SharedRateLimiter | None = None,
    enforce_pacing_bounds: bool = True,
    sleeper=time.sleep
) -> dict:
    """Execute decomposition in bounded batches with enforced aggregate pacing."""
    if apply:
        validate_pacing_parameters(
            batch_size, item_delay_seconds, batch_delay_seconds,
            enforce_minimums=enforce_pacing_bounds
        )

    match = PARENT_REF.fullmatch(plan["parent"])
    if not match or match[1] != client.repo:
        raise ContractError("parent repository mismatch")
    parent_no = int(match[2])

    if apply and not isinstance(client, RateLimitedGithubClient):
        if limiter is None:
            limiter = SharedRateLimiter()
        client = RateLimitedGithubClient(client, limiter)

    issues = client.list_issues()
    child_links: dict[str, str] = {}
    missing = []
    for task in plan["tasks"]:
        matches = [x for x in issues if is_task_issue(x, task, plan["parent"])]
        if len(matches) > 1:
            raise ContractError(f"ambiguous duplicate child issues for {task['task_id']}")
        if matches:
            child_links[task["task_id"]] = matches[0].get("html_url")
        else:
            missing.append(task)

    telemetry = {
        "parent": plan["parent"],
        "plan": plan["plan_version"],
        "total_tasks": len(plan["tasks"]),
        "already_existing": len(child_links),
        "total_missing": len(missing),
        "batches_executed": 0,
        "items_created": 0,
        "latencies_seconds": [],
        "dry_run": not apply,
        "index_actions": []
    }

    if not missing or not apply:
        if apply:
            action = update_index(plan, client, parent_no, child_links)
            telemetry["index_actions"].append(action)
        return telemetry

    total_missing_count = len(missing)
    num_batches = (total_missing_count + batch_size - 1) // batch_size

    for b_idx in range(num_batches):
        batch = missing[b_idx * batch_size: (b_idx + 1) * batch_size]
        print(f"Executing batch {b_idx + 1}/{num_batches} ({len(batch)} tasks)...", flush=True)

        for task in batch:
            title = child_title(task)
            body = child_body(task, plan)

            t0 = time.time()
            issue = client.create_issue(title, body)
            duration = time.time() - t0
            telemetry["latencies_seconds"].append(duration)
            telemetry["items_created"] += 1
            child_links[task["task_id"]] = issue.get("html_url")
            print(f"  Created {task['task_id']} in {duration:.2f}s: {issue.get('html_url')}", flush=True)

            if item_delay_seconds > 0 and task != batch[-1]:
                sleeper(item_delay_seconds)

        telemetry["batches_executed"] += 1

        # Intermediate index update after each batch to preserve index durability
        action = update_index(plan, client, parent_no, child_links)
        telemetry["index_actions"].append(action)

        if b_idx < num_batches - 1 and batch_delay_seconds > 0:
            print(f"Batch {b_idx + 1} complete. Pacing pause for {batch_delay_seconds}s...", flush=True)
            sleeper(batch_delay_seconds)

    return telemetry


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3.6 bounded rate-controlled decomposition")
    p.add_argument("--label", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--lab", help="explicit Writable lab: repository")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--confirm-scope", default="", help="exact owner/repo#parent required for --apply")
    p.add_argument("--batch-size", type=int, default=MAX_BATCH_SIZE)
    p.add_argument("--item-delay", type=float, default=MIN_ITEM_DELAY_SECONDS)
    p.add_argument("--batch-delay", type=float, default=MIN_BATCH_DELAY_SECONDS)
    p.add_argument("--rate-limit-file", default=DEFAULT_RATE_LIMITER_FILE, help="shared rate limiter state file")
    args = p.parse_args(argv)

    try:
        label = load_label(args.label)
        plan = load_plan(args.plan, label)
        require_explicit_lab(label, plan["parent"], args.lab)

        token = os.environ.get("GITHUB_TOKEN")
        if args.apply and (args.confirm_scope != plan["parent"] or not token):
            raise ContractError("write refused: --confirm-scope exact parent and GITHUB_TOKEN are required")

        base_client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1], token=token)
        limiter = SharedRateLimiter(state_path=args.rate_limit_file) if args.apply else None
        client = RateLimitedGithubClient(base_client, limiter) if args.apply else base_client

        res = run_bounded_decomposition(
            plan, client,
            apply=args.apply,
            batch_size=args.batch_size,
            item_delay_seconds=args.item_delay,
            batch_delay_seconds=args.batch_delay,
            limiter=limiter,
            enforce_pacing_bounds=True
        )
        print(json.dumps(res, indent=2))
    except ContractError as exc:
        print(f"v3.6 pacing harness error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
