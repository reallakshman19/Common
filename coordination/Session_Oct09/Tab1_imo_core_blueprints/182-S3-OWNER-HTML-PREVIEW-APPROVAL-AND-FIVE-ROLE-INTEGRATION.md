# 182-S3 | Owner HTML preview approval; integrated five-Core TEST-only draft

2026-10-12 | chat=6acc408a | Tab1 | issue Grade9v3.5 #182 | aim=v2.1.0 label_sha=adb005e | outcomes O1/O3 technical | authority-bound result, no release

**Outcome: O1. For the user:** Owner saw direct TEST Core1/Core2B HTML and candidate golden links at 2026-10-12T06:37Z and replied at 2026-10-12T06:56:34Z **“ok proceed, approved”**. This is positive Owner **shown-HTML preview approval to proceed**, limited to the **exact #187 preview** and not an accepted QRT cell, decision about the Core2A H3 protected move, goldens for other pages, A4 print, real learner success, merge or release. It was recorded on [issue #182 #6119344478](https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6119344478).

**Proof:** [draft PR #188](https://github.com/reallakshman19/Grade9v3.5/pull/188) at exact unmerged head `f87d2f627e3f05476d39fb04d7f26e453661dc68`, scoped hosted [five-role CI run 38215683516](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516) **SUCCESS (17/17 focused tests)**, action artifact `11732117118` downloaded independently for bytes/Chromium checks.

## Authorization and content boundary

- Owner preview approval original #187 Core1 HTML SHA256 `605c57fe7fff8b0f128ad41ef813f8db2717f603cfc7793545ded401330d578f`; original Core2B HTML SHA256 `d26f325e1f48dd8a4f938cfca7ccd59d8f380a8ab0aa420fc456da75e48ef231`; same head #187 `c55c9d927c09a4dfdb45eba5d038983e0f562275`. These are **not** the new integrated exact-head page bytes.
- Original #186 Core1A fix head `ef3d3e2dd7055d4d89d8aa154a861be2f37e11e1` remains DRAFT, #187 remains DRAFT; main remains unmodified by this work. Both previous drafts started from main `778eb35a70517a46108ad0a5dc01dfc89f61c0e3`. `#188` starts from #187 and overlays the exact #186 corrections, **not a merge**.
- Registered blueprints `BP-CORE1-ORIENTATION@1.1.0`, `BP-CORE1A-CONSTRUCTION@1.8.0`, `BP-CORE1B-RECONSTRUCTION@1.1.0`, `BP-CORE2A-SUPPORTED-APPLICATION@1.1.0`, `BP-CORE2B-TRANSFER@1.1.0` **unchanged**. Sole renderer `Shared/tools/render_core.py` **unchanged**. No authentic `CORE2` exam source, public route, source rights, shared printer or QRT registry writes.
- PR #188 original authored `TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json` blob **`002fc44d1038ed5628f5121d7a5d95072b867a3a`** (exact #186 fix, still **two** questions). Stage SVG blob **`b8f54b89706eaba84b2e631458c87360711c32be`** (exact #186 safe stage1 accessibility description). Core1A maturity tests blob **`d29c3a7527a42a8d820284891ef2305ed1b91263`** (exact #186 two regressions). Isolated authored Core2B snapshot `TEST/imo-research/pilots/imo182-core2b-transfer-pilot.v1.json` blob **`cd5ef962f47808a05cfebec3a8a4f836ef0695cf`** preserves three authored questions and carries the same no-premature-four-factor-method QUICK_CHECK correction.
- New `TEST/products/imo-182-five-core-integrated-review.manifest.json`: one governed package snapshot; `output_roles=[CORE1,CORE1A,CORE1B,CORE2A,CORE2B]`, `core2=[]`, original Core1B data not overwritten or remodeled. A first CI run rejected an invalid coverage note keyed as an omitted record; field removed with no learner-content change. Final successful head `f87d2f627e3f05476d39fb04d7f26e453661dc68`.

## One-head actual PAGES artifact, exact hosted digest

Existing renderer `render_core/2`, `PAGES` mode, `held_to=REFERENCE`, `gaps=[]`, `output_roles=[CORE1,CORE1A,CORE1B,CORE2A,CORE2B]`, full page digest `ad02fef42f0d505a`. `draft=false` in render receipt means **no renderer depth gaps only**; the GitHub PR is **DRAFT** and nothing is accepted for production. Same-hosted run produces old T6/T7 isolated comparators and candidate `G-MATH-LINEAR-CONSTRAINT` role HTML for golden method comparison.

| Integrated exact-head artifact | Actual SHA256 verified against hosted `imo182-evidence.json` |
| --- | --- |
| Core1 `build/imo182-five-core/core1.html` | `f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e` |
| Core1A `core1a.html` | `c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004` |
| Core1B `core1b.html` | `3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562` |
| Core2A `core2a.html` | `e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777` |
| Core2B `core2b.html` | `91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39` |
| `index.html` | `9fb37b2fe896481c88dc7aaf939fb0cd4235900f8051fe0e065b9db5be32513f` |

All six generated files were **recovered from exact-head CI artifact `11732117118`**, SHA256-compared to the artifact receipt, 6/6 correct (12/12 across original Core1/Core2B comparator products and five-role output including indices); no invented public URL. Golden semantic T14/T09 compare from candidate generated fixture; preservation T06/T10/T12 and Core1A T02/T03/T11 technical probes remain Owner unblessed. No pixel/perceptual golden guarantee claimed.

## Tests and actual browser / a11y observation

- **Hosted [38215683516](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516) SUCCESS**, 17/17 `python -m unittest tests.imo_182_core1_core2b_golden tests.test_core1a_renderer_maturity -v` independent tests; 9 Core1/Core2B/integrated checks + 8 Core1A maturity tests, including exact carried W02 SVG and QUICK_CHECK regressions. Existing original grade 1A and grade 1B targeted hosted workflows were triggered on same SHA and separately passed.
- Actual rendered HTML from this **one SHA** loaded in local headless Chromium with `page.set_content` (because local `file://` navigation was blocked by container browser policy; no hosted public browse). Core1A/Core1B/Core2A/Core2B each: protected answer `details` `locked=true,open=false,payload empty` initially; premature summary click blocked; blank answer commit blocked; a nonblank written response unlocks answer while retaining explicit manual summary disclosure; answer materializes after summary, with no page JS errors. All **four role probes PASS**, not four independent learner trials. Actual SVG `<desc>` on initial Core1A now names **only stage-one parity**, three SVG stage groups retained.
- H3 in Core2A is **still pre-attempt requestable** and may disclose D2 connection; local gates passing does **not** absolve H3. `D-182-2-H3` remains **pending Owner academic decision**.
- Other PR-wide checks at last observation: guardrails and canonical-assurance were still IN_PROGRESS; predecessor PR #187 had both red. **Never call #188 whole-PR CI green without explicit evidence.**

## Outcome and next decisions

**Result:** Owner-preview-approved original Core1/Core2B exact HTML recorded; consolidated authored TEST five-role integration proven on one hosted head, with no registry/renderer/product deployment changes. **This new changed-byte preview itself is not automatically Owner visually accepted**. O1 academic/golden and QRT O2 decisions remain open; QRT acceptance **0/28**; real learner outcomes/print A4 not measured.

**Owner next decisions, not assumed from “approved”:** decide `D-182-2-H3` based on exact H3 wording and D2 learner-owned W; assign independent academic reviewer/accept or reclassify named QRT per page; decide whether integrated #188 exact HTML requires new visual/golden review; authorize integration merge/release explicitly and reconcile red PR-wide CI first; A4 print remains parked with shared-printer owner. Until then, **no merge, source-admission, registry version bump, QRT acceptance or release**.
