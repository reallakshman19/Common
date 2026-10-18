"""Strict CRITERIA v1 declaration reader for Owner-frozen source clauses.

Reports *declared* source coverage, not independent proof that paraphrased
source words exactly match a remote issue. No network, approvals or writes.
"""
import re

# Shared by CRITERIA and SELF-CHECK: comma belongs to source authority.
SOURCE_PATTERN = r"#[1-9]\d* [^·\n]+"
HEADER = re.compile(
    r"CRITERIA v1 · (?P<version>[^·\n]+) · (?P<freeze>[^·\n]+) · source: "
    r"(?P<source>" + SOURCE_PATTERN + r")"
)
ROW = re.compile(r"(?P<id>(?:AC|K|J)[1-9]\d*) (?P<kind>MUST|CONSTRAINT|JUDGMENT) (?P<words>.+?) → (?P<measure>.+)")
SUMMARY = re.compile(r"Criteria: (?P<n>\d+) \((?P<m>\d+) MUST · (?P<c>\d+) CONSTRAINT · (?P<j>\d+) JUDGMENT\) · source coverage: (?P<coverage>.+)")


def parse_criteria_v1(body):
    if not isinstance(body, str) or len(body) > 200000:
        raise ValueError("CRITERIA must be bounded UTF-8 text")
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if len(lines) < 3:
        raise ValueError("missing CRITERIA header, source, rows or summary")
    header = HEADER.fullmatch(lines[0])
    summary = SUMMARY.fullmatch(lines[-1])
    if not header or not summary or not header["source"].strip():
        raise ValueError("missing frozen header, source authority or summary")
    clauses = {}
    types = {"MUST": 0, "CONSTRAINT": 0, "JUDGMENT": 0}
    for line in lines[1:-1]:
        match = ROW.fullmatch(line)
        if not match:
            raise ValueError("criterion requires ID, type, source words and measure")
        cid, kind, words, measure = (match["id"], match["kind"], match["words"], match["measure"])
        if cid in clauses:
            raise ValueError("duplicate criterion " + cid)
        if (not words.strip() or not measure.strip()
                or words.count('"') not in (0, 2)):
            raise ValueError("untraceable source words or missing measure")
        if cid.startswith("AC") and (not words.startswith('"') or
                                      not re.search(r'^"[^"]+"$', words)):
            raise ValueError("AC source words must be frozen in explicit quotation")
        if any(char in measure for char in ("<WORK>", "<SHA>")):
            raise ValueError("unresolved measurement placeholder")
        expected_kind = "MUST" if cid.startswith("AC") else (
            "CONSTRAINT" if cid.startswith("K") else "JUDGMENT")
        if kind != expected_kind:
            raise ValueError("criterion class inconsistent with ID")
        clauses[cid] = {"type": kind, "source_words": words.strip('"'), "measure": measure}
        types[kind] += 1
    count = len(clauses)
    if (count != int(summary["n"]) or types !=
            {"MUST": int(summary["m"]), "CONSTRAINT": int(summary["c"]),
             "JUDGMENT": int(summary["j"])}):
        raise ValueError("criterion totals mismatch")
    for prefix, quantity in (("AC", types["MUST"]), ("K", types["CONSTRAINT"]),
                             ("J", types["JUDGMENT"])):
        if {key for key in clauses if key.startswith(prefix)} != {
                f"{prefix}{n}" for n in range(1, quantity + 1)}:
            raise ValueError("criterion IDs must be complete and contiguous")
    return {"version": header["version"].strip(), "source": header["source"],
            "criteria": clauses, "types": types,
            "source_coverage": f"{count}/{count}",
            "coverage_basis": "declared source words; external fidelity requires Owner review"}
