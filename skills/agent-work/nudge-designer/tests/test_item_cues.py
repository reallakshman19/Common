"""Mechanical cue screening remains separate from verb fit and subject judgment."""
import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def item(verb='explain'):
    return {'id': 'I-01', 'verb': verb, 'question': 'Why does friction oppose sliding?',
            'options': [{'id': 'A', 'text': 'Because friction always resists relative motion'},
                        {'id': 'B', 'text': 'Because mass always becomes exactly zero'},
                        {'id': 'C', 'text': 'Because speed never changes its direction'}], 'answer': 'A'}


class ItemCueTests(unittest.TestCase):
    def setUp(self):
        try: self.module = importlib.import_module('nd_item_cues')
        except ModuleNotFoundError: self.fail('Selected-response cue helper not implemented')

    def scan(self, row=None, **kw):
        return self.module.inspect_items({'items': [row or item()]}, **kw)

    def test_generator_gets_computed_lengths_and_correct_only_shared_word(self):
        r = self.scan()
        self.assertEqual(r['items'][0]['word_counts'], {'A': 6, 'B': 6, 'C': 6})
        self.assertIn('friction', r['items'][0]['correct_only_question_words'])
        self.assertIn('SHARED_WORD_KEY_ONLY', r['items'][0]['flags'])

    def test_balanced_causal_options_are_not_banned_for_reasoning_words(self):
        r = self.scan()['items'][0]
        self.assertNotIn('REASONING_KEY_ONLY', r['flags'])
        self.assertEqual(r['reasoning_markers']['B'], ['because'])

    def test_reasoning_word_only_in_key_is_a_signal_not_a_subject_verdict(self):
        row = item(); row['options'][1]['text'] = 'Mass becomes zero'
        row['options'][2]['text'] = 'Speed remains unchanged'
        r = self.scan(row)
        self.assertIn('REASONING_KEY_ONLY', r['items'][0]['flags'])
        self.assertIn('LONGEST_KEY', r['items'][0]['flags'])
        self.assertFalse(r['physics_evaluated'])
        self.assertFalse(r['format_approved'])

    def test_retrieve_can_use_units_or_signs(self):
        row = item('retrieve')
        row.update(question='Which unit represents force?', options=[{'id': 'A', 'text': 'N'},
                   {'id': 'B', 'text': 'J'}, {'id': 'C', 'text': 'Pa'}])
        r = self.scan(row)
        self.assertEqual(r['items'][0]['word_counts']['A'], 1)
        self.assertNotIn('BARE_VALUE_FOR_REASONING_VERB', r['items'][0]['flags'])

    def test_bare_numbers_do_not_establish_an_explain_option(self):
        row = item(); row['options'][0]['text'] = '12'
        self.assertIn('BARE_VALUE_FOR_REASONING_VERB', self.scan(row)['items'][0]['flags'])

    def test_shared_stopwords_are_visible_with_substantive_subset_separate(self):
        row = item(); row['question'] = 'Which is the correct choice?'
        row['options'][0]['text'] = 'The moving body'
        result = self.scan(row)['items'][0]
        self.assertIn('the', result['correct_only_question_words'])
        self.assertNotIn('the', result['substantive_correct_only_question_words'])

    def test_case_and_unicode_words_are_normalized_for_screening(self):
        row = item(); row['question'] = 'Why is CAFÉ moving?'
        row['options'][0]['text'] = 'The café is moving'
        self.assertIn('café', self.scan(row)['items'][0]['correct_only_question_words'])

    def test_word_limit_is_only_applied_when_supplied(self):
        self.assertNotIn('WORD_LIMIT', self.scan()['items'][0]['flags'])
        self.assertIn('WORD_LIMIT', self.scan(max_words=5)['items'][0]['flags'])

    def test_zero_flags_does_not_approve_physics_or_verb_fit(self):
        row = item('retrieve'); row.update(question='Choose a unit', options=[
            {'id': 'A', 'text': 'N'}, {'id': 'B', 'text': 'J'}, {'id': 'C', 'text': 'Pa'}])
        r = self.scan(row)
        self.assertEqual(r['items'][0]['flags'], [])
        self.assertFalse(r['format_approved'])
        self.assertFalse(r['verb_fit_evaluated'])

    def test_missing_or_duplicate_item_option_ids_and_bad_key_refuse(self):
        for mutation in ('item', 'option', 'answer', 'empty'):
            data = {'items': [item()]}
            if mutation == 'item': data['items'].append(item())
            if mutation == 'option': data['items'][0]['options'][1]['id'] = 'A'
            if mutation == 'answer': data['items'][0]['answer'] = 'Z'
            if mutation == 'empty': data['items'][0]['options'][0]['text'] = ''
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.module.inspect_items(data)

    def test_selected_profile_reaches_rendered_generator_brief_only_when_selected(self):
        from nd_profiles import load_profiles, profile_digest
        from nd_contract import validate_plan
        from nd_io import load_json
        from nd_render import render_nudge
        profiles = load_profiles()
        self.assertIn('selected-response', profiles)
        intent = load_json(ROOT / 'examples/logic/intent.json')
        plan = load_json(ROOT / 'examples/logic/plan.json')
        ordinary = render_nudge(intent, plan, plan['nudges'][0]['id'], profiles)
        self.assertNotIn('Generator pre-return', ordinary)
        plan['profile_ids'].append('selected-response')
        plan['nudges'][0]['profile_ids'].append('selected-response')
        plan['profiles_sha256'] = profile_digest(profiles, plan['profile_ids'])
        rendered = render_nudge(intent, plan, plan['nudges'][0]['id'], profiles)
        self.assertIn('Generator pre-return', rendered)
        self.assertIn('option word counts', rendered)
        self.assertIn('tile verb', rendered)
        self.assertIn('plausible wrong', rendered)


if __name__ == '__main__': unittest.main()
