"""Bounded public event schedules using the prewritten Oracle ownership model.

At most five actions, three begin input variants, any pending callback delivered
once, and cancellation at any point. No concurrency or duplicate-delivery claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from oracle_probe import check_case


def schedules(prefix=(), issued=0, delivered=frozenset(), depth=5):
    if len(prefix) == depth:
        yield prefix
        return
    for scope, query in (("A", "q0"), ("A", "q1"), ("B", "q0")):
        yield from schedules(prefix + (("begin", str(issued), scope, query),),
                             issued + 1, delivered, depth)
    yield from schedules(prefix + (("cancel",),), issued, delivered, depth)
    for handle in range(issued):
        if handle not in delivered:
            for kind, payload in (("finish", ["z", "a"]), ("fail", "current or obsolete error")):
                yield from schedules(prefix + ((kind, str(handle), payload),),
                                     issued, delivered | {handle}, depth)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).with_name("session.py"))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("candidate", args.source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    total = passed = events = 0
    first_failure = None
    for operations in schedules():
        result = check_case(module.SearchSession, operations)
        total += 1
        passed += result["pass"]
        events += len(result["events"])
        if not result["pass"] and first_failure is None:
            first_failure = {"operations": operations, "result": result}
    print(json.dumps({"source": str(args.source.resolve()),
                      "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
                      "method": "All generated length-five schedules; each prefix checked after every action against prewritten public-state ownership model.",
                      "scope": "3 begin variants (A/q0, A/q1, B/q0), cancel anywhere, at most one finish/fail delivery per issued handle; no real concurrency or malformed tickets.",
                      "schedules": total, "passed": passed, "event_comparisons": events,
                      "first_failure": first_failure}, indent=2))
    raise SystemExit(0 if total == passed else 1)


if __name__ == "__main__":
    main()
