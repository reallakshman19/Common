"""Regression: Owner->Oracle is whole-project continuity; Oracle->Agent is WBS continuity.

Documentation-only checks. Passing them does NOT establish a new Oracle control
epoch, native Writer authorization, independent reviewer, or live task execution.
"""
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[2]
ORACLE = BASE / "nudge-designer/assets/oracle-onboard/ORACLE_ONBOARD_PROMPT.md"
AGENT = BASE / "nudge-designer/assets/agent-onboard/AGENT_ONBOARD_PROMPT.md"
MAP = BASE / "ENTRY_PROCESS_MAPS.md"

class OnBoardResponsibilityBoundary(unittest.TestCase):
    def test_owner_oracle_project_continuity(self):
        s = ORACLE.read_text(encoding="utf8")
        for v in ("SENDER: OWNER → ORACLE", "UNIT OF CONTINUITY: THE WHOLE PROJECT",
                  "all WBS", "ONE immediate project priority", "CANDIDATE_SUCCESSOR_READ_ONLY",
                  "NO_CONTROL_CUTOVER", "late returns", "Owner"):
            with self.subTest(needle=v):
                self.assertIn(v.lower(), s.lower())
        self.assertIn("Oracle → Agent WBS-level OnBoard", s)
        self.assertNotIn("four-file admission gate", s.lower())

    def test_oracle_agent_one_wbs_continuity(self):
        s = AGENT.read_text(encoding="utf8")
        for v in ("SENDER: PROJECT ORACLE → ASSIGNED AGENT", "ONE WBS TASK",
                  "parent", "upstream dependency", "downstream consumer",
                  "Stable task ID", "predecessor", "current candidate",
                  "AWAIT_ORACLE_RECONCILIATION", "NOT_RUN", "SELF_ASSESSED"):
            with self.subTest(needle=v):
                self.assertIn(v.lower(), s.lower())
        self.assertIn("No new approval gate", s)
        self.assertIn("READ_ONLY", s)
        self.assertNotIn("Recover THE PROJECT", s)
        self.assertNotIn("all WBS tasks", s.lower())

    def test_source_knowledge_not_four_mandatory_copies(self):
        a = AGENT.read_text(encoding="utf8").lower()
        o = ORACLE.read_text(encoding="utf8").lower()
        m = MAP.read_text(encoding="utf8").lower()
        self.assertIn("not mandatory", a)
        self.assertIn("not require a new file per wbs", o)
        self.assertIn("not four duplicate onboarding documents", m)
        self.assertIn("oracle cutover", m)
        self.assertIn("one wbs", m)
        self.assertIn("all wbs", m)

if __name__ == "__main__":
    unittest.main()
