SOURCE RECONCILIATION R-212-02 — LFJ to engineering authority bridge (design only)
Date 2026-10-11 | task 212-T4 PARTIAL | candidate authority 3D_Converters #211@e7be6e26099ebef482dd89dd12898d3661bd6405
Owner ACs AC-01,AC-02,AC-04,AC-05,AC-06,AC-07,AC-08. This is NOT a production adapter or Owner approval.

EXISTING EXACT SOURCE CONTRACTS
1 tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-events.js:339..457: actual indexed Build consumes original stagedJsonFile Blob, current XML, selectedScopeId and optional source-discovery SHA, produces verified preview and createIndexedExportReceipt into state; neither is passed to final workflow job.
2 tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-lfj-indexed-preview.js:82..159: return verified source-only status SOURCE_PINNED_PREVIEW_ONLY, engineeringReady:false, downloadAuthorized:false, originalSha256, xmlSha256, selectedScopeId/selectionDigestSha256, nodeWiseRows, evidenceTreeRows and CSV digests. Matching Worker handoff checks source/projection HEADs, but exported display rows are not a full physical FactRecord interface.
3 tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-lfj-indexed-export.js:57..152: CSV receipt verifies hashes, revision, source Blob, selection and consent; this is local CSV authorization only, always downstreamEngineeringAuthorized:false.
4 tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-run-workflow.js:259..285: constructs the actual job from current state after readiness and weight review.
5 tabs/xml-cii-2019-standalone/xml-cii-workflow-ui-adapter.js:108..131: rereads sourceFile+stagedJsonFile and constructs branchScope and separate job, not yet cross-checked against LFJ verified ledger and selected original owner/zone. This is the missing authoritative handoff.
6 tabs/xml-cii-2019-standalone/xml-cii-output-run-readiness.js:68..76: legacy resolver existence is warning only, not a source-basis blocking gate. Unscoped legacy remains a distinct compatibility mode.
7 lfj/qualification/experiments/consumer-sparse-b0-xml-match/xml-research-handoff-budget.mjs: 8MiB total inline original handoff budget. Don't add new unbounded full corpus object to preview UI.

PROPOSED LFJ.EngineeringSourceBasis.v1 (not implemented; no promotion of Worker flags)
fields:
schema/version, originalJsonSha256, originalXmlSha256, originalSourceBlobRef (ephemeral, not serialized), originalJsonByteCount, selectedScopeId (explicit ALL or verified selected ID), selectionDigestSha256 (required for non-ALL), branchSelectionManifestDigest, xmlLedgerCount, matchedXmlLedgerCount, nodeWiseCsvSha256, evidenceTreeCsvSha256, sourceMappingRevision, datasetRefs with keys+revision+fingerprints, fullLedgerHead/durableQueryReceipt, sourceOccurrenceId/sourcePath/branchScope per resolved FactRecord, runtimeGeneration and current UI revision, snapshotDigest and approvalEpochs for Preview/Weight/Material, transient engineeringReady:false until separate acceptance.
DO NOT infer unique source identity from NodeNumber or displayed CSV row text; repeated -1 and aliases require source occurrence/path identity.

ADMISSION CONTRACT
A original Blob SHA, XML SHA, file object/custody, verified non-ALL scope manifest and branch scope match current state and Worker receipts.
B selected JSON and XML occurrence census exactly matches frozen ledger; no omitted/duplicate source original rows.
C full-source facts are available through bounded/paged source-backed queries: do not build Owner 30MiB FactRecord basis by transporting arbitrary 8MiB inline research handoff.
D source datasetRefs verified for id, masterKey, revision and fingerprint independently at every downstream read. No silent fallback to resident or ALL when selection unsupported.
E separate downstream materialization must retain source occurrence ID, path, branch, original POS/PS and evidence lineage. Suggestions != approved facts.
F on source/scope/config/master/review revision mismatch: revoke Preview, both Weight snapshots, Material approval, final Run/Download. Reject before any CII commit.
G current LFJ source-only receipt remains sourceOnly:true / engineeringReady:false / downloadAuthorized:false. An explicit product adapter/attestor must return a *new* versioned accepted engineering basis, never mutate or reinterpret the old receipt.
H legacy XML/JSON mode remains distinguishable and must never be silently routed through LFJ if not selected. Maintain existing InputXML semantics separately.

FAILING NEGATIVE TESTS TO ADD BEFORE T4 EXIT
N1 two authentic selected owner IDs swapped same-length -> reject incorrect source, no ALL fallback.
N2 same XML display node/NodeNumber=-1 but different original occurrence/path -> reject correlation.
N3 Worker original SHA mismatch and stale file object -> no engineering basis.
N4 selected non-ALL missing manifest or wrong selection digest -> fail closed.
N5 changed config/master revision or old IndexedDB generation -> no Preview/Run.
N6 missing/torn paged rows or duplicate ledger occurrence -> refuse completeness.
N7 source-only research handoff falsely presented as engineering-ready -> refuse.
N8 tampered CSV hashes or unsupported 8MiB transfer -> refuse.
N9 actual File upload/Build/Preview/Run: same selected zone, no fresh unverified re-read granting authority.
N10 clear/mode switch/abort/cold reload -> invalidate all downstream approvals and exported outputs.

NEXT IMPLEMENTATION SKETCH
- Define pure adapter validation in tabs/xml-cii-2019-standalone/integration/ (B4 #136 writer consent), tests/recovery-final-cii.
- Add versioned FactSnapshot with exact original paths/occurrence IDs, not CSV strings. Prefer paging existing matching Worker indexed source projection over new geometry algorithm.
- Make buildXmlCiiWorkflowJobFromUiState accept a validated basis and explicitly reject source drift in LFJ mode; adjust output readiness, preserves legacy branch.
- Browser Firstpass vertical slice: original File + XML -> owner-selected Build (216/164, evidence241) -> full FactRecord basis -> 4 Preview and fail-closed Run conditions; initially no B2–B4 approval.
- No production release or full acceptance until Owner 30MiB, #141, C05 and Mode A/B final golden separately green.

STATE: PARTIAL DESIGN; no code or new negative test executed. T4 remains OPEN.
