# R3 — Native v3.6 source-cited twelve-section cold handover

**Primary Owner requirement:** [Complete Owner document on Common #400](https://github.com/reallakshman19/Common/issues/400#issuecomment-6223067953) — a tenth successor must recover original engineering WHY, original production inputs/goldens/benchmarks, Owner amendments, meaningful per-agent source actions, valid/invalid issue hops, parked ideas and true blocked-next from GitHub alone. Twelve populated headings **without source references are NOT acceptance**.

**Entry point:** the **existing** `scripts/successor_v36.py`, not a new delivery or handover controller. Its previous governed `cold --label --plan --lab ...` and `buddy --phase 1a/1b/2/Y` paths remain unchanged. The additive R3 route is:

```bash
GITHUB_TOKEN=<read-only token> python3 skills/engineering-pr-delivery-v3.6/scripts/successor_v36.py \
  cold --issue-url https://github.com/reallakshman19/Common/issues/400
```

The **only caller-supplied project input is the issue URL**. Authentication is taken from `GITHUB_TOKEN` if set, with GitHub Actions `contents: read` and `issues: read` permissions; the helper never requests write authority. The same R2 source reader already verifies owning issue, unique managed index, source-cut main SHA, live indexed comment actors/bodies, pinned Git bytes, two contiguous non-edited events, first-event C1B match, required predecessor SHA-256, safe public source and event chronology.

The separate pure `successor_issue_recovery_v36.py` module is **not a standalone executable generator**; it is called only by the existing successor `cold` CLI. After checking that the R2 status is `LIVE_INDEX_OBSERVED_CHRONOLOGY_PROVIDER_ONLY`, it re-reads audited source comments and compares the exact UTF-8 body digest and provider account/issue parent again to catch drift between audit and synthesis. Only audited comments and pinned files enter the citations allowlist. It refuses to produce a report without real Owner source/plan/C1B/C2/chronology/CI evidence references. It does not import v3.5/v3.2/v3.1/DELP, draft code in #403–#406 or a second coordinator.

## Twelve section source/authority contract

| Section | Source anchors | Strict epistemic status |
|---|---|---|
| 1. Original Owner problem and why | OWNER_STATEMENT, EVENT_0001 | Real public statement; Owner authorization not authenticated |
| 2. Required outcomes and acceptance | OWNER_STATEMENT | Exact Owner-supplied acceptance description, not derived PR counts |
| 3. Later Owner amendments and corrections | EVENT_0001, EVENT_0002, OWNER_STATEMENT | **UNKNOWN** beyond bounded verified events; agent plan is not an Owner amendment |
| 4. Original input fixtures, goldens and benchmarks | OWNER_STATEMENT, C2_ORIGINAL_REFERENCES | C2 manifest document pinned; external original file and complete golden **NOT** reattested |
| 5. Repository source authority and current cut | ISSUE_INDEX, C1B_RECEIPT | Current Common main and pinned source evidence; not deployed converter |
| 6. Causal input-to-output implementation path | ISSUE_INDEX, REVISED_PLAN | Verified continuity reader path; physical XML→CII source-to-output consumer **UNKNOWN** |
| 7. Agent contributions and event chronology | EVENT_0001, EVENT_0002 | Two known events, NOT the entire ten-agent lineage |
| 8. Decisions, improvements and parked ideas | OWNER_STATEMENT, REVISED_PLAN | Agent plan reported; effective Owner decisions and park history incomplete |
| 9. Issue lineage and conversation provenance | OWNER_STATEMENT, ISSUE_INDEX | #123 → ~~#125~~ → #126 strictly illustrative; chat URL NOT_CAPTURED |
| 10. Executed tests and observed results | R2_VERIFICATION | Previous R2 119-test receipt reported; R3 product/academic acceptance not inferred |
| 11. Unresolved defects, drift and permission gates | OWNER_STATEMENT, C2_ORIGINAL_REFERENCES, REVISED_PLAN | Explicit HOLD/UNKNOWN, no authenticated full original/golden |
| 12. Next reproducible verification and successor handover | REVISED_PLAN, ISSUE_INDEX | One bounded verification; no premature release/merge |

**Source gate:** `verify_sections` requires exactly these twelve ordered section titles, meaningful text and at least one distinct `source_refs` ID per section. Each ID must resolve to a validated, actual R2-observed GitHub comment, owning issue, unique index or pinned Git blob. A source ID absent from the verified allowlist is a hard error. Unit tests deliberately remove the citation from **each of the twelve** sections, inject a non-existent source ID and test malformed source links. All must fail. A missing or reordered R2 event, missing original Owner source, changed body between audit and second read, or absent chronology blocks R3 output completely. No partial report is printed as success.

**Hosted end-to-end proof:** the PR's path-scoped `.github/workflows/v36-r2-live-issue-spine.yml` runs the entire existing native tests and then calls the real successor with only `--issue-url` and the Common #400 URL, asserting 12/12 citation blocks, original Owner WHY, SOURCE/UNKNOWN distinctions, 119/119 previous R2 receipt, bounded two-event chronology and an explicit release HOLD. The generated full Markdown is retained for reviewer inspection under the GitHub Actions artifact `v36-r3-issue400-twelve-section-handover`.

**Explicit limitations:** GitHub owner/login observation is not cryptographic proof the Owner approved its assertions. Current issue records are not permanently immutable; a trusted tail witness is still needed to exclude coordinated deletion of an unanchored trailing event. R3 cannot manufacture the missing original Owner physical XML, complete golden or source-to-output model, or independently approve Physics/3D_Converters semantics. This is a **real source-cited twelve-section handover with honest UNKNOWNs**, not proof that all 12 technical sections have complete evidence. The independent #274 and Physics cold-agent falsifiers, official source-byte oracle, protected reviewer and Owner acceptance gates remain outside this PR slice.

**Authority:** PR #407 stays DRAFT/UNMERGED; the native accepted v3.6 lab, task evidence, accepted publisher, Buddy 1a HOLD and 2-pass/3-pass boundaries remain unchanged. No GitHub issue or title writes from the new code; only read-only GitHub requests and a hosted CI artifact.
