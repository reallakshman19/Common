---
name: relay-onboarding-rwi
description: Read-only source-bound engineering onboarding contracts and later bounded Relay with Improvement evaluation; never grants coding, merge, acceptance or release authority.
---

# ONB-RWI v1.0 — WP1a pure contract slice

Owner issue: https://github.com/reallakshman19/Common/issues/391

**Scope of this PR:** local, deterministic and fail-closed validation of target/evidence pointers. This is a foundation, **not** a GitHub collector, a factual handover renderer, a verified proof engine, an MCDA implementation, an execution trigger or a deployed product.

- Onboarding starts without predecessor chat or final LOG: the durable target and source heads are explicit.
- The repository identity and every permitted external evidence repository/head must be declared. Nothing is inferred from file names, task IDs or historical links.
- A reported, even well-formed, source pointer is **not** independently provider-verified. This pure slice never emits READY or grants permission to write.
- Missing current source inventory is BLOCKED; unknown Owner decisions are CONDITIONAL; revision mismatch is STALE; foreign evidence is BLOCKED.
- Privacy-labeled evidence is not rendered as raw user-facing text or copied into public issue comments.
- For now, **KEEP vs IMPROVE** is not scored. Reuse existing `skills/software-mcda/` and `skills/workflow-intelligence/` later through a narrow approved interface, with hard no-drift gates ahead of scoring.
- Do not modify `skills/engineering-pr-delivery-v3.6/`, BuddyRunner, Common's `AGENTS.md`, source/oracle/acceptance authority, **CoordinatorLandingpage #21 / Team Protocol v2.3**, monitor or software-mcda code. Historical Common #360/Dash V2 is superseded for future read-only projection.
- Do not treat this schema validation as qualification for engineering-critical takeover (e.g. XML_Compare_Utilities Appendix A).

## Read-only CLI

```sh
python skills/relay-onboarding-rwi/scripts/validate_contract.py --target path/to/target.json --evidence path/to/evidence.json
python -m unittest discover -s skills/relay-onboarding-rwi/tests -p 'test_*.py' -v
```

Target is one `onboarding.target/v1` JSON object with **separate exact main and PR candidate HEAD maps** (`source_heads`, `candidate_heads`). A `PR` evidence pointer must correspond exactly to a registered `candidate_heads` URL and assessed SHA. CI/test pointers may refer to an explicitly registered candidate or main; an unregistered PR must not silently become a `main` source. Evidence is an array of `onboarding.evidence/v1` pointers. The local source-pointer assessment outputs `onboarding.local-assessment/v1` (strict schema `schemas/local-assessment.v1.schema.json`). The separately merged WP5 report-readiness contract is `onboarding.verdict/v1` (`schemas/verdict.v1.schema.json`) and remains **BLOCKED without complete protected evidence**. These are distinct semantic objects and must never be assigned the same schema identity. A `CONDITIONAL / PROVIDER_RECHECK_REQUIRED` result is the **strongest** result possible for this local-only contract slice.

**Next PR:** WP1b original input/fixture, experiment and Owner decision custody; then WP2 independent GitHub provider collector and 12-section report. Before any real-provider conclusion, re-fetch current heads and review Owner approval; hash/URL alone is not semantic proof.

## Integration alert (WP5 merged)

The existing `main` contains WP5's 12-section generator at `skills/relay-onboarding-rwi/reporting/**`. WP1a is a still-draft independent branch, so its own tests can run with no WP5 dependency, but every final report readiness verdict must follow merged WP5's separate `onboarding.verdict/v1` contract. A valid local assessment NEVER implies that WP5 report evidence is fresh or Owner-approved. Additional source-cut and cross-workpack validation remain required before integration.
