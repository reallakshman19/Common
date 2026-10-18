"""Offline Git observations for the v3.6 mechanical checker; no provider I/O."""
from pathlib import Path
import difflib
import re
import subprocess


def git(repo, *args, optional=False):
    proc = subprocess.run(["git", *args], cwd=repo, capture_output=True)
    if proc.returncode:
        if optional:
            return None
        raise ValueError(proc.stderr.decode("utf-8", "replace").strip() or "git failed")
    return proc.stdout


def source(repo, ref, path):
    if ":" in path or path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("unsafe path")
    return git(repo, "show", f"{ref}:{path}", optional=True)


def text(data):
    return data.decode("utf-8") if data is not None else ""


def changed(repo, base, head):
    raw = text(git(repo, "diff", "--no-renames", "--name-status", base, head))
    rows = {}
    for line in raw.splitlines():
        status, path = line.split("\t", 1)
        if path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("unsafe git diff path")
        rows[path] = status
    return rows


def history(repo, base, head):
    if subprocess.run(["git", "merge-base", "--is-ancestor", base, head],
                      cwd=repo, capture_output=True).returncode:
        raise ValueError("base is not an ancestor of head")
    commits = text(git(repo, "rev-list", "--reverse", "--ancestry-path",
                       f"{base}..{head}")).splitlines()
    return commits


def per_commit(repo, commit):
    return changed(repo, f"{commit}^", commit)


def newly_added(old, new):
    """New diff lines, not unchanged historical source."""
    before = old.splitlines()
    after = new.splitlines()
    matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
    return [line for tag, _, _, start, end in matcher.get_opcodes()
            if tag in ("insert", "replace") for line in after[start:end]]


def churn(old_bytes, new_bytes):
    """Refuse blank-only edits, changed line endings and matched whitespace churn."""
    if old_bytes == new_bytes:
        return False
    old = text(old_bytes)
    new = text(new_bytes)
    if b"\r\n" in old_bytes and b"\r\n" not in new_bytes:
        return True
    if b"\r\n" in new_bytes and b"\r\n" not in old_bytes:
        return True
    a, b = old.splitlines(), new.splitlines()
    if [x.strip() for x in a] == [x.strip() for x in b]:
        return True
    match = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i, j, k, l in match.get_opcodes():
        if tag == "equal":
            continue
        left, right = a[i:j], b[k:l]
        if tag == "insert" and any(not s.strip() for s in right):
            return True
        if tag == "delete" and any(not s.strip() for s in left):
            return True
        if left and right and [s.strip() for s in left] == [s.strip() for s in right]:
            return True
    return False


def assertions(data):
    """Conservatively preserve original assertion/skip statements exactly."""
    lines = text(data).splitlines()
    return [x.strip() for x in lines if re.search(
        r"\bassert\b|\.assert[A-Za-z]+\(|\bskipTest\(|"
        r"@(?:unittest\.)?(?:skip|skipIf|skipUnless|expectedFailure)\b", x)]


def forbidden_build(path):
    parts = Path(path).parts
    return (any(x in ("__pycache__", ".pytest_cache", "node_modules", "build",
                      "dist", ".mypy_cache") for x in parts)
            or path.endswith((".pyc", ".pyo", ".class", ".o")))


def is_test(path):
    return (Path(path).name.startswith("test_") and path.endswith(".py"))


def is_authored(path):
    return path.endswith((".py", ".md", ".yaml", ".yml", ".json"))


def physical_lines(data):
    return len(data.splitlines()) if data else 0
