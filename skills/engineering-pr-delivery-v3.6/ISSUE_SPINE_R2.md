# R2 — One-issue native v3.6 live evidence spine (read-only)

**Owner WHY:** [Full Owner supplied 12-concern statement](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223067953) · [reconciled R0–R7 plan](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223085654). A tenth agent should enter one issue URL and see original intent, source/code/decision lineage, missing original inputs, historic invalid intermediate issues and next verified work. A source pointer must never become Owner or product acceptance.

## Architecture and scope

The v3.6 `issue_spine_read_v36.py` is a **standalone read-only GitHub resolver**, not a new database, writer, coordinator, handover engine, publisher, or replacement for native v3.6 O1–O5. It imports only the standard library. It consumes the **existing native v3.6 issue/comment source** and treats three versioned draft contracts as **data** (C1 chain #403; C1B receipt #406; C2 manifest #404), not runtime imports or automatic approvals. Existing C3 successor #405 is unaffected. All four branches are independent/main-rooted and unmerged.

A previously authenticated real GitHub issue URL is the only CLI input. For the #400 pilot, one uniquely marked issue comment contains `v36.live-issue-index/v1` with exact source cut, claimed index actor, provider comment pointers, and pinned revision/path/Git-blob SHA references. Code:
1. GET the owning issue (not a PR), paginate comments, require EXACTLY ONE versioned managed index; missing/duplicate index FAILS CLOSED.
2. Validate index parent, declared source cut, allowed same-repo pinned references and source URL strictness, actor-provider account correspondence (not Owner approval).
3. GET each referenced source issue comment and independently read its issue-parent identity, account and body digest. Unavailable/foreign/mismatched is recorded as negative, not a false PASS.
4. GET source JSON via immutable `/contents/<path>?ref=<commit_sha>`, verify Git blob hash against actual decoded bytes, then **join by schema**:
   - C1B v1 receipt: must belong to same issue parent, and link its reported event source refs back to an actual provider-observed comment (no authorization inference).
   - C1 v1 issue-chain: if its `parent` differs, report `C1_FOREIGN_PARENT_EXAMPLE_NOT_LIVE_ISSUE_HISTORY`, not current history.
   - C2 v1 manifest: verify the manifest document's pinned byte identity, **not** its six external binary artifact bytes or complete semantic oracle. Those remain a distinct C2 test and source scope.
5. Compare the index's `main@sha` to live main and mark drift. All outputs forbid publication, title change, O2 completion, semantic/Owner acceptance and merge/release.

The single existing issue index was published as [Common #400 comment #6223440822](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223440822), not as a new GitHub issue or edited-away historical comment. It deliberately keeps 3D_Converters #274 external and the Owner original source and complete golden UNKNOWN. This #400 index is a **manual declared pilot**, not an automatically maintained production receipt generator.


## R2 remainder — source-bound live event chronology (added 17 October 2026)

The existing [managed index](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223440822) now includes two chronological `ISSUE_COMMENT` references named `EVENT_0001` and `EVENT_0002`. They point to genuine GitHub issue comments [EV-0001](https://github.com/reallakshman19/Common/issues/400#issuecomment-6226645841) (original Owner statement **reported**, *not authenticated Owner approval*) and [EV-0002](https://github.com/reallakshman19/Common/issues/400#issuecomment-6226646245) (agent's proposed revised plan). The index is a mutable projection, while the event comments are intended as an append-only historical record. They were published sequentially; there is no separate GitHub writer service.

The new `verify_event_chronology()` operates inside the **same native** `issue_spine_read_v36.py` (no import of unmerged #406). It checks the indexed event reference order and full provider comment ID, parent URL and actual publishing-account login, then verifies that:

1. Event IDs and envelope sequences are contiguous `EV-0001`, `EV-0002`, …, with no omitted middle event or reversed index order.
2. Each current GitHub comment appears unedited (`created_at == updated_at`), its byte hash agrees with a second GET during the read, and publication timestamps/IDs progress monotonically.
3. The previous-digest field equals the SHA-256 of the preceding canonical event JSON, and source-event occurrence times do not move backward.
4. The first event's complete typed data equals the immutable pinned C1B source fixture in draft #406. All public event `source_ref` links must resolve to observed, separately indexed source comments.
5. No event claims authenticated Owner approval or access to unpublished/private ChatGPT conversations. Source readback proves GitHub account observation, **not Owner authority**.

The output `event_chronology.status` is `PROVIDER_OBSERVED_UNEDITED_CONTIGUOUS_NOT_OWNER_APPROVED` only for an intact read. With no indexed events, the overall issue status is **HOLD**, not a success inferred from seven source references. Missing events, a gap, reordering, changed predecessor hash, tampered source, lost provider comment or edited event cause the reader to **reject** the chronology. Old v3.6 task evidence, publisher and BuddyRunner stages are unchanged.

**Limit of proof:** GitHub issue comments and their managed index can subsequently be edited. The module detects edits visible at read time and verifies its pinned initial prefix, but cannot establish permanent server-side immutability or detect every coordinated deletion of a *trailing* unanchored event. A separately version-pinned trusted tail witness or an authorized append-only Git writer is needed for a stronger non-truncation guarantee. This qualification does **not** authenticate the underlying Owner document author, prove complete product goldens, or produce the native 12-section technical successor report.

The included adversarial `test_issue_spine_read_v36.py` verifies explicit rejection of missing-first/missing-middle/reordered event sequences, wrong predecessor digest, backward source/provider time, edited comments and changed bodies. The hosted workflow also replays the **real #400 index**, requiring the two-event chronology and **7/7 provider-observed references**.

## How to reproduce

```bash
python3 skills/engineering-pr-delivery-v3.6/scripts/issue_spine_read_v36.py --issue-url https://github.com/reallakshman19/Common/issues/400
python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_*.py' -v
```

The live read requires public GitHub read availability or `GITHUB_TOKEN` with **read-only** contents/issues permission, as required by GitHub API rate limits. No PAT with write scope is necessary; GitHub Pages/CoordinatorLandingpage is unchanged.

### Acceptance boundary

- [x] New standalone native read-only index reader and adversarial test doubles (coded in this draft).
- [x] One actual unique tagged index comment on owning GitHub issue #400 (provider publication).
- [x] Hosted **exact-head** CI executes full v3.6 suite and this R2 live provider-read check.
- [x] Index source refs 7/7 observed (two source comments, three pinned JSON files, two provider event comments); this is not 11/11 engineering evidence categories.
- [ ] Independent source/security review and freeze/visibility qualification.
- [x] Bounded R2 remainder: indexed two real provider-observed C1B-shaped event comments, pinned-first-event source join, contiguous sequence/hash/actor/timestamp checks, negative gap/reorder tests.\n- [ ] Independent immutable witnessed tail, automatic event admission and complete provider-verifiable original fixture/oracle chronology; GitHub comments and mutable index alone cannot guarantee permanent append-only history.
- [ ] R3 one-issue URL → full native twelve-section causal source-reconstruction, with external stage-disclosure control and no chat/LOG.
- [ ] R4 independent #274 plus Physics academic review cold pilot; no production/source/approval changes.
- [ ] R5/R6/R7 phase-specific Handover/2-/3-pass, optional title projection and Owner review/release.

**No regression or scope inflation:** no imports of v3.5/3.2/3.1/DELP, no writes, no new protocol precedence, no duplicate native successor, no smarter titles before real source-gaps are resolved.
