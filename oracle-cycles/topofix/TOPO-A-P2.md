# TOPO-A-P2 — Cycle brief (31 Oct 2026)

**You are coder-a (`6ae5bfb9`).** The Oracle checks every return, then an independent reviewer, before the Owner sees it. Report only in [issue #12](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12).

## Owner intent
An engineer who has reviewed a questioned connection (such as Node 6880 ↔ 6450, CLOS, 240.6 mm) must be able to **record a decision about it and take it upstream**, without the tool ever changing the XML. Spec: [TOPO-A concept spec R1](https://github.com/reallakshman19/progress-page/blob/main/docs/TOPO_A_ASSISTED_CONNECTION_CONCEPT_SPEC_R1.md) §3.2 and §3.4 ("Source Review Queue").

## What exists
- Draft [PR #14](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/pull/14) at head `a0962e77`. It provides the review-only **Find / Review Connection** panel and passed independent review at 93/100. Its review dispositions come from `closureBindingWitnesses`.
- The executable **Manual Fix Queue** (PR #11) is a different thing and stays untouched.
- **The Owner's trial of PR #14 on the private original is NOT_RUN.** You are building on an untried base, so keep this part separable.

## Your task: Source Review Queue (review-only)
Work on a new branch off `a0962e77`, and open a draft PR against `feat/topo-a-p1-review-connection-20261031`.

1. **"Add to Source Review" from the panel**, for any reviewed pair and any disposition, including `CONFLICTS_WITH_CLOS`. A pair whose source key is still ambiguous cannot be added.
2. **Each row holds:**
   - both exact port identities (source key, branch, Node Number, endpoint, owner);
   - the source sha256;
   - the disposition and the distance in mm;
   - an engineer decision from a fixed list: `INTENTIONAL_TERMINATION`, `DRAWING_CHECK_PENDING`, `UPSTREAM_SOURCE_CORRECTION_REQUIRED`, `NO_RELIABLE_DESIGN_AUTHORITY`;
   - an optional note and the time.
3. **A decision is an audit record, never an edit.** Changing it has no effect on the XML, the findings or the Manual Fix Queue. Show this text in the queue: "Correct in the upstream CAD/design source, then reimport."
4. **The same unordered pair is updated, not duplicated.**
5. **Stale source:** when the loaded source sha changes, existing rows show `STALE_SOURCE`. Never re-bind or delete them silently.
6. **Export and import** the queue as JSON, and export it as CSV (read-only evidence to hand upstream). An imported file with a different source sha comes in as `STALE_SOURCE`.

## Tests
- Unit tests for the queue model: add, update, de-duplicate, stale, export and import round-trip.
- A browser audit in `tests/audit-browser.mjs` on a synthetic 6880/6450-shaped fixture: review → add → set a decision → no Manual Fix Queue row → export content.
- A deliberate-failure test: anything that lets a Source Review row reach the executable queue or Apply must fail.
- Keep the existing Python and Node suites, and CI, green.

## Never
- Edit CLOS or any XML.
- Change tolerances.
- Join the 240.6 mm gap.
- Add Apply, or any path into the Manual Fix Queue, from a review row.
- Write to the PR #10/#11 branches.
- Touch CII Writer/Weight/Final.
- Put private model data on GitHub.
- Merge.

## Done = return in issue #12
- Draft PR link and head SHA.
- Changed-file list.
- Exact test commands and counts.
- One screenshot of the queue on the synthetic fixture.
- A deliberate-failure proof.
- What you ran vs only reasoned.

**Owner benchmark:** review 6880/6450, add it to Source Review, choose "upstream source correction required", export, and see that nothing in the model or fix queue changed.

## Every chat reply ends with this card (for the Owner)
```text
Task Evidence v2 · topofix · coder-a · TOPO-A-P2 · <time>
1. TASK: <repo> · WBS <id> · issue #<n> · PR #<n> <draft/state> @<head8>
2. PROGRESS: <done/total deliverables> · acceptance <none|scoped review|Owner>
3. WORK & PROOF: <what changed> · tests <n/n PASS|FAIL|NOT_RUN> · <permalinks>
4. BLOCKERS & RELAY: <receipt permalink or NOT_POSTED> · <review state> · <HOLDs>
5. NEXT → <ONE ACTOR>: <one bounded action> → <expected output> → <where>
```
Questions to the Oracle or the Owner: give options, each with a one-line reason ([PROTOCOL §0.8](../PROTOCOL.md)).

## Cycle receipts
Post an ACK (`action: received`) and a return (`work_returned` or `blocked`) on issue #12, using `ORACLE-CYCLE-RECEIPT v1` with `assignment_id: TOPO-A-P2`, `observed_revision: 3` and `role: coder-a`.
