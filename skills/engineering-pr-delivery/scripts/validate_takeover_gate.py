#!/usr/bin/env python3
from pathlib import Path
import re, sys

WEAK = re.compile(r"^\s*(?:Question:\s*)?(?:What is|Define|Describe|Discuss|List|Explain)\b", re.I | re.M)

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_takeover_gate.py <workreport.md>", file=sys.stderr)
        return 2
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    appendix = re.split(r"#\s+APPENDIX A", text, flags=re.I)
    if len(appendix) < 2:
        print("FAIL: Appendix A missing")
        return 1
    a = appendix[-1].split("# HISTORICAL", 1)[0]
    qs = re.findall(r"^###\s+A\d+\b.*$", a, re.M)
    errors = []
    if len(qs) < 5:
        errors.append(f"expected at least 5 A# challenges, found {len(qs)}")
    signals = {
        "repository evidence": r"(Repository anchors|file/function|test/benchmark|diff)",
        "required evidence": r"Required evidence",
        "falsifier": r"Falsifier",
        "next commit": r"Next-commit",
    }
    for label, pat in signals.items():
        if not re.search(pat, a, re.I):
            errors.append(f"Appendix A missing {label} signal")
    weak = WEAK.findall(a)
    if weak:
        print("WARN: weak textbook-style verbs detected; verify they are repository-bound")
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("PASS: takeover gate structural screen")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
