"""Reviewer-only migration trial for obsolete *positive* native Stage1 fixtures.

Runs ONLY on a disposable Actions/native-candidate checkout after the advisory
transactionlib patch. Migrates exactly seven original success fixtures from
generic document titles to REQUIRED real original-file stage headings. Does
NOT alter assertions, negative expectations, tested source semantics or any
protected source in GitHub. Legacy unmodified suite RED remains recorded.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

PIN = "da3680459c5b48f44cda822ccf5009be4b035eef"
BLOB = "6f6207b0f95315ca18b6d89f19374525921ea06c"
TARGET = "skills/engineering-pr-delivery-v3.2/tests/test_relay_tx.py"

# Source-literal byte strings, not an attempt to rewrite stdout evidence.
POSITIVE_FIXTURE_MIGRATIONS = (
    (r'b"# Independent original system baseline\n"', r'b"# STAGE1_BASELINE\n"'),
    (r'b"# Two independent designs\n"', r'b"# STAGE1_PLAN\n"'),
    (r'b"# Original source independently reconstructed\n"', r'b"# STAGE1_BASELINE\n"'),
    (r'b"# Independent options and falsifiers\n"', r'b"# STAGE1_PLAN\n"'),
    (r'b"# Source producer and consumer witness\n"', r'b"# STAGE1_BASELINE\n"'),
    (r'b"# Two alternate HOWs and falsifiers\n"', r'b"# STAGE1_PLAN\n"'),
    (r'b"# Original cutoff 1 baseline\n"', r'b"# STAGE1_BASELINE\n"'),
)


def git(root: pathlib.Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=pathlib.Path, required=True)
    args = parser.parse_args()
    root = args.native_root.resolve()
    if git(root, "rev-parse", "HEAD") != PIN:
        raise RuntimeError("PINNED_NATIVE_SOURCE_MISMATCH")
    blob = git(root, "rev-parse", f"HEAD:{TARGET}")
    if blob != BLOB:
        raise RuntimeError(f"NATIVE_FIXTURE_SOURCE_DRIFT: {blob}")
    path = root / TARGET
    source = path.read_text(encoding="utf-8")
    for old, new in POSITIVE_FIXTURE_MIGRATIONS:
        if source.count(old) != 1:
            raise RuntimeError(f"POSITIVE_FIXTURE_ANCHOR_MISMATCH: {old!r}")
        source = source.replace(old, new, 1)
    path.write_text(source, encoding="utf-8")
    actual = set(git(root, "status", "--porcelain").splitlines())
    allowed = {
        "M skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py",
        "M skills/engineering-pr-delivery-v3.2/tests/test_relay_tx.py",
    }
    if actual != allowed:
        raise RuntimeError(f"UNEXPECTED_EPHEMERAL_SCOPE: {actual}")
    print(f"NATIVE_IMMUTABLE_COMMIT_UNCHANGED={git(root,'rev-parse','HEAD')}", flush=True)
    print(f"POSITIVE_FIXTURE_MIGRATION_COUNT={len(POSITIVE_FIXTURE_MIGRATIONS)}", flush=True)
    print(f"EPHEMERAL_FIXTURE_BLOB={git(root,'hash-object',TARGET)}", flush=True)
    print("ONLY_SUCCESS_FIXTURE_BYTES_CHANGED_NO_ASSERTIONS_WEAKENED", flush=True)
    print("PROTECTED_GITHUB_SOURCE_UNCHANGED_OWNER_GRANT_STILL_REQUIRED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
