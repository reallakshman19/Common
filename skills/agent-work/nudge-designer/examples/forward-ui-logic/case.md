# Owner request — synthetic forward pilot

Help me make the record-review screen trustworthy. Several patches have changed
the loading spinner but reviewers still sometimes see the wrong record. Give me
useful next work that a narrower implementation agent can carry out. Preserve
ordinary click and keyboard navigation. Do not combine an unproven repair with
the first investigation. Also retain the independent pending CSV export request.

Supplied observations (not newly executed): load A starts, reviewer selects B,
load B resolves and B is shown; later A resolves and its text appears while the
header still says B. No ordinary pointer trace or full browser run is supplied.

Source revision: synthetic-v1. The following is the complete supplied source:

```javascript
let selectedId = null;
function select(id) {
  selectedId = id;
  header.textContent = id;
  fetchRecord(id).then(record => {
    details.textContent = record.description;
    spinner.hidden = true;
  });
}
```

CSV columns and delimiters have not yet been specified. Owner authorizes local
analysis and drafting only in this pilot, not product edits or external writes.
Available tools: Python, offline source inspection. Browser and backend absent.
Actual future worker model and reasoning configuration are unknown.
