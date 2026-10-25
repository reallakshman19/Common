from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]

# V2.5/V3 CI workflows were retired. Assert the currently maintained V3.1
# workflow rather than requiring removed historic jobs to be recreated.
WORKFLOWS = {
    "engineering-pr-delivery-v3.1.yml": (
        "skills/engineering-pr-delivery-v3.1/*",
        "skills/two-pass-prompt-generator/*",
        "relay/*",
    ),
}


class RequiredCheckTerminalityTests(unittest.TestCase):
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
                # Scope only files changed by the PR, excluding unrelated
                # commits that landed on the base after the branch forked.
                self.assertIn('git merge-base "$BASE_SHA" "$HEAD_SHA"', text)
                self.assertIn(
                    'git diff --name-only --no-renames "$merge_base" "$HEAD_SHA"',
                    text,
                )
                self.assertNotIn(
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
