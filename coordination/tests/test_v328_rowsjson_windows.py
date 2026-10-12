"""Executable Windows PowerShell v3.28 source-parity gate for Issue #353 WP2.

Both scripts and their dependencies come from the Owner-supplied skill archive,
pinned by SHA-256. The only source rewrite in temporary test copies changes
absolute dependency locations. No simulation of the RowsOut algorithm.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "v328_source"
ORIGINAL_SHA = "c8e0e06a753f5663bfa3768a9b3a61d9a62ee5f489a40916e3d4e614171b"
DEPS = {
    "state-io.ps1": "9f4a2164c5a31c636ebf1bfe991e84f9e4fe2adeed91820682c16c94252d8646",
    "aim-lib.ps1": "9623f038ba658cd254ee9bd0ad5498acd242c3e7d51ea0ca409083a41ae838ba",
    "cyclestate.ps1": "46f44c71cc1d13875510f237b6ed5f8f44eabc32b885aba557adf221aa172bd9",
}


class TestAuthoritativePowerShellWP2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("WP2_POWERSHELL_REQUIRED") != "1":
            raise unittest.SkipTest("Dedicated required Windows PowerShell job owns this test")
        cls.ps = shutil.which("powershell.exe") or shutil.which("powershell")
        if not cls.ps:
            raise AssertionError("WP2_POWERSHELL_REQUIRED=1 but powershell executable unavailable")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls._verify_source()
        for name in ("watch.ps1", "watch_rowsjson.ps1", *DEPS):
            text = (FIXTURES / name).read_text(encoding="utf-8")
            for dependency in DEPS:
                installed = r"C:\Users\reall\.claude\skills\coordinator-protocol\scripts" + "\\" + dependency
                text = text.replace(installed, str(cls.root / dependency))
            (cls.root / name).write_text(text, encoding="utf-8", newline="\n")
        cls.wrapper = cls.root / "invoke.ps1"
        cls.wrapper.write_text(r'''param([string]$Watch,[string]$Act,[string]$State,[switch]$Short)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
function Get-Date {
  param([string]$Format)
  $fixed = [datetime]"2026-10-12T12:00:00"
  if ($Format) { return $fixed.ToString($Format) }
  return $fixed
}
& ([scriptblock]::Create([IO.File]::ReadAllText($Watch, [Text.Encoding]::UTF8))) -Action $Act -Tabs '1=a1b2c3d4' -Session 'Session_Replay' -StateFile $State -Cycle 15 -Short:$Short
''', encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def _verify_source(cls):
        for filename, digest in (("watch.ps1", ORIGINAL_SHA), *DEPS.items()):
            actual = hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest()
            if actual != digest:
                raise AssertionError(f"Source SHA mismatch for {filename}: {actual}")
        original = (FIXTURES / "watch.ps1").read_text(encoding="utf-8")
        patched = (FIXTURES / "watch_rowsjson.ps1").read_text(encoding="utf-8")
        if patched.count("switch ($Action) {") != 1 or patched.count("function RowsOut {") != 1:
            raise AssertionError("Corrupt or duplicated PowerShell source")
        if "'rowsjson' {" not in patched or "function Capture-RowJson" not in patched:
            raise AssertionError("No real source-level capture/export")
        if "'rowsjson' {" in original:
            raise AssertionError("Original fixture was contaminated")

    def _state(self, kind):
        chat = {
            "id": "a1b2c3d4", "lastSeen": "2026-10-12T11:55:00",
            "lastState": "LOADFAIL" if kind == "loadfail" else "IDLE",
            "sumMin": 12, "sumPages": 3, "turns": 2,
            "pd": 2, "pt": 5, "aca": 1, "act": 3,
            "fPlan": "R2", "fTests": "3/3", "fPr": "#356@a5a55bc:green",
            "lastKind": "NONE", "last3": ["3m", "5m", "4m"],
        }
        names = {
            "normal": "Tab1 Worker",
            "out": "[OUT] Not mine",
            "hold": "[HOLD] Owner hold",
            "never": "Tab1 New chat",
            "shifted": "Tab2 Shifted",
            "loadfail": "Tab1 Worker",
        }
        mapping = "2|a1b2c3d4|coordination/test|Tab2 Shifted|" if kind == "shifted" else "1|a1b2c3d4|coordination/test|" + names[kind] + "|"
        cycle = {"map": [mapping], "seen": []}
        entries = ['"claude_code_cycle_Session_Replay": ' + json.dumps(cycle, separators=(",", ":"))]
        if kind != "never":
            entries.append('"claude_code_hw_a1b2c3d4": ' + json.dumps(chat, separators=(",", ":")))
        entries.append('"claude_code_log_anchor": 0')
        target = self.root / ("state_" + kind + ".json")
        target.write_text("{\n " + ",\n ".join(entries) + "\n}\n", encoding="utf-8")
        return target

    def _run(self, script, action, state, short=False):
        cmd = [self.ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", str(self.wrapper), "-Watch", str(self.root / script),
               "-Act", action, "-State", str(state)]
        if short:
            cmd += ["-Short"]
        p = subprocess.run(cmd, capture_output=True, timeout=60)
        if p.returncode != 0:
            self.fail(f"PowerShell {script} {action} exited {p.returncode}: "
                      f"stderr={p.stderr[-4000:]!r}; stdout={p.stdout[-4000:]!r}")
        return p.stdout.decode("utf-8-sig").strip()

    def test_source_rows_json_and_legacy_byte_parity(self):
        for case in ("normal", "out", "hold", "never", "shifted", "loadfail"):
            with self.subTest(case=case):
                state = self._state(case)
                for action, short in (("rows", False), ("report", False), ("report", True)):
                    old = self._run("watch.ps1", action, state, short=short)
                    new = self._run("watch_rowsjson.ps1", action, state, short=short)
                    self.assertEqual(new, old, f"Legacy output drift: {case}/{action}/{short}")
                raw = self._run("watch_rowsjson.ps1", "rowsjson", state)
                rows = json.loads(raw)
                self.assertEqual(len(rows), 1)
                row = rows[0]
                keys = ("tab", "status", "aim", "plan", "ac", "ci",
                        "meter", "due", "checked", "next")
                self.assertTrue(all(isinstance(row[k], str) for k in keys))
                self.assertEqual(row["tab_position"], "1")
                self.assertEqual(row["chat_id"], "a1b2c3d4")
                self.assertGreaterEqual(row["binding_generation"], 1)
                self.assertEqual(row["probe_status"], "NEVER_PROBED" if case == "never" else
                                 "LOADFAIL" if case == "loadfail" else "UNKNOWN" if case in ("out", "hold") else "SUCCESS")
                markdown_rows = [line for line in self._run("watch.ps1", "rows", state).splitlines()
                                 if line.startswith("| Tab1")]
                self.assertEqual(len(markdown_rows), 1)
                cells = [part.strip() for part in markdown_rows[0].strip().strip("|").split("|")]
                self.assertEqual(len(cells), 10, f"Unexpected pipe structure: {case}")
                self.assertEqual([row[k] for k in keys], cells)
