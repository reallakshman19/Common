import importlib.util
import pathlib
import unittest
import json

G = pathlib.Path(__file__).resolve().parents[1] / 'examples' / 'golden'
def load(name):
    spec = importlib.util.spec_from_file_location(name, G / (name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
C0, C1, C2 = map(load, ['baseline', 'candidate_a', 'candidate_b'])
M = {'occurrence_id':'m','url':'https://example.test/series','date':'2026-11-19','time':'09:00'}
E = {'occurrence_id':'e','url':'https://example.test/series','date':'2026-11-19','time':'18:00'}
MAN = {'id':'manual','url':'https://example.test/manual','title':'appointment'}

class Golden(unittest.TestCase):
    def test_baseline_loses_session(self): self.assertEqual(len(C0.merge([M,E,M])),1)
    def test_a_preserves_sessions(self): self.assertEqual({x['occurrence_id'] for x in C1.merge([M,E,M])},{'m','e'})
    def test_a_exact_repeat(self): self.assertEqual(len(C1.merge([M,M])),1)
    def test_b_preserves_a_fix(self): self.assertEqual(C2.merge([M,E,M]),C1.merge([M,E,M]))
    def test_c1_surviving_wrong_case(self):
        saved, suggestions = C1.dismiss([M,E,MAN],[M,E],M)
        self.assertEqual(saved,[MAN]); self.assertEqual(suggestions,[])
    def test_b_preserves_saved_bytes(self):
        original=[M,E,MAN]; saved,_=C2.dismiss(original,[M,E],M)
        self.assertEqual(json.dumps(saved,sort_keys=True),json.dumps(original,sort_keys=True))
    def test_b_dismisses_only_target(self): self.assertEqual(C2.dismiss([M,E,MAN],[M,E],M)[1],[E])
    def test_b_idempotent_dismissal(self):
        saved,suggestions=C2.dismiss([M,E,MAN],[M,E],M)
        self.assertEqual(C2.dismiss(saved,suggestions,M),(saved,suggestions))
    def test_b_reverse_order(self): self.assertEqual({x['occurrence_id'] for x in C2.merge([E,M,E])},{'m','e'})
    def test_b_preserves_unrelated(self): self.assertIn(MAN,C2.dismiss([M,E,MAN],[M,E],M)[0])
