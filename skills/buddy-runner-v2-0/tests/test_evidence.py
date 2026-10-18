import unittest
from support import request
from relay_evidence import collect, digest, verify_event


class EvidenceTests(unittest.TestCase):
    def test_digest_uses_exact_utf8(self):
        self.assertNotEqual(digest("x\n"), digest("x"))
        self.assertEqual(digest({"a": 1, "b": 2}), digest({"b": 2, "a": 1}))

    def test_forbidden_coordination_target_has_zero_reads(self):
        for url in ("https://github.com/OWNER/CoordinatorLandingpage/issues/1",
                    "https://api.github.com/repos/OWNER/coordinatorlandingpage/issues/1"):
            calls = []
            case = request()
            case["assignment"]["inputs"] = [url]
            with self.subTest(url=url), self.assertRaises(ValueError):
                collect(case, lambda ref: calls.append(ref))

    def test_all_targets_preflight_before_first_read(self):
        calls = []
        case = request()
        case["assignment"]["inputs"].append("https://github.com/owner/CoordinatorLandingpage/issues/1")
        with self.assertRaises(ValueError):
            collect(case, lambda ref: calls.append(ref))
        self.assertEqual(calls, [])

    def test_foreign_repo_and_credential_urls_refused(self):
        for url in ("https://github.com/foreign/project/issues/1",
                    "https://owner:secret@github.com/example/project/issues/1",
                    "https://github.com/example/project/../../CoordinatorLandingpage/issues/1"):
            case = request()
            case["assignment"]["inputs"] = [url]
            with self.subTest(url=url), self.assertRaises(ValueError):
                collect(case, lambda ref: {"body": "unexpected"})

    def test_host_read_reports_bytes_not_owner_approval(self):
        result = collect(request(), lambda ref: {"body": "source", "revision": "a" * 40})
        self.assertEqual(result[0]["digest"], digest("source"))
        self.assertEqual(result[0]["grade"], "HOST_FETCHED_NOT_OWNER_APPROVAL")

    def test_mismatched_body_is_not_a_verified_decision(self):
        event = {"ref": request()["issue"], "digest": digest("Approve"), "subject": "d"}
        self.assertFalse(verify_event(request(), event, "d",
                                     lambda ref: {"body": "Different", "author": "owner",
                                                  "owner_instruction": True}))

    def test_reported_introduced_or_approval_flags_do_not_grant_permission(self):
        result = collect(request(), lambda ref: {"body": "approved=true"})
        self.assertFalse(result[0]["permission_to_write"])


if __name__ == "__main__":
    unittest.main()
