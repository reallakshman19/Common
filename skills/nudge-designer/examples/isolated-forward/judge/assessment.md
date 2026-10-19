# A-ASSESS revision 1 — bounded local assessment

Both supplied prompt blocks cover their BP-1 demands: **F FULFILLED; U FULFILLED**. Exact independent calculations give **+9 N**, **+2 m/s² (right)** and **0.735 m**. No substantive prompt defect was found; the defect set is empty. This is T-ASSESS for MAP-BP1-PILOT revision 1, with no tracker alias or parent acceptance.

## Inputs and verification

Only assignment.md, ../judge-issued-inputs.sha256.json and the four specified inputs were read. All five file-byte SHA-256 digests listed in the manifest match. The manifest itself hashes to `1c7a42bf25d5f2730b195bfb2e3860d9e87c42a6d9d40986559f9aedb3afcfce`. Exact expected/actual input hashes and computations appear in calculations.json. Python ran with `-B` using only standard libraries; the stated decimal givens were treated as exact. No restriction prevented the required reads or computations.

## Coverage and witnesses

“MET” below means the prompt requires the part, not that a learner has demonstrated it.

| Part | Status | Prompt/source witness |
|---|---|---|
| F1: signed force assignments and net force, with units | MET | problems.md, F item 1 explicitly asks both. |
| F2: derive and calculate signed acceleration using positive mass and F_net=m*a, with units | MET | F opening gives 4.5 kg and F_net=m*a; item 2 explicitly asks derivation, signed acceleration and units. |
| U1: positive length, mm-to-m conversion and units | MET | U opening gives positive physical length 735 mm; item 1 asks conversion to metres with units. |
| U2: explain factor 1000 and the physical-length relationship | MET | U opening supplies 1000 mm = 1 m; item 2 asks why 1000 is used and whether physical length changes. |
| Two short, self-contained exercises with stipulated models | MET | One F and one U block. F gives 17 N right, 8 N left, no other horizontal forces and right positive. U supplies its unit equality. |
| Clear settings and values without a prescribed benchmark number | MET | Cart and strip settings are explicit; BP-1 final paragraph permits different settings/numbers. |
| Correct source-grounded producer solutions | UNKNOWN | BP-1 requires solutions; setup.md says they are withheld and problems.md contains prompts only. |
| Full producer artifact distinguishes conceptual validity from actual learner understanding | UNKNOWN | Required by BP-1; complete artifact/report is withheld. The supplied prompt blocks make no learner-understanding claim. |
| Actually invented settings/values or independent derivation | UNKNOWN | BP-1 requests invention; setup.md expressly says numerical/settings differences do not authenticate independent derivation. |

All MET gives FULFILLED: F1/F2, U1/U2 and their combined prompt demands therefore are FULFILLED. Any UNKNOWN gives UNKNOWN while retaining known misses: full BP-1 authoring compliance on this limited issued set is **UNKNOWN**, with **no known NOT_MET parts**. Missing producer evidence is not itself an observed content defect.

## Independent calculation and contrast

F: right-positive forces are +17 N and −8 N, hence F_net = +17 − 8 = **+9 N**. From F_net = m*a and m = 4.5 kg > 0, a = F_net/m = 9/(9/2) = **+2 m/s²**, toward the right. N/kg = m/s². Only the stipulated horizontal model is used.

U: 735 mm × (1 m / 1000 mm) = 735/1000 m = 147/200 m = **0.735 m**. A metre contains 1000 millimetres, so the numerical magnitude is divided by 1000 when expressed in metres. The conversion factor is a ratio of equal lengths and equals one: the unit and number change, while physical length stays the same. The prompt has no misleading physical premise.

These are correct answers derived from the prompts, not verification of the withheld producer answers. A meaningful missing-part contrast is to remove U item 2 while retaining 0.735 m: U1 would be MET, U2 NOT_MET, and the roll-up PARTIAL. Likewise, the bare F answer +2 m/s² supplies neither the signed-force/net-force work nor the required derivation. A correct final number alone cannot establish all demands. These contrasts are hypothetical; no input was edited and no learner was observed.

## Reference relationship and limits

The supplied reference uses 4 kg, 30 N right and 10 N left; recomputation gives +20 N and +5 m/s². Its 1600 mm converts to 1.6 m. New values (4.5 kg; 17/8 N; 735 mm) and results differ. The shared cart/force and unit-conversion structure follows BP-1. Numerical non-identity establishes neither invention nor independent derivation.

reference.md states that OLD-F was copied then renamed and OLD-U adapted, and that the old producer had read the reference. Its old producer verdict is not an oracle. setup.md records a fresh producer conversation, an issued set containing an operational brief and BP-1, exclusion of the reference/old examples/Oracle planning, and a producer self-report of using only those inputs. This supports a documented issued-input boundary. It does not prove an access audit, OS-enforced isolation, training-data independence or independent derivation; actual model/effort and formal qualification are unestablished.

For this assessment I read the allowed reference, including its old answer values, before computing the new answers; this is not a blind assessment against that reference. I did not read the original producer solutions/report, other Oracle records, parent checks, other task outputs or skill libraries. Isolation is an instruction boundary on shared storage. A different role or fresh conversation is not formal qualification or fully independent evidence. Shared assumptions are exact synthetic givens, the stipulated right-positive horizontal Newtonian model, standard SI units and the supplied mm/m equality.

The conclusion is limited to these prompt blocks and their independently computed answers. It establishes neither actual learner understanding nor wider generator/model/skill reliability. No external/product action, tracker change or parent acceptance occurred. Inputs were preserved; only assessment.md and calculations.json were created.
