import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/slice_check.py"
spec = importlib.util.spec_from_file_location("slice_check", SCRIPT)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def example(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def fails(card, fragment):
    errors = S.check(card)
    return any(fragment in e for e in errors), errors


class Examples(unittest.TestCase):
    def test_benchmark_r0_passes(self):
        self.assertEqual(S.check(example("CIIFR-S1.json")), [])

    def test_next_cards_pass(self):
        for name in ("CIIFR-S2.json", "CIIFR-S3.json"):
            self.assertEqual(S.check(example(name)), [], name)

    def test_horizon_is_connected(self):
        s1, s2, s3 = (example(f"CIIFR-S{i}.json") for i in (1, 2, 3))
        self.assertEqual(s1["state"], "accepted")
        self.assertIn("CIIFR-S2", [x["slice"] for x in s1["prepares_for"]])
        self.assertIn("CIIFR-S3", [x["slice"] for x in s2["prepares_for"]])
        self.assertIn("CIIFR-S2", [x["slice"] for x in s3["builds_on"]])

    def test_schema_is_valid_json_and_names_every_required_field(self):
        schema = json.loads((ROOT / "schemas/slice-card.v1.json").read_text(encoding="utf-8"))
        card = example("CIIFR-S1.json")
        for key in schema["required"]:
            self.assertIn(key, card)


class SeededDefects(unittest.TestCase):
    """Each rule is paired with a defect it must catch."""

    def setUp(self):
        self.r0 = example("CIIFR-S1.json")
        self.s2 = example("CIIFR-S2.json")

    def assertCaught(self, card, fragment):
        ok, errors = fails(card, fragment)
        self.assertTrue(ok, f"expected an error containing {fragment!r}, got {errors}")

    def test_no_real_input(self):
        c = copy.deepcopy(self.s2)
        c["real_inputs"] = []
        self.assertCaught(c, "real_inputs")

    def test_link_as_input_location(self):
        c = copy.deepcopy(self.s2)
        c["real_inputs"][0]["where"] = "https://example.org/folder"
        self.assertCaught(c, "not a link")

    def test_private_drive_link_anywhere(self):
        c = copy.deepcopy(self.s2)
        c["next_risks"].append("see drive.google.com/drive/folders/abc")
        self.assertCaught(c, "private link")

    def test_private_chat_link_as_evidence(self):
        c = copy.deepcopy(self.r0)
        c["after_use"]["evidence"] = "https://chatgpt.com/c/0000"
        self.assertCaught(c, "private link")

    def test_independent_without_reason(self):
        c = copy.deepcopy(self.s2)
        del c["why_check"]
        self.assertCaught(c, "why_check")

    def test_bad_wbs(self):
        c = copy.deepcopy(self.s2)
        c["wbs"] = "0.1"
        self.assertCaught(c, "wbs")

    def test_timebox_zero_and_too_long(self):
        for value in (0, 41, "4", True):
            c = copy.deepcopy(self.s2)
            c["timebox_h"] = value
            self.assertCaught(c, "timebox_h")

    def test_building_without_probe(self):
        c = copy.deepcopy(self.s2)
        c["state"] = "building"
        self.assertCaught(c, "probe")

    def test_runnable_without_demo(self):
        c = copy.deepcopy(self.r0)
        c["demo"] = c["demo"][:2]
        self.assertCaught(c, "demo")

    def test_runnable_without_command(self):
        c = copy.deepcopy(self.r0)
        c["runnable"] = " "
        self.assertCaught(c, "runnable")

    def test_tried_without_after_use(self):
        c = copy.deepcopy(self.r0)
        del c["after_use"]
        self.assertCaught(c, "after_use")

    def test_gaps_verdict_without_gaps(self):
        c = copy.deepcopy(self.r0)
        c["after_use"]["verdict"] = "gaps"
        self.assertCaught(c, "after_use.gaps")

    def test_accepted_without_owner_link(self):
        c = copy.deepcopy(self.r0)
        c["state"] = "accepted"
        del c["after_use"]["accept_src"]
        self.assertCaught(c, "accept_src")

    def test_hardened_without_exact_head(self):
        c = copy.deepcopy(self.r0)
        c["state"] = "hardened"
        c["after_use"]["accept_src"] = "https://github.com/o/r/issues/1#issuecomment-1"
        c["hardening"] = {"repo": "o/r", "head": "abc123", "evidence": "https://github.com/o/r/pull/1"}
        self.assertCaught(c, "hardening")

    def test_verified_needs_independent_check(self):
        c = copy.deepcopy(self.r0)
        c["state"] = "verified"
        c["after_use"]["accept_src"] = "https://github.com/o/r/issues/1#issuecomment-1"
        c["hardening"] = {"repo": "o/r", "head": "a" * 40, "evidence": "https://github.com/o/r/pull/1"}
        c["check_verdict"] = "https://github.com/o/r/pull/1#issuecomment-2"
        self.assertCaught(c, "state verified")

    def test_connection_needs_what(self):
        c = copy.deepcopy(self.s2)
        c["prepares_for"] = [{"slice": "CIIFR-S3"}]
        self.assertCaught(c, "prepares_for[0]")

    def test_unknown_state(self):
        c = copy.deepcopy(self.s2)
        c["state"] = "done"
        self.assertCaught(c, "state")


class CommandLine(unittest.TestCase):
    def run_cli(self, card):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "card.json"
            p.write_text(json.dumps(card), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)

    def test_exit_codes(self):
        good = self.run_cli(example("CIIFR-S1.json"))
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertIn("OK", good.stdout)
        bad = example("CIIFR-S2.json")
        bad["real_inputs"] = []
        res = self.run_cli(bad)
        self.assertEqual(res.returncode, 1)
        self.assertIn("real_inputs", res.stdout)


if __name__ == "__main__":
    unittest.main()
