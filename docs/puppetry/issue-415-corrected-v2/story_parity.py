#!/usr/bin/env python3
"""Compare real dialogue and scene time intervals, not just file presence."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEAD = re.compile(r"^## Scene ([1-4]):", re.M)
SLOT = re.compile(r"^\\*\\*(\\d:\\d{2})-(\\d:\\d{2}) - [^\\n]*?\\*\\*:", re.M)
EXPECTED = (35,40,55,50)


def seconds(hmm: str) -> int:
    minute, sec = map(int, hmm.split(":"))
    if sec > 59:
        raise ValueError("invalid seconds")
    return minute * 60 + sec


def inspect(root: Path = ROOT) -> dict:
    problems=[]
    master=(root/"story"/"COMPLETE_STORY.md").read_text(encoding="utf-8")
    starts=list(HEAD.finditer(master))
    if [int(x.group(1)) for x in starts] != [1,2,3,4]:
        problems.append("missing or reordered master sections")
    if len(starts)==4:
        for i,start in enumerate(starts):
            end=starts[i+1].start() if i<3 else len(master)
            canonical=master[start.start():end].strip()
            path=root/"scenes"/f"SCENE_0{i+1}.md"
            if not path.is_file():
                problems.append(f"missing {path.name}")
                continue
            detail=path.read_text(encoding="utf-8")
            marker=HEAD.search(detail)
            if marker is None or detail[marker.start():].strip()!=canonical:
                problems.append(f"Scene {i+1} diverges from complete script")
            slots=SLOT.findall(canonical)
            if not slots:
                problems.append(f"Scene {i+1} has no time slots")
                continue
            try:
                intervals=[(seconds(a),seconds(b)) for a,b in slots]
            except ValueError:
                problems.append(f"Scene {i+1} has invalid clock value")
                continue
            start_time=sum(EXPECTED[:i])
            end_time=start_time+EXPECTED[i]
            if intervals[0][0]!=start_time or intervals[-1][1]!=end_time:
                problems.append(f"Scene {i+1} boundary deviates from fixed timing")
            if any(a>=b for a,b in intervals) or any(a[1]!=b[0] for a,b in zip(intervals, intervals[1:])):
                problems.append(f"Scene {i+1} gaps, overlap or reversed dialogue times")
    board=(root/"story"/"FOUR_SCENE_ASCII_STORYBOARD.md").read_text(encoding="utf-8")
    if len(re.findall(r"^## Panel [1-4] -",board,re.M))!=4:
        problems.append("four ASCII panels not present")
    for cue in ("three small tap gestures","arm DOWN","bless","15 to 20 degrees"):
        if cue.lower() not in master.lower():
            problems.append(f"required cue absent: {cue}")
    return {"passed":not problems,"problems":problems,
            "authority":"SCRIPT_PARITY_ONLY__NOT_TIMED_REHEARSAL"}


if __name__=="__main__":
    result=inspect()
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["passed"] else 1)
