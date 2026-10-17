#!/usr/bin/env python3
"""Check exact recovered puppet bytes against the archived SHA-256 identities.

This checks *byte custody only*. It does not approve print dimensions,
mechanical design, safe use, or the 180-second rehearsal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "ORIGINALS_SHA256.json"
ORIGINALS = HERE / "originals"


def verify(manifest_path: Path, root: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "puppet-originals-sha256/v1":
        raise ValueError("Unsupported checksum manifest schema")
    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        raise ValueError("Checksum manifest must contain a nonempty files list")

    root = root.resolve()
    seen: set[str] = set()
    findings: list[dict] = []
    for entry in records:
        rel = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(rel, str) or not rel or "\\" in rel:
            raise ValueError("Invalid relative file path")
        p = PurePosixPath(rel)
        if p.is_absolute() or ".." in p.parts or p.as_posix() != rel:
            raise ValueError(f"Unsafe/noncanonical file path: {rel}")
        if rel in seen:
            raise ValueError(f"Duplicate path in manifest: {rel}")
        seen.add(rel)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError(f"Invalid SHA-256 for {rel}")
        dest = root.joinpath(*p.parts)
        if not dest.resolve().is_relative_to(root):
            raise ValueError(f"File escapes originals root: {rel}")
        if not dest.is_file():
            findings.append({"path": rel, "status": "MISSING", "sha256": None})
            continue
        digest = hashlib.sha256()
        with dest.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        actual = digest.hexdigest()
        findings.append({
            "path": rel,
            "status": "MATCH" if actual == expected else "MISMATCH",
            "sha256": actual
        })
    counts = {key: sum(x["status"] == key for x in findings)
              for key in ("MATCH", "MISSING", "MISMATCH")}
    return {
        "schema": "puppet-originals-custody-check/v1",
        "root": str(root),
        "counts": counts,
        "all_match": counts["MATCH"] == len(findings),
        "scope": "BYTE_IDENTITY_ONLY_NOT_MANUFACTURING_APPROVAL",
        "findings": findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ORIGINALS,
                    help="Directory with king_puppet_final/ and prahlada_puppet_corrected/")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--json", action="store_true", help="Emit machine-readable verdict")
    args = ap.parse_args()
    try:
        result = verify(args.manifest, args.root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"CUSTODY_CHECK_INVALID: {exc}")
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        for row in result["findings"]:
            print(f'{row["status"]:8} {row["path"]}')
        print(f'SUMMARY: {result["counts"]} — '
              f'{"ALL_BYTES_MATCH" if result["all_match"] else "CUSTODY_INCOMPLETE"}')
        print("Not a manufacturing, physical-operability, or rehearsal result.")
    return 0 if result["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
