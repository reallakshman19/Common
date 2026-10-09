"""Issue #16: source-witness checks on one FILLED engineering handover.

The canonical template linter protects the twelve-section FORMAT. This suite
checks a separate, existing source-grounded report's actual claims against
working-tree source and explicit evidence sections. It does not fetch GitHub,
attest CI execution, establish a B identity, authorize Stage2 disclosure, or
grant native Relay/Local custody. No new handover/progress authority is created.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "relay/CONTINUITY/REVIEWER_ONLY/ISSUE16_PR19_TECHNICAL_HANDOVER_V2.md"
TEMPLATE = ROOT / "relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md"
STAGE1_SOURCE = ROOT / "skills/engineering-pr-delivery-v3.5/tests/test_issue16_stage1_output_contract.py"

HEADINGS = re.compile(r"(?m)^## ([0-9]+)\. [^\n]+$")
COMMIT = re.compile(r"\b[0-9a-f]{40}\b")
RUN = re.compile(r"https://github\.com/reallakshman19/Common/actions/runs/[0-9]+")


def filled_report_findings(document: str, *, source: str) -> list[str]:
    """Check observable report evidence, not an agent's truth/authority claim."""
    errors: list[str] = []
    sections = list(HEADINGS.finditer(document))
    numbers = [int(m.group(1)) for m in sections]
    if numbers != list(range(1, 13)):
        return [f"REPORT_SECTIONS_MISSING_OR_REORDERED: {numbers}"]
    material = {
        number: document[m.start(): sections[i + 1].start() if i + 1 < len(sections) else len(document)]
        for i, (number, m) in enumerate(zip(numbers, sections))
    }
    preamble = document[: sections[0].start()]
    if not document.startswith("# HANDOVER_TECHNICAL_V2"):
        errors.append("REPORT_VERSION_MISMATCH")
    if "Issue #16 / PR #19" not in document.splitlines()[0]:
        errors.append("REAL_RESPONSIBILITY_IDENTITY_MISSING")
    if "**Report author/provenance:**" not in preamble:
        errors.append("REPORT_AUTHOR_PROVENANCE_MISSING")
    if "not a claim of independent Runner B" not in preamble:
        errors.append("NO_FALSE_RUNNER_IDENTITY_GUARD_MISSING")
    for number, section in material.items():
        if len(section.strip()) < 350:
            errors.append(f"SECTION_{number}_EMPTY_OR_PLACEHOLDER")
    if not all(repo in material[3] for repo in ("reallaksh19/Common", "reallakshman19/Common")):
        errors.append("REPOSITORY_MIGRATION_NOT_EXPLAINED")
    if not COMMIT.search(material[3]):
        errors.append("EXACT_SOURCE_IDENTITY_NOT_RECORDED")
    if "validate_buddy_stage1_output" not in material[4]:
        errors.append("PRODUCER_CONSUMER_SOURCE_SYMBOL_MISSING")
    if not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "validate_buddy_stage1_output"
        for node in ast.parse(source).body
    ):
        errors.append("REPORTED_SYMBOL_NOT_IN_ACTUAL_SOURCE")
    if "test_issue16_stage1_output_contract.py" not in material[5]:
        errors.append("IMPLEMENTATION_DELTA_PATH_MISSING")
    if not all(x in material[6] for x in ("negative", "NOT_RUN")):
        errors.append("POSITIVE_NEGATIVE_OUTPUT_LIMITS_MISSING")
    if not RUN.search(material[7]) or not COMMIT.search(material[7]):
        errors.append("EXECUTED_CI_REFERENCE_OR_TESTED_SHA_MISSING")
    if "FAILED" not in material[7]:
        errors.append("RED_NATIVE_RESULT_NOT_DISCLOSED")
    if not all(x in material[8] for x in ("BLOCKER", "HOLD")):
        errors.append("KNOWN_BLOCKER_OR_HOLD_MISSING")
    if "HANDOVER_CONTEXT" not in material[9]:
        errors.append("NATIVE_CUSTODY_BOUNDARY_MISSING")
    if not all(x in material[10].lower() for x in ("first safe source action", "stop")):
        errors.append("SUCCESSOR_ENTRY_AND_STOP_MISSING")
    if not all(re.search(rf"(?m)^\*\*Q{n} — ", material[11]) for n in (1, 2, 3)):
        errors.append("THREE_REAL_SUCCESSOR_QUESTIONS_MISSING")
    if "Explicit limitations" not in material[12]:
        errors.append("UNPROVEN_CLAIMS_NOT_DISCLOSED")
    return errors


class FilledHandoverEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.source = STAGE1_SOURCE.read_text(encoding="utf-8")

    def assert_rejected(self, report: str, code: str, marker: str):
        failures = filled_report_findings(report, source=code)
        self.assertIn(marker, failures, failures)

    def test_actual_filled_report_passes_bounded_source_witness_contract(self):
        self.assertEqual(filled_report_findings(self.report, source=self.source), [])

    def test_empty_template_cannot_impersonate_actual_engineering_handover(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(filled_report_findings(template, source=self.source))

    def test_removed_architecture_symbol_is_detected(self):
        altered = self.report.replace("validate_buddy_stage1_output", "unverified_algorithm")
        self.assert_rejected(altered, self.source, "PRODUCER_CONSUMER_SOURCE_SYMBOL_MISSING")

    def test_reported_symbol_must_exist_in_actual_source(self):
        altered = self.source.replace("def validate_buddy_stage1_output(", "def different_function(")
        self.assert_rejected(self.report, altered, "REPORTED_SYMBOL_NOT_IN_ACTUAL_SOURCE")

    def test_deleted_real_ci_references_are_rejected(self):
        altered = self.report.replace(
            "https://github.com/reallakshman19/Common/actions/runs/",
            "https://invalid.example/runs/",
        )
        self.assert_rejected(altered, self.source, "EXECUTED_CI_REFERENCE_OR_TESTED_SHA_MISSING")

    def test_greenwashing_native_failures_is_rejected(self):
        start = self.report.index("## 7. ")
        end = self.report.index("## 8. ", start)
        altered = self.report[:start] + self.report[start:end].replace("FAILED", "PASSED") + self.report[end:]
        self.assert_rejected(altered, self.source, "RED_NATIVE_RESULT_NOT_DISCLOSED")

    def test_missing_original_questions_are_rejected(self):
        altered = re.sub(r"(?ms)^\*\*Q3 — .*?(?=^## 12\.)", "", self.report)
        self.assert_rejected(altered, self.source, "THREE_REAL_SUCCESSOR_QUESTIONS_MISSING")

    def test_reduced_handover_to_pr_links_is_rejected(self):
        altered = re.sub(
            r"(?ms)^## 4\. .*?(?=^## 5\.)",
            "## 4. Architecture\n\nSee pull request.\n\n",
            self.report,
            count=1,
        )
        self.assert_rejected(altered, self.source, "SECTION_4_EMPTY_OR_PLACEHOLDER")


if __name__ == "__main__":
    unittest.main()
