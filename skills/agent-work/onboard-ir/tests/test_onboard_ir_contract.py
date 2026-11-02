"""OnBoard IR protocol smoke tests: no false real-source PASS or seeded stage 1."""
import csv
import io
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

MODULE = Path(__file__).resolve().parents[1]
AGENT = MODULE.parent
REPO = MODULE.parents[2]


def read(relative):
    return (MODULE / relative).read_text(encoding="utf-8")


class OnboardIrContract(unittest.TestCase):

    def test_skill_and_protocol_discoverable(self):
        skill = read("SKILL.md")
        self.assertTrue(skill.startswith("---\nname: onboard-ir\n"))
        for name in ("README.md", "PROTOCOL.md", "METHODOLOGY.md",
                     "ORACLE_CONTINUITY_BRIDGE.md",
                     "AGENT_ONBOARD_BRIDGE.md", "CHECKLIST.md"):
            self.assertTrue((MODULE/name).is_file(), name)
        for path in (
            AGENT/"START_HERE.md",
            AGENT/"REFERENCE_INDEX.md",
            AGENT/"independent-review/SKILL.md",
            AGENT/"oracle-continuity/PROTOCOL.md",
            AGENT/"nudge-designer/assets/agent-onboard/README.md",
        ):
            self.assertIn("onboard-ir/", path.read_text(encoding="utf-8"), str(path))

    def test_markdown_links_resolve_within_current_repository(self):
        all_md=list(MODULE.rglob("*.md"))
        routed=[
            AGENT/"START_HERE.md", AGENT/"REFERENCE_INDEX.md",
            AGENT/"independent-review/SKILL.md",
            AGENT/"oracle-continuity/PROTOCOL.md",
            AGENT/"nudge-designer/assets/agent-onboard/README.md",
        ]
        # Restrict broad legacy routing docs to our newly introduced links:
        # their pre-existing links are outside this module's contract.
        for path in all_md:
            body=path.read_text(encoding="utf-8")
            for href in re.findall(r"\]\(([^)]+)\)",body):
                target=unquote(href.split("#",1)[0])
                if not target or target.startswith(("https://","http://","mailto:")):
                    continue
                self.assertTrue((path.parent/target).is_file() or
                                (path.parent/target).is_dir(),
                                f"{path.relative_to(REPO)} -> {href}")
        for path in routed:
            text=path.read_text(encoding="utf-8")
            for href in re.findall(r"\]\(([^)]+)\)",text):
                if "onboard-ir/" not in href:
                    continue
                target=href.split("#",1)[0]
                self.assertTrue((path.parent/target).is_file(),
                                f"{path.relative_to(REPO)} -> {href}")

    def test_cold_prompt_never_seeds_golden_or_author_pr(self):
        for name in ("templates/STAGE1_COLD_PROMPT.md",
                     "examples/xml229/RAW_CASE.md"):
            text=read(name)
            self.assertNotIn("GOLDEN_WITHHOLD_UNTIL_AFTER_STAGE2.md",text)
            for number in range(392,400):
                self.assertNotIn(f"/pull/{number}",text)
            self.assertNotIn("all 21 are resolved",text.lower())
        self.assertIn("NOT_RUN",read("templates/STAGE1_COLD_PROMPT.md"))
        self.assertIn("after",read("templates/STAGE2_SOLUTION_PROMPT.md").lower())

    def test_twenty_one_claims_are_template_only(self):
        contents=read("examples/xml229/OWNER_21_CLAIMS_UNEVIDENCED.csv")
        rows=list(csv.DictReader(io.StringIO("\n".join(contents.splitlines()[1:]))))
        self.assertEqual(len(rows),21)
        self.assertEqual(len({r["claim_id"] for r in rows}),21)
        for row in rows:
            self.assertEqual(row["private_source_custody"],"NOT_RECEIVED")
            self.assertEqual(row["physical_vertex_classification"],"NOT_EVIDENCED")
            self.assertEqual(row["falsifier_execution"],"NOT_RUN")
            self.assertEqual(row["native_element_and_restraint_witness"],"NOT_RUN")
            self.assertEqual(row["disposition"],"UNRESOLVED_NO_SOURCE")
            self.assertEqual(row["authority_and_native_return"],"NOT_RECONCILED")
            self.assertEqual(row["actual_cii_sha256"],"NOT_RUN")

    def test_golden_and_worked_handoff_never_claim_production_pass(self):
        golden=read("examples/xml229/GOLDEN_WITHHOLD_UNTIL_AFTER_STAGE2.md")
        history=read("examples/xml229/WORKED_HANDOFF.md")
        self.assertIn("WITHHOLD",golden)
        self.assertIn("not",golden.lower())
        self.assertIn("not a real engineering product acceptance",golden)
        self.assertIn("NOT_RUN",history)
        self.assertIn("SELF_REVIEW",history)
        self.assertIn("NO PRODUCTION RELEASE",history)

    def test_oracle_continuity_keeps_independent_expectation(self):
        bridge=read("ORACLE_CONTINUITY_BRIDGE.md")
        for value in ("Owner outcome","Original evidence","Expected behavior",
                      "Candidate","Falsifier","Judgment","Decision","Next actor",
                      "STALE","POSTED","late return"):
            self.assertIn(value.lower(),bridge.lower())
        self.assertIn("SELF_REVIEW",bridge)
        self.assertIn("NOT_RUN",bridge)

    def test_review_template_has_causal_evidence_chain(self):
        schema=read("templates/CLAIM_EVIDENCE_MATRIX.csv").splitlines()[0].split(",")
        required={"claim_id","original_byte_sha256_or_UNKNOWN",
                  "expectation_authority","stage1_native_return",
                  "reviewed_candidate_sha","falsifier_witness",
                  "reviewer_identity_or_UNKNOWN","decision_owner"}
        self.assertTrue(required.issubset(set(schema)))
        self.assertIn("NOT_RECEIVED",read("templates/IR_ASSIGNMENT.md"))
        self.assertIn("Surviving wrong",read("templates/FINDINGS_REPORT.md"))


if __name__ == "__main__":
    unittest.main()
