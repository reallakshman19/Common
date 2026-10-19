"""Focused callback-order checks; SEARCH_SESSION_SOURCE selects a contrast source."""

import importlib.util
import os
from pathlib import Path
import unittest


SOURCE = Path(os.environ.get(
    "SEARCH_SESSION_SOURCE", str(Path(__file__).with_name("session.py"))
)).resolve()
spec = importlib.util.spec_from_file_location("session_under_test", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SearchSession = module.SearchSession


class RegressionChecks(unittest.TestCase):
    def assert_view(self, session, scope, query, busy, rows=None, error=None):
        self.assertEqual(session.snapshot(), {
            "scope": scope, "query": query, "busy": busy,
            "rows": [] if rows is None else rows, "error": error,
        })

    def deliver(self, session, ticket, callback, value):
        if callback == "finish":
            return session.finish(ticket, [value])
        return session.fail(ticket, value)

    def assert_ignored(self, session, ticket, callback):
        before = session.snapshot()
        self.assertIs(self.deliver(session, ticket, callback, "obsolete"), False)
        self.assertEqual(session.snapshot(), before)

    def check_supersession(self, callback, return_to_scope):
        for current_callback in ("finish", "fail"):
            with self.subTest(current_callback=current_callback):
                session = SearchSession()
                obsolete = [session.begin("A", "old")]
                self.assert_view(session, "A", "old", True)
                if return_to_scope:
                    obsolete.append(session.begin("B", "middle"))
                    self.assert_view(session, "B", "middle", True)
                current = session.begin("A", "new")
                self.assert_view(session, "A", "new", True)
                for ticket in obsolete:
                    self.assert_ignored(session, ticket, callback)
                self.assert_view(session, "A", "new", True)
                self.assertIs(self.deliver(
                    session, current, current_callback, "current"
                ), True)
                self.assert_view(
                    session, "A", "new", False,
                    rows=["current"] if current_callback == "finish" else [],
                    error="current" if current_callback == "fail" else None,
                )
                for ticket in obsolete:
                    self.assert_ignored(session, ticket, callback)

    def test_same_scope_stale_finish(self):
        self.check_supersession("finish", return_to_scope=False)

    def test_same_scope_stale_fail(self):
        self.check_supersession("fail", return_to_scope=False)

    def test_return_to_scope_stale_finish(self):
        self.check_supersession("finish", return_to_scope=True)

    def test_return_to_scope_stale_fail(self):
        self.check_supersession("fail", return_to_scope=True)

    def check_cancelled_callback(self, callback):
        session = SearchSession()
        cancelled = session.begin("A", "cancelled")
        self.assert_view(session, "A", "cancelled", True)
        session.cancel()
        self.assert_view(session, "A", "cancelled", False)
        self.assert_ignored(session, cancelled, callback)
        self.assert_view(session, "A", "cancelled", False)

    def test_cancel_then_late_finish(self):
        self.check_cancelled_callback("finish")

    def test_cancel_then_late_fail(self):
        self.check_cancelled_callback("fail")

    def check_cancel_and_begin(self, callback):
        for current_callback in ("finish", "fail"):
            with self.subTest(current_callback=current_callback):
                session = SearchSession()
                cancelled = session.begin("A", "cancelled")
                session.cancel()
                self.assert_view(session, "A", "cancelled", False)
                current = session.begin("A", "reused")
                self.assert_view(session, "A", "reused", True)
                self.assert_ignored(session, cancelled, callback)
                self.assertIs(self.deliver(
                    session, current, current_callback, "reused current"
                ), True)
                self.assert_view(
                    session, "A", "reused", False,
                    rows=["reused current"] if current_callback == "finish" else [],
                    error="reused current" if current_callback == "fail" else None,
                )
                self.assert_ignored(session, cancelled, callback)

    def test_cancel_begin_then_old_finish(self):
        self.check_cancel_and_begin("finish")

    def test_cancel_begin_then_old_fail(self):
        self.check_cancel_and_begin("fail")

    def test_valid_success_after_reuse_preserves_rank_and_copies(self):
        session = SearchSession()
        cancelled = session.begin("A", "cancelled")
        session.cancel()
        self.assert_view(session, "A", "cancelled", False)
        current = session.begin("A", "ranked")
        self.assert_view(session, "A", "ranked", True)
        rows = [{"id": "z", "details": [2]}, {"id": "a", "details": [1]}]
        expected = [{"id": "z", "details": [2]}, {"id": "a", "details": [1]}]
        self.assertIs(session.finish(current, rows), True)
        self.assert_view(session, "A", "ranked", False, rows=expected)
        rows[0]["details"].append(99)
        snapshot = session.snapshot()
        snapshot["rows"][1]["details"].append(88)
        self.assert_view(session, "A", "ranked", False, rows=expected)
        for callback in ("finish", "fail"):
            self.assert_ignored(session, cancelled, callback)

    def test_valid_error_after_reuse_and_recovery(self):
        session = SearchSession()
        cancelled = session.begin("A", "cancelled")
        self.assertIs(session.fail(cancelled, "first error"), True)
        self.assert_view(session, "A", "cancelled", False, error="first error")
        session.cancel()
        self.assert_view(session, "A", "cancelled", False)
        current = session.begin("A", "retry")
        self.assert_view(session, "A", "retry", True)
        self.assertIs(session.fail(current, RuntimeError("offline")), True)
        self.assert_view(session, "A", "retry", False, error="offline")
        for callback in ("finish", "fail"):
            self.assert_ignored(session, cancelled, callback)
        recovery = session.begin("A", "recovery")
        self.assert_view(session, "A", "recovery", True)
        self.assertIs(session.finish(recovery, ["ok"]), True)
        self.assert_view(session, "A", "recovery", False, rows=["ok"])


if __name__ == "__main__":
    print("Source under test:", SOURCE, flush=True)
    unittest.main()
