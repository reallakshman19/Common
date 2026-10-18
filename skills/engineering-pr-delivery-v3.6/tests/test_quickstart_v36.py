"""Execute every QUICKSTART command offline, including failure examples.

Command fences are all executable Python invocations from the skill folder.
Git repositories are temporary, with deterministic LF content.
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

import yaml
from test_a13_check_v36 import fixture
from test_scored_v36 import PLAN, LABEL, valid_check, FROZEN

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "QUICKSTART_STANDALONE.md"
FENCES = re.compile(r"(?ms)^\x60\x60\x60([^\r\n]*)\r?\n(.*?)^\x60\x60\x60[ \t]*\r?$")


class QuickstartTests(unittest.TestCase):
    def _documented_commands(self, page):
        # Account for ALL fenced blocks. Unknown languages must fail closed.
        blocks = FENCES.findall(page)
        self.assertEqual(page.count("\x60\x60\x60"), 2 * len(blocks),
                         "unmatched or silently ignored fenced content")
        commands = []
        for language, content in blocks:
            if language in ("yaml", "text"):
                continue  # examples, never executable
            match = re.fullmatch(r"bash exit=(\d+)", language)
            self.assertIsNotNone(match, f"unsupported fence: {language!r}")
            commands.append((match[1], content))
        return commands

    def test_unsupported_fence_cannot_be_skipped(self):
        page = PAGE.read_text(encoding="utf-8")
        for language in ("sh", "powershell", "python", "bash", "",
                         "bash exit=bad", "bash exit=0 extra"):
            with self.subTest(language=language), self.assertRaises(AssertionError):
                self._documented_commands(
                    page + f"\n\x60\x60\x60{language}\npython -c 'print(99)'\n\x60\x60\x60\n")

    def test_windows_owner_setup_and_visible_label_path(self):
        page = PAGE.read_text(encoding="utf-8")
        for phrase in ("Git Bash", "PowerShell 5.1",
                       'python -m pip install "PyYAML>=6.0,<7.0"',
                       'python -c "import yaml;', "C:/",
                       "relay/AIM/<WORK>.yaml",
                       "1A. Create the label file"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, page)
        self.assertLess(page.index("1A. Create the label file"),
                        page.index("validate-label"))

    def test_owner_steps_and_boundaries(self):
        self.assertTrue(PAGE.is_file(), "AC10 quickstart page missing")
        page = PAGE.read_text(encoding="utf-8")
        self.assertLessEqual(len(page.splitlines()), 300)
        steps = ("1. Standalone label", "2. Freeze the Owner's criteria",
                 "3. Child task evidence and SELF-CHECK v2",
                 "4. Run the A13 checkpoint gate",
                 "5. Recompute the score", "6. Owner decision")
        positions = [page.index(x) for x in steps]
        self.assertEqual(positions, sorted(positions))
        for required in ("mode: standalone", "core.autocrlf=true",
                         "Owner confirms", "child issue", "a13_check_v36.py",
                         "score_v36.py", "does not verify", "test counts",
                         "diff paths", "accept or reject", "dry-run"):
            with self.subTest(phrase=required):
                self.assertIn(required, page)

    def test_every_command_executes_offline_as_documented(self):
        self.assertTrue(PAGE.is_file(), "AC10 quickstart missing commands")
        page = PAGE.read_text(encoding="utf-8")
        snippets = self._documented_commands(page)
        self.assertGreaterEqual(len(snippets), 7)
        self.assertEqual(page.count("\x60\x60\x60bash"), len(snippets),
                         "every command fence must declare an expected exit")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            repo = folder / "pilot"
            repo.mkdir()
            base, head, first, scope = fixture(repo)
            label = folder / "relay/AIM/V35-LIFECYCLE.yaml"
            label.parent.mkdir(parents=True)
            label.write_bytes(yaml.safe_dump({**LABEL, "mode": "standalone"},
                                            sort_keys=False).encode("utf-8"))
            plan = folder / "plan.yaml"
            plan.write_bytes(yaml.safe_dump(PLAN).encode("utf-8"))
            criteria = folder / "criteria.txt"
            criteria.write_bytes(FROZEN.encode("utf-8"))
            check = folder / "selfcheck.txt"
            check.write_bytes(valid_check().replace("f" * 40, head).encode("utf-8"))
            bad = folder / "inflated.txt"
            bad.write_bytes(check.read_bytes().replace(b"Score: 14/14", b"Score: 15/14"))
            before = folder / "before.json"
            after = folder / "after.json"
            diff = folder / "diff.json"
            before.write_bytes(json.dumps({"run": 297, "passed": 297, "sha": base}).encode())
            after.write_bytes(json.dumps({"run": 298, "passed": 298, "sha": head}).encode())
            diff.write_bytes(json.dumps({
                "paths": ["src/engine.py", "tests/test_more_v36.py"],
                "allowed_paths": ["src/engine.py", "tests/test_more_v36.py"],
                "removed_tests": 0, "test_first": True}).encode())
            values = {"__LABEL__": label.as_posix(), "__PLAN__": plan.as_posix(),
                      "__REPO__": repo.as_posix(), "__BASE__": base, "__HEAD__": head,
                      "__CRITERIA__": criteria.as_posix(),
                      "__SELFCHECK__": check.as_posix(),
                      "__INFLATED__": bad.as_posix(), "__BEFORE__": before.as_posix(),
                      "__AFTER__": after.as_posix(), "__DIFF__": diff.as_posix(),
                      "__BENEFIT__": "Offline example only",
                      "__PROOF__": "https://github.com/reallakshman19/Common/pull/433",
                      "__TASK__": "V36-341-WP1", "__CHILD__": "reallakshman19/Common#345",
                      "__CANDIDATE__": "reallakshman19/Common@" + head,
                      "__PASS__": "298", "__RUN__": "298"}
            netlog = folder / "network-attempts.log"
            blocker = folder / "sitecustomize.py"
            blocker.write_bytes((
                "import socket, os\n"
                "def deny(*args, **kwargs):\n"
                "    with open(os.environ['V36_NETLOG'], 'a') as log: log.write('attempt\\n')\n"
                "    raise RuntimeError('network prohibited by walkthrough test')\n"
                "socket.socket.connect=deny\n"
                "socket.socket.connect_ex=deny\n"
                "socket.create_connection=deny\n").encode("utf-8"))
            env = dict(os.environ, PYTHONPATH=folder.as_posix(),
                       V36_NETLOG=netlog.as_posix(),
                       GIT_TERMINAL_PROMPT="0", GIT_ALLOW_PROTOCOL="file")
            for index, (expected, content) in enumerate(snippets, 1):
                commands = [line for line in content.strip().splitlines() if line.strip()]
                self.assertEqual(len(commands), 1, f"block {index} must be one command")
                parts = shlex.split(commands[0], posix=True)
                self.assertEqual(parts[0], "python")
                self.assertNotIn("--apply", parts)
                self.assertNotIn("git push", content)
                self.assertNotIn("git clone", content)
                args = [sys.executable] + parts[1:]
                args = [self._substitute(arg, values) for arg in args]
                run = subprocess.run(args, cwd=ROOT, text=True,
                                     capture_output=True, env=env, check=False)
                self.assertEqual(run.returncode, int(expected),
                                 f"command {index} disagrees: {run.stdout} {run.stderr}")
            self.assertFalse(netlog.exists(), "walkthrough attempted network access")

    @staticmethod
    def _substitute(value, mapping):
        for tag, resolved in mapping.items():
            value = value.replace(tag, resolved)
        return value


if __name__ == "__main__":
    unittest.main()
