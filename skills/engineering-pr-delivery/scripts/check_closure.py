#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

def run(script, report):
    p = subprocess.run([sys.executable, str(Path(__file__).with_name(script)), report])
    return p.returncode

def main():
    if len(sys.argv) != 2:
        print("Usage: check_closure.py <workreport.md>", file=sys.stderr)
        return 2
    report = sys.argv[1]
    rc = 0
    rc |= run("validate_workreport.py", report)
    text = Path(report).read_text(encoding="utf-8")
    if "APPENDIX_A_STATUS: CURRENT" in text:
        rc |= run("validate_takeover_gate.py", report)
    required = ["HANDOVER_READINESS: READY", "REPORT_SYNC: CURRENT"]
    for token in required:
        if token not in text:
            print("FAIL: closure requires", token)
            rc = 1
    if rc == 0:
        print("PASS: structural closure/handover gate")
    return 1 if rc else 0

if __name__ == "__main__":
    raise SystemExit(main())
