# Concept review

C1 contains an incorrect inference; C2 is correct under the stipulated model. Retain the zero initial velocity in C1 and the full result in C2.

## Source and applicable model

Reviewed `case.md` as supplied in this directory, including both transcribed note claims and the reported prior verdict. It stipulates release from rest, upward positive, constant downward gravity of 7.2 m/s², no drag and free flight after release. These conditions give, for the free-flight interval beginning at release,

\[
v(0)=0,\qquad a(t)=-7.2\ \mathrm{m/s^2},\qquad
v(t)=v(0)+at=-7.2t\ \mathrm{m/s}.
\]

Acceleration measures the rate of change of velocity, not its instantaneous value. At release, zero velocity and nonzero acceleration coexist. This is a contrary case supplied by the original model itself; no additional physical premise is required. Pre-release support forces are outside the stated free-flight interval.

## Claim-level results

| Claim or factor | Supplied assertion | Expected from the model | Verdict and disposition |
|---|---|---|---|
| C1: initial velocity | Velocity is zero at release. | Release from rest means `v(0) = 0 m/s`. | MATCH. Retain this premise. |
| C1: acceleration inference | Therefore acceleration is zero. | Constant downward gravity gives `a(0+) = −7.2 m/s²`, including the start of free flight. | MISMATCH. Observed conceptual defect: zero velocity does not imply zero acceleration. |
| C2: later velocity | At 0.5 seconds, velocity is −3.6 m/s. | `0 + (−7.2 m/s²)(0.5 s) = −3.60 m/s`. | MATCH. Retain; the negative sign correctly denotes downward motion. |

## Actual arithmetic check

I independently selected the constant-acceleration relation from the stipulated inputs and executed this local Python decimal arithmetic with bytecode disabled (`PYTHONDONTWRITEBYTECODE=1 python -B`):

```python
from decimal import Decimal
v0 = Decimal('0')
a = -Decimal('7.2')
t = Decimal('0.5')
v_release = v0 + a * Decimal('0')
v_half = v0 + a * t
rate = (v_half - v_release) / t
```

Observed outputs were `v_release = 0.0 m/s`, `v_half = −3.60 m/s` and `rate = −7.2 m/s²`, matching the derived expectations. The rate calculation checks the change over the interval; the stipulated constant acceleration establishes the instantaneous acceleration throughout free flight. This is an arithmetic witness, not a separate physical experiment or solver validation.

## Findings and next action

- **Content defect, C1:** its acceleration conclusion contradicts the governing model. Report this conclusion for correction to “velocity is zero at release; acceleration is −7.2 m/s² during free flight.” No source edit was performed.
- **Evidence gap in the supplied prior review:** quoting the note establishes what it says, not whether its inference follows. The reported “all factors match” verdict cannot be retained for C1's acceleration factor. The next review disposition should distinguish that mismatch from the correct factors above.

## Coverage and limits

Both supplied claims and C1's separate factors were checked against the original stipulated conditions, signs and units. `case.md` decoded strictly as UTF-8; its byte SHA-256 was `d384105802ac1bcfd49146946a3accc421c36d74155f64511c5cd1a514da4703`. No separate full note, prior-review artifact or revision history was supplied; review conclusions cover the text transcribed in this case only.

Read this run: `case.md`, the Nudge Designer `SKILL.md`, `references/ADAPTIVE_SUPPORT.md`, `references/APPLYING_GUIDANCE.md` and `assets/prompts/reviewer.md`. No examples, tests, verification/plan records, other task directories or other agents' outputs were read. I did not contribute to the supplied note or prior review during this run; the method shares the case's stipulated model. Blindness and formal review independence are not established. Host model/reasoning configuration and formal qualification remain UNKNOWN.

The bounded concept review is complete. There is no learner evidence, curriculum decision or parent-outcome acceptance in this result. No solver, learner contact, external write, delegation or source/product modification was performed. `review.md` is the sole new artifact.
