"""Offline acceptance tests for issue #378."""
import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mcda", ROOT / "scripts" / "mcda.py")
mcda = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcda)
EXAMPLE = json.loads((ROOT / "assets" / "example-decision.json").read_text())


class MCDAAcceptance(unittest.TestCase):
    def test_baseline(self):
        ranked = mcda.evaluate(EXAMPLE)
        result = {r["name"]: r["score"] for r in ranked}
        self.assertAlmostEqual(result["Refactor Existing Code"], 3.25)
        self.assertAlmostEqual(result["Rewrite From Scratch"], 3.80)
        self.assertEqual(mcda.winner(ranked), "Rewrite From Scratch")
        for row in ranked:
            self.assertAlmostEqual(sum(row["contributions"].values()), row["score"])

    def test_sensitivity(self):
        weights = mcda.rescale_weight(mcda.validate(EXAMPLE), "cost", 0.5)
        results = {r["name"]: r["score"] for r in mcda.evaluate(EXAMPLE, weights)}
        self.assertAlmostEqual(results["Refactor Existing Code"], 3.5)
        self.assertAlmostEqual(results["Rewrite From Scratch"], 3.2)

    def test_break_even(self):
        self.assertAlmostEqual(mcda.break_even(EXAMPLE, "cost")["crossing_weight"], 7 / 17)

    def test_bad_weights(self):
        d = copy.deepcopy(EXAMPLE)
        d["criteria"][0]["weight"] = 0.5
        with self.assertRaises(ValueError):
            mcda.evaluate(d)

    def test_nonfinite_boolean_and_range(self):
        for v in (True, math.inf, math.nan, -math.inf, 0, 6):
            with self.subTest(v=v):
                d = copy.deepcopy(EXAMPLE)
                d["options"][0]["scores"]["cost"] = v
                with self.assertRaises(ValueError):
                    mcda.evaluate(d)

    def test_missing_score_not_filled(self):
        d = copy.deepcopy(EXAMPLE)
        del d["options"][0]["scores"]["risk"]
        with self.assertRaises(ValueError):
            mcda.evaluate(d)

    def test_hard_constraint(self):
        d = copy.deepcopy(EXAMPLE)
        d["constraints"] = [{"passes": {"Refactor Existing Code": True, "Rewrite From Scratch": False}}]
        self.assertEqual(mcda.winner(mcda.evaluate(d)), "Refactor Existing Code")

    def test_no_eligible_option(self):
        d = copy.deepcopy(EXAMPLE)
        d["constraints"] = [{"passes": {"Refactor Existing Code": False, "Rewrite From Scratch": False}}]
        self.assertIsNone(mcda.winner(mcda.evaluate(d)))

    def test_unknown_constraint_rejected(self):
        d = copy.deepcopy(EXAMPLE)
        d["constraints"] = [{"passes": {"Refactor Existing Code": True, "Rewrite From Scratch": None}}]
        with self.assertRaises(ValueError):
            mcda.evaluate(d)

    def test_tie(self):
        d = copy.deepcopy(EXAMPLE)
        d["options"][0]["scores"] = d["options"][1]["scores"].copy()
        self.assertIsNone(mcda.winner(mcda.evaluate(d)))

    def test_schema_enforced(self):
        d = copy.deepcopy(EXAMPLE)
        d["schema"] = "wrong"
        with self.assertRaises(ValueError):
            mcda.evaluate(d)


if __name__ == "__main__":
    unittest.main()
