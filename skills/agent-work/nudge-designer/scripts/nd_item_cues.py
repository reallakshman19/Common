#!/usr/bin/env python3
"""Mechanical selected-response cues; no format, verb-fit or subject approval."""
import argparse
import json
import re
from nd_io import load_json, require

STOPWORDS = frozenset('a an the is are was were be been being to of and or in on at for with why what which how does do did this that it its as by from when'.split())
WORDS = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
REASONING = frozenset(('because', 'therefore', 'since', 'thus', 'hence'))


def tokens(value):
    return {x.casefold() for x in WORDS.findall(value)}


def assignment_support():
    return [
        'Generator pre-return: match option type to the tile verb: explain needs causal reasons; justify needs argument steps; retrieve may use a unit or sign. Check the specified demand, not numbers alone.',
        'Compute option word counts and correct-only shared question words with nd_item_cues.py or a stated equivalent script before handing over. Return its actual output and a disposition for each flag; no silent edits.',
        'Inspect longest-key and reasoning-word cues, parallel grammar and verb-option fit. Reasoning words and legitimate shared technical terms are signals to inspect, not universal bans. Ask whether a key can be picked without the target subject knowledge.',
        'Keep generator judgment SELF-ASSESSED. The judge records prior exposure, cites exact candidate files and states a plausible wrong result that could survive each verdict. A cue-free item can still be wrong or off-demand.',
    ]


def validate_item(row, seen):
    require(isinstance(row, dict), 'item must be an object')
    for key in ('id', 'verb', 'question', 'answer'):
        require(isinstance(row.get(key), str) and bool(row[key].strip()), 'missing item ' + key)
    require(row['id'] not in seen, 'duplicate item ID')
    seen.add(row['id'])
    options = row.get('options')
    require(isinstance(options, list) and len(options) >= 2, 'at least two options required')
    ids = set()
    for option in options:
        require(isinstance(option, dict), 'option must be an object')
        require(isinstance(option.get('id'), str) and bool(option['id'].strip()), 'option ID required')
        require(option['id'] not in ids, 'duplicate option ID')
        ids.add(option['id'])
        require(isinstance(option.get('text'), str) and bool(option['text'].strip()), 'empty option text')
    require(row['answer'] in ids, 'answer must identify an option')
    return options


def inspect_item(row, options, max_words):
    key = row['answer']
    counts = {o['id']: len(o['text'].split()) for o in options}
    words = {o['id']: tokens(o['text']) for o in options}
    distractors = set().union(*(v for k, v in words.items() if k != key))
    only_shared = sorted((tokens(row['question']) & words[key]) - distractors)
    markers = {o['id']: sorted(set(x.casefold() for x in WORDS.findall(o['text'])) & REASONING)
               for o in options}
    flags = []
    if only_shared: flags.append('SHARED_WORD_KEY_ONLY')
    if counts[key] > max(v for k, v in counts.items() if k != key): flags.append('LONGEST_KEY')
    if markers[key] and not any(v for k, v in markers.items() if k != key): flags.append('REASONING_KEY_ONLY')
    if max_words is not None and any(v > max_words for v in counts.values()): flags.append('WORD_LIMIT')
    if row['verb'].casefold() in ('explain', 'justify') and any(not WORDS.search(o['text']) for o in options):
        flags.append('BARE_VALUE_FOR_REASONING_VERB')
    return {'id': row['id'], 'verb': row['verb'], 'word_counts': counts,
            'correct_only_question_words': only_shared,
            'substantive_correct_only_question_words': sorted(set(only_shared) - STOPWORDS),
            'reasoning_markers': markers,
            'flags': flags, 'manual_checks': ['verb-option match', 'parallel grammar',
                'could the key be picked without the target subject knowledge?']}


def inspect_items(data, max_words=None):
    require(isinstance(data, dict) and isinstance(data.get('items'), list) and bool(data['items']), 'items must be a nonempty list')
    require(max_words is None or type(max_words) is int and max_words > 0, 'max words must be positive integer')
    seen, rows = set(), []
    for row in data['items']:
        rows.append(inspect_item(row, validate_item(row, seen), max_words))
    return {'items': rows, 'word_count_rule': 'whitespace-separated tokens, including standalone symbols',
            'shared_word_rule': 'all casefolded Unicode words; a separate non-stopword subset helps inspection; no stemming or semantic inference',
            'review_required': True, 'format_approved': False,
            'verb_fit_evaluated': False, 'physics_evaluated': False,
            'limits': ['Flags can be legitimate wording, not demonstrated defects.',
                       'No flags does not establish demand fit, answer truth or learner understanding.']}


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--items', required=True)
    cli.add_argument('--max-words', type=int)
    args = cli.parse_args(argv)
    try:
        print(json.dumps(inspect_items(load_json(args.items), args.max_words), ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({'error': str(exc), 'format_approved': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
