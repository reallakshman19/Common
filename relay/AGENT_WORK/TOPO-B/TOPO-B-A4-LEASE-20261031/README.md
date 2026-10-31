# TOPO-B · A4 and conditional Agent B lease · handover R1

**Nature:** PUBLIC-SAFE HANDOVER ONLY. Source-exposed independent reviewer first, existing Agent B second **only if** the two-file lease is activated. No code, private source, approved adapter, review verdict, engineering acceptance or release is delivered by this package.

**Governing native task:** [XML_Compare_Utilities #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239). **Source:** pinned XCU `main@417bf6a954c5a6de72237537e94b05b285191350`. **WBS:** TopoFix R1 2.1→4.1, RichInput proposed scope only. **Owner conditional scope authorization:** [#6541471409](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541471409). **Latest Oracle gate:** [#6541589959](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541589959). **Same-chat reviewer-conflict return:** [#6541639348](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541639348).

## Read in this order

1. [REVIEWER_HANDOVER.md](REVIEWER_HANDOVER.md): one source-exposed, **genuinely separate** non-author A4 review; all previously completed tests reused.
2. [CUSTODY_AND_AGENT_B_HANDOVER.md](CUSTODY_AND_AGENT_B_HANDOVER.md): exact two-new-file candidate writer lease, staged/blocked until both gate conditions are met. No implementation dispatch in this PR.
3. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json): public immutable source references and known evidence (not a private file transfer).
4. [ARTIFACT_REGISTER.md](ARTIFACT_REGISTER.md): relay state, producer/receiver separation, exact source/recipient evidence.

## Gate state at creation

| Gate | State |
| --- | --- |
| Public strict-reader source and F05/R4 fixture identities | **Verified in native #239 evidence**, not re-executed here |
| 16 valid V8 checks and Node+xmldom native 7/7 | **PASS reported with receipts**, preserve |
| Independent A4 non-author reviewer ACK + A1–A5 verdict | **NOT_VERIFIED / NOT_RUN** |
| Proposed reviewer IR `6ae2d5ac` | **Candidate only; separate-chat receipt and independence not established** |
| Exact two new XCU paths | **Absent on pinned main; public open-PR noncollision verified at prior gate** |
| Competing unpublished/local two-file claim | **UNKNOWN; writer confirmation needed** |
| Exclusive Agent B writer lease | **NOT_ACTIVE** |
| GLRD / CII Writer/Weight/Final / existing files / engineering acceptance / merge | **HOLD** |

**Cross-conversation transport:** A draft Common PR means `RELAY_REGISTERED / RECIPIENT_NOT_VERIFIED`. The recipient must retrieve the exact Common branch commit, verify the file identity, and acknowledge actual review. A GitHub issue comment is not delivery to a separate ChatGPT conversation. This relay does not replace the native #239 task or create a second Board/cycle.

**One accountable next operation:** Owner relays the [reviewer handover](REVIEWER_HANDOVER.md) to the genuinely independent IR; reviewer acknowledges eligibility and returns the bounded verdict on **existing issue #239**. Then Oracle performs final two-path custody activation check before existing Agent B writes.
