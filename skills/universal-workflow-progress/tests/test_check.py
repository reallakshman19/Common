import importlib.util
import unittest
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"scripts/check.py"
spec=importlib.util.spec_from_file_location("progress_check",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
WF={"id":"w","enabled":True,"repository":"owner/repo","issue":8,
    "stages":[{"id":"a","title":"Preparation","evidence_markers":["STAGE_A_RECORD"],"trusted_authors":["g1"]},
              {"id":"b","title":"Investigation","evidence_markers":["STAGE_B_RECORD"],"trusted_authors":["g2"]}]}

class MonitorTests(unittest.TestCase):
    def test_valid_config(self):
        m.validate({"schema":m.SCHEMA,"workflows":[WF]})
    def test_untrusted_author(self):
        state=m.snapshot(WF,[{"id":1,"body":"STAGE_A_RECORD","user":{"login":"stranger"}}],"now")
        self.assertEqual(state["stages"][0]["state"],"UNKNOWN")
    def test_unverified_submission(self):
        state=m.snapshot(WF,[{"id":1,"body":"STAGE_A_RECORD","user":{"login":"g1"}}],"now")
        self.assertEqual((state["stages"][0]["state"],state["stages"][0]["verification"]),("SUBMITTED","UNVERIFIED"))
    def test_first_run_no_alert(self):
        self.assertEqual(m.compare(None,{"workflows":[m.snapshot(WF,[],"now")]}),[])
    def test_stage_change(self):
        a=m.snapshot(WF,[],"a")
        b=m.snapshot(WF,[{"id":1,"body":"STAGE_B_RECORD","user":{"login":"g2"}}],"b")
        self.assertEqual(m.compare({"workflows":[a]},{"workflows":[b]})[0]["stage"],"b")
    def test_duplicate_not_realerted(self):
        c=[{"id":1,"body":"STAGE_A_RECORD","user":{"login":"g1"}}]
        a=m.snapshot(WF,c,"a")
        b=m.snapshot(WF,c,"b")
        self.assertEqual(m.compare({"workflows":[a]},{"workflows":[b]}),[])
    def test_changed_body_alert(self):
        a=m.snapshot(WF,[{"id":1,"body":"STAGE_A_RECORD","user":{"login":"g1"}}],"a")
        b=m.snapshot(WF,[{"id":1,"body":"STAGE_A_RECORD updated","user":{"login":"g1"}}],"b")
        self.assertEqual(len(m.compare({"workflows":[a]},{"workflows":[b]})),1)
    def test_enabled_requires_trusted_author(self):
        wrong={**WF,"stages":[{**WF["stages"][0],"trusted_authors":[]}]}
        with self.assertRaises(ValueError):
            m.validate({"schema":m.SCHEMA,"workflows":[wrong]})

if __name__=="__main__":
    unittest.main()
