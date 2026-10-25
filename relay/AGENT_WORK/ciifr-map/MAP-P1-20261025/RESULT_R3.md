# CIIFR-MAP-P1 R3 — prototype result relay
Task: [XCU #180](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180).
Canonical parent: #166; reconciliation #179; WBS3.1 / G1 / M13.
From: task-local map_p1_builder (Chat ID UNKNOWN). To: Owner-appointed Oracle (Chat ID UNKNOWN).
Authority: IMPLEMENTATION_R3.md at Common2627ff590ba26faf4329427ca4bde36177a233ae; receiver4800bytes SHA256f73be4c0c805e87f6877705f083063bc80d9be21ed3e686368dec6f33fdddbf5.
Coordination: standalone native task; no new Cycle, no replacement of G1 coder6addafaa.

## Prototype return
User can run the isolated XML Geometry Preview, upload TWO EXISTING supported XML files, add/remove manual node anchors, run unchanged Method C, inspect a metric overlay with linked node/element/field evidence and download current SVG/JSON/CSV.
Not integrated VNext; no converter input/control, legacy matcher, topology matcher, field transfer, Writer/Apply, CII output, merge or deployment.

- Draft product PR: https://github.com/reallakshman19/XML_Compare_Utilities/pull/181
- Exact published head: 683a1ac37b5e4457b3e67753cec1c951ec1a2dc9
- Branch: codex/ciifr-map-xml-overlay-p1-20261025
- Base: main c823f0c0edbeb315c07fa2911390dc781968146f
- Tree: 964218af596d52925654b45d9dc1e37f96314bdf
- Local tested source checkpoint:851c900ee1988a9ac7cc491bf89a6ae7c4501773, identical tree.
- Shell git push lacked credentials. Authorized GitHub connector published all21 exact blobs/tree/commit; commit metadata differs, every file byte is identical.
- Scope:21 added files,0 deletions:20 under prototypes/ciifr-map/ and agents/WIP-CIIFR-MAP-P1_workreport.md. No shared/G1/converter/writer/workflow/Page or operational-backup file in PR.

## Run and try
From repository root: `python3 prototypes/ciifr-map/server.py`.
Windows: double-click `prototypes\\ciifr-map\\Start-MAP.cmd`.
URL: http://127.0.0.1:8873/prototypes/ciifr-map/ (use --port to change; --no-browser supported).
1. SOURCE: prototypes/ciifr-map/tests/fixtures/S1-F05.xml.
2. TARGET: prototypes/ciifr-map/tests/fixtures/S1-R4.xml.
3. Add3790->3790; run and inspect one-anchor orientation warning.
4. Add3830->3830 and3840->3840; run. This same-original parity pair yields57/57 nearby endpoint nodes and proper scale1/det+1 numerical fit.
5. Inspect row/node/element witnesses, projection/zoom/pan and current exports. Change any file/anchor/parameter; stale evidence/export is revoked.

The supplied pair is PUBLIC_ORIGINAL_DERIVED_XML, the same public S1 original through two unchanged pinned converters. It demonstrates cross-profile geometry parity, not independently accepted physical mapping. No Owner/private pair supplied.

## Actual source and distribution receipt
Original public S1.CII108330bytes SHA2569a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b.
F05 source:a67487023bcafc13d68b62dbfc9bb74c61b3c64c. R4 source:9da244e7670a21d963def16543679a6d983d5ba7.
R4 frozen engine/profile independently matched b2bb8ed87440e46f72833424cacd82e6605c47f372f146deec749ad2bb0ee264 and8d2c2123bce98a387d00a3aeca69c8e5dea6b3831e29f65e7760f6a5694204b2.

| Committed fixture | Bytes | SHA256 | Git blob |
|---|---:|---|---|
| S1-F05.xml |882735|1154c980d08344b1f803cda3bd9884b169753148b150641a745c9bfcb15de995|914303e2437fffaa5682757ee32b3ae3d8f37df8|
| S1-R4.xml |1426775|a332dd7b2551faae51de3c016941762c3b795cdf19073b373817354e309526e6|2da10efac2d2f040000edd988d4a1e0baae5dbe1|

After publication, builder retrieved BOTH actual GitHub blobs through fetch_blob and compared their entire ASCII byte strings with measured committed payloads: exact equality and measured lengths PASS. This is actual distribution readback, not reliance on manifest alone. Oracle receipt/retrieval of this result remains NOT_RUN until Oracle actually reads it.

## Executed checks
Builder/self, contributor-exposed; no independent engineering acceptance:
- `CIIFR_TEST_RUNTIME=/workspace/scratch/ca71d2f89cf7/map-test-runtime node --test prototypes/ciifr-map/tests/adapter.test.mjs prototypes/ciifr-map/tests/geometry.test.mjs`:12/12 PASS, exit0. Actual test-only @xmldom/xmldom0.9.12 DOMParser; product uses native browser DOMParser.
- Full public XML bytes -> profile -> signed graph -> existing registerMethodC/findMethodCCandidates/methodCSvgScene/export chain passed.
- Source-bound sign challenge: change S1 3830->3840 Y from-1500 to+1500 while keeping embedded original-CII SHA. XML SHA changes and geometry moves3000mm Y; original CII claim stays CLAIMED_NOT_REVERIFIED.
- Delayed arrayBuffer reservation and late stale failure, delayed digest completion, one/two/degenerate/duplicate/cross-component anchors, reversed endpoints, cycle/seed contradictions, unsupported/malformed/DTD/entities/units/counts, known independent90degree rigid transform, ambiguity/collision and segment-only point passed.
- Retained unchanged Method C registration/rigid-fit/candidates/SVG suites45/45 PASS, exit0, including actual public S1/T. Exact HEAD tests and required docs mirror bytes materialized in ignored local mirror because checkout is sparse; no expectations/production files changed.
- `python3 prototypes/ciifr-map/tests/http_smoke.py`:PASS, exit0. Actual launcher subprocess HTML200 and18 imported ES modules200 with MIME. JS/Python syntax, new-JS<300lines, six shared-source byte comparisons and diff --check PASS.

## Honest limits and recovery
Actual served-browser uploads/keyboard/pan/zoom/downloads and Windows interaction: NOT_RUN. Oracle's real Chromium exits-5/SIGTRAP before any page. HTTP/native XML tests do not replace browser interaction. Owner trial and independent review pending.
Supported exact F05/R4 native-mm geometry profiles only;32MiB input and5million pair-work limits; seedless components relative; XML SHA measured independently, embedded CII claims unverified. Full XML engineering/writer validation is not claimed. R4 public T FORCMNT coverage remains a separate converter gap.
Required local ledger:.agent-worklogs/20261025_2230_ciifr-map-p1/, absent-file baseline, module no-index patches/final SHA inventory. Native backups1-15 retained locally. First correction of newly created task files missed pre-edit backup; explicitly disclosed, no retroactive claim. Safe baseline undo remains checksum-verified deletion of only task-created files. Tracked .backups/log.json tool-side-effect is preserved locally and excluded from PR.

## Next consumer and exact next action
WBS3.2/G2/M14 consumes the serializable XML graphs and correspondence ledger in CIIFR.XmlGeometryPreview.v1 for pose-free topology and Manual/Topology/OR/AND. None is implemented here. Later element/endpoint/field transfer remains deferred.
EXACT_NEXT_ACTION: Oracle read this exact relay and PR181 head, reconcile the bounded XML amendment, and arrange real Owner browser trial on a working browser. No merge/deploy authority.

RECEIPT_STATE=RESULT_REGISTERED;ORACLE_RECEIVER_RETRIEVAL_NOT_RUN
