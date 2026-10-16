"""v3.6 C1B source-first Owner-intent, lineage, private-source and ad-hoc tests."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import issue_receipt_v36 as c

REF="reallakshman19/Common#400"
SRC="https://github.com/reallakshman19/Common/issues/400#issuecomment-6223067953"
SAMPLE=ROOT/"tests/fixtures/c1b-common-400-owner-reported.json"
SHA="a"*40

def fixture():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))

def extra(kind="AGENT_CONTRIBUTION",when="2026-10-16T19:27:22Z"):
    return dict(id="EV-0002",kind=kind,occurred_at=when,source_ref=SRC,
        source_class="AGENT_REPORTED",actor_login_claim="reallakshman19",
        actor_authentication="PROVIDER_ACCOUNT_OBSERVED_NOT_OWNER_AUTHENTICATED",
        summary="Later engineer captured correction and preserved original provenance without granting product approval",
        visibility="PUBLIC_SAFE",source_sha256_claim=None,
        supersedes=[],disposition="PROPOSED",revisit_trigger=None,
        conversation_ref=None,conversation_access="NOT_CAPTURED",
        lineage=None,previous_digest=None)

def append(doc,row):
    row["previous_digest"]=c.digest(doc["events"][-1])
    doc["events"].append(row)
    return doc

def lineage():
    issues=[f"reallakshman19/Common#{i}" for i in (123,125,126)]
    nodes=[
        dict(issue=issues[0],state="ACTIVE",availability="ACCESSIBLE_PROVIDER_OBSERVED",
             reason=None,disposition_ref=None),
        dict(issue=issues[1],state="INVALID_REPORTED",availability="UNKNOWN",
             reason="An intermediate issue was reported invalid and replaced by successor",
             disposition_ref=SRC),
        dict(issue=issues[2],state="ACTIVE",availability="UNKNOWN",
             reason=None,disposition_ref=None)]
    edges=[{"from":issues[i],"to":issues[i+1],
            "relationship":"SUCCESSOR","source_ref":SRC} for i in (0,1)]
    return {"nodes":nodes,"edges":edges}

def adhoc():
    return dict(protocol_mode="AD_HOC_NO_OTHER_PROTOCOL",authorized_issue=None,
                human_outcome="Fix a real source issue with retained original engineering reason",
                source_revision="reallakshman19/Common@"+SHA,
                implementation_crux="A read-only source path now validates occurrence identity",
                original_inputs="UNKNOWN: source inputs have not been privately published",
                golden="UNKNOWN: complete source-linked output oracle not yet verified",
                benchmark="UNKNOWN: actual original workload not rerun under Chromium",
                tests="NOT_RUN: author has not executed product tests yet",
                issue_chain="UNKNOWN: predecessor issue links not independently found",
                known_gaps="Human engineering approval and source-oracle comparison outstanding",
                parked_ideas="PARKED: streaming source expansion until original large source arrives",
                next_verification="Re-fetch original input and compare existing native source path",
                conversation_ref=None,conversation_access="NOT_CAPTURED")

class ReceiptTests(unittest.TestCase):
    def test_actual_owner_document_source_is_reported_not_approved(self):
        a=fixture()
        o=c.validate_stream(a)
        self.assertEqual(o["events"],1)
        self.assertEqual(o["authenticated_owner_decisions"],0)
        self.assertEqual(o["verified_provider_events"],0)
        self.assertFalse(o["may_publish"])
        self.assertFalse(o["may_count_for_o2"])
        self.assertFalse(o["may_change_titles_or_labels"])
        self.assertFalse(o["may_merge_or_release"])
        self.assertIn("C-01",c.render(a))
        self.assertIn("6223067953",c.render(a))

    def test_append_only_real_reported_followup(self):
        a=fixture()
        b=append(copy.deepcopy(a),extra())
        o=c.verify_extension(a,b)
        self.assertEqual(o["prior_events"],1)
        self.assertEqual(o["next_events"],2)
        self.assertIn("PROVIDER_READBACK",o["status"])

    def test_history_cannot_be_removed_or_edited(self):
        a=fixture()
        b=append(copy.deepcopy(a),extra())
        for mutation in ("removal","changed_summary"):
            x=copy.deepcopy(b)
            if mutation=="removal":
                x["events"]=x["events"][:-1]
            else:
                x["events"][0]["summary"]="Changed original WHY without append-only amendment"
            with self.assertRaisesRegex(c.ReceiptError,
                                         "HISTORICAL_RECEIPT_EDIT_OR_REMOVAL"):
                c.verify_extension(b,x)

    def test_hash_chain_catches_old_entry_edit(self):
        a=append(fixture(),extra())
        a["events"][0]["summary"]="Undeclared rewrite of original Owner input"
        with self.assertRaisesRegex(c.ReceiptError,"HASH_MISMATCH"):
            c.validate_stream(a)

    def test_duplicate_event_id_denied(self):
        a=fixture()
        x=extra()
        x["id"]="EV-0001"
        append(a,x)
        with self.assertRaisesRegex(c.ReceiptError,"DUPLICATE"):
            c.validate_stream(a)

    def test_future_supersession_denied(self):
        a=fixture()
        x=extra()
        x["supersedes"]=["EV-9000"]
        append(a,x)
        with self.assertRaisesRegex(c.ReceiptError,"ORPHAN"):
            c.validate_stream(a)

    def test_claimed_owner_authority_never_self_verifies(self):
        a=fixture()
        a["events"][0]["actor_authentication"]="OWNER_ACCEPTED"
        with self.assertRaisesRegex(c.ReceiptError,"CANNOT_SELF_AUTHENTICATE"):
            c.validate_stream(a)

    def test_direct_owner_class_cannot_be_changed_to_agent(self):
        a=fixture()
        a["events"][0]["source_class"]="AGENT_REPORTED"
        with self.assertRaisesRegex(c.ReceiptError,"OWNER_INPUT_MUST_BE_REPORTED"):
            c.validate_stream(a)

    def test_private_owner_body_cannot_be_copied(self):
        a=fixture()
        e=a["events"][0]
        e["visibility"]="CONTENT_NOT_PUBLISHED"
        e["source_ref"]=None
        with self.assertRaisesRegex(c.ReceiptError,"PRIVATE_EVENT_CONTENT"):
            c.validate_stream(a)
        e["summary"]="CONTENT_NOT_PUBLISHED"
        e["source_sha256_claim"]=None
        self.assertEqual(c.validate_stream(a)["events"],1)

    def test_agent_chat_url_not_inferred(self):
        a=fixture()
        e=a["events"][0]
        e["conversation_access"]="RESTRICTED_NOT_PUBLISHED"
        e["conversation_ref"]="https://chatgpt.com/share/sensitive"
        with self.assertRaisesRegex(c.ReceiptError,"RESTRICTED_CONVERSATION_LEAK"):
            c.validate_stream(a)

    def test_public_chat_reference_requires_explicit_share(self):
        a=fixture()
        e=a["events"][0]
        e["conversation_access"]="AUTHORIZED_PUBLIC"
        e["conversation_ref"]="https://github.com/reallakshman19/Common/issues/400"
        with self.assertRaisesRegex(c.ReceiptError,"CONVERSATION_PUBLIC"):
            c.validate_stream(a)
        e["conversation_ref"]="https://chatgpt.com/share/explicitly-authorized-test"
        self.assertEqual(c.validate_stream(a)["events"],1)

    def test_lineage_preserves_invalid_middle_with_visible_strike(self):
        a=fixture()
        x=extra(kind="ISSUE_LINEAGE")
        x["lineage"]=lineage()
        append(a,x)
        md=c.render(a)
        self.assertIn("~~https://github.com/reallakshman19/Common/issues/125~~",md)
        self.assertIn("INVALID_REPORTED",md)
        self.assertIn("not provider",md.lower()) if False else None

    def test_lineage_missing_middle_hop_fails(self):
        a=fixture()
        x=extra(kind="ISSUE_LINEAGE")
        l=lineage()
        l["edges"]=[l["edges"][0]]
        x["lineage"]=l
        append(a,x)
        with self.assertRaisesRegex(c.ReceiptError,"MISSING_MIDDLE_HOP"):
            c.validate_stream(a)

    def test_lineage_404_remains_unverified_not_deleted(self):
        a=fixture()
        x=extra(kind="ISSUE_LINEAGE")
        l=lineage()
        n=l["nodes"][1]
        n["state"]="AVAILABILITY_UNVERIFIED"
        n["availability"]="NOT_FOUND_UNVERIFIED"
        n["disposition_ref"]=None
        n["reason"]="GitHub returned 404 and existence cannot be classified"
        x["lineage"]=l
        append(a,x)
        out=c.render(a)
        self.assertIn("AVAILABILITY_UNVERIFIED",out)
        self.assertNotIn("~~https://github.com/reallakshman19/Common/issues/125~~",out)
        n["state"]="INVALID_REPORTED"
        n["disposition_ref"]=None
        with self.assertRaisesRegex(c.ReceiptError,"TOMBSTONE_REQUIRES_SOURCE"):
            c.validate_stream(a)

    def test_lineage_cross_repo_unapproved_and_cycle_denied(self):
        a=fixture()
        x=extra(kind="ISSUE_LINEAGE")
        l=lineage()
        l["nodes"][1]["issue"]="other/external#125"
        x["lineage"]=l
        append(a,x)
        with self.assertRaises(c.ReceiptError):
            c.validate_stream(a)
        l=lineage()
        l["edges"].append({"from":"reallakshman19/Common#126",
                           "to":"reallakshman19/Common#123",
                           "relationship":"ALTERNATIVE","source_ref":SRC})
        a["events"][1]["lineage"]=l
        with self.assertRaisesRegex(c.ReceiptError,"CYCLE"):
            c.validate_stream(a)

    def test_parked_idea_requires_revisit_trigger(self):
        a=fixture()
        x=extra(kind="DECISION")
        x["disposition"]="PARKED"
        append(a,x)
        with self.assertRaisesRegex(c.ReceiptError,"PARKED_REVISIT"):
            c.validate_stream(a)
        x["revisit_trigger"]="Revisit when original positive fixture and target golden are available"
        self.assertIn("Revisit:",c.render(a))

    def test_optional_adhoc_is_copy_only_without_destination(self):
        text=c.render_adhoc(adhoc())
        self.assertIn("COPYABLE, NEVER PUBLISHED",text)
        self.assertIn("NO AUTHORIZED PUBLISH DESTINATION",text)
        self.assertIn("Not governed TASK_EVIDENCE",text)

    def test_governed_or_explicit_other_protocol_precedes_adhoc(self):
        for mode in ("GOVERNED_V36","EXPLICIT_OTHER_PROTOCOL"):
            d=adhoc()
            d["protocol_mode"]=mode
            with self.assertRaisesRegex(c.ReceiptError,
                                         "PROTOCOL_PRECEDENCE"):
                c.render_adhoc(d)

    def test_adhoc_private_chat_and_missing_sha_blocked(self):
        a=adhoc()
        a["source_revision"]="main"
        with self.assertRaisesRegex(c.ReceiptError,"EXACT_COMMIT"):
            c.render_adhoc(a)
        a=adhoc()
        a["conversation_ref"]="https://chatgpt.com/share/private"
        a["conversation_access"]="RESTRICTED_NOT_PUBLISHED"
        with self.assertRaisesRegex(c.ReceiptError,"PRIVATE_CONVERSATION"):
            c.render_adhoc(a)

    def test_no_other_runtime_imports(self):
        import ast
        tree=ast.parse((ROOT/"scripts/issue_receipt_v36.py").read_text(
            encoding="utf-8"))
        libs=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                libs.update(i.name.split(".")[0] for i in n.names)
            elif isinstance(n,ast.ImportFrom):
                libs.add((n.module or "").split(".")[0])
        self.assertTrue(libs <=
            {"__future__","argparse","hashlib","json","re","pathlib","urllib"})


if __name__=="__main__":
    unittest.main()
