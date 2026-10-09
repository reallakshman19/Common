"""Issue #6 R2: distinguish a filled engineering report from a V2 template.

This is a source/consumer *reviewer* oracle over exact PR19 report bytes staged
by CI after readback of their Git blob. It does not authenticate Agent A, Runner
B, information firewalls, Local handover, Owner decisions or any writer lease.
Never publish these reviewer checks into a clean Stage1 input packet.
"""
from __future__ import annotations

import os
import re
import unittest
from pathlib import Path

EXTERNAL_REPORT = os.environ.get("ISSUE6_EXTERNAL_REPORT_PATH", "")


def sections_of(report: str):
    headings = list(re.finditer(r"(?m)^## ([0-9]+)\. ([^\n]+)$", report))
    chunks = {}
    for index, heading in enumerate(headings):
        number = int(heading.group(1))
        end = headings[index + 1].start() if index + 1 < len(headings) else len(report)
        if number in chunks:
            return {}, ["DUPLICATE_SECTION"]
        chunks[number] = report[heading.start():end]
    ids = [int(m.group(1)) for m in headings]
    if ids != list(range(1, 13)):
        return chunks, ["SECTION_ORDER_OR_MISSING"]
    return chunks, []


def audit_filled_report(report: str) -> list[str]:
    """Audit source-oriented evidence presence, NOT its independent truth."""
    failures = []
    if not report.startswith("# HANDOVER_TECHNICAL_V2"):
        failures.append("WRONG_FORMAT")
    sections, structural = sections_of(report)
    failures += structural
    if structural:
        return failures

    preamble = report.split("## 1.", 1)[0].casefold()
    if "not a claim of independent runner b" not in preamble:
        failures.append("MISSING_PROVENANCE_LIMIT")
    if "stage 2 disclosure only after an independently attested stage 1 freeze" not in preamble:
        failures.append("MISSING_POST_FREEZE_BOUNDARY")

    required = {
        1: ("what the code actually does", "not", "draft"),
        2: ("owner", "negative", "source"),
        3: ("original agent a engineering task-start", "unknown", "reallakshman19/common"),
        4: ("producer", "consumer", "relay_tx.py::publish_buddy_markdown",
            "transactionlib.py::_validate_buddy_markdown_transaction"),
        5: ("test_issue16_stage1_output_contract.py", "consumer", "no"),
        6: ("synthetic", "original", "browser"),
        7: ("37991111370", "37989654186", "failed", "skipped"),
        8: ("native", "defect", "risk"),
        9: ("plan_handover", "handover_context", "not_granted", "stage2"),
        10: ("first safe", "head", "stop"),
        11: ("**q1", "**q2", "**q3", "**falsifier:**"),
        12: ("explicit limitations", "no independent frozen", "no exclusive writer"),
    }
    for number, terms in required.items():
        folded = sections[number].casefold()
        for term in terms:
            if term not in folded:
                failures.append(f"SECTION_{number}_MISSING_{term.upper()}")

    # Three questions, each with an explicit falsifier; no generic question-only
    # template can masquerade as a source-grounded, answered engineering report.
    part = sections[11]
    if len(re.findall(r"(?m)^\*\*Q[1-3] —", part)) != 3:
        failures.append("QUESTIONS_NOT_3")
    if part.count("**Falsifier:**") != 3:
        failures.append("QUESTIONS_WITHOUT_THREE_FALSIFIERS")

    # A filled technical report may be useful to a controller, but its own text
    # cannot issue a Stage2 release or a new source writer credential.
    if "no authentic external receipt" not in sections[9].casefold():
        failures.append("MISSING_EXTERNAL_FREEZE_HOLD")
    return failures


class Issue6FilledReportReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not EXTERNAL_REPORT:
            raise RuntimeError("ISSUE6_EXTERNAL_REPORT_PATH must point to exact pinned, read-back PR19 source")
        cls.source = Path(EXTERNAL_REPORT).read_text(encoding="utf-8")

    def test_pinned_filled_report_has_all_twelve_source_anchored_sections(self):
        self.assertEqual(audit_filled_report(self.source), [])

    def test_missing_source_level_mechanism_is_rejected(self):
        mutated = self.source.replace("transactionlib.py::_validate_buddy_markdown_transaction",
                                      "some generic file", 1)
        self.assertNotEqual(mutated, self.source)
        self.assertTrue(any("SECTION_4_MISSING" in e for e in audit_filled_report(mutated)))

    def test_missing_three_original_successor_questions_is_rejected(self):
        mutated = re.sub(r"(?m)^\*\*Q3 —.*$", "**Removed third question**", self.source, count=1)
        self.assertNotEqual(mutated, self.source)
        self.assertIn("QUESTIONS_NOT_3", audit_filled_report(mutated))

    def test_missing_red_native_run_cannot_claim_technical_completeness(self):
        sections, errors = sections_of(self.source)
        self.assertEqual(errors, [])
        tested_section = sections[7]
        self.assertIn("37991111370", tested_section)
        missing_native_negative = tested_section.replace("37991111370", "UNVERIFIED_RUN")
        mutated = self.source.replace(tested_section, missing_native_negative, 1)
        self.assertNotEqual(mutated, self.source)
        self.assertTrue(any("SECTION_7_MISSING" in e for e in audit_filled_report(mutated)))

    def test_missing_external_isolation_hold_is_rejected(self):
        mutated = self.source.replace("no authentic external receipt", "isolation independently approved", 1)
        self.assertNotEqual(mutated, self.source)
        self.assertIn("MISSING_EXTERNAL_FREEZE_HOLD", audit_filled_report(mutated))

    def test_report_format_alone_never_grants_stage2(self):
        # Readiness depends on actual external session/tool negative probes,
        # owner release and separate custody, none passed into this test runner.
        self.assertEqual(audit_filled_report(self.source), [])
        stage2_release_receipt = None
        self.assertIsNone(stage2_release_receipt)
        self.assertIn("Stage2:", self.source)
        self.assertIn("no same-B execution", self.source)


if __name__ == "__main__":
    unittest.main()
