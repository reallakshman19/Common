# G1 exact-head Oracle execution — 25 October 2026
Claim scope: read-only native reproduction and bounded browser-runner diagnosis. SELF_ASSESSED; not an independent G1 verdict, Owner acceptance or merge.
Candidate: PR174 9936d4078fb7f837ffe6f46805241efdb7bbc0e8.
Base: XCU main c823f0c0edbeb315c07fa2911390dc781968146f.
Both native checkouts remain product-clean. Node v24.22.1 / Python3.12.14.

## Actual inputs
S1.CII 108330 bytes SHA256 9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b
T.CII 2866002 bytes SHA256 abfa3ffc9281fe75d4170b2d885d554cb1f120dadedae7c7ab609548b63cc060
Measured again from candidate Benchmark bytes using sha256sum.

## Executed here
- Candidate: node --test tests/cii-fnr-vnext-g1-geometry.test.mjs = PASS5/5, exit0. Actual original input identity, physical-node/element-only exception, complete exports and signed discrepancy, common scale, authored/served mirror and writer separation.
- Candidate: node --test tests/cii-fnr-vnext-csv-resolver.test.mjs = PASS8/8, exit0. Includes controlled DOM mock; not a served browser claim.
- Candidate: node --test tests/cii-fnr-vnext-branch-scope.test.mjs =18PASS/1FAIL, exit1.
- Base main: same branch-scope command =18PASS/1FAIL, exit1, same test/line81 and observed1 vs expected0. An initial main sparse-checkout lacked docs mirror and produced an extra ENOENT; adding the actual tracked docs restored coverage, then the comparison above was executed.
- No diff between base/candidate Normal modules, shared physical parser or branch-scope test. The existing assertion remains open; this reproduction establishes inheritance, not a waiver or an engineering root-cause verdict.
- Earlier original shared parseCii and Method C observations remain at #175 comment6401364122: both raw originals accepted by actual shared parser; 4060 segment-only and4970 signed discrepancy reproduced. Those observations are module execution, not the real file-picker journey.

## Browser route: attempted, NOT_RUN
The shipped Playwright shell wrapper has CRLF and fails bash pipefail; its exact npx command works directly. @playwright/cli installed and help executes.
Standard installed Playwright browser installer initially failed because /tmp is absent. With a writable task TMPDIR, download ran but all built-in retries returned truncated/non-ZIP payloads.
A materially different npm package route @sparticuz/chromium153.0.0 supplied Chromium153.0.8010.0. Assets were decompressed in the writable task directory; --version succeeds.
Actual Playwright CLI launch with isolated configuration exited SIGTRAP before a page. Direct Chromium headless about:blank and local application launches also exit-5/SIGTRAP with empty stderr, including one bounded logging diagnostic. No browser page was opened and no application behavior is inferred from these failures.
Real served B1–B4, keyboard interaction, pan/zoom, actual downloads, original intake and stale-file race remain NOT_RUN on this host. No set_content, fake SHA or Method C substitution was used.
Existing G1/path-filtered workflows have no workflow_dispatch route for this exact journey; no workflow was modified or deployment attempted.

## Continuing outcome
No product repair is justified by runner launch failure. WBS3.1 XML adapter implementation proceeds disjointly under XCU#180 and Common IMPLEMENTATION_R3.md. That prototype must preserve this browser limitation and has no Writer/Apply authority.
Next G1 action: execute B1–B4 on a functioning supported browser host against this exact candidate, then obtain the separately required independent assessment. XML preview/module work continues now.
