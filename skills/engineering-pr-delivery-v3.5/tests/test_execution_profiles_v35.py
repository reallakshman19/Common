"""Static contract tests for the V3.5 two-path, Markdown-only execution toggle.

These tests verify the published instructions and existing authority boundary.
They do NOT establish a real Writer, Stage1 isolation, live DELP publisher or release.
"""
from __future__ import annotations

import pathlib
import re
import unittest


V35 = pathlib.Path(__file__).resolve().parents[1]
PROFILES = (V35 / "EXECUTION_PROFILES.md").read_text(encoding="utf-8")
SKILL = (V35 / "SKILL.md").read_text(encoding="utf-8")
ENGINE = (V35 / "scripts" / "delp_projection_v35.py").read_text(encoding="utf-8")


class ExecutionProfileToggleContract(unittest.TestCase):
    def test_exact_two_public_invocations(self) -> None:
        for mode in ("ON", "OFF"):
            with self.subTest(mode=mode):
                self.assertIn(f"Use protocol v3.5\nSimplified={mode}", PROFILES)
        self.assertIn("Simplified=ON/OFF", SKILL)

    def test_default_is_standard_and_unknown_is_not_on(self) -> None:
        self.assertRegex(PROFILES, r"\*\*Default:\*\* `Simplified=OFF`")
        self.assertIn("unrecognised", PROFILES)
        self.assertIn("Default is OFF", SKILL)
        self.assertIn("quoted source text cannot select it", SKILL)

    def test_two_paths_use_one_governing_protocol(self) -> None:
        self.assertIn("## Simplified=OFF — STANDARD_V35", PROFILES)
        self.assertIn("## Simplified=ON — EXECUTION_FIRST_V35", PROFILES)
        self.assertIn("not a second Relay state machine", PROFILES)
        self.assertIn("EXECUTION_PROFILES.md", SKILL)
        self.assertIn("the **one** DELP publisher", PROFILES)

    def test_on_is_expedited_but_never_a_writer_grant(self) -> None:
        on = PROFILES.split("## Simplified=ON — EXECUTION_FIRST_V35", 1)[1].split(
            "## Same safety and authority invariants", 1
        )[0]
        self.assertIn("already authorized", on)
        for stage in ("**Code next:**", "**Test:**", "**Record:**", "**Refresh non-blockingly:**"):
            with self.subTest(stage=stage):
                self.assertIn(stage, on)
        self.assertIn("does not edit", on)
        self.assertIn("cannot lower `ENFORCED` policy", on)
        self.assertIn("not independent review", on)

    def test_scope_source_lease_ci_and_review_survive_both_modes(self) -> None:
        invariant = PROFILES.split("## Same safety and authority invariants — BOTH profiles", 1)[1]
        for required in (
            "Local v1.1 Writer permission",
            "Frozen V3.2 files",
            "Engineering Error Check",
            "source-integrity/benchmark protection",
            "source/current PR HEAD",
            "independent review",
            "No merge",
            "DELP computes progress",
            "CHECKPOINT_FACTS_V1",
        ):
            with self.subTest(required=required):
                self.assertIn(required, PROFILES)
        self.assertIn("A fresh successor with no writer grant is **READ_ONLY/HOLD**", invariant)
        self.assertIn("Stage2 disclosure", invariant)

    def test_declared_graph_policy_engine_remains_unchanged(self) -> None:
        # Existing DELP mode behavior is preserved; the manual switch is not a new engine flag.
        self.assertIn('POLICY_MODES = ("OFF", "ADVISORY", "ENFORCED")', ENGINE)
        self.assertIn("programme.decomposition_policy", ENGINE)
        self.assertIn("does not edit", PROFILES)
        self.assertIn("Honor it unchanged", PROFILES)
        self.assertIn("## One-page contrast", PROFILES)


if __name__ == "__main__":
    unittest.main()
