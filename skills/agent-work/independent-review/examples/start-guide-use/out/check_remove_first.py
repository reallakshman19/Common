"""Disposable, task-local evidence checks; the supplied inputs are read only."""

from __future__ import annotations

import hashlib
import itertools
import platform
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INPUTS = ROOT / "inputs"
CANDIDATE = INPUTS / "candidate.py"
OWNER = INPUTS / "owner.txt"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exercise(function, values, item, expected):
    """Check the rule's output and input preservation, without requiring freshness."""
    argument = list(values)
    before = list(argument)
    try:
        actual = function(argument, item)
        unchanged = argument == before and all(
            a is b for a, b in zip(argument, before, strict=True)
        )
        success = actual == expected and unchanged
        return success, repr(actual), unchanged
    except Exception as error:
        return False, f"{type(error).__name__}: {error}", argument == before


MANUAL_CASES = [
    ("empty, absent", [], 7, []),
    ("nonempty, absent", [3, 1, 2], 9, [3, 1, 2]),
    ("singleton match", [7], 7, []),
    ("first-position match", [7, 1, 2], 7, [1, 2]),
    ("middle-position match", [1, 7, 2], 7, [1, 2]),
    ("last-position match", [1, 2, 7], 7, [1, 2]),
    ("separated duplicates", [7, 1, 7, 2, 7], 7, [1, 7, 2, 7]),
    ("adjacent duplicates", [1, 7, 7, 2], 7, [1, 7, 2]),
    ("all values match", [7, 7, 7], 7, [7, 7]),
    ("falsy requested value", [0, 1, 0, 2], 0, [1, 0, 2]),
    ("None requested value", [None, "x", None], None, ["x", None]),
    ("equal numeric values", [True, 2, 1, 3], 1, [2, 1, 3]),
]


def remove_all(values, item):
    return [value for value in values if value != item]


def remove_last(values, item):
    result = list(values)
    matches = [index for index, value in enumerate(result) if value == item]
    if matches:
        del result[matches[-1]]
    return result


def mutate_input(values, item):
    if item in values:
        values.remove(item)
    return values


def reverse_survivors(values, item):
    result = list(values)
    if item in result:
        result.remove(item)
    return result[::-1]


def fail_if_absent(values, item):
    result = list(values)
    result.remove(item)
    return result


def no_removal(values, item):
    return list(values)


