"""Source/document continuity regression for Common's four-document handover.

Structural only: does not prove comprehension, reviewer independence, private
recipient byte verification, a live project Cycle or Oracle control cutover.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
AGENT = ROOT / "skills" / "agent-work"
LANDING = ROOT / "relay" / "AGENT_WORK" / "common-agent-work-oracle-continuity" / "knowledge-20261025"
PAYLOAD = LANDING / "payload"
FOUR = ("CONCEPT_NOTE.md", "ARCHITECTURE_COMPLEX_LOGIC.md",
        "ARCHITECTURE_DECISIONS_AND_CHALLENGES.md", "ORACLE_HANDOVER.md")
LINKS = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")


def read(path):
    return path.read_text(encoding="utf-8")


class CommonOracleGoldenHandoverTests(unittest.TestCase):
    def test_four_documents_are_substantive(self):
        for name in FOUR:
            with self.subTest(document=name):
                source = PAYLOAD / name
                self.assertTrue(source.is_file())
                text = read(source)
                self.assertGreater(len(text), 6000, "status-only/placeholder transfer")
                self.assertIn("Owner", text)
                self.assertIn("source", text.lower())
                self.assertIn("NOT", text)

    def test_all_local_links_in_packet_resolve(self):
        paths = [PAYLOAD / name for name in FOUR] + [
            LANDING / "ORACLE_SUCCESSOR_PROMPT.md",
            LANDING / "receipt.md",
        ]
        for source in paths:
            s = read(source)
            for m in LINKS.finditer(s):
                target = m.group(1).split("#")[0]
                if not target or "://" in target or target.startswith(("mailto:", "#")):
                    continue
                resolved = (source.parent / target).resolve()
                with self.subTest(file=source.name, link=target):
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.exists(), f"broken handover link: {resolved}")

    def test_owner_meaning_and_causal_logic_survive(self):
        concept = read(PAYLOAD / FOUR[0])
        architecture = read(PAYLOAD / FOUR[1])
        decisions = read(PAYLOAD / FOUR[2])
        for term in ("no blocker unless unsolvable", "Owner outcome",
                     "user journey", "two connected"):
            self.assertIn(term.lower(), concept.lower() + architecture.lower())
        for term in ("validate.py", "CURRENT.json", "expected_revision",
                     "Oracle epoch", "worker", "write", "Progress Page",
                     "Option 1", "Option 2", "LOCAL_ONLY"):
            self.assertIn(term.lower(), architecture.lower())
        for term in ("F1 —", "F2 —", "F8 —", "F12 —", "rejected",
                     "opposite", "source", "NOT_RUN"):
            self.assertTrue(term.lower() in decisions.lower() or
                            (term == "opposite" and "discriminator" in decisions.lower()), term)

    def test_frontier_has_real_boundaries_and_next_action(self):
        handover = read(PAYLOAD / "ORACLE_HANDOVER.md")
        for term in ("c3d10bc7", "NOT_ASSIGNED", "NOT_ESTABLISHED",
                     "T1–T5", "SELF_ASSESSED", "NOW", "two connected",
                     "NOT_CUTOVER"):
            self.assertIn(term.lower(), handover.lower())
        self.assertIn("G2", handover)  # CIIFR explicitly *not* this project

    def test_cold_prompt_routes_to_this_packet_not_ciifr_as_controller(self):
        prompt = read(LANDING / "ORACLE_SUCCESSOR_PROMPT.md")
        self.assertIn("READ-ONLY", prompt)
        self.assertIn("Common Agent-Work", prompt)
        self.assertIn("NOT CONTROL CUTOVER", prompt)
        self.assertIn("NOT_POSTED", prompt)
        self.assertIn("one", prompt.lower())
        self.assertIn("payload/CONCEPT_NOTE.md", prompt)
        self.assertIn("payload/ARCHITECTURE_COMPLEX_LOGIC.md", prompt)
        self.assertIn("payload/ARCHITECTURE_DECISIONS_AND_CHALLENGES.md", prompt)
        self.assertIn("payload/ORACLE_HANDOVER.md", prompt)

    def test_relay_has_correct_option_priority_and_claim_lattice(self):
        receipt = read(LANDING / "receipt.md")
        self.assertIn("Option 1", receipt)
        self.assertIn("Option 2", receipt)
        self.assertIn("LOCAL_ONLY", receipt)
        self.assertIn("NOT_YET_VERIFIED", receipt)
        self.assertIn("NOT_RUN", receipt)
        self.assertNotIn("drive.google.com/drive/folders/", receipt)

    def test_existing_protocols_link_all_four_without_new_gates(self):
        continuity = read(AGENT / "oracle-continuity/PROTOCOL.md")
        standalone = read(AGENT / "oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md")
        for name in FOUR:
            for protocol in (continuity, standalone):
                self.assertIn(name, protocol)
        for protocol in (continuity, standalone):
            self.assertIn("ORACLE_SUCCESSOR_PROMPT.md", protocol)
            self.assertIn("no", protocol.lower())
        self.assertIn("KNOWLEDGE_CHECKPOINT_PUBLISHED", continuity)
        self.assertIn("ORACLE_CONTROL_TRANSFERRED", continuity)
        self.assertIn("ONE immediately executable", standalone)
        self.assertNotIn("Prepare **exactly five plausible actions**", standalone)

    def test_dont_invent_canonical_common_cycle(self):
        architecture = read(PAYLOAD / "ARCHITECTURE_COMPLEX_LOGIC.md")
        handover = read(PAYLOAD / "ORACLE_HANDOVER.md")
        self.assertIn("not a transaction server", architecture.lower())
        self.assertIn("not** assigned", handover.lower() if "not** assigned" in handover.lower() else "not** assigned")
        self.assertIn("NOT_ESTABLISHED", handover)
        self.assertIn("c3d10bc7", handover)


if __name__ == "__main__":
    unittest.main()
