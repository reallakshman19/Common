# QRT-EXPLAIN-D3 | authored cell review packet | 2026-10-12 | chat=6accb584

CELL REVIEW ARTIFACT, not a successor-chat handover. Footer handover=no. Academic reviewer / Owner not signed, accepted count remains 0/28.

## Pins, licensing and delivery state
- Branch in draft PR #193 stacked on unmerged H3 PR #190. Original source Grade9v3.5@9172f4ed550257df5e7771dc30797e8185cad8ad `TEST/imo-research/qrt-d3/explain.v1.json`; manifest `TEST/products/imo182-qrt-d3-explain.manifest.json`; four authored SVGs `TEST/library/figures/qrt-d3-explain-{construct,attempt,repair,transfer}.svg`; hosted QA `tests/test_imo182_qrt_d3_explain.py`.
- Source is ORIGINAL AUTHORED TEST, no official contest question, no admitted CORE2, `selection.core2=[]`. Only registered Core1, Core1A, Core1B, Core2A, Core2B roles; frozen owner golden `G-IMO-G9-FIVE-CORE-20261012` read-only.
- Sole renderer required: `python Shared/tools/render_core.py build --manifest TEST/products/imo182-qrt-d3-explain.manifest.json --out build/imo182-qrt/d3/explain --draft --reference`.
- Hosted run: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38245101026 ; initially QUEUED due repository-wide runner queue. **No rendered role QA, zero-gap or golden PASS claim until exact-head run succeeds.** No human academic verdict claimed.

## X/Y/Z/W and mathematical verification
- Primary EXPLAIN, D3 PROPOSED: X explain why a student retaining BOTH factored candidate values 4 and -1 for `sqrt(x+5)=x-1` is wrong. Y factorization `(x-4)(x+1)=0` already supplied, square and radical definitions known. Z develop causal nonreversibility sign explanation rather than merely solve. W protected: join `A=B => A²=B²` with the false converse (equal squares can have opposite signs), principal-root `sqrt(x+5)>=0` forcing WHOLE RHS `x-1>=0` and original-equality verification. Hint H3 alone may complete this bridge and is AFTER_ATTEMPT.
- Domain x>=-5 admits x=-1; the false root is NOT an invalid radicand. Squaring gives `x+5=x²-2x+1`, `(x-4)(x+1)=0`, candidates 4,-1. At x=4 sqrt9=3=4-1 true. At x=-1 sqrt4=2 while x-1=-2 false. Independent generic ±3 same squares and sign difference.
- Core1A independent exit `sqrt(z+6)=z`: squared roots 3,-2, domain radicand defined for both; z>=0 requirement and checks sqrt9=3 and sqrt4=2!=-2 select z=3.
- Core1B countercase `sqrt(9)=-3` (false) squares to 9=9 (true), so the specific failing implication can be isolated and reconstructed after attempt.
- Core2B changed original equation `sqrt(t+5)=|t-1|`: squared candidate set unchanged {-1,4}, but absolute value ensures RHS nonnegative. Check t=-1: sqrt4=2=|-2|; t=4: sqrt9=3=|3|. BOTH original equalities hold. New answer is not a rewording of the target because the sign guarantee changes.
- Adjacent band D2 if the sign-loss bridge and its order are supplied, D4 if a novel principle must be invented. REVIEWER MUST decide EXPLAIN-D3 rather than APPLY-D2/D3; test and renderer cannot certify curricular appropriateness.

## Five-role technique self-assessment (NOT qualified academic approval)
| Role | Governed golden blueprint and slots | New page technique to check |
| --- | --- | --- |
| CORE1 | BP-CORE1-ORIENTATION@1.1.0 identity/orientation | Concept framing that squared candidates are not originals; directs independent practice |
| CORE1A | BP-CORE1A-CONSTRUCTION@1.8.0 identity/construction/repair_closure x2 | Three-stage generic diagrams opposite signs, forward implication, nonnegative ray; prediction, repair and different exit |
| CORE1B | BP-CORE1B-RECONSTRUCTION@1.1.0 identity/attempt/reconstruction | Wrong 'squaring reversible' route, generic signed falsifier, learner reconstruction and independent changed-boundary commitment |
| CORE2A | BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 identity/attempt/reasoning/support | Original graph of unsigned sqrt curve versus signed line without root mark; learner must make W, safe H1/H2, H3 only after nonblank answer; original checks in postcommit model |
| CORE2B | BP-CORE2B-TRANSFER@1.1.0 identity/attempt/post_attempt | Changed absolute-value RHS graph and sign logic, distinct two-root admissibility decision, own attempt before explanation |

