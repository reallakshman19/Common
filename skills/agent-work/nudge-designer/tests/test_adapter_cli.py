"""Actual mixed-role CLI exchanges and local source protection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from adapter_support import ROOT, native_return, team_case

CLI = ROOT / "scripts/nudge_designer.py"


class AdapterCliTests(unittest.TestCase):
    def test_actual_bind_fit_return_and_role_surface_roundtrip(self):
        intent, plan, profiles = team_case()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            intent_path, plan_path = folder / "intent.json", folder / "plan.json"
            report_path = folder / "return.json"
            intent_path.write_text(json.dumps(intent))
            plan_path.write_text(json.dumps(plan))

            def run(command, *extra):
                return subprocess.run([sys.executable, "-B", str(CLI), command, "--intent", str(intent_path),
                    "--plan", str(plan_path), *map(str, extra)], capture_output=True, text=True,
                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), timeout=15)

            result = run("bind", "--nudge", "N-PROBE")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = native_return(json.loads(result.stdout))
            report_path.write_text(json.dumps(report))
            result = run("fit", "--nudge", "N-PROBE", "--participant", "W")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "RECORDED_FIT")
            result = run("receive", "--report", report_path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["accepted_outcomes"], [])
            result = run("adapt", "--nudge", "N-PROBE", "--audience", "reviewer", "--surface", "github",
                         "--recipient", "R", "--report", report_path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Native result: PASS", json.loads(result.stdout)["content"])
            result = run("adapt", "--nudge", "N-PROBE", "--audience", "successor", "--surface", "buddy-checkpoint")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("N-EXPORT", json.loads(result.stdout)["content"])
            native = folder / "work-report.md"
            native.write_text("Actual native artifact preserved")
            result = run("receive", "--report", report_path, "--out", native)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(native.read_text(), "Actual native artifact preserved")
            self.assertEqual(json.loads(intent_path.read_text()), intent)
            self.assertEqual(json.loads(plan_path.read_text()), plan)
            self.assertEqual(json.loads(report_path.read_text()), report)

    def test_malformed_native_report_types_return_errors_without_tracebacks(self):
        intent, plan, profiles = team_case()
        from nd_team import task_binding
        from nd_returns import receive
        from nd_io import ContractError
        for change in (lambda r: r["findings"][0].update(kind=[]),
                       lambda r: r.update(attempts=[None]),
                       lambda r: r["native_report"].update(content="\ud800")):
            report = native_return(task_binding(intent, plan, "N-PROBE"))
            change(report)
            with self.assertRaises(ContractError):
                receive(intent, plan, report, profiles)

    def test_host_without_validator_reports_not_run_instead_of_a_false_pass(self):
        result = subprocess.run([sys.executable, "-B", "-S", str(CLI), "--help"], capture_output=True,
                                text=True, env=dict(os.environ, PYTHONPATH=""), timeout=15)
        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "NOT_RUN")
        self.assertEqual(output["missing_module"], "jsonschema")
        self.assertFalse(output["structural_validation_performed"])
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
