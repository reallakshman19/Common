# CIIFR-Node P1.2 — original V14 isolated Property Transfer module browser qualification

**Scope:** WBS 2.2 / M5 / P1.2; issue [#229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229), parent #227, review #228. SELF_ASSESSED. This is an additional bounded return to the earlier independent physical receipt; it does not revise historical R3 Windows/public-fixture evidence.

**Candidate:** [PR #232](https://github.com/reallakshman19/XML_Compare_Utilities/pull/232), exact remote head `d3fbd4041ef4434b4cf5b3c22459f06167be2729` verified unchanged, base PR226 head `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`. No native Git checkout or tracked-file-clean check was possible: GitHub DNS/HTTPS failed. Product code and branch were not changed.

## Actual execution

1. The protected Owner original was read from the provided attachment as raw bytes, never rewritten. Its measured private file identity matched the authorized expected identity before and after the tests. Private filename, full hash, original path and unredacted witness ledger remain local.
2. The exact five source files used by the read-only module were individually reconstructed from pinned GitHub connector readback and verified by their Git blob hashes:
   - `physical.js`: `a0a5d5e1cf6f9c7e7bf4be51073518a2f85f618f`
   - `property-transfer/cii-index.js`: `93ec1b4339f0301be4104d96c94e126f8c9fa503`
   - `property-transfer/element.js`: `853352955b657853dfa8855eb566c97df67676f0`
   - `property-transfer/node.js`: `35109c593474b191178918d2d6f2a16c6d710571`
   - `property-transfer/panel.js`: `de3f6eb23d067b5d7e0641289059fd31f553f63b`
3. **Native Node actual reader:** `indexCiiV14` accepts the original, returns 521 ELEMENTS, 122 RESTRANT, 156 RIGID, 6 DISPLMNT, 0 FORCMNT, 177 NODENAME and 87 RRMAT material rows; five `PROPERTY_AUX_CONTENT_UNQUALIFIED` warnings (BEND, ALLOWBLS, SIF&TEES, NODENAME, REDUCERS). Its output is compared to the independently derived private physical audit, not used to create the oracle.
4. **Actual Linux Chromium 144 isolated DOM host:** 20/20 focused Boolean assertions PASS. Browser read the same original through the real `[data-pt-file=target]` file-input handler, without SOURCE, and displayed matching file identity/element count, five UNKNOWN warnings, exact first oriented element, T1/P1/density lexemes with zero-based half-open byte spans, shared-node incidents, restraint owner/pointer/slot/type/CNode, RIGID owner/pointer/weight, and DISPLMNT owner/pointer/specification. It correctly kept unrelated node attachments separate. No Property Apply/Export control or page exception observed. The private original's post-run digest remained unchanged.

## Environment adaptation and limits

**This is NOT the full pinned served application browser gate.** The sandbox Chromium rejects all navigation, including localhost and file:// (`ERR_BLOCKED_BY_ADMINISTRATOR`), and external GitHub DNS prevents native checkout. To test actual browser DOM behavior, Playwright used `page.set_content` with a minimal Property Transfer DOM host, and concatenated the Git-blob-verified module bodies after stripping only ES import/export declarations. Browser file-input processing, indexed records, panel event handlers, and DOM rendering are product logic, but the application shell, browser-native HTTP-served modules, Normal/Nodal tabs and exact deployed host were not tested.

Because the resulting about:blank context lacks `crypto.subtle`, a host-only SHA-256 bridge computed actual input bytes using Python `hashlib.sha256` and returned the digest to the unchanged panel logic. This is not a native browser WebCrypto hash PASS; only the displayed digest comparison and input immutability were tested.

Private witness content, byte spans, confidential node IDs, original bytes, unredacted screenshot and full private logs are excluded from Common. No engineering effective-value, CNode semantics, pressure case, support direction, force-vector or process-transfer claim.

**Disposition:** Original physical receipt PASS; exact source-verified reader ORIGINAL_INTAKE PASS; isolated Chromium module/browser display 20/20 PASS (SELF_ASSESSED, bounded); actual native Windows clean checkout + fully served PR232 application/browser original trial NOT_RUN. **WBS 2.2 PARTIAL/HOLD**, PR232/226 and GATE_R0 DRAFT/HOLD. No product edit, property write, TARGET1, automatic correspondence, merge, deployment or release.

**EXACT_NEXT_ACTION:** An authorized Windows local operator with exact PR232 checkout (HEAD/cleanliness verified) must serve the original pinned full HTML application, load the same privately authorized original in Property Transfer TARGET0, check corresponding displayed values/attachments and five UNKNOWN warnings against the protected physical ledger, capture exact browser result, verify original hash unchanged, return sanitized native evidence for non-author reconciliation.
