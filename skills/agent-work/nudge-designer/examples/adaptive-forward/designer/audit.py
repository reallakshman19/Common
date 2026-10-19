"""Local source audit; does not send, dispatch, accept work or alter raw inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


BASE = Path(__file__).resolve().parent
RAW_NAMES = ("owner.md", "packets.json", "receipts.json", "prior-review.md")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    before = {name: sha256((BASE / name).read_bytes()) for name in RAW_NAMES}
    packets = json.loads((BASE / "packets.json").read_bytes().decode("utf-8", errors="strict"))
    receipts = json.loads((BASE / "receipts.json").read_bytes().decode("utf-8", errors="strict"))
    observations = {}
    for revision, packet in packets.items():
        raw = packet.encode("utf-8", errors="strict")
        lines = packet.splitlines()
        assert lines and lines[0] == revision, "Packet key/header conflict"
        records = [
            {"physical_line": number, "value": line}
            for number, line in enumerate(lines[1:], start=2)
            if line != ""
        ]
        observations[revision] = {
            "header": lines[0],
            "utf8_byte_length": len(raw),
            "packet_utf8_sha256": sha256(raw),
            "record_count": len(records),
            "record_witnesses": records,
        }

    digest_matches = {
        field: [
            revision for revision, observed in observations.items()
            if observed["packet_utf8_sha256"] == receipts[field]
        ]
        for field in ("issued_packet_sha256", "delivered_packet_sha256", "recipient_packet_sha256")
    }
    selected_revision = receipts["issued_revision"]
    assert selected_revision == "R20", "Owner's selected revision changed; reconcile before use"
    candidate = BASE / "R20-draft.txt"
    candidate_bytes = packets[selected_revision].encode("utf-8", errors="strict")
    assert sha256(candidate_bytes) == receipts["issued_packet_sha256"], "Issued digest mismatch"
    if candidate.exists():
        assert candidate.read_bytes() == candidate_bytes, "Existing draft differs; preserve and reconcile"
    else:
        candidate.write_bytes(candidate_bytes)

    after = {name: sha256((BASE / name).read_bytes()) for name in RAW_NAMES}
    assert before == after, "Raw input bytes changed"
    report = {
        "scope": "Executed local audit of supplied sources; no transport inspected or performed",
        "python_observed": sys.version.split()[0],
        "input_file_byte_sha256_before": before,
        "input_file_byte_sha256_after": after,
        "raw_inputs_unchanged": before == after,
        "packet_digest_representation": receipts["digest_representation"],
        "parsing_rule": "First splitlines() entry is the exact revision header. Count every later nonempty line; exclude header and empty lines, do not strip or deduplicate.",
        "packet_observations": observations,
        "supplied_receipt_digest_matches": digest_matches,
        "delivered_equals_recipient_digest": receipts["delivered_packet_sha256"] == receipts["recipient_packet_sha256"],
        "delivered_equals_issued_digest": receipts["delivered_packet_sha256"] == receipts["issued_packet_sha256"],
        "local_candidate": {
            "locator": "R20-draft.txt",
            "state": "LOCAL_DRAFT_NOT_DELIVERED",
            "byte_sha256": sha256(candidate.read_bytes()),
            "equals_R20_packet_utf8_bytes": candidate.read_bytes() == candidate_bytes,
        },
        "interpretation": {
            "retained": "Prior native count and listed witnesses agree with independently recomputed supplied R19 content.",
            "unsupported": "R20 complete, all checks pass: the native report cites R19 and excludes other claims/production outcomes.",
            "correction": "Fix source selection/identity before rerunning affected R20 claims.",
        },
        "limits": [
            "Receipt metadata is supplied evidence; actual delivery/access/execution and source authenticity were not observed.",
            "This audit is a sender-side recomputation, not a new independent reviewer or next-worker execution.",
            "Record count evidence does not establish complete R20 review or production acceptance.",
            "Model, reasoning configuration, formal qualification and broader worker capability remain UNKNOWN.",
        ],
    }
    (BASE / "audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"audit": "audit.json", "candidate": "R20-draft.txt", "raw_inputs_unchanged": True, "packet_counts": {revision: row["record_count"] for revision, row in observations.items()}, "digest_matches": digest_matches}))


if __name__ == "__main__":
    main()
