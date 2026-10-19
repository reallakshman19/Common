# Owner request

Fix this small local search-session component. Users sometimes see an older search
replace newer results, including after returning to a previous project filter.
Cancellation must leave the view idle and empty even if the cancelled operation
finishes later. Preserve normal successful results, genuine current errors and
reuse after cancellation. Rows are already ranked; preserve their supplied order.

The source is work/session.py. The original source and existing native checks are
in raw/. Keep raw/ byte-identical and change only work/ and out/. Add focused checks
where useful. Use the provided Python runtime; no network, browser or live repo
actions are needed or authorized. Deliver a working component and concise evidence
of what actually happened, what changed direction and what remains unestablished.
