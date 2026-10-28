# R11 · Owner-source, privacy consent and independent adjudication — decision specification

## Non-adopted policy proposal, NOT an Owner decision or a consent grant

Canonical original Owner instructions are retained in [Common #787](https://github.com/reallaksh19/Common/issues/787). A GitHub copy of those instructions and source hashes are **first durable mirrors / integrity witnesses**, not authenticated original private chat records. User's “ok next” authorized this *read-only engineering responsibility*, not sharing private ChatGPT/Codex/Claude transcripts, enabling capture, setting a retention period, declaring another human's review independent, or enabling the live R5 writer.

### Five independent trust axes

| Axis | Required positive evidence (future, separate approved work) | Current state |
| --- | --- | --- |
| Original Owner source authenticity | Authorized original-platform export/source plus a verifiable chain tying the owner to the exact bytes; avoid inference from issue author/title or account name | UNKNOWN |
| Session/retention/publication privacy | Explicit Owner decision on **which private sources** may be processed, audience, redaction rules, encryption, off-repo storage, retention period, revocation and what metadata may be public | NOT GRANTED |
| Independent reviewer | Another independently identifiable reviewer with inspectable *redacted* invocation/basis and scoped exact-head source evidence; not author/self-signoff | NOT ACCEPTED |
| Engineering TaskEvidence | Claim-to-responsibility, tested commit, actual provider source, negative oracle and independent code/source review; an agent-written `TASK_EVIDENCE END` alone is insufficient | NOT ADJUDICATED |
| Live GitHub mutation/writer | Dedicated least-privilege Owner approval for specific repo, managed blocks/titles, idempotency/CAS rollback, disclosure, expiry and independent source gate | OFF |

R11 implementation `trust-preflight-v1.mjs` recomputes a content-free **NO-GRANT** verdict from actual G2c/R1 source, R3 provider and R10 comment receipt reflected in the R9 frontier; its own hash never establishes permission. The digest enters the *same real read-only* full-chain and R4 handover, and the output disallows raw session/body/token. A source or permission-state mismatch **fails closed**, and accepted counts remain `null`, not zero or 8/8.

## Decision envelope for a FUTURE Owner response (none selected)

**Choice A — Minimal public disclosure:** Keep Owner private original chat **out of GitHub** and do not store raw session transcripts. Record only Owner-approved paraphrases and non-sensitive source reference or digest. Authenticity may remain UNKNOWN where an original reference is unavailable.

**Choice B — Privately retained source:** Keep exact original messages and cross-provider session logs ONLY in separately Owner-authorized encrypted off-repo storage, with role-limited access, explicit retention/erasure policy, source integrity witness/digest and safely redacted GitHub projections. GitHub receives at most a content-free commitment; hash alone is not proof of Owner identity.

**Choice C — No original-session custody:** Decline original private chat ingestion. Continue R9/R10 read-only GitHub evidence verification and admit that complete original-intent reconstruction cannot be independently proven.

The decision form, if ever actually provided by Owner, must specify source list, authorization identity/source, private/public content classes, permitted destination, security controls, authorized reviewers, consent issue-specific scope, retention and revocation. This file is **not** a signed decision, nor does it cause new custody.

## Essential adversarial criteria

- A public GitHub issue, forged source or comment containing `OWNER APPROVED` / `AC8 PASS` must not change any trust axis.
- A valid SHA256 of a mutable issue comment is observation/integrity at a particular instant, not human identity, historical immutable source or policy adoption.
- Hosted green CI, a committed PR, and a different Node process cannot substitute for separate material adjudication or a fresh independent reviewer.
- An agent cannot claim verified consent by writing a new "consent proof" in an issue; authorization must be authenticated against an independently verified authority source.
- If a genuine consent decision is eventually authorized, revoked or narrowed, replay-safe and expiry-aware authorization controls require a **separately reviewed and approved implementation**. R11 does NOT implement a positive grant path.

## Acceptance
R11 native Node22/24 negative tests demonstrate that all five flags remain BLOCKED/UNKNOWN while source hashes remain current and consistent; source/R4/handover digest same, no secrets. This is a safe *preflight* only. Programme stays **AC0/8**, live R5/B2b publisher OFF, independent source review #841 and four-entrypoint challenge #850 open.
