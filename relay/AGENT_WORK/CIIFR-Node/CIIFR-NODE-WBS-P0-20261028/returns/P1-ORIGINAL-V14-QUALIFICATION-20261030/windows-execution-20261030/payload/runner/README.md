# CIIFR-Node WBS 2.2 / P1.2 — full pinned Windows original trial

**Mode:** READ_ONLY. **Product candidate:** XML_Compare_Utilities draft PR #232 at exact commit `d3fbd4041ef4434b4cf5b3c22459f06167be2729`. **Task:** #229, parent #227, reviewer #228. The scripts are qualification helpers, **not** product changes or new engineering authority.

This is an **execution package, not an execution receipt**. A final Windows PASS must come from running it in a truly clean native checkout with the Owner-authorized original file.

## Contents

- `tools/physical-oracle.mjs`: independent ASCII/CRLF V14 physical-card decoder, 15-family pointer custody, process raw-field and typed attachment witnesses. Does *not* import product source/indexer.
- `tools/run-windows-original.mjs`: native Node.js 22+ local static HTTP host, exact-head/clean tracked-checkout and Git blob checks, fresh local Edge/Chrome CDP instance, real Property Transfer TARGET0 file upload, full rendered field/ownership comparison and post-inspection immutability. Uses no npm dependencies or new product writer.

## Execution (Windows PowerShell; local qualified operator only)

1. Use the *authorized existing Windows checkout*. Preserve any working changes. Ensure no tracked dirt; do not force reset or overwrite. If necessary, in a separate clean clone: `git fetch origin pull/232/head` then `git switch --detach d3fbd4041ef4434b4cf5b3c22459f06167be2729`. Check `git rev-parse HEAD` and `git status --porcelain --untracked-files=no` locally.
2. Put the actual original `.CII` **or `.CII.bin`** under an authorized private folder **outside the served repository**. The extension is irrelevant. Do not copy it to `docs/`, browser host root, public Common, or a public fixture folder. Do not normalize CRLF or resave.
3. Use an execution directory outside the product repository; keep the private oracle and raw browser evidence local. In PowerShell, with your actual private paths:

```powershell
$env:PRIVATE_EXPECTED_SHA = (Read-Host 'Private expected SHA-256').Trim()
node .\tools\run-windows-original.mjs `
  --repo 'C:\AUTHORIZED\XML_Compare_Utilities' `
  --original 'C:\AUTHORIZED_PRIVATE\original.CII.bin' `
  --private-dir 'C:\AUTHORIZED_PRIVATE\ciifr-p12-local-ledger' `
  --public-dir 'C:\AUTHORIZED_PRIVATE\ciifr-p12-public-safe' `
  --expected-sha $env:PRIVATE_EXPECTED_SHA
$LASTEXITCODE
Remove-Item Env:\PRIVATE_EXPECTED_SHA
```

Optionally add `--browser 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'`. The runner discovers Edge/Chrome in conventional Windows paths when the argument is omitted. Its local server binds only to `127.0.0.1`, serves **only the pinned checkout**, and does not expose the original (which must reside elsewhere). Node's Chromium CDP must be permitted by local security policy.

## Exact acceptance and file custody

PASS only when all are established in the same native execution:

- Tracked tree HEAD equals the full pinned SHA and is clean before/after; all six sampled HTML/served JS blob identities match HEAD.
- Independent physical original intake identity matches the **privately supplied SHA**, V14/ASCII/CRLF verified, all 15 pointer owner counts reconcile.
- Real HTTP-served `docs/cii-fnr-vnext.html` boots successfully and Property Transfer TARGET0 reads original as file input. SOURCE stays optional.
- Displayed selected **oriented element** includes exact stored T1, P1, fluid density raw lexemes and zero-based half-open byte spans. No engineering-effective semantic promotion.
- Multiple node queries compare every rendered row exactly (including incident element, restraint owner/pointer/slot/type/CNode, rigid element/weight, displacement owner/pointer/spec). Five non-qualified auxiliary diagnostics remain UNKNOWN.
- Property panel has no Apply/Export; browser has zero uncaught page exceptions or external requests. Original bytes rehash identically afterwards.

`--private-dir/oracle.json` and `browser-private.json` contain confidential row identities/spans, diagnostics and private SHA. **Never commit/upload these files.** `--public-dir/sanitized-result.json` intentionally omits the original SHA, raw values, private path, node map and field ledger. Inspect it for unexpected disclosure before a permitted Common relay return. A FAIL or NOT_RUN result is not a reviewer PASS; preserve exact private diagnostic and sanitized code separately.

The earlier WBS 2.1/WH1/WH2 public-fixture qualification is not rerun. No original write/export, property writer, automated node mapping, merge, deployment or release.
