# Issue #415 — exact original source-custody runbook (NOT A PHASE)

**Scope:** The 10 original candidate files listed in `ORIGINALS_SHA256.json` were recovered in an earlier conversation execution environment. Their byte digests were recorded, but the original bytes **are not included in this draft branch**. The repository currently preserves hashes, not the binaries/source themselves.

## Recover and stage original bytes without regeneration

Place each **unaltered** file at the following directory relative to this runbook:

```text
originals/
  king_puppet_final/
    make.py
    King_Puppet_Cutting_Template_and_Parent_Appendix.pdf
    renders/page-1.png
    renders/page-2.png
  prahlada_puppet_corrected/
    build.py
    Prahlada_Complete_Puppet_Guide.pdf
    page-1.png
    page-2.png
    page-3.png
    page-4.png
```

Do **not** replace the files with a newly generated guide, OCR extract, new render, or recreated generator: a visual match is not a byte match. New alternatives must use new filenames and separate provenance.

## Verify exact bytes before and after a proposed upload

From repository root:

```bash
python3 docs/puppetry/issue-415/verify_originals.py --root docs/puppetry/issue-415/originals
python3 -m unittest discover -s docs/puppetry/issue-415/tests -v
```

The first command checks all ten SHA-256 identities against the recovered-asset manifest, distinguishes `MISSING` and `MISMATCH`, and exits with 0 only when all ten match. `--json` emits a structured receipt. Tests use synthetic bytes and **do not** substitute for original-file verification.

Once sources are available, stage them on **draft PR #416 only**, perform checksum readback from exact GitHub head (not just local files), and record:
- exact Git commit + each blob path;
- byte SHA-256 match for all ten;
- four-page Prahlada and two-page King PDF page counts, viewed preview sanity;
- ownership/provenance of the original recovered bytes, not only filename resemblance.

After byte custody, a later independent G2 may challenge dimensions, hole locations, physical movement and 1:1 print fidelity. A successful checksum has **no power** to grant design approval.

## Honest current state / ownership

- Stage 1a: **NOT_PUBLISHED / HOLD**; the checksum manifest/checker/runbook are preparation only.
- G1 actual role: **UNASSIGNED**; G2 distinct actual role: **UNASSIGNED**. GitHub repository owner is not automatically a buddy role.
- Owner-provided script: candidate archived separately; not rehearsed or approved.
- Product source parent/roadmap beyond coordination issue #415: **UNKNOWN**; do not pretend #415 is an authenticated distinct parent.
- Narasimha and pillar original designs: **NOT_DESIGNED**.
- Stage 1b and 2, Task Evidence Y, physical build and rehearsal: **NOT_RUN**.

**Only next phase once intake is genuinely complete:** render *one validated 1a*, publish/read back under existing authorization, then `1a | EXECUTION=HOLD | NEXT=G2 independently investigates and submits 1b`.

Record type: `SOURCE_CUSTODY_PREPARATION`, not `TASK_EVIDENCE` and not a BuddyRunner response.
