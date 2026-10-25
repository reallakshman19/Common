"""Source checks: Oracle four-file onboarding and v3.5-safe title ownership.

Static only: no live Oracle, agent, GitHub publisher, browser or cutover test.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
AGENT = ROOT / "skills" / "agent-work"
ORACLE = AGENT / "nudge-designer" / "assets" / "oracle-onboard"
NATIVE = AGENT / "nudge-designer" / "references" / "TITLE_AND_TRAFFIC_HYGIENE.md"
FOUR = ("CONCEPT_NOTE.md", "ARCHITECTURE_COMPLEX_LOGIC.md",
        "ARCHITECTURE_DECISIONS_AND_CHALLENGES.md", "ORACLE_HANDOVER.md")
LINKS = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")


def read(path):
    return path.read_text(encoding="utf-8")


class OracleOnboardTitleDocs(unittest.TestCase):
    def test_four_oracle_templates_and_actual_role_prompt(self):
        for name in FOUR:
            with self.subTest(name=name):
                text = read(ORACLE / name)
                self.assertIn("TEMPLATE", text)
                self.assertIn("Owner", text)
                self.assertIn("{{", text)
                self.assertGreater(len(text), 1400)
        prompt = read(ORACLE / "ORACLE_ONBOARD_PROMPT.md")
        self.assertIn("NEW_ORACLE", prompt)
        self.assertIn("PROMOTED_ORACLE", prompt)
        self.assertIn("CANDIDATE_SUCCESSOR_READ_ONLY", prompt)
        self.assertIn("KNOWLEDGE_READ_ONLY / NO_CONTROL_CUTOVER", prompt)
        self.assertIn("ONE", prompt)
        for name in FOUR:
            self.assertIn(f"({name})", prompt)

    def test_v35_projector_is_sole_owner_of_generated_issue_title(self):
        hygiene = read(NATIVE)
        oracle = read(ORACLE / "ORACLE_ONBOARD_PROMPT.md")
        agent = read(AGENT / "nudge-designer/assets/agent-onboard/AGENT_ONBOARD_PROMPT.md")
        v35 = read(ROOT / "skills/engineering-pr-delivery-v3.5/SKILL.md")
        self.assertIn("CHECKPOINT_FACTS_V1", hygiene)
        self.assertIn("DEL P", hygiene.replace("DELP", "DEL P"))
        self.assertIn("never manually authored", hygiene)
        self.assertIn("only the DELP runner", v35)
        self.assertIn("NEVER hand-edit", oracle)
        self.assertIn("Do not manually alter v3.5", agent)
        self.assertIn("CHAT-ID8", hygiene)
        self.assertIn("CHAT_ID8: UNKNOWN", hygiene)
        self.assertIn("authenticated author", hygiene)
        for color in ("🟢", "🟡", "🔴", "🔵"):
            self.assertIn(color, hygiene)
        self.assertIn("OWNER_ACTION: <NONE", hygiene)

    def test_pr_title_hygiene_is_conditional_on_native_title_ownership(self):
        docs = (read(NATIVE), read(ORACLE / "README.md"),
                read(AGENT / "nudge-designer/assets/agent-onboard/README.md"))
        self.assertIn("[<TASK-ID>][<ROLE>:<CHAT-ID8>]", docs[0])
        self.assertIn("If the title has a strict", docs[0])
        self.assertIn("No new", read(ORACLE / "README.md"))
        self.assertIn("return", read(ORACLE / "ORACLE_HANDOVER.md").lower())
        for text in docs:
            self.assertIn("DELP", text)
            self.assertIn("Chat", text)
        self.assertIn("NOT_TRANSFERRED", docs[1])
        self.assertIn("LOCAL_ONLY", docs[2])

    def test_local_links_and_no_protected_child_links(self):
        paths = [ORACLE / p for p in (*FOUR, "README.md", "ORACLE_ONBOARD_PROMPT.md")] + [
            NATIVE,
            AGENT / "nudge-designer/assets/agent-onboard/AGENT_ONBOARD_PROMPT.md"]
        for path in paths:
            with self.subTest(source=path.name):
                s = read(path)
                self.assertNotIn("drive.google.com/drive/folders/", s)
                for match in LINKS.finditer(s):
                    loc = match.group(1).split("#")[0].strip()
                    if not loc or "://" in loc or loc.startswith(("#", "mailto:")):
                        continue
                    target = (path.parent / loc).resolve()
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.exists(), str(target))


if __name__ == "__main__":
    unittest.main()
