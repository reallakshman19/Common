from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]

# V3.1's normative skill contract makes V2.5 and V3 historical-only.
# Following the repository migration, their workflow YAML files are absent.
# Never silently install placeholder old workflows to satisfy current CI.
# If a historical workflow is intentionally reinstated, reconcile it as an
# active required-check surface in this test and the branch-policy evidence.
RETIRED_PREMIGRATION_WORKFLOWS = (
    "engineering-pr-delivery-v2.5.yml",
    "engineering-pr-delivery-v3.yml",
)

# The existing live V3.1 workflow remains fully subject to terminality tests.
WORKFLOWS = {
    "engineering-pr-delivery-v3.1.yml": (
        "skills/engineering-pr-delivery-v3.1/*",
        "skills/two-pass-prompt-generator/*",
        "relay/*",
    ),
}


class RequiredCheckTerminalityTests(unittest.TestCase):
    def test_retired_workflows_cannot_be_silently_reactivated(self):
        """A re-added historical workflow needs explicit check-contract review."""
        for filename in RETIRED_PREMIGRATION_WORKFLOWS:
            with self.subTest(workflow=filename):
                self.assertFalse(
                    (ROOT / ".github/workflows" / filename).exists(),
                    "Historical workflow reappeared: reconcile its current "
                    "required-check terminality, source and branch-policy basis",
                )

    def test_relay_workflows_remain_valid_yaml(self):
        for filename in WORKFLOWS:
            with self.subTest(workflow=filename):
                text = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
                parsed = yaml.safe_load(text)
                self.assertIsInstance(parsed, dict)

    def test_relay_required_checks_always_instantiate_on_pull_requests(self):
        for filename in WORKFLOWS:
            with self.subTest(workflow=filename):
                text = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
                pull_request_block = text.split("pull_request:", 1)[1].split("push:", 1)[0]
                self.assertNotIn(
                    "paths:",
                    pull_request_block,
                    "PR-level path filters can leave required checks permanently Expected",
                )
                self.assertIn("Relay scope not applicable", text)
                self.assertIn("steps.relevance.outputs.relevant != 'true'", text)
                self.assertIn(
                    'git diff --name-only --no-renames "$BASE_SHA" "$HEAD_SHA"',
                    text,
                )
                self.assertIn(
                    "Path relevance could not be determined; running full validation.",
                    text,
                )

    def test_relay_required_checks_keep_real_validation_path_gated_inside_job(self):
        for filename, patterns in WORKFLOWS.items():
            with self.subTest(workflow=filename):
                text = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
                self.assertIn("fetch-depth: 0", text)
                self.assertIn("steps.relevance.outputs.relevant == 'true'", text)
                push_block = text.split("push:", 1)[1].split("permissions:", 1)[0]
                self.assertIn("paths:", push_block)
                for pattern in patterns:
                    self.assertIn(pattern, text)

                # The expensive Python setup must remain relevance-gated rather
                # than running on every unrelated PR.
                setup_match = re.search(
                    r"- name: Set up Python\n\s+if: ([^\n]+)",
                    text,
                )
                self.assertIsNotNone(setup_match)
                self.assertEqual(
                    "steps.relevance.outputs.relevant == 'true'",
                    setup_match.group(1).strip(),
                )


if __name__ == "__main__":
    unittest.main()
