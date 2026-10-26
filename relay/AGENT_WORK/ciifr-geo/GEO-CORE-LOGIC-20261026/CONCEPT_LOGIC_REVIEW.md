# CIIFR_GEO core logic — separate concept review

Review attempt: `core_logic_final_review`, 26 October 2026, Asia/Dubai. Reviewer is a separate non-author agent, exposed to the Owner conversation, author explanation and prior reviewer findings. This is not a blind review, separate-account GitHub approval, product runtime assessment or Owner acceptance. This reviewer did not author the candidate and is not the previous mathematical reviewer. No candidate/product edits or GitHub posts were made.

## Actual subject and receipt

- Common draft PR536, immutable candidate `31d489f0fe55e564e292958149aad73d5f59a704`.
- Independently retrieved the complete `oracle-cycles/ciifr/continuity/payload/GEOMETRY_CORRESPONDENCE_CORE_LOGIC.md` through the GitHub connector at that commit, not the author's working copy or summary. Read all 20 sections.
- Retrieved content: 63,090 bytes; SHA256 `e5e86ceb03b60fb5c0d69a1bd3c19c9bc3bad6c76d6a4e84ab78afe0dc8b36a7`; Git blob `6226e2f7e616784bb64e96549d94c574af138a89`. These values were calculated locally from retrieved UTF-8 bytes and matched the connector blob ID and published manifest.
- Separately retrieved/read relay `README.md`, `INPUT_MANIFEST.json`, `SCORING_REFERENCE_PROBE.py`, `PROBE_RESULTS.json`, `NEGATIVE_PROBE_RESULTS.json` and `ENGINE_SEAM_OBSERVATIONS.json` at the same immutable commit.
- Read Common `AGENTS.md` and `skills/agent-work/independent-review/SKILL.md` at that candidate. No shared policy alteration or legacy Relay write is part of this review.
- Temporary retrieved files and executions reside in `core-logic-final-review-input/` in the shared task workspace. Native-engine observations were inspected as producer receipts; this reviewer did not independently rerun the native engine.

## Scoped assessment

The candidate preserves the Owner's A/B/Consolidated concept, corrected anchor labels, checkbox versus radio semantics, whole-SOURCE-group exclusion, selected-option participation in the fit, fixed identity cohorts, continuous original TARGET geometry and manual override. The screenshot arithmetic, cycling counterexample and minmax-versus-minsum contrast are internally consistent under the declared translation-only reference model. New policy choices are labelled proposals rather than Owner-adopted decisions. The full-product/browser/GPU limitations are explicit.

Two material contract gaps should be clarified before this becomes an implementation-default contract. They do not require withdrawing the concept or stopping unaffected review. The author independently identified the same gaps while this review was in progress; agreement is disclosed, not treated as independent discovery of those gaps.

## Findings

### F1 — Medium: define one comparable trial universe before computing minima or defaults

Sections 5.2, 7.3, 8, 10.2 and 12 distinguish rank/custody diagnostics, but the section-12 `min over o in Og` formula does not formally restrict its alternatives to one comparable universe. A builder could rank a 6DOF rigid fit against a retained-orientation translation preview, switch fitting freedom only for a difficult option, or default a lower-scoring reused-TARGET diagnostic over a custody-consistent assignment. That would change the intended mathematical problem despite each individual row carrying a status.

Required clarification: freeze fit freedom, solver/order, frame, custody and admissibility policy per search job; classify strict rigid, explicit numerical preview and non-evaluable cases; evaluate conditional minima within that declared universe. Preserve the native strict validator; a diagnostic observation interface is not an acceptance bypass. Distinguish a diagnostic best trial from a custody-consistent default. If a same-context slice is empty or has no alternate comparable option, return a typed no-comparison/no-support result rather than `min(empty)`, zero evidence, or a false “all individual minima” claim. If pins leave no feasible assignment, retain the diagnostic and pins with that explicit result.

Surviving-error challenge: the existing translation-only public probe cannot detect mixed 3DOF/6DOF production ranking or a validator bypass. Add explicit contract/acceptance examples for these cases.

### F2 — Medium: partial-search regret is not exact regret

Sections 10.2 and 12 correctly label incomplete search generally, but section 12 can still be implemented using an observed-subset minimum as `best_g`. If an unvisited alternative is better, observed regret is too small. For a visited assignment, observed-subset regret is a lower bound on full conditional regret, not an exact value. A partially searched assignment that appears to have zero regret can lose that property after its missing counterfactual is evaluated.

