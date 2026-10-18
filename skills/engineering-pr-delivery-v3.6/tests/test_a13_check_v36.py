"""Offline RED-first tests for the nine v3.6.1 mechanical checkpoints."""
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def write(repo, name, data):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def fixture(repo, variant=""):
    """Three commits, including a test-only first implementation gate."""
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "user.name", "Fixture")
    write(repo, "src/engine.py", "def calculate():\n    return 0\n")
    write(repo, "tests/test_base_v36.py",
          "import unittest\nclass Base(unittest.TestCase):\n"
          "    def test_base(self):\n        self.assertEqual(1, 1)\n")
    write(repo, ".github/workflows/ci.yml",
          "name: CI\non: push\njobs:\n  tests:\n    runs-on: ubuntu-latest\n"
          "    steps:\n      - run: python -m unittest discover -s tests -p 'test_*_v36.py'\n")
    write(repo, "requirements.txt", "PyYAML>=6.0,<7.0\n")
    paths = ["src/engine.py", "tests/test_more_v36.py",
             "tests/test_other.py", "tests/test_base_v36.py",
             "requirements.txt"]
    policy = {"paths": paths, "ci_workflow": ".github/workflows/ci.yml",
              "ci_pattern": "test_*_v36.py", "protected": ["logs/", "protocol/"],
              "forbidden_literals": ["AcmeProject"]}
    write(repo, "policy.json", json.dumps(policy, sort_keys=True) + "\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "base")
    base = git(repo, "rev-parse", "HEAD")

    if variant == "C12":
        write(repo, "src/engine.py", "def calculate():\n    return 1\n")
    else:
        name = "tests/test_other.py" if variant == "C1" else "tests/test_more_v36.py"
        write(repo, name, "import unittest\nclass More(unittest.TestCase):\n"
              "    def test_new(self):\n        self.assertEqual(2, 2)\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "tests first")
    first = git(repo, "rev-parse", "HEAD")

    if variant == "C12":
        write(repo, "tests/test_more_v36.py",
              "import unittest\nclass More(unittest.TestCase):\n"
              "    def test_new(self):\n        self.assertEqual(2, 2)\n")
    elif variant == "C11":
        write(repo, "src/engine.py", "def calculate():\n\n    return 0\n")
    else:
        extra = ""
        if variant == "C13":
            extra = "    project_name = 'AcmeProject'\n"
        if variant == "C16":
            extra = "    token = 'ghp_" + ("a" * 36) + "'\n"
        write(repo, "src/engine.py",
              "def calculate():\n" + extra + "    return 1\n")
    if variant == "C3":
        write(repo, "tests/test_base_v36.py",
              "import unittest\nclass Base(unittest.TestCase):\n"
              "    def test_base(self):\n        pass\n")
    if variant == "C10":
        write(repo, "other/undeclared.py", "value = 1\n")
    if variant == "C17":
        write(repo, "requirements.txt", "PyYAML>=6.0,<7.0\nrequests>=2\n")
    if variant == "SIZE":
        write(repo, "src/engine.py", "def calculate():\n    return 1\n"
              + ("# retained source line\n" * 301))
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "implementation")
    return base, git(repo, "rev-parse", "HEAD"), first, repo / "policy.json"


class CheckpointTests(unittest.TestCase):
    def assessment(self, variant=""):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base, head, first, scope = fixture(repo, variant)
            checker = importlib.import_module("a13_check_v36")
            report = checker.check(repo, base, head, scope)
            self.assertEqual(report["first_test_commit"], first)
            self.assertEqual(set(report["checks"]),
                             {"C1", "C3", "C10", "C11", "C12",
                              "C13", "C16", "C17", "A13"})
            return report["checks"]

    def test_c1_positive(self):
        self.assertTrue(self.assessment()["C1"])

    def test_c1_negative_ci_glob_misses_new_test(self):
        self.assertFalse(self.assessment("C1")["C1"])

    def test_c3_positive(self):
        self.assertTrue(self.assessment()["C3"])

    def test_c3_negative_removed_assertion(self):
        self.assertFalse(self.assessment("C3")["C3"])

    def test_c10_positive(self):
        self.assertTrue(self.assessment()["C10"])

    def test_c10_negative_undeclared_file(self):
        self.assertFalse(self.assessment("C10")["C10"])

    def test_c11_positive(self):
        self.assertTrue(self.assessment()["C11"])

    def test_c11_negative_blank_line_only_change(self):
        self.assertFalse(self.assessment("C11")["C11"])

    def test_c12_positive(self):
        self.assertTrue(self.assessment()["C12"])

    def test_c12_negative_source_committed_before_new_test(self):
        self.assertFalse(self.assessment("C12")["C12"])

    def test_c13_positive(self):
        self.assertTrue(self.assessment()["C13"])

    def test_c13_negative_hardcoded_project_literal(self):
        self.assertFalse(self.assessment("C13")["C13"])

    def test_c16_positive(self):
        self.assertTrue(self.assessment()["C16"])

    def test_c16_negative_embedded_token(self):
        self.assertFalse(self.assessment("C16")["C16"])

    def test_c17_positive(self):
        self.assertTrue(self.assessment()["C17"])

    def test_c17_negative_new_dependency(self):
        self.assertFalse(self.assessment("C17")["C17"])

    def test_a13_positive(self):
        self.assertTrue(self.assessment()["A13"])

    def test_a13_negative_new_file_over_300_lines(self):
        self.assertFalse(self.assessment("SIZE")["A13"])

    def test_c5_checkpoint_table_has_18_three_mode_rows(self):
        text = (ROOT / "CODING_PRACTICES_ADDENDUM.md").read_text("utf-8")
        lines = [line for line in text.splitlines()
                 if line.startswith("| C") and " | " in line]
        self.assertEqual(len(lines), 18)
        for number, line in enumerate(lines, 1):
            self.assertTrue(line.startswith(f"| C{number} |"), line)
            self.assertGreaterEqual(line.count("|"), 5)
