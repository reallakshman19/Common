"""Exercise real CLI boundaries, custom libraries and large declared work."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from nd_contract import intent_digest, validate_plan
from nd_io import ContractError, load_json
from nd_profiles import load_profiles, profile_digest
from nd_render import render_nudge

CLI = ROOT / "scripts" / "nudge_designer.py"


class SupportTests(unittest.TestCase):
    def setUp(self):
        folder = ROOT / "examples" / "logic"
        self.intent_path, self.plan_path = folder / "intent.json", folder / "plan.json"
        self.intent, self.plan = load_json(self.intent_path), load_json(self.plan_path)
        self.profiles = load_profiles()

    def cli(self, *arguments):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "-B", str(CLI), *map(str, arguments)],
                              capture_output=True, text=True, env=env, timeout=15)

    def test_both_schema_documents_are_valid_draft_2020_12(self):
        for name in ("intent", "plan"):
            Draft202012Validator.check_schema(load_json(ROOT / "schemas" / (name + ".schema.json")))

    def test_real_validate_and_render_cli_for_each_case(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("lfea", "logic", "grade11", "fea"):
                with self.subTest(case=name):
                    folder = ROOT / "examples" / name
                    intent_path, plan_path = folder / "intent.json", folder / "plan.json"
                    result = self.cli("validate", "--intent", intent_path, "--plan", plan_path)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertFalse(json.loads(result.stdout)["execution_performed"])
                    for nudge in load_json(plan_path)["nudges"]:
                        output = Path(directory) / (name + "-" + nudge["id"] + ".md")
                        result = self.cli("render", "--intent", intent_path, "--plan", plan_path,
                                          "--nudge", nudge["id"], "--out", output)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertEqual(result.stdout, "")
                        self.assertEqual(output.read_text().count("\n## "), 7)
                        self.assertIn("does not grant permission", output.read_text())

    def test_real_impact_cli_reports_no_change_without_editing_inputs(self):
        before = [path.read_bytes() for path in (self.intent_path, self.plan_path)]
        result = self.cli("impact", "--previous-intent", self.intent_path,
                          "--previous-plan", self.plan_path, "--intent", self.intent_path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "NO_DECLARED_IMPACT")
        self.assertEqual(before, [path.read_bytes() for path in (self.intent_path, self.plan_path)])

    def test_cli_cannot_overwrite_input_or_symlink_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "intent.json"
            source.write_bytes(self.intent_path.read_bytes())
            alias = Path(directory) / "alias.json"
            alias.symlink_to(source)
            for target in (source, alias):
                before = source.read_bytes()
                result = self.cli("validate", "--intent", source, "--plan", self.plan_path,
                                  "--out", target)
                self.assertEqual(result.returncode, 2)
                self.assertIn("overwrite an input", json.loads(result.stdout)["reason"])
                self.assertEqual(before, source.read_bytes())

    def test_cli_invalid_json_and_stale_binding_are_useful_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            invalid = copy.deepcopy(self.intent)
            invalid["purpose"] += " altered"
            for contents in ('{"id": "a", "id": "b"}', json.dumps(invalid)):
                path.write_text(contents)
                result = self.cli("validate", "--intent", path, "--plan", self.plan_path)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "INVALID")
                self.assertNotIn("Traceback", result.stderr)

    def test_custom_library_rejects_unknown_fields_and_duplicate_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            library = {"schema": "nudge-designer.profiles/v1", "profiles": [self.profiles["core"]]}
            for mutation in ("unknown", "duplicate", "empty"):
                data = copy.deepcopy(library)
                if mutation == "unknown":
                    data["profiles"][0]["execution_authorized"] = True
                elif mutation == "duplicate":
                    data["profiles"].append(copy.deepcopy(data["profiles"][0]))
                else:
                    data["profiles"][0]["evidence_methods"] = []
                path.write_text(json.dumps(data))
                with self.assertRaises(ContractError):
                    load_profiles(path)

    def test_cli_accepts_a_composed_custom_domain_without_core_changes(self):
        custom = copy.deepcopy(self.profiles["core"])
        custom.update(id="translation", label="Translation review", revision="1",
                      reasoning_moves=["compare_register"], evidence_methods=["bilingual_review"])
        self.profiles["translation"] = custom
        self.plan["profile_ids"].append("translation")
        self.plan["profiles_sha256"] = profile_digest(self.profiles, self.plan["profile_ids"])
        nudge = self.plan["nudges"][0]
        nudge["profile_ids"].append("translation")
        nudge["reasoning_moves"], nudge["evidence_methods"] = ["compare_register"], ["bilingual_review"]
        with tempfile.TemporaryDirectory() as directory:
            library = Path(directory) / "profiles.json"
            plan = Path(directory) / "plan.json"
            library.write_text(json.dumps({"schema": "nudge-designer.profiles/v1",
                                           "profiles": list(self.profiles.values())}))
            plan.write_text(json.dumps(self.plan))
            result = self.cli("render", "--intent", self.intent_path, "--plan", plan,
                              "--profiles", library, "--nudge", nudge["id"])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Translation review", result.stdout)
            self.assertIn("bilingual_review", result.stdout)

    def test_large_hierarchy_and_many_nudges_preserve_remaining_work(self):
        parent = "O-CURRENT"
        for number in range(80):
            ident = "O-SUB-" + str(number)
            self.intent["outcomes"].append({"id": ident, "parent_id": parent,
                "text": "Declared subproblem " + str(number), "done_when": "Observed coherent result",
                "item_refs": ["R-CURRENT"]})
            self.plan["coverage"].append({"target_id": ident, "disposition": "UNRESOLVED",
                "nudge_ids": [], "evidence_refs": [], "rationale": "Not executed; parent outcome remains."})
            parent = ident
        first = self.plan["nudges"][0]
        first["outcome_refs"] = [parent]
        for number in range(80):
            child = copy.deepcopy(first)
            child.update(id="N-SUB-" + str(number), parent_id=first["id"], depends_on=[])
            self.plan["nudges"].append(child)
        self.plan["intent_sha256"] = intent_digest(self.intent)
        report = validate_plan(self.intent, self.plan, self.profiles)
        self.assertEqual(report["nudges"], 83)
        self.assertEqual(report["coverage_basis"], "DECLARED_ITEMS_ONLY")
        self.assertIn("O-EXPORT", render_nudge(self.intent, self.plan, first["id"], self.profiles))

    def test_multiple_original_conditions_survive_condensation(self):
        condition = "Original binary: 100 MiB; record limit: 2,000,000; both constraints apply."
        constraint = next(row for row in self.intent["items"] if row["kind"] == "CONSTRAINT")
        constraint["condition"] = condition
        self.plan["intent_sha256"] = intent_digest(self.intent)
        output = render_nudge(self.intent, self.plan, "N-PROBE", self.profiles)
        self.assertIn(condition, output)


if __name__ == "__main__":
    unittest.main()
