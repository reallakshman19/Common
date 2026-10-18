"""Offline reconciliation of claimed v2 score against frozen criteria/test/diff.

This is an author's quantitative claim check, not source attestation or Owner
approval. Never grants final acceptance, delegated merge, or reviewer PASS.
"""
import argparse
import json
from pathlib import Path

from criteria_v36 import parse_criteria_v1
from selfcheck_score_v36 import parse_self_check_v2


def _green(result):
    return (isinstance(result, dict) and type(result.get("run")) is int
            and type(result.get("passed")) is int and result["run"] > 0
            and result["passed"] == result["run"]
            and isinstance(result.get("sha"), str)
            and len(result["sha"]) == 40
            and all(c in "0123456789abcdef" for c in result["sha"]))


def _diff_ok(diff):
    if not isinstance(diff, dict):
        return False
    paths, allowed = diff.get("paths"), diff.get("allowed_paths")
    return (isinstance(paths, list) and bool(paths)
            and isinstance(allowed, list)
            and all(isinstance(p, str) and p and not p.startswith("/")
                    and ".." not in Path(p).parts for p in paths + allowed)
            and len(set(paths)) == len(paths) and set(paths) <= set(allowed)
            and type(diff.get("removed_tests")) is int
            and diff["removed_tests"] == 0 and diff.get("test_first") is True)


def recompute(criteria, report, before, after, diff):
    clauses = criteria["criteria"]
    claimed = report["criteria"]
    expected = {key for key, value in clauses.items()
                if value["type"] != "JUDGMENT"}
    observed = {key for key, value in claimed.items()
                if value["state"] == "MET" and bool(value["proof"].strip())}
    score = (len(expected & observed), len(expected))
    tests_ok = (_green(before) and _green(after)
                and after["run"] >= before["run"]
                and report["candidate"].split("@")[-1] == after["sha"])
    diff_ok = _diff_ok(diff)
    gaps = sorted(expected - observed)
    judgments_open = [k for k in clauses
                      if clauses[k]["type"] == "JUDGMENT"]
    # Only an actual Owner can accept JUDGMENT; machine cannot issue DONE.
    claim_class = ("BLOCKED" if (gaps or not tests_ok or not diff_ok)
                   else "PARTIAL" if judgments_open else "READY_FOR_OWNER")
    qualified = (score == tuple(report["claimed_score"])
                 and report["claim"] == claim_class
                 and tests_ok and diff_ok
                 and all(k in claimed for k in clauses)
                 and all(k not in claimed for k in set(claimed) - set(clauses)))
    return {"qualified": bool(qualified), "score": score, "claim_class": claim_class,
            "owner_accepted": False, "tests_ok": bool(tests_ok), "diff_ok": bool(diff_ok),
            "unmet": gaps, "judgment": judgments_open}


def main(argv=None):
    cli = argparse.ArgumentParser(description="v3.6.1 scored self-check; no provider access")
    for name in ("criteria", "self-check", "before", "after", "diff"):
        cli.add_argument("--" + name, required=True)
    args = cli.parse_args(argv)
    try:
        frozen = parse_criteria_v1(Path(args.criteria).read_text("utf-8"))
        claimed = parse_self_check_v2(Path(args.self_check).read_text("utf-8"), frozen)
        before = json.loads(Path(args.before).read_text("utf-8"))
        after = json.loads(Path(args.after).read_text("utf-8"))
        diff = json.loads(Path(args.diff).read_text("utf-8"))
        result = recompute(frozen, claimed, before, after, diff)
        score = result["score"]
        print(f"SELF_CHECK_V2 | source={frozen['source_coverage']}"
              f" | score={score[0]}/{score[1]} | claim={result['claim_class']}"
              f" | qualified={'YES' if result['qualified'] else 'NO'}"
              f" | owner_accepted=NO")
        return 0 if result["qualified"] else 1
    except Exception as exc:
        print(f"SELF_CHECK_V2 | qualified=NO | error={type(exc).__name__}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
