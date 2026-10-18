"""RED-only inert score verifier: never qualifies a claim."""

def recompute(criteria, report, before, after, diff):
    return {"qualified": False, "score": (0, 0), "claim_class": "UNKNOWN", "owner_accepted": False}
