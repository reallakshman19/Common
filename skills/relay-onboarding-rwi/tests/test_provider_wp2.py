"""WP2 negative source tests. Mock provider facts; NEVER a hosted GitHub acceptance claim."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_module(short, path):
    spec = importlib.util.spec_from_file_location(short, ROOT / "adapters" / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gh = source_module("onb_provider", "github.py")
v36 = source_module("onb_v36", "v36.py")

BASE = "/repos/acme/demo"
A = "a" * 40
B = "b" * 40
INDEX = "<!-- v36-plan-index:V36-7-PLAN-01 parent:acme/demo#7 -->"
BODY = INDEX + "\nPLAN_INDEX — V36-7-PLAN-01\n| one | O1 | S | [#8](https://github.com/acme/demo/issues/8) |\n"


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.map = {
            BASE: ({"full_name": "acme/demo", "default_branch": "main"}, ""),
            BASE + "/commits/main": ({"sha": A}, ""),
            BASE + "/issues/7": ({"number": 7, "title": "Lab Parent", "state": "open", "body": "Test source"}, ""),
            BASE + "/issues/7/comments?per_page=100&page=1": (
                [{"id": 10, "body": BODY, "user": {"login": "owner"},
                  "created_at": "2026-10-15T00:00:00Z", "updated_at": "2026-10-15T00:00:00Z"}], ""),
            BASE + "/pulls/2": ({"number": 2, "state": "open", "draft": True, "merged": False,
                                   "head": {"sha": B}, "base": {"sha": A}}, ""),
            BASE + "/pulls/2/files?per_page=100&page=1": (
                [{"filename": "src/core.py", "status": "modified"}], ""),
            BASE + "/commits/" + B + "/check-runs?per_page=100&page=1": (
                {"total_count": 1, "check_runs": [{"id": 10, "name": "unit", "status": "completed",
                                                  "conclusion": "success", "head_sha": B}]}, "")
        }
        self.change_sha = False
        self.pr_change = False
        self._main_calls = 0
        self._pr_calls = 0

    def get(self, path):
        self.calls.append(path)
        if path == BASE + "/commits/main":
            self._main_calls += 1
            if self.change_sha and self._main_calls == 2:
                return {"sha": B}, ""
        if path == BASE + "/pulls/2":
            self._pr_calls += 1
            if self.pr_change and self._pr_calls == 2:
                data = copy.deepcopy(self.map[path][0])
                data["head"]["sha"] = A
                return data, ""
        if path not in self.map:
            raise AssertionError("Unexpected read: " + path)
        return copy.deepcopy(self.map[path])


class WP2ProviderTests(unittest.TestCase):
    def fake(self):
        return FakeProvider()

    def collect(self, client=None, prs=(2,)):
        return gh.collect(client or self.fake(), "acme/demo", 7, prs,
                          expected_main=A, now="2026-10-15T00:00:00Z")

    def test_pilot_one_safe_snapshot(self):
        data = self.collect()
        self.assertEqual(data["schema"], "onboarding.provider-snapshot/v1")
        self.assertEqual(data["default_head_sha"], A)
        self.assertEqual(data["prs"][0]["head_sha"], B)
        self.assertEqual(data["prs"][0]["files"][0]["path"], "src/core.py")
        self.assertEqual(data["prs"][0]["checks"]["state"], "OBSERVED")
        self.assertFalse(data["owner_acceptance_verified"])
        self.assertFalse(data["execution_authorized"])

    def test_zero_exit_no_report_dependency(self):
        data = self.collect()
        self.assertFalse(data["predecessor_final_report_required"])
        self.assertNotIn("final_handover", data)

    def test_no_private_body_leaks_in_public_projection(self):
        data = gh.public_projection(self.collect())
        self.assertNotIn("body", data["v36_index_candidates"][0])
        self.assertNotIn(INDEX, str(data))
        self.assertFalse(data["comments"][0]["text_exported"])

    def test_renamed_provider_repo_fails(self):
        f = self.fake()
        f.map[BASE] = ({"full_name": "renamed/demo", "default_branch": "main"}, "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_expected_main_mismatch_fails(self):
        with self.assertRaises(gh.SourceError):
            gh.collect(self.fake(), "acme/demo", 7, (), expected_main=B)

    def test_main_moves_during_read(self):
        f = self.fake()
        f.change_sha = True
        with self.assertRaisesRegex(gh.SourceError, "STALE"):
            self.collect(f)

    def test_pr_head_moves_during_read(self):
        f = self.fake()
        f.pr_change = True
        with self.assertRaisesRegex(gh.SourceError, "STALE"):
            self.collect(f)

    def test_wrong_issue_number_fails(self):
        f = self.fake()
        f.map[BASE + "/issues/7"] = ({"number": 8, "title": "Wrong"}, "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_issue_must_not_be_pr(self):
        f = self.fake()
        f.map[BASE + "/issues/7"] = ({"number": 7, "title": "Wrong", "pull_request": {}}, "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_duplicate_pr_requested_fails(self):
        with self.assertRaises(gh.SourceError):
            self.collect(prs=(2, 2))

    def test_duplicate_comment_identity_fails(self):
        f = self.fake()
        c = f.map[BASE + "/issues/7/comments?per_page=100&page=1"][0][0]
        f.map[BASE + "/issues/7/comments?per_page=100&page=1"] = ([c, c], "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_gh_check_provider_403_is_unknown_not_green(self):
        f = self.fake()
        class Forbidden:
            def get(self, path):
                if "/check-runs?" in path:
                    raise gh.ProviderError(403, "no permission")
                return f.get(path)
        data = self.collect(Forbidden())
        self.assertEqual(data["source_health"], "PARTIAL_OPTIONAL_CI")
        self.assertEqual(data["prs"][0]["checks"]["state"], "UNKNOWN")

    def test_partial_check_run_total_fails(self):
        f = self.fake()
        k = BASE + "/commits/" + B + "/check-runs?per_page=100&page=1"
        f.map[k] = ({"total_count": 2, "check_runs": [{"id": 10, "head_sha": B}]}, "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_two_page_comments_safely_counted(self):
        f = self.fake()
        k = BASE + "/issues/7/comments?per_page=100&page=1"
        v = f.map[k][0]
        next_link = '<https://api.github.com' + BASE + '/issues/7/comments?per_page=100&page=2>; rel="next"'
        f.map[k] = (v, next_link)
        f.map[BASE + "/issues/7/comments?per_page=100&page=2"] = (
            [{"id": 11, "body": "not evidence", "user": {"login": "reader"}}], "")
        self.assertEqual(len(self.collect(f)["comments"]), 2)

    def test_foreign_next_page_link_rejected(self):
        f = self.fake()
        k = BASE + "/issues/7/comments?per_page=100&page=1"
        f.map[k] = (f.map[k][0], '<https://evil.example/?page=2&per_page=100>; rel="next"')
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_pagination_limit_rejects_incomplete(self):
        f = self.fake()
        next_link = '<https://api.github.com' + BASE + '/issues/7/comments?per_page=100&page=2>; rel="next"'
        f.map[BASE + "/issues/7/comments?per_page=100&page=1"] = ([], next_link)
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_check_run_wrong_commit_refused(self):
        f = self.fake()
        k = BASE + "/commits/" + B + "/check-runs?per_page=100&page=1"
        f.map[k] = ({"total_count": 1, "check_runs": [{"id": 11, "head_sha": A}]}, "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_v36_parent_index_advisory(self):
        index = v36.interpret_index(self.collect(), expected_plan="V36-7-PLAN-01")
        self.assertEqual(index["entry"]["children"], [8])
        self.assertEqual(index["status"], "INDEX_LINKS_OBSERVED_NOT_VERIFIED")
        self.assertFalse(index["entry"]["owner_accepted"])
        self.assertFalse(index["entry"]["child_issue_verified"])

    def test_v36_no_index_is_not_pass(self):
        f = self.fake()
        k = BASE + "/issues/7/comments?per_page=100&page=1"
        f.map[k] = ([{"id": 10, "body": "No handover / no index"}], "")
        self.assertEqual(v36.interpret_index(self.collect(f))["status"], "INDEX_NOT_VERIFIED")

    def test_v36_bad_foreign_child(self):
        f = self.fake()
        k = BASE + "/issues/7/comments?per_page=100&page=1"
        f.map[k][0][0]["body"] = INDEX + "\n[#5](https://github.com/foreign/repo/issues/5)"
        with self.assertRaisesRegex(ValueError, "cross-repository"):
            v36.interpret_index(self.collect(f))

    def test_v36_wrong_parent(self):
        f = self.fake()
        k = BASE + "/issues/7/comments?per_page=100&page=1"
        f.map[k][0][0]["body"] = "<!-- v36-plan-index:V36-7-PLAN-01 parent:acme/demo#9 -->"
        with self.assertRaisesRegex(ValueError, "wrong parent"):
            v36.interpret_index(self.collect(f))

    def test_v36_duplicate_indices(self):
        f = self.fake()
        k = BASE + "/issues/7/comments?per_page=100&page=1"
        f.map[k][0][0]["body"] = BODY + "\n" + INDEX
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            v36.interpret_index(self.collect(f))

    def test_suspicious_pr_file_path_rejected(self):
        f = self.fake()
        k = BASE + "/pulls/2/files?per_page=100&page=1"
        f.map[k] = ([{"filename": "../secrets", "status": "modified"}], "")
        with self.assertRaises(gh.SourceError):
            self.collect(f)

    def test_false_acceptance_does_not_follow_green_check(self):
        data = self.collect()
        self.assertEqual(data["prs"][0]["checks"]["items"][0]["conclusion"], "success")
        self.assertFalse(data["prs"][0]["candidate_accepted"])
        self.assertFalse(data["owner_acceptance_verified"])

    def test_hard_read_only_transport_no_post_method(self):
        self.assertFalse(hasattr(gh.HttpReadTransport(), "post"))
        self.assertFalse(hasattr(gh.HttpReadTransport(), "patch"))

    def test_declared_exact_ref_not_arbitrary_sample(self):
        f = self.fake()
        data = self.collect(f)
        self.assertNotIn("https://github.com/evil", str(data))
        self.assertTrue(all(s.startswith(BASE) for s in f.calls))


if __name__ == "__main__":
    unittest.main()
