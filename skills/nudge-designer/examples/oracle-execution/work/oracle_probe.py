"""Oracle-authored event-order witnesses; expected state uses issued handles.

The model does not inspect SearchSession's private state or implement a sequence
comparison. A new begin owns the view; cancellation revokes that ownership.
Each named operation delivers at most one terminal callback per schedule.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path


CASES = {
    "same_scope_stale_success_while_busy": [
        ("begin", "old", "A", "q0"), ("begin", "new", "A", "q1"),
        ("finish", "old", ["old"]), ("finish", "new", ["z", "a"])],
    "same_scope_stale_success_after_success": [
        ("begin", "old", "A", "q0"), ("begin", "new", "A", "q1"),
        ("finish", "new", ["z", "a"]), ("finish", "old", ["old"])],
    "same_scope_stale_error_while_busy": [
        ("begin", "old", "A", "q0"), ("begin", "new", "A", "q1"),
        ("fail", "old", "stale error"), ("fail", "new", "current error")],
    "same_scope_stale_error_after_success": [
        ("begin", "old", "A", "q0"), ("begin", "new", "A", "q1"),
        ("finish", "new", ["z", "a"]), ("fail", "old", "stale error")],
    "return_to_scope_stale_success": [
        ("begin", "a0", "A", "q0"), ("begin", "b", "B", "q1"),
        ("begin", "a1", "A", "q2"), ("finish", "a0", ["old"]),
        ("finish", "a1", ["z", "a"])],
    "return_to_scope_stale_error": [
        ("begin", "a0", "A", "q0"), ("begin", "b", "B", "q1"),
        ("begin", "a1", "A", "q2"), ("fail", "a0", "stale error"),
        ("fail", "a1", "current error")],
    "cancelled_success": [
        ("begin", "old", "A", "q"), ("cancel",), ("finish", "old", ["late"])],
    "cancelled_error": [
        ("begin", "old", "A", "q"), ("cancel",), ("fail", "old", "late error")],
    "reuse_after_cancel_stale_success": [
        ("begin", "old", "A", "q0"), ("cancel",),
        ("begin", "new", "A", "q1"), ("finish", "old", ["late"]),
        ("finish", "new", ["z", "a"])],
    "reuse_after_cancel_stale_error": [
        ("begin", "old", "A", "q0"), ("cancel",),
        ("begin", "new", "A", "q1"), ("fail", "old", "late error"),
        ("fail", "new", "current error")],
}


def check_case(cls, operations):
    session = cls()
    tickets = {}
    current = None
    expected = {"scope": None, "query": None, "busy": False, "rows": [], "error": None}
    events = []
    for operation in operations:
        kind = operation[0]
        if kind == "begin":
            _, handle, scope, query = operation
            tickets[handle] = session.begin(scope, query)
            current = handle
            expected = {"scope": scope, "query": query, "busy": True, "rows": [], "error": None}
            accepted, expected_accepted = None, None
        elif kind == "cancel":
            session.cancel()
            current = None
            expected.update(busy=False, rows=[], error=None)
            accepted, expected_accepted = None, None
        else:
            _, handle, value = operation
            expected_accepted = handle == current
            accepted = getattr(session, kind)(tickets[handle], value)
            if expected_accepted:
                expected.update(busy=False,
                                rows=deepcopy(value) if kind == "finish" else [],
                                error=None if kind == "finish" else str(value))
        observed = session.snapshot()
        events.append({"operation": operation, "accepted": accepted,
                       "expected_accepted": expected_accepted,
                       "observed": observed, "expected": deepcopy(expected),
                       "pass": accepted == expected_accepted and observed == expected})
    return {"pass": all(event["pass"] for event in events), "events": events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).with_name("session.py"))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("candidate", args.source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases = {name: check_case(module.SearchSession, ops) for name, ops in CASES.items()}
    report = {"source": str(args.source.resolve()),
              "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
              "method": "Compare callback acceptance and every public snapshot with latest noncancelled issued handle; preserve existing scope/query on cancel.",
              "cases_passed": sum(case["pass"] for case in cases.values()),
              "cases_total": len(cases), "cases": cases}
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["cases_passed"] == len(cases) else 1)


if __name__ == "__main__":
    main()
