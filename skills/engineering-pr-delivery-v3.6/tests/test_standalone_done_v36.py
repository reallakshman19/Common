"""Standalone completion witnesses and negative cases; no network/provider writes."""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
GROUPS = ('SC_INTENT', 'SC_INPUTS', 'SC_SCOPE', 'SC_FLOW', 'SC_TESTS',
          'SC_CODE', 'SC_PENDING', 'SC_FRESHNESS')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixture(folder):
    """Task with local proof, a frozen criterion and native A14 companion."""
    repo = Path(folder)
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()
    git('init', '-q'); git('config', 'user.email', 'fixture@example.invalid')
    git('config', 'user.name', 'Fixture'); git('config', 'core.autocrlf', 'false')
    (repo / 'result.txt').write_bytes(b'Observed output: 2; expected 2; negative missing-input error.\n')
    git('add', 'result.txt'); git('commit', '-qm', 'fixture candidate')
    head = git('rev-parse', 'HEAD')
    label = {'mode': 'standalone', 'work': 'PILOT', 'repository': 'sample/project',
             'engineering_critical': 'standard', 'version': '1.0.0', 'label_sha': 'abc1234',
             'label': {'problem': 'Missing result', 'main_aim': 'Produce a traceable result',
                       'outcomes': {'O1': 'Result can be checked'},
                       'owner_constraints': ['Owner retains acceptance'],
                       'task_outcome': 'O1', 'task_aim': 'Complete the bounded task',
                       'done_when': 'Observable result with evidence'},
             'guidance': {'not_now': [], 'watch': [], 'notes': []},
             'bindings': ['Owner task source issue 1'], 'history': ['Owner selected standalone']}
    plan = {'plan_version': 'V36-1-PLAN-01', 'parent': 'sample/project#1',
            'label': {k: label[k] for k in ('work', 'version', 'label_sha')},
            'tasks': [{'task_id': 'V36-1-WP1', 'size': 'S', 'outcome': 'O1',
                       'title': 'One result', 'acceptance': 'Result with negative contrast',
                       'for_user': 'The result can be checked'}]}
    criteria = ('CRITERIA v1 · PILOT · FROZEN 2026-10-19 by Owner · source: #1 body\n'
                'AC1 MUST "Produce a result" → Observable result\n'
                'Criteria: 1 (1 MUST · 0 CONSTRAINT · 0 JUDGMENT) · source coverage: all declared clauses\n')
    (repo / 'criteria.txt').write_text(criteria, encoding='utf-8')
    digest = sha((repo / 'criteria.txt').read_bytes())
    basis = (f'Basis: plan V36-1-PLAN-01; label PILOT@1.0.0:abc1234; criteria sha256 {digest}; '
             f'candidate sample/project@{head}; source #1 body')
    proof = f'proof: result.txt ; sha256: {sha((repo / "result.txt").read_bytes())}'
    lines = ['SELF-CHECK v1 · V36-1-WP1 · sample/project#2', basis]
    lines += [f'Done-when: {key} → MET ; {proof}' for key in (*GROUPS, 'AC1')]
    lines += ['Scope: allowed task inputs; actual one result; protected data preserved',
              'A13: no source change; stage assessment in result.txt',
              'A13 review: self-assessed; no independent reviewer required for this task',
              'Tests: local task check; no CI; evidence records limitations',
              'Issue reconciliation: task acceptance assessed; Owner acceptance separate',
              'Pending: none', 'Proposed claim: DONE · reason: bounded task witnessed',
              'Native report: PENDING publication follows local verification']
    body = '\n'.join(lines) + '\n'
    return repo, label, plan, criteria, digest, body, head


class StandaloneDoneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        (self.repo, self.label, self.plan, self.criteria, self.digest,
         self.body, self.head) = fixture(self.tmp.name)
        try:
            self.module = importlib.import_module('standalone_checklist_v36')
        except ModuleNotFoundError:
            self.fail('Standalone completion verifier is not implemented')

    def assess(self, **changes):
        values = dict(label=self.label, plan=self.plan, task_id='V36-1-WP1',
                      issue_ref='sample/project#2', candidate='sample/project@' + self.head,
                      criteria_text=self.criteria, criteria_sha256=self.digest,
                      body=self.body, repo=self.repo, evidence_root=self.repo)
        values.update(changes)
        return self.module.check_done(**values)

    def test_native_v1_with_real_witnesses_and_no_ci(self):
        result = self.assess()
        self.assertTrue(result['done_supported'], result)
        self.assertFalse(result['owner_accepted'])
        self.assertEqual(result['witnesses_checked'], 9)
        self.assertEqual(result['mode'], 'standalone')

    def test_missing_common_group_fails(self):
        body = '\n'.join(x for x in self.body.splitlines() if not x.startswith('Done-when: SC_FLOW '))
        self.assertFalse(self.assess(body=body)['done_supported'])

    def test_missing_or_extra_frozen_criterion_fails(self):
        missing = '\n'.join(x for x in self.body.splitlines() if not x.startswith('Done-when: AC1 '))
        self.assertFalse(self.assess(body=missing)['done_supported'])
        extra = self.body + next(x for x in self.body.splitlines() if x.startswith('Done-when: AC1 ')).replace('AC1 ', 'AC2 ') + '\n'
        self.assertFalse(self.assess(body=extra)['done_supported'])

    def test_duplicate_row_and_missing_proof_fail(self):
        row = next(x for x in self.body.splitlines() if x.startswith('Done-when: AC1 '))
        self.assertFalse(self.assess(body=self.body + row + '\n')['done_supported'])
        self.assertFalse(self.assess(body=self.body.replace('proof: result.txt', 'proof: missing.txt'))['done_supported'])

    def test_tampered_witness_fails(self):
        (self.repo / 'result.txt').write_bytes(b'Changed evidence\n')
        self.assertFalse(self.assess()['done_supported'])

    def test_stale_candidate_or_dirty_tracked_tree_fails(self):
        self.assertFalse(self.assess(candidate='sample/project@' + 'f' * 40)['done_supported'])
        (self.repo / 'result.txt').write_bytes(b'Working tree differs\n')
        self.assertIn('tracked worktree differs from candidate', self.assess()['gaps'])

    def test_criteria_drift_and_wrong_basis_fail(self):
        self.assertFalse(self.assess(criteria_text=self.criteria.replace('Produce a result', 'Skip the result'))['done_supported'])
        self.assertFalse(self.assess(body=self.body.replace('plan V36-1-PLAN-01', 'plan V36-1-PLAN-02'))['done_supported'])

    def test_pending_obligation_prevents_done(self):
        pending = 'Pending: task failure · owner agent · next fix failure · unblocks task · prevents task DONE yes'
        self.assertFalse(self.assess(body=self.body.replace('Pending: none', pending))['done_supported'])

    def test_unrelated_pending_does_not_block_bounded_done(self):
        pending = 'Pending: separate future task · owner Owner · next decide priority · unblocks future work · prevents task DONE no'
        self.assertTrue(self.assess(body=self.body.replace('Pending: none', pending))['done_supported'])

    def test_unknown_not_run_and_na_never_silently_qualify(self):
        for state in ('UNKNOWN', 'NOT_RUN', 'NOT_MET', 'NOT_APPLICABLE'):
            with self.subTest(state=state):
                body = self.body.replace('AC1 → MET', 'AC1 → ' + state)
                self.assertFalse(self.assess(body=body)['done_supported'])

    def test_coordinator_rejected_before_git_or_file_reads(self):
        for label in ({k: v for k, v in self.label.items() if k != 'mode'},
                      {**self.label, 'mode': 'coordinator'}):
            with mock.patch.object(self.module, 'git', side_effect=AssertionError('Git read')):
                with self.assertRaisesRegex(ValueError, 'explicit standalone'):
                    self.assess(label=label)

    def test_foreign_identity_and_parent_as_child_fail(self):
        self.assertFalse(self.assess(issue_ref='other/project#2')['done_supported'])
        self.assertFalse(self.assess(issue_ref='sample/project#1')['done_supported'])
        self.assertFalse(self.assess(task_id='V36-1-WP2')['done_supported'])

    def test_no_fake_acceptance_from_checklist(self):
        result = self.assess()
        self.assertEqual(result['verification'], 'STRUCTURE_AND_LOCAL_BYTES_ONLY')
        self.assertIn('semantic sufficiency', ' '.join(result['limits']))
        self.assertFalse(result['independent_review_established'])

    def test_path_escape_and_symlink_escape_fail(self):
        self.assertFalse(self.assess(body=self.body.replace('proof: result.txt', 'proof: ../result.txt'))['done_supported'])
        with tempfile.TemporaryDirectory() as outside:
            p = Path(outside) / 'outside.txt'; p.write_bytes((self.repo / 'result.txt').read_bytes())
            try:
                (self.repo / 'escape.txt').symlink_to(p)
            except OSError:
                self.skipTest('Symlink creation unavailable')
            self.assertFalse(self.assess(body=self.body.replace('proof: result.txt', 'proof: escape.txt'))['done_supported'])


if __name__ == '__main__':
    unittest.main()
