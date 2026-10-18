# Subject check for N-EXAMPLE

This is the same specialist's local calculation and content check, not an independent review or a learner assessment. Model and reasoning configuration are UNKNOWN because they were not observed.

## Basis and conditions

Read this run: `case.md`, `intent.json`, `plan.json`, and `packet.json`. The governing synthetic example is an upward throw with u = +18 m/s, upward positive, g = 9 m/s², and no drag (`C-PHYSICS`). No board syllabus, learner response, or delayed retrieval is available. Source `S-TEACHER` has no pinned revision.

The issued plan's handover says “20 m/s”; that conflicts with the explicit 18 m/s condition in the case, intent, and packet. The study note uses 18 m/s. The issued files were preserved; the Designer should reconcile the handover before reusing it.

## Derivation and actual local arithmetic

During free flight, a = −g = −9 m/s². For this constant acceleration,

- v(t) = u + at = 18 − 9t m/s, when t is entered in seconds.
- y(t) − y(0) = ut + ½at² = 18t − 4.5t² m.
- At the top, 0 = 18 − 9t gives t = 2 s.
- The rise is 18 × 2 − 4.5 × 2² = 18 m; the separate relation u²/(2g) = 324/18 = 18 m agrees.

Executed `arithmetic.py` with Python's exact `Fraction` arithmetic; `arithmetic.json` records the results. The signed values are:

| t (s) | v (m/s) | Rise (m) | a (m/s²) |
|---|---|---|---|
| 0 | +18 | 0 | −9 |
| 1 | +9 | 13.5 | −9 |
| 1.9 | +0.9 | 17.955 | −9 |
| 2 | 0 | 18 | −9 |
| 2.1 | −0.9 | 17.955 | −9 |
| 3 | −9 | 13.5 | −9 |

Across 1.9–2.1 s, Δv = −0.9 − (+0.9) = −1.8 m/s and Δt = 0.2 s, so Δv/Δt = −9 m/s². The stipulated constant-acceleration model also gives this acceleration at the turning instant itself. Zero velocity therefore does not imply zero acceleration.

For the contrast, an object held at rest has v = 0 throughout an interval, giving Δv/Δt = 0. Gravity still acts downward, while an upward holding force balances it; net force and acceleration are zero. This contrast introduces support explicitly and does not apply the free-flight acceleration to the held object.

Units check: (m/s²) × s = m/s; (m/s) × s and (m/s²) × s² are metres; (m/s)/s = m/s². The script's nine arithmetic and contrast checks passed.

## Limits and continuation

The short note and local arithmetic fulfill the bounded N-EXAMPLE draft/check task. A correct note does not establish actual understanding, independent subject review, or the integrated learning outcome. No learner was contacted and nothing was published. N-TRANSFER remains for a new motion problem and explanation rubric; actual learner response and learning gains remain unknown. The next local proposal is Designer review of these artifacts and the 20 m/s handover inconsistency, followed by preparation of the separately planned transfer material under existing authority.
