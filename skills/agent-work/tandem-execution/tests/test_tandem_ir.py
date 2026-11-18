import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ir_candidates", ROOT / "examples/tandem_ir/candidates.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
M = {"occurrence_id": "m", "url": "same", "metadata": {"saved": True}}
E = {"occurrence_id": "e", "url": "same"}
MAN = {"url": "same", "title": "manual"}
UNKNOWN = {"url": "other"}
SAVED = [M, MAN]
SUGGESTIONS = [M, E, MAN, UNKNOWN]


class TandemIRGolden(unittest.TestCase):
    def test_baseline_destroys_saved_and_other_occurrences(self):
        self.assertEqual(mod.c0(SAVED, SUGGESTIONS, M), ([], [UNKNOWN]))

    def test_a_protects_saved_but_b_wrong_case_detects_identity_bug(self):
        self.assertEqual(mod.c1(SAVED, SUGGESTIONS, M), (SAVED, [UNKNOWN]))
        self.assertNotEqual(mod.c1(SAVED, SUGGESTIONS, M), (SAVED, [E, MAN, UNKNOWN]))

    def test_b_correction_keeps_other_occurrences_and_saved_metadata(self):
        self.assertEqual(mod.c2(SAVED, SUGGESTIONS, M), (SAVED, [E, MAN, UNKNOWN]))

    def test_a_reciprocal_challenge_detects_b_missing_identity_bug(self):
        self.assertEqual(mod.c2(SAVED, SUGGESTIONS, MAN), (SAVED, [M, E]))
        self.assertNotEqual(mod.c2(SAVED, SUGGESTIONS, MAN), (SAVED, SUGGESTIONS))

    def test_final_preserves_both_corrections_and_new_guard(self):
        self.assertEqual(mod.c3(SAVED, SUGGESTIONS, M), (SAVED, [E, MAN, UNKNOWN]))
        for target in (MAN, UNKNOWN, {"occurrence_id": ""}, {"occurrence_id": " "}, {"occurrence_id": 7}):
            with self.subTest(target=target):
                self.assertEqual(mod.c3(SAVED, SUGGESTIONS, target), (SAVED, SUGGESTIONS))

    def test_final_is_idempotent_and_preserves_inputs(self):
        saved, suggestions = mod.c3(SAVED, SUGGESTIONS, M)
        self.assertEqual(mod.c3(saved, suggestions, M), (saved, suggestions))
        self.assertEqual(SAVED, [M, MAN])
        self.assertEqual(SUGGESTIONS, [M, E, MAN, UNKNOWN])


if __name__ == "__main__":
    unittest.main()
