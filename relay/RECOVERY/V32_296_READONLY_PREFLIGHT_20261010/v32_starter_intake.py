"""B2 V3.2 historic CSV Auditor starter ZIP intake; no extraction or grants.

The expected SHA and counts come from migrated Common #282, which reports the
archived source identity. Matching these bytes is not independent original
Owner approval, a released graph, a trusted fact or production eligibility.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import os
import stat
from typing import Any
from zipfile import BadZipFile, ZipFile

PARENT_ISSUE = "https://github.com/reallakshman19/Common/issues/282"
STARTER_SHA256 = "9f1c317494168bda0ea83baf31c5a6db4d6035085c102743b22c707c3f4a5030"
EXPECTED_MEMBER_COUNT = 35
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 128 * 1024 * 1024
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_COMPRESSION_RATIO = 1000
REQUIRED_BASENAMES = frozenset(("test_r01_input.py", "LOCAL_AGENT_TASKS.md", "TASK_EVIDENCE_TEMPLATE.md"))


@dataclass(frozen=True)
class StarterIntake:
    status: str
    reasons: tuple[str, ...]
    archive_sha256: str | None = None
    file_count: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reasons": list(self.reasons),
            "observed_sha256": self.archive_sha256,
            "members_observed": self.file_count,
            "pin_source": PARENT_ISSUE,
            "original_owner_authenticated": False,
            "original_fixture_tests_run": False,
            "product_pr_verified": False,
            "positive_fact_issuer": False,
            "delp_invoked": False,
            "writer_authorized": False,
        }


def _safe_name(name: str) -> bool:
    if (not isinstance(name, str) or not name or name.startswith("/") or
            "\\" in name or "\x00" in name or ":" in name or
            "//" in name or name.endswith("/")):
        return False
    p = PurePosixPath(name)
    return (all(piece not in (".", "..") for piece in p.parts)
            and len(p.parts) <= 12 and len(name) <= 300)


def inspect_starter_archive(
    archive_path: str | Path,
    *,
    expected_sha256: str = STARTER_SHA256,
) -> StarterIntake:
    """Always HOLD; injectable expected digest exists solely for offline tests."""
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(
            c not in "0123456789abcdef" for c in expected_sha256):
        return StarterIntake("FAILED_TARGET", ("INVALID_EXPECTED_SHA256",))
    if not isinstance(archive_path, (str, Path)) or not str(archive_path):
        return StarterIntake("FAILED_TARGET", ("INVALID_ARCHIVE_PATH",))
    p = Path(archive_path)
    try:
        if not p.is_file() or p.is_symlink():
            return StarterIntake("HOLD_ARCHIVE_MISSING", ("ARCHIVE_UNAVAILABLE_OR_SYMLINK",))
        if p.stat().st_size > MAX_ARCHIVE_BYTES:
            return StarterIntake("HOLD_ARCHIVE_UNSAFE", ("ARCHIVE_TOO_LARGE",))
        digest = sha256()
        with p.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        observed = digest.hexdigest()
        if observed != expected_sha256:
            return StarterIntake("HOLD_ARCHIVE_SHA_MISMATCH", ("PARENT_PIN_MISMATCH",), observed)
        with ZipFile(p) as z:
            members = z.infolist()
            if len(members) != EXPECTED_MEMBER_COUNT:
                return StarterIntake("HOLD_ARCHIVE_SHAPE", ("MEMBER_COUNT_MISMATCH",),
                                     observed, len(members))
            names = [item.filename for item in members]
            if len(set(names)) != len(names) or not all(_safe_name(n) for n in names):
                return StarterIntake("HOLD_ARCHIVE_UNSAFE", ("DUPLICATE_OR_UNSAFE_MEMBER",),
                                     observed, len(members))
            if any(item.is_dir() or item.flag_bits & 1 or
                   stat.S_IFMT(item.external_attr >> 16) == stat.S_IFLNK
                   for item in members):
                return StarterIntake("HOLD_ARCHIVE_UNSAFE", ("DIRECTORY_LINK_OR_ENCRYPTION",),
                                     observed, len(members))
            basenames = {PurePosixPath(n).name for n in names}
            if not REQUIRED_BASENAMES.issubset(basenames):
                return StarterIntake("HOLD_ARCHIVE_SHAPE", ("ORIGINAL_TEST_OR_TASK_MISSING",),
                                     observed, len(members))
            if (any(item.file_size > MAX_MEMBER_BYTES or
                    (item.file_size > 0 and
                     item.file_size > max(1, item.compress_size) * MAX_COMPRESSION_RATIO)
                    for item in members) or
                    sum(item.file_size for item in members) > MAX_UNCOMPRESSED_BYTES):
                return StarterIntake("HOLD_ARCHIVE_UNSAFE", ("ZIP_BOMB_BUDGET_EXCEEDED",),
                                     observed, len(members))
            # CRC and decompression-stream check before calling a supplied ZIP usable.
            for item in members:
                with z.open(item) as stream:
                    while stream.read(1024 * 1024):
                        pass
        # Never certify ownership or evidence based on a hash alone.
        return StarterIntake("HOLD_PARENT_PIN_ONLY", (
            "OUTER_BYTES_MATCH_REPORTED_PARENT_PIN",
            "OWNER_RELEASE_AND_ORIGINAL_TEST_EXECUTION_STILL_REQUIRED",
        ), observed, len(members))
    except (OSError, BadZipFile, RuntimeError, ValueError, EOFError):
        return StarterIntake("HOLD_ARCHIVE_UNREADABLE", ("ZIP_INSPECTION_FAILED",))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True,
                        help="Local original ZIP path; no downloads, writes or extraction")
    args = parser.parse_args()
    result = inspect_starter_archive(args.archive)
    print(json.dumps(result.as_dict(), sort_keys=True, indent=2))
    return 1 if result.status == "FAILED_TARGET" else 2


if __name__ == "__main__":
    raise SystemExit(main())
