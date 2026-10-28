# Authority Boundaries

For sensitive changes trace:

```text
authority
-> canonical data
-> transformation
-> solver/calculation
-> recovery
-> publication
-> report/UI/export
```

Identify where the symptom first becomes wrong.

For each layer state:
- source of truth;
- permitted mutations;
- downstream consumers;
- tests/evidence;
- whether this PR may change it.

Protect engineering authority, XML/writers, runtime publication, CAD/rendering geometry, topology, support classification, persistence, master data, and engineering exports from accidental duplicate authority.

Preview/UI state must not silently become solver/calculation authority.

Unrelated rendering/state updates must not discard uncommitted engineering input.

Model-changing mutations must invalidate incompatible execution state.

Record `DEC-*` for material authority-boundary decisions.
