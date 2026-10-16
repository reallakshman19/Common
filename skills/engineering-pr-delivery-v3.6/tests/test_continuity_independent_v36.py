"""C1/C1A independence qualification: no earlier Relay folders are needed."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ("issue_chain_v36.py", "continuity_addendum_v36.py",
           "continuity_bridge_v36.py")
FIXTURE = "issue-chain-274-reported.json"


class StandaloneContinuityTests(unittest.TestCase):
    def test_c1a_import_contract_is_v36_only(self):
        for name in SCRIPTS:
            source = ROOT / "scripts" / name
            tree = ast.parse(source.read_text(encoding="utf-8"))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            allowed = {"__future__", "argparse", "hashlib", "json", "re",
                       "pathlib", "urllib", "issue_chain_v36",
                       "continuity_addendum_v36"}
            self.assertFalse(imported - allowed, (name, imported - allowed))

    def test_isolated_cold_bridge_requires_no_v35_v32_v31_or_delp(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            for name in SCRIPTS:
                shutil.copyfile(ROOT / "scripts" / name, base / name)
            shutil.copyfile(ROOT / "tests" / "fixtures" / FIXTURE,
                            base / FIXTURE)
            # No other Common skills, historical Relay modules or repo packages.
            self.assertEqual(sorted(p.name for p in base.iterdir()),
                             sorted((*SCRIPTS, FIXTURE)))
            # -I excludes script directories; explicitly allow ONLY the
            # temporary isolated v3.6 modules, never the full Common repo.
            invocation = ("import sys; sys.path.insert(0, " +
                          repr(str(base)) + "); import continuity_bridge_v36; " +
                          "raise SystemExit(continuity_bridge_v36.main(" +
                          repr(["--input", str(base / FIXTURE),
                                "--inspect-protocol", "--governed-v36"]) + "))")
            completed = subprocess.run(
                [sys.executable, "-I", "-c", invocation],
                cwd=str(base), text=True, capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["required_categories"], 11)
            self.assertEqual(result["reported_categories"], 7)
            self.assertEqual(result["verified_source_categories"], 0)
            self.assertEqual(result["evidence_routing"]["mode"],
                             "NATIVE_V36_REQUIRED")
            self.assertFalse(result["may_publish"])
            self.assertFalse(result["may_count_for_native_o2"])


if __name__ == "__main__":
    unittest.main()
