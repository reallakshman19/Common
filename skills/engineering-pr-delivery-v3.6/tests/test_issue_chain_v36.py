"""V3.6 issue chain C1 structural and negative tests; never owner/source attestation."""
from __future__ import annotations
import copy
import ast
import subprocess
import tempfile
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"scripts"/"issue_chain_v36.py"
SPEC=importlib.util.spec_from_file_location("issue_chain_v36",TARGET)
chain=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=chain
SPEC.loader.exec_module(chain)
EXAMPLE=ROOT/"tests"/"fixtures"/"issue-chain-274-reported.json"

class ContinuityChainTest(unittest.TestCase):
    def subject(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def edge(self,obj,category):
        return next(x for x in obj["chain"] if x["category"]==category)

    def failure(self,obj,fragment):
        with self.assertRaisesRegex(chain.ChainError,fragment):
            chain.validate(obj)

    def test_real_owner_issue_example_accounts_not_certifies(self):
        output=chain.validate(self.subject())
        self.assertEqual(output["required_categories"],11)
        self.assertEqual(output["accounted_categories"],11)
        self.assertEqual(output["reported_categories"],7)
        self.assertEqual(output["unknown_categories"],4)
        self.assertEqual(output["verified_source_categories"],0)
        self.assertEqual(output["authenticated_owner_decisions"],0)
        self.assertEqual(output["claimed_adoptions"],0)
        self.assertEqual(output["accounting_coverage_percent"],100)
        self.assertEqual(output["verified_coverage_percent"],0)
        self.assertFalse(output["permission_to_write"])
        self.assertFalse(output["may_change_titles_or_labels"])
        self.assertFalse(output["may_merge_or_release"])
        self.assertIn("NOT_SOURCE_VERIFIED",output["status"])

    def test_original_inputs_goldens_benchmarks_explicit_unknown(self):
        data=self.subject()
        for category in ("ORIGINAL_INPUT","COMPLETE_GOLDEN","MEASURED_BENCHMARK"):
            with self.subTest(category=category):
                e=self.edge(data,category)
                self.assertEqual(e["state"],"UNKNOWN")
                self.assertEqual(e["record_ids"],[])
                self.assertGreater(len(e["reason"]),12)
        self.assertIn("2961",data["records"][2]["summary"])
        self.assertIn("zero Match-1/Final",data["records"][5]["summary"])

    def test_no_proposed_idea_promoted_to_approved(self):
        data=self.subject()
        e=data["records"][4]
        self.assertEqual(e["disposition"],"PROPOSED")
        self.assertEqual(chain.validate(data)["authenticated_owner_decisions"],0)

    def test_unpublished_chat_cannot_assert_owner_authentication(self):
        data=self.subject()
        data["owner_intent"]["actor_authentication"]="PROVEN_OWNER"
        self.failure(data,"OWNER_IDENTITY_NOT_AUTHENTICATED")

    def test_non_owner_quote_cannot_become_direct_owner_event(self):
        data=self.subject()
        data["owner_intent"]["source_class"]="AGENT_ANALYSIS_REPORTED"
        self.failure(data,"OWNER_INTENT_MUST_BE_REPORTED")

    def test_missing_root_link_blocks(self):
        data=self.subject()
        self.edge(data,"ROOT_OWNER_INTENT").update(state="UNKNOWN",record_ids=[],
                                                    reason="The original direct Owner message is unavailable")
        self.failure(data,"ROOT_OWNER_INTENT_MISSING")

    def test_missing_category_blocks(self):
        data=self.subject()
        data["chain"].pop(2)
        self.failure(data,"CHAIN_REQUIRED_CATEGORIES_MISSING")

    def test_wrong_category_order_blocks(self):
        data=self.subject()
        data["chain"][1],data["chain"][2]=data["chain"][2],data["chain"][1]
        self.failure(data,"CHAIN_ORDER_OR_CATEGORY_DRIFT")

    def test_unknown_with_forged_link_blocks(self):
        data=self.subject()
        self.edge(data,"COMPLETE_GOLDEN")["record_ids"]=["EV-003"]
        self.failure(data,"UNKNOWN_CANNOT_CLAIM_EVIDENCE")

    def test_reported_without_evidence_blocks(self):
        data=self.subject()
        e=self.edge(data,"COMPLETE_GOLDEN")
        e.update(state="PRESENT_REPORTED",record_ids=[],reason=None)
        self.failure(data,"CHAIN_UNBOUND_ORPHAN")

    def test_orphan_event_blocks(self):
        data=self.subject()
        self.edge(data,"AGENT_CONTRIBUTIONS")["record_ids"]=[]
        self.failure(data,"CHAIN_UNBOUND_ORPHAN")

    def test_duplicate_event_blocks(self):
        data=self.subject()
        data["records"].append(copy.deepcopy(data["records"][0]))
        self.failure(data,"EVENT_DUPLICATE_OR_INVALID_ID")

    def test_forward_history_reference_blocks(self):
        data=self.subject()
        data["records"][0]["related_ids"]=["EV-005"]
        self.failure(data,"ORPHAN_FORWARD_OR_CYCLIC")

    def test_unrelated_foreign_repo_source_blocks(self):
        data=self.subject()
        data["records"][2]["repository"]="attacker/untrusted"
        self.failure(data,"EVENT_SOURCE_REPO_OUT_OF_SCOPE")

    def test_url_lookalike_is_rejected(self):
        data=self.subject()
        data["records"][0]["source_ref"]="https://github.com.attacker.com/reallakshman19/3D_Converters/issues/274"
        self.failure(data,"URL_UNSAFE_OR_UNSUPPORTED")

    def test_url_query_and_fragment_injection_rejected(self):
        data=self.subject()
        data["records"][0]["source_ref"]="https://github.com/reallakshman19/3D_Converters/issues/274?auth=secret"
        self.failure(data,"URL_UNSAFE_OR_UNSUPPORTED")

    def test_cross_repo_source_url_mismatch_blocks(self):
        data=self.subject()
        data["observed_main"]["reallakshman19/Common"]="0a7c4d45d3fa0787d3e80858a27015b09a85eac2"
        data["records"][0]["source_ref"]="https://github.com/reallakshman19/Common/issues/400"
        self.failure(data,"EVENT_SOURCE_REPO_URL_MISMATCH")

    def test_fake_adoption_without_protected_receipt_blocks(self):
        data=self.subject()
        data["records"][4]["disposition"]="ADOPTED_REPORTED"
        self.failure(data,"PROTECTED_DECISION_REFERENCE_REQUIRED")

    def test_claimed_adoption_still_not_verified_owner_approval(self):
        data=self.subject()
        data["records"][4]["disposition"]="ADOPTED_REPORTED"
        data["records"][4]["decision_ref"]="https://github.com/reallakshman19/3D_Converters/issues/274"
        out=chain.validate(data)
        self.assertEqual(out["claimed_adoptions"],1)
        self.assertEqual(out["authenticated_owner_decisions"],0)
        self.assertFalse(out["may_merge_or_release"])

    def test_parked_idea_requires_next_revisit_trigger(self):
        data=self.subject()
        data["records"][4]["disposition"]="PARKED"
        self.failure(data,"PARKED_REVISIT_TRIGGER")
        data["records"][4]["revisit_trigger"]="Revisit once real JSON throughput and canonical Final audit are reproducible."
        self.assertEqual(chain.validate(data)["reported_categories"],7)

    def test_fake_historical_attestation_digest_blocks(self):
        data=self.subject()
        data["records"][3]["source_sha256"]="123"
        self.failure(data,"EVENT_SOURCE_DIGEST_INVALID")

    def test_private_chat_not_exposed_as_public_receipt(self):
        data=self.subject()
        data["records"][0]["visibility"]="PRIVATE"
        self.failure(data,"PRIVATE_RECORD_MUST_NOT_BE_PUBLISHED")

    def test_changed_source_cut_without_exact_sha_blocks(self):
        data=self.subject()
        data["observed_main"]["reallakshman19/3D_Converters"]="9944a5b"
        self.failure(data,"MAIN_SOURCE_CUT_INVALID")

    def test_claimed_report_reference_has_no_runtime_source_write(self):
        self.assertFalse(hasattr(chain,"apply"))
        self.assertFalse(hasattr(chain,"GithubClient"))
        self.assertFalse(hasattr(chain,"update_issue"))
        self.assertFalse(chain.validate(self.subject())["permission_to_write"])


    # V36-C1b reviewer regressions (RED before implementation).
    def test_category_record_kind_binding_fails_before_orphan_accounting(self):
        examples = (
            ("ROOT_OWNER_INTENT", "EV-004"),       # AGENT_EVIDENCE
            ("AGENT_CONTRIBUTIONS", "EV-001"),     # OWNER_INPUT
            ("DECISION_AND_PARKED_IDEAS", "EV-006"),  # KNOWN_FAILURE
            ("TECHNICAL_HANDOVER", "EV-005"),      # IDEA
        )
        for category, wrong_id in examples:
            with self.subTest(category=category):
                data=self.subject()
                self.edge(data,category)["record_ids"].append(wrong_id)
                self.failure(data,"CATEGORY_KIND_MISMATCH")

    def test_sha_is_shape_only_not_a_provider_attestation(self):
        data=self.subject()
        data["records"][0]["source_sha256"]="f"*64
        outcome=chain.validate(data)
        self.assertEqual(outcome["verified_source_categories"],0)
        self.assertEqual(outcome["authenticated_owner_decisions"],0)
        data["records"][0]["source_sha256"]="F"*64
        self.failure(data,"EVENT_SOURCE_DIGEST_INVALID")

    def test_not_applicable_explicit_reason_is_accounted_but_not_proven(self):
        data=self.subject()
        edge=self.edge(data,"OWNER_AMENDMENTS")
        edge["state"]="NOT_APPLICABLE"
        result=chain.validate(data)
        self.assertEqual(result["not_applicable_categories"],1)
        self.assertEqual(result["unknown_categories"],3)
        self.assertEqual(result["verified_source_categories"],0)
        edge["reason"]=None
        self.failure(data,"UNKNOWN_OR_NOT_APPLICABLE_REASON")

    def test_rejected_reported_decision_requires_ref_and_never_approves(self):
        data=self.subject()
        proposal=data["records"][4]
        proposal["disposition"]="REJECTED_REPORTED"
        self.failure(data,"PROTECTED_DECISION_REFERENCE_REQUIRED")
        proposal["decision_ref"]="https://github.com/reallakshman19/3D_Converters/issues/274"
        report=chain.validate(data)
        self.assertEqual(report["claimed_adoptions"],0)
        self.assertEqual(report["authenticated_owner_decisions"],0)
        self.assertFalse(report["may_merge_or_release"])

    def test_nondecision_cannot_adopt_or_reject(self):
        for kind_disposition in ("ADOPTED_REPORTED","REJECTED_REPORTED","PROPOSED","PARKED"):
            with self.subTest(disposition=kind_disposition):
                data=self.subject()
                data["records"][3]["disposition"]=kind_disposition
                self.failure(data,"NONDECISION_CANNOT_BE_ADOPTED")

    def test_ast_only_pure_stdlib_imports_no_network_or_older_skill(self):
        tree=ast.parse(TARGET.read_text(encoding="utf-8"))
        allowed={"__future__","argparse","hashlib","json","re","pathlib","urllib.parse"}
        found=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                found.update(alias.name for alias in node.names)
            if isinstance(node,ast.ImportFrom):
                found.add(node.module)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                self.assertNotIn(node.func.id,{"__import__","eval","exec"})
        self.assertEqual(found,allowed)
        self.assertNotIn("v3.5",str(found))
        self.assertNotIn("v3.2",str(found))

    def test_accounting_coverage_is_derived_not_literal_100(self):
        source=TARGET.read_text(encoding="utf-8")
        self.assertNotIn('"accounting_coverage_percent":100',source)
        report=chain.validate(self.subject())
        self.assertEqual(report["accounting_coverage_percent"],100)
        self.assertEqual(report["required_categories"],11)

    def test_cli_invalid_json_and_unreadable_input_exit_2(self):
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/"broken.json"
            bad.write_text("{ definitely not json",encoding="utf-8")
            for input_path in (bad,Path(td)/"missing.json"):
                with self.subTest(path=str(input_path)):
                    run=subprocess.run(
                        [sys.executable,str(TARGET),"--input",str(input_path)],
                        text=True,capture_output=True,check=False,timeout=15)
                    self.assertEqual(run.returncode,2,run.stderr)
                    self.assertEqual(json.loads(run.stdout)["status"],"CHAINAGE_BLOCKED")

    def test_cli_output_write_error_exit_2_no_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            inp=Path(td)/"input.json"
            inp.write_text(json.dumps(self.subject()),encoding="utf-8")
            output_is_directory=Path(td)/"existing-directory"
            output_is_directory.mkdir()
            run=subprocess.run(
                [sys.executable,str(TARGET),"--input",str(inp),
                 "--output",str(output_is_directory)],
                capture_output=True,text=True,check=False,timeout=15)
            self.assertEqual(run.returncode,2,run.stderr)
            self.assertEqual(json.loads(run.stdout)["status"],"CHAINAGE_BLOCKED")
            self.assertNotIn("Traceback",run.stderr)


if __name__=="__main__":
    unittest.main()
