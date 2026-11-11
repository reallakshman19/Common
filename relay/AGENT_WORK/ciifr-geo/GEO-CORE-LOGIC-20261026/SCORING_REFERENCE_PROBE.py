#!/usr/bin/env python3
"""Exact arithmetic reference examples; not the production Method C solver.

Tests translation-only trial fitting, whole-group exclusion, conditional regret,
and a separately proposed coherent-choice policy. Python standard library only.
"""

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def vec(values):
    return tuple(F(str(value)) for value in values)


def mean(vectors):
    return tuple(sum(vector[i] for vector in vectors) / len(vectors)
                 for i in range(3))


def error(required, shift):
    return sum(abs(shift[i] - required[i]) for i in range(3))


def evaluate(fixed, groups, choices):
    selected = [(None, value) for value in fixed]
    selected += [(group, groups[group][index])
                 for group, index in zip(groups, choices)]
    shift = mean([value for _, value in selected])
    scores = {group: sum(error(value, shift) for owner, value in selected
                         if owner != group) for group in groups}
    counts = {group: sum(owner != group for owner, _ in selected)
              for group in groups}
    return {"choices": choices, "shift": shift, "scores": scores,
            "witness_counts": counts,
            "total_error": sum(error(value, shift) for _, value in selected)}


def enumerate_cases(fixed, groups):
    products = itertools.product(*(range(len(options))
                                   for options in groups.values()))
    return [evaluate(fixed, groups, choices) for choices in products]


def regrets(case, cases, groups):
    result = []
    for position, group in enumerate(groups):
        others_fixed = [other for other in cases
                        if all(other["choices"][i] == case["choices"][i]
                               for i in range(len(groups)) if i != position)]
        best = min(other["scores"][group] for other in others_fixed)
        result.append(case["scores"][group] - best)
    return tuple(result)


def choose(cases, groups, minimax):
    def key(case):
        r = regrets(case, cases, groups)
        prefix = (max(r), sum(r)) if minimax else (sum(r),)
        return (*prefix, case["total_error"], case["choices"])
    return min(cases, key=key)


def serialise(value):
    if isinstance(value, F):
        return {"exact": str(value), "mm": float(value)}
    if isinstance(value, dict):
        return {str(key): serialise(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialise(item) for item in value]
    return value


def run():
    zero = vec((0, 0, 0))
    required_b = vec((669, 0, "0.1499791"))
    screenshot = enumerate_cases([zero, zero], {"G5210": [zero, required_b]})
    assert screenshot[0]["scores"]["G5210"] == 0
    assert screenshot[1]["shift"] == (F(223), F(0), F("0.1499791") / 3)
    assert screenshot[1]["scores"]["G5210"] == F(446) + 2 * F("0.1499791") / 3
    assert screenshot[1]["witness_counts"]["G5210"] == 2

    three_groups = {"G5210": [zero, required_b],
                    "G5220": [zero, vec((191, 0, 0))],
                    "G5229": [zero, vec((-191, 0, 0))]}
    eight = enumerate_cases([], three_groups)
    assert len(eight) == 8
    assert eight[0]["scores"] == dict.fromkeys(three_groups, F(0))

    cycle_groups = {"G1": [vec((-5, -8, -7)), vec((-3, 6, 5))],
                    "G2": [vec((4, -6, 4)), vec((6, 2, 1))]}
    cycle = enumerate_cases([vec((-8, -2, -3))], cycle_groups)
    expected = [((F(23), F(19))), ((F(70, 3), F(55, 3))),
                ((F(77, 3), F(67, 3))), ((F(22), F(71, 3)))]
    assert [tuple(c["scores"].values()) for c in cycle] == expected
    assert all(any(r > 0 for r in regrets(c, cycle, cycle_groups)) for c in cycle)
    assert choose(cycle, cycle_groups, True)["choices"] == (0, 0)

    fairness_groups = {
        "G1": [vec((-3, 19, 19)), vec((-9, -2, 0))],
        "G2": [vec((6, -2, 12)), vec((2, -10, -6))],
        "G3": [vec((-17, 0, 19)), vec((-10, -5, 18))],
    }
    fairness = enumerate_cases([vec((-9, -19, -14)), vec((4, -3, -14))],
                               fairness_groups)
    min_sum = choose(fairness, fairness_groups, False)
    min_max = choose(fairness, fairness_groups, True)
    assert min_sum["choices"] == (1, 1, 1)
    assert regrets(min_sum, fairness, fairness_groups) == (F(0), F(4, 5), F(0))
    assert min_sum["total_error"] == F(526, 5)
    assert min_max["choices"] == (1, 1, 0)
    assert regrets(min_max, fairness, fairness_groups) == (F(0), F(2, 5), F(2, 5))
    assert min_max["total_error"] == 116

    no_witness = enumerate_cases([], {"G": [zero, required_b]})
    assert all(c["scores"]["G"] == 0 and c["witness_counts"]["G"] == 0
               for c in no_witness)
    assert error(zero, vec((10, -10, 0))) == 20
    return {
        "scope": "Exact translation-only reference mathematics; no product/native rigid/browser acceptance",
        "status": "PASS_REFERENCE_ASSERTIONS",
        "screenshot_iterations": screenshot,
        "three_group_case_count": len(eight),
        "cycle_cases": [{**case, "regrets": regrets(case, cycle, cycle_groups)}
                        for case in cycle],
        "cycle_has_simultaneous_individual_minima": False,
        "fairness_min_sum": {**min_sum, "regrets": regrets(min_sum, fairness, fairness_groups)},
        "fairness_min_max_proposal": {**min_max, "regrets": regrets(min_max, fairness, fairness_groups)},
        "zero_witness_cases": no_witness,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(serialise(run()), indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Reference assertions passed; output: {args.output}")
    else:
        print(text, end="")
