"""Executable counterexamples from M3#375, comment6159911933, exact56c56c9.

These controller-run tests reproduce F02/F03/F05; they do not replace M3's
independent runtime verdict or establish live GitHub/browser/private parity.
"""
import tempfile
import unittest
import json
from pathlib import Path

from coordination.master_panel.github_source import GitHubSourceScanner
from coordination.master_panel.models import build_row
from coordination.master_panel.read_api import MasterReadService
from coordination.master_panel.storage import SourceStore
from coordination.tests.test_master_panel_intake import FakeGitHub
from coordination.tests.test_master_panel_read_api import source
from coordination.master_panel.report_parser import extract_report
from coordination.tests.test_master_panel_report_parser import envelope, source as report_source, STAMP


class M3SourceCounterexamples(unittest.TestCase):
    def test_identity_only_legacy_claim_is_explicitly_unqualified(self):
        body = envelope()
        claim = extract_report(body, report_source(body))
        self.assertEqual(claim['transport_status'], 'UNQUALIFIED_LEGACY')
        self.assertNotIn('review_verdict', claim)
        row = build_row(report_source(body), report=claim)
        self.assertEqual(row['report']['transport_status'], 'UNQUALIFIED_LEGACY')
        self.assertEqual(row['evidence']['review_verdict'], 'UNKNOWN')

    def test_transport_metadata_requires_valid_complete_minimum(self):
        original = json.loads(envelope().split('```casp\n')[1].split('\n```')[0])
        original.update(created_at=STAMP, request_digest='a'*64,
                        reply_to='synthetic-request-parent', expected_revision=1)
        original['target']['binding_generation'] = 1
        def claim(value):
            body = '```casp\n' + json.dumps(value) + '\n```'
            return extract_report(body, report_source(body))
        self.assertEqual(claim(original)['transport_status'], 'MINIMUM_FIELDS_VALID')
        request = {**original, 'kind':'REQUEST', 'status':'REQUESTED',
                   'reply_to':None, 'request_digest':None}
        self.assertEqual(claim(request)['transport_status'], 'MINIMUM_FIELDS_VALID')
        for key, value in [('created_at','2026-99-99T99:99:99Z'),
                           ('expected_revision',True), ('expires_at','not-a-clock'),
                           ('reply_to',None), ('status','RECEIVED')]:
            with self.subTest(key=key):
                self.assertIsNone(claim({**original,key:value}))
        self.assertIsNone(claim({**request, 'request_digest':'a'*64}))
        duplicate = '```casp\n' + json.dumps(original)[:-1] + ',"expected_revision":0}\n```'
        self.assertIsNone(extract_report(duplicate, report_source(duplicate)))

    def test_paginated_absence_notice_survives_sqlite_reopen(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp)/'source.sqlite')
            store, reader = SourceStore(path), FakeGitHub()
            try:
                reader.comments['common'] = [reader.comment('common',1000+i) for i in range(101)]
                scanner = GitHubSourceScanner(store,reader)
                self.assertTrue(scanner.run('common',max_requests=20)['complete'])
                reader.comments['common'] = reader.comments['common'][:100]
                outcome = scanner.run('common',max_requests=20)
                self.assertEqual(outcome['tombstones'],0)
                self.assertFalse(outcome['absence_verified'])
                store.close();store = SourceStore(path)
                self.assertEqual(store.scan('common')['failure_kind'],'ABSENCE_UNVERIFIED')
                retained = next(row for row in store.objects('common',limit=200) if row['entity_id']=='1100')
                self.assertEqual(retained['deleted'],0)
            finally:
                store.close()

    def test_review_without_head_cannot_borrow_provider_current_sha(self):
        row = build_row(source('1001', 'body'),
                        report={'candidate_sha': 'a' * 40},
                        review={'review_verdict': 'PASS',
                                'review_ref': 'https://github.com/reallakshman19/Common/issues/375#issuecomment-222'},
                        current_pr_head_sha='a' * 40)
        self.assertEqual(row['evidence']['candidate_relation'], 'UNKNOWN')
        self.assertIsNone(row['evidence']['review_candidate_sha'])
        self.assertEqual(row['evidence']['reported_verdict'], 'UNKNOWN')

    def test_failed_attempt_does_not_refresh_last_good_data(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / 'source.sqlite')
            writer = SourceStore(path)
            try:
                reader = FakeGitHub()
                scanner = GitHubSourceScanner(writer, reader)
                self.assertTrue(scanner.run('common')['complete'])
                count = len(writer.objects('common'))
                reader.fail_repo = 'common'
                for code, expected in [(503, 'UNAVAILABLE'), (429, 'RATE_LIMITED')]:
                    with self.subTest(code=code):
                        reader.fail_code = code
                        self.assertEqual(scanner.run('common')['source_status'], expected)
                        service = MasterReadService(path)
                        rows = service.rows('common')['items']
                        self.assertEqual(len(rows), count)
                        self.assertTrue(all(x['absence'] == 'PRESENT' for x in rows))
                        self.assertTrue(all(x['source_health']['freshness'] == 'UNKNOWN' for x in rows))
                        project = next(x for x in service.projects()['projects'] if x['project_id'] == 'common')
                        status = next(x for x in service.sources()['sources'] if x['project_id'] == 'common')
                        self.assertEqual(project['source_freshness'], 'UNKNOWN')
                        self.assertEqual(status['freshness'], 'UNKNOWN')
            finally:
                writer.close()

    def test_nonobject_meta_issue_or_comment_is_bounded_source_conflict(self):
        for failure in ['meta', 'issue', 'comment']:
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temp:
                store = SourceStore(str(Path(temp) / 'source.sqlite'))
                class Malformed(FakeGitHub):
                    def get_json(self, path, query=None):
                        value = super().get_json(path, query)
                        if failure == 'meta' and path == 'repos/reallakshman19/Common':
                            return []
                        if failure == 'issue' and path.endswith('/issues'):
                            return [None]
                        if failure == 'comment' and path.endswith('/comments'):
                            return ['malformed']
                        return value
                try:
                    result = GitHubSourceScanner(store, Malformed()).run('common')
                    self.assertEqual(result['source_status'], 'UNAVAILABLE')
                    self.assertEqual(result['error_kind'], 'SOURCE_CONFLICT')
                    self.assertEqual(result['tombstones'], 0)
                    self.assertFalse(result['complete'])
                finally:
                    store.close()


if __name__ == '__main__':
    unittest.main()
