#!/usr/bin/env python3
"""Offline support for agent-authored intent and nudge plans. No generate/apply flag."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from nd_contract import validate_plan
from nd_io import ContractError, load_json, require
from nd_profiles import LIBRARY, load_profiles
from nd_reconcile import impact_report
from nd_render import render_nudge


def write_output(text, output, inputs):
    if output is None:
        print(text)
        return
    target = Path(output).resolve()
    require(target not in {Path(path).resolve() for path in inputs}, "output cannot overwrite an input")
    require(target.parent.is_dir(), "output parent directory must exist")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                         prefix=".nudge-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text + "\n")
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "render", "impact"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--intent", required=True)
        subparser.add_argument("--profiles", default=str(LIBRARY))
        subparser.add_argument("--out")
        if command == "impact":
            subparser.add_argument("--previous-intent", required=True)
            subparser.add_argument("--previous-plan", required=True)
        else:
            subparser.add_argument("--plan", required=True)
        if command == "render":
            subparser.add_argument("--nudge", required=True)
    args = parser.parse_args(argv)
    try:
        intent = load_json(args.intent)
        profiles = load_profiles(args.profiles)
        inputs = [args.intent, args.profiles]
        if args.command == "impact":
            previous = load_json(args.previous_intent)
            plan = load_json(args.previous_plan)
            inputs.extend([args.previous_intent, args.previous_plan])
            result = impact_report(previous, plan, intent, profiles)
        else:
            plan = load_json(args.plan)
            inputs.append(args.plan)
            result = (render_nudge(intent, plan, args.nudge, profiles) if args.command == "render"
                      else validate_plan(intent, plan, profiles))
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2)
        write_output(text, args.out, inputs)
        return 0
    except (ContractError, OSError) as error:
        print(json.dumps({"status": "INVALID", "reason": str(error), "execution_performed": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
