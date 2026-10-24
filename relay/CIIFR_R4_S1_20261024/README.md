# CIIFR R4 S1 — Oracle ⇄ Builder artifact relay

This is a **public-safe, source-bound artifact transaction** stored under Common `relay/` in its own DRAFT PR. It is **not** Common's #438 internal `relay/TRANSACTIONS` ledger and changes no `relay/STATE.yaml`, leases, control records or Progress Page source data.

## Durable links and provenance

- **Builder return package now hosted in this folder:** [CIIFR_R4_S1_RELAY_SOURCE.zip](./CIIFR_R4_S1_RELAY_SOURCE.zip) — 72,147 bytes, SHA-256 `d6cc5d74eb3913184e69a511a47d0cf0be4337d9528aa56f9b921f5df767e039` (14 files, source texts assembled from immutable PR #163 code).
- **Authoritative converter code:** [XML_Compare_Utilities exact commit](https://github.com/reallakshman19/XML_Compare_Utilities/tree/4f31afebcc8afadc1024ef8e7545e5551229ff09/prototypes/ciifr-r4). Source-archive fallback: https://github.com/reallakshman19/XML_Compare_Utilities/archive/4f31afebcc8afadc1024ef8e7545e5551229ff09.zip
- **Existing draft PR:** [#163](https://github.com/reallakshman19/XML_Compare_Utilities/pull/163). S1 [assignment #159](https://github.com/reallakshman19/XML_Compare_Utilities/issues/159), [evidence comment](https://github.com/reallakshman19/XML_Compare_Utilities/issues/159#issuecomment-6387012220), [CI 4/4](https://github.com/reallakshman19/XML_Compare_Utilities/actions/runs/40113885630).
- **Oracle inbound ZIP:** 34,352 bytes, SHA `d85d7ede9abc4381fe636a85b22c9ba9449a860fa8fd0420d267eb1fde13c9cb`; original exact-byte transfer currently **NOT mirrored** into relay. Oracle receipt: [#158 comment](https://github.com/reallakshman19/XML_Compare_Utilities/issues/158#issuecomment-6386689258).
- **Earlier Owner chat demo ZIP:** 28,815 bytes, SHA `7b4fe07201a7716f07fffdccd5200095c971ebeea440d144993bcafa43d06bf3` — chat attachment only, **NOT the same bytes** as this relay source rebuild. A `sandbox:/mnt/data` link is not a cross-agent durable download.

## Next Oracle interaction

1. Download **the actual relay ZIP above** and independently verify its SHA/size before running anything. It contains the code needed for a synthetic test; run `python fixtures/make_synthetic.py` in the extracted `CIIFR_R4_S1` folder, then `python -m unittest discover -s tests -v`.
2. Read `OWNER-DEMO.md`, then commission an independent wrong-case review at exact candidate SHA. The builder's synthetic 10/10 and 4/4 CI claims apply to the source commit, not a newly run independent test of this relay ZIP.
3. Owner exercises the real private CII locally. Record independently measured original SHA-256 and size privately; do not publish any CII bytes, private paths, customer properties, or private Drive child links.
4. Keep PR #163 **DRAFT**, P2/P2.1 untouched, CAESAR engineering equivalence unclaimed, edit/transfer HOLD. Publish Progress only through the project's native data-only reviewed path.

## Handoff rule

Each Oracle → agent and agent → Oracle artifact must have a **recoverable transport** (public-safe GitHub file/commit or authorized private custody), an exact checksum + size, author/source, input/output roles, task/PR/evidence links, and a recorded retrieval/verification result. A chat-only `/mnt/data` link may be an extra convenience but **is not sufficient custody**. The original Oracle ZIP still needs a separate exact-byte relay or authorized private source before this transaction can be declared fully mirrored.

See [manifest.json](./manifest.json) for machine-readable provenance and outstanding gates.
