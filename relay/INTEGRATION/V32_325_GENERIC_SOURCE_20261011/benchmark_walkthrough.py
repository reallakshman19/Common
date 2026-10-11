"""Executable *synthetic* acceptance benchmark for the five production HOLDs.

Reuses the existing source-owned fixture/providers and actual T01/T02/T03 native
calls; does NOT create a new DELP, publisher, authorizer, evidence issuer or B.
Exit code 0 means EXPECTED synthetic acceptance/refusal behavior was observed,
NOT that any Owner acceptance or physical production gate passed.

From the Common checkout:
    python relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/benchmark_walkthrough.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
NATIVE = ROOT / "skills/engineering-pr-delivery-v3.2/scripts"
if str(NATIVE) not in sys.path:
    sys.path.insert(0, str(NATIVE))

from generic_source_preflight import SourceHold
from generic_current_source import reconcile_current_source
from generic_publication_plan import reconcile_publication_readback
from test_current_source_reconciliation import (
    CurrentSourceTests, FakeGraphSource, GRAPH_PATH, REVISION,
)
from test_generic_source_preflight import (
    GenericSourceTest, HEAD, LEAF, PR_NUM, REPO,
)
from test_publication_plan import PurePublisherPlanTests, PR_REF, ROOT_REF
from test_rest_readonly_provider import ObservedEnvelopeFixture, ROOT_NUM, LEAF_NUM


def _case(rows: list[dict[str, Any]], name: str, expected: str,
          actual: str, *, boundary: str) -> None:
    rows.append({
        "case": name, "expected": expected, "observed": actual,
        "result": "PASS" if expected == actual else "FAIL",
        "boundary": boundary,
    })


def _expect_hold(rows: list[dict[str, Any]], name: str, expected: str,
                 call: Callable[[], Any], *, boundary: str) -> None:
    try:
        call()
    except SourceHold as exc:
        actual = str(exc)
    except Exception as exc:
        actual = "UNEXPECTED_EXCEPTION:" + type(exc).__name__
    else:
        actual = "UNEXPECTEDLY_ACCEPTED"
    _case(rows, name, expected, actual, boundary=boundary)


def _t02() -> CurrentSourceTests:
    fixture = CurrentSourceTests(methodName="test_12_double_read_current_graph_reuses_native_ledger_and_core")
    fixture.setUp()
    return fixture


def _t01() -> GenericSourceTest:
    fixture = GenericSourceTest(methodName="test_02_readonly_generic_repository_returns_native_delp_zero_progress")
    fixture.setUp()
    return fixture


def _t03() -> PurePublisherPlanTests:
    fixture = PurePublisherPlanTests(methodName="test_22_three_disjoint_surface_ownership_and_human_preservation")
    fixture.setUp()
    return fixture


def run_benchmark() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    # G1 Owner source: a native graph can be *shape-consistent* even when its
    # issuance is not authenticated. No fabricated signing/release input.
    source = _t02().call()
    result = ("READ_ONLY_RECONCILED_UNATTESTED"
              if source["status"] == "READ_ONLY_RECONCILED_UNATTESTED"
              and source["source_authenticated"] is False
              and source["production_authorized"] is False
              and source["writes"] == 0 else "WRONG_AUTHORITY")
    _case(rows, "B01_synthetic_graph_readonly", "READ_ONLY_RECONCILED_UNATTESTED",
          result, boundary="G1_OWNER_SOURCE_NOT_AUTHENTICATED")

    changed = _t02()
    changed.graph_source.current_blob = b'{"schema":"different-release"}'
    _expect_hold(rows, "B02_original_graph_drift", "SOURCE_GRAPH_NOT_CURRENT_RELEASED",
                 changed.call, boundary="G1_PINNED_AND_CURRENT_GRAPH_PARITY")

    # G2 evidence must not accept an arbitrary claimant.
    forged = _t02()
    forged.provider.comments[733] = [{
        "id": 51, "user": {"login": "stranger"},
        "author_association": "NONE",
        "body": (
            "CHECKPOINT_FACTS_V1:\n"
            "  responsibility: {issue: Pipeline#733, id: R-PROJECTION}\n"
            "  material: {pr: Pipeline#740, candidate_sha: " + HEAD + "}\n"
            "  units:\n"
            "    - {id: VIEW-PR, state: COMPLETE, result: VERIFIED, evidence_refs: [Pipeline#733#issuecomment-51]}\n"
        ),
    }]
    observation = forged.call()
    outcome = ("FORGED_FACT_REJECTED_E_ZERO" if
               observation["native_ledger"]["accepted"] == 0 and
               observation["native_ledger"]["rejected"] >= 1 and
               observation["native_progress"]["leaf"]["E"] == 0 else
               "FORGED_FACT_UNSAFE")
    _case(rows, "B03_untrusted_fact_not_accepted", "FORGED_FACT_REJECTED_E_ZERO",
          outcome, boundary="G2_ISSUER_REVIEW_POLICY_NOT_QUALIFIED")

    moved = _t01()
    moved.provider.heads = [HEAD, "c" * 40]
    _expect_hold(rows, "B04_stale_head_refused", "PROVIDER_MOVED_DURING_READ",
                 moved.run_preflight, boundary="G2_EXACT_HEAD_MATERIAL")

    # G3 original native material-ref incompatibility is explicitly retained.
    full_ref = _t02()
    full_ref.graph["nodes"] = [
        {**node, "primary_pr": "example/Pipeline#740"}
        if node.get("ref") == LEAF else node
        for node in full_ref.graph["nodes"]
    ]
    full_ref.graph_source = FakeGraphSource(full_ref.graph)
    _expect_hold(rows, "B05_native_full_pr_ref_holds",
                 "NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY",
                 full_ref.call, boundary="G3_OWNER_PROTECTED_PATH_GRANT_REQUIRED")

    # G4 plan vs real provider write must stay visibly distinct.
    publisher = _t03()
    plan = publisher.build()
    result = ("PLAN_ONLY_UNATTESTED" if plan["status"] == "PLAN_ONLY_UNATTESTED"
              and plan["writes"] == 0
              and plan["production_authorized"] is False
              and all(publisher.observed[ref]["body"] in plan["surfaces"][ref]["expected_body"]
                      for ref in (ROOT_REF, LEAF, PR_REF))
              else "UNSAFE_PUBLISHER")
    _case(rows, "B06_three_surface_plan_preserves_human_text",
          "PLAN_ONLY_UNATTESTED", result,
          boundary="G4_NO_LIVE_GITHUB_MUTATION")

    # A partially matching readback must not masquerade as a complete sync.
    partial = copy.deepcopy(publisher.observed)
    partial[LEAF]["title"] = plan["surfaces"][LEAF]["expected_title"]
    partial[LEAF]["body"] = plan["surfaces"][LEAF]["expected_body"]
    partial_result = reconcile_publication_readback(plan, partial, {})
    partial_status = ("INCOMPLETE_SYNC" if
                      partial_result["status"] == "INCOMPLETE_SYNC"
                      and partial_result["verified"] is False and
                      partial_result["production_authorized"] is False
                      else "PARTIAL_UNSAFE")
    _case(rows, "B07_partial_sync_refused", "INCOMPLETE_SYNC",
          partial_status, boundary="G4_PROVIDER_CAS_READBACK_REQUIRED")

    # Even an artificial perfect observed-after object is not authorization.
    all_after = copy.deepcopy(publisher.observed)
    for ref in (LEAF, ROOT_REF, PR_REF):
        all_after[ref]["title"] = plan["surfaces"][ref]["expected_title"]
        all_after[ref]["body"] = plan["surfaces"][ref]["expected_body"]
    fake_native_status = {
        ref: {"version": 1, "input_digest": plan["expected_native_input_digest"]}
        for ref in (ROOT_REF, LEAF)
    }
    match = reconcile_publication_readback(plan, all_after, fake_native_status)
    matched = ("OBSERVED_MATCH_NOT_AUTHORIZATION"
               if match["status"] == "OBSERVED_MATCH_NOT_AUTHORIZATION"
               and match["verified"] is True
               and match["production_authorized"] is False
               and match["writes"] == 0 else "MATCH_UNSAFE")
    _case(rows, "B08_simulated_full_readback_still_not_authority",
          "OBSERVED_MATCH_NOT_AUTHORIZATION", matched,
          boundary="G4_AUTHORIZE_REAL_TRANSACTION_SEPARATELY")

    # G5: merged PR is not external lease revocation or independent B.
    merged = _t01()
    merged.provider.pull["merged"] = True
    merged.provider.pull["state"] = "closed"
    result = merged.run_preflight()
    outcome = ("NO_AUTOMATIC_SUCCESSOR" if result["pr_state"] == "MERGED"
               and result["automatic_successor"] is False
               and result["production_authorized"] is False
               and result["writes"] == 0 else "UNSAFE_SUCCESSOR")
    _case(rows, "B09_merged_pr_does_not_launch_B", "NO_AUTOMATIC_SUCCESSOR",
          outcome, boundary="G5_EXTERNAL_CUSTODY_AND_FOUR_CONTEXTS_NOT_RUN")

    # Public REST envelope is a SANITIZED REPLAY, not authenticated live source.
    replay = ObservedEnvelopeFixture()
    adapter = replay.provider()
    result = adapter.get_pull(PR_NUM)
    result2 = adapter.get_issue(LEAF_NUM)
    observed = ("SANITIZED_REPLAY_SHAPE_VALID" if
                result["head"]["repo"]["full_name"] == "reallakshman19/Common"
                and result2["number"] == LEAF_NUM
                and replay.reads == [("GET_PR", PR_NUM), ("GET_ISSUE", LEAF_NUM)]
                else "REST_SHAPE_INVALID")
    _case(rows, "B10_public_GET_envelope_replay", "SANITIZED_REPLAY_SHAPE_VALID",
          observed, boundary="G1_G2_PUBLIC_SHAPE_IS_NOT_AUTHENTICATION")

    gates = [
        {"id": "G1", "need": "Owner-authenticated current repo graph and original lab",
         "result": "HOLD_UNATTESTED"},
        {"id": "G2", "need": "Required checks, genuine positive+negative facts, independent reviewers",
         "result": "HOLD_UNQUALIFIED"},
        {"id": "G3", "need": "Protected full owner/repo#PR native fix and Owner grant",
         "result": "HOLD_NATIVE_MATERIAL_BOUNDARY"},
        {"id": "G4", "need": "Authorized live GitHub title/body/status CAS/readback",
         "result": "HOLD_NO_WRITES"},
        {"id": "G5", "need": "Isolated four-context B with externally revoked A lease",
         "result": "HOLD_NOT_RUN"},
    ]
    passing = sum(row["result"] == "PASS" for row in rows)
    return {
        "schema": "v32-325-synthetic-benchmark-v1",
        "classification": "SYNTHETIC_REPLAY_NOT_OWNER_ACCEPTANCE",
        "historical_graph_fixture": ".github/v32-evidence-spine/718-proposal-v2.json",
        "fixture_origin_repo": "reallaksh19/Common",
        "fixture_binding": REPO,
        "test_cases_pass": passing,
        "test_cases_total": len(rows),
        "expected_holds_observed": passing == len(rows),
        "cases": rows,
        "production_gates": gates,
        "owner_ac": "0/8_NOT_ADJUDICATED",
        "v32_live_writer": "OFF",
        "real_original_lab": "NOT_RUN",
        "real_github_managed_write": "NOT_RUN",
        "independent_agent_B": "NOT_RUN",
        "ready_for_production": False,
        "writes": 0,
    }


def main() -> int:
    try:
        result = run_benchmark()
    except Exception as exc:
        # A benchmark crash is RED, never a silent HOLD/PASS.
        print(json.dumps({"schema": "v32-325-synthetic-benchmark-v1",
                          "result": "BENCHMARK_ERROR", "error_type": type(exc).__name__,
                          "ready_for_production": False, "writes": 0},
                         sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["expected_holds_observed"] and not result["ready_for_production"] else 1


if __name__ == "__main__":
    sys.exit(main())
