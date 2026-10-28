# CIIFR-Node · Public-safe core fixture pack

**WBS:** [CIIFR-Node #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227) · **Exact read-only candidate:** [PR #226](https://github.com/reallakshman19/XML_Compare_Utilities/pull/226) @ `b2b695f66fc8dfc907f2b9a493b39bd4d4109570` (refresh actual head before qualification).

This directory is **Common's public-safe artifact relay**, *not* a newly created `CIIFR-Node` source repo, new Cycle activation, a product release or independent acceptance. Use [Common START_HERE](https://github.com/reallakshman19/Common/blob/a353371d5f1ea3d6df8214165ecdecebda9df41b/skills/agent-work/START_HERE.md), [artifact contract](https://github.com/reallakshman19/Common/blob/a353371d5f1ea3d6df8214165ecdecebda9df41b/skills/agent-work/ARTIFACT_RELAY.md), and [full WBS #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).

## Payload and readback

Both `.cii` files are **deterministically authored synthetic ASCII CRLF** (109 lines, 8276 bytes). Public-safety: no proprietary file data. The producer prepared and then read back exact GitHub blobs; **assigned reviewer readback is NOT_RUN**. Receiver must fetch the exact commit and verify size, SHA-256 and parsed content *before* saying BYTES_VERIFIED.

| File | SHA-256 (producer independently reproduced with Python) | Git blob |
|---|---|---|
| `SYNTH_V14_SOURCE.cii` | `c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b` | `7d00c13f5c5906a9bb2dba53287f133c8db06358` |
| `SYNTH_V14_TARGET0.cii` | `0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661` | `dddf157895571802973b71904fbad0a679a7e271` |

Both contain 2 oriented 15-row ELEMENTS, 1 RIGID, 1 RESTRANT×24, 1 DISPLMNT×20, 1 FORCMNT×20 and MISCEL_1 with two material IDs. Source: 400→500 (T1=200,P1=30), 500→600 (T1=180,P1=20); Target: 840→850 (T1=195,P1=28), 850→860 (T1=175,P1=18). **These are invented engineering values solely for software falsification.** Equal topology shape or a fixture's chosen correspondence does **not** authorize copying pressure/temperature from SOURCE to TARGET.

`FIXTURE_CATALOG.json` records F00–F07 public expectations, deliberate wrong cases, and private-original custody status; reviewers should derive an independent expected oracle rather than claiming author fixtures are blind.

## Private original is separate

Original V14 `GLRD-SYS-20-10.CII` is **not included**. Owner-controlled private handoff (`OWNER_PRIVATE_REF:HANDOFFS_PRIMARY`) is required for N-02; no protected paths/child links in public GitHub. Earlier aggregate inventory is **reported, not newly received**. Real SOURCE→TARGET comparison remains UNKNOWN until each authorized original is independently verified.

## Next actions, distinct roles

- N-01 [native regression/reviewer](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228): exact candidate original NODAL test and read-only Property tab isolation.
- N-02 [fixture custody and original source](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229): verify public payload hash and actual private bytes when access exists.
- N-03 [TO-only/oriented correspondence](https://github.com/reallakshman19/XML_Compare_Utilities/issues/230): only after N-01 independent seam, and separate code authority.

**All recipients currently UNASSIGNED; Common relay is not dispatch.** The Page project fixture entry must distinguish `RELAY_PUBLISHED` from `RECEIVED/BYTES_VERIFIED`, and Page data should be written only via its authorized CLI and operator.
