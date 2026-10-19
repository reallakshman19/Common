#!/usr/bin/env python3
"""Executed review witness, not a generator validator or learner trial.

Reads only this task's owner and candidate; calculations use the owner's stated
Newtonian model. Counts are whitespace tokens, so standalone equals signs count.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
raw = (ROOT / "items.json").read_bytes()
items = json.loads(raw)["items"]

hashes = {}
for rel in ["owner.md", "items.json"]:
    hashes[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

# Descriptive measurements. None of these metrics decides subject correctness.
stop = set("a an the its is of what which how happens next it and to each second points describes".split())
def words(s):
    return set(re.findall(r"[a-z]+(?:_[a-z]+)?", s.lower())) - stop
form = []
for i, item in enumerate(items):
    opts = item["options"]
    counts = {o["id"]: len(o["text"].split()) for o in opts}
    markers = {o["id"]: re.findall(r"\b(?:because|therefore|gives)\b", o["text"], re.I) for o in opts}
    overlap = {o["id"]: sorted(words(item["question"]) & words(o["text"])) for o in opts}
    max_len = max(counts.values())
    longest = [k for k,v in counts.items() if v == max_len]
    form.append({"locator": f"items[{i}] id={item['id']}",
                 "whitespace_token_counts": counts,
                 "longest_options": longest,
                 "key_unique_longest": longest == [item["answer"]],
                 "reasoning_markers": markers,
                 "question_option_content_word_overlap": overlap})

# Independent arithmetic on stated X2 givens, with right defined as positive.
# The candidate's claimed answer is compared only after calculating.
x2_mass = Fraction(3)
x2_force = Fraction(12)
x2_a = x2_force / x2_mass
assert x2_a == 4
x2_direction = "right" if x2_a > 0 else "left" if x2_a < 0 else "zero"
# X2 begins moving left: along velocity and opposite a rightward force are left.
x2_option_directions = {"A": "left", "B": "left", "C": "right"}
x2_compatible = [k for k,v in x2_option_directions.items() if v == x2_direction]
assert x2_compatible == ["C"]
assert next(i for i in items if i["id"] == "X2")["answer"] == x2_compatible[0]

# Concrete contrary conditions for X1's force-maintains-speed and increasing-a
# distractors. This instantiates the general algebra a=F/m and v=v0+(F/m)t;
# the proof that a is constant comes from fixed F and m, not sample sufficiency.
x1_samples = []
for mass, force, v0 in [(3, 6, 2), (5, 1, 3), (2, 9, 1)]:
    a = Fraction(force, mass)
    velocities = [Fraction(v0) + a*t for t in range(4)]
    increments = [velocities[j+1]-velocities[j] for j in range(3)]
    assert a > 0 and len(set(increments)) == 1
    assert increments[0] > 0
    x1_samples.append({"illustrative_only": True, "mass_kg": mass,
                       "force_N_right": force, "initial_velocity_m_per_s_right": v0,
                       "a_m_per_s2_right": str(a),
                       "velocities_at_t_0_1_2_3_s": [str(v) for v in velocities],
                       "successive_one_second_increases": [str(d) for d in increments]})

# X3's expected unit comes directly from owner.md, not option frequency.
x3_expected_unit = "newton (N)"
x3 = next(i for i in items if i["id"] == "X3")
x3_matching = [o["id"] for o in x3["options"] if o["text"] == x3_expected_unit]
assert x3_matching == ["A"] and x3["answer"] == "A"

result = {
  "execution": "Executed by reviewer; see execution.log for the captured invocation output.",
  "input_sha256": hashes,
  "form_measurements": form,
  "X1": {"general_derivation": "For constant m>0 and constant F>0 right, a=F/m>0 is constant. While v0>0 right, v(t)=v0+(F/m)t stays right for t>=0; speed rises by (F/m)*dt for each equal interval dt.",
         "expected_key_from_derivation": "B", "candidate_key": items[0]["answer"],
         "contrary_checks": x1_samples,
         "sample_limit": "Illustrative finite cases are not an exhaustive physical-model test."},
  "X2": {"mass_kg": str(x2_mass), "net_force_N_right": str(x2_force),
         "calculated_a_m_per_s2_right": str(x2_a),
         "a_direction": x2_direction, "directions_asserted_by_options": x2_option_directions,
         "compatible_options": x2_compatible, "candidate_key": next(i for i in items if i["id"] == "X2")["answer"]},
  "X3": {"source": "owner.md supplied subject basis", "expected_unit": x3_expected_unit,
         "compatible_options": x3_matching, "candidate_key": x3["answer"]},
  "limits": ["Text review and local computations only; no learner trial.",
             "The answer keys were visible when the candidate was first read.",
             "Metrics do not certify absence of every test-taking cue or learner transfer."]
}
assert items[0]["answer"] == "B"
(OUT / "check-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": "executed", "input_sha256": hashes,
                  "counts": [{"id": items[i]["id"], "counts": f["whitespace_token_counts"]} for i,f in enumerate(form)],
                  "derived_keys": {"X1": "B", "X2": x2_compatible[0], "X3": x3_matching[0]},
                  "witness": str(OUT / "check-results.json")}, indent=2))
