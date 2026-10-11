SOURCE AUDIT — C05 exact integrated HEAD, 2026-10-11
Reconcile ID: R-212-01; task 212-T2; raw 3D_Converters PR #211 HEAD e7be6e26099ebef482dd89dd12898d3661bd6405.
Source authority: 34 PR workflows 19 SUCCESS, 15 FAILURE. Examined failing job identities, failed steps and actual logs at this exact SHA; table below is diagnosis, not acceptance waiver. Each run URL = https://github.com/reallakshman19/3D_Converters/actions/runs/<run>.
ISSUE | CI RUN | OBSERVED FAILURE (exact head) | DISPOSITION / NEXT SOURCE CHECK
#835 | 38101542960 | evidence-only workflow scans wide integration diff and rejects legitimate LFJ #208 source/scope files; disallowed includes tabs and docs scope modules | QUALIFICATION-SCOPE; owner must decide applicability vs protected narrow-leaf scope; not runtime defect.
#836 | 38101543005 | predecessor test expects Mat_Map/Weight revision undefined although now 2, and stale piping-class cold restart promises rejection not observed | HISTORICAL PREDECESSOR + RESTORE SEMANTICS OPEN; assess currently isolated per-master restore source and original rev guard.
#837 | 38101542841 | predecessor test assumes future Weight revision missing (now 5); Mat_Map cold stale metadata Missing expected rejection | HISTORICAL PREDECESSOR + RESTORE SEMANTICS OPEN.
#855 | 38101542920 | explicitly RED baseline expects weight datasetRevision null/undefined but current result is 5 | BASELINE-EXPECTS-BUG; owner/qualification scope must not force product regression.
#856 | 38101542840 | deliberately RED prerequisite expects Weight datasetRevision undefined but current result 5 | HISTORICAL PREDECESSOR expected RED; verify current behavior rather than reducing custody.
#857 | 38101542821 | stale positive Weight restart revision expected rejection; none thrown | COLD RESTORE STALE-REVISION CONTRACT OPEN; real source guard/evidence versus isolated failure semantics.
#860 | 38101542885 | aggregate Valve Weight suite fails included stale Weight restart test #857 | AGGREGATE dependent; distinguish independent C04 assertions and actual Weight authority.
#871 | 38101542887 | IndexedDB persistence reject expected to reject whole import, current does not; corrupt restore similarly no top-level reject | FAILURE ISOLATION CONTRACT OPEN; current status receipt and sibling isolation must be checked.
#875 | 38101542940 | 52/53 tests pass; cache retry-generation chain asserts old literal 20261006-c05-5-5-persistence-retry-1 on tab entry | CACHE-GENERATION CONTRACT OPEN; tab current imports 20261008-p0-mode-b-parity-1; avoid blind rewinding versions.
#880 | 38101542873 | 3/3 old RED corrupt restore tests expected global rejection, current does not | HISTORICAL NEGATIVE BASELINE VS current per-master isolation; independently verify no silently accepted corrupt data.
#884 | 38101542870 | qualification-only scope compares wide integrated ancestry and fails at Verify qualification-only child scope; prints unrelated files | QUALIFICATION-APPLICABILITY; not application runtime pass, requires owner disposition.
#893 | 38101542898 | original C05 consumer test expects materializeRows(pipingClass, pc-cold-r7, revision7) and 2 full rows without branch samples; current bounded path queries none; also tab.js cache-version literal assertion; native browser expects 10699 resident Regex rows, actual bounded count | CONTRACT CONFLICT; preserve full-master general consumers, choose bounded Regex source mode via D-212-2, verify per-consumer expected semantics.
#894 | 38101542874 | scale Node suite inherits 2 failing #893 old consumer and cache-generation assertions; native scale-browser job PASS | AGGREGATE; not a fresh 100k scale failure.
#895 | 38101542856 | combined browser fails #893 Regex row count, Node inherits #893 two assertions; protected C05 scale browser PASS | AGGREGATE C05 consumer contract conflict.
#841 | 38101542868 | current C05 Node inherits #893 2, browser inherits #893; worker-line-list additionally matches historical #776 Match-1 literal expression /withXmlCiiRigidWeightMatch1(clean,candidates,proposalMeta)/ against changed code | MIXED AGGREGATE C05+Weight explicit predecessor shape; verify behavior, do not satisfy by superficial string substitution.

SOURCE CALL SITES (all from raw head)
- tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-regex-smart-evidence.js: materializeRegexSmartMasterContext builds sample-bucket bounded query; zero branchSamples => zero queries, not whole table; evidenceSummary marks truncation incomplete.
- tabs/xml-cii-2019-standalone/xml-cii-regex-bounded-evidence.js: resolves source-bound Worker search/index rows and census with non-optional provider guards on returned indexed rows.
- tests/xml-cii-issue-893-consumer-authority.test.mjs:197..222 expects legacy materializeRows and full row count; lines 251..285 assert all historical JS source cache query tags equal old literal.
- tabs/xml-cii-2019-standalone-tab.js top import explicitly uses ?v=20261008-p0-mode-b-parity-1, not 20261007-c05-6-2-consumer-authority-1 or 20261006-c05-5-5-persistence-retry-1.
- tests/xml-cii-issue-875-persistence-status-retry.test.mjs:514.. end asserts older generation substring in every entry in wide path list.
- docs/ parity and public registered Pages remain different questions; current staged Chromium green does not certify public deployment.

REMAINING DECISIONS / NO WAIVER
D-212-2 OPEN: owner independently chooses per-consumer C05 source authority and test applicability; do not rewrite #893 protected goldens or force 10699 rows into bounded Regex preview.
D-212-7 OPEN: exact stale revision behavior for cold IDB restore: whether rejection must be thrown globally or failure status recorded per isolated master; verify corrupted master never promoted and healthy siblings remain usable.
D-212-8 OPEN: qualification-only workflows #835/#884 applicability on integrated descendant PR versus owner narrow leaf; no auto-waiver.
Acceptance AC03: 15-red explained to test-log level but NOT RESOLVED; 0 formal release gates accepted. Continue T3 and T4 independent of these decisions.
