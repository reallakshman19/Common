"""R3: existing v3.6 successor one-URL twelve-section cold recovery tests."""
from __future__ import annotations
import base64
import contextlib
import copy
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import issue_spine_read_v36 as spine
import successor_issue_recovery_v36 as rec
import successor_v36 as existing
from test_issue_spine_read_v36 import EventFake, REPO, PARENT, ISSUE_URL

ORIGINAL_DOC=(
    "# Owner formalised concerns\n"
    "## 1. Problem statement\n"
    "A tenth agent must reconstruct the original engineering WHY, exact source "
    "fixtures, failed physical conversion, adopted changes and held gates "
    "without predecessor ChatGPT conversations. This is a real Owner statement.\n"
    "## 4. Lossless issue lineage\n"
    "Issue #123 → ~~Issue #125~~ → Issue #126 is illustrative, not asserted.\n"
    "## 6. v3.5 coding practices the Owner wants ported\n"
    "Source-first reconciliation, no duplicate engines and real test evidence "
    "must be native to v3.6 without older runtime dependencies.\n"
    "## 9.1 3D_Converters: Issue #274\n"
    "A reported 41 branches, 423 physical components, 2,961 FactRecords and "
    "zero accepted Match-1 or Final weights are NOT product acceptance.\n"
    "## 10. Owner-required acceptance demonstration\n"
    "1. Recover original WHY and corrections. 2. Find exact fixtures and "
    "complete golden or declare UNKNOWN. 3. Follow source through real output. "
    "4. Retain parked reasoning and failures. 5. Explain one safe next step.\n"
)

class R3Fake(EventFake):
    def __init__(self):
        super().__init__()
        self.idx["references"][0]["id"]="OWNER_STATEMENT"
        self.idx["references"][1]["id"]="C1B_RECEIPT"
        self.manifest={"schema":"v36.source-custody/v1",
            "repository":"reallakshman19/3D_Converters",
            "revision":"b"*40,"artifacts":[],"issue_records":[]}
        self.manifest_blob=json.dumps(self.manifest).encode()
        self.manifest_sha=spine.hashlib.sha1(
            b"blob "+str(len(self.manifest_blob)).encode()+bytes([0])+
            self.manifest_blob).hexdigest()
        self.idx["references"].extend([
            {"id":"REVISED_PLAN","kind":"ISSUE_COMMENT",
             "repository":REPO,"revision":None,"path":None,
             "blob_sha1":None,"issue_number":400,"comment_id":12348,
             "claimed_actor":"reallakshman19","schema":None},
            {"id":"R2_VERIFICATION","kind":"ISSUE_COMMENT",
             "repository":REPO,"revision":None,"path":None,
             "blob_sha1":None,"issue_number":400,"comment_id":12349,
             "claimed_actor":"reallakshman19","schema":None},
            {"id":"C2_ORIGINAL_REFERENCES","kind":"PINNED_JSON",
             "repository":REPO,"revision":"b"*40,"path":"source.json",
             "blob_sha1":self.manifest_sha,"issue_number":None,
             "comment_id":None,"claimed_actor":None,
             "schema":"v36.source-custody/v1"}])
        self.responses={
            12345:ORIGINAL_DOC,
            12348:"# Revised engineering plan\nR2 first, R3 source-only handover "
                  "next, independent #274 and Physics checks before acceptance.",
            12349:"# R2 exact-head CI receipt\n119/119 native v3.6 structural "
                  "tests passed, including gaps and reordered event rejections.",
        }
        # Initial C1B pinned event and both live events refer to source 12345.
    def get(self,path):
        if path in ("/repos/"+REPO+"/issues/comments/12345",
                    "/repos/"+REPO+"/issues/comments/12348",
                    "/repos/"+REPO+"/issues/comments/12349"):
            cid=int(path.rsplit("/",1)[1])
            return {"id":cid,"issue_url":
                    "https://api.github.com/repos/"+REPO+"/issues/400",
                    "user":{"login":"reallakshman19"},
                    "body":self.responses[cid]}
        if "/contents/source.json?" in path:
            return {"type":"file","sha":self.manifest_sha,
                    "encoding":"base64",
                    "content":base64.b64encode(self.manifest_blob).decode()}
        return super().get(path)

