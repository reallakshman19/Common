"""Reject unsupported binary columns in validator or reviewer draft nudges.

This is a narrow draft lint, not a model evaluator or proof of scientific quality.
"""
import argparse
from pathlib import Path
import re


BINARY = re.compile(r"(?i)(?:yes\s*/\s*no|y\s*/\s*n|true\s*/\s*false|pass\s*/\s*fail)")
SEPARATOR = re.compile(r"^\s*\|(?:\s*:?-{3,}:?\s*\|){2,}\s*$")
PER_ROW = re.compile(
    r"(?i)(?:for\s+each|per)\s+(?:row|item)\b[^\n.]{0,100}"
    r"(?:yes\s*/\s*no|y\s*/\s*n|true\s*/\s*false|pass\s*/\s*fail)"
)


def check_validator_draft(text):
    """Return one diagnostic for every binary-verdict column/request found."""
    lines = text.splitlines()
    problems = []
    for n, line in enumerate(lines[:-1], 1):
        if line.lstrip().startswith("|") and SEPARATOR.fullmatch(lines[n]):
            if any(BINARY.search(cell) for cell in line.split("|")[1:-1]):
                problems.append(f"line {n}: per-row yes/no column is insufficient")
    if PER_ROW.search(text):
        problems.append("per-row binary verdict requested without substantive review")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a validator draft for binary row columns")
    parser.add_argument("packet", type=Path, help="UTF-8 validator/reviewer Markdown brief")
    args = parser.parse_args(argv)
    try:
        problems = check_validator_draft(args.packet.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"DRAFT_CHECK ERROR: {exc}")
        return 2
    for problem in problems:
        print(f"DRAFT_CHECK FAIL: {problem}")
    if problems:
        return 1
    print("DRAFT_CHECK PASS: no per-row binary verdict column")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
