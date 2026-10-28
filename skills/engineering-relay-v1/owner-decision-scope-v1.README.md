# R1-B.2a — inert Owner-decision **declared scope** checker

Programme [#787](https://github.com/reallaksh19/Common/issues/787) → [R1-B policy #792](https://github.com/reallaksh19/Common/issues/792) → [bounded task #802](https://github.com/reallaksh19/Common/issues/802). This is a **pure candidate evaluator** and is deliberately *not* an authorization engine. It imports neither draft provenance PR [#790](https://github.com/reallaksh19/Common/pull/790) nor GitHub source PR [#796](https://github.com/reallaksh19/Common/pull/796); their independent review gates #791/#797 remain pending. Do not merge or connect to writers without those gates.

`evaluateDeclaredScope(grant,proposal)` checks declared parent, issuer, role/action matrix, exact claim/resource/full commit SHA, valid/revocation window, receipt status/transport/issuer shape, and research finding/reviewer self-review constraints. It may return `MATCHES_DECLARED_POLICY_ONLY`, **never `AUTHORIZATION_GRANTED`**: `authorization_granted:false` is unconditional and `requires_native_provider_recheck:true`. Both inputs are **untrusted user-provided JSON objects**, including any apparent GitHub OWNER metadata. A claimed source `PROVIDER_ISSUER_OBSERVED` is not real provider proof without a trusted, current readback.

The design separates *claim checks* from *source/role policy authenticity*. Future R1-B.2b must verify a role grant already authorized from an independent preexisting source (not from the proposed decision), verify current GitHub comment/PR/commit facts, enforce scope and revocation, and support org delegation intentionally. R1-B.2c must gate research adoption with an actual authentic Owner decision. This module cannot authorize merge, GitHub writes, adopt research, verify original chat transcript or accept programme evidence.

Run `node --test skills/engineering-relay-v1/owner-decision-scope-v1.test.mjs`. Pure offline Node 22/24 CI uses read-only checkout, no secrets or write tokens.

**Design gap intentionally retained:** syntactically correct declared grants or source receipts can be forged. No in-process `true` from these inputs is proof of original Owner authorization. No persistent session logging or live scoreboard exists here.
## Explicit repository boundary

Scope matching requires declared grant-source comment, decision-source comment and action resource to belong to the governing parent repository. Lookalike/foreign repositories stay DENIED even if an untrusted grant and proposal both claim the same foreign resource. Cross-repository opt-in is future R7, not implied by a matching mock grant.
