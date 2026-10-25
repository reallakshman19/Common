"""Read-only documentation regression checks for the existing Oracle continuity CI.

These prove documented routing/links are coherent, NOT that live agents,
independent reviewers, private bytes or actual control cutovers were tested.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
BASE = Path("skills/agent-work")

DOCS = (
    "START_HERE.md",
    "ENTRY_PROCESS_MAPS.md",
    "ROLE_LIFECYCLE.md",
    "oracle-standalone/SKILL.md",
    "oracle-standalone/references/CHANGEOVER.md",
    "oracle-standalone/references/PROGRESS_ADAPTER.md",
    "oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md",
    "oracle-continuity/PROTOCOL.md",
    "progress-page/references/MODES.md",
)
GOLDEN = "bf02e54e1b453c3206ae366de7d65f41c94ab0d4"
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")


def doc(name):
    return (ROOT / BASE / name).read_text(encoding="utf-8")


class WorkflowDocsTests(unittest.TestCase):
    def test_all_local_link_destinations_exist(self):
        """Catch file/folder link typos without remote network or new gates."""
        for name in DOCS:
            source = ROOT / BASE / name
            for match in LINK.finditer(doc(name)):
                target = match.group(1).strip().strip("<>")
                # Ignore fully qualified links and same-file anchors. The
                # immutable golden GitHub links are checked separately.
                if target.startswith(("#", "https://", "http://", "mailto:", "skills://")):
                    continue
                path = unquote(urlsplit(target).path)
                if not path or path.startswith(("{", "<")):
                    continue
                resolved = (source.parent / path).resolve()
                with self.subTest(document=name, link=target):
                    self.assertTrue(resolved.is_relative_to(ROOT), "outside repository")
                    self.assertTrue(resolved.exists(), f"missing target: {resolved}")

    def test_cold_builder_receives_pre_resolved_assignment(self):
        start = doc("START_HERE.md")
        maps = doc("ENTRY_PROCESS_MAPS.md")
        self.assertIn("Minimum executable assignment", start)
        for term in ("recipient", "task issue", "candidate", "return destination"):
            self.assertIn(term, start)
        self.assertIn("Oracle/OTM (or direct Owner)", maps)
        self.assertIn("Issue → WBS", maps)
        self.assertIn("v3.6 selected for this task?", maps)
        self.assertIn("selected native task / delivery protocol", maps)

    def test_warm_cycle_is_delta_only_and_idempotent(self):
        start, maps = doc("START_HERE.md"), doc("ENTRY_PROCESS_MAPS.md")
        self.assertIn("delta-only continuation", start)
        self.assertIn("Refresh changed issue/evidence/candidate", maps)
        self.assertIn("AWAIT_ORACLE_RECONCILIATION", maps)
        self.assertIn("do not rerun engineering", maps)
        self.assertIn("NO ACTION / NOT ACTIVE or BLOCKED", maps)

    def test_agent_handover_is_a_decision_not_auto_reset(self):
        maps = doc("ENTRY_PROCESS_MAPS.md")
        change = doc("oracle-standalone/references/CHANGEOVER.md")
        self.assertIn("## D. Oracle-driven agent continuity", maps)
        self.assertIn("Successor continues SAME task", maps)
        self.assertIn("No uncontrolled overlapping writes?", maps)
        self.assertIn("same task id", maps.lower())
        self.assertIn("two consecutive", change.lower())
        self.assertIn("eligible", change)
        self.assertIn("not already-adopted universal rules", change)

    def test_oracle_succession_preserves_knowledge_and_workers(self):
        maps = doc("ENTRY_PROCESS_MAPS.md")
        protocol = doc("oracle-continuity/PROTOCOL.md")
        handover = doc("oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md")
        self.assertIn("## E. Oracle continuity", maps)
        self.assertIn("ADOPT existing builder and IR assignments", maps)
        self.assertIn("Safe enforced or isolated control?", maps)
        self.assertIn(GOLDEN, protocol)
        self.assertIn(GOLDEN, handover)
        self.assertIn("four knowledge classes", protocol)
        self.assertIn("A status-only A–G checklist", protocol)
        self.assertIn("four distinct new files are not mandated", protocol)
        for name in ("CONCEPT_NOTE.md", "ARCHITECTURE_COMPLEX_LOGIC.md",
                     "ARCHITECTURE_DECISIONS_AND_CHALLENGES.md", "ORACLE_HANDOVER.md"):
            self.assertIn(name, handover)

    def test_measured_triggers_are_pilot_not_cutover(self):
        change = doc("oracle-standalone/references/CHANGEOVER.md")
        self.assertIn("last three eligible dispatches", change)
        self.assertIn("two consecutive", change.lower())
        self.assertIn("after correction", change.lower())
        self.assertIn("BuddyRunner suggestion only", change)
        self.assertIn("not a compulsory", doc("oracle-continuity/PROTOCOL.md"))
        self.assertIn("one explicit owner", change.lower())
        self.assertIn("actual write isolation", change)

    def test_scoped_progress_merge_grant_not_cross_repo(self):
        modes = doc("progress-page/references/MODES.md")
        self.assertIn("reallakshman19/progress-page", modes)
        self.assertIn("without requesting a second Owner approval", modes)
        self.assertIn("approve Common/other repositories", modes)
        for name in ("START_HERE.md", "ROLE_LIFECYCLE.md",
                     "oracle-standalone/SKILL.md",
                     "oracle-standalone/references/PROGRESS_ADAPTER.md",
                     "oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md"):
            with self.subTest(document=name):
                self.assertNotRegex(doc(name), r"\bOwner merges\b|\bfor Owner merge\b")
        self.assertIn("Progress Page modes", doc("oracle-standalone/references/PROGRESS_ADAPTER.md"))

    def test_process_maps_have_closed_fences_and_both_routes(self):
        maps = doc("ENTRY_PROCESS_MAPS.md")
        fence = chr(96) * 3
        self.assertEqual(maps.count(fence + "mermaid"), 5)
        self.assertEqual(maps.count(fence) % 2, 0)
        self.assertIn("## D. Oracle-driven agent continuity", maps)
        self.assertIn("## E. Oracle continuity", maps)
        self.assertIn("CONTINUE current agent", maps)
        self.assertIn("CONTINUE: preserve concept", maps)


if __name__ == "__main__":
    unittest.main()
