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
- Do not modify `skills/engineering-pr-delivery-v3.6/`, BuddyRunner, Common's `AGENTS.md`, source/oracle/acceptance authority, dashboard, monitor or software-mcda code.
- Do not treat this schema validation as qualification for engineering-critical takeover (e.g. XML_Compare_Utilities Appendix A).

## Read-only CLI

```sh
python skills/relay-onboarding-rwi/scripts/validate_contract.py --target path/to/target.json --evidence path/to/evidence.json
python -m unittest discover -s skills/relay-onboarding-rwi/tests -p 'test_*.py' -v
```

Target is one `onboarding.target/v1` JSON object; evidence is a JSON array of `onboarding.evidence/v1` pointers. The output conforms to `onboarding.verdict/v1`. A `CONDITIONAL / PROVIDER_RECHECK_REQUIRED` result is the **strongest** result possible for this local-only contract slice.

**Next PR:** WP1b original input/fixture, experiment and Owner decision custody; then WP2 independent GitHub provider collector and 12-section report. Before any real-provider conclusion, re-fetch current heads and review Owner approval; hash/URL alone is not semantic proof.
