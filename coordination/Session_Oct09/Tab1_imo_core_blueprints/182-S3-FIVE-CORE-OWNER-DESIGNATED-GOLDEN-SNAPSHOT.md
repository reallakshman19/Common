# 182-S3 — Saved golden fixture (exact five HTML files)

Date 2026-10-12 | chat=6acc408a | Owner directive received at 07:30:37 UTC: “save this as a golden fixture , provide me github link” | aim v2.1.0 adb005e | Outcome O1 | no user/public workflow change.

**Verified GitHub fixture:** https://github.com/reallakshman19/Grade9v3.5/blob/badd51a4053792cbacad36d936569aedaadaa37a/golden/units/G-IMO-G9-FIVE-CORE-20261012/GOLDEN.md. Issue #182 receipt: https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6119932510. Draft PR #188 remains unmerged; saved branch exact head `badd51a4053792cbacad36d936569aedaadaa37a`. No release, merger, source or QRT rights were inferred.

Five exact integrated TEST HTML pages (source commit `f87d2f627e3f05476d39fb04d7f26e453661dc68`, hosted run `38215683516`, artifact `11732117118`, renderer `render_core/2`, digest `ad02fef42f0d505a`, 0 authoring depth gaps) have been saved as tracked `golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshots/{core1,core1a,core1b,core2a,core2b}.html`. Each GitHub blob SHA was independently matched to the corresponding exact source file bytes:

| Page | Frozen SHA256 | Git blob SHA |
|--|--|--|
| Core1 | `f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e` | `d297bfafc40c4882b24fb7fe291e3b5b57aac20c` |
| Core1A | `c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004` | `200f3fbc2f3bd7d848668a415411880c613790f7` |
| Core1B | `3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562` | `6be9b95314f67cd29135cdd733325d38bb2bd2de` |
| Core2A | `e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777` | `be69d9eee4f012398d16328dd71fcc1a181f52b8` |
| Core2B | `91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39` | `cb03f78d526f42a41a6ff9e9474b8a2b8d00e7fe` |

Reproducer: `manifest.json` points to pinned `records.json` (git blob `cd5ef962f47808a05cfebec3a8a4f836ef0695cf`), with five selected roles, `core2=[]`. `snapshot-lock.json` records all file hashes. Tracked `snapshots/` deliberately differs from ignored regenerated `rendered/`. `golden/INDEX.md` links this exact Owner-designated frozen fixture. Test `tests/test_imo182_owner_golden_snapshot.py` asserts snapshot bytes + pinned regeneration; workflow `.github/workflows/imo-182-core1-core2b-golden.yml` invokes it. New CI run `38219091440` is **QUEUED at recording**; do not claim green before hosted conclusion. Previously hosted source-generation CI was green 17/17.

**Precise Owner scope:** The user directed exact fixture preservation. This does **not** accept an independent academic QRT mapping (0/28), decide `D-182-2-H3`, bless changed source rights, unblock parked A4 printer, merge PR #188 or publish a live product. Frozen exact HTML is a designated comparison oracle, not proof of educational effectiveness. For any future modification, write a new fixture version and separately obtain Owner academic approval and integration/merge authority.
