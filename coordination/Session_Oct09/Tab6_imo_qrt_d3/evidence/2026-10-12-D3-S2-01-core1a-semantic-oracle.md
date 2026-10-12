# D3-S2-01 | Exact-head Core1A/golden learner-state oracle | 2026-10-12

Outcome: O1 (registered-blueprint Core1A and related learner experience against frozen golden); O3 only if a missing registered affordance is observed.
For the user: No public learner workflow was changed. The existing authored TEST renderer output was rechecked in an isolated browser against the Owner golden's role/technique contract; QRT acceptance and new golden designation remain open.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38260460672/artifacts/11752107953 ; https://github.com/reallakshman19/Grade9v3.5/blob/684dc823caca93d51fd172d12382e65670d93323/golden/TECHNIQUES.md ; this audit.

## Identity / boundary

- Successor chat `6accf855`, current issue #182 plan revision r2: https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6127768791 .
- Examined product PR#193 DRAFT/unmerged exact HEAD `684dc823caca93d51fd172d12382e65670d93323`, stacked on #190 `67c34dababb0da0ef7d5f4a532bfcf3119754961`; first workpack in closed Stage2 Common/main `handovers/2026-10-12-g1-2.md`.
- Source identity: `TEST/imo-research/qrt-d3/synthesize.v1.json` source blob `f3ec184c8c20235a284159ed483ae3ab0fc87f91`, `TEST/products/imo182-qrt-d3-synthesize.manifest.json` blob `a3c1d186a5e319717388bb55116ad65b1c8b566c`, `selection.core2=[]`, AUTHORED TEST, no official SOF question.
- Downloaded actual Actions artifact `11752107953` (run `38260460672`), ZIP SHA-256 `683ee90126b359ebfc3ddf90a8f1b7d98e250209cd2deab5e5773c4e5bab0cae`, matches GitHub artifact digest. `render-receipt.json`: renderer `render_core/2`, `held_to=REFERENCE`, `mode=PAGES`, `draft=false`, `gaps=[]`, digest `0a0f599b8f8f9afa`, semantic digest `65867e229c198315`, five roles plus index. Independently hashed all six actual HTML byte files and matched artifact `synthesize-d3-sha256.json`.
- No modification of Grade9v3.5 source, registry, renderer, frozen golden or user-facing routes.

## Actual role HTML hashes and golden role comparison

| Role | Hosted actual SHA-256 | Registered blueprint / slot sequence | Frozen Owner role SHA-256 | Evaluation |
| --- | --- | --- | --- | --- |
| Core1A | `94a4461820dd96c23300e13dabc847ebaf339983a0ba1e57ced9aea6e653e316` | `BP-CORE1A-CONSTRUCTION@1.8.0`: identity/construction/repair_closure/repair_closure | `c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004` | Three sequential SVG disclosures, independent exit (odd unit digits); structure aligns to golden's 3-stage parity/residues/coprime construction, but content and direct learner study differ |
| Core2A | `c4fe72dc54516e96765a53bf4a1cdb130eabeef18374de021a735660f610c51c` | `BP-CORE2A-SUPPORTED-APPLICATION@1.1.0`: identity/attempt/reasoning/support | `e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777` | Authored original count, H1/H2 opt-in, H3 gated AFTER_ATTEMPT as Owner decided; this intentionally differs from pre-H3 frozen golden |
| Core1B | `87ade789de1fcc3d739406703144a9b219fc6375b8f8a4fb2c9900cb10dcd44a` | `BP-CORE1B-RECONSTRUCTION@1.1.0`: identity/attempt/reconstruction | `3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562` | Mistaken AP→divisible9 route (246) and zero-hundreds 036, two independent commitment gates |
| Core2B | `49cbfc223e849c53b77978e06e7d05ebef735059e1110dfe6a3bb268c5a329bc` | `BP-CORE2B-TRANSFER@1.1.0`: identity/attempt/post_attempt | `91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39` | Changed divisibility condition 9→6 with new parity filter and independent counting demand |

Frozen source `golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json` (Git blob `888678554c41257e6d96c802f0009983ccbb5328`) protects five exact old HTML snapshots from `f87d2f627e3f05476d39fb04d7f26e453661dc68`. These are NOT byte-equal to new D3 pages; no successor golden accepted. Source/golden registered slot comparisons are a *technique comparison*, not a mathematical identity or full judged learner equivalence.

## Fresh scoped browser/DOM evidence

