#!/usr/bin/env python3
"""Record current observations or summarize a standalone ChatGPT-agent episode."""
import argparse
import json
from standalone_activity_v36 import append_event, read_log, summarize, utc_now


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    start = sub.add_parser('start')
    start.add_argument('--surface', choices=('chatgpt-agent', 'chatgpt-work', 'other', 'unknown'), required=True)
    start.add_argument('--session-id', required=True)
    for name in ('start', 'turn-start', 'turn-end', 'github', 'gap', 'buddy-suggested', 'summary'):
        command = start if name == 'start' else sub.add_parser(name)
        command.add_argument('--log', required=True)
        if name in ('turn-start', 'turn-end', 'github'):
            command.add_argument('--turn-id', required=True)
        if name == 'github':
            command.add_argument('--tool', required=True)
            command.add_argument('--outcome', choices=('success', 'failure', 'unknown'), required=True)
        if name == 'gap': command.add_argument('--reason', required=True)
        if name == 'buddy-suggested': command.add_argument('--reference', required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == 'summary':
            result = summarize(read_log(args.log))
        elif args.operation == 'start' and args.surface != 'chatgpt-agent':
            result = {'surface': args.surface, 'policy_applies': None if args.surface == 'unknown' else False, 'log_created': False}
        else:
            row = {'event': 'session' if args.operation == 'start' else args.operation, 'at': utc_now()}
            if args.operation == 'start':
                row.update(session_id=args.session_id, surface=args.surface, observation='SELF_RECORDED')
            for key in ('turn_id', 'tool', 'outcome', 'reason', 'reference'):
                if hasattr(args, key): row[key] = getattr(args, key)
            result = append_event(args.log, row)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({'error': str(exc), 'owner_accepted': False}, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
