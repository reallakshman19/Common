"""Regression oracles for the executable, synthetic five-HOLD walkthrough."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from benchmark_walkthrough import run_benchmark


class SyntheticBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.result = run_benchmark()

    def test_01_benchmark_is_reproducible_and_covers_all_ten_cases(self):
        self.assertEqual(self.result["schema"], "v32-325-synthetic-benchmark-v1")
        self.assertEqual(self.result["test_cases_total"], 10)
        self.assertEqual(self.result["test_cases_pass"], 10, self.result["cases"])
        self.assertTrue(self.result["expected_holds_observed"])
        self.assertEqual(len({r["case"] for r in self.result["cases"]}), 10)

    def test_02_each_real_production_gate_remains_hold(self):
        self.assertEqual(
            [gate["id"] for gate in self.result["production_gates"]],
            ["G1", "G2", "G3", "G4", "G5"],
        )
        self.assertTrue(all(gate["result"].startswith("HOLD_")
                            for gate in self.result["production_gates"]))
        self.assertFalse(self.result["ready_for_production"])
        self.assertEqual(self.result["owner_ac"], "0/8_NOT_ADJUDICATED")

    def test_03_original_source_custody_and_external_authority_not_faked(self):
        self.assertEqual(self.result["fixture_origin_repo"], "reallaksh19/Common")
        self.assertEqual(self.result["fixture_binding"], "example/Pipeline")
        self.assertEqual(self.result["real_original_lab"], "NOT_RUN")
        self.assertEqual(self.result["real_github_managed_write"], "NOT_RUN")
        self.assertEqual(self.result["independent_agent_B"], "NOT_RUN")
        self.assertEqual(self.result["writes"], 0)
        self.assertEqual(self.result["v32_live_writer"], "OFF")
        self.assertEqual(self.result["classification"],
                         "SYNTHETIC_REPLAY_NOT_OWNER_ACCEPTANCE")

    def test_04_existing_native_material_and_readback_boundaries_proven_in_output(self):
        cases = {item["case"]: item for item in self.result["cases"]}
        self.assertEqual(cases["B05_native_full_pr_ref_holds"]["observed"],
                         "NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY")
        self.assertEqual(cases["B08_simulated_full_readback_still_not_authority"]["observed"],
                         "OBSERVED_MATCH_NOT_AUTHORIZATION")
        self.assertEqual(cases["B09_merged_pr_does_not_launch_B"]["observed"],
                         "NO_AUTOMATIC_SUCCESSOR")
        self.assertTrue(all(row["result"] == "PASS" for row in cases.values()))

    def test_05_benchmark_script_has_no_direct_network_or_writer(self):
        src = Path(__file__).with_name("benchmark_walkthrough.py")
        tree = ast.parse(src.read_text(encoding="utf-8"))
        banned_imports = {"requests", "httpx", "urllib", "socket", "aiohttp",
                          "subprocess"}
        banned_calls = {"patch", "post", "put", "delete", "urlopen",
                        "request", "system", "popen", "check_output"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertFalse(any(a.name.split(".")[0] in banned_imports
                                     for a in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn((node.module or "").split(".")[0], banned_imports)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr.lower(), banned_calls)


if __name__ == "__main__":
    unittest.main()
