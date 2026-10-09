"""Issue #16 R0/R2: preserve the already-merged V3.5 technical handover contract.

This checks template semantics, NOT author identity, Stage1 blindness, freeze,
native HANDOVER_CONTEXT execution, Owner acceptance or writer authority.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md"

# These are the 12 engineering INFORMATION DIMENSIONS delivered by merged PR #13.
# A future redesign may consolidate headings only after an approved, tested
# contract-version migration; silently substituting the competing ten-section
# template under the same V2 name is a regression.
REQUIRED = {
    1: ("problem", "working", "not yet implemented"),
    2: ("owner_verified", "unknown", "input"),
    3: ("task-start", "tested", "former repository"),
    4: ("consumer", "rollback", "input"),
    5: ("function", "before", "consumer"),
    6: ("positive", "negative/adversarial", "real_original", "browser_not_run"),
    7: ("tested", "skipped", "never infer pass"),
    8: ("failed strategies", "unknown", "blocker"),
    9: ("native", "writer", "unknown"),
    10: ("first", "head", "stop"),
    11: ("three questions", "source anchors", "falsifying"),
    12: ("provider", "not_run", "unknown"),
}


def check_handover_contract(document: str) -> list[str]:
    """Report missing delivery fields; don't infer a completed real handover."""
    errors = []
    if not document.startswith("# HANDOVER_TECHNICAL_V2"):
        errors.append("wrong canonical technical handover version")
    matches = list(re.finditer(r"(?m)^## ([0-9]+)\. ", document))
    ids = [int(m.group(1)) for m in matches]
    if ids != list(range(1, 13)):
        errors.append(f"missing/reordered 12 merged dimensions: {ids}")
    preamble = document[:matches[0].start()] if matches else document
    for required in (
        "Stage 2 after independently authenticated Stage 1 freeze only",
        "HANDOVER_CONTEXT",
        "one coherent report",
        "not a new",
    ):
        if required.casefold() not in preamble.casefold():
            errors.append(f"missing pre-release or native authority boundary: {required}")
    for i, match in enumerate(matches):
        number = int(match.group(1))
        if number not in REQUIRED:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(document)
        section = document[match.start():end].casefold()
        for key in REQUIRED[number]:
            if key.casefold() not in section:
                errors.append(f"section {number}: missing {key}")
    return errors


class Issue16HandoverContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TEMPLATE.read_text(encoding="utf-8")

    def assert_contract_rejects(self, text: str, marker: str):
        findings = check_handover_contract(text)
        self.assertTrue(findings, "corrupt handover was incorrectly accepted")
        self.assertTrue(
            any(marker.casefold() in finding.casefold() for finding in findings),
            f"expected {marker!r} in findings: {findings}",
        )

    def test_merged_main_v2_has_all_12_semantic_dimensions(self):
        self.assertEqual(check_handover_contract(self.source), [])

    def test_missing_successor_challenge_questions_rejected(self):
        modified = re.sub(
            r"(?ms)^## 11\. .*?(?=^## 12\.)", "", self.source, count=1
        )
        self.assert_contract_rejects(modified, "12 merged dimensions")

    def test_missing_real_negative_fixture_rejected(self):
        self.assert_contract_rejects(
            self.source.replace("negative/adversarial example", "example", 1),
            "negative/adversarial",
        )

    def test_silent_forged_green_ci_instruction_rejected(self):
        self.assert_contract_rejects(
            self.source.replace(
                "Never infer PASS from authored tests", "Always infer PASS from authored tests", 1
            ),
            "never infer pass",
        )

    def test_native_handover_authority_cannot_disappear(self):
        self.assert_contract_rejects(
            self.source.replace("HANDOVER_CONTEXT", "NEW_SHADOW_HANDOVER"),
            "HANDOVER_CONTEXT",
        )

    def test_unfrozen_stage1_cannot_receive_report(self):
        self.assert_contract_rejects(
            self.source.replace(
                "Stage 2 after independently authenticated Stage 1 freeze only",
                "Stage 1 before any independent freeze",
                1,
            ),
            "Stage 2 after independently authenticated Stage 1 freeze only",
        )

    def test_untested_current_source_not_mistaken_for_tested_head(self):
        self.assert_contract_rejects(
            self.source.replace(
                "Never imply a previous head tests the current head",
                "Assume past tests qualify newer heads",
                1,
            ),
            "tested",
        )


if __name__ == "__main__":
    unittest.main()
