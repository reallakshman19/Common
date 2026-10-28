# LOCAL_V1_1_INTEGRATED coordination mode

This mode is additive. Existing standalone / legacy V3.1 programme-coordinator interpretation remains readable and unchanged.

## Purpose

When Local PR Delivery v1.1 governs a parent programme, the programme coordinator may consume Local control-plane state and V3.5 nested-Coder evidence as **observations**.

It does not become an engineering acceptance authority.

```text
Local v1.1 Parent TASK
  +-- responsibility registry / release state
  +-- acceptance epoch/profile refs
  +-- Local role lifecycle truth
  |
  +--> engineering-programme-coordinator
  |      mode = LOCAL_V1_1_INTEGRATED
  |      authority = OBSERVATION_ONLY
  |
  `--> PRD-* / CODER
         `--> engineering-pr-delivery-v3.5
               ENG-PRD-*-CODER evidence
```

## Authority boundary

The integrated coordinator MUST NOT grant or synthesize:

- engineering PASS;
- Local role transition;
- product-write authority;
- acceptance-policy-write/adoption authority;
- risk-relaxation authority;
- merge authority.

These are recorded as explicit non-authorities in the machine contract.

## V3.1 compatibility

Historical/standalone coordinator records that refer to V3.1 remain readable under their existing contract.

Inside `LOCAL_V1_1_INTEGRATED` mode, a V3.1 reference is compatibility/history only and cannot select the active nested engineering provider. Native integrated observations must bind an exact `engineering-pr-delivery-v3.5` provider ref and digest.

## Evidence interpretation

A V3.5 result such as:

```text
ENG-PRD-017-CODER complete
```

may be observed as Coder engineering execution complete. It MUST NOT be projected as:

```text
PRD-017 complete
Local Reviewer complete
Local Coordinator/Super Review complete
merge ready
```

Those states remain Local v1.1 truth.
