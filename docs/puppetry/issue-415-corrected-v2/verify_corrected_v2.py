#!/usr/bin/env python3
"""Source-intake and exact-archive verification for Puppet #415 corrected v2.

A source-only pass is NEVER evidence that the ZIP or PDFs exist on GitHub.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_checks(root):
    missing = []
    story = root / "story" / "COMPLETE_STORY.md"
    board = root / "story" / "FOUR_SCENE_ASCII_STORYBOARD.md"
    if not story.is_file() or not board.is_file():
        return ["required editable story/storyboard missing"]
    script, panels = story.read_text(encoding="utf-8"), board.read_text(encoding="utf-8")
    for n in range(1, 5):
        if not (root / "scenes" / f"SCENE_0{n}.md").is_file():
            missing.append(f"scene {n} editable file missing")
        if not re.search(rf"^## Scene {n}:", script, re.M):
            missing.append(f"story scene {n} missing")
        if not re.search(rf"^## Panel {n} -", panels, re.M):
            missing.append(f"storyboard panel {n} missing")
    for time in ("0:00-0:35", "0:35-1:15", "1:15-2:10", "2:10-3:00"):
        if time not in script:
            missing.append(f"timing {time} missing")
    if panels.count("PERMANENT PALACE") != 4:
        missing.append("four permanent palace panels required")
    if "[||]" not in panels or "OPEN PILLAR" not in panels:
        missing.append("closed/open pillar continuity missing")
    return missing


def archive_checks(path, inventory):
    problems = []
    if not path.is_file():
        return ["ZIP not present: GitHub binary upload is still pending"]
    if sha256(path.read_bytes()) != inventory["zip_sha256"]:
        return ["ZIP sha256 mismatch"]
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            problems.append("invalid ZIP member")
        names = z.namelist()
        if len(names) != inventory["expected_members"]:
            problems.append("incorrect member count")
        if len(set(names)) != len(names):
            problems.append("duplicate path")
        if sum(n.lower().endswith(".pdf") for n in names) != inventory["expected_pdf_members"]:
            problems.append("incorrect PDF count")
        for name in names:
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts:
                problems.append(f"unsafe path: {name}")
        seen = []
        for item in inventory["key_members"]:
            name = item["path"]
            if name not in names:
                problems.append(f"missing {name}")
                continue
            data = z.read(name)
            identity = sha256(data)
            if identity != item["sha256"]:
                problems.append(f"sha256 mismatch for {name}")
            seen.append(identity)
            try:
                import fitz
                pdf = fitz.open(stream=data, filetype="pdf")
                if len(pdf) != item["pages"]:
                    problems.append(f"page count mismatch for {name}")
                if item["marker"] not in "\n".join(page.get_text() for page in pdf):
                    problems.append(f"expected content not found in {name}")
                pdf.close()
            except ImportError:
                problems.append("PyMuPDF required for PDF text/page verification")
        if len(seen) != 4 or len(set(seen)) != 4:
            problems.append("the four quick-print PDF identities are not distinct")
        if inventory["pillars_path"] not in names:
            problems.append("pillar-only PDF missing from stage folder")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=HERE)
    parser.add_argument("--zip", type=Path, default=None)
    args = parser.parse_args()
    manifest = json.loads((args.root / "expected_package.json").read_text(encoding="utf-8"))
    problems = source_checks(args.root)
    if args.zip is not None:
        problems.extend(archive_checks(args.zip, manifest))
    report = {
        "scope": "SOURCE_ONLY__BINARY_NOT_CHECKED" if args.zip is None else "SOURCE_AND_LOCAL_BINARY",
        "passed": len(problems) == 0,
        "issues": problems,
        "github_binary_custody": "NOT_ESTABLISHED_BY_THIS_SCRIPT",
        "physical_acceptance": "NOT_RUN",
    }
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(problems))


if __name__ == "__main__":
    main()
