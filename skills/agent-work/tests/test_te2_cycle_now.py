"""TE2-ROLE frozen Cycle now interface — fail-closed, source-document contract checks.

These guard the human-facing protocol consistency; browser/transaction tests live in
progress-page. They do not authenticate cross-chat delivery or engineering evidence.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class TE2RoleCycleNow(unittest.TestCase):
    def test_frozen_five_information_lines_unchanged(self):
        s = read("TASK_EVIDENCE_V2.md")
        for name in ("1. **TASK:**", "2. **PROGRESS:**", "3. **WORK & PROOF:**",
                     "4. **BLOCKERS & RELAY:**", "5. **NEXT → [ONE ACTOR]:**"):
            self.assertEqual(s.count(name), 1, name)
        self.assertIn("never a sixth information line", s)

    def test_acting_oracle_reports_its_own_task_not_two_agent_cards(self):
        for path in ("TASK_EVIDENCE_V2.md", "START_HERE.md",
                     "oracle-standalone/SKILL.md",
                     "progress-page/references/CYCLE_BOARD_PROTOCOLS.md"):
            s = read(path)
            self.assertRegex(s, r"(?i)(Oracle-owned|own coordination|Oracle coordination)")
            self.assertIn("Cycle now", s)
        self.assertIn("Board may show", read("TASK_EVIDENCE_V2.md"))
        self.assertIn("Owner explicitly asks", read("TASK_EVIDENCE_V2.md"))

    def test_separate_posted_delivery_ack_and_current_instruction(self):
        for path in ("TASK_EVIDENCE_V2.md", "oracle-chat-routing/STANDALONE.md"):
            s = read(path)
            for state in ("POSTED", "DELIVERED", "ACKNOWLEDGED", "EVIDENCE_RETURNED",
                          "ORACLE_RECONCILED", "AWAITING_RELAY"):
                self.assertIn(state, s, (path, state))
            self.assertIn("current", s.lower())

    def test_native_mode_not_blocked_by_inactive_formal_cycle(self):
        s = read("oracle-standalone/SKILL.md")
        self.assertIn("only the selected transport", s.lower())
        self.assertIn("formal", s.lower())
        self.assertIn("native", s.lower())
        self.assertIn("does **not** block", s)
        root = read("START_HERE.md")
        self.assertIn("only when the formal GitHub Oracle Cycle", root)

    def test_no_new_wbs_or_quiet_owner_relay_gap(self):
        s = read("TASK_EVIDENCE_V2.md")
        self.assertIn("Do not create an Oracle task or WBS", s)
        self.assertIn("minimum copy-ready Owner relay", s)
        chat = read("oracle-chat-routing/STANDALONE.md")
        self.assertIn("AWAITING_RELAY", chat)
        self.assertIn("No action requested from Owner", chat)
        self.assertIn("only if no Owner-dependent relay", chat)

    def test_legacy_ambiguous_default_is_gone(self):
        for path in ("START_HERE.md", "oracle-standalone/SKILL.md",
                     "progress-page/references/CYCLE_BOARD_PROTOCOLS.md",
                     "ROLE_LIFECYCLE.md", "ENTRY_PROCESS_MAPS.md"):
            s = read(path)
            self.assertNotIn("five-line card per relevant Agent/Oracle task", s, path)
            self.assertNotIn("five-information-line** card per current Agent/Oracle task", s, path)


if __name__ == "__main__":
    unittest.main()
