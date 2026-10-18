import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, request, reconstruction

CLI = ROOT / "scripts/buddy_runner_v20.py"


class CliTests(unittest.TestCase):
    def run_cli(self, case, rec=None, extra=()):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "case.json"
            source.write_text(json.dumps(case))
            command = [sys.executable, str(CLI), "--input", str(source), *extra]
            if rec:
                record = Path(tmp) / "record.json"
                record.write_text(json.dumps(rec))
                command += ["--record", str(record)]
            return subprocess.run(command, text=True, capture_output=True)

    def test_prepare_reports_no_dispatch(self):
        result = self.run_cli(request())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INDEPENDENT_RECONSTRUCTION", result.stdout)
        self.assertIn("high-ROI", result.stdout)

    def test_onboard_result_waits_without_native_invocation(self):
        result = self.run_cli(request("ONBOARD", "AWAIT_OWNER_TASK"),
                              reconstruction(), ["--status-json"])
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value["state"], "AWAITING_RECONSTRUCTION_APPROVAL")
        self.assertFalse(value["agent_invoked"])

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "case.json"
            source.write_text('{"mode":"RECOVERY","mode":"ONBOARD"}')
            result = subprocess.run([sys.executable, str(CLI), "--input", str(source)],
                                    text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate", result.stderr.lower())

    def test_output_cannot_alias_any_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "case.json"
            source.write_text(json.dumps(request()))
            before = source.read_bytes()
            result = subprocess.run([sys.executable, str(CLI), "--input", str(source),
                                     "--output", str(source)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()

