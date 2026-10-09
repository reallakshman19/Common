"""Regression: stacked PR CI cannot pass inherited frozen V3.2 scope debt.

This is a workflow contract test, not authorization to change the V3.2 code.
The canonical main guard is deliberately terminal when the four protected Buddy
paths are not already authorized by a merged, base-resident Owner amendment.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/engineering-pr-delivery-v3.5.yml"
FROZEN_GUARD = "skills/Local_PR_Deliverty_v1.1/scripts/frozen_tree_guard.py"


def both_frozen_lineage_gates_present(source: str) -> bool:
    return (
        source.count(FROZEN_GUARD) >= 2
        and 'PR_BASE_SHA: ${{ github.event.pull_request.base.sha }}' in source
        and 'python ' + FROZEN_GUARD + ' --base "$BASE_SHA" --head HEAD' in source
        and '\n          python ' + FROZEN_GUARD + ' --base "$MAIN_SHA" --head HEAD\n' in source
        and 'git fetch --no-tags origin +refs/heads/main:refs/remotes/origin/main' in source
        and 'git merge-base --is-ancestor "$MAIN_SHA" HEAD' in source
        and "Verify canonical-main frozen V3.2 authority" in source
        and "Verify base-pinned frozen V3.2 tree protection" in source
        and 'continue-on-error: true' not in source
    )


class CanonicalMainLineageGuardContractTests(unittest.TestCase):
    def test_actual_workflow_checks_stacked_delta_and_canonical_main_authority(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertTrue(both_frozen_lineage_gates_present(source))
        self.assertLess(source.index(' --base "$BASE_SHA" --head HEAD'), source.index(' --base "$MAIN_SHA" --head HEAD'))
        self.assertIn("Run provider issue-kind and migration-negative fixture regressions", source)
        self.assertLess(source.index("Verify V3.5 lineage metadata"), source.index("Verify canonical-main frozen V3.2 authority"))

    def test_stack_only_check_does_not_satisfy_authorization(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        mutated = source.replace('python ' + FROZEN_GUARD + ' --base "$MAIN_SHA" --head HEAD', 'echo stack-only')
        self.assertFalse(both_frozen_lineage_gates_present(mutated))

    def test_canonical_only_check_does_not_replace_stacked_delta(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        mutated = source.replace('python ' + FROZEN_GUARD + ' --base "$BASE_SHA" --head HEAD', 'echo main-only')
        self.assertFalse(both_frozen_lineage_gates_present(mutated))

    def test_cannot_silence_main_gate_or_trust_unfetched_base(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertFalse(both_frozen_lineage_gates_present(source.replace('git fetch --no-tags origin +refs/heads/main:refs/remotes/origin/main', 'echo main fetched')))
        self.assertFalse(both_frozen_lineage_gates_present(source.replace('git merge-base --is-ancestor "$MAIN_SHA" HEAD', 'true')))
        self.assertFalse(both_frozen_lineage_gates_present(source.replace(' --base "$MAIN_SHA" --head HEAD', ' --base "$MAIN_SHA" --head HEAD || true')))

    def test_frozen_v32_runtime_still_outside_this_stack(self):
        # This checks workflow guard intent, not the actual provider PR diff.
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('not just stacked PR delta', source)
        self.assertIn('canonical main has NEVER approved', source)


if __name__ == "__main__":
    unittest.main()
