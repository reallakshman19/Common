"""Regression coverage for the public successor instructions, without live I/O."""
import copy
import unittest

from test_generators_v36 import packet
from test_successor_v36 import HEAD, LABEL, PLAN, Provider
import prompt_2pass_v36 as two
import prompt_3pass_v36 as three
import successor_v36 as successor


class ReconstructionTests(unittest.TestCase):
    def assert_policy(self, text):
        self.assertIn('No takeover questionnaire', text)
        self.assertIn('additional reconstruction is NOT_APPLICABLE', text)
        self.assertIn('BuddyRunner, two-pass or three-pass', text)
        self.assertIn('own words', text)
        self.assertIn('source-backed', text)

    def test_cold_instructions_apply_to_both_modes(self):
        for mode in ('standalone', 'coordinator'):
            with self.subTest(mode=mode):
                label = copy.deepcopy(LABEL)
                label['mode'] = mode
                result = successor.build_packet(label, PLAN, Provider(), [4])
                rendered = successor.render_markdown(result)
                self.assert_policy(rendered)
                self.assertIn(label['label']['main_aim'], rendered)
                self.assertIn(HEAD, rendered)
                self.assertEqual(result['snapshot']['accepted_complete'], 0)

    def test_two_pass_keeps_its_two_native_passes(self):
        rendered = two.generate_two_pass(packet(), 'V36-1-WP1')
        self.assert_policy(rendered)
        self.assertEqual(rendered.count('PASS 1 —'), 1)
        self.assertEqual(rendered.count('PASS 2 —'), 1)
        self.assertNotIn('PASS 3 —', rendered)

    def test_onboard_continuation_is_emitted_in_both_modes(self):
        for mode in ('standalone', 'coordinator'):
            with self.subTest(mode=mode):
                label = copy.deepcopy(LABEL)
                label['mode'] = mode
                result = successor.build_packet(label, PLAN, Provider(), [4])
                rendered = successor.render_markdown(result)
                self.assertIn('usable Oracle OnBoard Prompt', rendered)
                self.assertIn('No separate reconstruction', rendered)
                self.assertIn('Treat its explanation as\nrevisable', rendered)
                self.assertIn('remaining parent work', rendered)
                self.assertIn('existing authority', rendered)
                self.assert_policy(rendered)
                self.assertIn(label['label']['main_aim'], rendered)
                self.assertIn(HEAD, rendered)
                self.assertEqual(result['snapshot']['accepted_complete'], 0)

    def test_three_pass_keeps_its_three_native_passes(self):
        rendered = three.generate_three_pass(packet(), 'V36-1-WP1')
        self.assert_policy(rendered)
        for n in (1, 2, 3):
            self.assertEqual(rendered.count(f'PASS {n} —'), 1)
        self.assertNotIn('PASS 4 —', rendered)

    def test_buddy_native_stages_have_no_extra_exam_or_stage(self):
        for phase in ('1a', '1b', '2', 'Y'):
            with self.subTest(phase=phase):
                text = successor.buddy_prompt(
                    phase, handover_id='case-reuse', parent=PLAN['parent'],
                    assessed_sha=HEAD,
                    evidence_url='https://github.com/sample/project/issues/1#issuecomment-1',
                    body_digest='a' * 64)
                self.assert_policy(text)
                self.assertIn(f'phase={phase}', text)
                if phase == '1b':
                    self.assertIn('PRODUCT_IMPLEMENTATION=HOLD', text)
                elif phase == '2':
                    self.assertIn('PREDECESSOR=STOP', text)
                elif phase == 'Y':
                    self.assertIn('No new review round', text)


if __name__ == '__main__':
    unittest.main()
