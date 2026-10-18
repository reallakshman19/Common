"""Synthetic workflow oracles; no fixture grants real source or execution authority."""
from copy import deepcopy
import json
import unittest
from jsonschema import Draft202012Validator
from support import ROOT, request, reconstruction, source
from relay_evidence import digest
from relay_workflow import assess


def overlay(base, patch):
    result = deepcopy(base)
    for key, value in patch.items():
        result[key] = overlay(result[key], value) if (
            isinstance(value, dict) and isinstance(result.get(key), dict)) else deepcopy(value)
    return result


class GoldenTests(unittest.TestCase):
    def test_synthetic_scenarios_keep_declared_expected_results(self):
        paths = sorted((ROOT / "examples/golden").glob("*.json"))
        self.assertGreaterEqual(len(paths), 10, "scenario corpus must be present")
        schemas = {name: json.loads((ROOT / "schemas" / (name + ".schema.json")).read_text())
                   for name in ("request", "reconstruction", "progress")}
        for schema in schemas.values():
            Draft202012Validator.check_schema(schema)
        for path in paths:
            with self.subTest(scenario=path.name):
                item = json.loads(path.read_text())
                self.assertEqual(item["basis"], "SYNTHETIC_REFERENCE_NOT_PROJECT_AUTHORITY")
                self.assertTrue(item["human_checks"], "semantic review remains explicit")
                case = overlay(request(), item.get("request_patch", {}))
                rec = overlay(reconstruction(), item.get("record_patch", {}))
                Draft202012Validator(schemas["request"]).validate(case)
                Draft202012Validator(schemas["reconstruction"]).validate(rec)
                if "progress" in case:
                    Draft202012Validator(schemas["progress"]).validate(case["progress"])
                kwargs = {}
                if "owner_source" in item:
                    original = item["owner_source"]
                    body = original["body"]
                    # This trusted-host seam exists only inside the synthetic test.
                    event = {"ref": case["issue"] + "#issuecomment-2",
                             "subject": digest(rec), "digest": digest(body)}
                    kwargs["reader"] = lambda ref, body=body, kinds=original["kinds"]: source(body, kinds=kinds)
                    if item.get("approval"):
                        kwargs["approval"] = event
                    if item.get("task"):
                        kwargs["task"] = event
                result = assess(case, rec, **kwargs)
                for field, expected in item["expected"].items():
                    value = result
                    for part in field.split("."):
                        value = value[part]
                    self.assertEqual(value, expected, field)
                self.assertFalse(result["agent_invoked"])
                self.assertFalse(result["workflow_executed"])
                self.assertFalse(result["coding_authorized"])
                self.assertEqual(result["semantic_assessment"], "NOT_MACHINE_VERIFIED")


if __name__ == "__main__":
    unittest.main()
