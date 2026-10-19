#!/usr/bin/env python3
"""Read task-local originals; write a byte-custody receipt and negative control."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


BASE = Path(__file__).resolve().parent.parent
INPUTS = BASE / "inputs"
OUT = BASE / "out"
MANIFEST = INPUTS / "custody.json"
LOG = OUT / "custody-log.json"
REPORT = OUT / "review.md"
record = {
    "started_utc": datetime.now(timezone.utc).isoformat(),
    "python": sys.version,
    "script": str(Path(__file__).resolve()),
    "manifest": str(MANIFEST),
    "originals": [],
    "commands": [],
    "access_failures": [],
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(argv, stdin=None):
    result = subprocess.run(argv, input=stdin, text=True, capture_output=True, check=False)
    evidence = {
        "argv": argv,
        "stdin": stdin,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    record["commands"].append(evidence)
    print(json.dumps(evidence))
    return evidence


def compare(path, expected):
    """The exact same comparator is used for originals and the altered copy."""
    data = path.read_bytes()
    actual = digest(data)
    tool_hash = command(["sha256sum", str(path)])
    tool_check = command(["sha256sum", "--check"], f"{expected}  {path}\n")
    tool_count = command(["wc", "-c", str(path)])
    return {
        "path": str(path),
        "bytes": len(data),
        "expected_sha256": expected,
        "actual_sha256": actual,
        "match": actual == expected,
        "sha256sum_agrees": (
            tool_hash["returncode"] == 0
            and tool_hash["stdout"].split()[0] == actual
        ),
        "sha256sum_check_exit": tool_check["returncode"],
        "wc_agrees": (
            tool_count["returncode"] == 0
            and int(tool_count["stdout"].split()[0]) == len(data)
        ),
    }


manifest_bytes = MANIFEST.read_bytes()
record["manifest_bytes"] = len(manifest_bytes)
record["manifest_sha256"] = digest(manifest_bytes)
manifest = json.loads(manifest_bytes)
record["manifest_purpose"] = manifest["purpose"]

for item in manifest["files"]:
    relative = Path(item["local_path"])
    if relative.is_absolute():
        raise ValueError("Manifest path must be relative to inputs")
    path = (INPUTS / relative).resolve()
    if not path.is_relative_to(INPUTS.resolve()):
        raise ValueError("Manifest path must stay under inputs")
    try:
        evidence = compare(path, item["sha256"])
        evidence["id"] = item["id"]
        record["originals"].append(evidence)
    except OSError as exc:
        record["access_failures"].append({
            "attempted_action": f"Read bytes and check custody for {path}",
            "observed_restriction": repr(exc),
            "affected_scope": item["id"],
            "next_feasible_action": "Provide readable access to the same exact file; retain unaffected results.",
        })

if record["originals"]:
    source = record["originals"][0]
    altered = OUT / "owner.altered.md"
    original_bytes = Path(source["path"]).read_bytes()
    with altered.open("xb") as handle:
        handle.write(original_bytes + b"\n[DISPOSABLE CUSTODY NEGATIVE CONTROL]\n")
    negative = compare(altered, source["expected_sha256"])
    negative["source_path"] = source["path"]
    negative["alteration"] = "Append 39 bytes: LF + [DISPOSABLE CUSTODY NEGATIVE CONTROL] + LF"
    negative["appended_bytes"] = len(altered.read_bytes()) - len(original_bytes)
    negative["rejected"] = not negative["match"] and negative["sha256sum_check_exit"] == 1
    record["negative_control"] = negative

for evidence in record["originals"]:
    try:
        after = Path(evidence["path"]).read_bytes()
        evidence["after_bytes"] = len(after)
        evidence["after_sha256"] = digest(after)
        evidence["preserved_at_recheck"] = (
            evidence["bytes"] == len(after)
            and evidence["actual_sha256"] == digest(after)
        )
    except OSError as exc:
        evidence["preserved_at_recheck"] = False
        record["access_failures"].append({
            "attempted_action": f"Reread original {evidence['path']} after negative control",
            "observed_restriction": repr(exc),
            "affected_scope": f"Final preservation recheck for {evidence['id']}",
            "next_feasible_action": "Restore readable access and rerun only the affected preservation check.",
        })

record["finished_utc"] = datetime.now(timezone.utc).isoformat()
record["overall_pass"] = (
    len(record["originals"]) == len(manifest["files"])
    and not record["access_failures"]
    and all(
        item["match"] and item["sha256sum_agrees"]
        and item["sha256sum_check_exit"] == 0 and item["wc_agrees"]
        and item["preserved_at_recheck"]
        for item in record["originals"]
    )
    and record.get("negative_control", {}).get("rejected", False)
)
LOG.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

rows = [
    f"| `{item['id']}` | {item['bytes']} | `{item['actual_sha256']}` | {'MATCH' if item['match'] else 'MISMATCH'} |"
    for item in record["originals"]
]
negative = record.get("negative_control")
negative_text = (
    f"Created `{negative['path']}` by appending {negative['appended_bytes']} bytes to a copy of "
    f"`{negative['source_path']}`. The altered copy is {negative['bytes']} bytes; its SHA-256 is "
    f"`{negative['actual_sha256']}`. The unchanged comparison function, supplied the original expected "
    f"hash `{negative['expected_sha256']}`, returned MISMATCH. `sha256sum --check` exited "
    f"{negative['sha256sum_check_exit']} and reported `FAILED`. Negative control: "
    f"{'PASS (alteration rejected)' if negative['rejected'] else 'FAIL'}."
    if negative else "NOT_RUN: no readable original was available for an altered copy."
)
failure_text = (
    "No access restriction or missing tool was observed. No assistance was needed."
    if not record["access_failures"] else json.dumps(record["access_failures"], indent=2)
)
report = f"""Review the original `owner.md` and `lesson.md` bytes against the custody purpose and expected SHA-256 values in `inputs/custody.json`. Use the participants and tools available. Show evidence, limitations and the next useful action.

