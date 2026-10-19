# Generation assignment A-GENERATE — revision 1

Prepared for a fresh task-local worker; no work has been dispatched by this packet.
Canonical task: MAP-BP1-PILOT revision 1 / T-GENERATE. Tracker alias: MOVE-31.
Your channel reply must start with **ACK MOVE-31**. This correlates the reply; it does not claim completion. Keep A-GENERATE revision 1 as the assignment identity.

## Purpose and one deliverable

Create one candidate bundle of two new short exercises, one F and one U, so Oracle can test BP-1 through separately assessed artifacts. Write `exercises.md` (both prompts and solutions) and `native-report.md` only in:

`/workspace/scratch/52eed2252c51/tmp/isolated-nudge-forward/oracle/generation`

This is synthetic authoring. Your own validity judgments are **SELF-ASSESSED**. Separate assessment, broader blueprint reliability and learner understanding remain for Oracle; do not claim them from your output.

## Allowed inputs

Read only this issued brief and `/workspace/scratch/52eed2252c51/tmp/isolated-nudge-forward/blueprint.md` (BP-1), whose full body appears below. Expected SHA-256 of the source file bytes:

`6b904a1405b98399d78dc6d8c87e4caf243cfc99a2cf53c550628953cc8c3546`

Withheld task material: the Oracle/assessor `reference.md`, prior examples and derivation logs, Oracle task map/native objects/assessment notes, and other task outputs. Do not browse those files, earlier conversations or external answers. Standard local runtime libraries are permitted. This is an instruction boundary on a shared filesystem, not verified OS prevention. Before authoring, report any relevant prior worked-answer/reference exposure; a fresh turn cannot remove it. Training-data exposure is UNKNOWN.

## GUIDED method and boundaries

1. Read BP-1 and check its file-byte hash with local Python if available. Invent your own clear setting and values for each profile. Do not ask for withheld benchmarks or choose values by comparison with them.
2. For F, stipulate the model and givens, including a positive mass, two opposing horizontal forces, a positive direction and no other horizontal forces. Ask for signed net force **then** signed acceleration. Assign each force its sign, add the signed forces, and derive `a = F_net / m` from `F_net = m*a`. Include units and explain direction/sign; positive mass preserves the net-force sign in acceleration.
3. For U, choose a positive millimetre length in an ordinary measurement setting. Ask for metres **and why the factor is 1000**. Derive `L_m = L_mm / 1000` using `1000 mm = 1 m`: the same physical length has fewer numerical units when expressed in metres. Avoid a premise implying the object changes length.
4. Recalculate your chosen values by hand or Python. On the same F item, check that reversing the coordinate convention reverses both signed answers while preserving magnitudes. On U, convert the metre value back to millimetres. These are self-checks of the two items, not requests for extra exercises. Read back the saved files and report the actual results.

Preserve original inputs. No external publication, product changes, delegation or actual learner acceptance. Model/effort and substantive task fit are UNKNOWN. Local file/Python tools are supplied as intended access; actual operation is unverified for you. The brief does not change runtime or qualify you. Oracle reserves changes to BP-1/scope/identity and acceptance of content, provenance or the whole pilot.

## Success and useful failure cases

Both exercises must be self-contained and satisfy every BP-1 condition. In your native report, give a concise witness and `MET`, `NOT_MET` or `UNKNOWN` for each required part:

| Part | Required witness |
|---|---|
| F.model | Prompt gives the cart, opposing forces, positive mass, sign direction, no other horizontal forces and usable units. |
| F.net | Learner is asked for signed net force; solution shows signed addition and result with units. |
| F.acceleration | Learner is asked to derive signed acceleration; solution uses positive mass and F_net=m*a with units. |
| U.premise | Positive length, clear self-contained givens and physically coherent premise. |
| U.conversion | Learner is asked to convert mm to m; solution derives the correct number and unit. |
| U.explanation | Prompt and solution include the explanatory demand and 1000 mm = 1 m relation. |

An absent required part is NOT_MET. UNKNOWN means available evidence cannot decide it. All MET gives FULFILLED; any UNKNOWN gives UNKNOWN while retaining known misses; otherwise a mix of MET/NOT_MET gives PARTIAL, and no MET gives NOT_FULFILLED. These summarize **content only**. A correct final acceleration without the net-force decision, or a correct metre value without the factor explanation, does not fulfill that profile. Different wording or numbers alone cannot establish independent generation.

## Uncertainty, return and continuation

If BP-1 is missing, unreadable or has a different hash, record the attempted access and observed mismatch; do not substitute another revision. Report prior relevant exposure and limit the clean-context claim. Preserve useful unaffected profile work as PARTIAL if feasible. If Python is unavailable, derive by hand and mark only that tool check NOT_RUN.

Return the two artifact locators and their actual file-byte SHA-256 values, with this exact assignment/map identity and the binding below. In `native-report.md` record actual input access/revisions, derivation and prior exposure, tool attempts/results, the SELF-ASSESSED part table, and `COMPLETE`, `PARTIAL`, `BLOCKED` or `NOT_RUN` for this bounded bundle. For a block, state attempt → observed restriction → affected part → next feasible action. COMPLETE does not accept the pilot. Do not invent executed checks or assess a nonexistent learner.

Oracle receives the artifacts and chooses the separately assessed T-ASSESS continuation; do not perform or dispatch it yourself. Preserve this issued file unchanged.

Canonical map content SHA-256: `b3e8bd62c71a32e760b6da7687cac1dda707f7001617fcd086468a5f18f98fe2` (sorted compact UTF-8 JSON; not source authentication).
Exact native binding to copy into the return (content hashes bind planning records; they do not prove execution):

```json
{
  "intent_id": "INTENT-BP1-PILOT",
  "intent_revision": 1,
  "intent_sha256": "aa9025cb19ac3fe4927cbb525a31f15be8d2533bfa9a051a6e4ac662c306d0c5",
  "plan_id": "PLAN-BP1-PILOT",
  "plan_revision": 1,
  "plan_sha256": "a756175be35b6bb9988b227514870c6f0dd560096690c7f90efca8eb3dc3c491",
  "nudge_id": "A-GENERATE",
  "nudge_sha256": "1fcf797407dd8a116b2eeaa978ae30d94c141d034c5ab1c7277f0c86fce13b03",
  "participant_id": "P-PRODUCER"
}
```

## Allowed blueprint — verbatim BP-1

# Allowed blueprint — revision BP-1
Produce two short self-contained physics exercises under an explicitly stipulated model, one per profile. Give correct source-grounded solutions. Keep conceptual validity distinct from actual learner understanding.

F: A cart experiences two opposing horizontal forces. Ask the learner to identify signed net force, then derive signed acceleration from positive mass using F_net=m*a. Stipulate no other horizontal forces and a sign direction; include units. Both decisions are required.

U: Ask the learner to convert a positive length from millimetres to metres and explain the factor 1000. Give the unit relation 1000 mm = 1 m. Avoid a misleading physical premise. Both conversion and explanatory relation are required.

No particular benchmark setting or number is stipulated here. Use clear invented settings and values. This is a synthetic authoring exercise, not a syllabus or learner record.
