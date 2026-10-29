# CIIFR-Node — exact Windows qualification checks, R3 continuation

Prepared 29 October 2026 (+04:00). Task: [#229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229), related review #228 and WBS #227. Recipient: existing local Windows qualification agent `01429edb`. Producer: current Owner-directed contributor, chat ID UNKNOWN; producer authored product PR232 repairs and this R3 harness correction. This is a prepared runnable continuation, not independent approval or an observed agent dispatch.

Product candidate remains `d3fbd4041ef4434b4cf5b3c22459f06167be2729` (draft PR232); parent PR226 remains `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`. No product file, product test, writer, deployment or Page data is changed by this package.

## What was verified and what changed

The receiver retrieved all 14 members plus the manifest of local agent R2 return Common `dffe98513ddb938426e2a0068ee97a411280bf8e`. Every member byte length, SHA-256 and Git blob matches. The two fixtures are now the actual canonical 8,276-byte CRLF blobs. Manifest identity is 3,543 bytes, SHA-256 `32b6ec3ed86c369dfb819f0398ae178c6d6e6b9e251e1bffda04e92f82401f78`. **WH1 byte-transfer finding is CLOSED for R2.** `evidence/r2-return-readback.json` preserves the measurements. Four UTF-16LE-with-BOM TAP logs were verified by reversing the connector transcode and matching both Git blob and declared SHA-256, not by normalizing uploaded evidence.

R2 added meaningful decision comparisons, active-delay preconditions, challenge enforcement and final page/console-error checks. The receiver independently reproduced rejection by its extracted Case 5/6 blocks. R2's 13 reported HTTP module identities match the receiver's previously pinned source snapshot; `evidence/r2-served-source-readback.json` contains that comparison. This is evidence reconciliation, not a fresh receiver Windows/browser run.

One part of WH2 remained: R2's element-column and attachment-column checks use substring matching. Its actual guards accept pressure `130` where `30` is required and `Pointer 10` where `Pointer 1` is required. Its output field-number objects also contain literal expected constants. `payload/receiver-probes-r2-r3.mjs` proves the two actual R2 guard false positives and their rejection by R3; `evidence/receiver-probes.json` records the result. These are harness findings, not newly demonstrated product defects. The historical R1, receiver review and R2 artifacts remain immutable.

R3 replaces these guards with complete cell comparisons to independently decoded physical raw tokens and byte spans. It checks the exact oriented element title/ordinal/endpoints, field identities, branch, qualification, incident rows and every attachment owner/pointer/slot/specification/type/CNode/rigid weight. It rejects missing or duplicated records. Reported field numbers and raw witnesses now come from the observed cells after validation. `physical_oracle.py` uses only Python standard-library byte/decimal operations on the canonical public SOURCE, imports no product reader and generates `physical-oracle.json`. This oracle covers stored public synthetic fields and record ownership; it does not qualify units, effective process values, displacement/force vector semantics, vendor legality or automatic correspondence.

R3 also makes the existing runner portable with explicit candidate/evidence paths, checks Git HEAD and every selected served disk blob against the pinned Git tree, and gives each browser a fresh profile. The existing 13 critical-module list is preserved; this is not a claim that every transitive dependency has been enumerated. The Case 1 demo preconditions are asserted explicitly. R2's other strengthened browser checks remain in the runner.

The new exact guards passed **23/23 native tests**, including positive physical witnesses and contrary substring/ownership/address/cardinality cases. They also pass against the actual pinned product panel loaded in its native controlled DOM, checking both real rendered element rows, their physical spans, the reverse selection and all node500 incident/attachment rows (`evidence/panel-integration.json`). This confirms compatibility with the actual panel output without calling the product reader to generate the physical oracle. `node --check` and `--help` pass for the prepared R3 runner. **R3 Windows/Edge/Chrome execution: NOT_RUN by this producer.** R2's recorded Edge/Chrome observations remain evidence on the unchanged product candidate, but do not count as execution of R3. Existing native suites remain required 17/17, repair 13/13, Geometry 9/9 and full-suite 123 PASS/1 FAIL, historical FAIL unchanged; no rerun is needed for this harness/package correction alone.

The fixture-local `.gitattributes` protects the public CII bytes. The new R2 repository-root `*.cii binary` addition is broader than this task; the continuation restores that root file's exact pre-R2 blob while retaining R2/R3 fixture-local protection. No fixture is rewritten and no repository-wide normalization is performed.

## Local continuation

Use the existing Windows host and checkout. Retrieve this exact package commit and verify `ARTIFACT_MANIFEST.json`; preserve byte settings (`core.autocrlf false`) for this clone. Run from the package directory:

```powershell
node .\payload\verify_pack.mjs
node --test --test-reporter=tap .\payload\qualification-guards.test.mjs
```

The supplied package includes the canonical fixtures and measured physical oracle. To inspect/regenerate the independent expectations, run `python .\payload\physical_oracle.py .\payload\fixtures\SYNTH_V14_SOURCE.cii`; compare the resulting JSON values with `physical-oracle.json`. Avoid PowerShell 5.1 default text redirection when creating an exact UTF-8 replacement; no regeneration is required for the checked package.

Serve the pinned product checkout from a separate terminal:

```powershell
py -3 -m http.server 8765 --bind 127.0.0.1 --directory "C:\path\to\pinned-product-checkout"
```

Run the prepared browser continuation, supplying an evidence directory outside the product checkout. Replace these example paths with the actual authorized local paths:

```powershell
node .\payload\run_qualification_browser.mjs --candidate-dir "C:\path\to\pinned-product-checkout" --evidence-dir "C:\path\to\private-evidence-r3"
```

Installed standard Edge/Chrome paths are defaults; `--edge-path` and `--chrome-path` override them. An existing port8765 server is usable only if the runner's source/tree comparisons pass; do not stop unrelated processes. Browser profiles/screenshots remain in the selected private evidence directory. Use only public fixtures for this rehearsal. Keep the original model out of the NodeName writer and do not use this harness on protected input.

The runner writes `browser_qualification_report.json` with exact observed raw fields and ownership rows, fresh source witnesses and the candidate identity. Preserve its raw process output/exit result locally, including any failure. Publish only the sanitized report/logs through this task's Common relay; measure the actual committed bytes and read them back. Do not replace previous historical returns. The complete native product suites need not be repeated unless product bytes or a newly exposed behavior changes.

## Stop condition and next actor

**Next actor/action:** local qualification agent `01429edb` verifies this package and executes the prepared R3 browser continuation on the same pinned product head, then returns measured results on #229. No new local execution is claimed by publishing this package.

WBS 2.1 remains PARTIAL pending this bounded observation. WBS 2.2 remains ORIGINAL NOT_RECEIVED/NOT_RUN; an authorized private original read-only trial may proceed independently when actual custody is supplied. PR232/226 and GATE_R0 remain DRAFT/HOLD. There is no merge, property-writing, P2, deployment or release promotion. The root producer's harness edit must not be represented as independent acceptance of its own product repair.
