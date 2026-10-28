#!/usr/bin/env python3
import sys

try:
    import yaml
except Exception:
    print("PyYAML is required for claim-file overlap checks.", file=sys.stderr)
    raise SystemExit(2)

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def vals(d, *keys):
    cur = d
    for k in keys:
        cur = (cur or {}).get(k, {})
    return set(cur or [])

def main():
    if len(sys.argv) < 3:
        print("Usage: detect_pr_overlap.py <claim1.yaml> <claim2.yaml> [...]", file=sys.stderr)
        return 2
    claims = [(p, load(p)) for p in sys.argv[1:]]
    conflicts = 0
    for i in range(len(claims)):
        for j in range(i+1, len(claims)):
            pa,a = claims[i]; pb,b = claims[j]
            exact = vals(a,"files","exact") & vals(b,"files","exact")
            auth = set(a.get("authority_domains") or []) & set(b.get("authority_domains") or [])
            prefixes_a = set((a.get("files") or {}).get("prefixes") or [])
            prefixes_b = set((b.get("files") or {}).get("prefixes") or [])
            prefix = {(x,y) for x in prefixes_a for y in prefixes_b if x.startswith(y) or y.startswith(x)}
            if exact or auth or prefix:
                conflicts += 1
                print(f"OVERLAP {pa} <-> {pb}")
                if exact: print("  exact:", sorted(exact))
                if auth: print("  authority:", sorted(auth))
                if prefix: print("  prefixes:", sorted(prefix))
    print(f"overlap_pairs={conflicts}")
    return 1 if conflicts else 0

if __name__ == "__main__":
    raise SystemExit(main())
