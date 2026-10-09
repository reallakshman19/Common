"""#16 scratch-only positive fixture migration for the V3.5 Stage1 H1 contract.

This never modifies committed GitHub V3.2 tests. It edits a disposable CI
checkout AFTER the original native suite has separately been run RED against
the source-only trial. It replaces exactly seven OLD positive sample headings
with the newly required canonical first-line Stage1 H1 and preserves their
substantive text. It does not remove, relax or edit any negative expectations.
Native test source HEAD remains the unpatched original commit; record the dirty
test-file blob separately. Do not claim original unmodified tests passed.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import subprocess

REL = Path("skills/engineering-pr-delivery-v3.2/tests/test_relay_tx.py")
HEAD = "da3680459c5b48f44cda822ccf5009be4b035eef"
BLOB = "6f6207b0f95315ca18b6d89f19374525921ea06c"

# These strings are source tokens, not execution-produced fixture bytes.
POSITIVE_ONLY = (
    (r'b"# Independent original system baseline\n\nObserved source-to-consumer path.\n"',
     r'b"# STAGE1_BASELINE\n\nObserved source-to-consumer path.\n"'),
    (r'b"# Two independent designs\n\nDesign A and B; decisive falsifiers.\n"',
     r'b"# STAGE1_PLAN\n\nDesign A and B; decisive falsifiers.\n"'),
    (r'b"# Original source independently reconstructed\n"',
     r'b"# STAGE1_BASELINE\n\nOriginal source independently reconstructed.\n"'),
    (r'b"# Independent options and falsifiers\n"',
     r'b"# STAGE1_PLAN\n\nIndependent options and falsifiers.\n"'),
    (r'b"# Source producer and consumer witness\n"',
     r'b"# STAGE1_BASELINE\n\nSource producer and consumer witness.\n"'),
    (r'b"# Two alternate HOWs and falsifiers\n"',
     r'b"# STAGE1_PLAN\n\nTwo alternate HOWs and falsifiers.\n"'),
    (r'b"# Original cutoff 1 baseline\n"',
     r'b"# STAGE1_BASELINE\n\nOriginal cutoff 1 baseline.\n"'),
)

def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()

def migrate(root: Path):
    if git(root, "rev-parse", "HEAD") != HEAD:
        raise ValueError("NATIVE_BASELINE_MISMATCH")
    p = root / REL
    if git(root, "hash-object", str(p)) != BLOB:
        raise ValueError("ORIGINAL_NATIVE_TEST_BLOB_MISMATCH")
    contents = p.read_text(encoding="utf-8")
    for old, new in POSITIVE_ONLY:
        if contents.count(old) != 1:
            raise ValueError(f"NATIVE_FIXTURE_SOURCE_DRIFT: {old}")
        contents = contents.replace(old, new, 1)
    ast.parse(contents, filename=str(p))
    p.write_text(contents, encoding="utf-8")
    print(f"ORIGINAL_NATIVE_TEST_BLOB={BLOB}")
    print(f"SCRATCH_MIGRATED_NATIVE_TEST_BLOB={git(root, 'hash-object', str(p))}")
    print("NEGATIVE_TEST_EXPECTATIONS_UNMODIFIED=YES")
    print("TEST_MIGRATION_IS_ADVISORY_NOT_APPROVED=YES")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--native-root", type=Path, required=True)
    ns = ap.parse_args()
    migrate(ns.native_root.resolve())
