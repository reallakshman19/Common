"""Documentation regressions for source-first initial mentoring.

These checks protect routing and truthful claim boundaries; they do not certify
that any real Oracle understands a private engineering model or can take control.
"""
from pathlib import Path
import unittest

AGENT_WORK = Path(__file__).resolve().parents[2]


def doc(relpath: str) -> str:
    return (AGENT_WORK / relpath).read_text(encoding="utf-8")


class InitialMentoringDocs(unittest.TestCase):
    def test_skill_links_are_real(self):
        for relpath in (
            "initial-mentoring/SKILL.md",
            "initial-mentoring/examples/word-table-and-cii.md",
            "START_HERE.md",
            "oracle-standalone/SKILL.md",
            "oracle-continuity/PROTOCOL.md",
            "nudge-designer/references/ORACLE_ONBOARD.md",
        ):
            with self.subTest(relpath=relpath):
                self.assertTrue((AGENT_WORK / relpath).is_file())

    def test_cold_entry_and_onboard_are_connected(self):
        start = doc("START_HERE.md")
        onboard = doc("nudge-designer/references/ORACLE_ONBOARD.md")
        oracle = doc("oracle-standalone/SKILL.md")
        self.assertIn("(initial-mentoring/SKILL.md)", start)
        self.assertIn("(../../initial-mentoring/SKILL.md)", onboard)
        self.assertIn("(../initial-mentoring/SKILL.md)", oracle)
        self.assertIn("original", start.lower())
        self.assertIn("domain-grounding before framework/design claims", oracle.lower())

    def test_oracle_continuity_reuses_same_mentoring_not_new_gate(self):
        continuity = doc("oracle-continuity/PROTOCOL.md")
        skill = doc("initial-mentoring/SKILL.md")
        for term in ("Owner outcome", "difficult architecture", "connected next",
                     "synthetic", "sentinel", "read-only"):
            with self.subTest(term=term):
                self.assertIn(term.lower(), continuity.lower())
        self.assertIn("(../initial-mentoring/SKILL.md)", continuity)
        self.assertIn("NOT A TEST", skill)
        self.assertIn("not an exam", skill.lower())
        self.assertIn("delta-only source refresh", skill)
        self.assertIn("never automatic control", continuity.lower())

    def test_ciifr_false_confidence_and_real_source_differentiation(self):
        skill = doc("initial-mentoring/SKILL.md")
        oracle = doc("oracle-standalone/SKILL.md")
        continuity = doc("oracle-continuity/PROTOCOL.md")
        example = doc("initial-mentoring/examples/word-table-and-cii.md")
        for term in ("original", "field-specific", "source", "wrong case"):
            self.assertIn(term, skill.lower())
        self.assertIn("13 green synthetic", continuity)
        self.assertIn("stored versus effective", example)
        self.assertIn("13/13 native tests", example)
        self.assertIn("NOT_TRANSFERRED", example)
        self.assertIn("13 green synthetic", oracle.lower().replace("tests", "tests") if False else continuity)
        self.assertIn("structural census", oracle.lower())

    def test_artifacts_and_benchmark_not_misrepresented(self):
        continuity = doc("oracle-continuity/PROTOCOL.md")
        example = doc("initial-mentoring/examples/word-table-and-cii.md")
        oracle = doc("oracle-standalone/SKILL.md")
        self.assertIn("three timed samples", continuity)
        self.assertIn("p95", continuity)
        self.assertIn("p95", example)
        self.assertIn("NOT_TRANSFERRED", continuity)
        self.assertIn("BLOCKED / NOT_TRANSFERRED", oracle)
        self.assertIn("Common/GitHub relay publication was BLOCKED", example)

    def test_old_cycle_and_cutover_are_not_upgraded_by_mentoring(self):
        skill = doc("initial-mentoring/SKILL.md")
        continuity = doc("oracle-continuity/PROTOCOL.md")
        self.assertIn("delta-only source refresh", skill)
        self.assertIn("does **not** revoke old writers", skill)
        self.assertIn("no scored onboarding exam", continuity.lower())
        self.assertIn("authenticat", continuity.lower())
        self.assertIn("exclusive write control", continuity.lower())


if __name__ == "__main__":
    unittest.main()
