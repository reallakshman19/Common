"""C3 exact native cold packet extension; no legacy or C1/C2 runtime imports."""
import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import successor_context_v36 as cx
import successor_v36 as sv
from test_successor_v36 import LABEL, PLAN, Provider, REPO

HEAD="6e7f4b98e286d19598fc6cb27f007c12811fbc4d"
OTHER="a"*40
DIGEST="b"*64

def chain():
    root={"id":"EV-001","kind":"OWNER_INPUT",
          "summary":"Owner requires exact original input provenance and durable engineering reason",
          "source_ref":"https://github.com/"+REPO+"/issues/1",
          "repository":REPO,"visibility":"PUBLIC","disposition":"N_A"}
    bad={"id":"EV-002","kind":"KNOWN_FAILURE",
         "summary":"Reported completed FactRecords do not prove original source masses and Final decisions",
         "source_ref":"https://github.com/"+REPO+"/issues/1",
         "repository":REPO,"visibility":"PUBLIC","disposition":"N_A"}
    edges=[]
    for cat in cx.CATEGORIES:
        ids=(["EV-001"] if cat=="ROOT_OWNER_INTENT" else
             ["EV-002"] if cat=="KNOWN_FAILURES" else [])
        edges.append({"category":cat,
                      "state":"PRESENT_REPORTED" if ids else "UNKNOWN",
                      "record_ids":ids,
                      "reason":None if ids else "Original current source and acceptance evidence not published"})
    return {"schema":"v36.issue-continuity-chain/v1",
            "parent":REPO+"#1","observed_main":{REPO:OTHER},
            "owner_intent":{"source_class":"OWNER_DIRECT_REPORTED",
                            "actor_authentication":"NOT_VERIFIED_BY_THIS_TOOL",
                            "source_ref":"https://github.com/"+REPO+"/issues/1",
                            "excerpt":"Original Owner outcome is a source-correct engineering lifecycle, not synthetic completion"},
            "records":[root,bad],"chain":edges}

def manifest():
    return {"schema":"v36.source-custody/v1","repository":REPO,"revision":HEAD,
            "artifacts":[{"id":"REAL_POINTER","role":"PARTIAL_GOLDEN",
                          "path":"Benchmarks/example.xml",
                          "expected_blob_sha1":"c"*40,
                          "expected_sha256":DIGEST,
                          "expected_size_bytes":144029,
                          "oracle_complete":False}],
            "issue_records":[]}

def packet():
    return sv.build_packet(LABEL,PLAN,Provider(),[4])


