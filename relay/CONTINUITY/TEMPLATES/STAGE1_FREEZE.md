# STAGE1_FREEZE_V1 — external Controller receipt (template)

Only an authenticated independent operator/controller may author this **after** fresh Runner B submitted an unchanged factual baseline and provisional Part B.

| Field | Controller evidence |
| --- | --- |
| Episode + existing responsibility | [IDs and governed binding] |
| B session identity, original source/tool envelope | [externally observed, not B's own claim] |
| Stage 1 source packet immutable SHA/digest | [commit/path/raw hash/readback] |
| B submitted reconstruction immutable SHA/digest | [commit/path/raw hash/readback] |
| Actual denied-read/tool-isolation evidence | [external Stage1 release preflight receipt with B identity, positive historical read plus denied-current-PR/issues/Stage2/alternate GitHub/tool access, or NOT_RUN] |
| Contamination verdict | `CLEAN_ATTESTED` / `CONTAMINATED` / `UNKNOWN` |
| Independent factual baseline + provisional interpretation were frozen BEFORE A reality | [independent observation timestamp/order or UNKNOWN] |
| Stage 2 disclosure authorization | [authenticated Owner/controller decision/ref or NOT_GRANTED] |
| Admission result | `STAGE2_RELEASE_PERMITTED` / `HOLD_BLINDNESS` / `HOLD_OWNER_APPROVAL` |

A `sha256` or Git blob readback proves bytes, **not** a fresh B context, authentic Owner approval, sole writer, or isolation of whole-repository GitHub tooling. If a forbidden route was open, fail closed even if the model says it didn't look. If material changed after submission, new B run required, not a retrospective rewrite.

**STOP:** this receipt may authorize *read-only Stage 2 disclosure* if genuinely backed by external authority; it never grants execution. Do not publish A current technical handover to a B-readable ref before `STAGE2_RELEASE_PERMITTED`.
