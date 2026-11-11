# CONTINUITY_IMPLEMENTATION_CHECKPOINT_V4 — Stage 1 operator release preflight

**Governing issue:** [Common #890](https://github.com/reallaksh19/Common/issues/890) · **Draft implementation PR:** [#893](https://github.com/reallaksh19/Common/pull/893) · **Record type:** source-readback contract review, not an agent-execution result.

**Pre-checkpoint candidate:** `b5d7b4914588b12f957b81a27edafbe582c60398` · **Original implementation base:** `d60c36605e988dcc160647421973f170fd87e0eb` · **Status:** Markdown contract changes committed; actual fresh Runner/access-denial/Stage2 still NOT_RUN. Committing this checkpoint creates a new HEAD; actual release receipts must be tied to exact immutable blobs, not a moving branch.

## What defect was corrected

A source-only packet and link-free generic prompt can still expose Agent A via an unsanitized *case-specific* input, an unrestricted GitHub connector or a response template linking to controller-only material. Read separation is not achieved by a repository folder name, a frozen source SHA or the agent's promise to ignore forbidden files.

**Generic repair now implemented:**
1. [Operator Stage1 release contract](OPERATOR_STAGE1_RELEASE_CONTRACT.md): profiles for offline-restricted input, scoped source proxy and non-blind rehearsal, with a positive historical read and negative forbidden-read probes **P01/N01–N06**. Every executed probe must be attributable to B's actual effective identity.
2. [Controller-only preflight receipt](TEMPLATES/STAGE1_RELEASE_PREFLIGHT.md): immutable release inputs, true B launch and session ID, tool/context restrictions, positive source read and denied current A branch/issues/PRs/Stage2/alternate tools; `NOT_RUN` denies a CLEAN verdict.
3. Existing Stage1 source packet and B output **templates** have zero links to broader Common/Stage2; the B response format no longer links to controller freeze. The generic Stage 1 golden prompt also remains link-free. Controller assembles only the approved input bytes.
4. V3.5 `SKILL.md`, Prepare command, Runner README, Relay README, dispatch request and runbook explicitly require actual release receipt before reporting an attested independent Runner.
5. [Reviewer-only static three-case audit](REVIEWER_ONLY/STAGE1_RELEASE_PREFLIGHT_DRY_RUN_V1.md) records **fail/HOLD** rather than fabricating success.

## Actual findings from existing evidence

| Item | Static source/readback verdict | Operational qualification |
| --- | --- | --- |
| Generic Stage1 golden prompt | Zero navigable Markdown links | Source-content PASS only |
| Generic Stage1 source packet & B output formats | Zero navigable Markdown links | Source-content PASS only |
| Core1B pinned Stage1 **V2 case packet** | Three outbound Markdown links: Common #890 issue, historical Common source-snapshot tree and a relative output-format link. Do not hand raw packet/whole Common repo to unrestricted B | `INPUT_RELEASE_FAIL`. Preserve pinned V2; a new sanitized *release* revision requires external controller review |
| R-PROJECTION historical review | Real `Common@80a9c03...` source exists, but complete historical allowed consumer/positive-golden envelope is absent | `SOURCE_CLOSURE_INCOMPLETE` |
| LFJ historical review | Real `3D_Converters@6fdf848...` scope index and UI event source exist, but complete original downstream XML/CSV/browser evidence envelope is absent | `SOURCE_CLOSURE_INCOMPLETE` |
| Actual fresh B session, tool denies, real B output | No provider/session/read-denial/outcome receipt | `NOT_RUN / NO_FRESH_CONTEXT` |
| Actual Stage1 external freeze, Stage2 and exclusive writer | No independent experiment, Owner admission or real old-writer denial | `HOLD` |

The above findings about Core1B links and other-domain source gaps are **static reviewer checks**. They do not demonstrate that a fresh model accessed any forbidden source, passed a read-denial test or achieved a user-visible application output.

## Source scope and inspection proof

- At pre-checkpoint `b5d7b491...`, Common compare from original base reported **28 Markdown files only**, all under `relay/CONTINUITY/**` or V3.5 Runner/SKILL Markdown. No edits to Relay state/events/leases/transactions, application code, Python, YAML, runtime or DELP.
- Relevant GitHub readback verified the three new release/preflight/reviewer records, link-free B-facing Stage1 source/response templates, V3.5 entrypoint and dispatch runbook.
- Checked **48 internal Markdown links** in the relevant new release/dispatch/entrypoint documents against the full exact Git tree: **zero missing targets**, tree not truncated.
- Existing historical Core1B V1 input remains preserved; the prior V2 case-specific packet is retained at its immutable blob instead of being silently rewritten.

## Explicit next gate (one action, not source re-verification)

An external operator with a genuine independent B-session facility must:
1. Accept the active source-pinned dispatch (or record `OPERATOR_UNASSIGNED` / `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` once).
2. Assemble a self-contained historically curated release envelope with no broad links, source closure and exact inputs; if missing historical dependencies, request a new reviewed packet revision.
3. Create a **new context** with actual source restrictions and execute allowed + forbidden reads (including alternative tools), recording real P01/N01–N06 result/identity.
4. Only after a release-attested read-only B starts, obtain its independent historical Part A and provisional Part B Markdown output. External controller freezes it before any Agent A reality or Stage2 release.

**Stop criteria:** no independent launch authority or real read controls → `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` / `READ_BOUNDARY_NOT_ATTESTED`. B may be used for an explicitly labelled *nonblind rehearsal*; it cannot be certified clean or promoted. Agent A remains the original primary writer. Owner/Local/DELP control planes remain authoritative.

**Release status:** `DOC_RELEASE_GATE_SPECIFIED` · `STATIC_NEGATIVE_CASES_OBSERVED` · `RUNNER_STARTED=NO` · `STAGE1_FREEZE=NO` · `STAGE2_ADMITTED=NO` · `WRITER_PROMOTION=NO`.
