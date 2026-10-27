"""Run source-synced portable Agent Start behavior in the existing Python CI matrix."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PortableAgentStart(unittest.TestCase):
    def test_exact_task_route_and_scoped_exports(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("NOT_RUN: Node unavailable for Agent Start behavioral regression")
        result = subprocess.run(
            [node, "--experimental-default-type=module", "--test",
             str(ROOT / "tests" / "portable-agent-start.test.mjs")],
            cwd=ROOT, text=True, capture_output=True, timeout=45, check=False)
        self.assertEqual(result.returncode, 0,
                         "Portable Agent Start Node tests:\n" + result.stdout + "\n" + result.stderr)

if __name__ == "__main__":
    unittest.main()