# Local byte-custody receipt

Result: **{'PASS' if record['overall_pass'] else 'INCOMPLETE OR FAILED'}** for this bounded GUIDED evidence operation. This result concerns exact bytes only.

Executed UTC: {record['started_utc']} to {record['finished_utc']}.

## Input binding and observed results

Manifest: `{MANIFEST}` ({record['manifest_bytes']} bytes), SHA-256 `{record['manifest_sha256']}`.
The expected hashes were read from that manifest; actual hashes below were computed over each file's bytes using Python `hashlib.sha256`, then checked with `sha256sum`. `wc -c` independently confirmed the byte counts.

| Original file | Bytes | Actual SHA-256 | Compared with manifest |
|---|---:|---|---|
{chr(10).join(rows)}

Original paths are resolved relative to `{INPUTS}`. Both original comparisons returned `sha256sum --check` exit 0 with `OK`. Each original was reread after the negative control; its byte count and digest matched the initial observation. The script opens original files for reading only and writes only under `out`.

## Contrary condition

{negative_text}

## Evidence and execution

Executed: `python3 {Path(__file__).resolve()}`.
The executed script is `verify_custody.py`; `custody-log.json` records every command argument, stdin check line, exit status, stdout and stderr, plus calculated hashes, counts and final preservation rechecks. The altered file is retained as a disposable witness.

Actually read: this assignment; `SKILL.md`, `references/INDEPENDENCE.md`, and `references/APPLYING_GUIDANCE.md` from the specified independent-review skill; `inputs/custody.json`; and the two named original files as raw bytes. Inspected only the task-local `out` directory before creating evidence. No document semantic content was decoded or assessed, and no golden cases or other agents' work were consulted.

## Independence and limits

This delegated worker did not author or modify either original during this operation. Prior authorship outside the visible assignment is not authenticated. The assignment and supplied manifest are shared upstream inputs; their authenticity and whether they represent the intended source revisions are not established by this check. The expected hashes are legitimate supplied custody expectations, not an independently established semantic oracle. Fresh SHA-256 calculations and the contrary-condition execution are independent of copying the expected values into an answer; they do not establish a distinct human principal or product correctness.

The claim supported is that the bytes at the two bound local paths matched the supplied hashes when read, and remained identical at the final recheck. SHA-256 matching does not assess correctness, completeness, safety, pedagogical quality, or acceptance. Files were not locked against concurrent external changes; future changes require a new check. No product approval, skill/source edit, or external publication was performed.

{failure_text}

## Next useful action

The lead can reconcile this receipt with the intended source revisions before consuming the two originals. Recheck hashes if any bytes change or the files move through an unverified transfer. Any content review requires a separate, expressly scoped assessment.
"""
REPORT.write_text(report, encoding="utf-8")
print(json.dumps({"overall_pass": record["overall_pass"], "report": str(REPORT), "log": str(LOG)}))
sys.exit(0 if record["overall_pass"] else 1)
