"""Advisory issue #16: stage a native Buddy ingress patch in an EPHEMERAL checkout.

Never edit, commit, force-push or merge the frozen V3.2 source in GitHub.
This file modifies only a separate Actions/native-candidate worktree. It checks
the immutable preimage Git SHA and transactionlib blob before patching; the
new worktree blob is NOT a new immutable GitHub commit or Owner authorization.

This deliberately does NOT fix simultaneous different-TX admission in _prepare.
The Owner/Local concurrent issue-scoped policy remains UNRESOLVED.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

NATIVE_SHA = "da3680459c5b48f44cda822ccf5009be4b035eef"
NATIVE_BLOB = "07368987c1156fb687a76139150dd58556c92269"
RELATIVE = pathlib.Path("skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py")

SEQUENCE_HELPER = r'''

def _reject_superseded_buddy_sequence(root: Path, issue: int, incoming_seq: int) -> None:
    """Advisory: reject a newly published lower serial after a later receipt.

    One-pass local committed-receipt scan. This is NOT atomic admission; two
    distinct concurrent TX IDs can still pass before either is committed.
    """
    folder = root / f"relay/CONTINUITY/episodes/ISSUE-{issue}/messages"
    for path in folder.glob(f"TX.{issue}.*-*.md"):
        if path.is_symlink():
            raise TransactionError("BUDDY_PRIOR_MESSAGE_SYMLINK_FORBIDDEN")
        match = re.fullmatch(
            rf"TX\.{issue}\.([1-9][0-9]*)-([A-Z0-9_]+)\.md", path.name
        )
        if match is None:
            raise TransactionError("BUDDY_ISSUE_MESSAGE_INVALID")
        observed_seq = int(match.group(1))
        if observed_seq < incoming_seq:
            continue
        tx_path = root / f"relay/TRANSACTIONS/TX.{issue}.{observed_seq}/manifest.yaml"
        if tx_path.is_symlink():
            raise TransactionError("BUDDY_PRIOR_RECEIPT_SYMLINK_FORBIDDEN")
        if not tx_path.is_file():
            raise TransactionError("BUDDY_PRIOR_MESSAGE_UNRECORDED")
        receipt = load_manifest(tx_path)
        operations = receipt.get("operations") or []
        payload = path.read_bytes()
        if (
            receipt.get("id") != f"TX.{issue}.{observed_seq}"
            or receipt.get("status") != "COMMITTED"
            or receipt.get("command") != "PUBLISH_BUDDY_MARKDOWN"
            or len(operations) != 1
            or operations[0].get("path") != path.relative_to(root).as_posix()
            or operations[0].get("after_digest") != _digest_bytes(payload)
        ):
            raise TransactionError("BUDDY_PRIOR_MESSAGE_RECEIPT_MISMATCH")
        raise TransactionError("BUDDY_STALE_STAGE_CHAIN")


'''

PAYLOAD_ADDENDUM = r'''    if match.group(4) in ("STAGE1_BASELINE", "STAGE1_PLAN"):
        stage = match.group(4)
        if not content.startswith(f"# {stage}\n"):
            raise TransactionError("BUDDY_STAGE1_EXACT_HEADING_REQUIRED")
        # Reject separately named Stage1 ATX H1 inside one original B file.
        # This is a bounded advisory shape contract, not provenance proof.
        if re.search(
            r"(?m)^[ ]{0,3}#[ \t]+STAGE1_(?:BASELINE|PLAN)(?:[ \t]+#+)?[ \t]*\r?$",
            content.split("\n", 1)[1],
        ):
            raise TransactionError("BUDDY_STAGE1_COMBINED_ORIGINALS_FORBIDDEN")
    _reject_superseded_buddy_sequence(
        root, int(match.group(1)), int(match.group(3))
    )
'''


def git(root: pathlib.Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"ADVISORY_PATCH_ANCHOR_MISMATCH: {label}: {source.count(old)}")
    return source.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=pathlib.Path, required=True)
    parser.add_argument("--expected-native-sha", default=NATIVE_SHA)
    args = parser.parse_args()
    root = args.native_root.resolve()
    observed = git(root, "rev-parse", "HEAD")
    if observed != args.expected_native_sha or observed != NATIVE_SHA:
        raise RuntimeError(f"PROTECTED_PREIMAGE_SHA_MISMATCH: {observed}")
    if git(root, "status", "--porcelain"):
        raise RuntimeError("REQUIRES_CLEAN_DISPOSABLE_NATIVE_CHECKOUT")
    original_blob = git(root, "rev-parse", f"HEAD:{RELATIVE.as_posix()}")
    if original_blob != NATIVE_BLOB:
        raise RuntimeError(f"PROTECTED_NATIVE_BLOB_DRIFT: {original_blob}")
    path = root / RELATIVE
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "\n\ndef _validate_buddy_markdown_transaction(",
        SEQUENCE_HELPER + "def _validate_buddy_markdown_transaction(",
        "helper insertion",
    )
    anchor = (
        '    if not content.startswith("# ") or "\\x00" in content:\n'
        '        raise TransactionError("BUDDY_MARKDOWN_HEADING_REQUIRED")\n'
    )
    source = replace_once(
        source, anchor, anchor + PAYLOAD_ADDENDUM, "shared ingress insertion"
    )
    # This is a reproducible CI-worktree-only source change. No protected
    # GitHub file or authority manifest may be written by this program.
    path.write_text(source, encoding="utf-8")
    dirty = git(root, "status", "--porcelain")
    expected_dirty = f" M {RELATIVE.as_posix()}"
    if dirty != expected_dirty:
        raise RuntimeError(f"DIRTY_WORKTREE_SCOPE_MISMATCH: {dirty!r}")
    print(f"PROTECTED_ORIGINAL_COMMIT={observed}", flush=True)
    print(f"PROTECTED_ORIGINAL_BLOB={original_blob}", flush=True)
    print(f"EPHEMERAL_PATCHED_BLOB={git(root, 'hash-object', str(RELATIVE))}", flush=True)
    print(f"EPHEMERAL_GIT_HEAD_UNCHANGED={git(root, 'rev-parse', 'HEAD')}", flush=True)
    print("EPHEMERAL_TRIAL_ONLY_NOT_AN_OWNER_GRANT_OR_MERGED_NATIVE_PATCH", flush=True)
    print("CONCURRENT_DIFFERENT_TX_ISSUE_POLICY_UNRESOLVED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
