# GC-PW/1.0 A0 SOURCE INPUT CENSUS — consolidated Tab3+Tab4 (2026-10-11)

## Exact custody
Principal issue #212 r5 https://github.com/reallakshman19/3D_Converters/issues/212#issuecomment-6105942722, task evidence https://github.com/reallakshman19/3D_Converters/issues/212#issuecomment-6106257785.
Draft integrated PR #216 current EXACT head `db6be834f106111b923ce54476e5ca4b242b875c`, base #215 `d1eb5d5dfdeb34f88c90768abfcfca8068a4471e`, **not merged/deployed**.
Two production-safe source-only commits: `41c26905c51706bccc869db130e16194b98f6423` and `db6be834f106111b923ce54476e5ca4b242b875c`, adding/editing ONLY `scripts/xml-cii-gcpw-a0-master-source-census.py` and `.github/workflows/lfj-212-gcpw-a0-master-census.yml`. All original master bytes, index serializer, C05, Preview, Weight, Material, CII, protected golden unchanged.
Exact-head A0 CI https://github.com/reallakshman19/3D_Converters/actions/runs/38118193100 SUCCESS, receipt artifact https://github.com/reallakshman19/3D_Converters/actions/runs/38118193100/artifacts/11693782470 .
Full exact-head actions 40 TERMINAL = 25 SUCCESS and 15 historic C05 FAILURE; #216 F01 reviewer `38118196668`, F02 actual real Firstpass source/CSV Chromium `38118196687`, T6 source guards `38118196684`, A0 `38118196693` SUCCESS on same final HEAD. Independent #141 NOT ACCEPTED.

## Full content SHA-256 and independently parsed source counts
| Checked-in original source | Byte size | SHA256 of content | Observed |
|---|---:|---|---|
| `docs/Masters/Piping_class_master.json` | 2439490 | `74997209ffbbf4c5e1eacc9948ec89a5e2f59ad87cc3dd7cfca6d24166d7fab1` | 10,699 JSON records: matches original scale |
| `docs/Masters/PCF_MAT_MAP.TXT` | 6639 | `84b2e94488e5bceb135557a9272b0a75a87d9a53c46783865373b18f7c4dda29` | 383 material code records after 2019 version |
| `docs/Masters/wtValveweights.json` | 417192 | `c6dc8cb1347d7250666979eb64a7e2a9e56dce216aeecaf4dc38b165137b6ada` | 1,595 JSON Valve Weight rows |
| `docs/Masters/ImportedRawLineListLL.xlsx` | 50224 | `a73d86cfb8a69ed0aad7e4656dd7a8d62075ffe1c3bf1bae0959601afbfdadbc` | 802 populated rows, `ImportedRawLineListLL` raw wide ID/numbered columns |
| `docs/Masters/LineDump.xlsx` | 19418 | `60d30737680e6b6f2d23bc3f9aeafb794b326cb3087d79f6d8e9902b64758fb5` | 206 populated worksheet rows, 205 after header; different Reference/Name/Type/Position layout |

Original #999 migrated current #96 GC-PW/1.0 Owner master scale **385/10699/383/1595**. The original 385 *logical* Line List count is NOT established by either tracked raw workbook; 802 or 205 physical rows cannot be treated as a verified 385-line mapped master. No heuristic filtering/renaming/replacement or golden rewriting permitted.

## Engineering disposition
SOURCE-ONLY A0 CENSUS PASS (3 counted sources match; Line List mapping/authentic Owner master unresolved). Real Owner-scale A0 browser Preview performance (time, memory, long tasks, cold/warm, four full authentic masters) NOT_RUN. No certified full physical FactRecord population, full staged source, engineeringRating/B31.3/Match-1/Match-2, CII or enriched evidence ZIP.

B1 issue #133 notified https://github.com/reallakshman19/3D_Converters/issues/133#issuecomment-6106260720; #96 architecture notified https://github.com/reallakshman19/3D_Converters/issues/96#issuecomment-6106261298. Required next: B1 Owner attests authoritative 385 logical Line List dataset *and mapping + SHA*, selected owner and zone, then native Chromium real Preview with exact source. B4 #136 writer not leased. C05 #203 D-212-2/7/8 contract adjudication unresolved, 15 CI red, DO NOT waive. Original Owner ~30MiB positive / protected independent #141 / registered public Pages remain HOLD.
