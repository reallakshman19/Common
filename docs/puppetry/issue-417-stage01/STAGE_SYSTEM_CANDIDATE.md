# PUPPET-415-STAGE-01 — integrated stage and pillar reveal

**Coordination:** [#415](https://github.com/reallakshman19/Common/issues/415)  
**Workpack:** [#417](https://github.com/reallakshman19/Common/issues/417)  
**Source baseline:** [draft intake PR #416](https://github.com/reallakshman19/Common/pull/416) @ 919417019f8cc22b2b348351b3acfca54472ae0a; supplied Narasimha ZIP SHA256 7a600a32f384e8a35a15c2375e586d051bce17c6e5eda9d418839ba63560fab5.  
**Authority:** ENGINEERING HYPOTHESIS. Not approved cutting dimensions. No physical test performed. BuddyRunner 1a remains HOLD, G2 not invoked.

## Governing outcome

Three-minute, four-scene Grade 4 puppet show; the same palace, throne and central pillar remain present in all scenes. King points and strikes three times, Prahlada keeps hands joined, Narasimha emerges from an opening pillar with arm down and blesses only after the puppet is clear, King retreats left. Every control has a real operator and no scenery change.

## Candidate coordinate system / dimensioned ASCII

Use x right from stage left, y up from visible baseline, and z backward away from audience, **all millimetres**. Proposed stage x=0..750, visible y=0..400, z=0..150. A separate 150 mm free zone **below y=0** must support the puppet sticks; 150 mm depth does not establish that clearance.

~~~text
FRONT (NOT TO SCALE)                          stage width 750
x0 +------------------------------------------------------+ x750
   |                  PALACE (fixed)                      |
   |                                                      |
   | KING              PILLAR             PRAHLADA       |
   | center220       x285-----465          center625       |
   |  [K]             |  [N]  |              [P]          |
   |                  +-------+                           |
 y0+------------------------------------------------------+
             opening x305..445, y15..245
             pillar outer width180, height280
             door leaves: two at 70 wide, 230 high
             BELOW baseline: free grip movement 150

TOP: z0 audience -> z20 emerged N -> z40 closed-door plane
     -> z110 open-door maximum rearward sweep
     -> z130 hidden N -> z150 rear edge/operator access
~~~ 

Pillar outer centre x375; exterior x285..465, y0..280. Opening width140 x305..445, height230 y15..245; 20 mm side posts, 15 mm lower sill, 35 mm lintel. Hinges are vertical **3D** rotation axes at x305/445, z40; leaves open BACK to 90 degrees. Do not confuse them with front-plane cardboard arm hinges.

## Inherited measurements versus novel hypotheses

Inherited candidate Narasimha arm-down width ~92 mm, body height180, raised arm horizontal width ~152–155, main stick260 with 90 mm overlap. King body 200×90, active arm approx80 mm pivot-to-tip (70 mm pivot-to-control-hole). Prahlada body160×70, rigid with joined hands and 250 mm rear stick/90 mm overlap. These have not been physically qualified.

**New values under test**: 750×400×150 stage; 180×280 pillar and 140×230 opening; z positions 20/40/110/130; Narasimha rise20; Prahlada bow15°. These are not final fabrication sizes.

## First numerical screen (rectangular envelopes; not real collision tests)

| Check | Candidate result |
|---|---|
| 140 opening − 92 N width | nominal 24 mm each side |
| ±5 mm placement and 2 mm door-edge intrusion | 17 mm nominal worst-case side margin |
| Door sweep z40→110 vs hidden N at z130 | 15 mm margin after 5 mm allowance |
| Front N z20 versus door plane z40 | 15 mm margin after allowance |
| N top y210 +20 rise vs opening y245 | 10 mm top margin after allowance |
| N stick260−90 overlap−feet y30 | 140 mm extends BELOW y=0 |
| King shoulder x250 +80 reach vs door starts x305 | nominal 25 mm reach beyond edge |
| 15° Prahlada bow toward extended blessing arm | ~15 mm worst-case horizontal gap |
| 20° bow under same model | FAIL conservative collision screen |
| Raised N arm (~152) within opening140 | FAIL; arm stays DOWN until fully in front |

Source and screen are repeatable via accompanying candidate JSON, model and tests. The model omits actual rods, pin heads, string sweep, card thickness variations, operator grip collisions and audience sightlines. **A numerical PASS cannot certify physical construction.**

## Mechanism choice — no premature final design

A: first mock-up candidate, two soft tape/fabric vertical hinges opening rearward 90°, two strings joined to one gentle pull, removable passive hold-open stop. Single pull, stop, latch and string routes **not mechanically proven**.

B: two manually opened doors and a designated helper; simpler doors, costs extra hand and must stay latched open.

C: two sliding shutters; avoids leaf sweep but introduces guide friction; defer unless hinged approaches fail.

Decision: choose the simplest option that survives five consecutive safe opening+reveal+hold trials without using an unassigned hand.

## Operator and timed cue hypothesis

A controls King's body+arm. B controls Prahlada rigid stick with one hand and the joined door pull with the other for 1:15–1:25. C holds Narasimha arm parked down, passes the body z130→20 through the doors, raises it 20 mm, then operates blessing arm in Scene 4. D narrates/provides sound. **Four distinct persons is only a candidate staffing arrangement**; availability has not been verified.

- 0:00–1:08 doors closed, King and Prahlada present; all scenes use the same pillar.
- 1:08–1:15 three knocks and roar; only decorative tremble, no unstable stage shake.
- 1:15–1:25 B opens and parks doors; C advances N arm-down, then raises body20 mm.
- 1:25–2:10 roar via voice/body; King exits LEFT behind mask; doors remain open.
- 2:10–2:32 N, fully clear of doors, raises one blessing arm.
- 2:32–3:00 Prahlada bows at most 15° candidate; final still pose. No curtain mechanism required.

## Full-size proof experiment, not final manufacture

Adult-fabricate a removable 180×280 pillar shell with 140×230 opening and two 70×230 door leaves, tape hinges, blunt strings and safe stops. Assemble temporary 750×400 backdrop, 150 depth supports and OPEN under-stage grip space. Use N 92×180 arm-down and 152-mm raised-arm envelopes initially; for final clearance replace rectangles with the *authentic* candidate cutout and rods. Use King 90×200 and Prahlada 70×160 silhouettes. Print calibration on ordinary paper and transfer to board; don't feed thick card through an office printer.

Record, with actual operators and millimetre readings:
1. M1 >=10 mm **physical** clearance to N including rods throughout opening and passage.
2. M2 5/5 consecutive smooth open/reveal/hold cycles; doors stay open for subsequent scenes.
3. M3 Hands/controls work with declared operators; no hidden extra hands or unsafe grip.
4. M4 N invisible before reveal from real audience positions.
5. M5 >=10 mm between Prahlada at 15° bow and N blessing silhouette/rods.
6. M6 King's three gestures + sound, retreat and exit without collision.
7. M7 >=140 mm free travel BELOW baseline for N stick.
8. M8 both doors open and N visible by 1:25 in a timed run.
9. M9 full 180-second rehearsal LATER, not yet performed.

Each record needs measured source version, date, count of hands/operators, PASS/FAIL/NOT_RUN, observations and correction. **Mock-up=NOT_RUN, physical acceptance=NOT_GRANTED.** First falsifier: if M1–M3 fail, revise pillar/linkage/operator design before final templates or decoration.