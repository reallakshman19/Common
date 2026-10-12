# 182-P5-W01 | Owner v3.1.0 exact five-Core golden lock — O1 TEST proof

2026-10-12 | chat=6acc408a | tab=Tab1 | issue Grade9v3.5 #182 | P5 W01 | master v3.1.0 / label_sha 2ff9246 | outcome O1 | TEST-only hosted proof

Outcome: O1
For the user: No real learner workflow has changed. The five previously viewed TEST Core pages now have a reproducible exact-byte Owner-golden regression from the existing registered blueprint renderer, and a pinned fixture re-render with zero depth gaps; no standalone or hand-written HTML is presented as a deliverable.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38219621844

## Authority and exact identity

- Owner master `reallakshman19/Common/main:relay/AIM/IMO-CORE-BLUEPRINTS.yaml` v3.1.0 label_sha `2ff9246` git blob `5c8457bdef4a7019c29f90668fe3b51118a4a7ff`. The new parent aim explicitly forbids treating separately hand-authored/composer-made HTML as deliverables; every page must come from registered blueprint + `Shared/tools/render_core.py`.
- New **Owner-designated HTML golden**, not the older unrelated-algebra candidate: `golden/units/G-IMO-G9-FIVE-CORE-20261012` on unmerged #188 Owner commit `a8dbdad1dd316574514d8a74a33c59e177c9ab97`, designation `OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT` (Owner directive 2026-10-12T07:30:37Z “save this as a golden fixture”). Frozen five HTML role files were **generated** by sole renderer from `TEST/products/imo-182-five-core-integrated-review.manifest.json`, exact run [38215683516](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516), artifact `11732117118`, source commit `f87d2f627e3f05476d39fb04d7f26e453661dc68`, original digest `ad02fef42f0d505a`, same authored TEST-only snapshot.
- Only work added here: `tests/test_imo182_owner_golden_snapshot.py` and `.github/workflows/imo-182-owner-golden-lock.yml` on isolated unmerged [DRAFT PR #189](https://github.com/reallakshman19/Grade9v3.5/pull/189) head **`6307e5dd97f9ae72a052fc7f3e88c368a4cc5434`**, forked from #188's Owner-designated golden commit. No authoring, frozen snapshot, current blueprint, sole renderer, QRT, printer, public route, production, merge/release or source-rights edit. Original PRs #186/#187/#188 remain DRAFT and unmerged.

## SHA and renderer role proof

| Registered Core | Exact Owner frozen SHA256 | Result from source manifest regenerated via sole render_core.py |
| --- | --- | --- |
| CORE1 `BP-CORE1-ORIENTATION@1.1.0` | `f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e` | **BYTE-EXACT PASS** |
| CORE1A `BP-CORE1A-CONSTRUCTION@1.8.0` | `c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004` | **BYTE-EXACT PASS** |
| CORE1B `BP-CORE1B-RECONSTRUCTION@1.1.0` | `3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562` | **BYTE-EXACT PASS** |
| CORE2A `BP-CORE2A-SUPPORTED-APPLICATION@1.1.0` | `e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777` | **BYTE-EXACT PASS** |
| CORE2B `BP-CORE2B-TRANSFER@1.1.0` | `91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39` | **BYTE-EXACT PASS** |

- Hosted [run 38219621844](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38219621844) **SUCCESS**, job `114712447220`: `python -m unittest tests.test_imo182_owner_golden_snapshot -v` **4/4 PASS**: snapshot SHA256+git blob pins; original source manifest EXACT five role byte equality; pinned copied `golden/manifest.json` reference-depth renderer rebuild and role markup equality; all five role registered blueprint refs and protected-attempt anatomy; no authentic `CORE2` selected.
- Same hosted head `python Shared/tools/build_golden.py --id G-IMO-G9-FIVE-CORE-20261012 --check` reports `G-IMO-G9-FIVE-CORE-20261012: ad02fef42f0d505a · 6 pages · 0 gaps`. Six pages means **five roles plus index**, not an extra invented Core. `CORE2` selection empty; all authored questions TEST origin.
- Predecessor #188 [38215683516](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516) remains valid: 17/17 combined TEST page tests plus four role local attempt/reveal gate checks; predecessor #186 Core1A stage accessibility correction and Owner-complete Core1B preservation also remain grounded on their exact test input versions. New frozen snapshot establishes a stronger direct O1 oracle compared with old `G-MATH-LINEAR-CONSTRAINT` method-only comparison.

### Unexpected documentation-vs-behavior finding; no unauthorized golden edit

The Owner-designated fixture's `GOLDEN.md` / `snapshot-lock.json` prose predicts the pinned copy manifest yields a **different** authority render digest from the original source manifest. The first new CI test was deliberately strict but failed because the actual sole renderer instead emits **the same** digest `ad02fef42f0d505a` for both manifests (run `38219291462` failed 1/4 on incorrect `assertNotEqual`). That observation does **not** invalidate the snapshot: all five frozen SHA/git pin checks and original source byte-for-byte rebuilds passed in that first run. We changed only the test's unfounded digest-inequality assumption; the final new hosted run proves pinned copied records also regenerate matching HTML exactly (or only known digest normalized, if policy changes later). This is **documentation expectation drift**, not a missing registered blueprint feature, and the Owner frozen source/records/docs were **not edited**. The Owner can clarify the digest note if desired, but no golden rewrite is required for this successful O1 role-content proof.

## P5 disposition and remaining outcomes

- `182-P5-W01` **DONE** for exact-source TEST O1 five-page golden lock; no new HTML was authored, composed or published. A strict regression now fails on any frozen byte drift, incorrect blueprint role, missing selection or reference-depth gap. O1's golden-matching **technical condition is proven** for this authorized TEST artifact, but real learner outcomes, publisher acceptance and production are not implied.
- O2 is **NOT MET**: five-role packet [T8](https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6118945308) remains source-bound but no Owner/named reviewer accepted demand/band per role, `QRT-JUSTIFY-D2` only author-proposed and total accepted **0/28**. `D-182-2-H3` remains unresolved and must not be silently accepted because a snapshot is Owner-designated.
- O3 **NO_CHANGE / NOT_TRIGGERED**: no golden-required missing blueprint capability; frozen and re-rendered anatomy match exactly. A source/renderer digest documentation expectation is not a blueprint affordance gap.
- The previously linked A4 learner PDF is **non-A4**, shared-printer issue parked with Owner; real learner study not conducted; no merge/release, public route, source rights, actual Core2 authentic 68 question or KEY. Repo-wide guardrails and canonical assurance are separate from scoped hosted success and cannot be assumed green on this result.

**Next shortest unblocked O1:** no additional Core HTML authoring justified — exact five-page Owner golden is pinned and now reproducible; return the named O2 QRT decisions and H3 to Owner/named reviewer, and reopen O3 only if a subsequently approved golden reveals a provable missing registered blueprint feature. Preserve Owner-complete Core1B. Do not spin up unrelated print/lease/route/code work to count activity.
