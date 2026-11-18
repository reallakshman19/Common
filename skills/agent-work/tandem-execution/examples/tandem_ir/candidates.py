"""Synthetic saved-occurrence candidates; no real project or agent claims."""


def c0(saved, suggestions, target):
    # Baseline deletes saved records and unrelated occurrences sharing a URL.
    return ([r for r in saved if r["url"] != target["url"]],
            [r for r in suggestions if r["url"] != target["url"]])


def c1(saved, suggestions, target):
    # A protects durable records, but still conflates distinct occurrences.
    return (list(saved),
            [r for r in suggestions if r["url"] != target["url"]])


def c2(saved, suggestions, target):
    # B fixes occurrence identity but accidentally conflates missing identities.
    return (list(saved),
            [r for r in suggestions if r.get("occurrence_id") != target.get("occurrence_id")])


def c3(saved, suggestions, target):
    # A retains B's fix and rejects an unidentifiable dismissal safely.
    key = target.get("occurrence_id")
    if not isinstance(key, str) or not key.strip():
        return list(saved), list(suggestions)
    return list(saved), [r for r in suggestions if r.get("occurrence_id") != key]
