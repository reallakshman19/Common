"""WP3 RED-first tests: frozen source, scoring, compatibility, no network."""
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import criteria_v36 as criteria
import selfcheck_score_v36 as selfcheck
import score_v36 as scoring
import decompose_v36 as decompose
import lifecycle_v36 as life

FROZEN = (ROOT / "tests/fixtures/V36-430-FROZEN.criteria.txt").read_text("utf-8")
REAL_V1 = (ROOT / "tests/fixtures/V36-409-REAL.selfcheck-v1.txt").read_text("utf-8")
LABEL = life.load_label(ROOT / "tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml")
PLAN = decompose.load_plan(ROOT / "plans/V36-341-PLAN-02.yaml", LABEL)
SHA = "f" * 40


def valid_check():
    lines = ["SELF-CHECK v2 · V36-430-WP3 · reallakshman19/Common#430",
             f"Basis: CRITERIA v1 · source #430 body · candidate reallakshman19/Common@{SHA}"]
    for prefix, limit in (("AC", 10), ("K", 4)):
        lines += [f"Criterion: {prefix}{n} → MET · proof: exact-head CI and diff" for n in range(1, limit + 1)]
    lines += ["Criterion: J1 → UNKNOWN · proof: Owner has not reviewed readability",
              "Score: 14/14 · claim: PARTIAL",
              "Proposed claim: PARTIAL · reason: Owner judgment pending"]
    return "\n".join(lines) + "\n"


BEFORE = {"run": 274, "passed": 274, "sha": "a" * 40}
AFTER = {"run": 297, "passed": 297, "sha": SHA}
DIFF = {"paths": ["src/engine.py", "tests/test_engine_v36.py"],
        "allowed_paths": ["src/engine.py", "tests/test_engine_v36.py"],
        "removed_tests": 0, "test_first": True}


class CriteriaFreezeTests(unittest.TestCase):
    def test_real_frozen_criteria_and_source_coverage(self):
        result = criteria.parse_criteria_v1(FROZEN)
        self.assertEqual(len(result["criteria"]), 15)
        self.assertEqual(result["source_coverage"], "15/15")
        self.assertEqual(result["types"], {"MUST": 10, "CONSTRAINT": 4, "JUDGMENT": 1})
        self.assertEqual(result["source"], "#430 body")

    def test_missing_source_words_refused(self):
        body = FROZEN.replace('"mode lives in the label"', "", 1)
        with self.assertRaises(ValueError):
            criteria.parse_criteria_v1(body)

    def test_missing_type_refused(self):
        with self.assertRaises(ValueError):
            criteria.parse_criteria_v1(FROZEN.replace("AC1 MUST", "AC1", 1))

    def test_missing_measure_refused(self):
        line = next(x for x in FROZEN.splitlines() if x.startswith("AC1 "))
        with self.assertRaises(ValueError):
            criteria.parse_criteria_v1(FROZEN.replace(line, line.split(" → ", 1)[0]))

    def test_duplicate_id_and_header_source_missing_refused(self):
        with self.assertRaises(ValueError):
            criteria.parse_criteria_v1(FROZEN.replace("AC2 MUST", "AC1 MUST"))
        with self.assertRaises(ValueError):
            criteria.parse_criteria_v1(FROZEN.replace("source: #430 body", "source: "))


