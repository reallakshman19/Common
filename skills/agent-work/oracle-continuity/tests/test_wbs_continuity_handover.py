"""Regression against link-only 'handover done' while live WBS lineage is lost.

Source-contract documentation test, not a live successor/engineering acceptance
or a requirement to create extra WBS documents or approval stages.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
CONTINUITY = ROOT / "skills/agent-work/oracle-continuity/PROTOCOL.md"
ORACLE = ROOT / "skills/agent-work/nudge-designer/assets/oracle-onboard/ORACLE_ONBOARD_PROMPT.md"
AGENT = ROOT / "skills/agent-work/nudge-designer/assets/agent-onboard/AGENT_ONBOARD_PROMPT.md"
CIIFR = ROOT / "oracle-cycles/ciifr/continuity/payload/ORACLE_HANDOVER.md"


class WbsContinuityRegression(unittest.TestCase):
    def test_handover_requires_current_wbs_not_only_document_readback(self):
        text = CONTINUITY.read_text(encoding="utf-8")
        for requirement in (
            "Live WBS continuity is the handover",
            "WBS 3 / 3.1–3.4",
            "WBS 5.x",
            "receiving Oracle's first actual continuity action",
            "continues, depends on, replaces or coexists",
            "KNOWLEDGE_CHECKPOINT_PUBLISHED",
            "blanket project HOLD",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement.lower(), text.lower())

    def test_oracle_prompt_reconciles_old_and_new_work_before_dispatch(self):
        text = ORACLE.read_text(encoding="utf-8")
        for requirement in (
            "Progress Page Home/WBS",
            "PARENT WBS → EXISTING/current WBS → NEXT WBS",
            "continues, reuses, supersedes or runs in parallel",
            "READ_ONLY",
            "no extra checkpoint",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement.lower(), text.lower())

    def test_agent_receives_full_journey_plus_specific_next_wbs(self):
        text = AGENT.read_text(encoding="utf-8")
        for requirement in (
            "Overall project picture, plus what comes NEXT",
            "original user inputs → working current product/stage",
            "NEXT WBS",
            "cross-WBS interface",
            "not delegation to redesign all WBS tasks",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement.lower(), text.lower())

    def test_ciifr_real_failure_has_explicit_reconciliation_not_false_acceptance(self):
        text = CIIFR.read_text(encoding="utf-8")
        for requirement in (
            "WBS continuity addendum",
            "WBS 3 G0, 3.1 G1, 3.2 G2, 3.3 G3, 3.4 G4",
            "WBS 5.x",
            "5.1 MAP-P1",
            "existing #166/#179",
            "proof that 5.1 supersedes 3.1",
            "no engineering or acceptance PASS",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement.lower(), text.lower())


if __name__ == "__main__":
    unittest.main()
