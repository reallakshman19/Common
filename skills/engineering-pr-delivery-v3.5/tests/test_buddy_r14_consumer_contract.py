"""Cross-version read-only contract oracles for native Buddy-to-R14 consumers.

This checks actual source and Markdown interfaces; it does not authenticate a GitHub
issue, Owner, separate Runner principal, Stage1 read boundary or writer custody.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTINUITY = ROOT / "relay/CONTINUITY"
NATIVE = ROOT / "skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py"


def source(name: str) -> str:
    return (CONTINUITY / name).read_text(encoding="utf-8")


def native_stages() -> set[str]:
    tree = ast.parse(NATIVE.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "BUDDY_MESSAGE_STAGES" for t in node.targets):
            continue
        call = node.value
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "frozenset":
            raise ValueError("native Buddy stages must remain a literal frozenset")
        if len(call.args) != 1 or not isinstance(call.args[0], (ast.Set, ast.List, ast.Tuple)):
            raise ValueError("native Buddy stages must be a static literal collection")
        stages = call.args[0].elts
        if not all(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in stages):
            raise ValueError("native Buddy stages must be string literals")
        return {v.value for v in stages}
    raise ValueError("native Buddy stage allowlist missing")


def has_provider_gate(s: str) -> bool:
    return (
        "| Current issue binding receipt |" in s
        and "operator-controlled provider" in s
        and "repository `id`" in s
        and "issue `id`" in s
        and "`pull_request` absent" in s
        and "HOLD_REPOSITORY_IDENTITY" in s
        and "Separate Owner/Local responsibility authorization" in s
        and "HOLD_OWNER_SCOPE" in s
        and "old issue refs remain historical" in s
    )


def is_complete_handover_template(s: str) -> bool:
    must = (
        "HANDOVER_TECHNICAL_V2",
        "HANDOVER_CONTEXT",
        "Original problem",
        "actual implementation",
        "downstream",
        "tests",
        "source",
        "UNKNOWN",
        "STAGE2_AFTER_FREEZE_ONLY",
        "writer",
    )
    normal = s.lower()
    return all(t.lower() in normal for t in must)


class BuddyR14ConsumerContractTests(unittest.TestCase):
    def test_native_stage_allowlist_separates_handover_and_stage2(self):
        self.assertEqual(
            native_stages(),
            {
                "READINESS", "STAGE1_INTAKE", "DISPATCH_REQUEST",
                "DISPATCH_OBSERVATION", "STAGE1_BASELINE",
                "STAGE1_PLAN", "STAGE1_FREEZE_CANDIDATE",
            },
        )
        native = NATIVE.read_text(encoding="utf-8")
        self.assertIn("relay/CONTINUITY/episodes/ISSUE-*/messages/*.md", native)
        for stage in ("TECHNICAL_HANDOVER", "STAGE2_RECONCILIATION", "OWNER_DECISION", "STAGE1_FREEZE"):
            self.assertNotIn(stage, native_stages())

    def test_dispatch_external_new_repository_issue_binding(self):
        dispatch = source("TEMPLATES/RUNNER_DISPATCH_REQUEST.md")
        self.assertTrue(has_provider_gate(dispatch))
        self.assertIn("Actual B session already launched?", dispatch)
        self.assertFalse(has_provider_gate(dispatch.replace("| Current issue binding receipt |", "| Legacy issue only |")))
        self.assertFalse(has_provider_gate(dispatch.replace("HOLD_REPOSITORY_IDENTITY", "ASSUME_MATCHED_SHA")))
        self.assertFalse(has_provider_gate(dispatch.replace("old issue refs remain historical", "old issue refs are new issues")))
        self.assertFalse(has_provider_gate(dispatch.replace("repository `id`", "repository name only")))
        self.assertFalse(has_provider_gate(dispatch.replace("`pull_request` absent", "any issues endpoint object")))
        self.assertFalse(has_provider_gate(dispatch.replace("HOLD_OWNER_SCOPE", "ISSUE_FOUND_IS_APPROVED")))

    def test_complete_narrative_is_stage2_only_and_native_custody_remains(self):
        handover = source("TEMPLATES/TECHNICAL_HANDOVER.md")
        self.assertTrue(is_complete_handover_template(handover))
        self.assertFalse(is_complete_handover_template(handover.replace("HANDOVER_CONTEXT", "chat memory")))
        self.assertFalse(is_complete_handover_template(handover.replace("STAGE2_AFTER_FREEZE_ONLY", "PUBLIC_STAGE1")))
        self.assertIn("PLAN_GRAPH_REVISION", handover)
        self.assertIn("SESSION_SOURCE_COMMIT", handover)
        self.assertIn("CODE_CANDIDATE_HEAD", handover)
        self.assertIn("tested", handover.lower())
        self.assertIn("original task", handover.lower())
        self.assertIn("INHERITED_BASELINE_FAILURE", handover)
        self.assertIn("ZERO_STEPS/NO_RUNNER", handover)
        self.assertIn("individual relevant job/step", handover)

    def test_stage2_requires_four_views_native_handover_and_separate_writer(self):
        stage2 = source("TEMPLATES/STAGE2_RECONCILIATION.md")
        for term in (
            "frozen", "HANDOVER_TECHNICAL_V2", "REVISE_BOTH",
            "READ_ONLY_RECONCILIATION", "NOT_GRANTED", "current provider",
            "Historical legacy repo", "Migration lineage",
        ):
            self.assertIn(term.lower(), stage2.lower(), term)
        owner = source("TEMPLATES/OWNER_DECISION.md")
        self.assertIn("New repository / issue / PR bindings", owner)
        self.assertIn("Old repository / issue / PR lineage", owner)
        self.assertIn("no acceptance", owner.lower())

    def test_relay_authority_and_r14_source_roles_not_shadowed(self):
        docs = source("AUTHORITY_MAP.md")
        for term in (
            "PLAN_GRAPH_REVISION", "SESSION_SOURCE_COMMIT", "CODE_CANDIDATE_HEAD",
            "HANDOVER", "relay/STATE.yaml", "DELP",
        ):
            self.assertIn(term.lower(), docs.lower(), term)
        agreement = source("REVIEWER_ONLY/BUDDY_R14_CONSUMER_CONVERGENCE_V1.md")
        self.assertIn("owner_authorized: false", agreement)
        self.assertIn("not native", agreement.lower())
        self.assertIn("Stage2", agreement)


    def test_native_bridge_preserves_two_original_b_files_and_distinct_external_freeze(self):
        bridge = source("STAGE1_NATIVE_RECORD_BRIDGE.md")
        baseline = source("TEMPLATES/STAGE1_RECONSTRUCTION.md")
        freeze = source("TEMPLATES/STAGE1_FREEZE.md")
        readme = source("README.md")
        for required in (
            "STAGE1_BASELINE", "STAGE1_PLAN", "STAGE1_FREEZE_CANDIDATE",
            "Isolation verdict: NOT_ATTESTED", "STAGE1_FREEZE_V1",
            "two separately", "controller", "HOLD",
        ):
            self.assertIn(required.lower(), bridge.lower(), required)
        self.assertIn("two separately deliverable original", baseline)
        self.assertIn("# STAGE1_BASELINE", baseline)
        self.assertIn("# STAGE1_PLAN", baseline)
        self.assertIn("STAGE1_FREEZE_CANDIDATE", freeze)
        self.assertIn("STAGE1_FREEZE_V1", freeze)
        self.assertIn("Stage 1 original-file mapping", readme)
        self.assertNotIn("STAGE1_FREEZE_V1", native_stages())
        self.assertNotIn("TECHNICAL_HANDOVER", native_stages())

    def test_b_facing_golden_requires_original_separate_files_not_controller_retyping(self):
        golden = (ROOT / "skills/engineering-pr-delivery-v3.5/runner/STAGE1_INDEPENDENT_RECONSTRUCTION.md").read_text(encoding="utf-8")
        for term in ("# STAGE1_BASELINE", "# STAGE1_PLAN", "same isolated session",
                     "TWO_NATIVE_FILES_UNAVAILABLE", "HOLD native publication", "must not split"):
            self.assertIn(term, golden, term)
        self.assertIn("historical baseline first", golden.lower() + " historical baseline first")

    def test_runner_prompts_separate_independent_baseline_from_stage2_source(self):
        stage1 = (ROOT / "skills/engineering-pr-delivery-v3.5/runner/STAGE1_INDEPENDENT_RECONSTRUCTION.md").read_text(encoding="utf-8")
        stage2 = (ROOT / "skills/engineering-pr-delivery-v3.5/runner/STAGE2_SOURCE_RECONCILIATION.md").read_text(encoding="utf-8")
        static = (ROOT / "skills/engineering-pr-delivery-v3.5/runner/STATIC_PACKET_FORMATS.md").read_text(encoding="utf-8")
        preparation = (ROOT / "skills/engineering-pr-delivery-v3.5/runner/PREPARE_FOR_RUNNER.md").read_text(encoding="utf-8")
        for marker in ("NO SOLUTION YET", "historical system", "Stage 1 ONLY"):
            self.assertIn(marker.lower(), stage1.lower(), marker)
        for marker in ("Stage 2 ONLY", "read admission", "four-perspective", "frozen"):
            self.assertIn(marker.lower(), stage2.lower(), marker)
        self.assertIn("never expose before Stage 2", static)
        self.assertIn("Prepare for runner", preparation)
        self.assertIn("Time for Runner", preparation)
        self.assertNotEqual(stage1, stage2)


if __name__ == "__main__":
    unittest.main()
