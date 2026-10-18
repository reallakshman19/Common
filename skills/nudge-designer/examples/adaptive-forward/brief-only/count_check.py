import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
directory = Path(__file__).resolve().parent
payload_path = directory / "payload.json"
raw = payload_path.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
records = json.loads(raw.decode("utf-8"))["records"]

rows = []
matches = 0
for record in records:
    text = record["text"]
    actual = len(text.split())
    claimed = record["claimed_tokens"]
    verdict = "MATCH" if actual == claimed else "MISMATCH"
    matches += actual == claimed
    literal = json.dumps(text, ensure_ascii=False).replace("|", "\\|")
    rows.append(f'| {record["id"]} | `{literal}` | {claimed} | {actual} | {verdict} |')

assert payload_path.read_bytes() == raw, "Input bytes changed during computation"
reviewed = len(rows)
report = f"""# Count-check report

The supplied claims do not all match: **{matches} match; {reviewed - matches} mismatch**.
Reviewed **{reviewed}/{len(records)} records**, recounted from the actual array, including the empty text. No records were skipped.

Input SHA-256: `{digest}`

Algorithm for every row: Python `len(text.split())`. Whitespace, including tabs, separates tokens; an empty string produces zero tokens. Text below uses JSON notation, so `\\t` denotes the original tab.

| Record | Original text (JSON literal) | Claimed | Computed | Verdict |
|---|---|---:|---:|---|
{chr(10).join(rows)}

L-01's empty string supports its claim of zero. L-02 splits into `["one", "two", "three"]`, so its claim is one below the computed count.

Supporting computation: `count_check.py` reads every array object, computes each count and verdict, and generates this report. Reproduce with `PYTHONDONTWRITEBYTECODE=1 python3 count_check.py` from this directory. The input bytes were verified unchanged after computation.

No computation was blocked. Wider acceptance, runtime model/effort, and formal qualification remain **UNKNOWN**. The next feasible action is to correct L-02's claimed count from 2 to 3 in an authorized copy, then rerun the check; the supplied input was not edited.
"""
(directory / "report.md").write_text(report, encoding="utf-8")
print(report)