class ContextTests(unittest.TestCase):
    def test_no_existing_successor_contract_change(self):
        p=packet()
        original=copy.deepcopy(p)
        report=cx.attach(p,chain(),manifest())
        self.assertEqual(original,p)
        self.assertEqual(report["source_verification"],
                         "NOT_ESTABLISHED_BY_JSON_INPUT")
        self.assertFalse(report["owner_acceptance"])
        self.assertFalse(report["may_count_for_o2"])
        self.assertFalse(report["may_publish"])
        self.assertFalse(report["may_merge_or_release"])
        self.assertEqual(report["source_drift_warning"],True)
        self.assertEqual(len(report["sections"]),11)

    def test_c1_missing_goldens_stays_unknown(self):
        ctx=cx.attach(packet(),chain(),manifest())
        md=cx.render(ctx)
        self.assertIn("COMPLETE_GOLDEN — UNKNOWN",md)
        self.assertIn("PARTIAL_GOLDEN",md)
        self.assertIn("Reported",md)
        self.assertIn("Re-fetch",md)
        self.assertNotIn("OWNER_ACCEPTED",md)

    def test_wrong_issue_cross_repo_context_blocks(self):
        d=chain()
        d["parent"]=REPO+"#3"
        with self.assertRaisesRegex(cx.ContextError,"C1_PARENT"):
            cx.attach(packet(),d,manifest())

    def test_untrusted_source_host_denied(self):
        d=chain()
        d["owner_intent"]["source_ref"]="https://github.com.evil.example/"+REPO+"/issues/1"
        with self.assertRaisesRegex(cx.ContextError,"UNTRUSTED_SOURCE_URL"):
            cx.attach(packet(),d,manifest())

    def test_private_contribution_denied(self):
        d=chain()
        d["records"][1]["visibility"]="PRIVATE"
        with self.assertRaisesRegex(cx.ContextError,"C1_EVENT_INVALID"):
            cx.attach(packet(),d,manifest())

    def test_reported_owner_cannot_upgrade_identity(self):
        d=chain()
        d["owner_intent"]["actor_authentication"]="VERIFIED_OWNER"
        with self.assertRaisesRegex(cx.ContextError,"OWNER_INPUT_MUST_REMAIN_REPORTED"):
            cx.attach(packet(),d,manifest())

    def test_category_missing_denied(self):
        d=chain()
        d["chain"].pop()
        with self.assertRaisesRegex(cx.ContextError,"C1_CATEGORY_ORDER"):
            cx.attach(packet(),d,manifest())

    def test_missing_gap_reason_denied(self):
        d=chain()
        d["chain"][1]["reason"]=""
        with self.assertRaisesRegex(cx.ContextError,"C1_MISSING_GAP_REASON"):
            cx.attach(packet(),d,manifest())

    def test_manifest_foreign_repo_denied(self):
        d=manifest()
        d["repository"]="attacker/external"
        with self.assertRaisesRegex(cx.ContextError,"C2_SOURCE_SCOPE"):
            cx.attach(packet(),chain(),d)

    def test_partial_golden_cannot_be_complete(self):
        d=manifest()
        d["artifacts"][0]["oracle_complete"]=True
        with self.assertRaisesRegex(cx.ContextError,"C2_PARTIAL_GOLDEN"):
            cx.attach(packet(),chain(),d)

    def test_untrusted_file_path_denied(self):
        d=manifest()
        d["artifacts"][0]["path"]="../../secret"
        with self.assertRaisesRegex(cx.ContextError,"C2_ARTIFACT_PATH"):
            cx.attach(packet(),chain(),d)

    def test_markdown_escapes_injected_summary(self):
        d=chain()
        d["records"][1]["summary"]="Reported <script>not executable</script> | escaped inline summary"
        md=cx.render(cx.attach(packet(),d,manifest()))
        self.assertNotIn("<script>",md)
        self.assertIn("&lt;script&gt;",md)

    def test_native_cli_requires_freeze_and_both_sources(self):
        paths=[str(ROOT/"tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml"),
               str(ROOT/"plans/V36-1-PLAN-01.yaml")]
        with tempfile.TemporaryDirectory() as temp:
            a=Path(temp)/"chain.json"
            b=Path(temp)/"manifest.json"
            a.write_text(json.dumps(chain()),encoding="utf-8")
            b.write_text(json.dumps(manifest()),encoding="utf-8")
            cmd=["cold","--label",paths[0],"--plan",paths[1],
                 "--lab",REPO,"--pr","4",
                 "--continuity-chain",str(a),"--custody-manifest",str(b)]
            class NativeProvider(Provider):
                def request(self,method,path,body=None):
                    if method=="GET" and path=="/pulls/4":
                        return self.pr
                    return super().request(method,path,body)
            with patch.object(sv,"GithubClient",lambda _:NativeProvider()):
                with self.assertRaises(SystemExit) as e:
                    with redirect_stdout(io.StringIO()):
                        sv.main(cmd)
                self.assertEqual(e.exception.code,2)
                with redirect_stdout(io.StringIO()) as output:
                    rc=sv.main(cmd+["--stage2-freeze-verified"])
                self.assertEqual(rc,0)
                rendered=output.getvalue()
                self.assertIn("V3.6 GitHub-only cold successor packet",rendered)
                self.assertIn("Issue-first engineering continuity",rendered)
                self.assertIn("No release or merge authority",rendered)

    def test_no_new_buddy_round(self):
        v=sv.buddy_prompt("1a",handover_id="C3-TEST",
                          parent=REPO+"#1",assessed_sha=HEAD)
        self.assertIn("EXECUTION=HOLD",v)
        self.assertNotIn("Issue-first engineering continuity",v)

    def test_no_legacy_relay_imports(self):
        import ast
        for filename in ("successor_context_v36.py","successor_v36.py"):
            src=(ROOT/"scripts"/filename).read_text(encoding="utf-8")
            mods=set()
            for n in ast.walk(ast.parse(src)):
                if isinstance(n,ast.Import):
                    mods.update(a.name.split(".")[0] for a in n.names)
                elif isinstance(n,ast.ImportFrom):
                    mods.add((n.module or "").split(".")[0])
            self.assertFalse(mods.intersection(
                {"engineering_pr_delivery_v35","engineering_pr_delivery_v32",
                 "lifecycle_v35","lifecycle_v32","delp_projection_v35"}))
            self.assertNotIn("v3.5/scripts",src)
            self.assertNotIn("v3.2/scripts",src)


if __name__=="__main__":
    unittest.main()
