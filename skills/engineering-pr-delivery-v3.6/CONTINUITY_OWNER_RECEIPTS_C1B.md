# C1B — Native v3.6 Owner input, issue lineage and ad-hoc receipts

**Parent:** [Common #400](https://github.com/reallakshman19/Common/issues/400)  
**User-supplied source:** [complete Owner intent preserved in #400](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223067953), SHA-256 `59c6d6ca34e98ba4e3079d6a2b7d39c0df9cefb1d6460cfb923d885603e2512d`.  
**Current proposed architecture:** [reconciled plan v2](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223085654).

## Owner WHAT/WHY (not an extra approval)

After the tenth incoming agent, the owning issue must expose original problem, authenticated/losslessly reported changes, original positive and negative fixtures, complete or UNKNOWN golden, benchmark, source-to-native output crux, individual agent contributions, PARK/ADOPT/REJECT with why and revisit, real successor history including invalid intermediate issue, and disclosed or missing conversation reference. A user asking “follow v3.6” in an ad-hoc task should have the **option** of a non-authoritative evidence receipt even without a coordinator. This is engineering **truth**, not merely more PR/CI counts.

The original document explicitly says **no exact JSON schema, automatic chat capture, publisher, or new permission model is approved**. This C1B schema is a **draft engineering hypothesis**, not Owner-adopted governance.

## No duplicate engine / native ownership

`scripts/issue_receipt_v36.py` is a pure stdlib-only, side-effect-free read-only module. It imports **zero v3.5, v3.2, v3.1, DELP or draft #403/#404/#405 runtime**, does not write GitHub issues, reopen PRs, change titles, publish chats, count canonical O2 TASK_EVIDENCE, or fabricate reviewer/Owner sign-off. It is an additive source-linked receipt *candidate* for the existing native v3.6 parent issue index. Do not install a new coordinator, independent successor or redundant source-of-truth database.

The file `owner-intent/2026-10-16-common-400-owner-concerns.md` preserves the **complete uploaded file** unchanged; this source and the parent Issue #400 are the Owner-intent entrypoints. Conversation-origin means supplied in this chat; GitHub issue author/creator readback is distinct from ChatGPT user identity and **not independent Owner verification**. The exact file SHA-256 is the source bytes receipt; actual Owner decision authority remains external and unauthenticated by this module.

## Receipt contract — `v36.issue-receipt-stream/v1`

A stream carries:
- `parent` and allowed repositories, so foreign issues do not silently enter the chain.
- An ordered `events[]` history with unique `EV-0001`-style IDs, `previous_digest` SHA-256 of the canonical prior event, timestamps, source refs, claimed source SHA, source class, actor account observation *without* Owner authentication, event kind, disposition/revisit and supersessions.
- Event kinds: `OWNER_INPUT`, `OWNER_AMENDMENT`, `AGENT_CONTRIBUTION`, `SOURCE_FACT`, `DECISION`, `ISSUE_LINEAGE`, `CONVERSATION_REFERENCE`, `ADHOC_EVIDENCE`.
- An `OWNER_INPUT` or `OWNER_AMENDMENT` can only be `OWNER_DIRECT_REPORTED`. It cannot self-assert `OWNER_ACCEPTED`; its source may be withheld entirely as `CONTENT_NOT_PUBLISHED` without publishing private text, hashes or links. Actual identity and authorized publication must be independently controlled.
- Decisions can be `PROPOSED`, `PARKED` (mandatory revisit trigger), or `ADOPTED/REJECTED/SUPERSEDED_REPORTED`. A reported decision source is **not independent Owner permission**.
- `conversation_access` is `NOT_CAPTURED`, `RESTRICTED_NOT_PUBLISHED` or `AUTHORIZED_PUBLIC`; public mode requires an explicit ChatGPT share URL. This tool **never discovers/creates** conversation links or copies restricted identifiers.
- The stream is **append-only relative to a supplied previous snapshot**, verified with exact prior-event-prefix comparison. **A GitHub provider must still independently attest** original/current immutable comment bodies and a managed issue index before anyone can claim genuinely append-only server custody. A local hash chain by itself is only tamper detection of the supplied sequence.

## Invalid/superseded/404 issue rule — C-07

The `ISSUE_LINEAGE` event contains chronological ordered nodes and source-linked successor edges. Test-only illustrative example:

`#123 → ~~#125~~ → #126`

Strikethrough requires explicitly `INVALID_REPORTED` or `SUPERSEDED_REPORTED`, an issue-specific source reference and reason. It is labelled **reported**, not independently verified. An API 404 or forbidden issue becomes `AVAILABILITY_UNVERIFIED` with `NOT_FOUND_UNVERIFIED` or `PERMISSION_DENIED_UNVERIFIED`; it is never silently classified `DELETED` or struck through. A missing intermediate successor link fails validation, and an alternative edge cannot erase the original history.

## Governed task vs optional ad-hoc — C-08

Native official v3.6 evidence and a different explicit project protocol **take precedence**. An actual no-protocol, ad-hoc task may render an **optional copyable technical note** through `render_adhoc`, naming human outcome, exact repo@SHA, source flow, inputs/golden/benchmark, tests, issue chain, known failures, parked ideas, next single verification and optional authorized conversation ref. If no approved issue destination exists the output says `NO AUTHORIZED PUBLISH DESTINATION`; even with a destination the CLI **does not post**. It cannot count for O2 or prove a task complete.

## CLI and tests

```bash
python3 skills/engineering-pr-delivery-v3.6/scripts/issue_receipt_v36.py --stream skills/engineering-pr-delivery-v3.6/tests/fixtures/c1b-common-400-owner-reported.json
python3 skills/engineering-pr-delivery-v3.6/scripts/issue_receipt_v36.py --stream skills/engineering-pr-delivery-v3.6/tests/fixtures/c1b-common-400-owner-reported.json --render
python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_issue_receipt_v36.py' -v
```

The authentic #400 source sample contains only a **reported, publicly exposed** Owner document pointer and claimed digest; it does not invent an agent conversation link. The #123/#125/#126 scenario is a **synthetic negative/lineage test only**, never claimed to be an actual invalid GitHub issue. A future real issue index can reference validated receipts, but deployment/publishing needs an explicit authority and independent GitHub readback.

## Exact acceptance for this bounded workpack

- [ ] Original Owner file byte identity verified from committed candidate and attachment digest.
- [ ] Hosted native v3.6 tests and C1B negative suite pass at exact candidate SHA; no old runtime import.
- [ ] Provider readback of real #400 Owner-statement **comment existence, author login and content hash**. Provider actor observation must not be upgraded to Owner authorization.
- [ ] Correct issue lineage: reported invalid middle survives visibly, missing hop rejected, 404 remains unverified.
- [ ] Ad-hoc receipt copy-only; governed/alternate-protocol precedence proved.
- [ ] Sensitive conversation refs never exported without explicit authorized public ref.
- [ ] Independent security/privacy/source review after hosted CI.
- [ ] C1B linked into existing C1 issue spine after contract reconciliation; **not yet done**.
- [ ] Full C3 issue URL → real 12-section technical handover and C6 cross-repo cold pilot; **not yet done**.
- [ ] Owner merge/acceptance after independent qualification; **not granted**.

**R1 is a safe receipt/view foundation, not 100% engineering continuity.** R2 provider-verified append-only index, R3 source-first cold recovery, R4 adversarial #274/Physics, R5 phase filtering, R6 titles and R7 Owner acceptance remain separate workpacks.
