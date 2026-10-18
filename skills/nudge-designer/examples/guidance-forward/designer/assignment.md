# UI-C7: trace ordinary pointer selection of B

## Purpose

The Owner requires: “ordinary pointer selection of B must make selected state, header and details all B; retain keyboard success.” This assignment supplies the missing evidence needed to choose a repair while preserving that outcome.

Decision basis: a supplied screenshot reports header B/details A after an ordinary pointer attempt, but the actual pointer point, event target and state timeline are missing. Programmatic and keyboard successes establish useful contrasts; they do not establish native pointer success. The earlier glass-layer finding may have sampled a different point. Diagnose the interaction before choosing a CSS or state repair.

## One bounded task

Return one browser diagnostic report for an ordinary pointer selection of B on an identified UI-C7 candidate, with a correlated hit/event/state/header/details trace and a keyboard contrast. Use **GUIDED** support: `core` + `ui` + `logic`, with coordinate reasoning from `quantitative`. No repair is assigned.

Use this method:

1. Record the URL, observable build/candidate identity, viewport in CSS pixels, device pixel ratio, scroll position, screenshot image size and B's current viewport rectangle. Distinguish the observed candidate from the deployed product. Verify the browser tool's coordinate convention; do not infer it from screenshot dimensions.
2. Before acting, state the predicted B center and why the old hit test may not identify B's native target. With the supplied geometry, B's center is `(100 + 80/2, 200 + 40/2) = (140, 220)` CSS pixels. Direct viewport-to-image scaling at the supplied dimensions would put it at `(280, 440)` image pixels; verify that capture mapping rather than assuming no cropping or other transforms. Calling `elementsFromPoint(280,440)` uses CSS pixels and probes a different location. Re-measure if the current geometry differs; devicePixelRatio alone does not establish every capture/tool transform.
3. Reuse the existing hit/state instrumentation in a diagnostic session. Establish and record an A baseline for selected state, header and details using the app's ordinary controls. Perform an actual browser/native pointer action inside B, using the tool's verified coordinate convention. Do not substitute `buttonB.click()`, keyboard activation or a synthetic DOM event for this attempt.
4. Record the actual event `clientX/clientY`, pointerdown/up/click targets and available event paths, plus `elementsFromPoint` at that same viewport point. Correlate these with selected state, header and details before the action, through relevant transitions and at the app's observable completion/settled state. Include evidence that B's handler ran if the existing instrumentation exposes it. Keep timestamps/order and interaction identity sufficient to connect the records. Capture the mismatch if it occurs. Record normal loading separately; do not invent a timeout or acceptance tolerance.
5. From an equivalent recorded baseline, exercise the ordinary keyboard path to B and capture the same outcome triple. Preserve the supplied DOM-click receipt as historical contrast; rerunning it is optional and cannot replace the pointer trace.
6. Explain which links the observations establish: the pointer reached B, B's action updated selection, and header/details reflected that selection. If B receives the native action and selection/header become B while details remain A, the evidence redirects investigation toward downstream state/render ordering. If the actual point hits glass and B's action is not reached, interception is supported for that attempt; a glass hit alone does not prove the entire mismatch's cause. Leave other explanations open when the trace cannot discriminate them.

## Authoritative inputs

- **READ_THIS_RUN:** `case.md` in this directory, the owning synthetic case. Preserve it unchanged. Candidate identity is **UI-C7, supplied; deployment UNKNOWN**.
- **SUPPLIED, underlying artifacts NOT_INSPECTED by this Designer:** `buttonB.click()` changed state/header/details to B; the keyboard receipt also says B; a screenshot after an ordinary pointer attempt shows header B/details A. The screenshot supplies no event target or state timeline.
- **SUPPLIED geometry:** viewport `1000x700 CSS px`; `devicePixelRatio 2`; screenshot `2000x1400 image px`; B rectangle `x=100,y=200,width=80,height=40` in CSS pixels.
- **SUPPLIED diagnostic/handover:** `elementsFromPoint(280,440)` in CSS pixels found glass and prompted a pointer-events proposal. No actual native pointer point or trace is supplied. The handover says “overlay confirmed; patch CSS now.” Treat that as an unsupported causal conclusion and proposed action, not authority to patch.
- **SUPPLIED capability:** the next worker can use a browser later and may reuse existing hit/state instrumentation. Actual session access, app/source locations and instrumentation interface are not supplied here.

## Boundaries

Perform browser observation and ordinary interactions within the later worker's authorized diagnostic session. Reuse existing instrumentation without product changes. Do not edit CSS, handlers, state logic or deployment; do not publish or make external writes. Preserve keyboard behavior and all original conditions. Reserve repair selection and implementation for a continuation based on the returned evidence and actual authority.

This Designer only read sources and drafted this assignment. No browser action, screenshot inspection, runtime test or product change occurred here. Designer and future worker host model/reasoning configuration and participant qualification remain **UNKNOWN**; role names and support profiles establish neither.

## Success criteria

The report identifies its tested surface and contains a reproducible native pointer attempt whose actual point, target/path and state/header/details transitions are correlated. The keyboard contrast reports its actual outcome. Clearly distinguish supplied reports, calculated coordinates and newly executed evidence.

The meaningful contrary case is a native action demonstrably reaching B while header B/details A persists: that weakens interception as the explanation for that attempt and makes downstream behavior the next question. Conversely, failure to reach B at the actual native point supports investigating hit routing. If all three become B, report the tested conditions and non-reproduction; do not claim the supplied failure was repaired or the deployed product accepted.

## Uncertainty handling

If UI-C7 cannot be identified, do not present another build as its reproduction. Record the inspected URL/build, the missing identity evidence and which conclusions remain conditional. Deployment identity blocks deployed-product acceptance, not candidate diagnostics.

If browser access or instrumentation is unavailable, return the attempted access, observed restriction and affected evidence. Continue feasible independent work: document accessible identity/geometry, verify coordinate arithmetic and tool conventions, inspect available baseline/keyboard behavior, or specify the exact missing trace hooks. Missing internal state evidence prevents a claim that the full triple passed; report observable header/details evidence separately. Do not fabricate a native point or infer hidden state from the header.

Return when the diagnostic report can distinguish the causal links or identify the precise missing evidence. Contradictory geometry, unreliable completion timing or inaccessible traces warrant a bounded unresolved finding, not a speculative patch.

## Evidence and continuation

Use the worker's existing native reporting format; none is supplied, so a concise Markdown report is sufficient. Include artifact references, tested identity/conditions, attempted actions, the coordinate calculation, actual ordered trace, pointer and keyboard results, conclusion with its decisive evidence, and execution limits. Keep the supplied records and this brief intact.

The next eligible action is evidence-dependent: investigate hit routing if the actual native trace supports interception; investigate downstream state/render ordering if B is reached but details diverge; or improve reproduction conditions/trace coverage when unresolved. Any repair remains a separate assignment. The parent outcome—ordinary pointer selection yielding B across state/header/details while retaining keyboard success—remains unaccepted until actually demonstrated on the relevant identified surface; deployment remains a separate unknown.