def main():
    start = datetime.now(timezone.utc).isoformat()
    original_bytes = {path: path.read_bytes() for path in (OWNER, CANDIDATE)}
    print(f"Run: remove-first-review-01; UTC start: {start}")
    print(f"Environment: {platform.python_implementation()} {platform.python_version()}")
    for path, data in original_bytes.items():
        print(f"BEFORE {path.name}: {len(data)} bytes; SHA256 {digest(data)}")

    # Compile the exact inspected bytes, avoiding import-created __pycache__ files.
    namespace = {"__name__": "reviewed_candidate"}
    exec(compile(original_bytes[CANDIDATE], str(CANDIDATE), "exec"), namespace)
    candidate = namespace["remove_first"]

    failures = []
    print("\nMANUAL ORACLE: explicit expected lists derived from owner.txt")
    for name, values, item, expected in MANUAL_CASES:
        passed, actual, unchanged = exercise(candidate, values, item, expected)
        print(
            f"{'PASS' if passed else 'FAIL'} {name}: input={values!r}, item={item!r}; "
            f"expected={expected!r}; actual={actual}; input_unchanged={unchanged}"
        )
        if not passed:
            failures.append(name)

    class Token:
        def __init__(self, key, label):
            self.key = key
            self.label = label

        def __eq__(self, other):
            return isinstance(other, Token) and self.key == other.key

        def __repr__(self):
            return f"Token({self.key!r}, {self.label!r})"

    first = Token(7, "first")
    middle = Token(8, "middle")
    later = Token(7, "later")
    tokens = [first, middle, later]
    result = candidate(tokens, Token(7, "requested"))
    identity_passed = (
        len(result) == 2
        and result[0] is middle
        and result[1] is later
        and len(tokens) == 3
        and all(a is b for a, b in zip(tokens, [first, middle, later], strict=True))
    )
    print(
        f"{'PASS' if identity_passed else 'FAIL'} equal, distinct objects: "
        f"input={tokens!r}; actual={result!r}; "
        "required survivor identities=[middle, later]; original identities preserved="
        f"{len(tokens) == 3 and all(a is b for a, b in zip(tokens, [first, middle, later], strict=True))}"
    )
    if not identity_passed:
        failures.append("equal distinct objects")

    a, b, c = [1], [2], [1]
    nested = [a, b, c]
    nested_result = candidate(nested, [1])
    nested_passed = (
        nested == [[1], [2], [1]]
        and len(nested_result) == 2
        and nested_result[0] is b
        and nested_result[1] is c
        and all(x is y for x, y in zip(nested, [a, b, c], strict=True))
    )
    print(
        f"{'PASS' if nested_passed else 'FAIL'} nested-list equality: "
        f"expected=[[2], [1]]; actual={nested_result!r}; "
        f"original={nested!r}; survivor identities correct={nested_passed}"
    )
    if not nested_passed:
        failures.append("nested list")

    # Positional oracle: exclude the earliest equal position, or exclude nothing.
    # It does not use membership, list.remove, or the candidate's result as truth.
    exhaustive_count = 0
    for length in range(7):
        for source in itertools.product((-1, 0, 1), repeat=length):
            for item in (-1, 0, 1, 2):
                positions = [i for i, value in enumerate(source) if value == item]
                excluded = min(positions) if positions else None
                expected = [value for i, value in enumerate(source) if i != excluded]
                passed, actual, unchanged = exercise(candidate, source, item, expected)
                exhaustive_count += 1
                if not passed:
                    failures.append(f"exhaustive {source!r}, {item!r}")
                    print(
                        f"FAIL exhaustive input={source!r}; item={item!r}; "
                        f"expected={expected!r}; actual={actual}; unchanged={unchanged}"
                    )
    print(f"EXHAUSTIVE: {exhaustive_count} cases checked; candidate failures={len(failures)}")

    print("\nCONTRARY IMPLEMENTATIONS: validation of the manual oracle")
    mutants = {
        "remove every occurrence": remove_all,
        "remove last occurrence": remove_last,
        "mutate the input": mutate_input,
        "reverse surviving order": reverse_survivors,
        "raise if absent": fail_if_absent,
        "never remove": no_removal,
    }
    for name, function in mutants.items():
        rejected = []
        first_witness = None
        for case_name, values, item, expected in MANUAL_CASES:
            passed, actual, unchanged = exercise(function, values, item, expected)
            if not passed:
                rejected.append(case_name)
                if first_witness is None:
                    first_witness = (
                        f"{case_name}: input={values!r}, item={item!r}; expected={expected!r}; "
                        f"actual={actual}; input_unchanged={unchanged}"
                    )
        print(
            f"{'REJECTED' if rejected else 'SURVIVED'} {name}: "
            f"{len(rejected)}/{len(MANUAL_CASES)} manual cases reject; witness: {first_witness}"
        )
        if not rejected:
            failures.append(f"oracle admitted mutant: {name}")

    print("\nINPUT CUSTODY")
    for path, before in original_bytes.items():
        after = path.read_bytes()
        unchanged = before == after
        print(f"AFTER {path.name}: SHA256 {digest(after)}; byte_identical={unchanged}")
        if not unchanged:
            failures.append(f"input changed: {path.name}")
    print(f"RESULT: {'PASS' if not failures else 'FAIL'}; failures={failures!r}")
    print(f"UTC finish: {datetime.now(timezone.utc).isoformat()}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
