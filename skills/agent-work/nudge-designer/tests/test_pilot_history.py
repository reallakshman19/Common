"""Preserved actual returns remain usable after a semantic working revision."""
import hashlib
import unittest

from adapter_support import ROOT
from nd_contract import validate_plan
from nd_io import ContractError, load_json
from nd_profiles import load_profiles
from nd_reconcile import impact_report
from nd_returns import receive
from nd_team import task_binding


class PilotHistoryTests(unittest.TestCase):
    def setUp(self):
        self.folder = ROOT / 'examples/adapter-cycle'
        self.profiles = load_profiles()

    def test_archived_inputs_returns_and_reviewer_manifest_remain_exact(self):
        for name, checksum in load_json(self.folder / 'issued-artifacts.sha256.json').items():
            self.assertEqual(hashlib.sha256((self.folder / name).read_bytes()).hexdigest(), checksum, name)
        reviewer = self.folder / 'reviewer'
        before = load_json(reviewer / 'input-manifest-before.json')
        self.assertEqual(before, load_json(reviewer / 'input-manifest-after.json'))
        self.assertEqual(len(before), 22)
        for name, checksum in before.items():
            self.assertEqual(hashlib.sha256((reviewer / name).read_bytes()).hexdigest(), checksum, name)
        for role in ('worker', 'specialist', 'reviewer'):
            folder = self.folder / role
            intent, plan, report = [load_json(folder / name)
                                    for name in ('intent.json', 'plan.json', 'return.json')]
            result = receive(intent, plan, report, self.profiles)
            self.assertEqual(result['status'], 'RETURN_RECORDED')
            self.assertEqual(result['accepted_outcomes'], [])
            self.assertEqual(report['binding'], load_json(folder / 'issued-binding.json'))
            self.assertEqual(report['binding'], load_json(folder / 'packet.json')['binding'])
            self.assertEqual(result['native_report']['content'].encode('utf-8'),
                             (folder / report['native_report']['locator']).read_bytes())
            self.assertFalse(result['execution_verified'])

    def test_current_revision_corrects_meaning_without_rewriting_issued_evidence(self):
        old = self.folder / 'specialist'
        current = self.folder / 'current-specialist'
        old_intent, old_plan = [load_json(old / name) for name in ('intent.json', 'plan.json')]
        intent, plan = [load_json(current / name) for name in ('intent.json', 'plan.json')]
        self.assertEqual(validate_plan(intent, plan, self.profiles)['status'], 'STRUCTURALLY_VALID')
        self.assertIn('20 m/s', old_plan['handover']['next_action'])
        self.assertIn('18 m/s', plan['handover']['next_action'])
        old_items = {row['id']: row for row in old_intent['items']}
        items = {row['id']: row for row in intent['items']}
        self.assertEqual(items['C-PHYSICS'], old_items['C-PHYSICS'])
        self.assertEqual(items['C-CLAIMS'], old_items['C-CLAIMS'])
        self.assertEqual(items['U-RESPONSE'], old_items['U-RESPONSE'])
        self.assertEqual((items['F-PREREQ']['kind'], items['F-PREREQ']['state']), ('PROPOSAL', 'PROPOSED'))
        self.assertEqual(intent['outcomes'], old_intent['outcomes'])
        self.assertEqual(plan['handover']['remaining'], ['R-LEARN', 'U-RESPONSE', 'O-CONTENT', 'O-LEARNING'])
        self.assertIn('N-TRANSFER', plan['handover']['next_action'])
        self.assertEqual(impact_report(old_intent, old_plan, intent, self.profiles), load_json(current / 'impact.json'))
        report = load_json(old / 'return.json')
        with self.assertRaisesRegex(ContractError, 'issued intent/plan snapshots'):
            receive(intent, plan, report, self.profiles)
        for audience in ('owner', 'successor'):
            packet = load_json(current / (audience + '-packet.json'))
            self.assertEqual(packet['binding'], task_binding(intent, plan, 'N-TRANSFER'))
            self.assertIn('18 m/s', packet['content'])
            self.assertFalse(packet['execution_dispatched'])


if __name__ == '__main__':
    unittest.main()