class SelfCheckV2Tests(unittest.TestCase):
    def setUp(self):
        self.criteria = criteria.parse_criteria_v1(FROZEN)

    def test_valid_v2_has_15_criteria_and_score(self):
        result = selfcheck.parse_self_check_v2(valid_check(), self.criteria)
        self.assertEqual(result["version"], 2)
        self.assertEqual(len(result["criteria"]), 15)
        self.assertEqual(result["claimed_score"], (14, 14))
        self.assertEqual(result["claim"], "PARTIAL")

    def test_missing_criterion_fails(self):
        with self.assertRaises(ValueError):
            selfcheck.parse_self_check_v2(valid_check().replace(
                "Criterion: AC2 → MET · proof: exact-head CI and diff\n", ""), self.criteria)

    def test_extra_criterion_fails(self):
        with self.assertRaises(ValueError):
            selfcheck.parse_self_check_v2(valid_check().replace(
                "Score: 14/14", "Criterion: AC11 → MET · proof: invented\nScore: 14/14"), self.criteria)

    def test_malformed_score_fails(self):
        with self.assertRaises(ValueError):
            selfcheck.parse_self_check_v2(valid_check().replace("Score: 14/14", "Score: all"), self.criteria)

    def test_real_409_legacy_companion_still_parses(self):
        result = selfcheck.parse_compatible(
            REAL_V1, task_id="V36-ECO-01",
            issue_ref="reallakshman19/Common#409", owner_login="reallakshman19")
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["issue"], "reallakshman19/Common#409")
        self.assertNotEqual(result["claim"], "UNKNOWN")

    def test_v2_cannot_include_canonical_evidence_marker(self):
        with self.assertRaises(ValueError):
            selfcheck.parse_self_check_v2(valid_check() + "TASK_EVIDENCE v3.6\n", self.criteria)


class RecomputeTests(unittest.TestCase):
    def setUp(self):
        self.criteria = criteria.parse_criteria_v1(FROZEN)
        self.report = selfcheck.parse_self_check_v2(valid_check(), self.criteria)

    def test_positive_exact_score_and_partial_claim(self):
        result = scoring.recompute(self.criteria, self.report, BEFORE, AFTER, DIFF)
        self.assertTrue(result["qualified"])
        self.assertEqual(result["score"], (14, 14))
        self.assertEqual(result["claim_class"], "PARTIAL")
        self.assertFalse(result["owner_accepted"])

    def test_altered_claimed_score_not_qualified(self):
        changed = selfcheck.parse_self_check_v2(valid_check().replace(
            "Score: 14/14", "Score: 15/14"), self.criteria)
        self.assertFalse(scoring.recompute(self.criteria, changed, BEFORE, AFTER, DIFF)["qualified"])

    def test_false_done_not_qualified(self):
        changed = selfcheck.parse_self_check_v2(valid_check().replace(
            "claim: PARTIAL", "claim: DONE").replace(
            "Proposed claim: PARTIAL", "Proposed claim: DONE"), self.criteria)
        self.assertFalse(scoring.recompute(self.criteria, changed, BEFORE, AFTER, DIFF)["qualified"])

    def test_test_failure_and_undeclared_diff_block_claim(self):
        self.assertFalse(scoring.recompute(self.criteria, self.report, BEFORE,
                         {**AFTER, "passed": 296}, DIFF)["qualified"])
        self.assertFalse(scoring.recompute(self.criteria, self.report, BEFORE, AFTER,
                         {**DIFF, "paths": ["other/secret.txt"]})["qualified"])


class PlanCriteriaTests(unittest.TestCase):
    def test_legacy_acceptance_sentence_unchanged(self):
        self.assertEqual(decompose.validate_plan(PLAN, LABEL)["tasks"][0]["acceptance"],
                         PLAN["tasks"][0]["acceptance"])

    def test_optional_criteria_list_accepted(self):
        task = {**PLAN["tasks"][0], "criteria": ["first source-backed rule", "second rule"]}
        self.assertEqual(decompose.validate_plan({**PLAN, "tasks": [task]}, LABEL)["tasks"][0]["criteria"],
                         task["criteria"])

    def test_optional_criteria_rejects_empty_and_duplicates(self):
        for bad in ([], [""], ["same", "same"], "single string"):
            task = {**PLAN["tasks"][0], "criteria": bad}
            with self.subTest(bad=bad), self.assertRaises(life.ContractError):
                decompose.validate_plan({**PLAN, "tasks": [task]}, LABEL)
