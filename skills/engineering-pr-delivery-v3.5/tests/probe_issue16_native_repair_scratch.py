"""Issue #16 scratch-only native candidate: exact H1 and monotonic message serial.

This test-helper modifies only a disposable checked-out PR2 candidate in CI.
It cannot authorize, stage, commit or push protected V3.2 files. The pinned
git HEAD remains the UNPATCHED baseline while the working-tree blob changes.
This deliberately DOES NOT address the unresolved same-issue different-TX
concurrency policy/linearization defect (issue #4).
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import subprocess

REL = Path("skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py")
PINNED_HEAD = "da3680459c5b48f44cda822ccf5009be4b035eef"
PINNED_BLOB = "07368987c1156fb687a76139150dd58556c92269"

SERIAL_GUARD = r'''
def _scratch_require_monotonic_buddy_serial(root: Path, issue: int, serial: int) -> None:
    """Fail closed on later durable messages, including a newer intake."""
    folder = root / f"relay/CONTINUITY/episodes/ISSUE-{issue}/messages"
    for path in folder.glob(f"TX.{issue}.*-*.md"):
        found = re.fullmatch(
            rf"TX\.{issue}\.([1-9][0-9]*)-([A-Z0-9_]+)\.md", path.name
        )
        if not found or found.group(2) not in BUDDY_MESSAGE_STAGES:
            raise TransactionError("BUDDY_EXISTING_MESSAGE_NAME_INVALID")
        if path.is_symlink():
            raise TransactionError("BUDDY_EXISTING_MESSAGE_SYMLINK_FORBIDDEN")
        previous = int(found.group(1))
        receipt_path = root / f"relay/TRANSACTIONS/TX.{issue}.{previous}/manifest.yaml"
        if receipt_path.is_symlink() or not receipt_path.is_file():
            raise TransactionError("BUDDY_EXISTING_RECEIPT_MISSING_OR_SYMLINKED")
        receipt = load_manifest(receipt_path)
        payload = path.read_bytes()
        ops = receipt.get("operations") or []
        if (
            receipt.get("id") != f"TX.{issue}.{previous}"
            or receipt.get("status") != "COMMITTED"
            or receipt.get("command") != "PUBLISH_BUDDY_MARKDOWN"
            or len(ops) != 1
            or ops[0].get("path") != path.relative_to(root).as_posix()
            or ops[0].get("after_digest") != _digest_bytes(payload)
        ):
            raise TransactionError("BUDDY_EXISTING_RECEIPT_MISMATCH")
        if previous >= serial:
            raise TransactionError("BUDDY_SERIAL_NOT_MONOTONIC")


'''

def run_git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()

def replace_exact(original: str, needle: str, replacement: str, label: str) -> str:
    count = original.count(needle)
    if count != 1:
        raise ValueError(f"NATIVE_SOURCE_DRIFT_{label}: {count} anchors")
    return original.replace(needle, replacement, 1)

def trial(native_root: Path) -> str:
    if run_git(native_root, "rev-parse", "HEAD") != PINNED_HEAD:
        raise ValueError("NATIVE_HEAD_DRIFT: refusing arbitrary source modification")
    if run_git(native_root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("NATIVE_WORKTREE_NOT_CLEAN")
    source_file = native_root / REL
    if run_git(native_root, "hash-object", str(source_file)) != PINNED_BLOB:
        raise ValueError("NATIVE_BLOB_DRIFT")
    original = source_file.read_text(encoding="utf-8")
    modified = replace_exact(
        original, "def _prior_buddy_message(", SERIAL_GUARD + "def _prior_buddy_message(",
        "SERIAL_GUARD_PLACEMENT",
    )
    marker = '    if not content.startswith("# ") or "\\x00" in content:\n        raise TransactionError("BUDDY_MARKDOWN_HEADING_REQUIRED")\n'
    extra = (
        '    stage = match.group(4)\n'
        '    if stage in {"STAGE1_BASELINE", "STAGE1_PLAN"}:\n'
        '        if not content.startswith(f"# {stage}\\n"):\n'
        '            raise TransactionError("BUDDY_STAGE1_EXACT_HEADING_REQUIRED")\n'
        '        if re.search(\n'
        '            r"(?m)^[ ]{0,3}#[ \\t]+STAGE1_(?:BASELINE|PLAN)(?:[ \\t]+#+)?[ \\t]*\\r?$",\n'
        '            content.split("\\n", 1)[1],\n'
        '        ):\n'
        '            raise TransactionError("BUDDY_STAGE1_COMBINED_ORIGINALS_FORBIDDEN")\n'
    )
    modified = replace_exact(modified, marker, marker + extra, "STAGE1_HEADING")
    call = '    _require_buddy_sequence(root, int(match.group(1)), int(match.group(3)), match.group(4), actor)\n'
    modified = replace_exact(
        modified, call,
        '    _scratch_require_monotonic_buddy_serial(root, int(match.group(1)), int(match.group(3)))\n' + call,
        "SERIAL_CALL",
    )
    ast.parse(modified, filename=str(source_file))
    source_file.write_text(modified, encoding="utf-8")
    after_blob = run_git(native_root, "hash-object", str(source_file))
    if after_blob == PINNED_BLOB:
        raise ValueError("SCRATCH_PATCH_NOT_APPLIED")
    print(f"PINNED_NATIVE_HEAD_UNCHANGED={PINNED_HEAD}")
    print(f"PINNED_NATIVE_BLOB_BEFORE={PINNED_BLOB}")
    print(f"SCRATCH_NATIVE_BLOB_AFTER={after_blob}")
    print(f"SCRATCH_NATIVE_GIT_STATUS={run_git(native_root, 'status', '--porcelain', '--untracked-files=no')}")
    print("SCOPE=SCRATCH_ONLY; NO_GITHUB_PROTECTED_WRITE; NO_CONCURRENCY_LOCK")
    return after_blob

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--native-root", type=Path, required=True)
    ns = ap.parse_args()
    trial(ns.native_root.resolve())
