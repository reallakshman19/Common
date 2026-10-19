"""Focused local checks for ONBOARD-DEMO-01 draft persistence."""

import unittest

from drafts import load_drafts, save_drafts


class DraftPersistenceTests(unittest.TestCase):
    def test_explicit_zero_and_nonzero_survive_round_trip(self):
        workspace = {}
        edits = {"zero": 0, "float_zero": 0.0, "normal": 12.5}

        save_drafts(workspace, "model-a", edits)
        loaded = load_drafts(workspace, "model-a")

        self.assertEqual(loaded, edits)
        self.assertIs(type(loaded["zero"]), int)
        self.assertIs(type(loaded["float_zero"]), float)

    def test_none_and_absence_do_not_become_zero_drafts(self):
        workspace = {}

        save_drafts(workspace, "model-a", {"unset": None, "normal": 3.5})
        loaded = load_drafts(workspace, "model-a")

        self.assertEqual(loaded, {"normal": 3.5})
        self.assertNotIn("unset", loaded)
        self.assertNotIn("absent", loaded)

    def test_saving_one_model_does_not_disturb_another(self):
        workspace = {}
        save_drafts(workspace, "model-b", {"mass": 8.25})

        save_drafts(workspace, "model-a", {"mass": 2.5})

        self.assertEqual(load_drafts(workspace, "model-a"), {"mass": 2.5})
        self.assertEqual(load_drafts(workspace, "model-b"), {"mass": 8.25})

    def test_unknown_model_loads_empty_without_creating_entry(self):
        workspace = {"model-a": {"mass": 4.5}}

        self.assertEqual(load_drafts(workspace, "unknown"), {})
        self.assertNotIn("unknown", workspace)
        self.assertEqual(workspace, {"model-a": {"mass": 4.5}})

    def test_loaded_dictionary_is_a_copy(self):
        workspace = {}
        save_drafts(workspace, "model-a", {"mass": 7.25})
        loaded = load_drafts(workspace, "model-a")

        loaded["mass"] = 99
        loaded["new"] = 6

        self.assertEqual(workspace["model-a"], {"mass": 7.25})
        self.assertEqual(load_drafts(workspace, "model-a"), {"mass": 7.25})
        self.assertIsNot(loaded, workspace["model-a"])

    def test_save_replaces_previous_drafts(self):
        workspace = {}
        save_drafts(workspace, "model-a", {"old": 4, "overwritten": 5})

        save_drafts(workspace, "model-a", {"overwritten": 6, "unset": None})

        self.assertEqual(load_drafts(workspace, "model-a"), {"overwritten": 6})

    def test_none_only_and_empty_saves_replace_with_empty_drafts(self):
        workspace = {"model-a": {"old": 4}}

        save_drafts(workspace, "model-a", {"unset": None})
        self.assertEqual(load_drafts(workspace, "model-a"), {})
        save_drafts(workspace, "model-a", {"old": 4})
        save_drafts(workspace, "model-a", {})
        self.assertEqual(load_drafts(workspace, "model-a"), {})


if __name__ == "__main__":
    unittest.main()
