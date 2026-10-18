# Raw synthetic logic case

Owner invariant: only a completion for the currently selected revision may publish
its result. Preserve successful current completions. Current revision is 7; NEW
belongs to rev7 and OLD to rev6. Each experiment starts with no result.

Supplied original function:

```python
def receive(state, request_revision, payload):
    state['result'] = payload
    return state
```

Python execution of this unchanged fixture is permitted, with no product edits.
The worker needs a concrete method. No run has been supplied. A separate CSV
format requirement remains unanswered and has no declared dependency on this race.
