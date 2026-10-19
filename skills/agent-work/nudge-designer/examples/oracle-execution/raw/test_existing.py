import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("session", Path(__file__).resolve().parents[1] / "work/session.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SearchSession = module.SearchSession


class ExistingChecks(unittest.TestCase):
    def test_success_and_order(self):
        s = SearchSession()
        t = s.begin("P", "bolt")
        self.assertTrue(s.snapshot()["busy"])
        self.assertTrue(s.finish(t, ["z", "a"]))
        self.assertEqual(s.snapshot()["rows"], ["z", "a"])
        self.assertFalse(s.snapshot()["busy"])

    def test_other_scope_is_ignored(self):
        s = SearchSession()
        a = s.begin("A", "old")
        b = s.begin("B", "new")
        self.assertFalse(s.finish(a, ["old"]))
        self.assertTrue(s.snapshot()["busy"])
        self.assertTrue(s.finish(b, ["new"]))

    def test_current_error_and_recovery(self):
        s = SearchSession()
        a = s.begin("A", "old")
        self.assertTrue(s.fail(a, "offline"))
        self.assertEqual(s.snapshot()["error"], "offline")
        b = s.begin("A", "new")
        self.assertTrue(s.finish(b, ["ok"]))
        self.assertIsNone(s.snapshot()["error"])

    def test_snapshot_is_detached(self):
        s = SearchSession()
        a = s.begin("A", "q")
        rows = [{"id": 2}]
        s.finish(a, rows)
        rows[0]["id"] = 99
        snapshot = s.snapshot()
        snapshot["rows"][0]["id"] = 88
        self.assertEqual(s.snapshot()["rows"], [{"id": 2}])


if __name__ == "__main__":
    unittest.main()
