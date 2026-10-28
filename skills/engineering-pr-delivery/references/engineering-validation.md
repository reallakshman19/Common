# Engineering-Critical Validation

Load this reference when `CRITICALITY=ENGINEERING_CRITICAL` or `SAFETY_CRITICAL`.

## Required principles

1. Establish governing units, axes, sign/end conventions, geometry, material/property authority, and relevant code/standard basis before comparing numbers.
2. Prefer independent analytical, authoritative-reference, cross-solver, or experimentally grounded expected values.
3. Keep implementation-coupled regressions separate from independent verification.
4. Fail closed where required engineering inputs/authority are missing.
5. Isolate one mechanism at a time when practical.
6. Record provenance for every benchmark and expected value.

## FEA / structural / piping solver work

Where applicable require:

- six-DOF residual/equilibrium checks;
- element/member free-body cuts;
- raw end-action recovery such as `q = K u - f_fixed - f_initial`;
- local/global axis verification;
- unit verification;
- DOF and end-I/end-J ordering/sign verification;
- transformation and moment-transport verification;
- trace from at least one failed reported row back to the raw solver quantity;
- independent benchmark or analytical solution;
- convergence/sensitivity where discretization is relevant.

Do not change stiffness/load assembly merely to correct a downstream recovery/reporting defect.

## Piping-specific mechanisms

When relevant isolate B31J flexibility, bend ovalization, pressure stiffening, translational/rotational Bourdon effects, pressure thrust, bend tangent/end conventions, SIF use versus flexibility use, pressure area, wall/geometry/orientation, and units through single-factor tests and predicted sensitive cases.

## Authority promotion

A usable implementation does not automatically gain engineering/screening/design authority. Record calculation state, qualification state, authority state, and missing qualification evidence separately.
