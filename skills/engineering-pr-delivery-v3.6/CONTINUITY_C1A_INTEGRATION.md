# C1/C1A Integrated Continuity — native v3.6

Parent: https://github.com/reallakshman19/Common/issues/400

Baseline: Common main 0a7c4d45d3fa0787d3e80858a27015b09a85eac2

Reused exact heads:
- PR #401, issue-chain contract: 9397fa567933b2ca53ecbbaa28294cd2dbf82373
- PR #402, coding-practice and lineage/ad-hoc view: 727eac119b74074136d2b44dd3c21a12e4466be1
- CoordinatorLandingpage PR #49 is now merged. Its evaluator is kept separate.

## Owner outcome

A successor given only the issue URL should recover original Owner WHY, later material amendments, original inputs and complete goldens, physical benchmark and codepath, every important agent contribution, rejected/parked/adopted ideas with reasons, current exact proof limits and one reproducible next verification.

## One canonical structural source and two bounded helper views

1. issue_chain_v36.py is the ONLY C1 eleven-category structural accounting contract; its reported sources are not authenticated.
2. continuity_addendum_v36.py provides an historical issue-hop presentation and optional, unbound ad-hoc evidence selector. It does not create native task completion or write GitHub.
3. continuity_bridge_v36.py validates the eleven-category contract FIRST, optionally checks that the displayed lineage starts from the SAME owning issue/repository, and can separately inspect evidence-protocol selection. It is one read-only entrypoint, not a competing evidence authority.
4. Existing lifecycle_v36.py, snapshot_v36.py, publisher_v36.py, successor_v36.py and Handover Master remain unchanged in behavior. BuddyRunner, two-pass, three-pass, native owner gates and Team Protocol TASK EVIDENCE v2 remain independent.
5. Never auto-export private chats; never equate a syntactically present Owner link, Git blob hash or completed category with authenticated Owner instruction, semantic truth or release acceptance.

## Execution and tests

    python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_*.py' -v
    python3 skills/engineering-pr-delivery-v3.6/scripts/continuity_bridge_v36.py --input skills/engineering-pr-delivery-v3.6/tests/fixtures/issue-chain-274-reported.json
    python3 skills/engineering-pr-delivery-v3.6/scripts/continuity_bridge_v36.py --input skills/engineering-pr-delivery-v3.6/tests/fixtures/issue-chain-274-reported.json --inspect-protocol --governed-v36 --has-issue

The fixture's 41 branches, 423 components and 2961 FactRecords remain historical reported data; zero accepted Match-1 and Final weights at the cited run is not release readiness. Original full fixture and golden custody remain UNKNOWN. The synthetic #123→#125→#126 path tests preservation of middle invalid hops, not actual GitHub deletion.

## G1 exit and next gate

Gate G1 is implementation of a single native structural contract plus bounded compatibility helpers, subject to exact-head CI and independent review. Drafts #401/#402 are neither silently merged nor silently closed.

Gate C2 must independently fetch Owner issue actors and exact original fixture/golden bytes, check source SHA/digest/partial oracle, and classify UNKNOWN, STALE and VERIFIED at appropriate scope. C3 may then ingest qualified data into native successor. No title, label, site, workflow send or acceptance mutation here.
