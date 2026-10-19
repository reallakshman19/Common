"""ChatGPT-agent-only activity, strict thresholds and honest incomplete coverage."""
import importlib
import io
import json
import tempfile
from contextlib import redirect_stdout
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def event(kind, at, **fields):
    return {'event': kind, 'at': at, **fields}


def events(turns=0, minutes=0, surface='chatgpt-agent', coverage='SELF_RECORDED'):
    rows = [event('session', '2026-10-19T10:00:00Z', session_id='agent-episode-1',
                  surface=surface, observation=coverage)]
    if minutes:
        rows += [event('turn-start', '2026-10-19T10:00:00Z', turn_id='timed'),
                 event('turn-end', f'2026-10-19T10:{minutes:02d}:00Z', turn_id='timed')]
    for n in range(turns):
        rows.append(event('github', f'2026-10-19T10:40:{n:02d}Z', turn_id=f'turn-{n}',
                          tool='github_fetch', outcome='success'))
    return rows


class ActivityTests(unittest.TestCase):
    def setUp(self):
        try:
            self.module = importlib.import_module('standalone_activity_v36')
        except ModuleNotFoundError:
            self.fail('Standalone activity recorder/evaluator is not implemented')

    def test_five_turns_and_35_minutes_do_not_cross_strict_thresholds(self):
        r = self.module.summarize(events(5, 35))
        self.assertFalse(r['buddy_suggestion_due'])
        self.assertEqual(r['github_access_turns_observed'], 5)
        self.assertEqual(r['closed_active_minutes_observed'], 35)

    def test_six_distinct_github_turns_trigger_without_time_threshold(self):
        self.assertTrue(self.module.summarize(events(6))['buddy_suggestion_due'])

    def test_36_minutes_trigger_without_github(self):
        self.assertTrue(self.module.summarize(events(minutes=36))['buddy_suggestion_due'])

    def test_many_calls_in_one_turn_are_not_many_turns(self):
        rows = events()
        rows += [event('github', f'2026-10-19T10:40:{n:02d}Z', turn_id='one',
                       tool='github_fetch', outcome='success') for n in range(12)]
        r = self.module.summarize(rows)
        self.assertEqual(r['github_tool_calls_observed'], 12)
        self.assertEqual(r['github_access_turns_observed'], 1)
        self.assertFalse(r['buddy_suggestion_due'])

    def test_work_and_other_surfaces_are_exempt(self):
        for surface in ('chatgpt-work', 'other'):
            with self.subTest(surface=surface):
                r = self.module.summarize(events(6, 36, surface))
                self.assertFalse(r['policy_applies'])
                self.assertFalse(r['buddy_suggestion_due'])

    def test_unknown_surface_does_not_claim_an_established_exemption(self):
        r = self.module.summarize(events(6, 36, 'unknown'))
        self.assertIsNone(r['policy_applies'])
        self.assertEqual(r['applicability'], 'UNKNOWN')

    def test_overlap_does_not_double_count_active_time(self):
        rows = events() + [event('turn-start', '2026-10-19T10:00:00Z', turn_id='a'),
                           event('turn-start', '2026-10-19T10:05:00Z', turn_id='b'),
                           event('turn-end', '2026-10-19T10:20:00Z', turn_id='a'),
                           event('turn-end', '2026-10-19T10:25:00Z', turn_id='b')]
        self.assertEqual(self.module.summarize(rows)['closed_active_minutes_observed'], 25)

    def test_idle_gap_is_not_active_work(self):
        rows = events() + [event('turn-start', '2026-10-19T10:00:00Z', turn_id='a'),
                           event('turn-end', '2026-10-19T10:05:00Z', turn_id='a'),
                           event('turn-start', '2026-10-20T10:00:00Z', turn_id='b'),
                           event('turn-end', '2026-10-20T10:05:00Z', turn_id='b')]
        self.assertEqual(self.module.summarize(rows)['closed_active_minutes_observed'], 10)

    def test_open_turn_is_not_counted_as_unobserved_active_duration(self):
        rows = events() + [event('turn-start', '2026-10-19T10:00:00Z', turn_id='a')]
        r = self.module.summarize(rows)
        self.assertEqual(r['closed_active_minutes_observed'], 0)
        self.assertEqual(r['open_turns'], ['a'])
        self.assertEqual(r['coverage'], 'INCOMPLETE')

    def test_unavailable_measurement_is_visible_and_not_a_quality_failure(self):
        rows = events() + [event('gap', '2026-10-19T10:01:00Z', reason='host IDs unavailable')]
        r = self.module.summarize(rows)
        self.assertEqual(r['coverage'], 'INCOMPLETE')
        self.assertEqual(r['threshold_state'], 'UNKNOWN')
        self.assertFalse(r['buddy_suggestion_due'])

    def test_observed_lower_bound_over_threshold_triggers_despite_gap(self):
        rows = events(6) + [event('gap', '2026-10-19T10:42:00Z', reason='earlier history absent')]
        r = self.module.summarize(rows)
        self.assertTrue(r['buddy_suggestion_due'])
        self.assertEqual(r['coverage'], 'INCOMPLETE')

    def test_suggestion_is_once_per_episode_and_does_not_reset_counts(self):
        rows = events(6)
        rows.append(event('buddy-suggested', '2026-10-19T10:42:00Z', reference='current reply'))
        r = self.module.summarize(rows)
        self.assertFalse(r['buddy_suggestion_due'])
        self.assertTrue(r['threshold_crossed_observed'])
        self.assertEqual(r['github_access_turns_observed'], 6)

    def test_premature_suggestion_does_not_satisfy_later_trigger(self):
        rows = events()
        rows.append(event('buddy-suggested', '2026-10-19T10:01:00Z', reference='old suggestion'))
        rows += events(6)[1:]
        self.assertTrue(self.module.summarize(rows)['buddy_suggestion_due'])

    def test_no_reset_by_new_task_or_duplicate_session(self):
        rows = events(6) + [events()[0]]
        with self.assertRaises(ValueError):
            self.module.summarize(rows)

    def test_duplicate_open_and_reversed_clock_are_invalid(self):
        rows = events() + [event('turn-start', '2026-10-19T10:02:00Z', turn_id='a')]
        for bad in (event('turn-start', '2026-10-19T10:03:00Z', turn_id='a'),
                    event('turn-end', '2026-10-19T10:01:00Z', turn_id='a')):
            with self.subTest(event=bad), self.assertRaises(ValueError):
                self.module.summarize(rows + [bad])

    def test_cli_exempt_surface_does_not_create_a_log(self):
        import standalone_activity_cli_v36 as cli
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'activity.jsonl'
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(['start', '--log', str(path), '--surface', 'chatgpt-work', '--session-id', 'work-ep'])
            self.assertEqual(code, 0)
            self.assertFalse(path.exists())
            self.assertFalse(json.loads(out.getvalue())['policy_applies'])

    def test_invalid_append_preserves_existing_log_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'activity.jsonl'
            self.module.append_event(path, events()[0])
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                self.module.append_event(path, events()[0])
            self.assertEqual(path.read_bytes(), before)

    def test_missing_turn_identity_is_not_invented(self):
        rows = events() + [event('github', '2026-10-19T10:01:00Z', tool='github_fetch', outcome='failure')]
        r = self.module.summarize(rows)
        self.assertEqual(r['github_access_turns_observed'], 0)
        self.assertEqual(r['github_tool_calls_observed'], 1)
        self.assertEqual(r['threshold_state'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
