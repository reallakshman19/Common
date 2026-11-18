"""Synthetic C0: publication identity conflates events and user-owned plans."""
def merge(events):
    return list({e['url']: e for e in events}.values())

def dismiss(saved, suggestions, target):
    return ([p for p in saved if p.get('url') != target['url']],
            [s for s in suggestions if s['url'] != target['url']])
