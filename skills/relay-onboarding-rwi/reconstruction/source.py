#!/usr/bin/env python3
"""WP3 exact-source slice identity. Verifies supplied bytes, NOT call-graph semantics.

An alleged GitHub URL or caller-supplied SHA is not provider authentication.
Use with independently fetched file bytes and readback of its Git blob identity.
"""
from __future__ import annotations

import hashlib
import re

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class SourceSliceError(ValueError):
    pass


def git_blob_sha(data):
    if not isinstance(data, bytes):
        raise SourceSliceError("Git blob contents must be bytes")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def line_slice_digest(data, start, end):
    if not isinstance(data, bytes):
        raise SourceSliceError("source text bytes required")
    if type(start) is not int or type(end) is not int or start < 1 or end < start:
        raise SourceSliceError("invalid line range")
    try:
        source = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceSliceError("text source must be valid UTF-8") from exc
    lines = source.splitlines(keepends=True)
    if end > len(lines):
        raise SourceSliceError("line span exceeds original file")
    excerpt = "".join(lines[start - 1:end]).encode("utf-8")
    return hashlib.sha256(excerpt).hexdigest()


def validate_slice_receipt(data, *, expected_blob, line_start, line_end,
                           expected_line_sha256):
    """Attest only bytes supplied to this function; never semantic correctness."""
    if not isinstance(expected_blob, str) or not HEX40.fullmatch(expected_blob):
        raise SourceSliceError("invalid expected Git blob")
    if not isinstance(expected_line_sha256, str) or not HEX64.fullmatch(expected_line_sha256):
        raise SourceSliceError("invalid expected source-line hash")
    observed_blob = git_blob_sha(data)
    observed_slice = line_slice_digest(data, line_start, line_end)
    return {
        "schema": "onboarding.source-slice/v1",
        "observed_git_blob": observed_blob,
        "observed_line_sha256": observed_slice,
        "status": ("BYTE_SLICE_MATCH" if observed_blob == expected_blob
                   and observed_slice == expected_line_sha256 else "BYTE_SLICE_MISMATCH"),
        "source_provider_authenticated": False,
        "semantic_call_edge_verified": False,
        "owner_acceptance_verified": False,
        "execution_authorized": False
    }