Downloaded the exact generated HTML and executed each role's existing inlined JS in a separate **Chromium headless** page at 1280×900, using `page.set_content` for byte-identical authored HTML. New external browser navigation to `file://` and `http://127.0.0.1` was rejected with `net::ERR_BLOCKED_BY_ADMINISTRATOR` in this sandbox; no claim that a hosted direct URL/assistive technology or golden snapshot was interactively browsed in this run. Static source/golden role/slot and named techniques were independently read through the GitHub connector. This prevents a claim of *full hosted-browser/golden behavioural identity*; it does not prevent inspecting the existing renderer output's inlined attempt/JS behavior.

Final local audit: **58/58 scoped assertions PASS**, 0 JavaScript exceptions in four examined roles. Assertions cover all six hosted page SHA receipts, `render_core/2` gap status, role blueprint+slot identity, Core1A stage1 initially alone / stage2 additive / stage3 all visible, independent odd-units exit, Core2A H1 initial / H2 after opt-in with no target-case leak, H3 outside preattempt ladder, blank written attempt and preattempt solution/H3 summary opening refused, written commitment then solution/H3 available, Core1B first reconstruct commitment plus *separately refused blank boundary* and unlocked after independent written second attempt, and Core2B changed divisor6 transfer and separate answer gate.

Screen-captured original renderer HTML on local Chromium after interactions: `core1a-final-verified.png` SHA-256 `4f8f833f47b2c313e372393bb95e22b771996b499e3107a722b8db7f161605ab`; `core2a-final-verified.png` `eafc1bbcdf3cc278818941d918d05f7cc342f447ca2c8f1519238ba5673f0827`; `core1b-final-verified.png` `4d978414b0307a4fd35b8bbc65f1bcd96cca2c9d57f801f2a4ec337b2ef36667`; `core2b-final-verified.png` `4c73019ce32d7dd4f7cd4752b5980b1b244cc2c3c9f44cb93bbf531500f535a1`. These screenshots are local audit attachments, not GitHub-hosted independently viewable releases; exact hosted HTML is linked above. The local check source and `oracle-assertions.json` were not product-repository commits.

## T01–T15 applied, limitations and decision

- T01/T02/T03/T11: learner Core1A concept steps, distinct compact anchor, staged H/T/U SVG and independent exit correspond to the design technique; golden's parity/residues/coprime teaching is a different problem. Cannot claim raw text/screenshot equality.
- T04/T05/T07: Core2A target-specific digit/conditions figure, actual H1/H2 requestable and answer after attempt. Core1A and Core2A displays refer to initial orientation, not prematurely exposing the final 14/t-case count; D3 difficulty and cue sufficiency await qualified judgment.
- T06/T10/T12: Core1B tests wrong AP-to-nine / leading-zero route, with separate written boundary and independent reconstruction; actual browser tested the second boundary refusal/unlock.
- T08/T09: Core2B retains three-digit AP invariant but changes divisibility test to 6, requiring parity filter; new complete-count reasoning not just a number substitution.
- T13/T15 official source/key fidelity not applicable: source is wholly AUTHORED TEST; no authentic Core2 selection. Current H3 AFTER_ATTEMPT is an intentional post-golden policy difference authorized separately by Owner.

**Technical finding: KEEP / NO_REGISTERED_BLUEPRINT_CHANGE on this sampled role/attempt oracle.** Observed role/slot and local learner gate behavior is expressible with existing registered blueprint through the sole renderer; no O3 missing affordance was demonstrated. **Acceptance boundary still OPEN**: frozen golden screenshots were not exercised in the same browser session, no screen-reader/AX semantic user study, no independent qualified D3 cognitive-band judgment, no Owner successor-golden designation, no QRT acceptance (accepted 0/28), no real public learner publication. The source's `microtopics[0].badge_reason` stale forbidden-coordinate wording remains documented for D3-S2-02 scoped metadata-impact evaluation; it is not visible in current rendered Core1A/core2a/body texts based on static term scan.

Status for task D3-S2-01: DONE (bounded exact HTML/learner-state oracle; O1 full product acceptance partial); no new product tests or CI triggered; local independent 58/58 audit assertions and inherited exact-head hosted CI are distinguished. Next: D3-S2-02 scoped SYNTHESIZE-SOURCE-REPAIR. If full golden behavioural certification is required, it needs a browser/runtime capable of opening original golden bytes alongside new hosted bytes and independent learner/AX review; do not substitute it with unchecked claim.
