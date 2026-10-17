"""Verify printed candidate dimensions in the generated vector PDF, not physical prints."""
from __future__ import annotations
import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from make_mockup_kit import build,validate

CFG=json.loads((ROOT/"mockup_candidate_v1.json").read_text())
def near(v,w):return math.isclose(v,w,abs_tol=.05)

class MockupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)/"kit.pdf"
        build(CFG,cls.out)
        cls.doc=fitz.open(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.doc.close();cls.tmp.cleanup()

    def test_candidate_parameters(self):
        validate(CFG)
        self.assertIn("NOT_FINAL",CFG["status"])

    def test_seven_a4_vector_pages(self):
        self.assertEqual(len(self.doc),7)
        for p in self.doc:
            self.assertTrue(near(p.rect.width*25.4/72,210))
            self.assertTrue(near(p.rect.height*25.4/72,297))
            self.assertGreater(len(p.get_drawings()),2)

    def test_two_pillar_tiles_180_by_145(self):
        for i in (0,1):
            r=self.doc[i].get_drawings()[0]["rect"]
            self.assertTrue(near(r.width*25.4/72,180))
            self.assertTrue(near(r.height*25.4/72,145))
        self.assertEqual(CFG["template"]["overlap"],10)

    def test_door_outlines_69_by_227(self):
        shapes=[x["rect"] for x in self.doc[2].get_drawings()
                if x["items"] and x["items"][0][0]=="re"]
        leaves=[r for r in shapes if near(r.width*25.4/72,69)]
        self.assertEqual(len(leaves),2)
        for r in leaves:self.assertTrue(near(r.height*25.4/72,227))
        self.assertEqual(140-2*69,2)
        self.assertEqual(230-227,3)

    def test_narasimha_envelopes_scale(self):
        for index,width in ((3,92),(4,155)):
            r=self.doc[index].get_drawings()[0]["rect"]
            self.assertTrue(near(r.width*25.4/72,width))
            self.assertTrue(near(r.height*25.4/72,180))

    def test_every_page_has_100mm_calibration(self):
        for p in self.doc:
            lines=[x["rect"] for x in p.get_drawings() if
                   near(x["rect"].height,0) and near(x["rect"].width*25.4/72,100)]
            self.assertTrue(lines,p.number+1)

    def test_text_not_off_sheet(self):
        for p in self.doc:
            for b in p.get_text("dict")["blocks"]:
                if b["type"]!=0:continue
                for ln in b["lines"]:
                    for sp in ln["spans"]:
                        r=fitz.Rect(sp["bbox"])
                        self.assertGreaterEqual(r.x0,-.1)
                        self.assertGreaterEqual(r.y0,-.1)
                        self.assertLessEqual(r.x1,p.rect.width+.1)
                        self.assertLessEqual(r.y1,p.rect.height+.1)

    def test_assembly_page_requires_clear_rod_corridor(self):
        instructions=self.doc[5].get_text()
        receipt=self.doc[6].get_text()
        self.assertIn("NEVER glue flush",instructions)
        self.assertIn("shaft corridor OPEN",instructions)
        self.assertIn("140 mm below",instructions)
        self.assertIn("Open shaft corridor",receipt)

    def test_oversize_door_rejected(self):
        c=copy.deepcopy(CFG);c["leaves"]["width"]=71
        with self.assertRaises(AssertionError):validate(c)

    def test_unfitted_height_rejected(self):
        c=copy.deepcopy(CFG);c["leaves"]["height"]=230
        with self.assertRaises(AssertionError):validate(c)

    def test_no_tiling_overlap_rejected(self):
        c=copy.deepcopy(CFG);c["template"]["overlap"]=0
        with self.assertRaises(AssertionError):validate(c)

if __name__=="__main__":unittest.main()
