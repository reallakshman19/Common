"""Documentation regressions for the reusable source-grounded Agent OnBoard template.

These are static checks only. They do not create or authenticate an agent,
authorize a task, prove original engineering meaning, transfer private bytes,
or replace the selected native review/delivery process.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
AGENT_WORK = ROOT / "skills" / "agent-work"
BASE = AGENT_WORK / "nudge-designer" / "assets" / "agent-onboard"
FOUR = ("CONCEPT_NOTE.md", "ARCHITECTURE_COMPLEX_LOGIC.md",
        "ARCHITECTURE_DECISIONS_AND_CHALLENGES.md", "AGENT_HANDOVER.md")
LINKS = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")


def read(path):
    return path.read_text(encoding="utf-8")


class AgentOnBoardGoldenDocs(unittest.TestCase):
    def test_four_knowledge_templates_are_present_and_different(self):
        for name in FOUR:
            with self.subTest(name=name):
                text = read(BASE / name)
                self.assertGreater(len(text), 2500)
                self.assertIn("TEMPLATE", text)
                self.assertIn("{{", text)
                self.assertIn("source", text.lower())
                self.assertIn("Owner", text)
        self.assertIn("user journey", read(BASE / FOUR[0]).lower())
        self.assertIn("state", read(BASE / FOUR[1]).lower())
        self.assertIn("rejected", read(BASE / FOUR[2]).lower())
        self.assertIn("NOW", read(BASE / FOUR[3]))

    def test_actual_existing_routes_reference_new_template(self):
        route = read(AGENT_WORK / "START_HERE.md")
        guide = read(AGENT_WORK / "nudge-designer/references/ORACLE_ONBOARD.md")
        prompt = read(AGENT_WORK / "nudge-designer/assets/prompts/oracle-onboard.md")
        self.assertIn("nudge-designer/assets/agent-onboard/README.md", route)
        self.assertIn("nudge-designer/assets/agent-onboard/AGENT_ONBOARD_PROMPT.md", route)
        self.assertIn("../assets/agent-onboard/AGENT_ONBOARD_PROMPT.md", guide)
        self.assertIn("../agent-onboard/AGENT_ONBOARD_PROMPT.md", prompt)
        self.assertIn("existing", guide.lower())
        self.assertIn("not a required extra briefing", guide)

    def test_cold_prompt_is_executable_but_not_a_new_approval_gate(self):
        prompt = read(BASE / "AGENT_ONBOARD_PROMPT.md")
        readme = read(BASE / "README.md")
        handover = read(BASE / "AGENT_HANDOVER.md")
        for name in FOUR:
            self.assertIn(f"({name})", prompt)
        for text in (prompt, readme):
            self.assertTrue("no new" in text.lower() or "not a new" in text.lower())
            self.assertIn("independent reviewer", text.lower())
            self.assertIn("not", text.lower())
            self.assertIn("native", text.lower())
        self.assertIn("NOW", prompt)
        self.assertIn("native", handover.lower())
        self.assertIn("RETURNED", readme.upper() + prompt.upper())
        self.assertIn("SELF_ASSESSED", prompt)
        self.assertIn("NOT_RUN", prompt)
        self.assertIn("AWAIT_ORACLE_RECONCILIATION", prompt)

    def test_any_artifact_must_use_one_of_two_durable_routes(self):
        doc = read(BASE / "AGENT_HANDOVER.md")
        prompt = read(BASE / "AGENT_ONBOARD_PROMPT.md")
        readme = read(BASE / "README.md")
        for text in (doc, prompt, readme):
            self.assertRegex(text, r"(?i)(Option|Priority)\s*\*{0,2}1\*{0,2}")
            self.assertRegex(text, r"(?i)(Option|Priority)\s*\*{0,2}2\*{0,2}")
            self.assertIn("LOCAL_ONLY / NOT_TRANSFERRED", text)
            self.assertIn("Common", text)
            self.assertIn("Drive", text)
            self.assertIn("receipt", text.lower())
        self.assertIn("their own", doc.lower())

    def test_independence_and_writer_ownership_not_implied(self):
        prompt = read(BASE / "AGENT_ONBOARD_PROMPT.md")
        decisions = read(BASE / FOUR[2])
        handover = read(BASE / FOUR[3])
        self.assertIn("READ_ONLY", prompt)
        self.assertIn("do not", prompt.lower())
        self.assertIn("F6", decisions)
        self.assertIn("new assignment generation", handover.lower())
        self.assertIn("SELF_ASSESSED", handover)
        self.assertIn("original", decisions.lower())

    def test_local_links_exist_and_no_private_child_location(self):
        paths = [BASE / p for p in (*FOUR, "README.md", "AGENT_ONBOARD_PROMPT.md"),
                 AGENT_WORK / "nudge-designer/references/ORACLE_ONBOARD.md",
                 AGENT_WORK / "nudge-designer/assets/prompts/oracle-onboard.md",
                 AGENT_WORK / "START_HERE.md"]
        for source in paths:
            for match in LINKS.finditer(read(source)):
                url = match.group(1).strip()
                if not url or url.startswith(("#", "https:", "http:", "mailto:")):
                    continue
                target = (source.parent / url.split("#")[0]).resolve()
                with self.subTest(src=source.name, link=url):
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.exists(), f"Missing local path: {target}")
        for source in [BASE / p for p in (*FOUR, "README.md", "AGENT_ONBOARD_PROMPT.md")]:
            self.assertNotIn("drive.google.com/drive/folders/", read(source))


if __name__ == "__main__":
    unittest.main()
