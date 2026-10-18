"""RED-only inert self-check parsers: never grant claimed criteria or scores."""

def parse_self_check_v2(body, criteria):
    return {"version": 2, "criteria": {}, "claimed_score": (0, 0), "claim": "UNKNOWN"}


def parse_compatible(body, *, task_id, issue_ref, owner_login):
    return {"version": 1, "issue": "", "claim": "UNKNOWN"}
