# TAB3-O1-W08 — lifecycle / source cancellation / source-kind (chat 6acc9596)

Outcome: O1
For the user: In DRAFT PR #228, rapidly switching JSON originals A→B→C no longer permits an older upload to overwrite the last selection. Changing source XML/configuration revokes old trace and CSV controls immediately, not merely when a stale export is clicked. No released app change.
Proof: [initial failing six-case real Chromium #38229853338](https://github.com/reallakshman19/3D_Converters/actions/runs/38229853338); [bounded correction first positive #38230366026](https://github.com/reallakshman19/3D_Converters/actions/runs/38230366026); [current exact-head rerun #38230735758](https://github.com/reallakshman19/3D_Converters/actions/runs/38230735758).

## Mandate and owner bounds
AIM v2.2.0 O1 label_sha 5f9065d, approved <=104857600 original bytes AND <=2000000 original occurrences inclusive; beyond either typed zero trace/CSV rights. R7 workpack on [#226 comment 6120751655](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6120751655), owner-directed W09 before W08 [sequence comment 6121246944](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6121246944). Inherited W07 W09 DONE; this is W08 only.

## Exact first before-head discriminator (real authored standalone Chromium)
Initial test-only exact head dbef2a410dda04c1e69c2c0024ef4090fbab6720 at [run 38229853338](https://github.com/reallakshman19/3D_Converters/actions/runs/38229853338):
- **race FAIL:** A original Firstpass JSON index commits at SHA 6b2c8b01ab0b. Quickly upload B (SHA ac8df0c650a9) then final C (SHA cb29583979fb), while deliberately delaying the IndexedDB delete success callback (without disabling the real delete). App showed LFJ_SOURCE_SUPERSEDED instead of committed last-user C; no stale CSV actually downloaded. This independently reproduces the old-scan installs-after-new-scan hypothesis.
- **config FAIL:** start with protected original 216+241 Worker trace and two CSV controls; change authored resolver join-mode; old controls remain visible (2) although clicking produces typed O1_EXPORT_SOURCE_STALE and no download.
- **xml FAIL:** start with same protected positive, replace authored XML source; old CSV controls still visible (2) until clicked, then typed O1_EXPORT_SOURCE_STALE blocks download.
- **inflight PASS:** replace staged JSON during domain Build; previous/old export controls absent, zero download rights.
- **scope LIMITED:** original Firstpass UI renders disabled resolver-hierarchy-scope select with single `__ALL__` choice, All scopes (0), thus **no executable positive scope switch** with this protected original, not a proven branch selection oracle; do not invent a positive.
- **nc-kind first PROBE MALFORMED:** authentic NC JSON SHA 89f9c2ab7a9f..., 328156 original occurrences COMMITTED as **source-only** under PSI116; after changing original XML to deliberately incompatible InputXML, authored JSON Trace phase is actually DISABLED (correct product denial). Initial test improperly tried clicking disabled phase and later awaited non-existent O1 status; test was corrected to assert disabled phase and zero O1 Worker domain/export rights. A *genuinely compatible* protected NC XML pair is NOT_PROVEN, not fabricated.

## Narrow O1 adapter correction
In `tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-lfj-o1-intake.js`: monotonic `requestSeq` assigned synchronously at every scan/user change. After asynchronous IndexedDB revoke/cleanup, a superseded scan must exit without installing an older Worker. Superseded errors must never overwrite the latest generation's status. Source/XML source-kind changes invalidate source generation and old domain/CSV rights immediately. Config/branch/scope changes revoke old domain/CSV controls synchronously during real captured UI change, ahead of legacy state mutation, while retaining valid JSON source for rebuild. No change to old foreground parsing, source Worker tokenizer/caps, independent XML-domain semantics, CSV exporter, O2/O3 or C05.

[Corrected run #38230366026](https://github.com/reallakshman19/3D_Converters/actions/runs/38230366026): **race PASS** last C SHA cb29583979fb COMMITTED and domain matched 241 original paths; **XML PASS** two previously visible controls removed and zero CSV downloaded; **config PASS** stale controls removed and zero CSV downloaded; **inflight PASS**. The NC test has been corrected to treat actual disabled JSON Trace as a safe negative, not an unrelated UI timeout. Final exact-head source SHA fb1d354ceac76e4c8c2dcdc478dd498ea6e9cdeb and [rerun 38230735758](https://github.com/reallakshman19/3D_Converters/actions/runs/38230735758) are pending terminal proof at this writing.

## Qualification limits / stop
- Original Firstpass + explicit incompatible InputXML proves negative source-kind denial, *not* compatible NC XML matching. Original NC JSON is authentically sourced, not a verified compatible paired XML.
- There is no enabled authored scope selector in the protected Firstpass pair (All scopes (0)); active user branch/scope mutation with a real protected multibranch fixture remains NOT_PROVEN.
- No release, no overall O1 acceptance, no broad C05/Weight CI waiver. Retain zero stale downloads even when controls were wrongly visible before the fix.
