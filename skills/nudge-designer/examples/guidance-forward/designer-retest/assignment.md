# Assignment: establish the ordinary-pointer failure boundary for B

## Purpose

The Owner needs an ordinary pointer selection of B to make selected state, header and details all B, while retaining keyboard success. Produce evidence that locates the first divergence on that real interaction path so a subsequent repair can address the observed cause. The supplied reports establish neither the pointer event route nor the selected-state timeline; the handover's “overlay confirmed” conclusion is therefore unsupported.

## One bounded task

Return one browser diagnostic report for candidate UI-C7, using GUIDED support with the core, UI, logic and quantitative methods below. Reuse the existing hit/state instrumentation where available. This assignment is diagnosis only.

1. Identify the browser entrypoint and the actual candidate/build being exercised. Record the URL, available build identity, viewport, device-pixel ratio, scroll position and current B rectangle. Distinguish an identified UI-C7 candidate from an unidentified page or deployment. Do not silently substitute another build.
2. Resolve the coordinate frames before testing. In the supplied geometry, B occupies CSS x=100–180, y=200–240, with CSS center (140,220). The 2000×1400 screenshot represents the 1000×700 CSS viewport at 2×, so that center is image pixel (280,440). The prior `elementsFromPoint(280,440)` call used CSS coordinates outside that supplied B rectangle. Its glass-layer result cannot establish interception of a pointer directed at B. These are derivations from the receipt, not fresh browser observations. Remeasure in the actual browser; do not reuse the old point after layout or viewport changes.
3. Establish and record a baseline through ordinary UI actions, preferably A selected with header/details A if available. Predict which event route and state sequence would distinguish interception from a later state/details failure. Then select B using the browser's ordinary pointer action. Do not substitute `buttonB.click()`, keyboard activation or direct state manipulation for this attempt.
4. Capture the actual native pointer location in viewport CSS coordinates, pointer/click event targets and propagation path, and time-ordered observations of selected state, header and details from before the action through its updates. Sample `elementsFromPoint` at that same CSS point with the timing recorded. Note whether an event target is a descendant of B. Preserve a screenshot tied to the trace. Record missing instrumentation instead of inferring internal state from the header or details.
5. From a comparable ordinary-UI baseline, exercise keyboard selection of B and record its selected state/header/details result. This is the preserved-behavior contrast, not evidence that the pointer path works. Use the paired observations to identify the earliest supported divergence, or return an inconclusive diagnosis with the missing discriminator.

## Authoritative inputs

The owning raw source is [case.md](case.md), read for this assignment. Its original conditions are: “ordinary pointer selection of B must make selected state, header and details all B; retain keyboard success.” UI-C7 is the supplied candidate; deployment is UNKNOWN.

Treat the DOM-click success, keyboard receipt, screenshot showing header B/details A, geometry receipt, prior glass-layer sample and handover as supplied observations/reports, not fresh execution. No actual native pointer trace was supplied. The screenshot alone does not establish the event target, selected state or causal order. No candidate URL, source artifact or native report format is provided here.

## Boundaries

Use the browser and existing observational instrumentation when available. Do not change product code, CSS, pointer-events behavior, deployment or external records. In particular, do not implement the handover's proposed overlay repair. Reserve repair selection and integrated acceptance for reconciliation against the returned evidence.

The worker is supplied as able to use a browser later; browser availability, candidate access and instrumentation access have not been tested. Worker qualification and host model/reasoning configuration remain UNKNOWN. Record fresh observations and their source; a role title does not establish capability.

## Success criteria

The report makes one actual ordinary-pointer attempt reproducible and links its true CSS point, event route and state/header/details sequence to the observed candidate identity. It includes the keyboard contrast and separates observed results from inference.

The evidence must be able to change the diagnosis. For example, a pointer event routed to B followed by selected state/header B but details A weakens an overlay-only explanation and locates a downstream divergence. An event intercepted elsewhere at the actual B point supports investigating routing, subject to the captured timeline. A glass hit at the old unrelated CSS point supports neither conclusion. If the inconsistency does not reproduce, report the actual trace and remaining limits; do not declare the Owner outcome accepted.

## Uncertainty handling

If UI-C7 cannot be located or identified, record the attempted access and observed restriction. Do not claim execution against UI-C7; request the specific missing entrypoint/build identifier in the return. If internal state or event timing is inaccessible, collect the available native pointer/screenshot and keyboard evidence, name exactly which conclusion remains blocked, and identify the smallest missing observation needed. Useful independent work remains the coordinate derivation, instrumentation-readiness inventory and trace plan. No repair depends solely on an unobserved cause.

## Evidence and continuation

Return the single diagnostic report in the project's native reporting format if one is available; otherwise use concise Markdown with candidate identity, attempts, coordinate mapping, linked trace/screenshots, expected-versus-observed outcomes, conclusion and execution limits. Mark supplied reports, derived geometry, freshly executed observations and unrun checks distinctly. Do not invent artifact paths or fill missing state with guesses.

Return when the trace supports a bounded diagnosis or a specific restriction prevents the next discriminating observation. State the next feasible diagnostic or repair proposal justified by that result. Ordinary-pointer correctness, retained keyboard behavior after any future repair and the deployment outcome remain unresolved until directly checked. This assignment has not executed a browser test or authorized a product change.
