# Engineering PR Delivery v3.6 — coding and task-continuity ADDENDUM

**Owner authority:** [Common #400](https://github.com/reallakshman19/Common/issues/400), additional Owner direction [#6220465115](https://github.com/reallakshman19/Common/issues/400#issuecomment-6220465115). Additive guidance only. The accepted native v3.6 O1–O5 lifecycle, exact AIM label, canonical TASK_EVIDENCE v3.6 parser, snapshot, publisher, separate v3.6 two-/three-pass generators and BuddyRunner 1a→1b→2 must not be changed by this addendum. Historical v3.5 practices are **copied as independent design invariants**, not imported as runtime dependencies.

## Original problem

After several engineers, activity reports and PR titles say that tasks progressed but do not preserve the original Owner WHY, original inputs/golden/benchmark, root-cause-to-code path, competing approaches, chat-delivered Owner technical amendments, parked improvements and reason for adopting a high-ROI fix. Ad hoc agents asked simply "follow v3.6" can also omit task-evidence entirely, because no coordinating agent appointed a governing work label and child. Make the issue **the navigable and lossless engineering record**; do not make a reporting tool another execution authority.

## Source-level v3.5 practice port audit (not a bulk version migration)

| v3.5 source | Behavior worth retaining independently in v3.6 | Native disposition |
|---|---|---|
| `operating-model/architecture-preservation-contract.md` | ROADMAP/Owner > bounded task; status projections distinct from material/execution/merge/release; recovery vs handoff; source-specific drift; immutable receipts | ADDENDUM rule, no v3.5 import |
| `scripts/owner_commands.py` / `SKILL.md` | Lossless direct Owner intent; meaningful chat amendments before technical normalization; quoted source cannot fake direct Owner instruction | Input custody for C2/C3, not auto-publication |
| `operating-model/agent-task-publication.md` | Owned child ISSUE with IMPLEMENTATION_PLAN, PLAN_UPDATE, TASK_EVIDENCE, TASK_RESULT; cross-issue links; conversation record for material changes | Preserve structure via issue chain; do not create unnecessary issue per reply |
| `templates/checkpoint-facts-v35.md` + `delp_projection_v35.py` | Agents publish facts for their own leaf, not percentages or titles; exact SHA/evidence refs; empty proof visible; changed HEAD invalidates old proof | Native v3.6 governed O2 stays mandatory; optional ad hoc receipt cannot set E count |
| `operating-model/parent-handover-ledger.md` | Parent=WHAT/WHY/roadmap, child=implementation/repro/test, handover=index; source before chat memory | C1/C2/C3 issue spine, append-only receipts |
| `operating-model/durable-execution-lineage-projection-v35.md` | Stable task identity/lineage, rejected stale bindings, continuity from current provider truth, E/P separate from Owner acceptance | C2/C3 and future C4; do not import DELP |
| `operating-model/owner-reporting-delta.md` | Report only what changed; status failure cannot become a new material-write safety gate | Read model, no new writer authority |
| `SKILL.md` continuation/coordination | Reconcile parent+Owner decisions, selected frontier, exact PR/CI, negative knowledge before “proceed”; recover missing checkpoints | C3 successor and this addendum |
| v3.5 BuddyRunner/2-/3-pass integration | Independent thinking, reconcile KEEP vs high-ROI IMPROVE, park ideas with return condition | Use current selected native v3.6 BuddyRunner or Handover Master version (no stage graft) |

**Caution:** Some v3.5 operating-model files document historical v3.1 recorder semantics and conflict with stronger security invariants elsewhere. Do not blindly port policies (e.g. permissive takeover, external lease weakness) into v3.6. Use current native v3.6 and actual selected product protocol as binding authority.

## Ad-hoc task evidence — optional only when NO protocol is selected

Precedence is explicit:

| Conditions observed | Result |
|---|---|
| Project Team Protocol `TASK EVIDENCE v2`, or another explicit programme protocol | It wins; its evidence is mandatory on its governed surface |
| Approved v3.6 `relay/AIM/<WORK>.yaml` + matching plan + actual owned child | Existing `TASK_EVIDENCE v3.6` **mandatory** at finished task boundaries; original parser unchanged |
| Someone says "use v3.6" but no approved label/plan/child exists | No fictitious v3.6 O2 or task progress; HOLD native admission, allow harmless investigation |
| Genuine ad hoc agent, no explicit/project evidence scheme | OFFER optional `TASK_EVIDENCE — ADHOC` (readable evidence), chat-only unless authorised issue target |
| Ad hoc agent expressly selects another evidence protocol | Follow it; DO NOT add a v3.6 receipt in parallel |
| Explicit and project protocols conflict | HOLD/conflict disclosure; do not choose the lax one |

Ad-hoc receipt is a helpful default **invitation**, not a mandatory protocol on a foreign agent. It must not begin the exact three-line "Outcome / For the user / Proof" native `TASK_EVIDENCE v3.6` opening or include the literal `TASK_EVIDENCE v3.6` parser token. It is never eligible for v3.6 publisher progress, issue title mutation, material/merge/release permissions, or TeamOwner TASK EVIDENCE v2 credit. An explicit selected protocol is respected and validated by *its* real governing code.

### Optional ad-hoc receipt example (not proof)

~~~text
TASK_EVIDENCE — ADHOC / ADVISORY (NOT v3.6 O2)
Issue chain: #123 → ~~#125~~ (INVALID_REPORTED: out-of-scope; decision ref) → #126
User outcome: <what changed for the user, or nothing yet>
Exact source/candidate SHA: <40-character actual SHA or UNKNOWN>
Implementation crux: <entrypoint -> adapter -> worker -> consumer; source links>
Original fixture / golden / benchmark: <original hashes or specific UNKNOWNs>
Tests on exact SHA: <hosted run, negatives, environment; else NOT_RUN>
Observed result / negative knowledge: <precise claim, hypothesis vs proof>
Next source-first verification: <one reproducible check, blocking authority>
Owner/academic/merge acceptance: NOT_GRANTED
~~~

If no exact commit exists, the **programmatic receipt refuses** instead of printing fake SHA. Human-only draft can explicitly say UNKNOWN without claiming an exact source. Never publish Owner-provided private chat or source files to public GitHub without authorization.


### Native v3.6: continuity must be a SEPARATE issue-context receipt

Source-first compatibility: `lifecycle_v36.validate_evidence` requires the **exact eight-line canonical task-evidence comment** produced by `render_evidence`. It rejects **all trailing lines**. `snapshot_v36.snapshot` scans issue comments for the exact `TASK_EVIDENCE v3.6` marker before applying validation, so even an explanatory human comment containing that marker may generate a spurious invalid-evidence observation.

Therefore, on a **governed** child publish:
1. The existing **unchanged canonical eight-line task-evidence comment** on that child's issue (exact source, proof, candidate, tests).
2. A **different** linked comment, headed `CONTINUITY_CONTEXT v3.6`, containing the issue genealogy (`#123 → ~~#125~~ → #126`), original fixture/golden/benchmark source pointers, actual implementation crux, Owner amendments, causal known gaps, parked/adopted decisions, and one next verification. **Do not include the canonical task-evidence marker anywhere in this context comment.**
3. Link the context comment in the parent/child evidence spine, or if the protocol disallows a comment, in a separate authorized versioned issue index. It is **advisory context, not a second O2 proof or acceptance record**.

This is not yet an automatic publisher or index writer. The two-comment pattern is **planned** until the source-custody/provider integration C2/C3 is implemented, and requires the same authorized issue publication scope and privacy review as other technical Owner context.

## Issue lineage as a complete time-indexed path

Use a historical list/graph, not only today's active issue hops. An invalid/superseded middle step still represents a real attempted agent handoff, source decision or fixture.

### Example — purely illustrative, not actual Common issue status

`[#123](https://github.com/example/tracker/issues/123) → ~~[#125](https://github.com/example/tracker/issues/125)~~ (INVALID_REPORTED — wrong responsibility; [decision](https://github.com/example/tracker/issues/123#issuecomment-12345)) → [#126](https://github.com/example/tracker/issues/126)`

The arrow from #125 to #126 **remains**. The tombstone is not removed or replaced by a shortcut #123→#126. Each node keeps issue number, previous hop, status, reason and source-bearing decision receipt. A *status claim* can be shown as a reported tombstone; it is NOT verified by the renderer. A future C2 provider verifier must confirm actor, exact Owner decision and source before upgrading it to authenticated invalid/deleted.

Status rules:

| Status | Display | Reason |
|---|---|---|
| ACTIVE | Plain linked | Current candidate/path; not guaranteed accepted |
| SUPERSEDED_REPORTED, INVALID_REPORTED, DELETED_REPORTED | Strikethrough **plus** status/reason/decision link | Preserves history; indicates the disposition is reported, NOT authenticated |
| INACCESSIBLE_UNVERIFIED, NOT_FOUND_UNVERIFIED, UNKNOWN | Not struck; explicit warning/reason | A 404 can mean deleted, private, no permission or transient absence |
| Future DELETED_VERIFIED | Not in current C1 renderer | Requires independently corroborated deletion record beyond unauthenticated 404 |

The [synthetic test fixture](tests/fixtures/chainage-tombstone-synthetic.json) and [pure renderer](scripts/continuity_addendum_v36.py) test duplicate #s, broken parent edges, unsafe/foreign decision links, missing reasoning and false deletion classification. They cannot know about unknown *unpublished* intermediate issues; complete history depends on the owning issue index (C2/C3), append-only evidence and source actor/fixture verification.

## Workstream implementation coding checklist

- [ ] Verify current main, exact PR head, selected Owner AIM label/plan and original user problem before coding.
- [ ] Determine real source→effect chain, actual Writer/calc/adapter/Worker boundaries, dedicated source files and exclusive ownership.
- [ ] Identify original positive and negative fixtures, source blob/content SHA and golden completeness; never use synthetic data as acceptance proof.
- [ ] Reconstruct previous agents' meaningful contribution/false turns and Owner corrections from durable issues and relevant technical chat receipts.
- [ ] Choose KEEP vs bounded IMPROVE; record ADOPTED/REJECTED/PARKED with actual decision source, evidence and revisit trigger. No forced innovation.
- [ ] Declare tests that could falsify the proposed fix and check baseline-red vs introduced red, in actual user flow.
- [ ] Deliver small main-rooted PR, no patchwork or duplicate calculation engine; after tests reconcile candidate SHA to exact hosted results.
- [ ] Publish governed TASK_EVIDENCE on own child when required; in unbound ad hoc work *offer* an advisory evidence receipt, never mark native O2.
- [ ] Capture one human implementation crux: changed modules/functions, preserved consumers, before/after, observed failures and next verification.
- [ ] After source/issue drift, pause the affected unsafe step and re-evaluate; do not infer Owner merge/release or task priority from current titles.
- [ ] Never hide historical invalid issues or close chain history because an intermediate node is removed. Keep a tombstone with attributable evidence.

## Phase-safe relation to existing protocols

Handover Master chooses the currently approved process. BuddyRunner 1a remains HOLD, 1b independently reconstructs and 2 reconciles once, Xb→Y once; version selected by the project's real governing source. V3.6 native two-/three-pass keep their own stage definitions. No authored answer, finished fix or later chat solution goes to a blind Pass A. This addendum is **coding practice and read-only receipt/view only**, not another coordinator, module-scoring system, provider fetcher or execution lease.

## Next stages / limits

This is a separate main-rooted addendum PR, independent of draft #401 C1. Real source-provider attestation of Owner input/issue deletion, full original fixture/golden/benchmark, native successor wiring and the C4 automatic title/labels are NOT implemented here. Those require the Issue #400 C2–C7 programme and independently tested exact-head source. No current v3.6 source protocol, TeamOwner mode, hard-coded LAB title or protected decision is altered.
