"""WP1 RED-first acceptance tests for v3.6.1 operating modes."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib
import inspect
import io
from pathlib import Path
from unittest import TestCase, mock
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lifecycle_v36 as life
import decompose_v36 as decompose

FIXTURE = ROOT / "tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml"
PLAN = ROOT / "plans/V36-341-PLAN-02.yaml"
CL = "reallakshman19/CoordinatorLandingpage"
MODES = ("coordinator", "standalone")


class ModeTests(TestCase):
    def setUp(self):
        self.base = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))

    def test_coordinator_mode_is_accepted(self):
        label = life.validate_label({**self.base, "mode": "coordinator"})
        self.assertEqual(life.label_mode(label), "coordinator")

    def test_standalone_mode_is_accepted(self):
        label = life.validate_label({**self.base, "mode": "standalone"})
        self.assertEqual(life.label_mode(label), "standalone")

    def test_other_modes_are_rejected(self):
        for value in ("other", "Standalone", "", None, 0, True, [], {}):
            with self.subTest(value=value), self.assertRaises(life.ContractError):
                life.validate_label({**self.base, "mode": value})

    def test_real_legacy_label_defaults_to_coordinator(self):
        old = life.load_label(FIXTURE)
        self.assertEqual(life.label_mode(old), "coordinator")
        self.assertNotIn("mode", old)

    def test_standalone_denies_coordination_repository(self):
        label = {**self.base, "mode": "standalone", "repository": CL}
        with self.assertRaisesRegex(life.ContractError, "standalone isolation"):
            life.validate_label(label)

    def test_standalone_denies_coordination_writable_lab(self):
        label = deepcopy(self.base)
        label["mode"] = "standalone"
        label["guidance"]["notes"] = ["Writable lab: " + CL]
        with self.assertRaisesRegex(life.ContractError, "standalone isolation"):
            life.validate_label(label)

    def test_coordination_mode_preserves_existing_target_rules(self):
        label = deepcopy(self.base)
        label["mode"] = "coordinator"
        label["repository"] = CL
        label["guidance"]["notes"] = []
        validated = life.validate_label(label)
        self.assertEqual(validated["repository"], CL)
        self.assertEqual(life.label_mode(validated), "coordinator")

    def test_standalone_denies_parent_even_if_label_was_unchecked(self):
        label = deepcopy(self.base)
        label["mode"] = "standalone"
        with self.assertRaisesRegex(life.ContractError, "standalone isolation"):
            life.require_explicit_lab(label, CL + "#341", CL)

    def test_all_label_target_clis_refuse_before_client_creation(self):
        label = deepcopy(self.base)
        label["mode"] = "standalone"
        label["repository"] = CL
        label["guidance"]["notes"] = []
        plan = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
        plan["parent"] = CL + "#341"
        with tempfile.TemporaryDirectory() as folder:
            d = Path(folder) / "relay/AIM"
            d.mkdir(parents=True)
            label_path = d / "V35-LIFECYCLE.yaml"
            plan_path = Path(folder) / "plan.yaml"
            label_path.write_text(yaml.safe_dump(label), encoding="utf-8")
            plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")
            for module_name in (
                "decompose_v36", "snapshot_v36", "publisher_v36",
                "successor_v36", "readmodel_v36",
                "prompt_2pass_v36", "prompt_3pass_v36",
            ):
                with self.subTest(cli=module_name):
                    module = importlib.import_module(module_name)
                    args = ["--label", str(label_path), "--plan", str(plan_path)]
                    if module_name == "successor_v36":
                        args = ["cold", *args, "--pr", "1"]
                    if module_name == "readmodel_v36":
                        args += ["--now", "2026-10-18T00:00:00Z"]
                    if module_name.startswith("prompt_"):
                        args += ["--task-id", "V36-341-WP1", "--pr", "1"]
                    out, err = io.StringIO(), io.StringIO()
                    with mock.patch.object(module, "GithubClient",
                                           side_effect=AssertionError("network access")) as client:
                        with redirect_stdout(out), redirect_stderr(err):
                            with mock.patch.object(sys, "argv", [module_name, *args]):
                                try:
                                    if inspect.signature(module.main).parameters:
                                        module.main(args)
                                    else:
                                        module.main()
                                except (Exception, SystemExit) as exc:
                                    message = str(exc) + out.getvalue() + err.getvalue()
                                else:
                                    message = out.getvalue() + err.getvalue()
                        client.assert_not_called()
                    self.assertIn("standalone isolation", message)

    def test_mode_docs_and_a01_a14_classification(self):
        for name in ("SKILL.md", "MODE_COORDINATOR.md", "MODE_STANDALONE.md"):
            with self.subTest(document=name):
                data = (ROOT / name).read_text(encoding="utf-8")
                self.assertLessEqual(len(data.splitlines()), 300)
        standalone = (ROOT / "MODE_STANDALONE.md").read_text(encoding="utf-8")
        for number in range(1, 15):
            with self.subTest(rule=number):
                self.assertIn(f"| A{number:02d} |", standalone)
        classifications = {}
        for line in standalone.splitlines():
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) == 3 and cells[0].startswith("A") and cells[0][1:].isdigit():
                self.assertNotIn(cells[0], classifications)
                classifications[cells[0]] = cells[1]
        expected = {f"A{n:02d}": ("Simplified" if n in (10, 12) else "Core")
                    for n in range(1, 15)}
        self.assertEqual(classifications, expected)
