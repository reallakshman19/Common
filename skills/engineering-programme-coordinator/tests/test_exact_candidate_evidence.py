#!/usr/bin/env python3
from __future__ import annotations
import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from coordlib import load_yaml
from exact_candidate_evidence import (
    canonical_digest,
    compile_source,
    extract_precommitted_source,
    object_digest,
    validate_ledger,
    validate_ledger_shape,
    validate_source,
)

SOURCE_PATH = ROOT / "references" / "p2-s4-evidence-source.yaml"
LEDGER_PATH = ROOT / "references" / "p2-s4-evidence-ledger.yaml"

class ExactCandidateEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = load_yaml(SOURCE_PATH)
        self.ledger = load_yaml(LEDGER_PATH)

    def test_retained_denominator_is_closed(self) -> None:
        compiled = compile_source(self.source, REPO_ROOT)
        self.assertEqual(13, compiled["denominator"]["obligation_count"])
        self.assertEqual(13, compiled["denominator"]["requirement_count"])
        self.assertEqual(13, len(compiled["records"]))
        requirements = [req for row in compiled["records"] for req in row["requirements"]]
        self.assertEqual(13, len(requirements))
        self.assertEqual(self.ledger, compiled)

    def test_missing_evidence_remains_visible(self) -> None:
        compiled = compile_source(self.source, REPO_ROOT)
        requirements = [req for row in compiled["records"] for req in row["requirements"]]
        empty = [req for req in requirements if not req["evidence_items"]]
        self.assertEqual(9, len(empty))
        self.assertEqual(9, compiled["accounting"]["requirements_without_evidence"])
        self.assertEqual(9, compiled["accounting"]["obligations_without_evidence"])

    def test_retained_real_evidence_count_is_four(self) -> None:
        compiled = compile_source(self.source, REPO_ROOT)
        self.assertEqual(4, compiled["accounting"]["evidence_item_count"])
        self.assertEqual(4, compiled["accounting"]["requirements_with_evidence"])
        self.assertEqual(4, compiled["accounting"]["obligations_with_evidence"])

    def test_all_evidence_binds_exact_candidate(self) -> None:
        compiled = compile_source(self.source, REPO_ROOT)
        candidate = compiled["candidate"]["sha"]
        items = [
            item
            for row in compiled["records"]
            for req in row["requirements"]
            for item in req["evidence_items"]
        ]
        self.assertTrue(items)
        self.assertTrue(all(item["candidate_sha"] == candidate for item in items))

    def test_unknown_requirement_submission_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        item = copy.deepcopy(source["evidence_items"][0])
        item["evidence_id"] = "EVID-P2S4-UNKNOWN-REQ"
        item["requirement_id"] = "REQ-DOES-NOT-EXIST"
        source["evidence_items"].append(item)
        with self.assertRaisesRegex(ValueError, "undeclared requirement"):
            compile_source(source, REPO_ROOT)

    def test_wrong_evidence_method_fails_closed(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_items"][0]["method"] = "UNIT_TEST"
        with self.assertRaisesRegex(ValueError, "expects method"):
            compile_source(source, REPO_ROOT)

    def test_stale_candidate_evidence_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_items"][0]["candidate_sha"] = "a" * 40
        errors = validate_source(source)
        self.assertTrue(any("candidate_sha must equal source candidate sha" in e for e in errors), errors)

    def test_duplicate_evidence_id_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        item = copy.deepcopy(source["evidence_items"][0])
        item["requirement_id"] = source["evidence_items"][1]["requirement_id"]
        item["method"] = source["evidence_items"][1]["method"]
        source["evidence_items"].append(item)
        errors = validate_source(source)
        self.assertTrue(any("evidence ids must be globally unique" in e for e in errors), errors)

    def test_multiple_evidence_items_for_one_requirement_are_preserved(self) -> None:
        source = copy.deepcopy(self.source)
        item = copy.deepcopy(source["evidence_items"][0])
        item["evidence_id"] = "EVID-P2S4-SCHEMA-LEDGER-SECOND"
        item["refs"] = ["evidence://second"]
        source["evidence_items"].append(item)
        compiled = compile_source(source, REPO_ROOT)
        req = next(
            req
            for row in compiled["records"]
            for req in row["requirements"]
            if req["requirement_id"] == item["requirement_id"]
        )
        self.assertEqual(2, len(req["evidence_items"]))
        self.assertEqual(5, compiled["accounting"]["evidence_item_count"])
        self.assertEqual(4, compiled["accounting"]["requirements_with_evidence"])

    def test_manifest_declared_digest_mismatch_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["manifests"]["l0"]["digest"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "source-declared digest"):
            compile_source(source, REPO_ROOT)

    def test_manifest_content_tamper_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            for layer in ("l0", "l1", "l2"):
                rel = self.source["manifests"][layer]["path"]
                target = repo / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPO_ROOT / rel, target)
            l0 = repo / self.source["manifests"]["l0"]["path"]
            text = l0.read_text(encoding="utf-8").replace(
                "one_primary_outcome:",
                "one_primary_outcome: tampered #",
                1,
            )
            l0.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "manifest_digest"):
                compile_source(self.source, repo)

    def test_source_candidate_must_equal_l2_candidate(self) -> None:
        source = copy.deepcopy(self.source)
        source["candidate"]["ref"] = "wrong-ref"
        with self.assertRaisesRegex(ValueError, "exactly equal L2 candidate identity"):
            compile_source(source, REPO_ROOT)

    def test_removed_obligation_cannot_self_certify(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"] = ledger["records"][:-1]
        ledger["denominator"]["obligation_count"] -= 1
        ledger["denominator"]["requirement_count"] -= 1
        ledger["accounting"]["obligations_without_evidence"] -= 1
        ledger["accounting"]["requirements_without_evidence"] -= 1
        ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
        errors = validate_ledger(ledger, self.source, REPO_ROOT)
        self.assertTrue(errors)
        self.assertTrue(
            any(
                "manifest obligation_count does not match records" in e
                or "fresh denominator replay" in e
                for e in errors
            ),
            errors,
        )

    def test_removed_requirement_cannot_self_certify(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        row = next(row for row in ledger["records"] if not row["requirements"][0]["evidence_items"])
        row["requirements"] = []
        ledger["denominator"]["requirement_count"] -= 1
        layer = row["layer"].lower()
        ledger["manifests"][layer]["requirement_count"] -= 1
        ledger["accounting"]["requirements_without_evidence"] -= 1
        ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
        errors = validate_ledger(ledger, self.source, REPO_ROOT)
        self.assertTrue(errors)

    def test_tampered_evidence_candidate_fails_shape_semantics(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        item = next(
            item
            for row in ledger["records"]
            for req in row["requirements"]
            for item in req["evidence_items"]
        )
        item["candidate_sha"] = "a" * 40
        ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
        errors = validate_ledger_shape(ledger)
        self.assertTrue(any("candidate_sha must equal ledger candidate sha" in e for e in errors), errors)

    def test_accounting_tamper_rejected(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["accounting"]["requirements_with_evidence"] = 13
        ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
        errors = validate_ledger_shape(ledger)
        self.assertTrue(any("accounting must exactly equal" in e for e in errors), errors)

    def test_unbound_ledger_validation_fails_closed(self) -> None:
        errors = validate_ledger(self.ledger)
        self.assertTrue(any("source-bound denominator replay is required" in e for e in errors), errors)

    def test_generic_validator_requires_source_and_repo_basis(self) -> None:
        unbound = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate.py"),
                "exact-candidate-evidence-ledger",
                str(LEDGER_PATH),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, unbound.returncode)
        self.assertIn("source-bound denominator replay is required", unbound.stdout)

        bound = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate.py"),
                "exact-candidate-evidence-ledger",
                str(LEDGER_PATH),
                "--evidence-source",
                str(SOURCE_PATH),
                "--repo-root",
                str(REPO_ROOT),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, bound.returncode, bound.stdout + bound.stderr)

    def test_recomputed_tamper_digest_does_not_bypass_replay(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["claim_type"] = "AUTHORITY"
        ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
        errors = validate_ledger(ledger, self.source, REPO_ROOT)
        self.assertTrue(errors)
        self.assertTrue(
            any(
                "manifest obligation_count does not match records" in e
                or "fresh denominator replay" in e
                for e in errors
            ),
            errors,
        )

    def test_source_schema_rejects_verdict_fields(self) -> None:
        for field, value in [
            ("state", "VERIFIED"),
            ("verdict", "PASS"),
            ("pass", True),
            ("waiver", "accepted"),
        ]:
            source = copy.deepcopy(self.source)
            source[field] = value
            self.assertTrue(validate_source(source), field)

    def test_ledger_schema_rejects_verdict_fields(self) -> None:
        for field, value in [
            ("state", "VERIFIED"),
            ("verdict", "PASS"),
            ("pass", True),
            ("waiver", "accepted"),
            ("not_applicable", True),
        ]:
            ledger = copy.deepcopy(self.ledger)
            ledger[field] = value
            ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
            self.assertTrue(validate_ledger_shape(ledger), field)

    def test_authority_boundaries_are_accounting_only(self) -> None:
        boundaries = self.ledger["authority_boundaries"]
        self.assertTrue(boundaries["consumes_obligation_manifests"])
        self.assertTrue(boundaries["consumes_exact_candidate_evidence"])
        for key, value in boundaries.items():
            if key not in {"consumes_obligation_manifests", "consumes_exact_candidate_evidence"}:
                self.assertFalse(value, key)

    def test_source_digest_is_frozen(self) -> None:
        self.assertEqual(
            "41a70b1580aadc31c278d9659ef785e9ef73eccc7d00ae7e4f4e98761910bd8b",
            canonical_digest(self.source),
        )

    def test_extracts_precommitted_issue_source(self) -> None:
        import yaml
        markdown = (
            "# Child\n\n"
            "## Precommitted exact-candidate evidence source\n\n"
            "```yaml\n"
            + yaml.safe_dump(self.source, sort_keys=False)
            + "```\n"
        )
        self.assertEqual(self.source, extract_precommitted_source(markdown))

    def test_duplicate_precommitted_heading_rejected(self) -> None:
        block = (
            "## Precommitted exact-candidate evidence source\n"
            "```yaml\n{}\n```\n"
        )
        with self.assertRaises(ValueError):
            extract_precommitted_source(block + block)

if __name__ == "__main__":
    unittest.main()
