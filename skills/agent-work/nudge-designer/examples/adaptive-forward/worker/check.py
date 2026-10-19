#!/usr/bin/env python3
"""Review packet-local synthetic bytes without writing a decoded source view.

Run from this directory with PYTHONDONTWRITEBYTECODE=1 python -B check.py.
Only computation.json is created; existing output is never overwritten.
"""
import base64
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


packet_bytes = (HERE / "packet.md").read_bytes()
artifact_bytes = (HERE / "artifact.json").read_bytes()
artifact = json.loads(artifact_bytes.decode("utf-8", errors="strict"))
raw = base64.b64decode(artifact["data_base64"], validate=True)
computed_raw_sha256 = sha(raw)
decoded = raw.decode(artifact["encoding"], errors="strict")

record_pattern = re.compile(r"^(?P<id>[^|]+?)\s*\|\s*claimed_tokens=(?P<claim>\d+)\s*\|\s*text=(?P<text>.*)$")
lines = decoded.splitlines()
records = []
other_nonempty = []
for line_number, line in enumerate(lines, 1):
    if not line.strip():
        continue
    match = record_pattern.fullmatch(line)
    if match is None:
        other_nonempty.append({"line_number": line_number, "line": line})
        continue
    fields = match.groupdict()
    tokens = fields["text"].split()
    claim = int(fields["claim"])
    records.append({
        "line_number": line_number,
        "id": fields["id"].strip(),
        "claimed_tokens": claim,
        "text": fields["text"],
        "tokens": tokens,
        "computed_tokens": len(tokens),
        "verdict": "MATCH" if len(tokens) == claim else "MISMATCH",
        "non_ascii_characters": [
            {"character": c, "codepoint": f"U+{ord(c):04X}",
             "declared_codec_hex": c.encode(artifact["encoding"], errors="strict").hex()}
            for c in fields["text"] if ord(c) > 127
        ],
    })

# An independently phrased source scan checks the set of candidate record lines;
# any non-record nonempty lines remain explicit instead of silently disappearing.
candidate_lines = [i for i, line in enumerate(lines, 1)
                   if "claimed_tokens=" in line and "text=" in line]
reviewed_lines = [row["line_number"] for row in records]
ids = [row["id"] for row in records]
coverage_ok = (candidate_lines == reviewed_lines
               and len(ids) == len(set(ids))
               and not other_nonempty)

result = {
    "assignment": "packet.md: source claim review",
    "runtime": {"python": sys.version.split()[0], "bytecode_disabled": sys.dont_write_bytecode,
                "host_model": "UNKNOWN", "reasoning_configuration": "UNKNOWN",
                "formal_qualification": "UNKNOWN"},
    "sources": {
        "packet": {"path": "packet.md", "file_bytes_sha256": sha(packet_bytes)},
        "artifact": {"path": "artifact.json", "file_bytes_sha256": sha(artifact_bytes)},
        "payload": {"representation": artifact["representation"],
                    "declared_encoding": artifact["encoding"],
                    "byte_length": len(raw),
                    "declared_raw_sha256": artifact["raw_sha256"],
                    "computed_raw_sha256": computed_raw_sha256,
                    "digest_matches": computed_raw_sha256 == artifact["raw_sha256"],
                    "base64_validation": "PASS", "strict_decode": "PASS",
                    "strict_roundtrip_matches_raw": decoded.encode(artifact["encoding"], errors="strict") == raw},
    },
    "algorithm": "After strict declared-codec decoding, parse id | claimed_tokens=<n> | text=<text>; count len(text.split()). Python str.split() with no argument splits on whitespace, excluding field labels, headers and blank lines. Standalone punctuation is a token.",
    "prediction_before_execution": "A standalone punctuation token contributes one to len(text.split()); any earlier count derived from ignored decoding errors is not evidence against original-byte claims.",
    "records": records,
    "coverage": {"source_line_count": len(lines),
                 "nonempty_lines": sum(bool(line.strip()) for line in lines),
                 "blank_lines": sum(not line.strip() for line in lines),
                 "candidate_record_lines": candidate_lines,
                 "reviewed_record_lines": reviewed_lines,
                 "reviewed_record_ids": ids,
                 "reviewed_record_count": len(records),
                 "unparsed_nonempty_lines": other_nonempty,
                 "duplicate_record_ids": sorted({i for i in ids if ids.count(i) > 1}),
                 "complete_for_this_artifact": coverage_ok},
    "findings": {"token_claim_mismatches": [row["id"] for row in records if row["verdict"] == "MISMATCH"],
                 "input_digest_mismatch": computed_raw_sha256 != artifact["raw_sha256"],
                 "interpretation_or_access_blockers": []},
    "preservation": {
        "packet_unchanged_during_computation": (HERE / "packet.md").read_bytes() == packet_bytes,
        "artifact_unchanged_during_computation": (HERE / "artifact.json").read_bytes() == artifact_bytes,
        "decoded_source_bytes_written": False},
    "limits": ["Synthetic artifact only; no wider product acceptance.",
               "The sender's earlier UTF-8 view was not supplied or reproduced.",
               "Strict decoding and a matching digest establish interpretation and identity for this assignment, not independent proof of intended encoding or source truth.",
               "Self-check by the same worker; no independent reviewer or model qualification established."],
}
output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
with (HERE / "computation.json").open("x", encoding="utf-8", newline="\n") as handle:
    handle.write(output)
print(output, end="")
