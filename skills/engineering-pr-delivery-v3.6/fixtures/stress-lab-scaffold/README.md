# relay-v36-stress-lab

> **Disposable Integration Testing Lab for Engineering PR Delivery v3.6**  
> **Controlling Proposal:** [reallakshman19/Common#355](https://github.com/reallakshman19/Common/pull/355)  
> **Governing Sticky Label:** `relay/AIM/V36-STRESS.yaml` (Change Card `CP-V36-STRESS-01`)  
> **Baseline Source:** Pinned `skills/engineering-pr-delivery-v3.6` (`bd8ee38`)  

---

## Strict Isolation Notice
This repository is a dedicated, disposable integration testing lab authorized exclusively for full-scale stress testing (`V36-STRESS-PLAN-01`).

- **Target Workload:** 300 child issues, 600 evidence cases, 20 pull requests, up to 8 concurrent local workers.
- **Progress Boundaries:** Controlling Parent Issue #1 maintains a strictly bounded denominator of 6 stages (`E0/6` to `E6/6`). Workload Parent Issue #8 benchmarks 300 decomposed tasks.
- **Safety Guarantee:** Zero mutations or writes permitted against `reallakshman19/Common`, `reallakshman19/relay-v36-e2e-lab`, or existing production repositories.
