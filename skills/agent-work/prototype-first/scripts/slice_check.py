#!/usr/bin/env python3
"""Check prototype-first slice cards (schema v1). Standard library only.

Usage: python slice_check.py CARD.json [CARD.json ...]
Prints "OK <file>" or one line per error, and exits 1 when any card fails.
"""
import json
import re
import sys
from pathlib import Path

STATES = ("written", "building", "runnable", "tried", "accepted", "hardened", "verified")
CHECKS = ("none", "self", "independent")
VERDICTS = ("works", "gaps", "fails")
PROBE_KEYS = ("code", "downloads", "read_attachments", "browser", "repo_push")
PROBE_VALUES = ("yes", "no", "unknown")
WBS = re.compile(r"[1-9][0-9]{0,2}(\.[1-9][0-9]{0,2}){0,3}")
SLICE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,40}")
SHA40 = re.compile(r"[0-9a-f]{40}")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
# Chat and storage links are private: a card names files, never links to them.
PRIVATE = re.compile(r"chatgpt\.com|chat\.openai\.com|claude\.ai|(drive|docs|drive\.usercontent)\.google\.com"
                     r"|onedrive\.live\.com|1drv\.ms|sharepoint\.com|dropbox\.com", re.I)


def reached(state, other):
    """True when `state` is `other` or later in the lifecycle."""
    return STATES.index(state) >= STATES.index(other)


def strings(obj, path=""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from strings(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from strings(v, f"{path}[{i}]")


def text(v):
    return isinstance(v, str) and bool(v.strip())


def https(v):
    """A link field: public GitHub only, so no private host can pass."""
    return isinstance(v, str) and v.startswith("https://github.com/") and not any(c.isspace() for c in v)


def check(card):
    """Return the errors of one card; an empty list means it passes."""
    if not isinstance(card, dict):
        return ["card: must be a JSON object"]
    e = []
    for path, s in strings(card):
        if PRIVATE.search(s):
            e.append(f"{path}: private link; name the file and its folder instead")

    for key in ("user_can", "user", "done_when"):
        if not text(card.get(key)):
            e.append(f"{key}: required")
    if not (isinstance(card.get("slice"), str) and SLICE.fullmatch(card["slice"])):
        e.append("slice: required, letters, digits, '.', '_' or '-'")
    if not (isinstance(card.get("wbs"), str) and WBS.fullmatch(card["wbs"])):
        e.append("wbs: required, like 2 or 1.3 (no zero parts)")
    state = card.get("state")
    if state not in STATES:
        e.append(f"state: one of {', '.join(STATES)}")
        state = "written"
    check_level = card.get("check")
    if check_level not in CHECKS:
        e.append(f"check: one of {', '.join(CHECKS)}")
    if check_level == "independent" and not text(card.get("why_check")):
        e.append("why_check: required when check is independent")
    tb = card.get("timebox_h")
    if isinstance(tb, bool) or not isinstance(tb, (int, float)) or not 0 < tb <= 40:
        e.append("timebox_h: a number of hours above 0 and at most 40")
    keeps = card.get("keeps")
    if not (isinstance(keeps, list) and all(text(k) for k in keeps)):
        e.append("keeps: required list of earlier benchmarks (may be empty)")

    inputs = card.get("real_inputs")
    if not (isinstance(inputs, list) and inputs):
        e.append("real_inputs: at least one real input; synthetic data never replaces it")
    else:
        for i, item in enumerate(inputs):
            if not (isinstance(item, dict) and text(item.get("name")) and text(item.get("where"))):
                e.append(f"real_inputs[{i}]: needs name and where")
            elif re.search(r"https?://", item["where"], re.I):
                e.append(f"real_inputs[{i}].where: a folder or 'attached in chat', not a link")

    for key in ("builds_on", "prepares_for"):
        links = card.get(key)
        if links is None:
            continue
        if not isinstance(links, list):
            e.append(f"{key}: a list of slice and what")
            continue
        for i, link in enumerate(links):
            if not (isinstance(link, dict) and text(link.get("slice")) and text(link.get("what"))):
                e.append(f"{key}[{i}]: needs slice and what")

    if reached(state, "building"):
        probe = card.get("probe")
        if not isinstance(probe, dict):
            e.append("probe: required once a builder is working (send the capability probe first)")
        else:
            for k in PROBE_KEYS:
                if probe.get(k) not in PROBE_VALUES:
                    e.append(f"probe.{k}: yes, no or unknown")
    if reached(state, "runnable"):
        if not text(card.get("runnable")):
            e.append("runnable: required from state runnable (one command or one URL)")
        demo = card.get("demo")
        if not (isinstance(demo, list) and 3 <= len(demo) <= 6 and all(text(d) for d in demo)):
            e.append("demo: 3 to 6 steps the user performs, required from state runnable")
    if reached(state, "tried"):
        use = card.get("after_use")
        if not isinstance(use, dict):
            e.append("after_use: required from state tried (the user's own run)")
        else:
            for k in ("tried_at", "by", "can_do_today"):
                if not text(use.get(k)):
                    e.append(f"after_use.{k}: required")
            if use.get("verdict") not in VERDICTS:
                e.append(f"after_use.verdict: one of {', '.join(VERDICTS)}")
            if use.get("verdict") == "gaps" and not (isinstance(use.get("gaps"), list) and use["gaps"]):
                e.append("after_use.gaps: list the gaps when the verdict is gaps")
            if "evidence" in use and not https(use["evidence"]):
                e.append("after_use.evidence: a public GitHub link")
            if reached(state, "accepted") and not https(use.get("accept_src")):
                e.append("after_use.accept_src: link to the Owner's acceptance, required from state accepted")
    if reached(state, "hardened"):
        h = card.get("hardening")
        if not (isinstance(h, dict) and isinstance(h.get("repo"), str) and REPO.fullmatch(h["repo"])
                and isinstance(h.get("head"), str) and SHA40.fullmatch(h["head"]) and https(h.get("evidence"))):
            e.append("hardening: repo owner/name, 40-character head and GitHub evidence, required from state hardened")
    for i, st in enumerate(card.get("owner_steering") or []):
        if isinstance(st, dict) and "src" in st and not https(st["src"]):
            e.append(f"owner_steering[{i}].src: a public GitHub link")
    if state == "verified":
        if check_level != "independent":
            e.append("state verified: only a card with check independent can be verified")
        if not https(card.get("check_verdict")):
            e.append("check_verdict: link to the independent PASS, required for state verified")
    return e


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    failed = False
    for name in argv:
        try:
            card = json.loads(Path(name).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            print(f"{name}: cannot read: {exc}")
            failed = True
            continue
        errors = check(card)
        if errors:
            failed = True
            for err in errors:
                print(f"{name}: {err}")
        else:
            print(f"OK {name}")
            if (card.get("check") == "independent" and card.get("state") in ("accepted", "hardened")):
                print(f"NOTE {name}: check independent; trial use only until verified")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