## H/S/P/M twelve semantic tests (worker hypothesis pending hosted/browser verification)
| Code | Planned self-assessment | Concrete evidence |
| --- | --- | --- |
| H1 | target framing safe | Candidate-versus-solution wording, no selected root |
| H2 | orient, don't solve | Ask which ORIGINAL expression has restricted range without applying complete condition |
| H3 | AFTER_ATTEMPT | Third scaffold joins loss-of-sign and original test only after learner commits |
| S1 | initial meaning | Unsigned radical curve and signed line, no labelled intersection or target answer |
| S2 | staged prerequisites | ±3 symmetric sign values, one-way arrow, nonnegative ray shown as separate stages |
| S3 | generic sign connection | Concept card for opposite signed values does not leak target candidate verdict |
| P1 | protect W | No preattempt exclusion of -1 or complete x-1>=0 argument in authored figures |
| P2 | repair route | Core1A shows false converse and root nonnegative prerequisite without target solution |
| P3 | independent warrant | Both candidate original checks plus one-way implication, not just numerical rejection |
| M1 | wrong rule | 'Squared roots all valid' is diagnostic |
| M2 | falsifier | sqrt9=-3 vs squared 9=9 demonstrates logical error, not calculation slip |
| M3 | concept repair | Reconstruct missing branch restriction and independent sqrt(z+6)=z exit |

Zero-gap receipt, exact role HTML SHA, actual Playwright Chromium proof and immutable snapshot-lock check belong to the dedicated run and cannot be marked PASS while QUEUED. Qualified academic reviewer and Owner decision later; Owner D-182-3/4/5 do not block further original TEST work.

## Exact-head hosted delivery closing addendum | 2026-10-12 | chat=6accb584

This addendum supersedes only the previous QUEUED technical status, not the academically unreviewed verdict. Code @9172f4ed550257df5e7771dc30797e8185cad8ad (not later APPLY-only commits). Hosted [run 38245101026](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38245101026) **SUCCESS**: renderer `python Shared/tools/render_core.py build --manifest TEST/products/imo182-qrt-d3-explain.manifest.json --out build/imo182-qrt/d3/explain --draft --reference` wrote 6 pages, `receipt.gaps=[]`, `renderer=render_core/2`, `digest=5d5c942f60801a7b`, `semantic_digest=e752056e9307a3ef`. All 7 tests PASS incl original independent maths, frozen Owner golden five SHA locks, same role blueprint/slots and live Playwright Chromium gated nonblank attempt/H3. Artifact [11745844293](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38245101026/artifacts/11745844293) downloaded and locally inspected: all six HTML hashes independently reverified; Chromium opened each of Core1, Core1A, Core1B, Core2A, Core2B, screenshot captured, 0 JS errors.

| Role page | Existing governed blueprint technique match | Exact SHA256 |
| --- | --- | --- |
| Core1 orientation identity/orientation | BP-CORE1-ORIENTATION@1.1.0 | 41f7a86872cdd90a226c0982125ac41db7bc28a65f7bc000b901272834cf4e79 |
| Core1A staged construction / repair closure x2 | BP-CORE1A-CONSTRUCTION@1.8.0 | c928e949419090082c54f6016e21074cbf566196afd43cb2b90570598767553c |
| Core1B precommit wrong-route reconstruction and changed boundary | BP-CORE1B-RECONSTRUCTION@1.1.0 | ce527b3304f2f54793e26f4f83c2cb0c6b5f696dc0b35d005bc07630c37642e3 |
| Core2A unmarked graph, reasoning/support, H3 only after attempt | BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 | 55fc857de6f73beb88996bf41c31cbc7b358bc8c03933febf2dcc4dfcd694f76 |
| Core2B distinct absolute-value sign transfer and postattempt proof | BP-CORE2B-TRANSFER@1.1.0 | cb16c27aba85008888466c705d1580772515f890ce51887b49cdd8341016972a |
| Index | Navigation only | ef0c6d5fb26535b94b84338cdeaf752d7cb35a92c3824c1790fed72050a1b4f7 |

H1/H2 before attempt protect W; H3 after committed response passes actual Chromium. S1 original unmarked signed graph; S2 3 separate generic SVG stages; S3 independent ±3 sign counterexample, all technique PASS. P1 signed-loss W not exposed as target worked answer before learner attempt; P2 general one-way-square/sign repair; P3 two checks against original equation and why. M1 'all squared roots valid' diagnosed; M2 sqrt9=-3 despite 9=9 tests misconception; M3 reconstructed original sign check plus independent exit. These 12 H/S/P/M checks are **worker technical self-assessment**, not human academic reviewer signature. **Independent reviewer and Owner QRT acceptance PENDING; no golden successor, blueprints, accepted canonical QRT table or production product changed.**