class R3ExistingSuccessorTests(unittest.TestCase):
    def test_one_url_produces_twelve_source_cited_sections(self):
        report=rec.build(ISSUE_URL,R3Fake())
        self.assertEqual(len(report["sections"]),12)
        self.assertEqual([x["number"] for x in report["sections"]],
                         list(range(1,13)))
        self.assertTrue(all(x["source_refs"] for x in report["sections"]))
        md=rec.render(report)
        self.assertEqual(md.count("\nSource references:\n"),12)
        self.assertIn("119/119",md)
        self.assertIn("UNKNOWN",md)
        self.assertIn("EVENT_0002",md)
        self.assertIn("HOLD",md)
        self.assertNotIn("Owner accepted: True",md)
        self.assertFalse(report["owner_accepted"])
        self.assertFalse(report["may_merge_or_release"])

    def test_every_section_fails_if_source_reference_removed(self):
        report=rec.build(ISSUE_URL,R3Fake())
        for i in range(12):
            damaged=copy.deepcopy(report)
            damaged["sections"][i]["source_refs"]=[]
            with self.subTest(section=i+1),self.assertRaisesRegex(
                    rec.RecoveryError,"R3_SECTION_MISSING_SOURCE_REFERENCE"):
                rec.verify_sections(damaged)
            # A completely invented citation must also fail.
            damaged["sections"][i]["source_refs"]=["MADE_UP_SOURCE"]
            with self.subTest(fake_source=i+1),self.assertRaisesRegex(
                    rec.RecoveryError,"R3_SECTION_SOURCE_UNVERIFIED"):
                rec.verify_sections(damaged)

    def test_forged_or_unobserved_url_is_rejected(self):
        report=rec.build(ISSUE_URL,R3Fake())
        report["sources"]["OWNER_STATEMENT"]["url"]=""
        with self.assertRaisesRegex(rec.RecoveryError,"R3_SECTION_SOURCE_UNVERIFIED"):
            rec.verify_sections(report)

    def test_missing_real_owner_original_fails_closed(self):
        f=R3Fake()
        f.idx["references"]=[x for x in f.idx["references"]
                              if x["id"]!="OWNER_STATEMENT"]
        with self.assertRaises((rec.RecoveryError,spine.SpineError)):
            rec.build(ISSUE_URL,f)

    def test_reordered_r2_events_blocks_r3_before_report(self):
        f=R3Fake()
        a=next(i for i,x in enumerate(f.idx["references"])
               if x["id"]=="EVENT_0001")
        b=next(i for i,x in enumerate(f.idx["references"])
               if x["id"]=="EVENT_0002")
        f.idx["references"][a],f.idx["references"][b]=(
            f.idx["references"][b],f.idx["references"][a])
        with self.assertRaisesRegex(spine.SpineError,"EVENT_SEQUENCE_GAP_OR_REORDERED"):
            rec.build(ISSUE_URL,f)

    def test_missing_first_event_blocks_r3(self):
        f=R3Fake()
        f.idx["references"]=[x for x in f.idx["references"]
                              if x["id"]!="EVENT_0001"]
        with self.assertRaisesRegex(spine.SpineError,"EVENT_SEQUENCE_GAP_OR_REORDERED"):
            rec.build(ISSUE_URL,f)

    def test_ref_only_index_without_chronology_blocks_r3(self):
        f=R3Fake()
        f.idx["references"]=[x for x in f.idx["references"]
                              if not x["id"].startswith("EVENT_")]
        with self.assertRaisesRegex(rec.RecoveryError,"R3_REQUIRES_LIVE_VERIFIED"):
            rec.build(ISSUE_URL,f)

    def test_source_body_changed_between_audit_and_recovery_blocks(self):
        f=R3Fake()
        seen={"read":0}
        old=f.get
        def changing(path):
            x=old(path)
            if path.endswith("/issues/comments/12345"):
                seen["read"]+=1
                if seen["read"]>1: x={**x,"body":x["body"]+" edited after read"}
            return x
        f.get=changing
        with self.assertRaisesRegex(rec.RecoveryError,
                                     "R3_SOURCE_DRIFT_AFTER_VERIFIED_READ"):
            rec.build(ISSUE_URL,f)

    def test_original_governed_buddy_output_stays_unchanged(self):
        text=existing.buddy_prompt("1a",handover_id="R3-TEST",
             parent=PARENT,assessed_sha="a"*40)
        self.assertIn("EXECUTION=HOLD",text)
        self.assertIn("NEXT=G2",text)

    def test_existing_cli_cold_issue_url_only_invokes_new_view(self):
        with patch("issue_spine_read_v36.Reader",return_value=R3Fake()):
            out=io.StringIO()
            with contextlib.redirect_stdout(out):
                code=existing.main(["cold","--issue-url",ISSUE_URL])
        self.assertEqual(code,0)
        text=out.getvalue()
        self.assertIn("Native v3.6 twelve-section technical handover",text)
        self.assertEqual(text.count("\nSource references:\n"),12)

    def test_cli_refuses_mixing_issue_url_and_governed_plan(self):
        with self.assertRaises(SystemExit):
            existing.main(["cold","--issue-url",ISSUE_URL,
                           "--plan","not-an-approved-plan.yaml"])

    def test_no_old_relay_import_in_new_helper(self):
        import ast
        p=(ROOT/"scripts/successor_issue_recovery_v36.py").read_text(
          encoding="utf-8")
        names=set()
        for item in ast.walk(ast.parse(p)):
            if isinstance(item,ast.Import):
                names.update(x.name.split(".")[0] for x in item.names)
            elif isinstance(item,ast.ImportFrom):
                names.add((item.module or "").split(".")[0])
        self.assertTrue(names<={"__future__","hashlib","re","issue_spine_read_v36"})

if __name__=="__main__":
    unittest.main()
