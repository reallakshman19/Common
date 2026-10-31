# TOPO-B-B2 — Cycle brief (31 Oct 2026)

**You are the TOPO-B writer.** The Oracle (a Claude Code session) checks every return before the Owner sees it. Report only in [issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239).

## Owner intent
Offload format interoperability to one agent. **Reuse** the XML_Compare_Utilities InputXML Workspace and the existing parsers; never re-implement them. Admission is read-only and fail-closed. An unsupported file must never look like a successful "0 errors" model.

Spec: [TOPO-B concept spec R1](https://github.com/reallakshman19/progress-page/blob/main/docs/TOPO_B_UNIVERSAL_XML_TOPOLOGY_CONCEPT_SPEC_R1.md), sections 2–4.

## What exists (checkpoint)
- Draft [PR #240](https://github.com/reallakshman19/XML_Compare_Utilities/pull/240) at head `a3ad4dd3`, with two new files:
  - `prototypes/ciifr-map/xml-format-admission.js` exports `admitXmlBytes` and a text entry point. It admits only F05 RichInputXML-P1.v1.1 and R4 RichInputXMLv2.1, through the existing `extractXmlProfile` and `buildXmlGraph`. Everything else (GLRD, PSI116, InputXML, unknown roots) returns `UNSUPPORTED_INPUT`; DTD, malformed input and wrong units, counts, dialects or profiles return `INVALID`. The digest is taken from the real bytes, and a BOM is recorded.
  - `prototypes/ciifr-map/tests/format-admission.test.mjs`.
- Independent review passed at 93/100. The reviewer independently checked F05 element 1: 3790→3830, ΔZ 1348 mm, absolute seed.
- Tests: from `prototypes/ciifr-map`, run `CIIFR_TEST_RUNTIME=<npm prefix with @xmldom/xmldom@0.9.8> node --test tests/*.test.mjs`. 61/63 pass. The 2 failures (`app-startup-ownership`, "unlinked physical TARGET") already fail on main.

## Your task: show the admission verdict in the InputXML Workspace
Work on a new branch off `a3ad4dd3`, and open a draft PR against PR #240's branch `feat/topo-b-format-admission`.

1. **Finish the carried-forward items first:**
   - (a) Write the BOM literal as `'﻿'` instead of the invisible character.
   - (b) Add a `parsererror` test on an F05 root, the way Chrome builds a partly parsed document.
2. **On file upload in the InputXML Workspace,** read the file as bytes and call `admitXmlBytes` before any topology preview. Read `tabs/inputxml-workspace/inputxml-workspace-tab.js`, `-orchestration.js` and `-xml-detect.js` first, and change as few existing lines as possible.
3. **Show a profile banner:** status, exact schema/profile, element count vs node count, absolute or relative geometry, the byte sha256 (short form), and the reason code when the file is refused. UNSUPPORTED or INVALID files must block the topology preview with a clear message, never "0 errors".
4. **Keep everything else exactly as it is:** CleanXML → 5C → InputXML enrichment, and categorized conversion. Do not reroute RichInput to 5C. Replacing the source file clears the previous verdict and graph.
5. **Tests:**
   - a unit test for the banner/state logic;
   - one real-browser check (Chrome) that loads the public S1 F05 fixture (admitted, 56 elements / 57 nodes) and a synthetic unknown XML (blocked);
   - the browser `DOMParser` path, which is NOT_RUN so far.

## Never
GLRD support (refusing it is correct for now); edits to `xml-profiles.js`, `xml-graph.js`, Workbench3D or TopoFix; CII Writer/Weight/Final; any mutation of the input; the Owner's private F05/R4/GLRD files or their hashes on GitHub; merge.

## Done = return in issue #239
- Draft PR link and head SHA.
- Changed-file list.
- Exact test commands and counts.
- Two screenshots: F05 admitted, unknown refused.
- A deliberate-failure proof.
- What you ran vs only reasoned (OBSERVED / EXECUTED_HERE / NOT_RUN).

Then stop. **Owner benchmark:** uploading F05 shows "Admitted · F05 v1.1 · 56 elements / 57 nodes · absolute"; uploading GLRD or an unknown file shows "Not supported" with the reason, and no topology.

## Every chat reply ends with this card (for the Owner)
Five lines, your own task only. Use `UNKNOWN` or `NOT_RUN` instead of guessing ([PROTOCOL §0.7](../PROTOCOL.md#0-lean-cold-start-v020)).

```text
Task Evidence v2 · topofix · coder-b · TOPO-B-B2 · <time>
1. TASK: <repo> · WBS <id> · issue #<n> · PR #<n> <draft/state> @<head8>
2. PROGRESS: <done/total deliverables> · acceptance <none|scoped review|Owner>
3. WORK & PROOF: <what changed> · tests <n/n PASS|FAIL|NOT_RUN> · <permalinks>
4. BLOCKERS & RELAY: <receipt permalink or NOT_POSTED> · <review state> · <HOLDs>
5. NEXT → <ONE ACTOR>: <one bounded action> → <expected output> → <where>
```

## Cycle receipts (how you report)
Post both receipts as comments on [issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239). That issue is this assignment's only inbox.

1. **ACK, before any work.** It binds you to this assignment. If an ACK from another chat is already there, reply `NO ACTION — already bound` and stop.
2. **Return, when done.** Put the evidence in the draft PR. Keep the receipt short.

```text
ORACLE-CYCLE-RECEIPT v1
project: topofix
receipt_id: TOPO-B-B2-<ack|ret>-<yyyymmddhhmm>
assignment_id: TOPO-B-B2
observed_revision: <CURRENT.json revision you read>
role: coder-b
chat_id8: <first 8 chars of your chat id, or UNKNOWN>
action: <received|work_returned|blocked>
candidate: <draft PR number + head SHA, or base SHA on ACK>
result: <PASS|FAIL|PARTIAL|BLOCKED|NOT_RUN; scope>
public_evidence: <PR link or NONE>
private_receipt: NONE
limits: <what you did not run>
next: <suggestion only>
END-ORACLE-CYCLE-RECEIPT
```
