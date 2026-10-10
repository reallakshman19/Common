# Stage 1 admission dry-run — three cases, real packet/link inspection

**Type:** REVIEWER_ONLY_STAGE1_STATIC_PREFLIGHT_V1 · [Common #890](https://github.com/reallaksh19/Common/issues/890) · PR #893. **Not a new Runner B session, provider access-denial test, sandbox, or external freeze.**

**Source basis:** GitHub readback of current PR candidate `docs/relay-890-continuity-md-v1` and immutable historical source identities already recorded in the case material. Dates and source cutoff are observations for the *historical fixtures*, not a claim about A's current implementation. **Do not send this document, its answers or its links to Stage 1 B.**

## Actual generic B-facing surface inspection

| Component inspected | GitHub blob | Outbound Markdown links to broad Common/Relay | Content result |
| --- | --- | --- | --- |
| Generic Stage 1 reasoning instruction | `8c2c870ddce2082a9b47610e5454dfe6ad09a7e6` | 0 | Part A historical system first, Part B original-problem reasoning second; A diagnostic risks withheld |
| Generic Stage 1 source-packet format | `18ee601f20213b349ef6a4952f9233b1dbd70258` | 0 | Source/Owner facts, no B-independent answer key |
| Generic Stage 1 reconstruction output format | `862193be2ba9478dd167290fae7ac74f0bf12085` | 0 | Controller freeze URL removed; submission still needs external proof |
| Core1B Stage 1 *case-specific* V2 packet | `75e7f1b7b9352f8bb4ee135c006ab1845b476eaf` | **3** | **FAIL B-READABLE RELEASE**: links to Common issue #890, historical Common GitHub tree and a relative controller/template path. These are invalid for an unrestricted B and need an operator-curated link-free B envelope; do NOT silently rewrite pinned V2 blob |

**Critical distinction:** The generic instructions are internally link-free; a *case packet* may still leak broader repository navigation. The actual Stage 1 release gate applies to the **concatenated input bytes**, not just the golden prompt. Link-free documents alone also do not enforce source access. Do not qualify Core1B V2 as a clean B input until a separately versioned sanitized release envelope is externally reviewed and really restricted.

## Two unrelated historical source domains — case-specific admission, not a B trial

| Domain | Actual historical source inspected | Static release issue | Correct verdict |
| --- | --- | --- | --- |
| Common V3.2 / R-PROJECTION | `Common@80a9c03d8f33ace129d21cb868c93e9359a8868a`; `delp_projection_v32.py` blob `d1f71b18733d9ffc833e91b12cd0792d3ad2bed2`, with evidence/projection/status functions | A complete historical source/fixture/Owner-provenance allowlist and true downstream provider readback were not supplied as a B release envelope. Current #733 status/PR is NOT acceptable Stage 1 original source. | `SOURCE_CLOSURE_INCOMPLETE / NOT_RELEASED` |
| 3D_Converters / LFJ+Resolver | `3D_Converters@6fdf84803443385337c5ecf2f1d40d934986240f`; scope-index blob `a29ed52cb907d91a6009c158d718c9800a0c8f44`; UI-events blob `178bdecbc92c69f5061ebf2bd09a4ef955db2c31` | The two source files alone do not provide all original downstream XML match/CSV consumers, authenticated original XML+JSON positive/negative goldens or served browser proof. Do not imply LFJ Worker or browser was qualified from old handler declarations. | `SOURCE_CLOSURE_INCOMPLETE / NOT_RELEASED` |

The examples are a test of *what the protocol must refuse to certify*. They are not a measurement of Runner independent thinking or output quality. Any missing original owner issue/source belongs under controller review, not another unsanctioned GitHub read by B.

## Static protocol checks versus unavailable execution checks

| Test | Observed facts | Disposition |
| --- | --- | --- |
| G-P01 — Generic Stage 1 instructions link-free | Fetched and inspected three B-facing generic Markdown source forms | **SOURCE-CONTENT PASS** (not an isolation pass) |
| G-P02 — Actual case packet metadata/URL scan | Core1B V2 has 3 Markdown hyperlinks into Common | **INPUT-RELEASE FAIL** for raw B delivery |
| G-P03 — Historical closure complete on R-PROJECTION? | One real large projection file, no complete approved closure/positive witness delivered | **HOLD** |
| G-P04 — Historical closure complete on LFJ/Resolver? | Index and UI-event declarations, but no complete consumer/golden chain | **HOLD** |
| G-N01 — Fresh B session identity/isolated creation | No external B launch receipt | **NOT RUN / HOLD** |
| G-N02 — Effective read denial to live A branch, issues/PR, Stage2 | No independent access-control log or negative probes | **NOT RUN / HOLD** |
| G-N03 — Alternative raw-url/browser/connector/shared-memory denial | No actual B context/tool inventory | **NOT RUN / HOLD** |
| G-N04 — Independent baseline/witness, frozen result, Stage2 source comparison | No actual B output, provider readback or freeze | **NOT RUN / HOLD** |
| G-N05 — Exclusive old writer revocation/new B admission | No credential fencing or scope/Local proof | **NOT RUN / HOLD** |

## Minimal repair decisions

1. **Generic repair now:** require a complete **exact B-readable bytes** audit before release, test source closure across authentic consumers and perform denial on B's actual effective tool identity. Added as the controller-only release contract and preflight receipt.
2. **Case-specific historical packet:** Core1B V2 is preserved as provenance, **not released**. A future actual operator may create a new immutable, link-free release revision with exactly the original curated facts, self-contained prompt/format and nine pinned source blobs (or explicit MISSING_APPROVED_SOURCE). Do not rewrite V2 or its published dispatch request.
3. **One launcher dependency:** without actual isolated B session capability, report `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY`; **do not** publish repeated Source-Integrity PASS notes.
4. **Exact next gate:** external operator accepts/updates one dispatch request, creates restricted session, returns actual denied-read receipt; then and only then can B produce a genuine Stage 1 reconstruction for separate freeze.

**Bottom line:** `DOC_CONTRACT_READY_FOR_OWNER_REVIEW` / `STAGE1_RELEASE_NOT_QUALIFIED` / `RUNNER_NOT_STARTED`. Future actions stay under Common/relay Markdown and canonical Local/Owner controls. No Python/YAML, Grade9/LFJ product source, Relay lease or DELP source was changed by this reviewer-only analysis.
