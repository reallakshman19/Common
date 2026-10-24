# CIIFR R4 — relay artifact handoffs (proposed, isolated)

This directory indexes **CIIFR R4 Oracle↔builder artifact transactions** using the Common engineering Relay V3.1 conventions at pinned commit `37435267c861d54998fee589e6dc91385bf59bfa`.

**Status:** DRAFT PROPOSAL. This is an artifact *index* for CIIFR, not an admitted or committed native `relay-v3.1-transaction`. In particular it does not activate a new work package, lease, custody epoch, `TX.438.*` identity, checkpoint, or shared Common `relay/STATE.yaml` update. The existing Common #438 programme's canonical relay remains untouched. Native per-project V3.1 adoption requires its own scoped initialization and recorder-validated write.

## Artifact routing contract

1. Every Oracle→agent and agent→Oracle handoff has a stable ID, exact sender/recipient role, task, input/output artifacts, bytes, SHA-256, immutable source references, privacy designation, and expected receipt.
2. A chat attachment or `sandbox:/mnt/data` URL is only a *transport locator*; **not** a permanent cross-chat URL or verified delivery. When bytes are supplied privately, the receiver obtains those bytes independently and computes SHA-256.
3. A GitHub PR/commit file tree is a durable public *source artifact* but it is **not byte-identical to a separately zipped workpack**. Never substitute one checksum for another.
4. Protected customer CII bytes, identifiable model contents, private file locations and full chat links must never appear in this public index.
5. Handoff transitions stay separate: `DECLARED` → `RECEIVED_CONFIRMED` → `BYTES_VERIFIED` → `WORK_RETURNED` → `REVIEWED` → `OWNER_ACCEPTED`. Record receipts only after actual measurement/readback; do not advance on a claim alone.
6. The sender/receiver posts a public-safe receipt on the task issue; the Oracle reconciles evidence and projects to the **existing** standalone Progress Page key `ciifr` using `pp_cli.py` in a data-only draft PR. A draft does not equal publication.
7. No transfer, engineering edit, merge, release or Owner acceptance authority follows merely from a relay record.

## First handoff

`S1-ORACLE-TO-BUILDER.yaml` indexes R4 S1 issue #159, charter #158, public code source at the exact head of draft PR #163, and the separate local ZIP checksum. The recipient must verify an actually obtained ZIP before treating it as received.

## Protocol bases

- [Pinned Common Relay tree](https://github.com/reallakshman19/Common/tree/37435267c861d54998fee589e6dc91385bf59bfa/relay)
- [Engineering Relay V3.1](https://github.com/reallakshman19/Common/blob/37435267c861d54998fee589e6dc91385bf59bfa/skills/engineering-pr-delivery-v3.1/SKILL.md)
- [CIIFR R4 charter](https://github.com/reallakshman19/XML_Compare_Utilities/issues/158)
- [R4 S1 task](https://github.com/reallakshman19/XML_Compare_Utilities/issues/159)
