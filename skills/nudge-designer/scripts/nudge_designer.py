#!/usr/bin/env python3
"""Offline support for agent-authored intent and nudge plans. No generate/apply flag."""
import argparse
import json
import os
from pathlib import Path
import tempfile

try:
    from nd_contract import validate_plan
    from nd_io import ContractError, load_json, require
    from nd_profiles import LIBRARY, load_profiles
    from nd_reconcile import impact_report
    from nd_render import render_nudge
    from nd_adapters import SURFACES, adapt
    from nd_team import ROLES, capability_fit, task_binding
    from nd_returns import receive
except ModuleNotFoundError as error:
    print(json.dumps({"status": "NOT_RUN", "missing_module": error.name,
                      "reason": "Use a complete package and Python 3.10+ with jsonschema installed, or preserve manual checks as NOT_RUN.",
                      "structural_validation_performed": False, "execution_performed": False}))
    raise SystemExit(2)


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
    for command in ("validate", "render", "impact", "adapt", "fit", "bind", "receive"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--intent", required=True)
        subparser.add_argument("--profiles", default=str(LIBRARY))
        subparser.add_argument("--out")
        if command == "impact":
            subparser.add_argument("--previous-intent", required=True)
            subparser.add_argument("--previous-plan", required=True)
        else:
            subparser.add_argument("--plan", required=True)
        if command in ("render", "adapt", "fit", "bind"):
            subparser.add_argument("--nudge", required=True)
        if command == "adapt":
            subparser.add_argument("--audience", choices=ROLES, default="worker")
            subparser.add_argument("--surface", choices=SURFACES, default="plain")
            subparser.add_argument("--recipient")
            subparser.add_argument("--report")
        if command == "fit":
            subparser.add_argument("--participant")
        if command == "receive":
            subparser.add_argument("--report", required=True)
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
            validate_plan(intent, plan, profiles)
            report = None
            if getattr(args, "report", None):
                report = load_json(args.report)
                inputs.append(args.report)
                native = report.get("native_report") if isinstance(report, dict) else None
                locator = native.get("locator") if isinstance(native, dict) else None
                if isinstance(locator, str) and "://" not in locator:
                    inputs.append(str(Path(args.report).resolve().parent / locator))
            if args.command == "render":
                result = render_nudge(intent, plan, args.nudge, profiles)
            elif args.command == "adapt":
                result = adapt(intent, plan, args.nudge, profiles, args.audience, args.surface, args.recipient, report)
            elif args.command == "fit":
                result = capability_fit(plan, args.nudge, args.participant)
            elif args.command == "bind":
                result = task_binding(intent, plan, args.nudge)
            elif args.command == "receive":
                result = receive(intent, plan, report, profiles)
            else:
                result = validate_plan(intent, plan, profiles)
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2)
        write_output(text, args.out, inputs)
        return 0
    except (ContractError, OSError) as error:
        print(json.dumps({"status": "INVALID", "reason": str(error), "execution_performed": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
