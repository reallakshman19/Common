"""CLI never issues a false-green exit and never assumes available gh."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v32_readonly_cli import main
from v32_provider_preflight import PreflightResult


class CliTests(unittest.TestCase):
    def test_invalid_path_ends_failed_without_network(self):
        b = StringIO()
        with redirect_stdout(b):
            code = main(["--repository", "a/b", "--repository-id", "1",
                         "--graph-path", "../graph.json", "--leaf-ref", "b#1", "--pr-number", "1"])
        self.assertEqual(code, 1)
        self.assertIn("FAILED_TARGET", b.getvalue())

    def test_missing_local_facts_is_failed_input(self):
        b = StringIO()
        with redirect_stdout(b):
            code = main(["--repository", "a/b", "--repository-id", "1",
                         "--graph-path", "graph.json", "--leaf-ref", "b#1", "--pr-number", "1",
                         "--facts-file", "/missing/v32/facts.json"])
        self.assertEqual(code, 1)
        self.assertIn("FACTS_FILE_UNREADABLE", b.getvalue())

    def test_even_stable_readonly_witness_exits_nonzero(self):
        b = StringIO()
        fake = PreflightResult("HOLD_NO_APPROVED_POSITIVE_ISSUER", ("UNKNOWN",),
                               "TWO_CONSISTENT_NONATOMIC_READS_NOT_ATOMIC_PROOF", None, None, 2, None)
        with patch("v32_readonly_cli.inspect_v32_read_only", return_value=fake):
            with redirect_stdout(b):
                code = main(["--repository", "a/b", "--repository-id", "1",
                             "--graph-path", "graph.json", "--leaf-ref", "b#1", "--pr-number", "1"])
        self.assertEqual(code, 2)
        self.assertIn("HOLD_NO_APPROVED_POSITIVE_ISSUER", b.getvalue())

if __name__ == "__main__":
    unittest.main()
