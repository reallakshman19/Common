"""Issue #16 R1: reviewer-side Stage1 original-byte packaging contract tests.

This test module is NOT a native Relay transaction controller and cannot prove
fresh Runner identity, read isolation, provenance, or independent freeze. It
checks only a bounded textual seam between the V3.5 Runner output contract and
the native stage name. Actual provenance requires external attestation.
"""
from __future__ import annotations

import re
import unittest


STAGE1_BASELINE = "STAGE1_BASELINE"
STAGE1_PLAN = "STAGE1_PLAN"


def validate_buddy_stage1_output(stage: str, original_bytes: bytes) -> list[str]:
    """Reviewer-only fail-closed static check of ORIGINAL B-authored file bytes."""
    if stage not in {STAGE1_BASELINE, STAGE1_PLAN}:
        return ["UNSUPPORTED_STAGE"]
    if not isinstance(original_bytes, bytes):
        return ["ORIGINAL_BYTES_REQUIRED"]
    try:
        text = original_bytes.decode("utf-8", "strict")
    except UnicodeDecodeError:
        return ["ORIGINAL_UTF8_REQUIRED"]
    if "\x00" in text:
        return ["NUL_FORBIDDEN"]
    if not text.startswith(f"# {stage}\n"):
        return ["STAGE1_EXACT_HEADING_REQUIRED"]
    # Check all subsequent Markdown H1 stage delimiters, including CRLF,
    # trailing spaces, up to three leading spaces, optional closing hashes
    # and headers at EOF. Four-space indented code is not an H1.
    # Never reconstruct a second B-authored original from a combined document.
    if re.search(r"(?m)^[ ]{0,3}# STAGE1_(?:BASELINE|PLAN)(?:[ \\t]+#+)?[ \\t]*\\r?$", text.split("\\n", 1)[1]):
        return ["COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES"]
    if not text.split("\n", 1)[1].strip():
        return ["EMPTY_STAGE1_SUBSTANCE"]
    return []


class Stage1OriginalFileContractTests(unittest.TestCase):
    def test_source_grounded_baseline_original_file_accepted(self):
        raw = ("# STAGE1_BASELINE\n\nObserved producer A -> consumer B at historical SHA.\n".encode())
        self.assertEqual(validate_buddy_stage1_output(STAGE1_BASELINE, raw), [])

    def test_source_grounded_plan_original_file_accepted(self):
        raw = b"# STAGE1_PLAN\n\nProvisional response to the original Owner problem.\n"
        self.assertEqual(validate_buddy_stage1_output(STAGE1_PLAN, raw), [])

    def test_evidence_based_no_change_is_a_valid_plan(self):
        raw = b"# STAGE1_PLAN\n\nNO_CHANGE: historical observed output already meets the requirement.\n"
        self.assertEqual(validate_buddy_stage1_output(STAGE1_PLAN, raw), [])

    def test_generic_markdown_heading_is_not_a_real_baseline_file(self):
        raw = b"# Source producer and consumer witness\n\nSource-derived analysis.\n"
        self.assertIn("STAGE1_EXACT_HEADING_REQUIRED", validate_buddy_stage1_output(STAGE1_BASELINE, raw))

    def test_generic_markdown_heading_is_not_a_real_plan_file(self):
        raw = b"# Two alternate HOWs and falsifiers\n\nSome guesses.\n"
        self.assertIn("STAGE1_EXACT_HEADING_REQUIRED", validate_buddy_stage1_output(STAGE1_PLAN, raw))

    def test_baseline_cannot_be_relabelled_as_plan(self):
        raw = b"# STAGE1_BASELINE\n\nObserved fact.\n"
        self.assertIn("STAGE1_EXACT_HEADING_REQUIRED", validate_buddy_stage1_output(STAGE1_PLAN, raw))

    def test_combined_document_cannot_be_split_and_relabelled(self):
        raw = b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN\n\nPlan.\n"
        self.assertIn("COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES", validate_buddy_stage1_output(STAGE1_BASELINE, raw))

    def test_embedded_plan_header_with_crlf_is_rejected(self):
        raw = b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN\r\nProvisional plan.\n"
        self.assertIn("COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES", validate_buddy_stage1_output(STAGE1_BASELINE, raw))

    def test_embedded_plan_header_with_trailing_space_is_rejected(self):
        raw = b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN  \nProvisional plan.\n"
        self.assertIn("COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES", validate_buddy_stage1_output(STAGE1_BASELINE, raw))

    def test_embedded_plan_header_at_eof_is_rejected(self):
        raw = b"# STAGE1_BASELINE\n\nFacts.\n# STAGE1_PLAN"
        self.assertIn("COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES", validate_buddy_stage1_output(STAGE1_BASELINE, raw))

    def test_prose_mention_of_stage_label_is_allowed(self):
        raw = b"# STAGE1_BASELINE\n\nThe STAGE1_PLAN label belongs to a later independent document.\n"
        self.assertEqual(validate_buddy_stage1_output(STAGE1_BASELINE, raw), [])

    def test_indented_second_stage_h1_is_rejected(self):
        # Markdown permits 0-3 spaces before an ATX H1.
        for indentation in (b" ", b"  ", b"   "):
            with self.subTest(indentation=indentation):
                raw = b"# STAGE1_BASELINE\\n\\nFacts.\\n" + indentation + b"# STAGE1_PLAN\\nPlan.\\n"
                self.assertIn(
                    "COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES",
                    validate_buddy_stage1_output(STAGE1_BASELINE, raw),
                )

    def test_closing_hashes_on_second_stage_h1_are_rejected(self):
        # Markdown closing hashes do not turn an H1 into prose.
        for closing in (b" ###", b"   ##  ", b" ##\\r"):
            with self.subTest(closing=closing):
                raw = b"# STAGE1_BASELINE\\n\\nFacts.\\n# STAGE1_PLAN" + closing + b"\\nPlan.\\n"
                self.assertIn(
                    "COMBINED_STAGE1_OUTPUT_NOT_ORIGINAL_FILES",
                    validate_buddy_stage1_output(STAGE1_BASELINE, raw),
                )

    def test_four_space_indented_code_heading_is_not_rejected(self):
        raw = b"# STAGE1_BASELINE\\n\\nFacts.\\n    # STAGE1_PLAN\\nLiteral code example.\\n"
        self.assertEqual(validate_buddy_stage1_output(STAGE1_BASELINE, raw), [])

    def test_empty_file_is_rejected(self):
        self.assertIn("EMPTY_STAGE1_SUBSTANCE", validate_buddy_stage1_output(STAGE1_BASELINE, b"# STAGE1_BASELINE\n"))

    def test_non_utf8_is_rejected(self):
        self.assertIn("ORIGINAL_UTF8_REQUIRED", validate_buddy_stage1_output(STAGE1_PLAN, b"# STAGE1_PLAN\n\xff"))

    def test_unknown_stage_is_rejected(self):
        self.assertIn("UNSUPPORTED_STAGE", validate_buddy_stage1_output("STAGE2_RECONCILIATION", b"# STAGE2_RECONCILIATION\n"))

    def test_text_cannot_replace_original_byte_receipt(self):
        self.assertIn("ORIGINAL_BYTES_REQUIRED", validate_buddy_stage1_output(STAGE1_PLAN, "# STAGE1_PLAN\n"))


if __name__ == "__main__":
    unittest.main()
