"""CLI and native reader compatibility for standalone completion only."""
from contextlib import redirect_stdout
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import yaml
from test_standalone_done_v36 import ROOT, fixture
sys.path.insert(0, str(ROOT / 'scripts'))
import decompose_v36 as dc
import lifecycle_v36 as lc
import readmodel_v36 as rm


class Provider:
    repo = 'sample/project'
    def __init__(self, plan, head, body):
        self.head = head
        self.issue = {'number': 2, 'title': dc.child_title(plan['tasks'][0]),
                      'body': dc.child_body(plan['tasks'][0], plan), 'state': 'open',
                      'html_url': 'https://github.com/sample/project/issues/2'}
        link = self.issue['html_url'] + '#issuecomment-1'
        evidence = lc.render_evidence(
            outcome='O1', for_user='Result observed Self-check: ' + link,
            proof='https://github.com/sample/project/pull/3/commits/' + head,
            task_id='V36-1-WP1', issue_ref='sample/project#2',
            candidate='sample/project@' + head, tests_passed=1, tests_run=1)
        self.comments = [self.comment(1, body), self.comment(2, evidence)]
    @staticmethod
    def comment(cid, body):
        return {'id': cid, 'body': body, 'user': {'login': 'sample'},
                'html_url': 'https://github.com/sample/project/issues/2#issuecomment-' + str(cid),
                'created_at': f'2026-10-19T10:00:0{cid}Z',
                'updated_at': f'2026-10-19T10:00:0{cid}Z'}
    def list_issues(self): return [self.issue]
    def list_comments(self, number): return self.comments if number == 2 else []
    def get_pr(self, number): return {'head': {'sha': self.head}, 'draft': True}


class StandaloneCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        (self.repo, self.label, self.plan, self.criteria, self.digest,
         self.body, self.head) = fixture(self.tmp.name)
        self.label_path = self.repo / 'relay/AIM/PILOT.yaml'
        self.label_path.parent.mkdir(parents=True)
        self.label_path.write_text(yaml.safe_dump(self.label), encoding='utf-8')
        (self.repo / 'plan.yaml').write_text(yaml.safe_dump(self.plan), encoding='utf-8')
        (self.repo / 'selfcheck.txt').write_text(self.body, encoding='utf-8')

    def args(self):
        return ['--label', str(self.label_path), '--plan', str(self.repo / 'plan.yaml'),
                '--task-id', 'V36-1-WP1', '--issue-ref', 'sample/project#2',
                '--candidate', 'sample/project@' + self.head,
                '--criteria', str(self.repo / 'criteria.txt'), '--criteria-sha256', self.digest,
                '--self-check', str(self.repo / 'selfcheck.txt'), '--repo', str(self.repo),
                '--evidence-root', str(self.repo)]

    def run_cli(self):
        cli = importlib.import_module('standalone_done_v36')
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = cli.main(self.args())
        return code, json.loads(stream.getvalue())

    def test_real_cli_with_no_ci_and_no_judgment_is_usable(self):
        code, result = self.run_cli()
        self.assertEqual(code, 0, result)
        self.assertTrue(result['declaration_consistent'])
        self.assertFalse(result['owner_accepted'])

    def test_coordinator_and_missing_mode_refuse_before_reading_plan(self):
        for mode in ('coordinator', None):
            label = dict(self.label)
            if mode: label['mode'] = mode
            else: label.pop('mode')
            self.label_path.write_text(yaml.safe_dump(label), encoding='utf-8')
            with mock.patch('standalone_done_v36.load_plan', side_effect=AssertionError('plan read')):
                code, result = self.run_cli()
            self.assertEqual(code, 2)
            self.assertIn('explicit standalone', result['error'])

    def test_mutated_proof_cli_returns_one_failure_record(self):
        (self.repo / 'result.txt').write_bytes(b'Wrong bytes\n')
        code, result = self.run_cli()
        self.assertEqual(code, 1)
        self.assertFalse(result['declaration_consistent'])

    def test_native_reader_consumes_v1_with_common_checklist(self):
        report = rm.read_model(self.plan, Provider(self.plan, self.head, self.body),
                               '2026-10-19T10:01:00Z')
        task = report['tasks'][0]
        self.assertEqual(task['status'], 'CURRENT_EVIDENCE')
        self.assertTrue(task['claim_qualified'], task['reasons'])
        self.assertEqual(task['self_check']['done_when']['MET'], 9)
        self.assertEqual(report['acceptance'], 'NOT_EVALUATED')

    def test_native_coordinator_label_and_v2_helpers_keep_original_behavior(self):
        old = lc.load_label(ROOT / 'tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml')
        self.assertNotIn('mode', old)
        self.assertEqual(lc.label_mode(old), 'coordinator')
        import test_scored_v36 as scored
        from criteria_v36 import parse_criteria_v1
        from selfcheck_score_v36 import parse_self_check_v2
        from score_v36 import recompute
        frozen = parse_criteria_v1(scored.FROZEN)
        result = recompute(frozen, parse_self_check_v2(scored.valid_check(), frozen),
                           scored.BEFORE, scored.AFTER, scored.DIFF)
        self.assertTrue(result['qualified'])
        self.assertEqual(result['claim_class'], 'PARTIAL')

    def test_network_and_writes_are_not_part_of_helper(self):
        with mock.patch('socket.socket.connect', side_effect=AssertionError('network')):
            before = {p: p.read_bytes() for p in self.repo.rglob('*')
                      if p.is_file() and '.git' not in p.parts}
            self.assertEqual(self.run_cli()[0], 0)
            after = {p: p.read_bytes() for p in self.repo.rglob('*')
                     if p.is_file() and '.git' not in p.parts}
            self.assertEqual(before, after)


    def test_chatgpt_agent_requires_activity_while_work_does_not(self):
        import standalone_done_v36 as cli
        for surface, expected in [('chatgpt-agent', 1), ('chatgpt-work', 0), ('other', 0)]:
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = cli.main(self.args() + ['--agent-surface', surface])
            self.assertEqual(code, expected, stream.getvalue())

    def test_activity_unknown_is_reportable_without_fabrication(self):
        from standalone_activity_check_v36 import check_activity
        from standalone_activity_v36 import append_event
        import hashlib
        path = self.repo / 'activity.jsonl'
        append_event(path, {'event': 'session', 'at': '2026-10-19T10:00:00Z',
                           'session_id': 'ep-1', 'surface': 'chatgpt-agent',
                           'observation': 'SELF_RECORDED'})
        append_event(path, {'event': 'gap', 'at': '2026-10-19T10:01:00Z',
                           'reason': 'native turn IDs and earlier active duration unavailable'})
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        body = self.body.replace('Owner acceptance separate', f'Owner acceptance separate; activity episode ep-1; activity sha256 {digest}')
        result, gaps = check_activity('chatgpt-agent', path, 'ep-1', body)
        self.assertEqual(gaps, [])
        self.assertEqual(result['threshold_state'], 'UNKNOWN')
        self.assertEqual(result['coverage'], 'INCOMPLETE')

    def test_chatgpt_agent_must_report_actual_suggestion_when_due(self):
        from standalone_activity_check_v36 import check_activity
        from standalone_activity_v36 import append_event
        from test_standalone_activity_v36 import events
        import hashlib
        path = self.repo / 'activity.jsonl'
        for row in events(6): append_event(path, row)
        def body():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            return self.body.replace('Owner acceptance separate', f'Owner acceptance separate; activity episode agent-episode-1; activity sha256 {digest}')
        result, gaps = check_activity('chatgpt-agent', path, 'agent-episode-1', body())
        self.assertTrue(result['buddy_suggestion_due'])
        self.assertTrue(gaps)
        append_event(path, {'event': 'buddy-suggested', 'at': '2026-10-19T10:41:00Z',
                           'reference': 'actual reply proposing BuddyRunner'})
        result, gaps = check_activity('chatgpt-agent', path, 'agent-episode-1', body())
        self.assertEqual(gaps, [])
        self.assertFalse(result['buddy_suggestion_due'])

    def test_full_chatgpt_agent_cli_consumes_native_activity_binding(self):
        from standalone_activity_v36 import append_event
        import standalone_done_v36 as cli
        import hashlib
        path = self.repo / 'activity.jsonl'
        append_event(path, {'event': 'session', 'at': '2026-10-19T10:00:00Z',
                           'session_id': 'ep-1', 'surface': 'chatgpt-agent',
                           'observation': 'SELF_RECORDED'})
        append_event(path, {'event': 'gap', 'at': '2026-10-19T10:01:00Z',
                           'reason': 'historical host observations unavailable'})
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        body = self.body.replace('Owner acceptance separate',
                                 f'Owner acceptance separate; activity episode ep-1; activity sha256 {digest}')
        (self.repo / 'selfcheck.txt').write_text(body, encoding='utf-8')
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(self.args() + ['--agent-surface', 'chatgpt-agent',
                            '--activity-log', str(path), '--activity-session-id', 'ep-1'])
        self.assertEqual(code, 0, out.getvalue())
        result = json.loads(out.getvalue())
        self.assertTrue(result['activity']['policy_applies'])
        self.assertEqual(result['activity']['threshold_state'], 'UNKNOWN')
        self.assertFalse(result['owner_accepted'])


if __name__ == '__main__':
    unittest.main()
