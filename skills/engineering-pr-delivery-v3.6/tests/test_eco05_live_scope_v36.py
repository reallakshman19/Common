"""Step-1 ECO-05 live scope RED tests. Fake GitHub client ONLY; never connect.

Owner consent #409 comment 6244462145 is limited to disposable #426,
title and scoreboard independently. The production writer must stay OFF
unless that exact scope is presented and verified.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publisher_v36 as pu
import lifecycle_v36 as lc

REPO = "reallakshman19/Common"
ISSUE = 426
TITLE = "[TEST] V36-ECO-05 live write demonstration target (disposable)"
ORIGINAL_BODY = ("[OTM · acting TeamCoordinator] Disposable test issue. Sole purpose: "
                 "exact-scope live demonstration of V36-ECO-05 (title + scoreboard "
                 "surfaces only), per Owner consent relayed on #409. "
                 "No real work is tracked here. Close after the demonstration.")
CONSENT = (
    '[OTM · acting TeamCoordinator] **Owner decision recorded (relayed from Owner chat, '
    '18 Oct 06:5x +04:00):** Owner words: "go ahead. Non critical project, '
    'you are authorized on my behalf." This answers all three pending live steps:\n\n'
    '1. **ECO-05 live write:** exact scope = disposable test issue #426 only; '
    'surfaces = title + scoreboard only; allow_write on that one issue; nothing else.\n'
    '2. **ECO-06 / ECO-08 live participation:** authorized; '
    'ECO-08 pilot proceeds with Common coder 6ad3b9ce as the participating agent.\n'
    '3. **#401 admission:** authorized.\n\n'
    'OTM runs these under delegation CL #1 6238268372 plus this consent; '
    'independent PASS still required before any merge. '
    'Next: WP sent to Common coder (tab-3).'
)
CONSENT_URL = f"https://github.com/{REPO}/issues/409#issuecomment-6244462145"
NEW_TITLE = "[ECO-05 DEMO] " + TITLE
SCORE_TEXT = ("ECO-05 TEST ONLY — simulated scoreboard surface; "
              "E/attestation/Owner acceptance NOT_EVALUATED; not a work plan.")


class FakeNative(pu.GithubClient):
    """isinstance(..., GithubClient) is true, but request never touches HTTP."""
    def __init__(self):
        super().__init__(REPO, token=None)
        self.issue = {"number": ISSUE, "html_url": f"https://github.com/{REPO}/issues/{ISSUE}",
                      "title": TITLE, "body": ORIGINAL_BODY, "labels": [],
                      "state": "open"}
        self.comment = {"id": 6244462145, "html_url": CONSENT_URL,
                        "body": CONSENT, "user": {"login": "reallakshman19"}}
        self.operations = []
        self.corrupt_readback = False
        self.fail_patch = False
        self.corrupt_body_readback = False
        self.race_before_patch = False
    def request(self, method, endpoint, body=None):
        self.operations.append((method, endpoint, copy.deepcopy(body)))
        if method == "GET" and endpoint == "/issues/comments/6244462145":
            return copy.deepcopy(self.comment)
        if method == "GET" and endpoint == "/issues/426":
            return copy.deepcopy(self.issue)
        if method == "PATCH" and endpoint == "/issues/426":
            if self.fail_patch:
                raise lc.ContractError("fake 503 after attempted PATCH")
            if set(body) not in ({"title"}, {"body"}):
                raise AssertionError("unexpected multi-surface PATCH")
            if self.race_before_patch:
                # Models the non-atomic gap AFTER second GET and BEFORE PATCH.
                self.issue["body"] += "\nlate concurrent Owner edit"
            self.issue.update(body)
            if self.corrupt_readback:
                self.issue["title"] = "concurrent Owner title"
            if self.corrupt_body_readback:
                self.issue["body"] += "\nprovider readback differs"
            return copy.deepcopy(self.issue)
        raise AssertionError(f"UNAUTHORISED provider operation: {method} {endpoint}")


def prepare(client, surface):
    consent_pin = pu.disposable_consent_pin(client)
    proposal = pu.disposable_demo_projection(
        client.request("GET", "/issues/426"), surface=surface,
        consent_pin=consent_pin,
        title=NEW_TITLE if surface == "title" else None,
        scoreboard_region=SCORE_TEXT if surface == "scoreboard" else None,
    )
    opts = {"confirm_scope": f"{REPO}#426", "allow_write": True,
            "authorized_surfaces": frozenset({surface}),
            "authorized_targets": frozenset({("issue", 426)}),
            "demo_authority": CONSENT_URL}
    return proposal, opts


class DisposableScopeTests(unittest.TestCase):
    def test_default_native_writer_still_denies_writes_without_exact_demo_authority(self):
        client = FakeNative()
        proposed, opts = prepare(client, "title")
        opts.pop("demo_authority")
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(proposed, client, **opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_exact_disposable_target_only_no_pr_parent_or_other_issue(self):
        client = FakeNative()
        proposed, opts = prepare(client, "title")
        for kind, number in (("pr", 426), ("issue", 409), ("issue", 427)):
            with self.subTest(kind=kind, number=number):
                bad = copy.deepcopy(proposed)
                bad["changes"][0]["kind"] = kind
                bad["changes"][0]["number"] = number
                with self.assertRaises(lc.ContractError):
                    pu.apply_projection(bad, client, **opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_no_fixture_plan_label_or_unrelated_surface_is_authorised(self):
        client = FakeNative()
        title, opts = prepare(client, "title")
        self.assertNotIn("label_sha", title)
        self.assertNotIn("plan", title)
        for surface in ("namespace", "labels"):
            with self.subTest(surface=surface):
                denied = dict(opts, authorized_surfaces=frozenset({surface}))
                with self.assertRaises(lc.ContractError):
                    pu.apply_projection(title, client, **denied)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_consent_comment_drift_blocks_before_any_patch(self):
        client = FakeNative()
        proposed, opts = prepare(client, "title")
        client.comment["body"] += "\npermission rescinded"
        result = pu.apply_projection(proposed, client, **opts)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["applied"], 0)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_title_then_scoreboard_get_verified_separate_and_replay_zero(self):
        client = FakeNative()
        title, opts = prepare(client, "title")
        result = pu.apply_projection(title, client, **opts)
        self.assertEqual((result["status"], result["applied"]), ("VERIFIED", 1))
        self.assertEqual(client.issue["title"], NEW_TITLE)
        self.assertEqual(client.issue["body"], ORIGINAL_BODY)
        writes = [op for op in client.operations if op[0] == "PATCH"]
        self.assertEqual(writes, [("PATCH", "/issues/426", {"title": NEW_TITLE})])
        again = pu.apply_projection(title, client, **opts)
        self.assertEqual((again["status"], again["applied"]), ("VERIFIED", 0))

        board, board_opts = prepare(client, "scoreboard")
        applied = pu.apply_projection(board, client, **board_opts)
        self.assertEqual((applied["status"], applied["applied"]), ("VERIFIED", 1))
        self.assertTrue(client.issue["body"].startswith(ORIGINAL_BODY))
        self.assertEqual(client.issue["labels"], [])
        replay = pu.apply_projection(board, client, **board_opts)
        self.assertEqual((replay["status"], replay["applied"]), ("VERIFIED", 0))
        self.assertEqual(len([op for op in client.operations if op[0] == "PATCH"]), 2)

    def test_unexpected_owner_edit_blocks_and_never_restores_body(self):
        client = FakeNative()
        # Simulate previously GET-verified title; this test isolates a later
        # Owner body edit without issuing any fake or real PATCH.
        client.issue["title"] = NEW_TITLE
        proposal, opts = prepare(client, "scoreboard")
        client.issue["body"] += "\nOwner added text"
        result = pu.apply_projection(proposal, client, **opts)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("Owner added text", client.issue["body"])
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_manually_forged_title_or_board_cannot_bypass_builder(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        forged = copy.deepcopy(proposal)
        forged["changes"][0]["after"] = "[ACCEPTED] forged success"
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(forged, client, **opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

        # A pure managed-region replacement is not enough: demo-only semantics
        # must be enforced in the writer, even for an untrusted direct caller.
        client.issue["title"] = NEW_TITLE
        board, board_opts = prepare(client, "scoreboard")
        forged_board = copy.deepcopy(board)
        forged_board["changes"][0]["after_body"] = (
            pu.scoreboard_body_change(
                client.issue, "APPROVED 100% — arbitrary forged claims",
                parent_number=426
            )["after_body"]
        )
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(forged_board, client, **board_opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_scoreboard_requires_get_verified_title_first(self):
        client = FakeNative()
        board, opts = prepare(client, "scoreboard")
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(board, client, **opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_patch_throws_without_false_verified(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        client.fail_patch = True
        result = pu.apply_projection(proposal, client, **opts)
        self.assertIn(result["status"], ("UNCERTAIN", "PARTIAL"))
        self.assertFalse(result["complete"])
        self.assertEqual(result["applied"], 0)
        self.assertTrue(result["pending_surfaces"])
        self.assertTrue(result["attempted_surfaces"])
        self.assertEqual(len([op for op in client.operations if op[0] == "PATCH"]), 1)

    def test_concurrent_edit_after_second_get_before_patch_is_uncertain_not_cas(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        client.race_before_patch = True
        result = pu.apply_projection(proposal, client, **opts)
        self.assertEqual(result["status"], "UNCERTAIN")
        self.assertFalse(result["complete"])
        self.assertIn("late concurrent Owner edit", client.issue["body"])
        self.assertEqual(len([op for op in client.operations if op[0] == "PATCH"]), 1)

    def test_scoreboard_readback_mismatch_is_uncertain_not_verified(self):
        client = FakeNative()
        client.issue["title"] = NEW_TITLE
        proposal, opts = prepare(client, "scoreboard")
        client.corrupt_body_readback = True
        result = pu.apply_projection(proposal, client, **opts)
        self.assertEqual(result["status"], "UNCERTAIN")
        self.assertFalse(result["complete"])
        self.assertEqual(result["applied"], 0)
        self.assertTrue(result["pending_surfaces"])
        self.assertEqual(len([op for op in client.operations if op[0] == "PATCH"]), 1)

    def test_foreign_demo_authority_denied_before_write(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        for value in (
            "https://github.com/other/repo/issues/409#issuecomment-6244462145",
            "https://github.com/reallakshman19/Common/issues/409#issuecomment-999",
            "",
        ):
            with self.subTest(value=value), self.assertRaises(lc.ContractError):
                pu.apply_projection(proposal, client, **(opts | {"demo_authority": value}))
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_client_repo_mismatch_denied_before_write(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        client.repo = "foreign/repo"
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(proposal, client, **opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_forged_consent_identity_not_sufficient_even_if_body_forged(self):
        for key, value in (
            ("id", 1234),
            ("html_url", "https://github.com/foreign/other/issues/409#issuecomment-6244462145"),
            ("user", {"login": "not-owner"}),
        ):
            client = FakeNative()
            proposal, opts = prepare(client, "title")
            client.comment[key] = value
            with self.subTest(key=key):
                result = pu.apply_projection(proposal, client, **opts)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertEqual(result["applied"], 0)
                self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_consent_body_altered_but_required_fragments_remain_is_rejected(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        client.comment["body"] = client.comment["body"].replace(
            "Next: WP sent to Common coder (tab-3).",
            "Next: WP sent to Common coder (tab-3). Reinterpreted authority.")
        # Refreshing the digest of the *modified* comment must not bypass
        # the frozen approved-body hash: this is NOT user-authorised consent.
        with self.assertRaises(lc.ContractError):
            pu.disposable_consent_pin(client)
        result = pu.apply_projection(proposal, client, **opts)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_nondict_projection_change_raises_contract_error(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        for value in (None, 7, "[malformed]"):
            with self.subTest(value=value):
                changed = copy.deepcopy(proposal)
                changed["changes"] = [value]
                with self.assertRaises(lc.ContractError):
                    pu.apply_projection(changed, client, **opts)
        self.assertFalse(any(op[0] == "PATCH" for op in client.operations))

    def test_uncertain_readback_never_claims_verified_or_replays(self):
        client = FakeNative()
        proposal, opts = prepare(client, "title")
        client.corrupt_readback = True
        result = pu.apply_projection(proposal, client, **opts)
        self.assertEqual(result["status"], "UNCERTAIN")
        self.assertFalse(result["complete"])
        self.assertTrue(result["pending_surfaces"])
        self.assertEqual(len([op for op in client.operations if op[0] == "PATCH"]), 1)


if __name__ == "__main__":
    unittest.main()
