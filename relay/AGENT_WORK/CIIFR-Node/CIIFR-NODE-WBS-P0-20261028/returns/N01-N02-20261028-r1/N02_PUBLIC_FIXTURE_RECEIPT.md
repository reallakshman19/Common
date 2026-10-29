# N-02 public fixture receipt — 28 October 2026

Task: CIIFR-NODE-N02-FIXTURE-V14 / [issue #229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229). Parent: [WBS #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).
Candidate: PR226 at `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`.
Input relay: Common commit `56dbc3a0af137c433ffb5fec48316fa2022d075c`, Common PR559 still DRAFT / NOT_MERGED.

## Actual receipt

The receiving root review session fetched the two permitted public synthetic files using GitHub's base64 contents reader, decoded the returned bytes, and independently measured length, SHA-256 and Git blob SHA-1. Both are ASCII with CRLF-only line terminators.

| Public file | Bytes | SHA-256 | Git blob |
|---|---:|---|---|
| SYNTH_V14_SOURCE.cii | 8276 | c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b | 7d00c13f5c5906a9bb2dba53287f133c8db06358 |
| SYNTH_V14_TARGET0.cii | 8276 | 0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661 | dddf157895571802973b71904fbad0a679a7e271 |

All measured identities match the relay catalog and received GitHub blob identities. Public fixture receipt for this receiving session: **BYTES_VERIFIED**. This does not merge Common PR559 or establish receipt by any other participant.

## Independent bounded physical observation

The accompanying Python auditor imports no product parser. It decodes fixed fields directly, checks primary/selected auxiliary counts and pointer ownership, and compares its own decoded facts to the author-exposed catalog.

Observed in each file:
- VERSION14; two 15-row elements; NUMNOZ=NOHGRS=0; IZUP=0.
- One RIGID, RESTRANT, DISPLMNT and FORCMNT block, each referenced by element ordinal 1.
- One populated restraint/specification per relevant auxiliary family; material entries [1,1].
- Element process values and oriented endpoints agree with F01's source/target rows.
- A seeded CONTROL.NUMELT corruption is rejected by the separate auditor.

Command: `python n02_fixture_audit.py`, Python native runtime. Result: PASS for this bounded public synthetic physical contract. Reproduction requires the input JSON catalog and the two immutable public input blobs; retrieve them from the original relay, not an original/customer file.

## Limits and surviving wrong case

Authorship: this review session did not author the fixture pack. Principal/account independence is not established; the GitHub identity is shared. The catalog and expected values were read before comparison and remain AUTHOR_EXPOSED. A separate decoding method is evidence of method diversity, not independent engineering acceptance.

The fixtures contain no nonzero DISPLMNT/FORCMNT numeric fields after their first node reference and no displacement 9999.99 sentinel. They test record existence and ownership, not nonzero vector, operating-set, free-versus-zero displacement or unit interpretation. The minimal reader-profile files are not certified as complete vendor-importable CAESAR II models.

A parser that correctly indexes these first records but mishandles a nonzero load component or a later case could still pass these fixtures. Add independently justified nonzero-vector and sentinel cases before P3 semantics, and original-positive/vendor cases before writer qualification.

Protected original: **NOT_RECEIVED / NOT_RUN**. No protected source, child URL or private node map was retrieved or published. Original V14, Windows/browser and licensed vendor qualifications are not established by this receipt.

## Disposition and next action

N-02 is **PARTIAL**: public synthetic custody and bounded physical audit PASS; protected-original custody/inspection NOT_RUN. Keep all writer/release HOLDs. The next N-02 actor is an authorized original-file custodian/receiver who can provide exact permitted private bytes and independently establish their identity and physical-field evidence.
