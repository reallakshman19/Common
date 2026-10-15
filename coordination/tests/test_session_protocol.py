"""Include the standalone CASP package in the existing coordination CI entrypoint."""
import subprocess
import sys
import unittest
from pathlib import Path


class SessionProtocolPackageTests(unittest.TestCase):
    def test_standalone_conformance(self):
        folder = Path(__file__).resolve().parents[1] / "session-protocol" / "tests"
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(folder), "-v"],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
