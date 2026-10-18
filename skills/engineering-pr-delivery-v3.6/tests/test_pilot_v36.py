"""v3.6.2 RED-first owner-pilot regressions; no GitHub/network reads."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import criteria_v36 as criteria
import selfcheck_score_v36 as companion
import score_v36 as scoring

PILOT = ROOT / "tests/fixtures/v362_pilot"
CRITERIA = (PILOT / "criteria.txt").read_text(encoding="utf-8")
SELFCHECK = (PILOT / "selfcheck.txt").read_text(encoding="utf-8")
BEFORE = json.loads((PILOT / "before.json").read_text(encoding="utf-8"))
AFTER = json.loads((PILOT / "after.json").read_text(encoding="utf-8"))
DIFF = json.loads((PILOT / "diff.json").read_text(encoding="utf-8"))
POLICY = json.loads((PILOT / "policy.json").read_text(encoding="utf-8"))
SOURCE = "#1 issue body, reallakshman19/v361-pilot"


class SourceCommaTests(unittest.TestCase):
    def test_b1_comma_source_matches_in_two_parsers(self):
        parsed = criteria.parse_criteria_v1(CRITERIA)
        self.assertEqual(parsed["source"], SOURCE)
        self.assertEqual(parsed["source_coverage"], "10/10")
        self.assertEqual(companion.parse_self_check_v2(
            SELFCHECK, parsed)["source"], SOURCE)

    def test_b1_wrong_or_shortened_basis_refused(self):
        parsed = criteria.parse_criteria_v1(CRITERIA)
        for bad in ("#1 issue body", SOURCE + " extra"):
            with self.subTest(source=bad), self.assertRaises(ValueError):
                companion.parse_self_check_v2(
                    SELFCHECK.replace("source " + SOURCE + " ·",
                                      "source " + bad + " ·"), parsed)


class ZeroBaselineTests(unittest.TestCase):
    def setUp(self):
        self.parsed = criteria.parse_criteria_v1(
            CRITERIA.replace("source: " + SOURCE,
                             "source: #1 issue body"))
        self.report = companion.parse_self_check_v2(
            SELFCHECK.replace("source " + SOURCE,
                              "source #1 issue body"), self.parsed)

    def test_b2_declared_zero_suite_with_after_eight_qualifies(self):
        result = scoring.recompute(self.parsed, self.report,
                                   BEFORE, AFTER, DIFF)
        self.assertTrue(result["qualified"], result)
        self.assertEqual(result["score"], (9, 9))
        self.assertEqual(result["claim_class"], "PARTIAL")

    def test_b2_undeclared_zero_baseline_refused(self):
        before = {k: v for k, v in BEFORE.items()
                  if k != "zero_test_baseline"}
        result = scoring.recompute(self.parsed, self.report,
                                   before, AFTER, DIFF)
        self.assertFalse(result["qualified"], result)

    def test_b2_zero_after_run_refused(self):
        after = {**AFTER, "run": 0, "passed": 0}
        self.assertFalse(scoring.recompute(
            self.parsed, self.report, BEFORE, after, DIFF)["qualified"])

    def test_b2_false_declaration_and_inconsistent_counts_refused(self):
        for bad in ({**BEFORE, "zero_test_baseline": False},
                    {**BEFORE, "passed": 1},
                    {**BEFORE, "zero_test_baseline": "true"}):
            with self.subTest(bad=bad):
                self.assertFalse(scoring.recompute(
                    self.parsed, self.report, bad, AFTER, DIFF)["qualified"])


class RealPilotReplayTests(unittest.TestCase):
    def test_ac4_exact_pilot_source_and_score_qualify(self):
        self.assertEqual(BEFORE["sha"],
                         "0bd3d9312196da49422efe4da54ca34e6c8a354b")
        self.assertEqual(AFTER["sha"],
                         "cfc121be0c7c25cf298f1f0906080068ecf19b6e")
        self.assertEqual((BEFORE["run"], AFTER["run"]), (0, 8))
        self.assertEqual(DIFF["paths"],
                         ["tests/test_wordcount.py", "wordcount.py"])
        self.assertEqual(DIFF["allowed_paths"], POLICY["paths"])
        parsed = criteria.parse_criteria_v1(CRITERIA)
        check = companion.parse_self_check_v2(SELFCHECK, parsed)
        result = scoring.recompute(parsed, check, BEFORE, AFTER, DIFF)
        self.assertTrue(result["qualified"], result)
        self.assertEqual((result["score"], result["claim_class"]),
                         ((9, 9), "PARTIAL"))
        self.assertFalse(result["owner_accepted"])

    def test_ac4_actual_scoring_cli_returns_qualified_yes(self):
        command = [sys.executable, str(ROOT / "scripts/score_v36.py"),
                   "--criteria", str(PILOT / "criteria.txt"),
                   "--self-check", str(PILOT / "selfcheck.txt"),
                   "--before", str(PILOT / "before.json"),
                   "--after", str(PILOT / "after.json"),
                   "--diff", str(PILOT / "diff.json")]
        completed = subprocess.run(command, cwd=ROOT, text=True,
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("qualified=YES", completed.stdout)
        self.assertIn("owner_accepted=NO", completed.stdout)


class QuickstartReadabilityTests(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "QUICKSTART_STANDALONE.md").read_text("utf-8")

    def test_r1_windows_py_fallback(self):
        self.assertIn("use `py` on Windows", self.page)

    def test_r2_label_rejects_angle_bracket_placeholders(self):
        self.assertIn("FILE", self.page)
        self.assertIn("<file>", self.page)
        self.assertIn("reject", self.page.lower())

    def test_r3_exact_frozen_header_and_sample_row(self):
        self.assertIn(
            "CRITERIA v1 · <WORK> · FROZEN <date> by Owner · source: #N <text>",
            self.page)
        self.assertIn("AC1 MUST", self.page)

    def test_r4_exact_selfcheck_header_and_basis(self):
        self.assertIn("SELF-CHECK v2 · <TASK> · owner/repo#N", self.page)
        self.assertIn("Basis: CRITERIA v1 · source", self.page)
        self.assertIn("exactly", self.page.lower())

    def test_r5_baseline_before_not_red(self):
        self.assertIn("baseline suite before the change", self.page)
        self.assertIn("not the RED commit", self.page)
        self.assertIn('"run": 0', self.page)
        self.assertIn('"zero_test_baseline": true', self.page)

    def test_r6_backslashes_render_single(self):
        self.assertIn("C:\\pilot\\my-repo", self.page)
        self.assertNotIn("C:\\\\pilot\\\\my-repo", self.page)


if __name__ == "__main__":
    unittest.main()
