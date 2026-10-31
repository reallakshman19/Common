# P1.2 original Windows return — reporting erratum F1

30 October 2026 (+04:00). Native task [#229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229); [receiver findings F1–F3](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229#issuecomment-6521095090). This append-only erratum corrects narration in the immutable `windows-receipt.md` at Common `52067c1b36d54f50c6945c3538dcc83967232fbe`; it does not replace or alter that historical return.

Product candidate: draft PR232 `d3fbd4041ef4434b4cf5b3c22459f06167be2729`. Exact product GitHub tree and separately committed `payload/evidence/source-verification.json` agree on all 11 source records. The receipt's two quoted IDs are stale:

| Path | Historical receipt quote | Correct exact-head Git blob |
|---|---|---|
| `docs/cii-fnr-vnext.html` | `d1b748eb12cefe7aa5ee5a1fbbeaa82c23dc03ea` | `3c0f8dae2ccc68f518f1ad582f1ba831a13a24ac` |
| `docs/tabs/cii-workspace/cii-fnr-vnext/ui/app.js` | `668702c81335cb8c1e7a022513ba6f59b02a249c` | `74891ccd948782b54b8f7781168e996c65d2af9e` |

The sanitized runner reports **six sampled file checks** (`blobVerified:6`). The separate source-verification artifact covers **11 source/served records**. These counts describe different checks and are retained distinctly. F1's identity narration is corrected by this erratum; no changed product is established.

The receiver independently retrieved all 11 manifest members plus the manifest: byte lengths, SHA-256 and Git blob identities match. `READBACK.json` contains the actual measurements; `SOURCE_COMPARISON.json` contains the actual product-tree comparisons. Edge/Chrome sanitized outputs share a deterministic 783-byte blob; this is not by itself a defect, nor proof of two distinct executed browsers.

**Status remains executor-reported SELF_ASSESSED PASS; execution authentication pending F2/F3.** Neither this custody check nor the reporting correction authenticates private process logs or the presence of `--expected-sha`. No new browser run occurred in the receiver environment. Root previously authored PR232 repairs and R3 public-fixture harness work; this is reporting reconciliation, not independent engineering acceptance.

**Next actor:** existing local qualification agent `01429edb` supplies the small per-run addendum already requested in #229, using preserved private command/process evidence where adequate. `LOCAL_AGENT_ADDENDUM_REQUEST.md` gives the exact remaining facts and fallback. WBS 2.1 public-fixture evidence remains closed; original-file evidence is not reset to NOT_RECEIVED. PR232/226 and GATE_R0 remain DRAFT/HOLD. No product/source/fixture change, full native suite rerun, writer, merge or release is authorized by this erratum.

