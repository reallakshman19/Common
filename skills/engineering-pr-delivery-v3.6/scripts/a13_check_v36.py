"""C1/C3/C10/C11/C12/C13/C16/C17 + A13 offline scope gate.

--scope names an immutable, git-tracked JSON policy at --base, containing
paths (declared changed files), ci_workflow, ci_pattern and optional
protected / forbidden_literals. This is a mechanical gate, not independent
CI attestation, semantic assertion review, permission or Owner acceptance.
"""
import argparse
from collections import Counter
import fnmatch
import json
from pathlib import Path
import re
import sys

from a13_git_v36 import (assertions, changed, churn, forbidden_build, git,
                         history, is_authored, is_test, newly_added,
                         per_commit, physical_lines, source, text)

IDS = ("C1", "C3", "C10", "C11", "C12", "C13", "C16", "C17", "A13")
SECRET = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)


def load_scope(repo, base, head, location):
    policy = Path(location)
    absolute = policy if policy.is_absolute() else repo / policy
    relative = absolute.resolve().relative_to(repo.resolve()).as_posix()
    old = source(repo, base, relative)
    now = source(repo, head, relative)
    if not old or old != now:
        raise ValueError("--scope policy must be tracked and unchanged since base")
    rules = json.loads(text(old))
    files = rules.get("paths")
    if (not isinstance(files, list) or not files or
            any(not isinstance(x, str) or x.startswith("/") or ".." in Path(x).parts
                for x in files) or len(files) != len(set(files))):
        raise ValueError("--scope requires distinct declared relative paths")
    for key in ("protected", "forbidden_literals"):
        if not isinstance(rules.get(key), list) or not all(
                isinstance(x, str) for x in rules[key]):
            raise ValueError("--scope requires explicit protected and forbidden_literals")
    return rules


def c1_ci(repo, base, head, changes, rules):
    name = rules.get("ci_workflow")
    pattern = rules.get("ci_pattern")
    added = [p for p, status in changes.items()
             if status == "A" and is_test(p)]
    if not added or not isinstance(name, str) or not isinstance(pattern, str):
        return False
    workflow = text(source(repo, head, name))
    if (not workflow or workflow != text(source(repo, base, name))
            or "unittest discover" not in workflow or "-p" not in workflow
            or pattern not in workflow):
        return False
    return all(fnmatch.fnmatch(Path(p).name, pattern) for p in added)


def c3_assertions(repo, base, head, changes):
    for path, status in changes.items():
        if not is_test(path):
            continue
        before, after = source(repo, base, path), source(repo, head, path)
        prior, current = Counter(assertions(before)), Counter(assertions(after))
        if any(current[statement] < count for statement, count in prior.items()):
            return False
        additions = newly_added(text(before), text(after))
        if any(re.search(r"\bskipTest\(|@(?:unittest\.)?skip\b|\bpytest\.skip\(",
                         row) for row in additions):
            return False
    return True


def c10_scope(changes, rules):
    declared = set(rules["paths"])
    protected = tuple(rules["protected"])
    return (all(p in declared for p in changes)
            and not any(p.startswith(protected) for p in changes))


def c11_format(repo, base, head, changes):
    return not any(churn(source(repo, base, p), source(repo, head, p))
                   for p, status in changes.items() if status not in ("A", "D"))


def c12_order(repo, base, head, changes, commits):
    if len(commits) < 2:
        return False
    first = per_commit(repo, commits[0])
    if not first or not all(status == "A" and is_test(p)
                            for p, status in first.items()):
        return False
    created = [p for p, status in changes.items() if status == "A" and is_test(p)]
    if not created or not set(created).issubset(first):
        return False
    if not any(p != q for p in changes for q in created):
        return False
    for commit in commits:
        if any(forbidden_build(p) for p in per_commit(repo, commit)):
            return False
    return True


def c13_literals(repo, base, head, changes, rules):
    forbidden = [v.casefold() for v in rules["forbidden_literals"] if v]
    hardcoded = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b|"
                           r"(?:/home/|/Users/|[A-Za-z]:\\Users\\)")
    for path in changes:
        if not path.endswith(".py") or is_test(path):
            continue
        lines = newly_added(text(source(repo, base, path)),
                            text(source(repo, head, path)))
        for line in lines:
            if any(v in line.casefold() for v in forbidden) or hardcoded.search(line):
                return False
    return True


def c16_secrets(repo, base, head, changes):
    return not any(SECRET.search("\n".join(newly_added(
        text(source(repo, base, p)), text(source(repo, head, p)))))
        for p in changes)


def c17_dependencies(repo, base, head, changes):
    dependency_names = ("requirements.txt", "pyproject.toml", "Pipfile",
                        "package.json", "package-lock.json")
    for p in changes:
        if Path(p).name in dependency_names and source(repo, base, p) != source(repo, head, p):
            return False
    # New imports must be stdlib, existing dependency, or in-repo code.
    modules = {Path(p).stem for p in changes if p.endswith(".py")}
    for p in changes:
        if not p.endswith(".py") or is_test(p):
            continue
        lines = newly_added(text(source(repo, base, p)), text(source(repo, head, p)))
        for line in lines:
            match = re.match(r"\s*(?:from|import)\s+([a-zA-Z_][\w]*)", line)
            if match and (match[1] not in sys.stdlib_module_names
                          and match[1] not in modules and match[1] != "yaml"):
                return False
    return True


def a13_size(repo, base, head, changes):
    for p in changes:
        if not is_authored(p):
            continue
        before = physical_lines(source(repo, base, p))
        after = physical_lines(source(repo, head, p))
        if after > 300 and (before <= 300 or after >= before):
            return False
    return True


def check(repo, base, head, scope):
    repo = Path(repo).resolve()
    rules = load_scope(repo, base, head, scope)
    commits = history(repo, base, head)
    files = changed(repo, base, head)
    result = {
        "C1": c1_ci(repo, base, head, files, rules),
        "C3": c3_assertions(repo, base, head, files),
        "C10": c10_scope(files, rules),
        "C11": c11_format(repo, base, head, files),
        "C12": c12_order(repo, base, head, files, commits),
        "C13": c13_literals(repo, base, head, files, rules),
        "C16": c16_secrets(repo, base, head, files),
        "C17": c17_dependencies(repo, base, head, files),
        "A13": a13_size(repo, base, head, files),
    }
    return {"checks": result, "first_test_commit": commits[0] if commits else None,
            "changed_paths": sorted(files)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="v3.6 offline mechanical A13/C checkpoint gate")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--scope", required=True, help="tracked frozen JSON scope policy at base")
    args = parser.parse_args(argv)
    try:
        result = check(Path.cwd(), args.base, args.head, args.scope)
        failed = [key for key, ok in result["checks"].items() if not ok]
        values = ",".join(f"{key}={'PASS' if ok else 'FAIL'}"
                          for key, ok in result["checks"].items())
        print(f"A13_CHECK v36 | {values} | result={'FAIL' if failed else 'PASS'}"
              f" | failed={','.join(failed) if failed else 'none'}")
        return 1 if failed else 0
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"A13_CHECK v36 | result=FAIL | input={type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
