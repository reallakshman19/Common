"""Composable, caller-selectable reasoning/evidence guidance, never admission."""
from pathlib import Path
import re

from nd_io import digest, indexed, load_json, require

LIBRARY = Path(__file__).resolve().parents[1] / "profiles" / "library.json"
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,79}$")
FIELDS = {"id", "revision", "label", "knowledge", "reasoning_moves", "evidence_methods",
          "review_questions", "pitfalls"}


def load_profiles(path=LIBRARY):
    data = load_json(path)
    require(isinstance(data, dict) and set(data) == {"schema", "profiles"}, "invalid profile library")
    require(data["schema"] == "nudge-designer.profiles/v1", "wrong profile library version")
    require(isinstance(data["profiles"], list) and bool(data["profiles"]), "empty profile library")
    for profile in data["profiles"]:
        require(isinstance(profile, dict) and set(profile) == FIELDS, "invalid profile fields")
        for key in ("id", "revision", "label"):
            require(isinstance(profile[key], str) and bool(profile[key].strip()), "empty profile " + key)
        require(bool(IDENTIFIER.fullmatch(profile["id"])), "invalid profile ID")
        for key in FIELDS - {"id", "revision", "label"}:
            values = profile[key]
            require(isinstance(values, list) and bool(values), "empty profile " + key)
            require(all(isinstance(v, str) and bool(v.strip()) for v in values), "invalid profile " + key)
            require(len(values) == len(set(values)), "duplicate profile " + key)
    return indexed(data["profiles"], "profile")


def profile_digest(profiles, ids):
    require(len(ids) == len(set(ids)), "duplicate selected profile")
    require(all(ident in profiles for ident in ids), "unknown selected profile")
    return digest([profiles[ident] for ident in sorted(ids)])


def guidance(profiles, ids, field):
    return list(dict.fromkeys(value for ident in ids for value in profiles[ident][field]))
