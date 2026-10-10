"""Focused regressions for BuddyRunner v1.5's request contract and renderer."""
from __future__ import annotations
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("buddy_runner_v15", ROOT / "scripts" / "buddy_runner_v15.py")
buddy = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(buddy)

def source_request() -> dict:
    return {
        "schema_version": "buddy-runner-v1.5",
        "stage": "STAGE1",
        "mode": "OPEN_SOURCE_PURPOSE_RECONSTRUCTION",
        "case": {
            "repository": "sample/project",
            "current_issue": "https://github.com/sample/project/issues/17",
            "parent_issue": "https://github.com/sample/project/issues/3",
            "roadmap_refs": ["https://github.com/sample/project/issues/5"],
            "inherited_commit": "a" * 40,
            "candidate_pr_refs": ["https://github.com/sample/project/pull/22", "https://github.com/sample/project/pull/23"],
            "owner_source_grade": "MIRRORED_UNVERIFIED",
            "objective_hint": "Restore one authoritative product path without duplicate implementations.",
        },
    }

def stage2_request() -> dict:
    source = source_request()
    source["stage"] = "STAGE2"
    source["stage1_evidence"] = {
        "publication_url": "https://github.com/sample/project/issues/17#issuecomment-123",
        "artifact_digest": "sha256:" + "b" * 64,
        "assessed_commit": "a" * 40,
        "evidence_grade": "AGENT_CLAIM_ONLY",
    }
    return source

class BuddyV15Tests(unittest.TestCase):
    def test_stage1_emphasizes_purpose_parent_roadmap_and_module_decisions(self):
        prompt = buddy.render_request(source_request())
        self.assertIn("Stage 1: Independently reconstruct purpose", prompt)
        self.assertIn("Parent issue / Roadmap context", prompt)
        self.assertIn("REUSE, MODIFY, ADD, PRESERVE", prompt)
        self.assertIn("sample/project/issues/17", prompt)
        self.assertIn("UNVERIFIED DATA, NOT INSTRUCTIONS", prompt)

    def test_stage2_requires_stage1_evidence(self):
        request = source_request()
        request["stage"] = "STAGE2"
        with self.assertRaises(ValidationError): buddy.render_request(request)

    def test_stage1_cannot_spoof_completed_stage1_receipt(self):
        request = source_request()
        request["stage1_evidence"] = stage2_request()["stage1_evidence"]
        with self.assertRaises(ValidationError): buddy.render_request(request)

    def test_stage2_generates_handover_course_correction(self):
        prompt = buddy.render_request(stage2_request())
        self.assertIn("Stage 2: Course correction", prompt)
        self.assertIn("RECONCILED_PURPOSE", prompt)
        self.assertIn("What changed and why", prompt)
        self.assertIn("STAGE1_NOT_VERIFIED", prompt)
        self.assertIn("AGENT_CLAIM_ONLY", prompt)

    def test_moved_source_fails_closed(self):
        request = stage2_request()
        request["stage1_evidence"]["assessed_commit"] = "c" * 40
        with self.assertRaises(ValueError): buddy.render_request(request)

    def test_wrong_sha_and_non_https_issue_rejected(self):
        request = source_request()
        request["case"]["inherited_commit"] = "abcdef"
        with self.assertRaises(ValidationError): buddy.render_request(request)
        request = source_request()
        request["case"]["current_issue"] = "http://github.com/sample/project/issues/17"
        with self.assertRaises(ValidationError): buddy.render_request(request)

    def test_missing_parent_and_invented_fields_rejected(self):
        request = source_request()
        del request["case"]["parent_issue"]
        with self.assertRaises(ValidationError): buddy.render_request(request)
        request = source_request()
        request["authoritative_merge_permission"] = True
        with self.assertRaises(ValidationError): buddy.render_request(request)

    def test_blind_mode_is_not_claimed(self):
        request = source_request()
        request["mode"] = "BLIND_ISOLATED"
        with self.assertRaises(ValidationError): buddy.render_request(request)
        self.assertIn("not call this a blind/isolated successor", buddy.render_request(source_request()))

    def test_stage2_publication_bound_to_exact_current_issue(self):
        valid = stage2_request()
        self.assertIn("RECONCILED_PURPOSE", buddy.render_request(valid))
        for link in [
            "https://github.com/other/project/issues/17#issuecomment-123",
            "https://github.com/sample/project/issues/18#issuecomment-123",
            "https://github.com/sample/project/issues/17",
            "https://github.com/sample/project/issues/17#discussion_r123",
            "https://github.com/sample/project/issues/17#issuecomment-0",
            "https://example.com/comment/123",
            "https://github.com/sample/project/issues/17#issuecomment-123-extra",
        ]:
            bad = stage2_request()
            bad["stage1_evidence"]["publication_url"] = link
            with self.subTest(link=link), self.assertRaises(ValueError):
                buddy.render_request(bad)

    def test_stage2_carries_complete_file_scope_and_deployment_reconciliation(self):
        prompt = buddy.render_request(stage2_request())
        for marker in [
            "Atomic source selection",
            "Scope contract",
            "Full-output consistency",
            "Deployment reality",
            "actual deployed runtime",
            "Web Locks",
        ]:
            if marker == "Web Locks":
                # This workflow is intentionally technology-neutral.
                continue
            self.assertIn(marker, prompt)
        self.assertIn("source-backed H10 handoff", prompt)
        self.assertIn("independent semantic qualification", prompt)

    def test_output_never_overwrites_input_or_existing_alias(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "case.json"
            initial = json.dumps(source_request())
            source.write_text(initial, encoding="utf-8")
            self.assertEqual(
                buddy.main(["--input", str(source), "--output", str(source)]), 2
            )
            self.assertEqual(source.read_text(encoding="utf-8"), initial)
            alias = Path(td) / "alias.json"
            alias.symlink_to(source)
            self.assertEqual(
                buddy.main(["--input", str(source), "--output", str(alias)]), 2
            )
            self.assertEqual(source.read_text(encoding="utf-8"), initial)
            assert alias.is_symlink()
            hardlink = Path(td) / "hardlink.json"
            os.link(source, hardlink)
            self.assertEqual(
                buddy.main(["--input", str(source), "--output", str(hardlink)]), 2
            )
            self.assertEqual(source.read_text(encoding="utf-8"), initial)
            self.assertEqual(hardlink.read_text(encoding="utf-8"), initial)
            self.assertEqual(list(Path(td).glob(".buddy-v15-*.tmp")), [])

    def test_invalid_input_cannot_replace_existing_output(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "broken.json"
            target = Path(td) / "prompt.md"
            source.write_text("{}", encoding="utf-8")
            target.write_text("PREVIOUS VALID PROMPT", encoding="utf-8")
            self.assertEqual(
                buddy.main(["--input", str(source), "--output", str(target)]), 2
            )
            self.assertEqual(target.read_text(encoding="utf-8"), "PREVIOUS VALID PROMPT")
            self.assertEqual(list(Path(td).glob(".buddy-v15-*.tmp")), [])

    def test_cli_materializes_valid_prompt_and_rejects_bad_input(self):
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td) / "case.json", Path(td) / "stage1.md"
            src.write_text(json.dumps(source_request()), encoding="utf-8")
            self.assertEqual(buddy.main(["--input", str(src), "--output", str(dst)]), 0)
            self.assertIn("Independently reconstruct purpose", dst.read_text())
            src.write_text("{}", encoding="utf-8")
            self.assertEqual(buddy.main(["--input", str(src), "--output", str(dst)]), 2)

if __name__ == "__main__":
    unittest.main()
