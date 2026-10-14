# r6 oracle verification bindings — strict data contract diagnosis, no fake admission

**UTC:** 2026-10-14, chat `6ace7d89`; issue [D1 #200](https://github.com/reallakshman19/Grade9v3.5/issues/200). **Code state:** independent [draft #238](https://github.com/reallakshman19/Grade9v3.5/pull/238) head `28511cb4b82c17f90892867cae85955fc29c21d8` unchanged. **Purpose:** make the next source-owner decision concrete without bypassing generic admission or changing public output.

## Exact provider inputs

Refetched GitHub source on #238 exact head:
- `TEST/library/imo-g9-divisibility-core1a.v1.json` Git blob `31ec1141eaea2a0f49fffafa9dd2a740620c70b0` remains research-only `subject=TEST`, `status=CANDIDATE`, `questions=[]`, **`data=[]`**, no QRT/Owner/publication claim.
- `Shared/library/package.schema.json` Git blob `a9cdf31d6ae46d00ac227791264231f05d453725`, specifically `$defs.microtopic.properties.exit_task.properties.oracle.properties.verification` has required `validator_id` and `bindings`, and `bindings` is a string-valued object. Its **description** says these map to **declared data**. `$defs.datum` requires `id,version,status,source_refs,evidence_refs,extensions,kind,value,locator,meaning`. `kind=DATUM` needs a finite numeric value plus `unit`; `kind=EQUATION` needs a restricted presentation-MathML string, not an unconstrained verbal domain/range.
- `Shared/library/intake.py` Git blob `4b4553643eb67f3921d340bf59303a01944d090e`; the exact `EXIT_ORACLE` rule takes `datum_ids={d.id for d in package.data}` and rejects every oracle `verification.bindings` target not in that set.
- Current exit oracle: `validator_id="TEST/imo-research/validate_core1a_candidate_package.py"`; `bindings` target literals:
  - `domain = positive_integer` — domain constraint, *not* a scalar governed numerical datum;
  - `divisor = 24` — a scalar divisor that could be represented as governed numeric data with correct provenance and unit convention;
  - `residue_classes = 0..23` — finite index set / quantifier, *not* a single datum;
  - `symbolic_expression = n(n+1)(n+2)(n+3)` — mathematical expression, but not itself a restricted presentation-MathML value.
  Each target is absent from `data=[]`, so generic admission can add `EXIT_ORACLE` findings even though the custom candidate verifier runs its own modular-6 and modular-24 checks.

## Why the next fix is held

This is **not merely four missing arbitrary IDs**. Changing the literal `bindings` values to invented `data` IDs would either fabricate governed evidence or misrepresent mathematical domains as scalar measurements. In particular, a `DATUM` row named `positive_integer` would be structurally wrong for a nonnumeric domain descriptor; an `EQUATION` row containing raw `n(n+1)(n+2)(n+3)` is not a schema-admitted MathML value. The source owner must distinguish **declarative validator parameters** (domain, residue cases, mathematical expression) from **bound governed data values**, and demonstrate that the canonical oracle is actually executable and mathematically adequate. Do not:
1. remove the exit oracle, declare `no_numeric_claim` when the task explicitly claims 24-divisibility, or use `held_by` to pretend a current valid oracle was tested;
2. set `bindings={}` while silently smuggling the four literal inputs into unverified extension fields merely to make generic intake return true;
3. invent four provenance records, widen canonical schema, or mark this TEST research source as `Mathematics` / `CURATED` / QRT-accepted;
4. alter the separate draft #238 or the D1 review branch #231 without a measured attributable source/contract check.

## Next owned resolution (not approved)

- First determine what the validator truly consumes. It presently computes exhaustive modular divisibility internally, not by consuming named declared data rows from the oracle `bindings`. A governed option might formalize its **explicit fixed parameters** separately from truly data-backed values, but only after source schema/validator owner defines and tests the contract. Another option is to author truly governed datum records for legitimate numerical constants and a proper symbolic-expression encoding; the domain and range still need a valid parameter language. Choose **one** coherent approach and add negative admission tests that prevent validation from becoming a no-op.
- Preserve unchanged independent proof that **every four consecutive positive integers have product divisible by 24** (two factors supply 8, at least one divisible by 3), and the existing authored Core1A parity/residue-3 route. Do not conflate an author's exhaustive modular check with learner comprehension or QRT independent academic acceptance.
- Require exact-head generic `tests/test_library.py`, custom `tests/test_imo_core1a_candidate_package.py`, source review/receipt checks, broad guardrails and canonical CI once a source-authorized correction exists.
- At this checkpoint, #238 exact-head six workflows [guardrails 38497211734](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38497211734), [canonical 38497212010](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38497212010) and four others are still **QUEUED**; zero GitHub CI PASS asserted. Review-only #223/#228/#231 scoped PASS remains on their own exact heads, broader integration FAIL. Owner QRT 0/7 D1, 0/28 global; source rights/Golden D-182-3/merge/release separate.

## Source-safe next turn

Open issue #200 and this note, verify #238 CI finished status. If not, proceed read-only on the oracle consuming code and safely propose one contract-consistent fix under the appropriate authority; do not patch global schema or public learner data by intuition.

LOG | Outcome=oracle domain/constant/range/expression data-binding conflict classified, no false datum/admission | Proof=actual #238 source and canonical schema/intake Git SHAs | Open=owner-governed parameter/data contract, queued CI, broad red checks, Owner 0/28.
