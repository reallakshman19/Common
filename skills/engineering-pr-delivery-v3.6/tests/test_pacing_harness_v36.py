"""Hardened tests for v3.6 bounded decomposition pacing harness & shared rate limiter."""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lifecycle_v36 as lc
import decompose_v36 as dc
import pacing_harness_v36 as ph

LABEL = lc.load_label(ROOT / "tests" / "fixtures" / "relay" / "AIM" / "V35-LIFECYCLE.yaml")
PLAN = dc.load_plan(ROOT / "plans" / "V36-341-PLAN-02.yaml", LABEL)


class VirtualClock:
    """Deterministic virtual clock for fast and exact rate-limit verification."""

    def __init__(self, start_time: float = 1000.0):
        self.current_time = start_time
        self.sleep_calls: list[float] = []

    def time(self) -> float:
        return self.current_time

    def sleep(self, seconds: float) -> None:
        self.sleep_calls.append(seconds)
        self.current_time += seconds


class FakeClient:
    repo = "reallakshman19/Common"

    def __init__(self):
        self.issues = []
        self.comments = []
        self.calls = []

    def list_issues(self):
        return list(self.issues)

    def list_comments(self, n):
        self.calls.append(("list_comments", n))
        return list(self.comments)

    def create_issue(self, title, body):
        self.calls.append(("create_issue", title))
        number = 500 + len(self.issues)
        issue = {
            "number": number,
            "title": title,
            "body": body,
            "html_url": f"https://github.com/reallakshman19/Common/issues/{number}"
        }
        self.issues.append(issue)
        return issue

    def create_comment(self, n, body):
        self.calls.append(("create_comment", n))
        item = {"id": 1000 + len(self.comments), "body": body}
        self.comments.append(item)
        return item

    def update_comment(self, comment_id, body):
        self.calls.append(("update_comment", comment_id))
        for c in self.comments:
            if c["id"] == comment_id:
                c["body"] = body
                return c
        return {"id": comment_id, "body": body}


class HardenedPacingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "limiter.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    # --- Parameter Validation Tests ---

    def test_parameter_validation_rejects_excessive_batch_size(self):
        with self.assertRaises(lc.ContractError) as ctx:
            ph.validate_pacing_parameters(batch_size=16, item_delay_seconds=4.0, batch_delay_seconds=60.0)
        self.assertIn("batch-size must be an integer between 1 and 15", str(ctx.exception))

        with self.assertRaises(lc.ContractError):
            ph.validate_pacing_parameters(batch_size=0, item_delay_seconds=4.0, batch_delay_seconds=60.0)

    def test_parameter_validation_rejects_subminimum_item_delay(self):
        with self.assertRaises(lc.ContractError) as ctx:
            ph.validate_pacing_parameters(batch_size=15, item_delay_seconds=3.9, batch_delay_seconds=60.0)
        self.assertIn("item-delay must be >= 4.0s", str(ctx.exception))

    def test_parameter_validation_rejects_subminimum_batch_delay(self):
        with self.assertRaises(lc.ContractError) as ctx:
            ph.validate_pacing_parameters(batch_size=15, item_delay_seconds=4.0, batch_delay_seconds=59.0)
        self.assertIn("batch-delay must be >= 60.0s", str(ctx.exception))

    # --- Timed Tests with Virtual Clock ---

    def test_timed_pacing_with_virtual_clock_verifies_rate_and_delays(self):
        vclock = VirtualClock(start_time=100.0)
        limiter = ph.SharedRateLimiter(
            state_path=self.state_file,
            max_requests=15,
            window_seconds=60.0,
            clock=vclock.time,
            sleeper=vclock.sleep
        )
        client = FakeClient()
        # PLAN has 7 tasks. Run with batch_size=3 -> 3 batches (3, 3, 1 tasks)
        res = ph.run_bounded_decomposition(
            PLAN, client,
            apply=True,
            batch_size=3,
            item_delay_seconds=4.0,
            batch_delay_seconds=60.0,
            limiter=limiter,
            enforce_pacing_bounds=True,
            sleeper=vclock.sleep
        )
        self.assertEqual(res["items_created"], len(PLAN["tasks"]))
        self.assertEqual(res["batches_executed"], 3)

        # In batch 1 (3 items): 2 item sleeps of 4s = 8s; + 1 batch pause of 60s
        # In batch 2 (3 items): 2 item sleeps of 4s = 8s; + 1 batch pause of 60s
        # In batch 3 (1 item): 0 item sleeps; 0 batch pause
        # Total sleep duration across harness: (4*2 + 60) + (4*2 + 60) = 136s
        # Plus rate limiter acquisitions: tokens are available (<= 15 total operations), so limiter adds 0 sleep
        self.assertGreaterEqual(sum(vclock.sleep_calls), 136.0)

        # Total elapsed time proves aggregate rate <= 15 items per minute
        elapsed_minutes = (vclock.time() - 100.0) / 60.0
        effective_rate = res["items_created"] / elapsed_minutes
        self.assertLessEqual(effective_rate, 15.0)

    def test_shared_rate_limiter_sliding_window_enforces_budget(self):
        vclock = VirtualClock(start_time=500.0)
        limiter = ph.SharedRateLimiter(
            state_path=self.state_file,
            max_requests=15,
            window_seconds=60.0,
            clock=vclock.time,
            sleeper=vclock.sleep
        )
        acquired = []
        # Acquire 20 tokens rapidly
        for i in range(20):
            t = limiter.acquire()
            acquired.append(t)

        self.assertEqual(len(acquired), 20)
        # First 15 tokens acquired at t=500.0 without sleeping
        for i in range(15):
            self.assertEqual(acquired[i], 500.0)
        # 16th token required waiting until oldest (at 500.0) expired at 560.0
        self.assertGreaterEqual(acquired[15], 560.0)
        self.assertGreater(len(vclock.sleep_calls), 0)

        # Assert sliding window invariant: within any 60-second slice, <= 15 requests
        for window_start in [500.0, 501.0, 560.0]:
            count = sum(1 for t in acquired if window_start <= t < window_start + 60.0)
            self.assertLessEqual(count, 15)

    # --- 8 Concurrent Workers Aggregate Pacing Test ---

    def test_8_concurrent_workers_shared_rate_limiter(self):
        # Micro-window test with 8 concurrent threads: budget = 4 writes per 0.25 seconds
        limiter = ph.SharedRateLimiter(
            state_path=self.state_file,
            max_requests=4,
            window_seconds=0.25
        )
        results = []
        errors = []

        def worker_job(worker_id: int):
            try:
                t = limiter.acquire()
                results.append((worker_id, t))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker_job, args=(i,)) for i in range(8)]
        t_start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        self.assertEqual(len(errors), 0, f"Worker errors: {errors}")
        self.assertEqual(len(results), 8, "All 8 concurrent workers must acquire slots")

        # 8 requests with 4 per 0.25s requires spanning at least 2 full windows (>= 0.25s)
        total_duration = time.time() - t_start
        self.assertGreaterEqual(total_duration, 0.20)

        # Invariant: within any 0.25s window, no more than 4 workers acquired slots
        timestamps = sorted([r[1] for r in results])
        for i in range(len(timestamps)):
            window_end = timestamps[i] + 0.25
            count = sum(1 for ts in timestamps if timestamps[i] <= ts <= window_end)
            self.assertLessEqual(count, 4, f"Aggregate pacing exceeded: {count} writes in 0.25s")

    # --- Base Harness Functionality ---

    def test_dry_run_never_creates_issues(self):
        client = FakeClient()
        res = ph.run_bounded_decomposition(PLAN, client, apply=False)
        self.assertTrue(res["dry_run"])
        self.assertEqual(res["items_created"], 0)
        self.assertEqual(res["batches_executed"], 0)
        self.assertEqual(len(client.calls), 0)
        self.assertEqual(res["total_missing"], len(PLAN["tasks"]))

    def test_idempotent_subsequent_run(self):
        client = FakeClient()
        limiter = ph.SharedRateLimiter(state_path=self.state_file, clock=lambda: 1000.0, sleeper=lambda s: None)
        # First run
        ph.run_bounded_decomposition(
            PLAN, client, apply=True, batch_size=10,
            item_delay_seconds=4.0, batch_delay_seconds=60.0,
            limiter=limiter, enforce_pacing_bounds=False, sleeper=lambda s: None
        )
        initial_issues = len(client.issues)

        # Second run should find 0 missing
        res2 = ph.run_bounded_decomposition(
            PLAN, client, apply=True, batch_size=10,
            item_delay_seconds=4.0, batch_delay_seconds=60.0,
            limiter=limiter, enforce_pacing_bounds=False, sleeper=lambda s: None
        )
        self.assertEqual(res2["total_missing"], 0)
        self.assertEqual(res2["items_created"], 0)
        self.assertEqual(len(client.issues), initial_issues)

    def test_parent_repository_mismatch_fails(self):
        client = FakeClient()
        client.repo = "different/repository"
        with self.assertRaises(lc.ContractError):
            ph.run_bounded_decomposition(PLAN, client, apply=False)


if __name__ == "__main__":
    unittest.main()
