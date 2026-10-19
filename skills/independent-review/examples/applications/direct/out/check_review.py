#!/usr/bin/env python3
"""Disposable, read-only checks of the exact task-local estimator.

The expected values come from owner.md: apply floor(subtotal / 10) only
when subtotal >= 10000, then add delivery. Existing tests are replayed as
artifacts, not used as the oracle. No input file is written.
"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
INPUTS = OUT.parent / "inputs"
FILES = ("owner.md", "rate.py", "test_rate.py")


def hashes():
    return {
        name: hashlib.sha256((INPUTS / name).read_bytes()).hexdigest()
        for name in FILES
    }


def owner_expectation(subtotal, delivery):
    # Exact integer arithmetic, following the item-only threshold in owner.md.
    discount = subtotal // 10 if subtotal >= 10000 else 0
    return subtotal - discount + delivery


def main():
    print("READ-ONLY ESTIMATOR REVIEW", flush=True)
    print("Python:", sys.version.replace("\n", " "), flush=True)
    print("Platform:", platform.platform(), flush=True)
    print("Candidate:", INPUTS / "rate.py", flush=True)
    before = hashes()
    print("Input SHA-256 before:", json.dumps(before, sort_keys=True), flush=True)

    command = [sys.executable, "-B", "-m", "unittest", "-v", "test_rate"]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    print("\nEXISTING TESTS:", repr(command), "cwd=", INPUTS, flush=True)
    existing = subprocess.run(
        command,
        cwd=INPUTS,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    print(existing.stdout, end="", flush=True)
    print("Existing tests exit:", existing.returncode, flush=True)

    spec = importlib.util.spec_from_file_location("reviewed_rate", INPUTS / "rate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    estimate = module.estimate

    observations = []

    def record_valid(group, label, subtotal, delivery, expected):
        row = {
            "group": group,
            "label": label,
            "subtotal": subtotal,
            "delivery": delivery,
            "expected": expected,
        }
        try:
            actual = estimate(subtotal, delivery)
            row.update(actual=actual, actual_type=type(actual).__name__)
            row["passed"] = type(actual) is int and actual == expected
        except Exception as exc:
            row.update(exception=repr(exc), passed=False)
        observations.append(row)

    # Hand-derived concrete examples include both sides of each relevant boundary.
    concrete = [
        ("zero", 0, 0, 0),
        ("delivery_only", 0, 10000, 10000),
        ("zero_floor_discount", 9, 10000, 10009),
        ("first_nonzero_wrong_discount", 10, 9990, 10000),
        ("below_threshold_no_delivery", 9999, 0, 9999),
        ("delivery_one_crosses_threshold", 9999, 1, 10000),
        ("delivery_just_below_crossing", 9000, 999, 9999),
        ("delivery_hits_threshold", 9000, 1000, 10000),
        ("small_items_large_delivery", 4000, 6000, 10000),
        ("exact_item_threshold", 10000, 0, 9000),
        ("threshold_with_delivery", 10000, 500, 9500),
        ("fractional_discount_down_1", 10001, 500, 9501),
        ("fractional_discount_down_9", 10009, 0, 9009),
        ("discount_cent_step", 10010, 0, 9009),
        ("fractional_discount_down_19", 10019, 1, 9019),
        ("large_author_case", 20000, 500, 18500),
    ]
    for label, subtotal, delivery, expected in concrete:
        record_valid("concrete", label, subtotal, delivery, expected)

    huge = 10**100 + 9
    record_valid("large_integer", "arbitrary_precision", huge, 37,
                 owner_expectation(huge, 37))

    subtotals = sorted(set(range(31)) | set(range(9980, 10031)) |
                       {4000, 5000, 9000, 20000, huge})
    for subtotal in subtotals:
        deliveries = {0, 1, 9, 10, 500, 999, 1000, 6000, 10000, 10001}
        if subtotal < 10000:
            crossing = 10000 - subtotal
            deliveries.update({crossing - 1, crossing, crossing + 1})
        for delivery in sorted(deliveries):
            record_valid("boundary_sweep", "owner_formula", subtotal, delivery,
                         owner_expectation(subtotal, delivery))

    invalid_values = [
        -1, -10000, 0.0, 0.5, True, False, None, "10000", [1],
        complex(1, 0), float("nan"), float("inf"),
    ]
    for index, value in enumerate(invalid_values):
        for position in (0, 1):
            arguments = [0, 0]
            arguments[position] = value
            row = {
                "group": "invalid_input",
                "label": f"invalid_{index}_position_{position}",
                "value_repr": repr(value),
                "value_type": type(value).__name__,
                "argument": "subtotal" if position == 0 else "delivery",
            }
            try:
                row.update(actual=repr(estimate(*arguments)), passed=False)
            except (ValueError, TypeError) as exc:
                row.update(exception=type(exc).__name__, passed=True)
            except Exception as exc:
                row.update(exception=repr(exc), passed=False)
            observations.append(row)

    groups = {}
    for row in observations:
        counts = groups.setdefault(row["group"], {"passed": 0, "failed": 0})
        counts["passed" if row["passed"] else "failed"] += 1
    failed = [row for row in observations if not row["passed"]]

    print("\nCHECK SUMMARY:", json.dumps(groups, sort_keys=True), flush=True)
    print("Concrete observations:", flush=True)
    for row in observations:
        if row["group"] in ("concrete", "large_integer"):
            print(json.dumps(row, sort_keys=True), flush=True)
    print("First 10 boundary sweep failures:", flush=True)
    for row in [r for r in failed if r["group"] == "boundary_sweep"][:10]:
        print(json.dumps(row, sort_keys=True), flush=True)

    after = hashes()
    unchanged = before == after
    print("Input SHA-256 after:", json.dumps(after, sort_keys=True), flush=True)
    print("Inputs unchanged:", unchanged, flush=True)
    evidence = {
        "candidate": str(INPUTS / "rate.py"),
        "python": sys.version,
        "hashes_before": before,
        "hashes_after": after,
        "inputs_unchanged": unchanged,
        "existing_tests": {
            "command": command,
            "cwd": str(INPUTS),
            "exit": existing.returncode,
            "output": existing.stdout,
        },
        "summary": groups,
        "observations": observations,
    }
    evidence_path = OUT / "check_evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
    print("Detailed evidence:", evidence_path, flush=True)
    print("Review checks:", "FAIL" if failed else "PASS", flush=True)
    return 1 if failed or existing.returncode or not unchanged else 0


if __name__ == "__main__":
    raise SystemExit(main())