Required clarification: track completeness of each same-context counterfactual slice separately from joint search completeness. Exact per-group regret needs that slice complete under the frozen policy; a globally optimal coherent/minmax default needs appropriate joint coverage/proof as well. Otherwise expose provisional/lower-bound regret and best-found recommendations; do not certify exact zero-regret or optimum.

Surviving-error challenge: all existing public reference cases are exhaustive, so an implementation that silently treats two visited cases as a complete three-option slice could pass them. Include a seeded unvisited winning alternative acceptance case.

### F3 — Low: view-only invalidation is the proposed state model, not current delivered behaviour

Sections 13.3 and 15 propose camera/projection isolation correctly. Section 20.2 should explicitly distinguish this new numerical/view revision model from the current single-session prototype, whose projection changes currently revoke its epoch. This avoids reading the desired contract as an already verified implementation property. This reviewer did not rerun that prototype; the current-behaviour statement is author-reported and should remain so unless independently inspected.

### F4 — Low: make epsilon tie semantics deterministic

Section 13.2 supplies `1e-6 mm`, but a production floating-point implementation should define ties relative to the unrounded minimum (e.g. the minimum-score epsilon band), rather than use a nontransitive pairwise epsilon comparator while sorting. State how that tolerance applies to zero regret/coherent-status classification; preserve raw scores and do not let display rounding decide. This is an implementation clarification, not a contradiction of the reference fractions.

## Actual checks

1. `python core-logic-final-review-input/SCORING_REFERENCE_PROBE.py --output core-logic-final-review-input/ACTUAL_PROBE_RESULTS.json`: exit 0. Actual output was byte-for-byte identical to independently retrieved `PROBE_RESULTS.json`.
2. Independently created a local wrong variant replacing absolute-axis error with signed sums: exited 1, `AssertionError`.
3. Independently created a local wrong variant retaining the tested group in its own score: exited 1, `AssertionError`.
4. Inspected full equations and exact expected tables: tested group remains in fitting, absent from scoring; inactive alternatives absent from both; cycle improvements and the differing minsum/minmax choices agree with the numerical model. This supports those finite reference examples, not every possible geometry or production search.

The expected negative failures are falsification evidence for two wrong scalar rules. They do not establish production integration, native solver fidelity or search scalability. A faulty renderer, changed candidate identity, stale Worker or mixed trial-class search could survive all these reference checks.

## Untested scope and next action

No served browser, WebGL/GPU, native integrated consolidation, private original CII, independent-model physical qualification, transfer/Writer, full performance budget or Owner acceptance was executed. The native seam receipt is not promoted to an independent rerun.

Return F1–F4 to the Oracle for a narrow document clarification and immutable publication. Reassess the changed clauses and their acceptance/export consequences; no reason to rerun unrelated product checks or claim a product release. The present verdict is **concept/reference mathematics supported within the disclosed model; implementation-default contract needs the stated clarifications**.

## Delta reassessment — local v1.1, remote receipt pending

The author revised the specification while preserving the original review above. This reviewer read the complete diff from independently received31d to the local v1.1 candidate and inspected its changed surrounding clauses. Local candidate identity: 68,295 bytes, SHA256 `d20c37b566e427ad9847775847ad978907e2ae697eaab5bab7c19156b170dff6`, Git blob `086b52271ffc3d09268afe1f0312093774f33983`.

- F1 addressed in proposed P09: one declared fit/admissibility universe, no per-option fallback or strict-validator bypass, diagnostic versus custody-consistent defaults, typed empty context, all-pinned evaluation, and no-comparable-alternative/feasibility-forced labels. CU03/RG07 acceptance cases and trial-universe receipt fields were added.
- F2 addressed with per-context slice completeness, observed regret as a lower bound, and no exact minmax/simultaneous-minimum certification from incomplete slices/search. MC06 includes the concrete visited5/7/unvisited1 counterexample; exports retain bound kind and coverage.
- F3 addressed by explicitly separating proposed view/numerical revisions from the current prototype's reported projection-epoch behaviour.
- F4 addressed with a minimum-relative epsilon band, raw score/regret retention, explicit near-zero support, stagewise lexicographic filtering and SC10's epsilon-chain challenge.

No remaining material concept-contract finding from F1–F4 survives this inspected delta. This is a scoped document assessment, not adoption of P01–P09 or product acceptance. The mathematical probe was unchanged, so no unrelated product rerun is warranted. Final immutable GitHub receipt is still pending; local hash assessment alone is not claimed as remote handoff completion.
