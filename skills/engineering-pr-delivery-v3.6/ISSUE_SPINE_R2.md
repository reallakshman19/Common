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

## How to reproduce

```bash
python3 skills/engineering-pr-delivery-v3.6/scripts/issue_spine_read_v36.py --issue-url https://github.com/reallakshman19/Common/issues/400
python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_*.py' -v
```

The live read requires public GitHub read availability or `GITHUB_TOKEN` with **read-only** contents/issues permission, as required by GitHub API rate limits. No PAT with write scope is necessary; GitHub Pages/CoordinatorLandingpage is unchanged.

### Acceptance boundary

- [x] New standalone native read-only index reader and adversarial test doubles (coded in this draft).
- [x] One actual unique tagged index comment on owning GitHub issue #400 (provider publication).
- [ ] Hosted **exact-head** CI executes full v3.6 suite and this R2 live provider-read check.
- [ ] Index source refs 5/5 independently verified from current GitHub commit bytes/account readback; do not mistake 5 refs for 11 engineering categories.
- [ ] Independent source/security review and freeze/visibility qualification.
- [ ] Future R2 managed index integration with C1B append-only provider comment identities and real C2 original Owner fixture bytes and benchmark; not supplied by this small PR.
- [ ] R3 one-issue URL → full native twelve-section causal source-reconstruction, with external stage-disclosure control and no chat/LOG.
- [ ] R4 independent #274 plus Physics academic review cold pilot; no production/source/approval changes.
- [ ] R5/R6/R7 phase-specific Handover/2-/3-pass, optional title projection and Owner review/release.

**No regression or scope inflation:** no imports of v3.5/3.2/3.1/DELP, no writes, no new protocol precedence, no duplicate native successor, no smarter titles before real source-gaps are resolved.
