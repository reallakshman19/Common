# NLM-P3 synthetic validator return

| Item | Quoted evidence or computed number | Finding | Source |
|---|---|---|---|
| I-01 | "red blue" has 2 whitespace tokens; claim=2 | MATCH | sample-items.txt:1 |
| I-02 | "red blue green" has 3 whitespace tokens; claim=3 | MATCH | sample-items.txt:2 |
| I-03 | "red" has 1 whitespace token; claim=2 | MISMATCH | sample-items.txt:3 |

Three weakest: I-03 (contradiction), I-01 (short source), I-02 (least independent context).
Claimed row count: 3. Independently recount from sample-items.txt, not from this report.
