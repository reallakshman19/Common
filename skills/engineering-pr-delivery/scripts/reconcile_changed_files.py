#!/usr/bin/env python3
from pathlib import Path
import re, sys

def ledger_paths(text):
    section = re.split(r"##\s+\d*\.*\s*Changed-File Ledger", text, flags=re.I)
    body = section[-1] if len(section) > 1 else text
    return set(re.findall(r"`([^`\n]+(?:\.[A-Za-z0-9_-]+))`", body))

def main():
    if len(sys.argv) != 3:
        print("Usage: reconcile_changed_files.py <workreport.md> <actual_paths.txt>", file=sys.stderr)
        return 2
    report = Path(sys.argv[1]).read_text(encoding="utf-8")
    actual = {x.strip() for x in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines() if x.strip()}
    ledger = ledger_paths(report)
    missing = sorted(actual - ledger)
    extra = sorted(ledger - actual)
    if missing:
        print("FAIL: actual files absent from ledger:")
        for p in missing: print("  ", p)
    if extra:
        print("WARN: ledger-like paths not in actual diff:")
        for p in extra: print("  ", p)
    if missing:
        return 1
    print(f"PASS: {len(actual)} actual changed paths represented in report")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
