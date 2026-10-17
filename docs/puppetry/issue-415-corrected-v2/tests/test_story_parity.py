"""Boundary tests on archived story; these do not rehearse the puppet show."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from story_parity import inspect, seconds

class StoryParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "story", self.root / "story")
        shutil.copytree(ROOT / "scenes", self.root / "scenes")

    def test_four_scenes_and_slots_pass(self):
        self.assertTrue(inspect(self.root)["passed"], inspect(self.root))

    def test_modified_scene_line_detected(self):
        p = self.root/"scenes"/"SCENE_02.md"
        p.write_text(p.read_text().replace("Yes, Father!","Maybe, Father!",1),encoding="utf-8")
        self.assertFalse(inspect(self.root)["passed"])

    def test_missing_clock_second_detected(self):
        p = self.root/"scenes"/"SCENE_01.md"
        s = p.read_text()
        p.write_text(s.replace("0:08-0:17","0:08-0:16",1),encoding="utf-8")
        self.assertFalse(inspect(self.root)["passed"])

    def test_invalid_seconds_rejected(self):
        with self.assertRaises(ValueError):
            seconds("1:65")


if __name__ == "__main__":
    unittest.main()
