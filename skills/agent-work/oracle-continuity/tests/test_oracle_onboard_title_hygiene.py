"""Static regression tests for gold-depth Oracle OnBoard and title hygiene.

No live Oracle authority, Chat ID authentication, title publication, DELP writes
or actual engineering/reviewer acceptance is exercised by these source checks.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
AGENT = ROOT / "skills" / "agent-work"
ORACLE = AGENT / "nudge-designer/assets/oracle-onboard"
AGENT_PACKET = AGENT / "nudge-designer/assets/agent-onboard"
HYG = AGENT / "nudge-designer/references/TITLE_AND_TRAFFIC_HYGIENE.md"
FOUR = ("CONCEPT_NOTE.md", "ARCHITECTURE_COMPLEX_LOGIC.md",
        "ARCHITECTURE_DECISIONS_AND_CHALLENGES.md", "ORACLE_HANDOVER.md")
LOCAL = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")


def read(path):
    return path.read_text(encoding="utf-8")


class OracleAndAgentOnboardHygiene(unittest.TestCase):
    def test_oracle_four_distinct_sources_and_prompt(self):
        for name in FOUR:
            with self.subTest(document=name):
                text = read(ORACLE / name)
                self.assertIn("TEMPLATE", text)
                self.assertIn("{{", text)
                self.assertIn("Owner", text)
                self.assertIn("source", text.lower())
                self.assertGreater(len(text), 1700)
        prompt = read(ORACLE / "ORACLE_ONBOARD_PROMPT.md")
        self.assertIn("UNIT OF CONTINUITY: THE WHOLE PROJECT", prompt)
        self.assertIn("SENDER: OWNER → ORACLE", prompt)
        self.assertIn("all WBS", prompt)
        self.assertIn("ONE immediate project priority", prompt)
        self.assertIn("READ_ONLY", prompt)
        self.assertIn("NOW", prompt)
        self.assertIn("chat", prompt.lower())
        self.assertIn("not", prompt.lower())

    def test_chat_id_is_locator_not_authentication(self):
        doc = read(HYG).lower()
        for word in ("chat-id8", "not authenticated", "principal", "unknown",
                     "independent", "replacing", "assignment"):
            self.assertIn(word, doc)
        self.assertIn("chat", read(ORACLE / "ORACLE_HANDOVER.md").lower())
        self.assertIn("chat", read(AGENT_PACKET / "AGENT_HANDOVER.md").lower())

    def test_title_owner_is_projector_when_v35_selected(self):
        doc = read(HYG)
        for word in ("DELP", "CHECKPOINT_FACTS_V1", "never manually authored",
                     "P/E/D", "projector", "do not"):
            self.assertIn(word.lower(), doc.lower())
        self.assertIn("PR title", doc)
        self.assertIn("issue title", doc)

    def test_traffic_light_claims_are_bounded(self):
        doc = read(HYG)
        for item in ("🟢", "🟡", "🔴", "🔵", "OWNER_ACTION",
                     "NEXT:", "BLOCKER", "source", "NOT"):
            self.assertIn(item.lower(), doc.lower())
        self.assertIn("one", doc.lower())
        self.assertIn("after", doc.lower())

    def test_local_links_and_no_private_child_paths(self):
        source_files = [ORACLE / name for name in (*FOUR, "README.md", "ORACLE_ONBOARD_PROMPT.md")]
        source_files += [AGENT_PACKET / "README.md", AGENT_PACKET / "AGENT_HANDOVER.md",
                         AGENT_PACKET / "AGENT_ONBOARD_PROMPT.md", HYG]
        for source in source_files:
            raw = read(source)
            self.assertNotIn("drive.google.com/drive/folders/", raw)
            for match in LOCAL.finditer(raw):
                loc = match.group(1).split("#", 1)[0]
                if not loc or "://" in loc or loc.startswith(("mailto:", "#")):
                    continue
                resolved = (source.parent / loc).resolve()
                with self.subTest(file=source.name, link=loc):
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.exists(), str(resolved))

    def test_native_entry_reuses_packet_not_a_new_gate(self):
        start = read(AGENT / "START_HERE.md")
        onboard = read(AGENT / "nudge-designer/references/ORACLE_ONBOARD.md")
        for word in ("oracle-onboard/README.md", "agent-onboard/README.md"):
            self.assertIn(word, start + onboard)
        self.assertIn("not extra", read(ORACLE / "README.md").lower())
        self.assertIn("existing", onboard.lower())


if __name__ == "__main__":
    unittest.main()
