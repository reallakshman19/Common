# BuddyRunner v1.5 — Purpose-first engineering buddy

## Intent: reconstruction with high ROI and hand-holding

BuddyRunner v1.5 helps a *new or continuing* engineering agent avoid blindly continuing an old PR. It teaches the agent to reason in this order:

**Current issue → Parent issue → Original roadmap/Owner WHY → Exact inherited source → Agent's own purpose → Smallest module corrections → High-ROI reconciliation → Technical handover.**

The value is not counting tests or issuing another process certificate. It is a defensible explanation, in normal language with code references, of **what the user needs, what exists, which module should change, why that change helps, and what should remain unchanged**.

The two stages:

- **Stage 1: Independent purpose discovery** — source-first, read-only application investigation. Write a module-level REUSE/MODIFY/ADD/PRESERVE recommendation, explain Parent/Roadmap context in plain language, compare competing PR implementations and publish a purpose proposal on the existing issue where authorized. Do *not* start coding or a test campaign.
- **Stage 2: Course correction + ROI + handover** — re-open the Stage 1 proposal, challenge it against the Owner and live code, choose one authority per responsibility, accept/park/reject up to three ROI improvements, then create a full successor-readable technical handover. Reconcile source/test truth and explain unresolved independent acceptance. Do *not* merge, deploy, change programme status or promote an executor.

**This is an OPEN-SOURCE reconstruction lane**, not the existing strict blind Runner B lane. Stage 1 can see current code/PRs; therefore blind independence is NOT claimed. For genuinely isolated custody-transfer trials use the existing ../STAGE1_INDEPENDENT_RECONSTRUCTION.md, ../STAGE2_SOURCE_RECONCILIATION.md and separate externally enforced read/freeze/Owner disclosures. Buddy v1.5 does not create a second Relay ledger, DELP projector, Owner authority or writer lease.

## Main schema and programmatic generation

- Normative request schema: ../../schemas/buddy-runner-v1.5.schema.json
- Python validated renderer: ../../scripts/buddy_runner_v15.py
- Stage 1 agent instructions: STAGE1_PURPOSE_RECONSTRUCTION.md
- Stage 2 agent instructions: STAGE2_RECONCILE_ROI_HANDOVER.md
- Regression tests: ../../tests/test_buddy_runner_v15.py
- Example case: ../../examples/buddy-runner-v15/lfj-stage1.json

Requires Python 3.10+ and the published jsonschema package. Install using: python -m pip install jsonschema.

From the Common checkout, run:

    python skills/engineering-pr-delivery-v3.5/scripts/buddy_runner_v15.py --input skills/engineering-pr-delivery-v3.5/examples/buddy-runner-v15/lfj-stage1.json --output /tmp/buddy-v15-stage1.md

Stage 1: the generated prompt contains an indented JSON **untrusted case packet** and explicit instructions to verify actual GitHub issues/source independently. The renderer performs schema/case link checks and Markdown assembly; it does not fetch, authenticate or publish anything. It rejects `--output` aliases of `--input` and writes generated prompts using an atomic same-directory replacement. All specific source findings must come from the agent's own live inspection.

Stage 2: copy the same case metadata, set the stage field to STAGE2, and add stage1_evidence with the **real** Stage 1 GitHub issue-comment URL on the **same owning current issue**, the exact assessed commit and the digest. Compute `artifact_digest` as `sha256:` followed by the SHA-256 of the **UTF-8 bytes of the published GitHub comment body's text**, exactly as returned by the provider, including original line breaks; exclude the URL, issue metadata, JSON quoting, API response wrapper and Markdown rendering. Generate the second prompt with the same CLI. The renderer checks the issue-link shape and source commit but **does not fetch the comment or verify its digest**; the Stage 2 agent must re-fetch and compare both. **Do not fabricate a digest, URL or readback grade.**

If Stage 1 was `NOT_PUBLISHED`, retain the copy-ready artifact, but **do not generate Stage 2 in this provider-backed v1.5 lane**. Obtain a permitted publication and genuine readback first; otherwise report `STAGE1_NOT_VERIFIED` and stop at the diagnostic. A local file's digest alone is not an accepted substitute for the provider publication. A syntactically valid claim with unreadable/mismatched provider evidence must likewise stop without an invented reconciliation.

## Evidence and safety

- Purpose proposal publication: a human-readable PLAN_UPDATE — BUDDY_V15_STAGE1_PURPOSE_PROPOSAL comment on the current existing issue, **if authorized**; otherwise copy-ready NOT_PUBLISHED.
- Course correction: PLAN_UPDATE — BUDDY_V15_STAGE2_RECONCILED_PURPOSE_AND_HANDOVER with current source, module ownership, ROI dispositions, next-start and handover link (if authorized).
- These are prose discussions, NOT TASK_EVIDENCE or machine CHECKPOINT_FACTS_V1; do not invent an E/P/D score, current test pass or governance grant.
- The schema validates *syntax*, not correctness of Owner-source identity, repository state, GitHub readback or content digest. No external fetch/credentials or side effects in the generator.
- Existing V3.5 Simplified=ON/OFF and Local v1.1 rights apply independently. This generator cannot lower real writer, protected-source, reviewer or release constraints.
- A valid result can recommend NO_CHANGE, identify a competing architecture seam, record unknown source/Owner permission and propose controlled verification before coding.

## First small example: LFJ

The example references the **historical assessed source** for XML→CII 2019: A3/H10 draft PR #184 against its pinned commit, with competing draft PR #185. It is deliberately an *intake*, not a pre-written answer or a recommendation to merge either branch. An agent must still re-read the current issue #132, parent #1, A1/A2/H10 and protected golden responsibilities, and independently decide how to reconcile the two approaches.

The agreed **illustrative Stage 2 objective** for this example is one authoritative, source-preserving LFJ Resolver in the *actual* XML→CII 2019 application. Before editing, reconcile #184/#185 Build, original-file identity, bounded hashing, cancellation/recovery, projection, revision and consent/CSV authorization. Assign one owner per responsibility and select compatible reusable components. Verify atomic source selection, declared complete-vs-subtree hierarchy scope and parity between full source-backed output, rendered tables and both downloads. Investigate the actual deployed artifact early, but reconcile its `docs/`/root import and Worker closure only after choosing the product implementation. Independent golden correctness, genuine Owner 30/90MB sources and downstream CII release remain separate. These are **questions and preservation criteria for an agent to verify**, not preaccepted diagnoses or permission to merge either product PR.

## Integration and custody

This capability is additive under V3.5. It does not replace V3.5's manual Prepare for runner, cannot launch a model, does not enforce a blind source allowlist and does not autonomously create two agent sessions. A true A→B transfer still uses the separate real Local/Owner control plane. Buddy v1.5 can *prepare much clearer engineering purpose and handover artifacts* without claiming any handover authority itself.
