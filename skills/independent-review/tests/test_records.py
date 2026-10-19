import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from review import render
from review_records import compare_candidates, digest, inspect_records, read_json, schema_check


class RecordChecks(unittest.TestCase):
    def setUp(self):
        self.case = read_json(ROOT / 'examples/records/case.json')
        self.result = read_json(ROOT / 'examples/records/result.json')

    def codes(self):
        return {issue['code'] for issue in inspect_records(self.case, self.result)['issues']}

    def test_sound_bounded_self_review_with_no_findings(self):
        report = inspect_records(self.case, self.result)
        self.assertFalse([issue for issue in report['issues'] if issue['kind'] != 'LIMIT'])
        self.assertEqual(self.result['findings'], [])

    def test_schemas_are_self_contained_and_check_examples(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest('Optional full schema validation not installed.')
        for name, record in [('review-case', self.case), ('review-result', self.result)]:
            schema = read_json(ROOT / 'schemas' / (name + '.schema.json'))
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(record)
            record = copy.deepcopy(record)
            record['unexpected_permission'] = 'merge'
            self.assertTrue(list(Draft202012Validator(schema).iter_errors(record)))

    def test_case_binding_changes_with_actual_meaning(self):
        self.case['owner_intent']['text'] += ' New Owner amendment.'
        self.assertIn('CASE_BINDING', self.codes())

    def test_canonical_binding_is_not_file_byte_hash(self):
        import hashlib
        import json
        formatted = json.dumps(self.case, indent=4).encode()
        self.assertEqual(digest(self.case), digest(__import__('json').loads(formatted)))
        self.assertNotEqual(digest(self.case), hashlib.sha256(formatted).hexdigest())

    def test_wrong_reviewed_candidate_or_base_is_visible(self):
        self.result['candidates'][0]['base_revision'] = 'different-base'
        self.assertIn('CANDIDATE_BINDING', self.codes())

    def test_unknown_reference_is_not_silently_dropped(self):
        self.result['claim_results'][0]['evidence_refs'] = ['ABSENT']
        self.assertIn('UNKNOWN_REFERENCE', self.codes())
        self.assertIn('UNSUPPORTED_CONCLUSION', self.codes())

    def test_reported_assertion_is_not_first_hand_evidence(self):
        self.result['evidence'][0]['kind'] = 'REPORTED'
        self.assertIn('UNSUPPORTED_CONCLUSION', self.codes())

    def test_evidence_for_wrong_candidate_does_not_cover_claim(self):
        self.result['evidence'][0]['candidate_refs'] = []
        self.assertIn('CANDIDATE_COVERAGE', self.codes())

    def test_no_source_lineage_is_visible(self):
        self.result['evidence'][0]['source_refs'] = []
        self.assertIn('SOURCE_LINEAGE', self.codes())

    def test_missing_claim_is_visible(self):
        self.result['claim_results'].pop()
        self.assertIn('MISSING_CLAIM', self.codes())

    def test_narrow_pass_does_not_accept_unrun_parent_claim(self):
        self.result['claim_results'][1].update(status='NOT_RUN', evidence_refs=[], reason='Input unavailable.')
        self.result['verdict']['claim_refs'] = ['ORDER']
        self.assertNotIn('PASS_SCOPE', self.codes())
        self.result['verdict']['claim_refs'].append('EMPTY')
        self.assertIn('PASS_SCOPE', self.codes())

    def test_known_failure_and_unknown_both_survive_rendering(self):
        self.result['claim_results'][0]['status'] = 'CONTRADICTED'
        self.result['claim_results'][1].update(status='NOT_RUN', evidence_refs=[], reason='No runtime.')
        self.result['verdict']['value'] = 'FAIL'
        self.assertNotIn('PASS_SCOPE', self.codes())
        text = render(self.case, self.result)
        for value in ('CONTRADICTED', 'NOT_RUN', 'No runtime.', 'not_assessed', 'native_report'):
            self.assertIn(value, text)

    def test_same_author_cannot_be_relabelled_separate(self):
        self.result['review_type'] = 'SEPARATE_REVIEW'
        self.assertIn('INDEPENDENCE_DECLARATION', self.codes())

    def test_distinct_identity_does_not_remove_shared_oracle_limit(self):
        self.result['reviewer']['author_relation'] = 'DISTINCT'
        self.result['review_type'] = 'SEPARATE_REVIEW'
        self.result['independence']['expectation']['status'] = 'SHARED'
        self.assertIn('SHARED_EXPECTATION', self.codes())
        self.assertNotIn('INDEPENDENCE_DECLARATION', self.codes())

    def test_duplicate_identity_is_diagnosed(self):
        self.result['evidence'].append(copy.deepcopy(self.result['evidence'][0]))
        self.assertIn('DUPLICATE_ID', self.codes())

    def test_supplied_freshness_does_not_rewrite_historical_result(self):
        historical = copy.deepcopy(self.result)
        observations = read_json(ROOT / 'examples/records/current.json')
        self.assertEqual(compare_candidates(self.case, observations)['observations'][0]['status'], 'CHANGED')
        self.assertEqual(self.result, historical)
        self.assertEqual(compare_candidates(self.case, [])['observations'][0]['status'], 'NOT_OBSERVED')

    def test_partial_identity_observation_is_not_a_match(self):
        observed = copy.deepcopy(self.case['candidates'])
        observed[0].pop('sha256')
        self.assertEqual(compare_candidates(self.case, observed)['observations'][0]['status'], 'INCOMPLETE_OBSERVATION')

    def test_unknown_revision_is_not_a_freshness_match(self):
        self.case['candidates'][0]['revision'] = 'UNKNOWN'
        observed = copy.deepcopy(self.case['candidates'])
        self.assertEqual(compare_candidates(self.case, observed)['observations'][0]['status'], 'INCOMPLETE_OBSERVATION')

    def test_duplicate_issued_or_observed_identity_cannot_be_a_match(self):
        observed = copy.deepcopy(self.case['candidates'])
        self.case['candidates'].append(copy.deepcopy(self.case['candidates'][0]))
        report = compare_candidates(self.case, observed)
        self.assertEqual(report['observations'][0]['status'], 'AMBIGUOUS_IDENTITY')
        self.assertIn('DUPLICATE_ID', [item['code'] for item in report['issues']])
        self.case['candidates'].pop()
        observed.append(copy.deepcopy(observed[0]))
        self.assertEqual(compare_candidates(self.case, observed)['observations'][0]['status'], 'AMBIGUOUS_IDENTITY')

    def test_structure_diagnostic_does_not_crash_on_bad_record(self):
        report = inspect_records({'schema_version': 'independent-review.case/v1'}, self.result)
        self.assertEqual(report['consistency'], 'NOT_RUN')


if __name__ == '__main__':
    unittest.main()
