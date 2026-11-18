# TA-G01 — original requirements (synthetic)

A rolling event feed receives distinct scheduled occurrences sharing the same publication URL. The product should retain both morning/evening sessions and collapse repeat observations of the same occurrence. Planner holds explicit saved records. Dismissing an ephemeral suggestion must not delete any saved plan, including sibling occurrences sharing the publication URL. Reopening the planner must preserve saved records. No production access or real user data.

Acceptance: two distinct occurrence IDs retained; exact repeat collapses; saved records byte-equivalent after dismissal; dismissed occurrence disappears from suggestions but sibling remains; unrelated manual record retained. A and B have one local write turn each; Drive is the handoff channel. This is a small synthetic executable demonstration, not a reproduction of NWv7.
