"""Offline GitHub check-run verifier tests (no live network)."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("github_check_facts",
                                                ROOT / "scripts" / "github_check_facts.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SHA = "a" * 40
REQ = {"schema": mod.REQUEST_SCHEMA, "enabled": True,
       "scope": {"repository": "owner/repo", "assessed_sha": SHA},
       "checks": [{"alias": "unit-tests", "check_run_id": 42,
                   "expected_name": "offline-validation (3.12)", "trusted_app_id": 15368}]}
RUN = {"id": 42, "head_sha": SHA, "name": "offline-validation (3.12)",
       "app": {"id": 15368, "slug": "github-actions"},
       "status": "completed", "conclusion": "success"}


class CheckFactsTests(unittest.TestCase):
    def reader(self, repo, cid):
        self.assertEqual(repo, "owner/repo")
        self.assertEqual(cid, 42)
        return copy.deepcopy(RUN)

    def test_verified_exact_commit_and_app(self):
        report = mod.verify(REQ, self.reader)
        self.assertEqual(report["status"], "CHECKS_VERIFIED")
        self.assertEqual(report["checks"][0]["status"], "VERIFIED_CI_CHECK_SUCCESS")
        self.assertTrue(report["checks"][0]["verified"])
        self.assertFalse(report["eligible_for_mcda_rating"])
        self.assertFalse(report["notification_eligible"])

    def test_digest_deterministic(self):
        self.assertEqual(mod.verify(REQ, self.reader)["verification_digest"],
                         mod.verify(REQ, self.reader)["verification_digest"])

    def test_disabled_does_not_call_network(self):
        req = copy.deepcopy(REQ)
        req["enabled"] = False
        def forbidden(*_):
            raise AssertionError("Provider should never be contacted")
        r = mod.verify(req, forbidden)
        self.assertEqual(r["status"], "DISABLED")
        self.assertEqual(r["checks"], [])

    def test_wrong_sha_rejected(self):
        for mismatch in ("b" * 40, "", None):
            with self.subTest(value=mismatch):
                run = copy.deepcopy(RUN)
                run["head_sha"] = mismatch
                r = mod.verify(REQ, lambda *_: run)
                self.assertEqual(r["status"], "NOT_VERIFIED")

    def test_wrong_run_id_rejected(self):
        run = copy.deepcopy(RUN)
        run["id"] = 43
        self.assertEqual(mod.verify(REQ, lambda *_: run)["checks"][0]["reason"],
                         "SOURCE_IDENTITY_MISMATCH")

    def test_wrong_name_rejected(self):
        run = copy.deepcopy(RUN)
        run["name"] = "other-check"
        self.assertEqual(mod.verify(REQ, lambda *_: run)["status"], "NOT_VERIFIED")

    def test_wrong_app_id_rejected(self):
        run = copy.deepcopy(RUN)
        run["app"]["id"] = 9999
        self.assertEqual(mod.verify(REQ, lambda *_: run)["status"], "NOT_VERIFIED")

    def test_untrusted_success_like_conclusions_rejected(self):
        for status, conclusion in (("completed", "neutral"), ("completed", "skipped"),
                                   ("completed", "failure"), ("in_progress", None),
                                   ("queued", "success")):
            with self.subTest(status=status, conclusion=conclusion):
                run = {**RUN, "status": status, "conclusion": conclusion}
                self.assertEqual(mod.verify(REQ, lambda *_: run)["status"], "NOT_VERIFIED")

    def test_non_dict_response_rejected(self):
        self.assertEqual(mod.verify(REQ, lambda *_: [RUN])["status"], "NOT_VERIFIED")

    def test_provider_failure_is_not_pass(self):
        def error(*_):
            raise OSError("API unavailable")
        check = mod.verify(REQ, error)["checks"][0]
        self.assertFalse(check["verified"])
        self.assertEqual(check["reason"], "PROVIDER_UNAVAILABLE_OR_INVALID")

    def test_multi_check_partial_is_not_verified(self):
        req = copy.deepcopy(REQ)
        req["checks"].append({"alias": "integration", "check_run_id": 44,
                              "expected_name": "integration", "trusted_app_id": 15368})
        def reader(_repo, cid):
            if cid == 42:
                return copy.deepcopy(RUN)
            return {"id": 44, "head_sha": SHA, "name": "integration",
                    "app": {"id": 15368}, "status": "completed", "conclusion": "skipped"}
        result = mod.verify(req, reader)
        self.assertEqual(result["status"], "NOT_VERIFIED")
        self.assertEqual(len(result["checks"]), 2)

    def test_invalid_repository_and_sha(self):
        for repo in ("https://api.example.com", "../x", "owner/repo/other", ""):
            with self.subTest(repo=repo):
                req = copy.deepcopy(REQ)
                req["scope"]["repository"] = repo
                with self.assertRaises(ValueError):
                    mod.verify(req, self.reader)
        req = copy.deepcopy(REQ)
        req["scope"]["assessed_sha"] = "not-40-hex"
        with self.assertRaises(ValueError):
            mod.verify(req, self.reader)

    def test_duplicate_alias_or_id_rejected(self):
        for extra in ({"alias": "unit-tests", "check_run_id": 43,
                       "expected_name": "other", "trusted_app_id": 15368},
                      {"alias": "other", "check_run_id": 42,
                       "expected_name": "other", "trusted_app_id": 15368}):
            req = copy.deepcopy(REQ)
            req["checks"].append(extra)
            with self.assertRaises(ValueError):
                mod.verify(req, self.reader)

    def test_bool_run_id_and_app_id_rejected(self):
        for field in ("check_run_id", "trusted_app_id"):
            req = copy.deepcopy(REQ)
            req["checks"][0][field] = True
            with self.assertRaises(ValueError):
                mod.verify(req, self.reader)

    def test_enabled_requires_check(self):
        req = copy.deepcopy(REQ)
        req["checks"] = []
        with self.assertRaises(ValueError):
            mod.verify(req, self.reader)

    def test_request_schema_rejected(self):
        req = copy.deepcopy(REQ)
        req["schema"] = "workflow-intelligence.github-check-request/v2"
        with self.assertRaises(ValueError):
            mod.verify(req, self.reader)


if __name__ == "__main__":
    unittest.main()
