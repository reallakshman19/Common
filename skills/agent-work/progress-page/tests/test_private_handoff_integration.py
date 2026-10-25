"""Guard existing Progress Page writer and private artifact-relay documentation.

These are documentation/source checks only: no Drive permission or real recipient
access is verified by tests. Do not put an Owner's actual private URL or folder ID
in this test or any public GitHub file.
"""
from pathlib import Path
import re
import unittest

AGENT = Path(__file__).resolve().parents[2]
PAGE = AGENT / "progress-page"


def read(relative):
    return (AGENT / relative).read_text(encoding="utf-8")


class HandoffIntegrationDocs(unittest.TestCase):
    def test_actual_bundled_progress_scripts(self):
        for name in ("pp_cli.py", "pp_check.py", "page_triggers.py", "pp_inputs.py"):
            with self.subTest(name=name):
                self.assertTrue((PAGE / "scripts" / name).is_file())

    def test_writer_checks_real_checkout_not_browsed_cli(self):
        prompt = read("progress-page/assets/ORACLE_ONBOARD_PROMPT.md")
        guide = read("progress-page/README.md")
        for text in (prompt, guide):
            self.assertIn("python tools/pp_cli.py --help", text)
            self.assertIn("python tools/pp_cli.py check", text)
            self.assertIn("scripts/pp_cli.py", text)
        self.assertIn("PAGE: PENDING", guide)
        self.assertIn("NOT_RUN", prompt)

    def test_owner_private_location_is_opaque_and_unverified(self):
        relay = read("ARTIFACT_RELAY.md")
        guide = read("progress-page/README.md")
        onboarding = read("progress-page/assets/ORACLE_ONBOARD_PROMPT.md")
        for text in (relay, guide, onboarding):
            self.assertIn("OWNER_PRIVATE_REF:HANDOFFS_PRIMARY", text)
            self.assertNotRegex(text, r"https?://drive[.]google[.]com/drive/folders/[A-Za-z0-9_-]+")
        self.assertIn("SHARING_NOT_VERIFIED", relay)
        self.assertIn("RECIPIENT_ACCESS_NOT_RUN", relay)
        self.assertIn("shared=true", relay)
        self.assertIn("do not change Drive ACLs".lower(), relay.lower())

    def test_owner_order_is_mandatory_and_sandbox_is_not_delivery(self):
        relay = read("ARTIFACT_RELAY.md")
        guide = read("progress-page/README.md")
        onboarding = read("progress-page/assets/ORACLE_ONBOARD_PROMPT.md")
        reviewer = read("independent-review/SKILL.md")
        self.assertIn("**1 — FIRST**", relay)
        self.assertIn("**2 — NEXT**", relay)
        self.assertIn("**Mandatory:** Every material artifact", relay)
        self.assertIn("**FALLBACK — NOT DELIVERED**", relay)
        self.assertIn("Option 1 FIRST", reviewer)
        self.assertIn("Option 2 NEXT", reviewer)
        self.assertIn("**Option 1 FIRST**", guide)
        self.assertIn("**Option 2 NEXT**", guide)
        self.assertIn("**1 — Common public-safe relay", onboarding)
        self.assertIn("**2 — Owner-designated Google Drive", onboarding)
        for text in (relay, guide, onboarding, reviewer):
            with self.subTest(origin=text[:42]):
                self.assertIn("LOCAL_ONLY / NOT_TRANSFERRED", text)
        self.assertIn("for either", relay.lower())
        self.assertIn("Owner-designated Google Drive", relay)

    def test_receiver_and_reviewer_each_prove_bytes(self):
        relay = read("ARTIFACT_RELAY.md")
        reviewer = read("independent-review/SKILL.md")
        self.assertIn("BYTES_VERIFIED", relay)
        self.assertIn("their own", relay)
        self.assertIn("reviewer's", reviewer)
        self.assertIn("NOT_RECEIVED", reviewer)
        self.assertIn("native issue/PR", relay)
        self.assertIn("not** independent approval".lower(), relay.lower())

    def test_no_secret_custody_locations_hardcoded(self):
        paths = (
            "ARTIFACT_RELAY.md",
            "progress-page/README.md",
            "progress-page/assets/ORACLE_ONBOARD_PROMPT.md",
            "independent-review/SKILL.md",
        )
        for path in paths:
            with self.subTest(path=path):
                s = read(path)
                self.assertNotRegex(s, r"https?://drive[.]google[.]com/drive/folders/[A-Za-z0-9_-]+")


if __name__ == "__main__":
    unittest.main()
