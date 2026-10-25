# {{PROJECT}} — Agent OnBoard complex architecture and source semantics

**TEMPLATE / no engineering claims until source-filled.** Actor `{{Oracle/coordinator}}`; exact source `{{repo + commit + relevant lines/tests}}`. Explain *why* the current components and restrictions exist, not just their names. Original input/source semantics outrank this document.

## 1. Data, ownership, and trust boundaries for THIS task

```text
{{original authoritative byte/record/Owner object}}
  → {{parser/intake and field-specific version/rules, exact file}}
  → {{identity/state model: what is keyed, ordered, inherited or invalidated}}
  → {{bounded target module; what it MAY edit or compute}}
  → {{observed runnable candidate/result and actual validation}}
  → {{native reviewer/Owner release decision (separate claims)}}
```

**Actual code/spec links and why they matter**:
- `{{path@exact SHA to original parser/source interpreter}}` — `{{load-bearing rule}}`.
- `{{path@exact SHA to state/invalidation logic}}` — `{{what prevents stale alias/approval}}`.
- `{{path@exact SHA to output/consumer}}` — `{{who trusts it / when it is actually usable}}`.
- `{{test/negative issue permalink}}` — `{{what is genuinely observed, not assumed}}`.

A diagram is conceptual until verified against source; no generic process diagram proves domain identity/semantics.

## 2. Difficult concepts the agent must not guess

| Invariant / source issue | Original authority + concrete example | Why the shortcut is wrong | Counterexample or effect |
| --- | --- | --- | --- |
| `{{original item identity vs display identity}}` | `{{source/version/line/field/unit}}` | `{{incorrect deduplication, default, inherit, sentinel or guessing}}` | `{{opposite-case behavior}}` |
| `{{state revision/epoch/async ordering}}` | `{{state owner and invalidation condition}}` | `{{stale result/approval survives}}` | `{{different request/head/input generation}}` |
| `{{authority/provenance}}` | `{{original spec/reviewer decision}}` | `{{candidate/self test promoted to acceptance}}` | `{{wrong but green artifact}}` |

**Explain causal dependency:** `{{input A}}` changes → `{{state/check B}}` must be invalidated or recomputed because `{{specific source relationship}}`. If current code contradicts the proposed model, record **SOURCE_CONTRADICTION** and inspect/repair the model first rather than just changing tests to pass.

## 3. Current candidate, scopes and technical exposure

- Baseline/current head/diff ownership: `{{exact SHA, PR, edited files; no concurrent writers}}`.
- Tested actual result: `{{command/environment/input/output/exit + independent vs author}}`.
- Untested original/native/browser/custody requirements: `{{NOT_RUN and why; only affected claim}}`.
- Original bytes and target of modifications: `{{immutable source vs permitted output, real input locator}}`.
- Prior code authorship / review exposure: `{{SELF_ASSESSED / genuinely non-author scope}}`.

## 4. One informative end-to-end trace and opposite case

**Positive original source trace:** `{{source input/field → parser → state → expected output and origin of expected value}}`.

**Plausible surviving failure:** `{{different source state, repeated identity, missing unit, stale epoch, ambiguous candidate, invalid pointer or other domain-specific wrong case}}`.

**Discriminator:** `{{actual fixture, observable difference and test method}}` with **predictions before execution** when applicable. Report `NOT_RUN` rather than invent results. The recipient can change the hypothesis in light of original evidence within assigned scope.

## 5. Dependencies / reserved architecture decisions

- **Inside assignment:** `{{one bounded module/writable paths + safe tests}}`.
- **Outside / reserved:** `{{selection, coupling, product acceptance, irreversible writes}}`.
- **Next connected module or task:** `{{what output/candidate this work must supply}}`.
- **Safe independent work if one test cannot run:** `{{source analysis, disjoint test, documentation, narrow negative}}`.

**This file informs work; it never grants access or substitutes for the native task instruction.**
