"""NLM pilot lesson contract and focused validator draft lint regressions."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from nd_validator_check import check_validator_draft


def section(title):
    doc = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    return doc.split("## " + title + "\n", 1)[1].split("\n## ", 1)[0]


class NlmPilotLessonsTests(unittest.TestCase):
    def test_table_yes_no_header_rejected_even_with_evidence_column(self):
        packet = (
            "| Item | All five factors match? (Yes/No) | Source evidence |\n"
            "|---|---|---|\n"
            "| 001 | YES | example line |\n"
        )
        self.assertTrue(check_validator_draft(packet))

    def test_binary_per_row_instruction_rejected(self):
        self.assertTrue(check_validator_draft("For each row report pass/fail."))
        self.assertTrue(check_validator_draft("Per item enter Y/N."))

    def test_source_evidence_review_passes_narrow_lint(self):
        packet = (
            "| Item | Quoted source evidence | Computed count | Finding |\n"
            "|---|---|---|---|\n"
            '| 001 | "alpha beta" | 2 | MATCH |\n'
            "Name three weakest items and give one reason for each.\n"
        )
        self.assertEqual(check_validator_draft(packet), [])

    def test_real_sample_packet_passes(self):
        packet = (ROOT / "examples/nlm-validator/packet.md").read_text(encoding="utf-8")
        self.assertEqual(check_validator_draft(packet), [])

    def test_cli_reports_failure_and_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.md"
            path.write_text("| Item | Yes/No |\n|---|---|\n| 1 | yes |\n", encoding="utf-8")
            command = [sys.executable, str(ROOT / "scripts/nd_validator_check.py"), str(path)]
            bad = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("DRAFT_CHECK FAIL", bad.stdout)
            path.write_text("| Item | Evidence |\n|---|---|\n| 1 | 3 |\n", encoding="utf-8")
            good = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0)
            self.assertIn("DRAFT_CHECK PASS", good.stdout)

    def test_guidance_is_in_its_own_relevant_sections(self):
        first = section("Start from the real assignment")
        draft = section("Check the draft and inspect its meaning")
        surfaces = section("Use with different participants and surfaces")
        self.assertIn("cp1252", first)
        self.assertIn("per-row yes/no", draft)
        self.assertIn("three weakest", draft)
        self.assertIn("independently recompute", draft)
        self.assertIn("GUIDED", surfaces)
        self.assertIn("ONE\nresult file", surfaces)

    def test_example_packet_and_result_sha_are_byte_bound(self):
        folder = ROOT / "examples/nlm-validator"
        intro = (folder / "README.md").read_text(encoding="utf-8")
        for name in ("packet.md", "nlm-p3-result.md"):
            digest = hashlib.sha256((folder / name).read_bytes()).hexdigest()
            self.assertIn(digest, intro)
        self.assertIn("rows=3", intro)
        self.assertEqual(len((folder / "sample-items.txt").read_text(encoding="utf-8").splitlines()), 3)

    def test_changed_authored_files_within_a13_line_limit(self):
        paths = [
            ROOT / "SKILL.md", ROOT / "scripts/nd_validator_check.py",
            ROOT / "tests/test_nlm_lessons.py",
            *(ROOT / "examples/nlm-validator").iterdir(),
        ]
        for path in paths:
            with self.subTest(path=path.name):
                self.assertLessEqual(len(path.read_bytes().splitlines()), 300)


if __name__ == "__main__":
    unittest.main()
