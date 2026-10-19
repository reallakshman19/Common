import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/task_decomposer.py"
spec = importlib.util.spec_from_file_location("task_decomposer", SCRIPT)
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)


def fixture(name="ui-programme"):
    return T.load(ROOT / "examples" / name / "task-map.json")


def row(value, key):
    return next(t for t in value["tasks"] if t["id"] == key)


def run_cli(*args, script=SCRIPT, env=None):
    return subprocess.run([sys.executable, "-B", str(script), *map(str, args)], text=True, capture_output=True, env=env)


class TaskMapContract(unittest.TestCase):
    def test_schema_and_four_distinct_maps(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(T.load(T.SCHEMA))
        for name in ("ui-programme", "single-logic", "study-programme", "single-model"):
            with self.subTest(name=name):
                value = fixture(name)
                T.validate(value)
                for task in value["tasks"]:
                    if task["detail"] == "BOUNDED":
                        self.assertIn(T.digest(value), T.render(value, task["id"]))

    def test_single_coherent_task_has_no_minimum_size_or_count(self):
        value = fixture("single-logic")
        self.assertEqual(1, len(T.validate(value)["tasks"]))
        self.assertEqual("DESIGN_CANDIDATE", T.frontier(value)["candidates"][0]["state"])

    def test_duplicate_ids_and_unknown_fields_rejected(self):
        for field in ("sources", "items", "tasks"):
            with self.subTest(field=field):
                value = fixture();value[field].append(copy.deepcopy(value[field][0]))
                with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture();value["progress_percent"] = 90
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_wrong_version_blank_text_and_boolean_revision_rejected(self):
        for key, change in [("schema", "other/v1"), ("purpose", "  "), ("revision", True)]:
            value = fixture();value[key] = change
            with self.subTest(key=key), self.assertRaises(T.ContractError): T.validate(value)

    def test_broken_source_task_and_item_refs_rejected(self):
        for change in (lambda v: v["items"][0]["source_refs"].append("ABSENT"), lambda v: v["tasks"][1]["depends_on"].append("ABSENT"), lambda v: v["tasks"][1]["item_refs"].append("ABSENT"), lambda v: v["items"][3]["blocks"].append("ABSENT")):
            value = fixture();change(value)
            with self.assertRaises(T.ContractError): T.validate(value)

    def test_nonunknown_claim_needs_source_and_cannot_author_block(self):
        for field, val in [("source_refs", []), ("blocks", ["T-REPAIR"])]:
            value = fixture();value["items"][0][field] = val
            with self.assertRaises(T.ContractError): T.validate(value)

    def test_parent_dependency_and_combined_cycles_rejected(self):
        value = fixture();row(value, "T-OUTCOME")["parent_id"] = "T-DISCOVER"
        with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture();row(value, "T-DISCOVER")["depends_on"] = ["T-INTEGRATE"]
        with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture();row(value, "T-INVENTORY")["depends_on"] = ["T-OUTCOME"]
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_expansion_and_split_need_explicit_structure(self):
        value = fixture();row(value, "T-OUTCOME")["boundary"]["cut"] = None
        with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture();row(value, "T-OUTCOME")["detail"] = "BOUNDED"
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_every_declared_obligation_is_accounted_for(self):
        value = fixture();value["coverage"].pop()
        with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture();value["coverage"].append(copy.deepcopy(value["coverage"][0]))
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_coverage_cannot_map_to_unrelated_task_or_empty_evidence(self):
        value = fixture();value["coverage"][1]["task_refs"] = ["T-REPAIR"]
        with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture();value["coverage"][0]["disposition"] = "EVIDENCE_REPORTED"
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_preserved_constraint_is_inherited_verbatim(self):
        value = fixture();text = value["items"][2]["statement"]
        for key in ("T-DISCOVER", "T-REPAIR", "T-INVENTORY"):
            self.assertIn("> " + text, T.render(value, key))
        value["preserve_refs"] = ["R-JOURNEY"]
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_unknown_blocks_only_affected_work_and_dependents(self):
        states = {r["task"]: r for r in T.frontier(fixture())["candidates"]}
        self.assertEqual(["U-CAUSE"], states["T-REPAIR"]["blocking_unknowns"])
        self.assertEqual(["U-CAUSE"], states["T-INTEGRATE"]["blocking_unknowns"])
        self.assertEqual([], states["T-INVENTORY"]["blocking_unknowns"])
        self.assertEqual([], states["T-DISCOVER"]["blocking_unknowns"])

    def test_unallocated_unknown_does_not_create_global_blocker(self):
        value = fixture();before = T.frontier(value)
        value["items"].append({"id":"U-NEW", "kind":"UNKNOWN", "statement":"Unallocated future question.", "source_refs":[], "blocks":[]})
        value["coverage"].append({"item_ref":"U-NEW", "disposition":"UNRESOLVED", "task_refs":[], "source_refs":[], "reason":"Not a prerequisite of current work."})
        after = T.frontier(value)
        self.assertEqual(before["candidates"], after["candidates"])
        self.assertIn("U-NEW", [r["item"] for r in after["unallocated"]])

    def test_complete_calculation_goal_remains_visible_while_model_is_reconstructed(self):
        result = T.frontier(fixture("single-model"))
        self.assertEqual("DESIGN_CANDIDATE", result["candidates"][0]["state"])
        self.assertIn("R-CALCULATION", [r["item"] for r in result["unallocated"]])

    def test_deferred_work_visible_and_not_presented_as_ready(self):
        result = T.frontier(fixture())
        self.assertIn("T-LATER", result["deferred"])
        self.assertNotIn("T-LATER", [r["task"] for r in result["candidates"]])
        with self.assertRaises(T.ContractError): T.render(fixture(), "T-LATER")

    def test_open_model_decision_cannot_be_relabelled_as_verified_fact(self):
        value = fixture("single-logic");value["tasks"][0]["decision_refs"] = ["F-TRACE"]
        with self.assertRaises(T.ContractError): T.validate(value)
        value = fixture("single-logic");cover = value["coverage"][-1]
        cover.update(disposition="EVIDENCE_REPORTED", source_refs=["S-CASE"])
        with self.assertRaises(T.ContractError): T.validate(value)

    def test_digest_is_canonical_content_and_changes_with_meaning(self):
        value = fixture();reordered = dict(reversed(list(value.items())))
        self.assertEqual(T.digest(value), T.digest(reordered))
        self.assertNotEqual(hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(), T.digest(value))
        changed = copy.deepcopy(value);changed["purpose"] += " amended"
        self.assertNotEqual(T.digest(value), T.digest(changed))

    def test_tools_leave_inputs_unchanged(self):
        value = fixture();before = copy.deepcopy(value)
        T.validate(value);T.frontier(value);T.render(value, "T-DISCOVER")
        after = copy.deepcopy(value);after["revision"] += 1;T.impact(value, after)
        self.assertEqual(before, value)

    def test_impact_scopes_correction_and_preserves_independent_work(self):
        before = fixture();after = copy.deepcopy(before);after["revision"] += 1
        next(i for i in after["items"] if i["id"]=="U-CAUSE")["statement"] += " New observed distinction."
        out = T.impact(before, after)
        self.assertIn("T-REPAIR", out["review_tasks"])
        self.assertIn("T-INTEGRATE", out["review_tasks"])
        self.assertIn("T-OUTCOME", out["integration_ancestors"])
        self.assertIn("T-INVENTORY", out["unchanged_candidates"])
        self.assertEqual([], out["authority_effects"])

    def test_coverage_change_is_substantive_impact(self):
        before = fixture();after = copy.deepcopy(before);after["revision"] += 1
        next(c for c in after["coverage"] if c["item_ref"]=="U-CAUSE")["disposition"] = "SUPERSEDED"
        self.assertIn("T-REPAIR", T.impact(before, after)["review_tasks"])

    def test_source_revision_change_reaches_affected_tasks(self):
        before = fixture();after = copy.deepcopy(before);after["revision"] += 1;after["sources"][0]["revision"] = "new"
        out = T.impact(before, after)
        self.assertEqual(["S-CASE"], out["changed_sources"])
        self.assertIn("T-INVENTORY", out["review_tasks"])

    def test_impact_requires_identity_and_increasing_revision(self):
        value = fixture()
        with self.assertRaises(T.ContractError): T.impact(value, value)
        other = copy.deepcopy(value);other.update(id="ANOTHER", revision=2)
        with self.assertRaises(T.ContractError): T.impact(value, other)

    def test_long_hierarchy_does_not_depend_on_python_recursion_depth(self):
        value = fixture("single-logic");template = value["tasks"][0];value["tasks"] = []
        for i in range(1050):
            task = copy.deepcopy(template);task.update(id=f"T{i}", parent_id=f"T{i-1}" if i else None, detail="BOUNDED" if i==1049 else "EXPANDED")
            value["tasks"].append(task)
        for cover in value["coverage"]: cover["task_refs"] = ["T0"]
        value["focus"] = ["T1049"]
        self.assertEqual(1050, len(T.validate(value)["tasks"]))


class CliAndIsolation(unittest.TestCase):
    def test_strict_duplicate_keys_and_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"bad.json"
            for text in ('{"id":1,"id":2}', '{"value":NaN}', '{"value":Infinity}'):
                path.write_text(text)
                self.assertNotEqual(0, run_cli("validate", "--map", path).returncode)

    def test_actual_validate_frontier_render_and_impact_cli(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);a=root/"a.json";b=root/"b.json";out=root/"task.md"
            value=fixture();a.write_text(json.dumps(value));value["revision"]+=1;b.write_text(json.dumps(value))
            for command,args in [("validate",["--map",a]),("frontier",["--map",a]),("render",["--map",a,"--task","T-DISCOVER","--out",out]),("impact",["--before",a,"--after",b])]:
                with self.subTest(command=command):
                    result=run_cli(command,*args);self.assertEqual(0,result.returncode,result.stderr)
            self.assertIn(T.digest(T.load(a)),out.read_text())

    def test_input_existing_output_and_symlink_are_protected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);path=root/"map.json";path.write_text(json.dumps(fixture()));original=path.read_bytes()
            self.assertNotEqual(0,run_cli("validate","--map",path,"--out",path).returncode)
            out=root/"exists.txt";out.write_text("retain me")
            self.assertNotEqual(0,run_cli("validate","--map",path,"--out",out).returncode)
            self.assertEqual("retain me",out.read_text());self.assertEqual(original,path.read_bytes())
            if hasattr(os,"symlink"):
                alias=root/"alias";alias.symlink_to(path)
                self.assertNotEqual(0,run_cli("validate","--map",path,"--out",alias).returncode)

    def test_invalid_input_creates_no_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);path=root/"bad.json";out=root/"out.json";path.write_text('{}')
            self.assertNotEqual(0,run_cli("validate","--map",path,"--out",out).returncode)
            self.assertFalse(out.exists())

    def test_package_executes_with_no_sibling_skills_or_repository(self):
        with tempfile.TemporaryDirectory() as td:
            isolated=Path(td)/"standalone";shutil.copytree(ROOT,isolated)
            result=run_cli("validate","--map",isolated/"examples/single-logic/task-map.json",script=isolated/"scripts/task_decomposer.py")
            self.assertEqual(0,result.returncode,result.stderr)
            result=run_cli("render","--map",isolated/"examples/single-logic/task-map.json","--task","T-TRACE",script=isolated/"scripts/task_decomposer.py")
            self.assertEqual(0,result.returncode,result.stderr)
            self.assertIn(T.digest(fixture("single-logic")),result.stdout)

    def test_missing_optional_dependency_is_an_observed_not_run(self):
        env=os.environ.copy();env["PYTHONPATH"]=""
        result=subprocess.run([sys.executable,"-S","-B",str(SCRIPT),"validate","--map",str(ROOT/"examples/single-logic/task-map.json")],text=True,capture_output=True,env=env)
        self.assertEqual(2,result.returncode);self.assertIn("NOT_RUN",result.stderr)


if __name__ == "__main__":
    unittest.main()
