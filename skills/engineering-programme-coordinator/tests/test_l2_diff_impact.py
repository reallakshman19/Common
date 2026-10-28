#!/usr/bin/env python3
from __future__ import annotations
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from l2_diff_impact import (
    canonical_digest,
    compile_changes,
    compile_source,
    exact_changed_paths,
    extract_precommitted_source,
    manifest_digest,
    validate_manifest,
    validate_source,
)
def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True,
    ).strip()
class L2DiffImpactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.repo, check=True)
        for path, body in {
            "skills/engineering-programme-coordinator/schemas/a.yaml": "type: object\n",
            "skills/engineering-programme-coordinator/scripts/a.py": "VALUE = 1\n",
            "skills/engineering-programme-coordinator/tests/test_a.py": "VALUE = 1\n",
            ".github/workflows/a.yml": "name: baseline\n",
        }.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "base"], cwd=self.repo, check=True, capture_output=True)
        self.base = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "skills/engineering-programme-coordinator/schemas/a.yaml").write_text(
            "type: object\nadditionalProperties: false\n",
            encoding="utf-8",
        )
        docs = self.repo / "docs" / "unmapped.md"
        docs.parent.mkdir(parents=True, exist_ok=True)
        docs.write_text("changed\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "candidate"], cwd=self.repo, check=True, capture_output=True)
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.source = self.make_source(self.base, self.head)
    def tearDown(self) -> None:
        self.tmp.cleanup()
    def make_source(self, base: str, head: str) -> dict:
        return {
            "schema_version": "L2_IMPACT_SOURCE_V1",
            "authority": "CANDIDATE_DIFF_SELECTION_CONTRACT",
            "identity": {
                "programme_or_parent_id": "TEST",
                "parent_ref": "issue://1",
                "task_id": "PRD-TEST-L2",
                "child_ref": "issue://2",
                "contract_version": "v1",
            },
            "candidate": {
                "repository": "example/repo",
                "pr_number": 1,
                "base_ref": "main",
                "base_sha": base,
                "head_ref": "candidate",
                "head_sha": head,
                "diff_mode": "NO_RENAMES_PATH_SET",
            },
            "rules": [
                {
                    "id": "L2-RULE-SCHEMA",
                    "path_glob": "skills/engineering-programme-coordinator/schemas/*",
                    "severity": "CRITICAL",
                    "impact_statement": "Schema impact.",
                    "expected_observation": "Schema evidence exists.",
                    "plausible_green_but_wrong": "Schema changed without relevant evidence.",
                    "evidence_requirement": {"id_prefix": "REQ-L2-SCHEMA", "method": "SCHEMA_CHECK"},
                },
                {
                    "id": "L2-RULE-RUNTIME",
                    "path_glob": "skills/engineering-programme-coordinator/scripts/*",
                    "severity": "HIGH",
                    "impact_statement": "Runtime impact.",
                    "expected_observation": "Runtime evidence exists.",
                    "plausible_green_but_wrong": "Runtime changed without relevant evidence.",
                    "evidence_requirement": {"id_prefix": "REQ-L2-RUNTIME", "method": "UNIT_TEST"},
                },
            ],
            "unknown_policy": {
                "severity": "HIGH",
                "expected_observation": "Unknown impact is reviewed.",
                "plausible_green_but_wrong": "Unknown impact disappears.",
                "evidence_requirement": {"id_prefix": "REQ-L2-UNKNOWN", "method": "MANUAL_REVIEW"},
            },
            "forbidden_outcomes": ["changed path omitted"],
            "non_goals": ["evidence ledger"],
        }
    def test_exact_diff_compiles_every_changed_path_once(self) -> None:
        manifest = compile_source(self.source, self.repo)
        rows = manifest["obligations"]
        self.assertEqual(2, len(rows))
        self.assertEqual(
            {"docs/unmapped.md", "skills/engineering-programme-coordinator/schemas/a.yaml"},
            {row["diff_observation"]["path"] for row in rows},
        )
        self.assertEqual(
            manifest["diff"]["changed_paths_digest"],
            canonical_digest([
                {"status": "A", "path": "docs/unmapped.md"},
                {"status": "M", "path": "skills/engineering-programme-coordinator/schemas/a.yaml"},
            ]),
        )
    def test_known_and_unmapped_unknown_are_distinct(self) -> None:
        manifest = compile_source(self.source, self.repo)
        by_path = {row["diff_observation"]["path"]: row for row in manifest["obligations"]}
        self.assertEqual("UNKNOWN_UNMAPPED", by_path["docs/unmapped.md"]["impact_classification"])
        self.assertEqual(
            "KNOWN",
            by_path["skills/engineering-programme-coordinator/schemas/a.yaml"]["impact_classification"],
        )
    def test_working_tree_mutation_cannot_change_exact_diff(self) -> None:
        before = compile_source(self.source, self.repo)
        (self.repo / "docs" / "unmapped.md").write_text("working tree only\n", encoding="utf-8")
        (self.repo / "untracked.txt").write_text("not committed\n", encoding="utf-8")
        self.assertEqual(before, compile_source(self.source, self.repo))
    def test_new_exact_head_changes_manifest(self) -> None:
        first = compile_source(self.source, self.repo)
        target = self.repo / "skills/engineering-programme-coordinator/scripts/a.py"
        target.write_text("VALUE = 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "next"], cwd=self.repo, check=True, capture_output=True)
        next_source = copy.deepcopy(self.source)
        next_source["candidate"]["head_sha"] = git(self.repo, "rev-parse", "HEAD")
        second = compile_source(next_source, self.repo)
        self.assertNotEqual(first["manifest_digest"], second["manifest_digest"])
        self.assertEqual(3, second["diff"]["changed_path_count"])
    def test_multiple_rules_are_unknown_ambiguous(self) -> None:
        source = copy.deepcopy(self.source)
        source["rules"].append({
            "id": "L2-RULE-SECOND-SCHEMA",
            "path_glob": "skills/engineering-programme-coordinator/schemas/*",
            "severity": "HIGH",
            "impact_statement": "Second schema impact.",
            "expected_observation": "Second schema evidence exists.",
            "plausible_green_but_wrong": "Second rule could hide ambiguity.",
            "evidence_requirement": {"id_prefix": "REQ-L2-SECOND-SCHEMA", "method": "MANUAL_REVIEW"},
        })
        row = compile_changes(
            source,
            [{"status": "M", "path": "skills/engineering-programme-coordinator/schemas/a.yaml"}],
        )[0]
        self.assertEqual("UNKNOWN_AMBIGUOUS", row["impact_classification"])
        self.assertEqual(["L2-RULE-SCHEMA", "L2-RULE-SECOND-SCHEMA"], row["matched_rule_ids"])
        self.assertEqual("MANUAL_REVIEW", row["evidence_required"]["method"])
    def test_unsupported_status_is_unknown_status(self) -> None:
        row = compile_changes(
            self.source,
            [{"status": "X", "path": "skills/engineering-programme-coordinator/schemas/a.yaml"}],
        )[0]
        self.assertEqual("UNKNOWN_STATUS", row["impact_classification"])
        self.assertIn("Unsupported diff status", row["unknown_reason"])
    def test_no_renames_mode_emits_delete_and_add(self) -> None:
        old_path = "skills/engineering-programme-coordinator/scripts/a.py"
        new_path = "skills/engineering-programme-coordinator/scripts/b.py"
        subprocess.run(["git", "mv", old_path, new_path], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "rename"], cwd=self.repo, check=True, capture_output=True)
        source = copy.deepcopy(self.source)
        source["candidate"]["base_sha"] = self.head
        source["candidate"]["head_sha"] = git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(
            [{"status": "D", "path": old_path}, {"status": "A", "path": new_path}],
            exact_changed_paths(source, self.repo),
        )
    def test_duplicate_rule_ids_are_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["rules"][1]["id"] = source["rules"][0]["id"]
        self.assertTrue(any("rule ids must be globally unique" in e for e in validate_source(source)))
    def test_duplicate_evidence_prefixes_are_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["rules"][1]["evidence_requirement"]["id_prefix"] = source["rules"][0]["evidence_requirement"]["id_prefix"]
        self.assertTrue(any("id prefixes must be globally unique" in e for e in validate_source(source)))
    def test_source_rejects_candidate_evidence_fields(self) -> None:
        source = copy.deepcopy(self.source)
        source["implementation_evidence"] = {"pass": True}
        self.assertTrue(validate_source(source))
    def test_source_rejects_reviewer_verdict_fields(self) -> None:
        source = copy.deepcopy(self.source)
        source["reviewer_verdict"] = "PASS"
        self.assertTrue(validate_source(source))
    def test_source_rejects_same_base_and_head(self) -> None:
        source = copy.deepcopy(self.source)
        source["candidate"]["head_sha"] = source["candidate"]["base_sha"]
        self.assertTrue(any("must differ" in e for e in validate_source(source)))
    def test_unbound_manifest_validation_fails_closed(self) -> None:
        manifest = compile_source(self.source, self.repo)
        self.assertTrue(any("source-bound exact-diff replay is required" in e for e in validate_manifest(manifest)))
    def test_generic_validator_requires_source_and_exact_repo(self) -> None:
        manifest = compile_source(self.source, self.repo)
        source_path = self.repo / "l2-source.yaml"
        manifest_path = self.repo / "l2-manifest.yaml"
        source_path.write_text(
            yaml.safe_dump(self.source, sort_keys=False),
            encoding="utf-8",
        )
        manifest_path.write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )
        unbound = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "validate.py"),
                "l2-impact-obligation-manifest",
                str(manifest_path),
            ],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, unbound.returncode)
        self.assertIn(
            "source-bound exact-diff replay is required",
            unbound.stdout,
        )
        bound = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "validate.py"),
                "l2-impact-obligation-manifest",
                str(manifest_path),
                "--l2-source",
                str(source_path),
                "--repo-root",
                str(self.repo),
            ],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, bound.returncode, bound.stdout + bound.stderr)
    def test_recomputed_tamper_digest_does_not_bypass_replay(self) -> None:
        manifest = compile_source(self.source, self.repo)
        manifest["obligations"][0]["claim"]["statement"] = "forged"
        manifest["manifest_digest"] = manifest_digest(manifest)
        self.assertTrue(any("fresh exact-diff replay" in e for e in validate_manifest(manifest, self.source, self.repo)))
    def test_all_requirements_are_impact_derived(self) -> None:
        manifest = compile_source(self.source, self.repo)
        self.assertTrue(all(row["evidence_required"]["independence"] == "IMPACT_DERIVED" for row in manifest["obligations"]))
    def test_authority_boundaries_do_not_emit_verdict_or_lifecycle(self) -> None:
        manifest = compile_source(self.source, self.repo)
        boundaries = manifest["authority_boundaries"]
        self.assertTrue(boundaries["consumes_candidate_diff"])
        for key, value in boundaries.items():
            if key != "consumes_candidate_diff":
                self.assertFalse(value, key)
    def test_manifest_schema_rejects_aggregate_pass(self) -> None:
        manifest = compile_source(self.source, self.repo)
        manifest["pass"] = True
        self.assertTrue(validate_manifest(manifest, self.source, self.repo))
    def test_extracts_real_fenced_issue_source(self) -> None:
        markdown = (
            "# Child\n\n"
            "## Precommitted L2 impact source\n\n"
            "```yaml\n"
            + yaml.safe_dump(self.source, sort_keys=False)
            + "```\n"
        )
        self.assertEqual(self.source, extract_precommitted_source(markdown))
    def test_duplicate_precommitted_heading_is_rejected(self) -> None:
        block = (
            "## Precommitted L2 impact source\n"
            "```yaml\n"
            + yaml.safe_dump(self.source, sort_keys=False)
            + "```\n"
        )
        with self.assertRaises(ValueError):
            extract_precommitted_source(block + block)
if __name__ == "__main__":
    unittest.main()
