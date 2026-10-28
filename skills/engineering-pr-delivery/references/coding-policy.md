# Coding and Scope Policy

Keep changes surgical.

- No broad refactors, dependency upgrades, generated churn, abandoned flags, backup copies, or unrelated cleanup.
- New JavaScript modules should normally remain under 300 physical lines; functions under 40 logical lines where practical. These are maintainability heuristics, not correctness gates.
- Prefer named exports, pure functions, explicit dependencies, bounded mutation, and no hidden singleton authority.
- No hidden/default production mocks.
- No silent engineering-data fallback.
- No temporary authority-changing shims.
- New abstractions should have a real production consumer in the same PR unless explicitly approved otherwise.
- Avoid unused speculative infrastructure.

Action-first gate:

```text
core production behavior
-> production integration
-> operator-visible/downloadable/measurable result
-> focused regression
-> required engineering evidence
```

Docs/schema/validator-only work does not prove production completion unless that is explicitly the mission.
