#!/usr/bin/env python3
"""Deterministic weighted MCDA. No network, writes, or optional dependencies."""
import argparse
import json
import math
from pathlib import Path

SCHEMA = "software-mcda.decision/v1"
EPS = 1e-9


def finite(value, label):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label}: expected finite number (not boolean)")
    return float(value)


def validate(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(f"Expected schema {SCHEMA}")
    cs, opts = data.get("criteria"), data.get("options")
    if not isinstance(cs, list) or len(cs) < 2:
        raise ValueError("At least two criteria required")
    if not isinstance(opts, list) or len(opts) < 2:
        raise ValueError("At least two options required")
    weights = {}
    for c in cs:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not c["id"].strip():
            raise ValueError("Invalid criterion ID")
        key = c["id"]
        if key in weights:
            raise ValueError("Duplicate criterion")
        v = finite(c.get("weight"), f"Weight {key}")
        if not 0 <= v <= 1:
            raise ValueError("Weight outside [0,1]")
        weights[key] = v
    if not math.isclose(sum(weights.values()), 1, rel_tol=0, abs_tol=EPS):
        raise ValueError("Criteria weights must total 1.0")
    names = set()
    for o in opts:
        if not isinstance(o, dict) or not isinstance(o.get("name"), str) or not o["name"].strip():
            raise ValueError("Option name missing")
        name = o["name"]
        if name in names:
            raise ValueError("Duplicate option")
        names.add(name)
        scores = o.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(weights):
            raise ValueError(f"Scores for {name} must match criteria")
        for key in weights:
            score = finite(scores[key], f"Score {name}/{key}")
            if not 1 <= score <= 5:
                raise ValueError("Rating outside [1,5]")
    constraints = data.get("constraints", [])
    if not isinstance(constraints, list):
        raise ValueError("Constraints must be a list")
    for constraint in constraints:
        if not isinstance(constraint, dict) or not isinstance(constraint.get("passes"), dict):
            raise ValueError("Invalid hard constraint")
        passes = constraint["passes"]
        if set(passes) != names or any(type(v) is not bool for v in passes.values()):
            raise ValueError("Constraint requires boolean result for each option")
    return weights


def rescale_weight(weights, target, new_weight):
    if target not in weights:
        raise ValueError("Unknown sensitivity criterion")
    new_weight = finite(new_weight, "Sensitivity weight")
    if not 0 <= new_weight <= 1:
        raise ValueError("Sensitivity weight outside [0,1]")
    other_total = sum(v for k, v in weights.items() if k != target)
    if other_total <= 0:
        raise ValueError("Cannot rescale zero other weights")
    return {k: new_weight if k == target else v * (1 - new_weight) / other_total
            for k, v in weights.items()}


def evaluate(data, weights=None):
    baseline = validate(data)
    w = baseline if weights is None else weights
    if set(w) != set(baseline) or any(not 0 <= finite(v, k) <= 1 for k, v in w.items()):
        raise ValueError("Invalid evaluation weights")
    if not math.isclose(sum(w.values()), 1, rel_tol=0, abs_tol=EPS):
        raise ValueError("Evaluation weights must total 1.0")
    ranked = []
    for option in data["options"]:
        contributions = {k: w[k] * option["scores"][k] for k in baseline}
        name = option["name"]
        eligible = all(c["passes"][name] for c in data.get("constraints", []))
        ranked.append({"name": name, "score": sum(contributions.values()),
                       "contributions": contributions, "eligible": eligible,
                       "evidence_level": option.get("evidence_level", "UNKNOWN")})
    return sorted(ranked, key=lambda r: (not r["eligible"], -r["score"], r["name"]))


def winner(ranked):
    available = [r for r in ranked if r["eligible"]]
    if not available:
        return None
    if len(available) > 1 and math.isclose(available[0]["score"], available[1]["score"],
                                          rel_tol=0, abs_tol=EPS):
        return None
    return available[0]["name"]


def break_even(data, target):
    weights = validate(data)
    if target not in weights:
        raise ValueError("Unknown break-even criterion")
    remaining = 1 - weights[target]
    if remaining <= 0:
        raise ValueError("No other weighted criteria")
    ranked = [r for r in evaluate(data) if r["eligible"]]
    if len(ranked) < 2:
        return {"criterion": target, "crossing_weight": None, "reason": "Fewer than two eligible"}
    a, b = [next(o for o in data["options"] if o["name"] == r["name"]) for r in ranked[:2]]
    target_diff = a["scores"][target] - b["scores"][target]
    other_diff = sum(weights[k] * (a["scores"][k] - b["scores"][k])
                     for k in weights if k != target) / remaining
    denom = other_diff - target_diff
    if math.isclose(denom, 0, rel_tol=0, abs_tol=EPS):
        return {"criterion": target, "crossing_weight": None, "reason": "No unique crossing"}
    crossing = other_diff / denom
    return {"criterion": target, "between": [a["name"], b["name"]],
            "crossing_weight": crossing if 0 <= crossing <= 1 else None,
            "reason": None if 0 <= crossing <= 1 else "Out of range"}


def report(data, sensitivity=None, crossover=None):
    ranked = evaluate(data)
    output = {"schema": "software-mcda.result/v1",
              "title": data.get("title", "Software MCDA"),
              "original": {"ranking": ranked, "winner": winner(ranked)},
              "assumptions": data.get("assumptions", [])}
    if sensitivity:
        if "=" not in sensitivity:
            raise ValueError("Use CRITERION=WEIGHT")
        key, value = sensitivity.split("=", 1)
        adjusted = rescale_weight(validate(data), key, float(value))
        ranking = evaluate(data, adjusted)
        output["sensitivity"] = {"weights": adjusted, "ranking": ranking,
                                 "winner": winner(ranking)}
    if crossover:
        output["break_even"] = break_even(data, crossover)
    return output


def markdown(result):
    lines = ["# " + result["title"], "", "| Option | Score / 5 | Eligible | Evidence |",
             "|---|---:|:---:|---|"]
    for row in result["original"]["ranking"]:
        lines.append(f"| {row['name']} | {row['score']:.2f} | {row['eligible']} | {row['evidence_level']} |")
    lines.extend(["", "Recommendation: " + str(result["original"]["winner"] or "NO_UNIQUE_WINNER")])
    if "sensitivity" in result:
        lines.extend(["", "## Sensitivity"])
        for row in result["sensitivity"]["ranking"]:
            lines.append(f"- {row['name']}: {row['score']:.2f}")
        lines.append("Recommendation: " + str(result["sensitivity"]["winner"] or "NO_UNIQUE_WINNER"))
    if "break_even" in result:
        lines.extend(["", "## Break-even", json.dumps(result["break_even"], sort_keys=True)])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--sensitivity")
    parser.add_argument("--break-even")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = report(data, args.sensitivity, args.break_even)
        print(json.dumps(result, indent=2, allow_nan=False) if args.format == "json"
              else markdown(result), end="\n" if args.format == "json" else "")
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, f"MCDA error: {exc}\n")


if __name__ == "__main__":
    main()
