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
        and "provider GET/identity" in s
        and "HOLD_REPOSITORY_IDENTITY" in s
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


if __name__ == "__main__":
    unittest.main()
