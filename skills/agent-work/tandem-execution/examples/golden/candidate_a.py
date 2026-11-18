"""Synthetic C1: A fixes feed identity, but leaves dismissal path unchanged."""
def merge(events):
    return list({e['occurrence_id']: e for e in events}.values())

def dismiss(saved, suggestions, target):
    return ([p for p in saved if p.get('url') != target['url']],
            [s for s in suggestions if s['url'] != target['url']])
